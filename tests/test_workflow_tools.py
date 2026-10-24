import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from scripts.authoring_preflight import inspect_authoring
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import Workflow

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'blender-new-llm-setup'))


class PreflightTests(unittest.TestCase):
    def test_render_aliases_and_subdirectories_are_rejected_before_execution(self):
        for code in ['import bpy\nbpy.ops.render.render()',
                     'import bpy as b\nr=b.ops.render.render\nr()',
                     'from bpy.ops import render as r\nr.opengl()',
                     'import bpy\ngetattr(bpy.ops.render,"render")()',
                     'import os\nos.makedirs("/job/renders")',
                     'from pathlib import Path\nPath("/job/renders").mkdir()']:
            with self.subTest(code=code):
                result=inspect_authoring(code)
                self.assertFalse(result['ok'])
                self.assertFalse(result['attempt_consumed'])
                self.assertTrue(result['recoverable'])

    def test_supported_scene_preparation_and_flat_outputs_are_allowed(self):
        code="import bpy,json,os\nscene=bpy.context.scene\nscene.render.image_settings.file_format='PNG'\nos.makedirs('/job',exist_ok=True)\nreport={'prepared':True}\n"
        self.assertTrue(inspect_authoring(code)['ok'])

    def test_known_bad_render_material_api_and_syntax_have_repair_feedback(self):
        for code in ["scene=bpy.context.scene\nrs=scene.render\nrs.file_format='PNG'",
                     "scene.render.image_format='PNG'", "p.inputs['Clearcoat'].default_value=1", 'def broken(:']:
            self.assertFalse(inspect_authoring(code)['ok'])


