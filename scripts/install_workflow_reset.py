"""One explicit operator install/reset/reconciliation, with immutable old history."""
import asyncio
from contextlib import closing
import fcntl
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.submission_guard import SubmissionGuard
from scripts.checkpoint_bowling import publish_source
from scripts.workflow_tools import Workflow,atomic_json
import blender52_mcp as worker

SOURCE='756846c5415e4c5e92f159389a87eeb0'


async def main():
    folder=ROOT/'testing/workflow-hardening-20261024'
    assert not folder.exists(), 'Install/reset already attempted; inspect durable evidence instead of replaying'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and 'client_pid' not in state
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
            worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        with guard.locked():
            rows=guard.rows()
            assert len(rows)==64 and sum(r['state']=='failed' for r in rows)==26
            assert guard.summary()['failed_count']==8
            for row in rows:
                assert row['job'] and row['state'] in {'completed','failed','cancelled'}
                observed=await client.rpc('status',{'job_id':row['job']})
                assert observed['state']==row['state'], 'Remote status differs; reconcile first'
            folder.mkdir()
            for name in ['BUILD_STATUS.md','HANDOFF.md','AGENTS.md','opencode.json','CONTROLLED_CONTINUATION.md']:
                target=folder/'before'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
            shutil.copy2(runtime/'state.json',folder/'controller.before.json')
            shutil.copy2(ROOT/'artifacts/blend/BowlingPair01.blend',folder/'checkpoint.before.blend')
            for script in (ROOT/'artifacts/scripts').glob('*_v*.py'):
                target=folder/'failed-model-scripts'/script.name;target.parent.mkdir(exist_ok=True);shutil.copy2(script,target)
            with closing(sqlite3.connect(guard.path)) as db,closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:
                db.backup(backup)
            atomic_json(folder/'attempts.before.json',rows)
            receipt=await publish_source(ROOT,SOURCE,client)
            with guard.connect() as db:
                cutoff=db.execute('SELECT max(rowid) FROM attempts').fetchone()[0]
                db.execute('INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(?,?,?)',
                    (cutoff,'User explicitly authorized enforced MCP tool/queue fixes, archived counter reset, commit/push and detached relaunch',time.time()))
                reset_id=db.execute('SELECT last_insert_rowid()').fetchone()[0]
            assert reset_id==2 and guard.rows()==rows and guard.summary()['failed_count']==0
            atomic_json(folder/'reset-receipt.json',{'reset_id':reset_id,'cutoff_rowid':cutoff,'active_failures':0,
                'historical_failures_preserved':26,'attempt_rows_unchanged':True,'source':SOURCE,'checkpoint':receipt})
        workflow=Workflow(ROOT,client,guard)
        if workflow.path.exists():shutil.copy2(workflow.path,folder/'workflow.before.json')
        workflow.state={'jobs':{SOURCE:{'role':'asset','source':'9322aa8b09454873a84141920c5bd552','published':True}},
            'views':{},'reviews':{},'validations':{},'current_source':SOURCE,'checkpoint':receipt}
        workflow.save()
        validation=await workflow.call('validate')
        atomic_json(folder/'validation-job.json',validation)
        assert validation.get('id')
        for _ in range(120):
            result=await workflow.call('status',job_id=validation['id'])
            atomic_json(folder/'validation-result.json',result)
            if result.get('state') in {'completed','failed','cancelled'}:break
            await asyncio.sleep(2)
        assert result['state']=='completed',result
        assert guard.summary()['failed_count']==0
        atomic_json(folder/'checkpoint.json',receipt)
        print(json.dumps({'installed':True,'source':SOURCE,'active_failures':0,'historical_failures':26,
            'validation':workflow.state.get('validation'),'archive':str(folder.relative_to(ROOT))},indent=2))


if __name__=='__main__':asyncio.run(main())
