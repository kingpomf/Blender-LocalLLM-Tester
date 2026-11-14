"""Publish completed bowling outputs to a versioned, hash-verified OneDrive folder."""
import asyncio
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
PARENT=Path('/Users/start/Library/CloudStorage/OneDrive-Personal/AI-Creative/Review/Blender/EliteDesk')
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.trial_settings import MODEL,TRIAL
import blender52_mcp as worker


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def verify_uploads(target):
    manifest=json.loads((target/'PACKAGE_MANIFEST.json').read_text())
    uploaded=[];pending=[]
    for item in manifest['files']:
        path=target/item['path']
        assert path.is_relative_to(target) and path.is_file()
        assert path.stat().st_size==item['bytes'] and digest(path)==item['sha256'],str(path)
    for relative in [item['path'] for item in manifest['files']]+['PACKAGE_MANIFEST.json']:
        result=subprocess.run(['fileproviderctl','evaluate',str(target/relative)],capture_output=True,text=True,timeout=20,check=True)
        match=re.search(r'\bisUploaded\s*=\s*([01]);',result.stdout)
        (uploaded if match and match[1]=='1' else pending).append(relative)
    return {'path':str(target),'content_files_hash_verified':len(manifest['files']),
        'provider_uploaded':len(uploaded),'provider_pending_or_unknown':pending,
        'total_bytes':sum(item['bytes'] for item in manifest['files']),
        'trial_status':manifest['trial_status']}


