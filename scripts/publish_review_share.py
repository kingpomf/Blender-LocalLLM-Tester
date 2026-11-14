"""Publish a versioned, hash-verified OneDrive review package without claiming approval."""
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
PARENT=Path('/Users/start/Library/CloudStorage/OneDrive-Personal/AI-Creative/Review/Blender/Z6')
NAME='Kart01-FlashNext-Strata-20261025-6078c288'


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


async def main():
    assert PARENT.is_dir(),'Verify shared review parent before publishing'
    target=PARENT/NAME
    if target.exists():
        manifest=json.loads((target/'PACKAGE_MANIFEST.json').read_text())
        for item in manifest['files']:
            path=target/item['path'];assert path.is_file() and digest(path)==item['sha256']
        uploaded=[];pending=[]
        for relative in [item['path'] for item in manifest['files']]+['PACKAGE_MANIFEST.json']:
            result=subprocess.run(['fileproviderctl','evaluate',str(target/relative)],capture_output=True,text=True,timeout=20,check=True)
            match=re.search(r'\bisUploaded\s*=\s*([01]);',result.stdout)
            (uploaded if match and match[1]=='1' else pending).append(relative)
        print(json.dumps({'already_published':True,'path':str(target),'files_hash_verified':len(manifest['files']),
            'provider_uploaded':len(uploaded),'provider_pending_or_unknown':pending,'status':'REVIEW_REQUIRED'},indent=2));return
    state=json.loads((ROOT/'RUN_STATE.json').read_text())
    assert state['verified_source']=='6078c288fd7b4de38c095a4fd071ab5c'
    assert state['evidence']['numeric']['passed'] is True
    assert digest(ROOT/'artifacts/reports/validation.json')==state['evidence']['numeric']['sha256']
    assert digest(ROOT/'artifacts/blend/Kart01.blend')==state['checkpoint']['sha256']
    assert digest(ROOT/'artifacts/exports/Kart01.glb')==state['evidence']['delivery']['deliverables']['glb']
    # Fetch the already-completed presentation scene, not a new author/render job.
    sys.path.insert(0,'/Users/start/Development/blender-new-llm-setup')
    from blender_worker.transport import SSHTransport
    client=SSHTransport('kingpomf@z6-llm','/home/kingpomf/Development/blender-new-llm-setup',
        '/home/kingpomf/Development/blender-new-llm-setup/var/kart-simplified-flash-next-strata-20261025-r1',
        '/home/kingpomf/Development/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender',str(ROOT/'artifacts/downloads'))
    presentation=await client.fetch('ec42914ecc074926a928b1a94f28c5c7','scene.blend')
    staging=PARENT/('.'+NAME+'.staging')
    assert not staging.exists(),'Partial package exists; inspect it instead of overwriting'
    staging.mkdir()
    files={
        'Kart01.blend':ROOT/'artifacts/blend/Kart01.blend',
        'Kart01.glb':ROOT/'artifacts/exports/Kart01.glb',
        'Kart01_Presentation.blend':Path(presentation['path']),
        'Kart01_preview.png':ROOT/'artifacts/renders/Kart01_perspective.png',
        'RUN_STATE.json':ROOT/'RUN_STATE.json',
        'reports/validation.json':ROOT/'artifacts/reports/validation.json',
        'reports/BUILD_REPORT.md':ROOT/'artifacts/reports/BUILD_REPORT.md',
        'reports/roundtrip-reference.json':ROOT/'artifacts/downloads/5518fc08437c451d9caf5caeec1d5532/report.json',
        'source/KART_SIMPLIFIED.md':ROOT/'spec/KART_SIMPLIFIED.md',
    }
    for view in ['perspective','front','side','rear']:
        source=ROOT/f'artifacts/renders/Kart01_{view}.png'
        assert digest(source)==state['evidence']['visual']['renders_sha256'][view]
        files[f'renders/Kart01_{view}.png']=source
    for name in ['build.py','review.py','roundtrip.py']:files['source/'+name]=ROOT/'artifacts/scripts'/name
    for name in ['helpers.py','presentation.py','validate.py']:files['source/supplied/'+name]=ROOT/'support/kart'/name
    entries=[]
    for relative,source in files.items():
        assert source.is_file(),str(source)
        destination=staging/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        expected=digest(source);shutil.copy2(source,destination)
        assert digest(destination)==expected and destination.stat().st_size==source.stat().st_size
        entries.append({'path':relative,'bytes':destination.stat().st_size,'sha256':expected})
    readme='''# Kart01 — Qwen3.8 Flash-Next / Strata review package

Status: REVIEW REQUIRED, not approved or COMPLETE.

Open Kart01_Presentation.blend for the scene with cameras/lights/ground, or
Kart01.blend for the asset-only native scene. Kart01.glb is the asset export.
Kart01_preview.png and renders/ contain the four actual 512x512 renders.

The supplied numeric validator passed:17 required meshes,1192 triangles,
envelope1.10 x1.785 x0.94 m. Local delivery structure checks also passed.
The text-only trial agent did not inspect pixels and correctly marked visual
acceptance BLOCKED. Operator preview found a recognizable kart and distinct
views; body/tire color appearance looks lighter than intended and merits review.
Do not interpret numeric pass or file publication as full visual acceptance.

Provenance: z6-llama/qwen38-flash-next through Strata; Blender5.2.3 LTS on Z6;
CPU scene authoring and CPU rendering, no protected GPU work interrupted.
Asset source6078c288fd7b4de38c095a4fd071ab5c; presentation/validation source
ec42914ecc074926a928b1a94f28c5c7; render job6f8b6d395bf54b51ac8967a0b4ff99c4.

Important delivery-audit note: reports/roundtrip-reference.json validates a
separately exported68344-byte GLB, not the byte-identical50216-byte delivered
Kart01.glb. Its findings are reference evidence, not proof that the exact delivered
file was reimported. Final delivery provenance review remains outstanding.

Original model-authored report/ledger are included unaltered under reports/ and
RUN_STATE.json. The supplied helpers/rig/validator and model-authored submissions
are included under source/ for attribution/reproducibility. Historical job paths
inside those reports refer to the original workspace; package-relative paths and
hashes are listed in PACKAGE_MANIFEST.json. All listed copies were hash-verified.
'''
    path=staging/'README.md';path.write_text(readme)
    entries.append({'path':'README.md','bytes':path.stat().st_size,'sha256':digest(path)})
    manifest={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'status':'REVIEW_REQUIRED',
        'model':'z6-llama/qwen38-flash-next','backend':'strata','blender_version':'5.2.3 LTS',
        'asset_source':state['verified_source'],'presentation_source':'ec42914ecc074926a928b1a94f28c5c7',
        'numeric_passed':True,'visual_approved':False,'exact_delivered_glb_roundtrip_verified':False,
        'files':entries}
    (staging/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for item in entries:assert digest(staging/item['path'])==item['sha256']
    staging.rename(target)
    print(json.dumps({'published':True,'path':str(target),'files_verified':len(entries),
        'total_bytes':sum(item['bytes'] for item in entries),'status':'REVIEW_REQUIRED',
        'cloud_sync':'Placed in OneDrive-synced folder; provider upload acknowledgement not independently verified'},indent=2))


if __name__=='__main__':asyncio.run(main())
