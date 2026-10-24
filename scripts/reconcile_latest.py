"""Operator reconciliation v2: terminal states, verified current scene and four renders."""
import asyncio
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import blender52_mcp as worker
from submission_guard import SubmissionGuard

SOURCE='6b947366ef42484291a8ee70a19c32e6'
RENDERS={'overview':'acd151e9599448a4964426ff5b1f03be',
         'player':'5c9d98141f8748f585f3e7fd981b1060',
         'pindeck':'b61e77cd38b944e0b5c3f2f3c3dca0b9',
         'props':'b99e756159724e659b8735c24f26ea0b'}


async def main():
    folder=ROOT/'testing/reconciliation-v2-20261024'
    assert not folder.exists(), 'Existing evidence must not be overwritten'
    folder.mkdir()
    for name in ['BUILD_STATUS.md','HANDOFF.md']:
        shutil.copy2(ROOT/name,folder/(name+'.before'))
    shutil.copy2(ROOT/'.runtime/autonomous-run/state.json',folder/'controller.before.json')
    with closing(sqlite3.connect(ROOT/'.runtime/blender52/submissions.sqlite')) as db, closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:
        db.backup(backup)
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
        worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    statuses=[]
    for row in guard.rows():
        assert row['job'], 'Uncertain job requires reconciliation'
        status=await client.rpc('status',{'job_id':row['job']})
        assert status['state'] in {'completed','failed','cancelled'} and status['state']==row['state']
        statuses.append(status)
    (folder/'jobs.json').write_text(json.dumps(statuses,indent=2)+'\n')
    scene_files={}
    for name in ['scene.blend','scene.json','report.json','author.py']:
        scene_files[name]=await client.fetch(SOURCE,name)
    checkpoint=ROOT/'artifacts/blend/BowlingPair01.blend'
    if checkpoint.exists():
        shutil.copy2(checkpoint,folder/'checkpoint.before.blend')
    shutil.copy2(scene_files['scene.blend']['path'],checkpoint)
    assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()==scene_files['scene.blend']['sha256']
    images=[]
    for role,job in RENDERS.items():
        status=next(s for s in statuses if s['id']==job)
        assert status['spec']['operation']=='render'
        source=status['spec']['source_job']
        source_row=next(s for s in statuses if s['id']==source)
        assert source_row['spec']['source_job']==SOURCE, 'Render is from another asset revision'
        png=next(a['path'] for a in status['manifest']['artifacts'] if a['path'].endswith('.png'))
        fetched=await client.fetch(job,png)
        target=ROOT/'artifacts/renders'/('BowlingPair01_'+role+'.png')
        assert not target.exists(), 'Review existing render before replacement'
        shutil.copy2(fetched['path'],target)
        images.append({'role':role,'job_id':job,'source_job':source,'asset_source':SOURCE,
            'path':str(target.relative_to(ROOT)),'bytes':fetched['bytes'],'sha256':fetched['sha256']})
    evidence={'source_job':SOURCE,'canonical_checkpoint':'artifacts/blend/BowlingPair01.blend',
        'checkpoint_sha256':scene_files['scene.blend']['sha256'],'scene_artifacts':scene_files,
        'render_images':images,'failures_retained':sum(s['state'] in {'failed','cancelled'} for s in statuses),
        'terminal_jobs':len(statuses),'pending_jobs':0,'guard':guard.summary()}
    (folder/'reconciliation.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (ROOT/'artifacts/reports/render-manifest.json').write_text(json.dumps({'asset_source':SOURCE,'images':images},indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':
    asyncio.run(main())