async def main():
    assert PARENT.is_dir(),'Shared review parent must already exist'
    state=json.loads((ROOT/'.runtime/autonomous-run/state.json').read_text())
    assert state['state']=='completed' and not state.get('client_pid')
    delivery=json.loads((ROOT/'artifacts/reports/DELIVERY_MANIFEST.json').read_text())
    source=delivery['final_source_job']
    date=datetime.fromtimestamp(state['finished'],timezone.utc).strftime('%Y%m%d')
    target=PARENT/f'BowlingPair01-FlashNext-Strata-{date}-{source[:8]}'
    if target.exists():
        print(json.dumps({'already_published':True,**verify_uploads(target)},indent=2));return
    validation=json.loads((ROOT/'artifacts/reports/validation.json').read_text())
    assert validation['asset_source_job']==source and validation['passed'] is True
    assert validation['fail_count']==0 and validation['unresolved_count']==0
    exports=json.loads((ROOT/'artifacts/reports/export-receipt.json').read_text())
    assert exports['source']==source and exports['job_id']==delivery['roundtrip_job']
    assert len(exports['roundtrips'])==6 and all(row['passed'] for row in exports['roundtrips'])
    for item in delivery['artifacts']+exports['artifacts']:
        path=(ROOT/item['path']).resolve()
        assert path.is_relative_to(ROOT/'artifacts') and path.is_file()
        assert path.stat().st_size==item['bytes'] and digest(path)==item['sha256'],str(path)
    renders=json.loads((ROOT/'artifacts/reports/render-manifest.json').read_text())
    assert renders['asset_source']==source
    assert {item['role'] for item in renders['images']}=={'overview','player','pindeck','props'}
    client=worker.ProjectTransport(worker.WORKER_HOST,worker.REMOTE_APP,worker.WORKER_ROOT,
        worker.BINARY,str(ROOT/'artifacts/downloads'),dedicated_gpu=worker.DEDICATED_GPU)
    devices=[]
    for item in renders['images']:
        assert item['asset_source']==source and digest(ROOT/item['path'])==item['sha256']
        result=await client.rpc('status',{'job_id':item['job_id']})
        assert result['state']=='completed'
        manifest=result['manifest'];device=manifest['device']
        assert device['backend']=='CUDA' and device['cpu_enabled'] is False
        assert '3060' in device['name'] and manifest['blender_version']=='5.2.3 LTS'
        devices.append({'role':item['role'],'job_id':item['job_id'],'device':device,
            'blender_version':manifest['blender_version']})
    staging=PARENT/('.'+target.name+'.staging')
    assert not staging.exists(),'Partial package exists; inspect rather than overwrite'
    staging.mkdir()
    files={}
    for item in delivery['artifacts']:
        original=Path(item['path']);parts=original.parts
        relative=(original.name if parts[1] in {'blend','exports'} else str(Path(*parts[1:])))
        files[relative]=ROOT/original
    for filename in ['DELIVERY_MANIFEST.json','export-receipt.json','render-manifest.json',
                     'validation.json','qualitative-evidence.json','checkpoint.json']:
        files['reports/'+filename]=ROOT/'artifacts/reports'/filename
    for path in (ROOT/'artifacts/references').rglob('*'):
        if path.is_file() and path.name!='pending-requests.json':
            files[str(Path('references')/path.relative_to(ROOT/'artifacts/references'))]=path
    for path in (ROOT/'artifacts/scripts').glob('*.py'):
        files['source/scripts/'+path.name]=path
    for path in (ROOT/'spec/bowling-pair-01').iterdir():
        if path.is_file():files['source/spec/'+path.name]=path
    for filename in ['BUILD_STATUS.md','HANDOFF.md']:
        files['reports/'+filename]=ROOT/filename
    files['source/final-scene.json']=ROOT/'artifacts/downloads'/source/'scene.json'
    files['BowlingPair01_preview.png']=ROOT/'artifacts/renders/BowlingPair01_overview.png'
    entries=[]
    for relative,path in sorted(files.items()):
        assert path.is_file(),str(path)
        destination=staging/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        expected=digest(path);shutil.copy2(path,destination)
        assert digest(destination)==expected and destination.stat().st_size==path.stat().st_size
        entries.append({'path':relative,'source_path':str(path.relative_to(ROOT)),
            'bytes':destination.stat().st_size,'sha256':expected})
    def write_generated(relative,text):
        path=staging/relative;path.write_text(text)
        entries.append({'path':relative,'bytes':path.stat().st_size,'sha256':digest(path)})
    write_generated('reports/render-device-evidence.json',json.dumps(devices,indent=2)+'\n')
    write_generated('README.md',f'''# BowlingPair01 — Flash-Next / Strata, EliteDesk Blender5.2

Open **BowlingPair01.blend** for the editable native scene with cameras and lights.
**BowlingPair01.glb** is the full exported pair. The other five GLBs contain the
reusable pin, three balls and collision proxies. BowlingPair01_preview.png is the
overview; renders/ contains all four actual1280x720 Blender views.

Trial status: COMPLETE through the fixed workflow. Final measured validation:
{validation['pass_count']} PASS,0 FAIL,0 unresolved. Six GLB export/reimport checks
passed. Presentation acceptance came from the fixed pixel helper; this package
does not add a separate human approval. Reports and the asset guide are in reports/.

Execution: {MODEL} through Strata on Z6. Blender5.2.3 LTS runs on EliteDesk:
CPU scene authoring, validation and export; all four final renders use the NVIDIA
GeForce RTX3060 via CUDA with CPU rendering disabled. The actual backend device
records are included in reports/render-device-evidence.json.

Final native source: {source}
Export/roundtrip job: {exports['job_id']}
Trial: {TRIAL}

References and their receipts are in references/. Current-trial author scripts,
the fixed supplied validator and the ten specification files are in source/.
Gameplay, physics and engine integration are outside this asset validation.

Original tool/model reports are preserved. Their historical workspace-relative
paths refer to the original checkout; PACKAGE_MANIFEST.json maps source_path to
each package path and records independently verified copy hashes. Historical
operator/next-action prose in the ledgers is not current acceptance evidence;
use the final validation, delivery manifest and export receipt instead.
''')
    package={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),
        'trial_status':'COMPLETE','model':MODEL,'backend':'strata','execution_host':'elitedesk-3060',
        'blender_version':'5.2.3 LTS','render_backend':'CUDA','render_cpu_enabled':False,
        'final_source':source,'validation_pass_count':validation['pass_count'],
        'glb_roundtrips_passed':6,'human_approval_added':False,'files':entries}
    (staging/'PACKAGE_MANIFEST.json').write_text(json.dumps(package,indent=2)+'\n')
    for item in entries:assert digest(staging/item['path'])==item['sha256']
    staging.rename(target)
    print(json.dumps({'published':True,**verify_uploads(target)},indent=2))


if __name__=='__main__':asyncio.run(main())
