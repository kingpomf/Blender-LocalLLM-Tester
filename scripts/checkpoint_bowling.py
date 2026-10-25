"""Verified artifact publication and deterministic ledger updates; no scene generation."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import importlib.util
import os

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.check_resume import fields
from scripts.continuation_preflight import guard_rows
from scripts.submission_guard import budget_accounting

STAGES=['Contract and scene safety','Lane pair and markings','Gutters, decks and pit',
        'Reusable bowling pins','Reusable bowling balls','Return, seating and alley dressing',
        'Materials, hierarchy and collision','Presentation cameras and lighting','Final measured validation','Export and delivery']


def checksum(path):
    with Path(path).open('rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()


def saved_mesh_signature(data):
    meshes=sorted([o for o in data['objects'] if o['type']=='MESH'],key=lambda o:o['name'])
    used={name for obj in meshes for name in obj.get('materials',[]) if name}
    materials=sorted([m for m in data['materials'] if m['name'] in used],key=lambda m:m['name'])
    return hashlib.sha256(json.dumps({'meshes':meshes,'materials':materials},sort_keys=True).encode()).hexdigest()


def update_fields(text,updates):
    """Replace all duplicate metadata keys, preserving unrelated prose and stage rows."""
    lines=text.splitlines()
    for key,value in updates.items():
        pattern=re.compile(r'^- '+re.escape(key)+r':')
        matches=[i for i,line in enumerate(lines) if pattern.match(line)]
        if matches:
            lines[matches[0]]=f'- {key}: {value}'
            lines=[line for i,line in enumerate(lines) if i==matches[0] or i not in matches]
        else:
            lines.insert(2,f'- {key}: {value}')
    return '\n'.join(lines)+'\n'


def replace_stage_table(text,rows):
    """Emit exactly ten rows, removing stale duplicate REPAIRING/ACCEPTED rows."""
    lines=text.splitlines()
    start=next(i for i,line in enumerate(lines) if line.startswith('## Stage ledger'))
    end=next((i for i in range(start+1,len(lines)) if lines[i].startswith('## ')),len(lines))
    table=['## Stage ledger','','| Stage | Name | Result | Evidence |','| --- | --- | --- | --- |']
    table += [f'| {i:02d} | {STAGES[i]} | {state} | {evidence.replace("|","/")} |' for i,(state,evidence) in enumerate(rows)]
    return '\n'.join(lines[:start]+table+['']+lines[end:])+'\n'


def backup_and_write(root,name,text):
    root=Path(root); path=root/name
    archive=root/'.runtime/checkpoint-history'
    archive.mkdir(parents=True,exist_ok=True)
    if path.exists():
        previous=archive/(path.name+'.'+checksum(path))
        if not previous.exists():shutil.copy2(path,previous)
    temp=path.with_suffix(path.suffix+'.next')
    temp.write_text(text)
    temp.replace(path)


def sync_ledgers(root):
    root=Path(root)
    receipt=json.loads((root/'artifacts/reports/checkpoint.json').read_text())
    validation=json.loads((root/'artifacts/reports/validation.json').read_text())
    source=receipt['source_job']
    assert validation['asset_source_job']==source, 'Validation is for another scene'
    assert checksum(root/receipt['path'])==receipt['sha256'], 'Canonical scene changed'
    attempts=guard_rows(root)
    assert all(r['job'] and r['state'] in {'completed','failed','cancelled'} for r in attempts), 'Reconcile pending/uncertain jobs before ledger synchronization'
    assert any(r['job']==source and r['state']=='completed' for r in attempts)
    rows=[]
    for i in range(8):
        result=validation['stage_results'][f'{i:02d}']
        state='IN_PROGRESS' if result=='UNRESOLVED' else result
        relevant=[c for c in validation['checks'] if c['stage']==f'{i:02d}' and c['status']!='PASS']
        evidence=('Measured PASS' if not relevant else f'{len(relevant)} failed/unresolved checks: '+', '.join(c['id'] for c in relevant[:4]))
        rows.append((state,evidence+'; artifacts/reports/validation.json; validation job '+validation['validation_job']))
    rows.append(('PASS' if validation['passed'] else 'FAIL',
        f"Read-only validator completed: {validation['pass_count']} PASS, {validation['fail_count']} FAIL, {validation['unresolved_count']} unresolved; source {source}."))
    rows.append(('NOT_STARTED','No qualified final export/round-trip delivery yet.'))
    next_stage=next((i for i,(state,_) in enumerate(rows) if state!='PASS'),9)
    accounting=budget_accounting(root/'.runtime/blender52/submissions.sqlite',attempts)
    failure_count=len(accounting['counted_failures'])
    historical_failures=sum(r['state'] in {'failed','cancelled'} for r in attempts)
    source_failures=sum(r['source']==source for r in accounting['counted_failures'])
    controller_path=root/'.runtime/autonomous-run/state.json'
    controller=json.loads(controller_path.read_text()) if controller_path.exists() else {}
    run_status='BLOCKED' if controller.get('state') in {'blocked','interrupted'} else 'IN_PROGRESS'
    common={'Reference phase':'READY','Pending reference job':'none','Pending job':'none','Pending source job':'none',
            'Validation state':'completed current-source measurements; see artifacts/reports/validation.json',
            'Operator validation pending':'none',
            'Checkpoint SHA-256':receipt['sha256'],
            'API corrections':str(len(accounting['api_corrections']))+' recoverable API errors excluded from hard-failure budget; original jobs preserved',
            'Failure budget':f'6 per source / 20 total; current failures {failure_count}; {source_failures} on current source; {historical_failures} historical failures preserved; reset epoch {accounting["reset_id"]}',
            'Controller':'RUNNING; continue current session' if controller.get('state')=='running' else 'STOPPED; awaiting explicit operator continuation',
            'Operator intervention':('Operator supplied and verified pin-profile/cap/band correction; user authorized archived counter reset; all original jobs preserved'
                if (root/'testing/pin-correction-reset-20261024/pin-report.json').exists() else
                'Latest native scene and renders reconciled; fixed read-only validation; history preserved'),
            'Next action':f'Read CONTROLLED_CONTINUATION.md and the active handoff report; repair Stage {next_stage:02d} and dependencies; use verified checkpoint tools.'}
    build=(root/'BUILD_STATUS.md').read_text()
    build=replace_stage_table(build,rows)
    build=update_fields(build,{**common,'Status':run_status,'Next stage':f'{next_stage:02d} — {STAGES[next_stage]}',
        'Active source job':source,'Active checkpoint':receipt['path'],'Accepted job IDs':', '.join(r['job'] for r in attempts)})
    handoff=update_fields((root/'HANDOFF.md').read_text(),{**common,'Run status':run_status,
        'Current stage':f'{next_stage:02d} — {STAGES[next_stage]}','Last verified source job':source,
        'Pending source job':'none','Latest verified local checkpoint':receipt['path']})
    # Reconciled reports supersede old forward-looking text rather than leaving
    # contradictory restart/source instructions below the current metadata.
    build=build[:build.index('## Next action')]+'## Next action\n\n'+common['Next action']+'\n\n## Evidence\n\nNative and local measurements are in artifacts/reports/validation.json.\nHistorical ledgers, jobs, guard backups and operator assistance are preserved\nunder testing/. Only current measured PASS results may be carried forward.\n'
    header=handoff.split('\n\n',1)[0]
    metadata='\n'.join(line for line in handoff.splitlines() if line.startswith('- '))
    handoff=header+'\n\n'+metadata+'\n\nThe current source is a completed integrity-verified repair base, not a claim\nthat all stages passed. Use the measured validator and render reviews. Failed\njobs never become sources. Preserve all historical failures and all real STOPs.\n'
    backup_and_write(root,'BUILD_STATUS.md',build)
    backup_and_write(root,'HANDOFF.md',handoff)
    return {'source':source,'next_stage':f'{next_stage:02d}','failure_count':failure_count,
            'historical_failures_preserved':historical_failures,'pending_jobs':0}


async def publish_source(root,source,client=None):
    root=Path(root)
    assert re.fullmatch('[a-f0-9]{32}',source)
    sys.path.insert(0,str(root/'scripts'))
    if client is None:
        import blender52_mcp as worker
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(root/'artifacts/downloads'))
    attempts=guard_rows(root)
    assert any(row['job']==source and row['state']=='completed' and row['operation']=='author' for row in attempts), 'Source must be a completed authoring job in this trial'
    status=await client.rpc('status',{'job_id':source})
    assert status['state']=='completed'
    native=await client.fetch(source,'scene.blend')
    scene=await client.fetch(source,'scene.json')
    path=root/'artifacts/blend/BowlingPair01.blend'
    if path.exists() and checksum(path)!=native['sha256']:
        history=root/'.runtime/checkpoint-history'; history.mkdir(parents=True,exist_ok=True)
        previous=history/(checksum(path)+'.blend')
        if not previous.exists():shutil.copy2(path,previous)
    temp=path.with_suffix('.next.blend');shutil.copy2(native['path'],temp)
    assert checksum(temp)==native['sha256']
    temp.replace(path)
    receipt={'source_job':source,'path':str(path.relative_to(root)),'sha256':native['sha256'],'bytes':native['bytes'],'scene_json':scene}
    (root/'artifacts/reports/checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n')
    # Update source/checkpoint fields consistently even before validation, without
    # assigning a new PASS or destroying the previous measured stage evidence.
    for name,updates in [('BUILD_STATUS.md',{'Active source job':source,'Active checkpoint':receipt['path']}),
                         ('HANDOFF.md',{'Last verified source job':source,'Latest verified local checkpoint':receipt['path']})]:
        text=update_fields((root/name).read_text(),{**updates,'Checkpoint SHA-256':receipt['sha256'],
            'Accepted job IDs':', '.join(r['job'] for r in attempts),'Pending job':'none'})
        backup_and_write(root,name,text)
    return receipt


async def publish_render(root,role,job_id,asset_source,client=None):
    root=Path(root)
    assert role in {'overview','player','pindeck','props'}
    assert all(re.fullmatch('[a-f0-9]{32}',value) for value in [job_id,asset_source])
    sys.path.insert(0,str(root/'scripts'))
    if client is None:
        import blender52_mcp as worker
        client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(root/'artifacts/downloads'))
    render=await client.rpc('status',{'job_id':job_id})
    assert render['state']=='completed' and render['spec']['operation']=='render'
    camera_source=render['spec']['source_job']
    camera_job=await client.rpc('status',{'job_id':camera_source})
    assert camera_source==asset_source or camera_job['spec'].get('source_job')==asset_source, 'Camera revision is not based on this asset source'
    base_json=await client.fetch(asset_source,'scene.json')
    camera_json=await client.fetch(camera_source,'scene.json')
    def signature(path):
        data=json.loads(Path(path).read_text())
        return saved_mesh_signature(data)
    assert signature(base_json['path'])==signature(camera_json['path']), 'Render-only camera revision changed saved mesh description or materials'
    png=next(a['path'] for a in render['manifest']['artifacts'] if a['path'].endswith('.png'))
    fetched=await client.fetch(job_id,png)
    from scripts.check_references import image_dimensions
    dimensions=image_dimensions(Path(fetched['path']))
    assert dimensions[0]>=1280 and dimensions[1]>=720
    destination=root/'artifacts/renders'/f'BowlingPair01_{role}.png'
    if destination.exists() and checksum(destination)!=fetched['sha256']:
        history=root/'.runtime/checkpoint-history';history.mkdir(parents=True,exist_ok=True)
        previous=history/(destination.name+'.'+checksum(destination)+'.png')
        if not previous.exists():shutil.copy2(destination,previous)
    temp=destination.with_suffix('.next.png');shutil.copy2(fetched['path'],temp)
    assert checksum(temp)==fetched['sha256']
    temp.replace(destination)
    path=root/'artifacts/reports/render-manifest.json'
    manifest=json.loads(path.read_text()) if path.exists() else {'asset_source':asset_source,'images':[]}
    if manifest['asset_source']!=asset_source:
        backup_and_write(root,'artifacts/reports/render-manifest.json',json.dumps({'asset_source':asset_source,'images':[]},indent=2)+'\n')
        manifest={'asset_source':asset_source,'images':[]}
    image={'role':role,'job_id':job_id,'source_job':camera_source,'asset_source':asset_source,
           'path':str(destination.relative_to(root)),'bytes':fetched['bytes'],'sha256':fetched['sha256'],
           'width':dimensions[0],'height':dimensions[1]}
    previous=next((i for i in manifest['images'] if i['role']==role and i['sha256']==image['sha256']),None)
    if previous and 'visual_review' in previous:
        image['visual_review']=previous['visual_review']
    manifest['images']=[i for i in manifest['images'] if i['role']!=role]+[image]
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    return {**image,'next':'Inspect actual pixels and record visual_review for this image hash; publication alone does not imply PASS.'}


def main():
    if importlib.util.find_spec('mcp') is None:
        python=ROOT.parent/'blender-new-llm-setup/.venv/bin/python'
        os.execv(str(python),[str(python),str(Path(__file__).resolve()),*sys.argv[1:]])
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source')
    group.add_argument('--sync-ledgers',action='store_true')
    group.add_argument('--render',nargs=2,metavar=('ROLE','JOB_ID'))
    parser.add_argument('--asset-source')
    args=parser.parse_args()
    if args.render and not args.asset_source:parser.error('--render requires --asset-source')
    result=(sync_ledgers(ROOT) if args.sync_ledgers else asyncio.run(publish_render(ROOT,args.render[0],args.render[1],args.asset_source))
            if args.render else asyncio.run(publish_source(ROOT,args.source)))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
