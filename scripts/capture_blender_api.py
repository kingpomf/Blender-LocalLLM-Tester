"""Durably capture/poll installed API; never replay an uncertain submission."""
import asyncio
import argparse
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
    parser=argparse.ArgumentParser();parser.add_argument('--refresh-return-types',action='store_true');args=parser.parse_args()
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    receipt=ROOT/('.runtime/blender52/api-capture-v2.json' if args.refresh_return_types else '.runtime/blender52/api-capture.json')
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
    data=json.loads(Path(artifact['path']).read_text());assert data['version']=='5.2.3 LTS'
    assert data.get('schema_version',0)>=2,'Legacy catalog cannot replace current API checks; use --refresh-return-types'
    target=ROOT/'artifacts/reports/blender-api-catalog.json'
    if target.exists():
        archived=ROOT/'.runtime/blender52/api-catalog-archive'/hashlib.sha256(target.read_bytes()).hexdigest()
        archived.parent.mkdir(parents=True,exist_ok=True)
        if not archived.exists():shutil.copy2(target,archived)
    shutil.copy2(artifact['path'],target)
    atomic_json(ROOT/'artifacts/reports/blender-api-catalog-receipt.json',{'job':job,'version':data['version'],'sha256':artifact['sha256'],'bytes':artifact['bytes']})
    print(json.dumps({'job':job,'state':'completed','version':data['version'],'types':len(data['types']),'operators':len(data['operators']),'errors':data['errors'],'bytes':artifact['bytes'],'runtime_returns':data.get('runtime_returns')},indent=2))


if __name__=='__main__':asyncio.run(main())
