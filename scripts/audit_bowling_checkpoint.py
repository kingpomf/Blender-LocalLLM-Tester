"""Submit one guarded read-only reconciliation audit and retain accepted identity."""
import asyncio
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import blender52_mcp as worker
from submission_guard import SubmissionGuard
from check_references import check

SOURCE='d1ce998472c349ac9f9fc2775afefdf6'


async def main():
    folder=ROOT/'testing/reconciliation-20261024'
    state_path=folder/'audit-job.json'
    assert check(ROOT)['passed']
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
        worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    if state_path.exists():
        state=json.loads(state_path.read_text())
        assert state.get('id'), 'Uncertain audit acceptance: reconcile guard/job before any retry'
    else:
        state_path.write_text(json.dumps({'state':'submission_uncertain','source':SOURCE}))
        state=await guard.submit({'operation':'author','source_job':SOURCE,
            'code':(ROOT/'testing/audit_bowling_checkpoint.py').read_text()},client.rpc)
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            path=ROOT/name
            with path.open('a') as out:
                out.write(f'\n- Operator read-only audit pending: {state["id"]}; source {SOURCE}; no geometry modification authorized\n')
        print(json.dumps({'accepted_audit':state['id'],'source':SOURCE}),flush=True)
    for _ in range(60):
        state=await client.rpc('status',{'job_id':state['id']})
        for row in guard.rows():
            if row['job']==state['id']:
                guard.update(row['fingerprint'],state)
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        if state['state'] in {'completed','failed','cancelled'}:
            break
        await asyncio.sleep(2)
    if state['state']!='completed':
        if state['state'] in {'failed','cancelled'}:
            print(json.dumps(await client.rpc('diagnostics',{'job_id':state['id']}),indent=2))
        raise RuntimeError('Audit incomplete; preserve ID and inspect state')
    result=await client.fetch(state['id'],'report.json')
    (folder/'native-audit.json').write_text(Path(result['path']).read_text())
    print(json.dumps({'audit':state['id'],'report':str(folder/'native-audit.json')}))


if __name__=='__main__':
    asyncio.run(main())
