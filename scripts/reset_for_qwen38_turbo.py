"""Archive the complete retired trial before the user-authorized clean model trial."""
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.blender_api import load_catalog
from scripts.checkpoint_bowling import STAGES
from scripts.probe_coding_model import probe
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import Workflow,atomic_json
from scripts.trial_settings import TRIAL,MODEL
import blender52_mcp as worker

NEW_MODEL='z6-llama/qwen38-turbo'
NEW_TRIAL='bowling52-qwen38-turbo-20261025-r1'
ARCHIVE='artifacts/archive/qwen36-final-before-qwen38-turbo-20261025'
TOOLS={'artifacts/scripts/validate_bowling_pair01.py','artifacts/reports/blender-api-catalog.json',
       'artifacts/reports/blender-api-catalog-receipt.json'}


async def main():
    archive=ROOT/ARCHIVE
    assert not archive.exists(),'Fresh reset already attempted; inspect archived journal, never repeat it'
    assert TRIAL!=NEW_TRIAL and MODEL!=NEW_MODEL,'Archive old configuration before changing the selected model'
    model=probe(NEW_MODEL);assert model['advertised'] and model['tool_call']
    runtime=ROOT/'.runtime'
    with (runtime/'autonomous-run/controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'autonomous-run/state.json').read_text())
        assert state['state'] in {'blocked','interrupted','completed'} and not state.get('client_pid')
        guard=SubmissionGuard(runtime/'blender52/submissions.sqlite')
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        status=await Workflow(ROOT,client,guard).call('workflow_status')
        assert not status['pending_jobs']
        rows=guard.rows()
        for row in rows:
            assert row['job'] and row['state'] in {'completed','failed','cancelled'}
            observed=await client.rpc('status',{'job_id':row['job']})
            assert observed['state']==row['state'],'Remote state mismatch: reconcile before reset'
        assert load_catalog(ROOT) is not None
        archive.mkdir(parents=True)
        journal={'state':'archiving','created':time.time(),'old_model':MODEL,'old_trial':TRIAL,'new_model':NEW_MODEL,
            'new_trial':NEW_TRIAL,'old_attempts':len(rows),'old_failures':sum(r['state'] in {'failed','cancelled'} for r in rows),
            'preserved_tools':{},'moves':[],'model_probe':model}
        for relative in TOOLS:journal['preserved_tools'][relative]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
        atomic_json(archive/'ARCHIVE_MANIFEST.json',journal)
        # Preserve the exact launch instructions/config and all authored documents.
        for relative in ['opencode.json','AGENTS.md','BUILD_STATUS.md','HANDOFF.md','CONTROLLED_CONTINUATION.md',
                         'REFERENCE_IMAGES.md','MODEL_SETUP.md','README.md','WORKER_GUIDE.md','RUNTIME_52.md',
                         '.opencode/commands','scripts/trial_settings.py','testing/ACTIVE_CONTINUATION.json']:
            source=ROOT/relative
            if source.exists():
                target=archive/'project-before'/relative;target.parent.mkdir(parents=True,exist_ok=True)
                if source.is_dir():shutil.copytree(source,target)
                else:shutil.copy2(source,target)
        for name in ['blend','downloads','exports','references','renders','reports','scripts']:
            source=ROOT/'artifacts'/name;target=archive/'artifacts'/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(source),str(target));source.mkdir()
            journal['moves'].append('artifacts/'+name);atomic_json(archive/'ARCHIVE_MANIFEST.json',journal)
        for relative in TOOLS:
            target=ROOT/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(archive/relative,target)
            assert hashlib.sha256(target.read_bytes()).hexdigest()==journal['preserved_tools'][relative]
        for name in ['ASSET_GUIDE.md','BUILD_REPORT.md']:
            source=ROOT/name
            if source.exists():shutil.move(str(source),str(archive/name))
        # Renaming runtime retains original SQLite databases, accepted IDs, events and locks.
        shutil.move(str(runtime),str(archive/'runtime'))
        runtime.mkdir()
        for folder in ['blend','exports','references','renders','reports','scripts']:
            (ROOT/'artifacts'/folder/'.gitkeep').touch()
        fresh=SubmissionGuard(runtime/'blender52/submissions.sqlite')
        assert fresh.rows()==[]
        (ROOT/'testing/ACTIVE_CONTINUATION.json').unlink(missing_ok=True)
        common={'Next stage':'00 — Contract and scene safety','Active source job':'none','Accepted job IDs':'none',
            'Default model':NEW_MODEL,'Actual model used':'not started','Trial queue':worker.REMOTE_APP+'/var/'+NEW_TRIAL,
            'Controller':'NOT_STARTED; fresh detached launch authorized','Active checkpoint':'none','Reference phase':'NOT_STARTED',
            'Pending reference job':'none','Pending job':'none','Pending source job':'none','Failure budget':'6 hard/source20 total; current hard failures0; API corrections0; fresh trial',
            'Next action':'Read CONTROLLED_CONTINUATION.md; create fresh references, then build Stage00 in a new session.'}
        metadata='\n'.join('- '+key+': '+value for key,value in common.items())
        table='\n'.join(f'| {i:02d} | {STAGES[i]} | NOT_STARTED | Fresh Qwen3.8 Turbo trial; no stage accepted. |' for i in range(10))
        (ROOT/'BUILD_STATUS.md').write_text('# BowlingPair01 — fresh Qwen3.8 Turbo trial\n\n- Status: NOT_STARTED\n'+metadata+'\n\n## Stage ledger\n\n| Stage | Name | Result | Evidence |\n| --- | --- | --- | --- |\n'+table+'\n\n## Next action\n\n'+common['Next action']+'\n')
        (ROOT/'HANDOFF.md').write_text('# BowlingPair01 — fresh Qwen3.8 Turbo handoff\n\n- Run status: NOT_STARTED\n- Current stage: 00 — Contract and scene safety\n- Last verified source job: none\n- Latest verified local checkpoint: none\n'+metadata+'\n')
        journal.update(state='archived_fresh_state_ready',completed=time.time(),fresh_attempts=0,fresh_asset_source=None)
        atomic_json(archive/'ARCHIVE_MANIFEST.json',journal)
        atomic_json(runtime/'fresh-trial.json',{'model':NEW_MODEL,'trial':NEW_TRIAL,'archive':ARCHIVE,'created':time.time()})
        print(json.dumps({'archived':ARCHIVE,'old_attempts':len(rows),'old_failures':journal['old_failures'],
            'fresh_model':NEW_MODEL,'fresh_trial':NEW_TRIAL,'fresh_attempts':0,'fresh_asset':None,'references':'NOT_STARTED'},indent=2))


if __name__=='__main__':asyncio.run(main())
