"""Bind the user's API-aware relaunch to the current checkpoint and unchanged budget."""
import asyncio
import fcntl
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.blender_api import load_catalog
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import SubmissionGuard,budget_accounting
from scripts.workflow_tools import Workflow,atomic_json
import blender52_mcp as worker


async def main():
    folder=ROOT/'testing/api-aware-relaunch';plan_path=folder/'continuation.json'
    assert not plan_path.exists(),'Already prepared; inspect state before any duplicate launch'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        atomic_json(folder/'controller.before.json',state)
        rows=guard_rows(ROOT);atomic_json(folder/'attempts.before.json',rows)
        catalog=load_catalog(ROOT);assert catalog is not None
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        accounting=budget_accounting(guard.path,rows)
        assert len(accounting['counted_failures'])==3 and len(accounting['api_corrections'])==1 and accounting['reset_id']==2
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
        status=await Workflow(ROOT,client,guard).call('workflow_status')
        assert not status['pending_jobs']
        receipt=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
        assert status['current_source']==receipt['source_job']=='2b37b77ce016462c943a217f67fb9418'
        old=json.loads((ROOT/'testing/ACTIVE_CONTINUATION.json').read_text())
        plan=json.loads((ROOT/old['path']).read_text())
        plan.update(authorization='User requested committing API-aware correction/recovery changes and launching a new detached run; no budget reset.',
            source_job=receipt['source_job'],checkpoint=receipt['path'],checkpoint_sha256=receipt['sha256'],
            guard_rows_sha256=rows_hash(rows),fresh_coding_session=True,
            diagnostic_report='testing/api-aware-relaunch/HANDOFF.md',
            scope='Use installed API lookups and recoverable API feedback to self-correct. Preserve current verified source and passing foundations. Repair actual gutter/collision/support/framing findings with small validated edits, then finish real-image review and measured delivery through MCP tools.')
        for key,relative in [('validation_sha256','artifacts/reports/validation.json'),('validator_sha256','artifacts/scripts/validate_bowling_pair01.py')]:
            plan[key]=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
        atomic_json(folder/'api-catalog-receipt.json',json.loads((ROOT/'artifacts/reports/blender-api-catalog-receipt.json').read_text()))
        atomic_json(folder/'active-plan.before.json',old)
        atomic_json(folder/'workflow.before.json',status)
        atomic_json(plan_path,plan)
        atomic_json(ROOT/'testing/ACTIVE_CONTINUATION.json',{'path':str(plan_path.relative_to(ROOT))})
        checked=validate(ROOT)
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),'controller_pid':state.pop('controller_pid',None)})
        state.update(state='ready_to_continue',prepared_continuation=checked,last_errors=[],
            reconciliation_plan=str(plan_path.relative_to(ROOT)),reason='User authorized API-aware detached continuation after commit; hard failure streak and accounting preserved.')
        atomic_json(runtime/'state.json',state)
        assert rows_hash(guard_rows(ROOT))==rows_hash(rows)
        print(json.dumps({'prepared':True,'started':False,'hard_failures':3,'api_corrections':1,'epoch':2,'source':receipt['source_job'],'guard_unchanged':True},indent=2))


if __name__=='__main__':asyncio.run(main())
