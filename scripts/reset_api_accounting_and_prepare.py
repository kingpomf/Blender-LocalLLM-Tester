"""One explicit user-authorized archived epoch reset and fresh continuation plan."""
import asyncio
from contextlib import closing
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.blender_api import load_catalog
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import Workflow,atomic_json
from scripts.run_bowling import hard_native_streak
import blender52_mcp as worker


async def main():
    folder=ROOT/'testing/api-accounting-reset-20261025'
    assert not (folder/'reset.started.json').exists(),'Reset already attempted: inspect durable receipts; never replay a reset'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        catalog=load_catalog(ROOT);assert catalog and catalog['runtime_returns']['Object.children']['python_type']=='tuple'
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        workflow=Workflow(ROOT,client,guard)
        current=await workflow.call('workflow_status');assert not current['pending_jobs']
        assert current['current_source']=='2b37b77ce016462c943a217f67fb9418'
        with guard.locked():
            rows=guard.rows();before=guard.summary()
            assert before['failure_budget_reset_id']==2 and before['failed_count']==3 and before['api_correction_count']==2
            assert before['historical_failed_count']==31
            for row in rows:
                assert row['job'] and row['state'] in {'completed','failed','cancelled'}
                observed=await client.rpc('status',{'job_id':row['job']})
                assert observed['state']==row['state'],'Remote/local state differs; reconcile before resetting'
            atomic_json(folder/'reset.started.json',{'created':time.time(),'reason':'User explicitly authorized archived zero-counter reset after API/accounting review, commit/push and detached launch'})
            for relative in ['BUILD_STATUS.md','HANDOFF.md','CONTROLLED_CONTINUATION.md','.runtime/autonomous-run/state.json',
                             '.runtime/workflow/state.json','artifacts/reports/checkpoint.json','artifacts/reports/validation.json',
                             'artifacts/reports/blender-api-catalog-receipt.json','artifacts/blend/BowlingPair01.blend',
                             'artifacts/scripts/accepted_bd557eba1416427cb8c9c2ed428fa43f.py']:
                source=ROOT/relative;target=folder/'before'/relative;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,target)
            with closing(sqlite3.connect(guard.path)) as db,closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:db.backup(backup)
            atomic_json(folder/'attempts.before.json',rows)
            with guard.connect() as db:
                corrections=[dict(row) for row in db.execute('SELECT * FROM api_corrections ORDER BY job')]
                cutoff=db.execute('SELECT max(rowid) FROM attempts').fetchone()[0]
                db.execute('INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(?,?,?)',
                    (cutoff,'User authorized archived reset of hard/API counts after source-proven API/accounting fixes; preserve attempts and fingerprints',time.time()))
                epoch=db.execute('SELECT last_insert_rowid()').fetchone()[0]
            after=guard.summary()
            assert epoch==3 and after['failed_count']==0 and after['api_correction_count']==0 and guard.rows()==rows
            atomic_json(folder/'api-corrections.before.json',corrections)
            atomic_json(folder/'reset-receipt.json',{'epoch':epoch,'cutoff_rowid':cutoff,'before':{k:v for k,v in before.items() if k!='accepted_jobs'},
                'after':{k:v for k,v in after.items() if k!='accepted_jobs'},'attempts_unchanged':True,
                'native_statuses_verified':len(rows),'source_unchanged':True})
        # Refresh measured mirrors under the stopped controller; never rerun geometry.
        current=await workflow.call('workflow_status')
        pointer=ROOT/'testing/ACTIVE_CONTINUATION.json';old=json.loads(pointer.read_text());plan=json.loads((ROOT/old['path']).read_text())
        receipt=current['checkpoint']
        plan.update(authorization='User explicitly authorized review/fixes, archived reset to zero, commit/push and detached relaunch.',
            source_job=current['current_source'],checkpoint=receipt['path'],checkpoint_sha256=receipt['sha256'],
            guard_rows_sha256=rows_hash(guard_rows(ROOT)),failure_budget_reset_id=epoch,fresh_coding_session=True,
            diagnostic_report='testing/api-accounting-reset-20261025/HANDOFF.md',
            scope='Use installed API return-type lookups and recoverable source-proven API corrections. Start with one small collision-only edit, preserve valid visual gutters/foundations, poll measured validation before any further changes. Complete remaining support/camera/pixel/delivery acceptance through fixed tools.')
        for key,relative in [('validation_sha256','artifacts/reports/validation.json'),('validator_sha256','artifacts/scripts/validate_bowling_pair01.py')]:
            plan[key]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
        atomic_json(folder/'active-plan.before.json',old);atomic_json(folder/'continuation.json',plan)
        atomic_json(pointer,{'path':str((folder/'continuation.json').relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
            'controller_pid':state.pop('controller_pid',None),'native_streak':state.get('native_failures_since_progress',{}),
            'native_progress':state.get('native_progress',{}),'reset_epoch':epoch})
        state.update(state='ready_to_continue',last_errors=[],native_failures_since_progress={},
            native_progress={'asset_jobs':[current['current_source']],'failed_jobs':[]},prepared_continuation=checked,
            reason='Authorized archived epoch3 reset and verified API/accounting repair; commit/push then launch detached.',
            reconciliation_plan=str((folder/'continuation.json').relative_to(ROOT)))
        atomic_json(runtime/'state.json',state)
        assert hard_native_streak(ROOT,{r['job']:'old failure' for r in rows if r['state']=='failed'})=={}
        print(json.dumps({'ready':True,'started':False,'epoch':epoch,'hard_failures':0,'api_corrections':0,
            'historical_failed_jobs':31,'attempts_preserved':len(rows),'source':current['current_source']},indent=2))


if __name__=='__main__':asyncio.run(main())
