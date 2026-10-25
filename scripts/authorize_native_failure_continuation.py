"""Prepare the user's requested retry; preserve the guard and archive stopped state."""
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
    folder=ROOT/'testing/native-failure-relaunch'
    path=folder/'continuation.json'
    assert not path.exists(), 'Prepared already; inspect existing state, never launch a duplicate'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state'] in {'interrupted','blocked'} and not state.get('client_pid')
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        status=await Workflow(ROOT,client,guard).call('workflow_status')
        assert not status['pending_jobs']
        rows=guard_rows(ROOT);accounting=budget_accounting(guard.path,rows)
        assert len(accounting['counted_failures'])==2 and accounting['reset_id']==2
        old=json.loads((ROOT/'testing/ACTIVE_CONTINUATION.json').read_text())
        plan=json.loads((ROOT/old['path']).read_text())
        assert status['current_source']==plan['source_job']
        plan.update(authorization='User explicitly requested another detached run after reviewed native-failure fixes; no failure-budget reset.',
                    guard_rows_sha256=rows_hash(rows),fresh_coding_session=True,
                    diagnostic_report='testing/native-failure-relaunch/HANDOFF.md',
                    scope='Follow the retry handoff. Start with one small geometry correction and its automatic measured validation. Preserve prior passing stages. Repair remaining acceptance through MCP tools; do not repeat broad failed scripts or unsafe deletion order.')
        for key,relative in [('validation_sha256','artifacts/reports/validation.json'),('validator_sha256','artifacts/scripts/validate_bowling_pair01.py')]:
            plan[key]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
        atomic_json(folder/'controller.before.json',state)
        atomic_json(folder/'attempts.before.json',rows)
        atomic_json(folder/'active-plan.before.json',old)
        atomic_json(path,plan)
        atomic_json(ROOT/'testing/ACTIVE_CONTINUATION.json',{'path':str(path.relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
            'native_failures_since_progress':state.pop('native_failures_since_progress',{}),'controller_pid':state.pop('controller_pid',None)})
        state.update(state='ready_to_continue',prepared_continuation=checked,
            reason='User authorized retry after failure diagnosis and reviewed fixes; two counted failures preserved.',
            reconciliation_plan=str(path.relative_to(ROOT)),last_errors=[])
        atomic_json(runtime/'state.json',state)
        assert rows_hash(guard_rows(ROOT))==rows_hash(rows)
        print(json.dumps({'prepared':True,'started':False,'current_failures':2,'reset_id':2,'guard_unchanged':True},indent=2))


if __name__=='__main__':asyncio.run(main())
