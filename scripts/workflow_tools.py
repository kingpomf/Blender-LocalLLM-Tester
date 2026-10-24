"""Project-owned workflow controller behind MCP. No arbitrary host commands or GPU controls."""
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import re
import uuid
import subprocess
import os
import sys
import shutil
import time

from scripts.authoring_preflight import inspect_authoring
from scripts.checkpoint_bowling import publish_source,publish_render,sync_ledgers,update_fields,backup_and_write,replace_stage_table
from scripts.check_references import check as reference_check
from scripts.submission_guard import fingerprint,GuardBlocked
from scripts.validate_checkpoint import merge_report,local_render_checks,qualitative_evidence

VALIDATOR_SHA256='3cac4d432bf99f6fcaf4193737b629fa9edf083cffe1431096c409d3decc3493'
ROLES={'overview':'Overview','player':'Player','pindeck':'PinDeck','props':'Props'}


def atomic_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.next')
    temporary.write_text(json.dumps(data,indent=2)+'\n')
    temporary.replace(path)


class Workflow:
    def __init__(self,root,client,guard,validator_sha256=VALIDATOR_SHA256):
        self.root=Path(root);self.client=client;self.guard=guard
        self.directory=self.root/'.runtime/workflow'
        self.directory.mkdir(parents=True,exist_ok=True)
        self.path=self.directory/'state.json';self.lock=asyncio.Lock()
        self.validator_sha256=validator_sha256
        self.state={}
        self.review_processes={}

    def load(self):
        self.state=json.loads(self.path.read_text()) if self.path.exists() else {'jobs':{},'views':{},'validations':{},'reviews':{}}
        self.state.setdefault('reviews',{})
        if not self.state.get('current_source'):
            receipt=self.root/'artifacts/reports/checkpoint.json'
            if receipt.exists():
                data=json.loads(receipt.read_text())
                self.state.update(current_source=data['source_job'],checkpoint=data)

    def save(self):atomic_json(self.path,self.state)

    async def call(self,method,**arguments):
        async with self.lock:
            with (self.directory/'workflow.lock').open('a') as lock:
                try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:
                    return self.error('workflow_busy','Another workflow operation is publishing state. Retry status; no submission occurred.')
                self.load()
                try:return await getattr(self,method)(**arguments)
                finally:self.save()

    @staticmethod
    def error(code,message,**details):
        return {'ok':False,'recoverable':True,'submitted':False,'attempt_consumed':False,
                'code':code,'message':message,**details}

    def pending(self,exclude_view=None):
        rows=self.guard.rows()
        if any(not row['job'] for row in rows):
            raise GuardBlocked('STOP: uncertain submission exists; reconcile its accepted identity, never replay.')
        native=[r['job'] for r in rows if r['state'] in {'queued','running'}]
        views=[key for key,row in self.state['views'].items() if key!=exclude_view and row['state'] not in {'completed','failed','cancelled'}]
        reviews=[key for key,row in self.state['reviews'].items() if row['state'] not in {'completed','failed','cancelled'}]
        return native+views+reviews

    def current(self,source=None):
        current=self.state.get('current_source')
        if current and source and source!=current:
            return self.error('stale_source','Use the machine-tracked current asset source, not an older branch or a failed/camera job.',current_source=current)
        return source or current

    def mark_pending(self,job,source,operation):
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            path=self.root/name
            if path.exists():
                backup_and_write(self.root,name,update_fields(path.read_text(),{
                    'Pending job':job,'Pending source job':source or 'none','Workflow operation':operation}))

    def clear_pending(self,job):
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            path=self.root/name
            if path.exists() and f'- Pending job: {job}' in path.read_text():
                backup_and_write(self.root,name,update_fields(path.read_text(),{'Pending job':'none','Pending source job':'none'}))

    def mark_validation_required(self,source):
        build=self.root/'BUILD_STATUS.md'
        if build.exists():
            rows=[('IN_PROGRESS',f'Current source {source}; fixed measured validation pending.') for _ in range(9)]+[('NOT_STARTED','No verified final delivery yet.')]
            text=replace_stage_table(build.read_text(),rows)
            backup_and_write(self.root,'BUILD_STATUS.md',update_fields(text,{'Status':'IN_PROGRESS',
                'Next stage':'00 — current-source revalidation pending','Validation state':'pending'}))
        handoff=self.root/'HANDOFF.md'
        if handoff.exists():backup_and_write(self.root,'HANDOFF.md',update_fields(handoff.read_text(),{
            'Run status':'IN_PROGRESS','Current stage':'00 — current-source revalidation pending','Validation state':'pending'}))

    async def submit_native(self,spec,role,**metadata):
        pending=self.pending(exclude_view=metadata.get('view_id'))
        if pending:
            return self.error('pending_work','Poll the existing accepted job before another submission.',pending_jobs=pending,next_tool='blender_job_status')
        request_path=self.directory/'requests'/(fingerprint(spec)+'.json')
        if not request_path.exists():atomic_json(request_path,{'role':role,'spec':spec,'state':'reserved_before_guarded_submit'})
        row=await self.guard.submit(spec,self.client.rpc)
        atomic_json(request_path,{'role':role,'spec':spec,'state':'accepted','id':row['id']})
        if role=='asset':
            script=self.root/'artifacts/scripts'/('accepted_'+row['id']+'.py')
            if script.exists():assert script.read_text()==spec['code'], 'Accepted source snapshot changed'
            else:script.write_text(spec['code'])
        self.state['jobs'].setdefault(row['id'],{'role':role,'source':spec.get('source_job'),**metadata})
        self.save()
        self.mark_pending(row['id'],spec.get('source_job'),role)
        if row['state']=='completed':return await self.observe(row)
        return {'id':row['id'],'state':row['state'],'operation':role,'next_tool':'blender_job_status'}

    async def author(self,code,source_job=None):
        inspected=inspect_authoring(code)
        if not inspected['ok']:return inspected
        references=reference_check(self.root)
        if not references['passed']:
            return self.error('references_required','Complete the verified image reference phase first.',issues=references['issues'])
        selected=self.current(source_job)
        if isinstance(selected,dict):return selected
        return await self.submit_native({'operation':'author','code':code,**({'source_job':selected} if selected else {})},'asset')

    async def queue_validation(self,source):
        path=self.root/'artifacts/scripts/validate_bowling_pair01.py'
        code=path.read_text();digest=hashlib.sha256(code.encode()).hexdigest()
        if digest!=self.validator_sha256:
            return self.error('validator_changed','The operator-reviewed validator changed. Do not weaken it; restore/review with the operator before validation.')
        key=source+':'+digest
        saved=self.state['validations'].get(key)
        if saved and saved.get('id'):
            return await self.native_status(saved['id'])
        spec={'operation':'author','source_job':source,'code':code}
        previous=next((r for r in self.guard.rows() if r['fingerprint']==fingerprint(spec)),None)
        if previous:
            if not previous['job']:raise GuardBlocked('STOP: validation submission is uncertain; reconcile before retry')
            self.state['validations'][key]={'id':previous['job']}
            self.state['jobs'][previous['job']]={'role':'validation','source':source}
            self.save()
            return await self.native_status(previous['job'])
        self.state['validations'][key]={'state':'reservation_before_submit'};self.save()
        row=await self.submit_native(spec,'validation')
        if row.get('id'):
            self.state['validations'][key]={'id':row['id']};self.save()
        return row

    async def publish_validation(self,row):
        source=self.state['jobs'][row['id']]['source']
        if source!=self.state.get('current_source'):
            return self.error('stale_validation','Validation completed for an older scene; it will not replace current evidence.',source=source)
        fetched=await self.client.fetch(row['id'],'validation.json')
        native=json.loads(Path(fetched['path']).read_text())
        assert native['read_only'] and native['source_fingerprint_before']==native['source_fingerprint_after']
        merged=merge_report(native,local_render_checks(self.root,source),source,row['id'],qualitative_evidence(self.root,source))
        data=json.dumps(merged,indent=2)+'\n';digest=hashlib.sha256(data.encode()).hexdigest()
        archive=self.directory/'validated-reports'/f'{digest}.json'
        archive.parent.mkdir(parents=True,exist_ok=True)
        if not archive.exists():archive.write_text(data)
        (self.root/'artifacts/reports/validation.json').write_text(data)
        self.state['validation']={'source_job':source,'job_id':row['id'],'sha256':digest,
            'path':str(archive.relative_to(self.root)),'stage_results':merged['stage_results'],
            'passed':merged['passed'],'fail_count':merged['fail_count'],'unresolved_count':merged['unresolved_count']}
        self.save()
        sync_ledgers(self.root)
        return {'id':row['id'],'state':'completed','operation':'validation','execution_succeeded':True,
                'asset_passed':merged['passed'],'validation':self.state['validation'],
                'remaining_checks':[{'id':c['id'],'status':c['status'],'observed':str(c['observed'])[:240]} for c in merged['checks'] if c['status']!='PASS']}

    def sync_failure_mirrors(self):
        if self.state.get('validation') and self.state['validation']['source_job']==self.state.get('current_source') and not self.pending():
            sync_ledgers(self.root)

    async def observe(self,row):
        for attempt in self.guard.rows():
            if attempt['job']==row['id']:self.guard.update(attempt['fingerprint'],row)
        metadata=self.state['jobs'].get(row['id'])
        if row['state'] in {'failed','cancelled'}:
            self.clear_pending(row['id'])
            self.sync_failure_mirrors()
        if row['state']!='completed' or metadata is None:
            return {k:row[k] for k in ['id','state','error','progress','diagnostics'] if k in row}
        self.clear_pending(row['id'])
        role=metadata['role']
        if role=='validation':return await self.publish_validation(row)
        if role=='asset':
            if not metadata.get('published'):
                receipt=await publish_source(self.root,row['id'],self.client)
                self.state.update(current_source=row['id'],checkpoint=receipt)
                self.state.pop('validation',None)
                self.state.pop('delivery',None)
                self.state.pop('delivery_export',None)
                self.mark_validation_required(row['id'])
                qualitative=self.root/'artifacts/reports/qualitative-evidence.json'
                if qualitative.exists() and json.loads(qualitative.read_text()).get('asset_source')!=row['id']:
                    archive=self.directory/'stale-evidence'/('qualitative-'+hashlib.sha256(qualitative.read_bytes()).hexdigest()+'.json')
                    archive.parent.mkdir(parents=True,exist_ok=True)
                    if not archive.exists():shutil.copy2(qualitative,archive)
                    qualitative.unlink()
                metadata['published']=True;self.save()
            validation=await self.queue_validation(row['id'])
            return {'id':row['id'],'state':'completed','operation':'asset','checkpoint':self.state['checkpoint'],
                    'execution_succeeded':True,'asset_acceptance':'validation required; job success is not stage PASS',
                    'validation_job':validation,'next_tool':'blender_job_status'}
        if role=='direct_render':
            image=await publish_render(self.root,metadata['view_role'],row['id'],metadata['asset_source'],self.client)
            return {'id':row['id'],'state':'completed','artifact':image,'visual_acceptance':'unreviewed'}
        if role=='delivery_export':
            selected=metadata['source']
            proof=await self.client.fetch(row['id'],'report.json')
            actual=json.loads(Path(proof['path']).read_text())
            assert actual.get('fixed_export_pipeline') and actual.get('passed') and len(actual.get('roundtrip_checks',[]))==6
            base=await self.client.fetch(selected,'scene.json');after=await self.client.fetch(row['id'],'scene.json')
            from scripts.checkpoint_bowling import saved_mesh_signature
            assert saved_mesh_signature(json.loads(Path(base['path']).read_text()))==saved_mesh_signature(json.loads(Path(after['path']).read_text())), 'Export/roundtrip mutated source mesh descriptions'
            outputs=[]
            for item in row['manifest']['artifacts']:
                if item['path'].endswith('.glb'):
                    fetched=await self.client.fetch(row['id'],item['path'])
                    target=self.root/'artifacts/exports'/item['path']
                    assert item['path'] in {'BowlingPair01.glb','BowlingPair01_Collision.glb','BowlingPin01.glb','BowlingBall01.glb','BowlingBall02.glb','BowlingBall03.glb'}
                    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fetched['path'],target)
                    outputs.append({'path':str(target.relative_to(self.root)),'bytes':fetched['bytes'],'sha256':fetched['sha256']})
            assert len(outputs)==6
            self.state['delivery_export']={'source':selected,'job_id':row['id'],'artifacts':outputs,'roundtrips':actual['roundtrip_checks']};self.save()
            atomic_json(self.root/'artifacts/reports/export-receipt.json',self.state['delivery_export'])
            return {'id':row['id'],'state':'completed','exports':outputs,'roundtrip_passed':True,'next':'Write BUILD_REPORT.md and ASSET_GUIDE.md; call blender_finish_delivery.'}
        return {'id':row['id'],'state':'completed','operation':role,'execution_succeeded':True,
                **({'workflow_id':metadata['view_id']} if metadata.get('view_id') else {})}

    async def native_status(self,job_id):
        assert re.fullmatch('[a-f0-9]{32}',job_id)
        return await self.observe(await self.client.rpc('status',{'job_id':job_id}))

    async def status(self,job_id):
        if job_id.startswith('view-'):return await self.view_status(job_id)
        if job_id.startswith('review-'):return await self.review_status(job_id)
        return await self.native_status(job_id)

    async def checkpoint(self,job_id):
        assert re.fullmatch('[a-f0-9]{32}',job_id)
        row=await self.client.rpc('status',{'job_id':job_id})
        if row['state']!='completed' or row['spec']['operation']!='author':
            return self.error('completed_source_required','Only completed same-trial authoring jobs can be published.')
        current=self.state.get('current_source')
        if current and job_id!=current and row['spec'].get('source_job')!=current:
            return self.error('stale_source','Checkpoint must be current or its direct completed repair child.',current_source=current)
        self.state['jobs'].setdefault(job_id,{'role':'asset','source':row['spec'].get('source_job')})
        return await self.observe(row)

    async def validate(self,source_job=None):
        selected=self.current(source_job)
        if isinstance(selected,dict):return selected
        if not selected:return self.error('source_required','Author a scene first.')
        return await self.queue_validation(selected)

    async def render_view(self,role,source_job=None,resolution=None,samples=8):
        selected=self.current(source_job)
        if isinstance(selected,dict):return selected
        if not selected:return self.error('source_required','Author a scene first.')
        assert role in ROLES
        if type(samples) is not int or not 1<=samples<=64:return self.error('samples_out_of_bounds','Use1..64 samples; default8.')
        resolution=resolution or [1280,720]
        if not (len(resolution)==2 and all(type(v) is int for v in resolution) and 1280<=resolution[0]<=2048 and 720<=resolution[1]<=2048):
            return self.error('resolution_out_of_bounds','Named delivery views require at least1280x720 and at most2048 per side.')
        pending=self.pending()
        if pending:return self.error('pending_work','Poll accepted work first.',pending_jobs=pending)
        fetched=await self.client.fetch(selected,'scene.json');scene=json.loads(Path(fetched['path']).read_text())
        camera='CAM_BowlingPair01_'+ROLES[role]
        if not any(o['name']==camera and o['type']=='CAMERA' for o in scene['objects']):
            return self.error('missing_camera','Author the named camera without rendering, then use this tool.',camera=camera)
        key=hashlib.sha256(json.dumps([selected,role,resolution,samples]).encode()).hexdigest()
        existing=next((key_id for key_id,view in self.state['views'].items() if view['request_key']==key),None)
        if existing:return await self.view_status(existing)
        view_id='view-'+uuid.uuid4().hex
        view={'request_key':key,'source':selected,'role':role,'resolution':resolution,'samples':samples,'state':'camera_submission_uncertain'}
        self.state['views'][view_id]=view;self.save()
        code=("import bpy\nscene=bpy.context.scene\n"+
              f"scene.camera=bpy.data.objects[{camera!r}]\n"+
              "scene.render.engine='CYCLES'\nscene.cycles.device='CPU'\n"+
              f"report={{'selected_camera':{camera!r},'rendered':False}}\n")
        result=await self.submit_native({'operation':'author','source_job':selected,'code':code},'view_camera',view_id=view_id)
        assert result.get('id'), result
        view.update(camera_job=result['id'],state='selecting_camera');self.save()
        return {'id':view_id,'state':'queued','camera_job':result['id'],'role':role,'next_tool':'blender_job_status'}

    async def view_status(self,view_id):
        view=self.state['views'].get(view_id)
        if not view:return self.error('unknown_view','Unknown workflow view ID; never resubmit after uncertain acceptance.')
        if view['state']=='cancelled':return {'id':view_id,'state':'cancelled'}
        if not view.get('camera_job'):
            raise GuardBlocked('STOP: camera submission identity is uncertain; operator reconciliation required')
        camera=await self.client.rpc('status',{'job_id':view['camera_job']})
        await self.observe(camera)
        if camera['state'] in {'failed','cancelled'}:
            view['state']=camera['state'];self.save();self.sync_failure_mirrors()
            return {'id':view_id,'state':camera['state'],'native_job':camera['id'],'next_tool':'blender_job_diagnostics'}
        if camera['state']!='completed':return {'id':view_id,'state':'running','phase':'camera_selection','native_job':camera['id']}
        if view.get('cancel_requested') and not view.get('render_job'):
            view['state']='cancelled';return {'id':view_id,'state':'cancelled'}
        if not view.get('render_job'):
            if view.get('state')=='render_submission_uncertain':raise GuardBlocked('STOP: render submission identity is uncertain; reconcile before retry')
            pending=self.pending(exclude_view=view_id)
            if pending:return self.error('pending_work','Poll existing native job before the render is admitted.',pending_jobs=pending,view_id=view_id)
            view['state']='render_submission_uncertain';self.save()
            result=await self.submit_native({'operation':'render','source_job':camera['id'],'frames':[1],
                'resolution':view['resolution'],'samples':view['samples']},'view_render',view_id=view_id)
            assert result.get('id'),result
            view.update(render_job=result['id'],state='rendering');self.save()
            return {'id':view_id,'state':'running','phase':'render','native_job':result['id']}
        render=await self.client.rpc('status',{'job_id':view['render_job']});await self.observe(render)
        if render['state']=='completed':
            image=await publish_render(self.root,view['role'],render['id'],view['source'],self.client)
            view.update(state='completed',artifact=image);self.save()
            measured=await self.queue_validation(view['source'])
            return {'id':view_id,'state':'completed','artifact':image,'asset_source':view['source'],
                    'measured_validation':measured,
                    'visual_acceptance':'not yet reviewed; successful rendering is not Stage07 PASS'}
        if render['state'] in {'failed','cancelled'}:
            view['state']=render['state'];self.save();self.sync_failure_mirrors()
        return {'id':view_id,'state':render['state'],'phase':'render','native_job':render['id'],'error':render.get('error')}

    async def publish(self,role,job_id,asset_source_job=None):
        selected=self.current(asset_source_job)
        if isinstance(selected,dict):return selected
        image=await publish_render(self.root,role,job_id,selected,self.client)
        return {'published':True,'artifact':image,'visual_acceptance':'unreviewed'}

    async def cancel(self,job_id):
        if job_id.startswith('review-'):
            return self.error('review_cancellation_requires_reconciliation','The bounded image-description HTTP request may already be running. Preserve its ID; do not replay or kill an unverified process.')
        if job_id.startswith('view-'):
            view=self.state['views'].get(job_id)
            if not view:return self.error('unknown_view','Unknown view ID')
            native=view.get('render_job') or view.get('camera_job')
            if not native:raise GuardBlocked('STOP: view submission uncertain; reconcile before cancellation')
            view['cancel_requested']=True
            row=await self.client.rpc('cancel',{'job_id':native});await self.observe(row)
            if row['state'] in {'completed','failed','cancelled'}:
                view['state']='cancelled';self.save();self.sync_failure_mirrors()
                return {'id':job_id,'state':'cancelled','native_job':native,'native_state':row['state']}
            return {'id':job_id,'state':'running','cancellation_requested':True,'native_job':native}
        row=await self.client.rpc('cancel',{'job_id':job_id})
        return await self.observe(row)

    async def diagnostics(self,job_id):
        if job_id.startswith('view-'):
            view=self.state['views'].get(job_id)
            if not view:return self.error('unknown_view','Unknown view ID')
            job_id=view.get('render_job') or view.get('camera_job')
        if job_id and job_id.startswith('review-'):
            review=self.state['reviews'].get(job_id)
            if not review:return self.error('unknown_review','Unknown review ID')
            path=self.root/review['folder']/'helper.log'
            if not path.exists():return {'id':job_id,'state':review['state'],'log':'No helper log available yet'}
            with path.open('rb') as file:
                file.seek(max(0,path.stat().st_size-16384))
                return {'id':job_id,'state':review['state'],'log':file.read(16384).decode(errors='replace')}
        return await self.client.rpc('diagnostics',{'job_id':job_id})

    async def workflow_status(self):
        # Machine-owned report restores accidental edits to the stage mirrors.
        validation=self.state.get('validation')
        if validation and validation['source_job']==self.state.get('current_source'):
            saved=self.root/validation['path']
            if hashlib.sha256(saved.read_bytes()).hexdigest()!=validation['sha256']:
                raise GuardBlocked('STOP: machine-owned validation receipt changed; reconcile before work')
            (self.root/'artifacts/reports/validation.json').write_bytes(saved.read_bytes())
            if not self.pending():sync_ledgers(self.root)
        if self.state.get('delivery',{}).get('source')==self.state.get('current_source'):
            self.complete_mirrors()
        summary=self.guard.summary()
        summary.pop('accepted_jobs',None)
        remaining=[]
        if validation:
            report=json.loads((self.root/validation['path']).read_text())
            remaining=[{'id':c['id'],'stage':c['stage'],'status':c['status'],'expected':c.get('expected'),
                        'observed':str(c.get('observed'))[:320]} for c in report['checks'] if c['status']!='PASS']
        return {'current_source':self.state.get('current_source'),'checkpoint':self.state.get('checkpoint'),
                'validation':validation,'pending_jobs':self.pending(),'guard':summary,
                'remaining_checks':remaining,
                'views':{key:{k:value for k,value in row.items() if k in {'role','state','render_job','camera_job'}} for key,row in self.state['views'].items()},
                'instructions':'Use author for scene edits only. Poll every accepted ID. Checkpoints/validation/stage mirrors are automatic. Use render_view for queued views; never render inline or manually claim PASS.'}

    async def render(self,source_job,frames,resolution,samples):
        selected=self.current(source_job)
        if isinstance(selected,dict):return selected
        if frames!=[1]:return self.error('use_named_view','This asset workflow uses named camera views. Use blender_render_view.')
        if type(samples) is not int or not 1<=samples<=64:return self.error('samples_out_of_bounds','Use1..64 samples; default8.')
        fetched=await self.client.fetch(selected,'scene.json');scene=json.loads(Path(fetched['path']).read_text())
        role=next((key for key,value in ROLES.items() if scene.get('active_camera')=='CAM_BowlingPair01_'+value),None)
        if role is None:return self.error('use_named_view','Use blender_render_view to select a known camera; no fallback camera accepted.')
        return await self.submit_native({'operation':'render','source_job':selected,'frames':frames,
            'resolution':resolution,'samples':samples},'direct_render',asset_source=selected,view_role=role)

    async def review_presentation(self):
        source=self.state.get('current_source');path=self.root/'artifacts/reports/render-manifest.json'
        if not source or not path.exists():return self.error('renders_required','Render all four current views first.')
        manifest=json.loads(path.read_text())
        images=[{key:value for key,value in item.items() if key in {'role','path','sha256','bytes','job_id','source_job','asset_source'}} for item in manifest['images']]
        if manifest['asset_source']!=source or len(images)!=4 or {i['role'] for i in images}!=set(ROLES):
            return self.error('current_views_required','All four views must come from the current asset source.')
        if any(not c['passed'] for c in local_render_checks(self.root,source) if not c['id'].endswith('_visibility')):
            return self.error('render_artifact_invalid','Repair image hashes/dimensions/provenance before review.')
        report=json.loads((self.root/'artifacts/reports/validation.json').read_text())
        guide=self.root/'artifacts/reports/ASSET_GUIDE.md'
        request={'asset_source':source,'images':images,'asset_guide':guide.read_text()[:20000] if guide.exists() else '',
                 'geometry_facts':{name:{k:f[k] for k in ['signed_volume','nonmanifold_edges','degenerate_faces','local_center']}
                                   for name,f in report.get('facts',{}).items()}}
        key=hashlib.sha256(json.dumps(request,sort_keys=True).encode()).hexdigest()
        previous=next((review_id for review_id,review in self.state['reviews'].items() if review['request_key']==key),None)
        if previous:return await self.review_status(previous)
        if self.pending():return self.error('pending_work','Finish accepted work first.',pending_jobs=self.pending())
        review_id='review-'+uuid.uuid4().hex;folder=self.directory/'reviews'/review_id
        folder.mkdir(parents=True);atomic_json(folder/'request.json',request)
        review={'state':'submission_uncertain','source':source,'request_key':key,'folder':str(folder.relative_to(self.root)),'created':time.time()}
        self.state['reviews'][review_id]=review;self.save()
        with (folder/'helper.log').open('ab') as log:
            process=subprocess.Popen([sys.executable,str(self.root/'scripts/review_presentation.py'),str(folder)],cwd=self.root,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        review.update(state='running',pid=process.pid);self.save()
        self.review_processes[review_id]=process
        return {'id':review_id,'state':'running','operation':'pixel_review','next_tool':'blender_job_status'}

    async def review_status(self,review_id):
        review=self.state['reviews'].get(review_id)
        if not review:return self.error('unknown_review','Unknown review ID; no replay was performed.')
        folder=self.root/review['folder'];path=folder/'result.json'
        if not path.exists():
            process=self.review_processes.get(review_id)
            if process is not None and process.poll() is not None or time.time()-review.get('created',time.time())>650:
                review['state']='failed';self.save()
                return {'id':review_id,'state':'failed','reason':'Review helper ended or exceeded its bounded wait without a completed receipt; preserve request and reconcile, never replay automatically.','log':str(folder/'helper.log')}
            try:os.kill(review['pid'],0)
            except (OSError,KeyError):
                review['state']='failed';self.save()
                return {'id':review_id,'state':'failed','reason':'Image helper exited without completion. Preserve request/uncertainty; operator reconciliation required.','log':str(folder/'helper.log')}
            return {'id':review_id,'state':'running','operation':'pixel_review'}
        result=json.loads(path.read_text());request=json.loads((folder/'request.json').read_text())
        if request['asset_source']!=self.state.get('current_source'):
            review['state']='failed';return self.error('stale_review','Asset changed; review cannot approve current images.')
        manifest_path=self.root/'artifacts/reports/render-manifest.json';manifest=json.loads(manifest_path.read_text())
        by_role={i['role']:i for i in request['images']}
        for item in result['review']['views']:
            image=next(i for i in manifest['images'] if i['role']==item['role'])
            assert image['sha256']==by_role[item['role']]['sha256']
            image['visual_review']={'sha256':image['sha256'],'passed':item['passed'],'observations':item['observations'],'reviewer':'fixed pixel helper '+result['model']}
        atomic_json(manifest_path,manifest)
        criteria=[]
        allowed={'S04_Ball_01_holes_visual','S04_Ball_02_holes_visual','S04_Ball_03_holes_visual',
                 'S05_return_opening','S05_scoreboard_labels','S05_masking_labels','S06_normals_and_static_origins'}
        for item in result['review'].get('criteria',[]):
            assert item['id'] in allowed and item['role'] in ROLES and type(item['passed']) is bool and len(item['observations'])>=80
            criteria.append({'id':item['id'],'passed':item['passed'],'observations':item['observations'],
                'reviewer':'fixed pixel/geometry helper '+result['model'],'render_sha256':by_role[item['role']]['sha256']})
        atomic_json(self.root/'artifacts/reports/qualitative-evidence.json',{'asset_source':review['source'],'criteria':criteria})
        review.update(state='completed',result=result['review']);self.save()
        measured=await self.queue_validation(review['source'])
        return {'id':review_id,'state':'completed','review':result['review'],'measured_validation':measured}

    async def export_delivery(self):
        measured=self.state.get('validation')
        if not measured or measured['source_job']!=self.state.get('current_source') or not measured['passed']:
            return self.error('acceptance_required','Complete current measured/visual acceptance before final export.')
        code=(self.root/'scripts/export_delivery_payload.py').read_text()
        return await self.submit_native({'operation':'author','source_job':self.state['current_source'],'code':code},'delivery_export')

    async def finish_delivery(self):
        measured=self.state.get('validation');exported=self.state.get('delivery_export');source=self.state.get('current_source')
        if not measured or not measured['passed'] or not exported or exported['source']!=source:
            return self.error('delivery_not_ready','Current acceptance and fixed native export/roundtrip proof required.')
        paths=[self.state['checkpoint']['path'],'artifacts/reports/validation.json','artifacts/reports/BUILD_REPORT.md','artifacts/reports/ASSET_GUIDE.md']
        paths.extend(a['path'] for a in exported['artifacts'])
        renders=json.loads((self.root/'artifacts/reports/render-manifest.json').read_text())
        if renders['asset_source']!=source or any(not c['passed'] for c in local_render_checks(self.root,source)):
            return self.error('render_acceptance_required','Current verified useful beauty images are required.')
        paths.extend(i['path'] for i in renders['images'])
        refs=json.loads((self.root/'artifacts/references/manifest.json').read_text())
        paths.extend(['artifacts/references/manifest.json','artifacts/references/DESIGN_GUIDE.md'])
        paths.extend(i['path'] for i in refs['images']);paths.extend(i['receipt'] for i in refs['images'])
        artifacts=[];expected={a['path']:a['sha256'] for a in exported['artifacts']}
        for relative in sorted(set(paths)):
            path=(self.root/relative).resolve()
            if not path.is_relative_to((self.root/'artifacts').resolve()) or not path.is_file():return self.error('missing_delivery','Required deliverable missing.',path=relative)
            data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
            if relative in expected and digest!=expected[relative]:return self.error('export_changed','GLB changed after roundtrip.',path=relative)
            if relative.endswith(('BUILD_REPORT.md','ASSET_GUIDE.md')) and len(data)<200:return self.error('documentation_incomplete','Write substantive measured documentation.',path=relative)
            artifacts.append({'path':relative,'bytes':len(data),'sha256':digest})
        manifest={'final_source_job':source,'export_jobs':[exported['job_id']],'render_sources':renders['images'],
                  'roundtrip_job':exported['job_id'],'artifacts':artifacts}
        path=self.root/'artifacts/reports/DELIVERY_MANIFEST.json';atomic_json(path,manifest)
        self.state['delivery']={'source':source,'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'artifacts':artifacts}
        self.save();self.complete_mirrors()
        return {'state':'completed','asset_source':source,'delivery_manifest':str(path.relative_to(self.root)),'roundtrip_job':exported['job_id']}

    def complete_mirrors(self):
        delivery=self.state['delivery'];source=delivery['source']
        for artifact in delivery['artifacts']:
            path=self.root/artifact['path']
            assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==artifact['sha256'], 'Delivery bytes changed'
        build=self.root/'BUILD_STATUS.md';text=build.read_text()
        text=re.sub(r'^\| 09 \|[^\n]+',f'| 09 | Export and delivery | PASS | Fixed export/roundtrip and delivery manifest verified; source {source}. |',text,flags=re.M)
        backup_and_write(self.root,'BUILD_STATUS.md',update_fields(text,{'Status':'COMPLETE','Next stage':'none — complete','Controller':'COMPLETE'}))
        handoff=self.root/'HANDOFF.md'
        backup_and_write(self.root,'HANDOFF.md',update_fields(handoff.read_text(),{'Run status':'COMPLETE','Current stage':'none — complete','Next action':'Verified delivery complete; review DELIVERY_MANIFEST.json.'}))