class FakeClient:
    def __init__(self,folder):
        self.folder=Path(folder);self.rows={};self.submissions=[]

    async def rpc(self,action,request):
        if action=='submit':
            job=f'{len(self.rows)+1:032x}'
            self.rows[job]={'id':job,'state':'queued','spec':copy.deepcopy(request),'manifest':None}
            self.submissions.append(copy.deepcopy(request))
            return copy.deepcopy(self.rows[job])
        return copy.deepcopy(self.rows[request['job_id']])

    def complete(self,job):
        row=self.rows[job];folder=self.folder/job;folder.mkdir(parents=True)
        scene={'blender_version':'5.2.3 LTS','objects':[{'name':'CAM_BowlingPair01_Overview','type':'CAMERA'}],
               'materials':[],'active_camera':'CAM_BowlingPair01_Overview'}
        (folder/'scene.blend').write_bytes(json.dumps(row['spec']).encode())
        (folder/'scene.json').write_text(json.dumps(scene))
        (folder/'report.json').write_text('{"passed":true}')
        if row['spec']['operation']=='render':
            Image.new('RGB',(1280,720),(50,70,90)).save(folder/'frame-0001.png')
        if row['spec'].get('code')=='report = {}':
            report={'checks':[{'id':f'S{i:02d}_test','stage':f'{i:02d}','status':'FAIL' if i==5 else 'PASS','passed':i!=5,'observed':'fixture observation'} for i in range(8)],
                    'read_only':True,'source_fingerprint_before':'same-geometry','source_fingerprint_after':'same-geometry','facts':{}}
            (folder/'validation.json').write_text(json.dumps(report))
        row.update(state='completed',manifest={'blender_version':'5.2.3 LTS','artifacts':[
            {'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in folder.iterdir()]})

    async def fetch(self,job,name):
        path=self.folder/job/name
        return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for directory in ['artifacts/scripts','artifacts/reports','artifacts/blend','artifacts/renders']:
            (self.root/directory).mkdir(parents=True)
        (self.root/'artifacts/scripts/validate_bowling_pair01.py').write_text('report = {}')
        rows='\n'.join(f'| {i:02d} | Stage | NOT_STARTED | |' for i in range(10))
        (self.root/'BUILD_STATUS.md').write_text('# Build\n\n- Status: NOT_STARTED\n- Active source job: none\n\n## Stage ledger\n\n'+rows+'\n\n## Next action\nStart.\n')
        (self.root/'HANDOFF.md').write_text('# Handoff\n\n- Run status: NOT_STARTED\n- Last verified source job: none\n')
        self.client=FakeClient(self.root/'native')
        self.guard=SubmissionGuard(self.root/'.runtime/blender52/submissions.sqlite')
        self.workflow=Workflow(self.root,self.client,self.guard,hashlib.sha256(b'report = {}').hexdigest())
        self.references=patch('scripts.workflow_tools.reference_check',return_value={'passed':True,'issues':[]})
        self.references.start();self.addCleanup(self.references.stop)

    async def ready_asset(self):
        accepted=await self.workflow.call('author',code="report={'stage':'00'}")
        self.client.complete(accepted['id'])
        result=await self.workflow.call('status',job_id=accepted['id'])
        validation=result['validation_job']['id'];self.client.complete(validation)
        await self.workflow.call('status',job_id=validation)
        return accepted['id'],validation

    async def test_preflight_rejection_consumes_no_guard_or_network_submission(self):
        result=await self.workflow.call('author',code='import bpy\nbpy.ops.render.render()')
        self.assertFalse(result['ok']);self.assertTrue(result['recoverable'])
        self.assertEqual(self.guard.rows(),[]);self.assertEqual(self.client.submissions,[])

    async def test_completed_author_publishes_checkpoint_queues_validation_once_and_blocks_overlap(self):
        accepted=await self.workflow.call('author',code="report={'stage':'00'}")
        self.client.complete(accepted['id'])
        observed=await self.workflow.call('status',job_id=accepted['id'])
        self.assertTrue((self.root/'artifacts/blend/BowlingPair01.blend').exists())
        self.assertEqual(self.workflow.state['current_source'],accepted['id'])
        self.assertEqual(len(self.client.submissions),2)
        pending=await self.workflow.call('author',code="report={'next':True}")
        self.assertEqual(pending['code'],'pending_work')
        self.assertEqual(len(self.client.submissions),2)
        validation=observed['validation_job']['id'];self.client.complete(validation)
        result=await self.workflow.call('status',job_id=validation)
        self.assertFalse(result['asset_passed'])
        self.assertIn('| 05 | Return, seating and alley dressing | FAIL |',(self.root/'BUILD_STATUS.md').read_text())
        await self.workflow.call('status',job_id=accepted['id'])
        self.assertEqual(len(self.client.submissions),2)

    async def test_authoritative_report_restores_false_manual_pass_and_works_after_restart(self):
        source,_=await self.ready_asset()
        text=(self.root/'BUILD_STATUS.md').read_text().replace('| FAIL |','| PASS |')
        (self.root/'BUILD_STATUS.md').write_text(text)
        (self.root/'artifacts/reports/validation.json').write_text('{"passed":true}')
        restarted=Workflow(self.root,self.client,self.guard,self.workflow.validator_sha256)
        result=await restarted.call('workflow_status')
        self.assertEqual(result['current_source'],source)
        self.assertFalse(result['validation']['passed'])
        self.assertIn('| 05 | Return, seating and alley dressing | FAIL |',(self.root/'BUILD_STATUS.md').read_text())

    async def test_old_source_and_changed_validator_are_rejected_before_submission(self):
        await self.ready_asset();before=len(self.client.submissions)
        result=await self.workflow.call('author',code='report={"new":True}',source_job='f'*32)
        self.assertEqual(result['code'],'stale_source')
        (self.root/'artifacts/scripts/validate_bowling_pair01.py').write_text('report={"passed":True}')
        result=await self.workflow.call('validate')
        self.assertEqual(result['code'],'validator_changed')
        self.assertEqual(len(self.client.submissions),before)

    async def test_named_view_selects_camera_then_real_render_queue_and_does_not_change_asset_source(self):
        source,_=await self.ready_asset()
        view=await self.workflow.call('render_view',role='overview')
        camera=view['camera_job'];self.client.complete(camera)
        selected=await self.workflow.call('status',job_id=view['id'])
        render=selected['native_job']
        self.assertEqual(self.client.rows[render]['spec']['operation'],'render')
        self.assertNotIn('render.render',self.client.rows[camera]['spec']['code'])
        self.assertEqual(self.workflow.state['current_source'],source)
        self.client.complete(render)
        result=await self.workflow.call('status',job_id=view['id'])
        self.assertEqual(result['state'],'completed')
        self.assertTrue((self.root/'artifacts/renders/BowlingPair01_overview.png').exists())
        self.assertEqual(self.workflow.state['current_source'],source)

    async def test_delivery_cannot_finish_merely_from_agent_pass_claims(self):
        await self.ready_asset()
        result=await self.workflow.call('finish_delivery')
        self.assertEqual(result['code'],'delivery_not_ready')
        result=await self.workflow.call('export_delivery')
        self.assertEqual(result['code'],'acceptance_required')

    async def test_incomplete_new_revision_clears_old_pass_mirrors_until_validation(self):
        await self.ready_asset()
        new=await self.workflow.call('author',code="report={'geometry_changed':True}")
        self.client.complete(new['id'])
        await self.workflow.call('status',job_id=new['id'])
        self.assertNotIn('| PASS |',(self.root/'BUILD_STATUS.md').read_text())
        self.assertIn('revalidation pending',(self.root/'HANDOFF.md').read_text())

    async def test_failed_view_camera_never_admits_render_or_retries(self):
        await self.ready_asset()
        view=await self.workflow.call('render_view',role='overview')
        self.client.rows[view['camera_job']].update(state='failed',error='fixture failure')
        before=len(self.client.submissions)
        result=await self.workflow.call('status',job_id=view['id'])
        self.assertEqual(result['state'],'failed')
        await self.workflow.call('status',job_id=view['id'])
        self.assertEqual(len(self.client.submissions),before)
        self.assertEqual(self.guard.summary()['failed_count'],1)

    async def test_invalid_view_resolution_consumes_no_attempt(self):
        await self.ready_asset();before=len(self.guard.rows())
        result=await self.workflow.call('render_view',role='overview',resolution=[320,180])
        self.assertEqual(result['code'],'resolution_out_of_bounds')
        self.assertEqual(len(self.guard.rows()),before)
