"""One authorized archived active-error reset and context-safe continuation plan."""
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
from scripts.context_recovery import reconcile
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import SubmissionGuard
from scripts.trial_settings import MODEL,TRIAL
from scripts.workflow_tools import Workflow,atomic_json
import blender52_mcp as worker


async def main():
    folder=ROOT/'testing/context-recovery-reset-20261025'
    assert not (folder/'reset.started.json').exists(),'Reset already attempted; inspect durable receipts, never reset twice'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        workflow=Workflow(ROOT,client,guard)
        verified=await reconcile(ROOT,workflow,guard)
        rows=guard.rows();before=guard.summary()
        assert verified['source']=='c3e6eb270cce4cdd82671452900849bc'
        with guard.locked():
            assert before['failure_budget_reset_id']==0 and before['failed_count']==4 and before['api_correction_count']==1
            assert before['historical_failed_count']==5
            for row in rows:
                observed=await client.rpc('status',{'job_id':row['job']})
                assert row['state']==observed['state'] and row['state'] in {'completed','failed','cancelled'}
            atomic_json(folder/'reset.started.json',{'at':time.time(),'authorization':'User authorized context recovery fixes, archived error reset, all changes commit/push and detached relaunch'})
            for relative in ['BUILD_STATUS.md','HANDOFF.md','CONTROLLED_CONTINUATION.md','opencode.json',
                             '.runtime/autonomous-run/state.json','.runtime/workflow/state.json','artifacts/reports/checkpoint.json',
                             'artifacts/reports/validation.json','artifacts/blend/BowlingPair01.blend']:
                source=ROOT/relative;target=folder/'before'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
            shutil.copy2(ROOT/state['events_file'],folder/'events.before.log')
            with closing(sqlite3.connect(guard.path)) as db,closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:db.backup(backup)
            atomic_json(folder/'attempts.before.json',rows)
            atomic_json(folder/'reconciliation.json',verified)
            with guard.connect() as db:
                cutoff=db.execute('SELECT max(rowid) FROM attempts').fetchone()[0]
                corrections=[dict(row) for row in db.execute('SELECT * FROM api_corrections')]
                db.execute('INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(?,?,?)',
                    (cutoff,'User authorized archived reset before context-safe automatic continuation; no attempt deletion',time.time()))
                epoch=db.execute('SELECT last_insert_rowid()').fetchone()[0]
            after=guard.summary()
            assert epoch==1 and after['failed_count']==0 and after['api_correction_count']==0 and guard.rows()==rows
            atomic_json(folder/'api-corrections.before.json',corrections)
            atomic_json(folder/'reset-receipt.json',{'epoch':epoch,'cutoff_rowid':cutoff,'before':{k:v for k,v in before.items() if k!='accepted_jobs'},
                'after':{k:v for k,v in after.items() if k!='accepted_jobs'},'attempts_unchanged':True,'source_unchanged':True})
        status=await workflow.call('workflow_status')
        checkpoint=status['checkpoint']
        plan={'authorization':'User authorized context recovery repairs, archived zero-error reset, commit/push all changes and new detached run.',
            'model':MODEL,'agent':'bowling-coder','trial':TRIAL,'source_job':verified['source'],
            'checkpoint':checkpoint['path'],'checkpoint_sha256':checkpoint['sha256'],'guard_rows_sha256':rows_hash(guard_rows(ROOT)),
            'validation_sha256':hashlib.sha256((ROOT/'artifacts/reports/validation.json').read_bytes()).hexdigest(),
            'validator_sha256':hashlib.sha256((ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_bytes()).hexdigest(),
            'limits':{'per_source':6,'total':20},'failure_budget_reset_id':epoch,'fresh_coding_session':True,'workflow_managed':True,
            'first_stage':'00','diagnostic_report':'testing/context-recovery-reset-20261025/HANDOFF.md','handoff':'CONTROLLED_CONTINUATION.md',
            'scope':'Continue from the current verified checkpoint and completed references. Repair the FIRST failing stage, starting with actual root parenting/hierarchy, using compact scene_summary and validation_details. Avoid whole-file scene/report reads and repeated pin rewrites without measured progress. Context-only overflow may rotate sessions only after accepted-work reconciliation; preserve every hard STOP and uncertain ID.'}
        pointer=ROOT/'testing/ACTIVE_CONTINUATION.json'
        if pointer.exists():atomic_json(folder/'active-plan.before.json',json.loads(pointer.read_text()))
        atomic_json(folder/'continuation.json',plan)
        atomic_json(pointer,{'path':str((folder/'continuation.json').relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
            'controller_pid':state.pop('controller_pid',None),'native_streak':state.get('native_failures_since_progress',{}),'context_recoveries':state.get('context_recoveries',[])})
        state.update(state='ready_to_continue',last_errors=[],native_failures_since_progress={},
            consecutive_context_recoveries=0,context_recovery_checkpoint=None,prepared_continuation=checked,
            reason='Context-safe continuation authorized after archived epoch1 reset; commit/push before detached launch.',
            reconciliation_plan=str((folder/'continuation.json').relative_to(ROOT)))
        atomic_json(runtime/'state.json',state)
        print(json.dumps({'ready':True,'started':False,'epoch':epoch,'hard_failures':0,'api_corrections':0,
            'historical_failures':after['historical_failed_count'],'source':verified['source'],'attempts_preserved':len(rows)},indent=2))


if __name__=='__main__':asyncio.run(main())
