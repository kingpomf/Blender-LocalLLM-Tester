"""Consume a completed saved review and prepare the user's requested detached retry."""
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import SubmissionGuard,budget_accounting
from scripts.workflow_tools import Workflow,atomic_json
import blender52_mcp as worker


async def main():
    folder=ROOT/'testing/review-recovery-relaunch';plan_path=folder/'continuation.json'
    assert not plan_path.exists(),'Recovery already prepared; inspect before any relaunch'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        atomic_json(folder/'controller.before.json',state)
        for relative in ['.runtime/workflow/state.json','artifacts/reports/render-manifest.json','artifacts/reports/qualitative-evidence.json','artifacts/reports/validation.json']:
            path=ROOT/relative
            if path.exists():
                target=folder/'before'/path.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        rows=guard_rows(ROOT);atomic_json(folder/'attempts.before.json',rows)
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        status=await Workflow(ROOT,client,guard).call('workflow_status')
        review_id='review-ffc5c5a8c3e748e4982fb2f13968a4a1'
        assert status['reviews'][review_id]['state']=='completed'
        assert not status['pending_jobs']
        assert rows_hash(guard_rows(ROOT))==rows_hash(rows),'Recovery must reuse existing jobs, never submit or reset'
        accounting=budget_accounting(guard.path,rows)
        assert len(accounting['counted_failures'])==2 and accounting['reset_id']==2
        old=json.loads((ROOT/'testing/ACTIVE_CONTINUATION.json').read_text())
        plan=json.loads((ROOT/old['path']).read_text())
        receipt=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
        assert receipt['source_job']==status['current_source']=='2b37b77ce016462c943a217f67fb9418'
        plan.update(authorization='User authorized fixing stuck review handling, automatic review recovery and detached relaunch; no counter reset.',
            source_job=receipt['source_job'],checkpoint=receipt['path'],checkpoint_sha256=receipt['sha256'],
            guard_rows_sha256=rows_hash(rows),fresh_coding_session=True,
            diagnostic_report='testing/review-recovery-relaunch/HANDOFF.md',
            scope='Follow active recovery handoff. Preserve prior verified foundations and latest checkpoint. Fix actual camera occlusion/framing and remaining collision/support criteria in small validated edits, then review changed real images and finish measured delivery through fixed MCP tools.')
        for key,relative in [('validation_sha256','artifacts/reports/validation.json'),('validator_sha256','artifacts/scripts/validate_bowling_pair01.py')]:
            plan[key]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
        atomic_json(folder/'active-plan.before.json',old)
        atomic_json(folder/'recovery-status.json',status)
        atomic_json(plan_path,plan)
        atomic_json(ROOT/'testing/ACTIVE_CONTINUATION.json',{'path':str(plan_path.relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),'controller_pid':state.pop('controller_pid',None)})
        state.update(state='ready_to_continue',prepared_continuation=checked,last_errors=[],
            reconciliation_plan=str(plan_path.relative_to(ROOT)),reason='Saved review recovered without replay; user authorized detached continuation.')
        atomic_json(runtime/'state.json',state)
        print(json.dumps({'ready':True,'started':False,'review':status['reviews'][review_id],
            'guard_unchanged':True,'counted_failures':2,'source':receipt['source_job'],'validation':status['validation']},indent=2))


if __name__=='__main__':asyncio.run(main())
