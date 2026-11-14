"""Bind the user's fivefold-limit continuation to the verified EliteDesk checkpoint."""
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.check_resume import check as resume_check
from scripts.check_references import check as reference_check
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import SubmissionGuard,budget_accounting,FAILURE_LIMIT_PER_SOURCE,FAILURE_LIMIT_TOTAL,FAILURE_LIMIT_WITHOUT_PROGRESS
from scripts.workflow_tools import Workflow,atomic_json
from scripts.checkpoint_bowling import sync_ledgers
from scripts.trial_settings import MODEL,TRIAL
import blender52_mcp as worker


async def main():
    runtime=ROOT/'.runtime/autonomous-run'
    folder=ROOT/'testing/breathing-room-continuation'
    assert not folder.exists(),'Already prepared; inspect state rather than repeat'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        path=runtime/'state.json';state=json.loads(path.read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        assert state['reason'].startswith('STOP: two distinct native jobs')
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        client=worker.ProjectTransport(worker.WORKER_HOST,worker.REMOTE_APP,worker.WORKER_ROOT,
            worker.BINARY,str(ROOT/'artifacts/downloads'),dedicated_gpu=worker.DEDICATED_GPU)
        status=await Workflow(ROOT,client,guard).call('workflow_status')
        assert not status['pending_jobs'],status
        rows=guard_rows(ROOT);before_hash=rows_hash(rows)
        assert all(row['job'] and row['state'] in {'completed','failed','cancelled'} for row in rows)
        source=status['current_source'];assert source=='cf9e9c33d60a4f99ae69e149236e0acf'
        for row in rows:
            live=await client.rpc('status',{'job_id':row['job']})
            assert live['state']==row['state'],live
        accounting=budget_accounting(guard.path,rows)
        assert len(accounting['counted_failures'])==2 and accounting['reset_id']==0
        assert len(state['native_failures_since_progress'])==2<FAILURE_LIMIT_WITHOUT_PROGRESS
        checkpoint=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
        assert checkpoint['source_job']==source
        assert hashlib.sha256((ROOT/checkpoint['path']).read_bytes()).hexdigest()==checkpoint['sha256']
        for check in [reference_check,resume_check]:
            result=check(ROOT);assert result['passed'],result
        folder.mkdir()
        atomic_json(folder/'controller.before.json',state)
        atomic_json(folder/'attempts.before.json',rows)
        for filename in ['BUILD_STATUS.md','HANDOFF.md']:
            (folder/filename).write_text((ROOT/filename).read_text())
        plan={'authorization':'User requested 120-second MCP timeout, clearing this block, fivefold hard-failure headroom and detached continuation.',
            'model':MODEL,'trial':TRIAL,'source_job':source,'checkpoint':checkpoint['path'],
            'checkpoint_sha256':checkpoint['sha256'],'guard_rows_sha256':before_hash,
            'validator_sha256':hashlib.sha256((ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_bytes()).hexdigest(),
            'limits':{'per_source':FAILURE_LIMIT_PER_SOURCE,'total':FAILURE_LIMIT_TOTAL},
            'without_progress_limit':FAILURE_LIMIT_WITHOUT_PROGRESS,'failure_budget_reset_id':0,
            'fresh_coding_session':True,'workflow_managed':True,'diagnostic_report':'CONTROLLED_CONTINUATION.md',
            'scope':'Resume the completed Stage00 source. Repair lane slab boundary indices/material-slot consistency in a changed asset revision, then poll automatic validation. Initial empty-scene validation crashed; do not replay it or weaken the validator. References are READY. Continue measured construction and delivery through MCP tools. Two hard failures remain counted; limits30/source100/total and10 without a published asset advance. No reset or empty rebuild.'}
        if (ROOT/'artifacts/reports/validation.json').exists():
            plan['validation_sha256']=hashlib.sha256((ROOT/'artifacts/reports/validation.json').read_bytes()).hexdigest()
        plan_path=folder/'continuation.json';atomic_json(plan_path,plan)
        atomic_json(ROOT/'testing/ACTIVE_CONTINUATION.json',{'path':str(plan_path.relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('operator_recoveries',[]).append({'at':time.time(),'authorization':plan['authorization'],
            'prior_reason':state['reason'],'prior_errors':state['last_errors'],'counters_reset':False,
            'previous_limits':{'without_progress':2,'per_source':6,'total':20},
            'new_limits':{'without_progress':FAILURE_LIMIT_WITHOUT_PROGRESS,**plan['limits']}})
        state.update(state='ready_to_continue',last_errors=[],prepared_continuation=checked,
            reason='User-authorized fivefold headroom; checkpoint verified and both failures retained.',
            reconciliation_plan=str(plan_path.relative_to(ROOT)))
        atomic_json(path,state)
        sync_ledgers(ROOT)
        assert rows_hash(guard_rows(ROOT))==before_hash,'Guard history changed'
        print(json.dumps({'prepared':True,'source':source,'failures_retained':2,'reset_id':0,
            'limits':plan['limits'],'without_progress_limit':FAILURE_LIMIT_WITHOUT_PROGRESS,
            'guard_unchanged':True,'preflight_passed':validate(ROOT)['passed']},indent=2))


if __name__=='__main__':asyncio.run(main())
