import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
from scripts.checkpoint_bowling import update_fields, replace_stage_table, saved_mesh_signature, sync_ledgers
from scripts.submission_guard import SubmissionGuard
from scripts.validate_checkpoint import local_render_checks, merge_report, qualitative_evidence


class CheckpointTests(unittest.TestCase):
    def test_failed_initial_validator_allows_honest_sync_without_inventing_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source='a'*32;failed='b'*32
            guard=SubmissionGuard(root/'.runtime/blender52/submissions.sqlite')
            with guard.connect() as db:
                db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',('source','EMPTY','author',source,'completed'))
                db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',('validation',source,'author',failed,'failed'))
            (root/'artifacts/reports').mkdir(parents=True)
            scene=root/'scene.blend';scene.write_bytes(b'verified fixture')
            (root/'artifacts/reports/checkpoint.json').write_text(json.dumps({'source_job':source,'path':'scene.blend',
                'sha256':hashlib.sha256(scene.read_bytes()).hexdigest()}))
            (root/'.runtime/workflow').mkdir()
            state=root/'.runtime/workflow/state.json'
            state.write_text(json.dumps({'jobs':{}}))
            for filename in ['BUILD_STATUS.md','HANDOFF.md']:
                (root/filename).write_text('# Fixture\n\n## Stage ledger\n\n## Next action\n')
            with self.assertRaisesRegex(AssertionError,'reconciled failed validator'):sync_ledgers(root)
            state.write_text(json.dumps({'jobs':{failed:{'role':'validation','source':source}}}))
            result=sync_ledgers(root)
            self.assertEqual(result['failure_count'],1)
            self.assertEqual(result['next_stage'],'00')
            text=(root/'BUILD_STATUS.md').read_text()
            self.assertNotIn('| PASS |',text)
            self.assertIn('FAILED execution',text)
            self.assertFalse((root/'artifacts/reports/validation.json').exists())

    def test_camera_revision_ignores_unused_material_purge_but_checks_used_materials(self):
        base={'objects':[{'name':'Cube','type':'MESH','materials':['Wood'],'location':[0,0,0]}],
              'materials':[{'name':'Wood','color':[1,0,0]},{'name':'Unused','color':[0,1,0]}]}
        camera={'objects':base['objects'],'materials':[base['materials'][0]]}
        self.assertEqual(saved_mesh_signature(base),saved_mesh_signature(camera))
        changed={'objects':base['objects'],'materials':[{'name':'Wood','color':[0,0,1]}]}
        self.assertNotEqual(saved_mesh_signature(base),saved_mesh_signature(changed))

    def test_metadata_updates_remove_duplicates_without_dropping_evidence(self):
        text='# Test\n\n- Status: old\n- Next stage: old\n- Status: conflicting\n\nEvidence kept.\n'
        output=update_fields(text,{'Status':'IN_PROGRESS','Next stage':'02 — Gutters'})
        self.assertEqual(output.count('- Status:'),1)
        self.assertIn('Evidence kept.',output)
        self.assertIn('- Status: IN_PROGRESS',output)

    def test_stage_table_has_exactly_ten_rows_and_keeps_next_section(self):
        text='# Test\n\n## Stage ledger\n\n| 02 | X | REPAIRING | old |\n| 02 | X | PASS | wrong |\n\n## Next action\nPreserve this.\n'
        output=replace_stage_table(text,[('NOT_STARTED','') for _ in range(10)])
        self.assertEqual(sum(line.startswith('| 0') for line in output.splitlines()),10)
        self.assertNotIn('REPAIRING',output)
        self.assertIn('Preserve this.',output)


class RenderValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'artifacts/renders').mkdir(parents=True)
        (self.root/'artifacts/reports').mkdir(parents=True)
        self.source='a'*32
        self.images=[]
        for index,role in enumerate(['overview','player','pindeck','props']):
            path=self.root/'artifacts/renders'/f'{role}.png'
            Image.new('RGB',(1280,720),(index*60,90,180)).save(path)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            self.images.append({'role':role,'path':str(path.relative_to(self.root)),'bytes':path.stat().st_size,
                                'sha256':digest,'visual_review':{'sha256':digest,'passed':False,
                                'observations':'Actual image review: required asset features are not visible in this fixture.'}})
        self.manifest=self.root/'artifacts/reports/render-manifest.json'
        self.manifest.write_text(json.dumps({'asset_source':self.source,'images':self.images}))

    def test_existing_valid_pngs_do_not_imply_visual_pass(self):
        checks=local_render_checks(self.root,self.source)
        self.assertTrue(all(c['passed'] for c in checks if c['id'].endswith('_artifact')))
        self.assertEqual(sum(not c['passed'] for c in checks),4)

    def test_wrong_asset_source_and_tampered_png_fail(self):
        (self.root/self.images[0]['path']).write_bytes(b'not a PNG')
        checks=local_render_checks(self.root,'b'*32)
        self.assertFalse(next(c for c in checks if c['id']=='S07_local_source')['passed'])
        self.assertFalse(next(c for c in checks if c['id']=='S07_local_overview_artifact')['passed'])

    def test_missing_render_proof_is_not_hardcoded_true(self):
        self.manifest.unlink()
        self.assertFalse(local_render_checks(self.root,self.source)[0]['passed'])

    def test_review_can_resolve_unknown_but_cannot_override_geometry_failure(self):
        raw={'checks':[{'id':'S04_holes','stage':'04','status':'UNRESOLVED','passed':False},
                       {'id':'S04_diameter','stage':'04','status':'FAIL','passed':False}]}
        reviews={'S04_holes':{'passed':True},'S04_diameter':{'passed':True}}
        result=merge_report(raw,[],self.source,'job',reviews)
        self.assertEqual(next(c for c in result['checks'] if c['id']=='S04_holes')['status'],'PASS')
        self.assertEqual(next(c for c in result['checks'] if c['id']=='S04_diameter')['status'],'FAIL')
        self.assertFalse(result['passed'])

    def test_missing_stage_coverage_stays_unresolved(self):
        result=merge_report({'checks':[]},[],self.source,'job')
        self.assertFalse(result['passed'])
        self.assertEqual(result['unresolved_count'],8)

    def test_qualitative_evidence_is_bound_to_image_and_asset(self):
        path=self.root/'artifacts/reports/qualitative-evidence.json'
        path.write_text(json.dumps({'asset_source':self.source,'criteria':[{'id':'S04_holes','passed':True,
            'reviewer':'fixture-reviewer','render_sha256':self.images[0]['sha256'],
            'observations':'Actual image inspection notes naming the recessed openings and their visible wall geometry, not intended prompt text.'}]}))
        self.assertIn('S04_holes',qualitative_evidence(self.root,self.source))
        with self.assertRaises(AssertionError):qualitative_evidence(self.root,'b'*32)


if __name__=='__main__':unittest.main()
