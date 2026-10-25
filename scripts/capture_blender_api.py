"""Durably capture/poll installed API; never replay an uncertain submission."""
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import atomic_json
import blender52_mcp as worker


async def main():
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    receipt=ROOT/'.runtime/blender52/api-capture.json'
    if receipt.exists():job=json.loads(receipt.read_text())['job']
    else:
        source=json.loads((ROOT/'.runtime/workflow/state.json').read_text())['current_source']
        code=(ROOT/'scripts/blender_api_catalog_payload.py').read_text()
        row=await guard.submit({'operation':'author','source_job':source,'code':code},client.rpc)
        job=row['id'];atomic_json(receipt,{'job':job,'source':source,'payload_sha256':hashlib.sha256(code.encode()).hexdigest()})
    row=await client.rpc('status',{'job_id':job})
    for attempt in guard.rows():
        if attempt['job']==job:guard.update(attempt['fingerprint'],row)
    if row['state']=='failed':
        print(json.dumps(await client.rpc('diagnostics',{'job_id':job})));return
    if row['state']!='completed':print(json.dumps({'job':job,'state':row['state']}));return
    artifact=await client.fetch(job,'api-catalog.json')
    target=ROOT/'artifacts/reports/blender-api-catalog.json';shutil.copy2(artifact['path'],target)
    data=json.loads(target.read_text());assert data['version']=='5.2.3 LTS'
    atomic_json(ROOT/'artifacts/reports/blender-api-catalog-receipt.json',{'job':job,'version':data['version'],'sha256':artifact['sha256'],'bytes':artifact['bytes']})
    print(json.dumps({'job':job,'state':'completed','version':data['version'],'types':len(data['types']),'operators':len(data['operators']),'errors':data['errors'],'bytes':artifact['bytes']},indent=2))


if __name__=='__main__':asyncio.run(main())
