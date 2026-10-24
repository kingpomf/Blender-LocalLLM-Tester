"""Bind the enforced-workflow checkpoint/reset to an explicitly authorized fresh session."""
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
from scripts.trial_settings import MODEL,TRIAL
import blender52_mcp as worker


async def main():
    folder=ROOT/'testing/workflow-hardening-20261024'
    path=folder/'continuation.json'
    assert not path.exists(), 'Relaunch plan exists; inspect instead of replacing authorization'
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+TRIAL,
                                   worker.BINARY,str(ROOT/'artifacts/downloads'))
    workflow=Workflow(ROOT,client,guard)
    current=await workflow.call('workflow_status')
    assert not current['pending_jobs']
    assert current['guard']['failed_count']==0 and current['guard']['failure_budget_reset_id']==2
    receipt=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
    assert receipt['source_job']==current['current_source']=='756846c5415e4c5e92f159389a87eeb0'
    rows=guard_rows(ROOT);accounting=budget_accounting(guard.path,rows)
    assert not accounting['counted_failures'] and sum(r['state']=='failed' for r in rows)==26
    report=json.loads((ROOT/'artifacts/reports/validation.json').read_text())
    first=next((stage for stage,result in report['stage_results'].items() if result!='PASS'),'08')
    plan={'authorization':'User explicitly authorized enforced MCP workflow/queue controls, another archived error-counter reset, commit/push and detached relaunch.',
          'model':MODEL,'agent':'bowling-coder','trial':TRIAL,'source_job':receipt['source_job'],
          'checkpoint':receipt['path'],'checkpoint_sha256':receipt['sha256'],
          'guard_rows_sha256':rows_hash(rows),'validation_sha256':hashlib.sha256((ROOT/'artifacts/reports/validation.json').read_bytes()).hexdigest(),
          'validator_sha256':hashlib.sha256((ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_bytes()).hexdigest(),
          'limits':{'per_source':6,'total':20},'failure_budget_reset_id':2,'fresh_coding_session':True,
          'workflow_managed':True,'first_stage':first,'diagnostic_report':'testing/WORKFLOW_HARDENING.md',
          'handoff':'CONTROLLED_CONTINUATION.md',
          'scope':'Preserve source geometry and verified foundation/pin repairs. Use actual current MCP checks to repair remaining ball/support/dressing/collision/framing criteria. Never render inline, create output directories, manually claim stage PASS or alter managed state. Complete validation and selected export/reimport delivery through fixed tools.'}
    atomic_json(path,plan)
    pointer=ROOT/'testing/ACTIVE_CONTINUATION.json'
    (folder/'active-plan.before.json').write_bytes(pointer.read_bytes())
    atomic_json(pointer,{'path':str(path.relative_to(ROOT))})
    checked=validate(ROOT)
    for name in ['validation.json','checkpoint.json','render-manifest.json']:
        (folder/name).write_bytes((ROOT/'artifacts/reports'/name).read_bytes())
    atomic_json(folder/'attempts.after.json',rows)
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and 'client_pid' not in state
        state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
                                                   'controller_pid':state.pop('controller_pid',None)})
        state.update(state='ready_to_continue',last_errors=[],prepared_continuation=checked,
            reason='Enforced MCP workflow qualified, latest checkpoint reconciled, active errors zero. Detached relaunch authorized.',
            reconciliation_plan=str(path.relative_to(ROOT)),continuation_command='python3 scripts/run_bowling.py --resume --continuation --detach')
        atomic_json(runtime/'state.json',state)
    print(json.dumps({'ready':True,'started':False,'source':plan['source_job'],'agent':'bowling-coder',
                      'active_failures':0,'historical_failures':26,'next_stage':first},indent=2))


if __name__=='__main__':asyncio.run(main())
