"""Apply exactly the operator-reviewed pin correction once, through the normal guard."""
import asyncio
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.submission_guard import SubmissionGuard
from scripts.checkpoint_bowling import publish_source, update_fields, backup_and_write
import blender52_mcp as worker

SOURCE='e8630f4b79ba468ebd18ef53e2f1d51d'


async def main():
    folder=ROOT/'testing/pin-correction-reset-20261024'
    path=folder/'correction-job.json'
    assert (folder/'reset-receipt.json').exists()
    code=(ROOT/'artifacts/scripts/stage03_pins_corrected.py').read_text()
    digest=hashlib.sha256(code.encode()).hexdigest()
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
        worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    if path.exists():
        state=json.loads(path.read_text())
        assert state.get('id') and state['code_sha256']==digest, 'Uncertain/different correction: reconcile before any retry'
    else:
        state={'state':'submission_uncertain','code_sha256':digest,'source':SOURCE}
        path.write_text(json.dumps(state,indent=2)+'\n')
        job=await guard.submit({'operation':'author','source_job':SOURCE,'code':code},client.rpc)
        state.update(id=job['id'],state=job['state'])
        path.write_text(json.dumps(state,indent=2)+'\n')
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            backup_and_write(ROOT,name,update_fields((ROOT/name).read_text(),{'Pending job':job['id'],
                'Pending source job':SOURCE,'Operator intervention':'User-authorized pin correction and archived failure-counter reset in progress'}))
        print(json.dumps({'accepted_pin_correction':job['id'],'source':SOURCE}),flush=True)
    for _ in range(60):
        job=await client.rpc('status',{'job_id':state['id']})
        row=next(r for r in guard.rows() if r['job']==job['id'])
        guard.update(row['fingerprint'],job)
        state.update(state=job['state'])
        path.write_text(json.dumps(state,indent=2)+'\n')
        if job['state'] in {'completed','failed','cancelled'}:break
        await asyncio.sleep(2)
    if job['state']!='completed':
        if job['state'] in {'failed','cancelled'}:
            diagnosis=await client.rpc('diagnostics',{'job_id':job['id']})
            (folder/'correction-diagnostics.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
            print(json.dumps(diagnosis,indent=2))
        raise RuntimeError('Correction did not complete; preserve accepted ID, no replay')
    report=await client.fetch(job['id'],'report.json')
    actual=json.loads(Path(report['path']).read_text())
    assert actual['passed'] and actual['pin_count']==20 and actual['nonmanifold_edges']==0
    (folder/'pin-report.json').write_text(json.dumps(actual,indent=2)+'\n')
    receipt=await publish_source(ROOT,job['id'])
    (folder/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'completed':True,'source':job['id'],'canonical':receipt,'budget':guard.summary()['failed_count']},indent=2))


if __name__=='__main__':asyncio.run(main())
