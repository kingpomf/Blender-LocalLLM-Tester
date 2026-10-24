"""Operator-authorized read/fetch reconciliation; no scene submission or guard reset."""
import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
from contextlib import closing

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import blender52_mcp as worker

SOURCE='d1ce998472c349ac9f9fc2775afefdf6'


async def main():
    folder=ROOT/'testing/reconciliation-20261024'
    assert not folder.exists(), 'Existing reconciliation evidence; inspect rather than overwrite'
    folder.mkdir()
    for name in ['BUILD_STATUS.md','HANDOFF.md']:
        shutil.copy2(ROOT/name,folder/(name+'.before'))
    shutil.copy2(ROOT/'.runtime/autonomous-run/state.json',folder/'controller.before.json')
    with closing(sqlite3.connect(ROOT/'.runtime/blender52/submissions.sqlite')) as source, closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:
        source.backup(backup)
    with closing(sqlite3.connect(f'file:{ROOT}/.runtime/blender52/submissions.sqlite?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        attempts=[dict(row) for row in db.execute('SELECT * FROM attempts ORDER BY rowid')]
    assert all(row['job'] for row in attempts), 'Uncertain submission requires reconciliation before continuation'
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
        worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    statuses=[]
    for row in attempts:
        status=await client.rpc('status',{'job_id':row['job']})
        assert status['state'] in {'completed','failed','cancelled'}, 'A job is still active'
        assert status['state']==row['state'], 'Local/remote job state mismatch; review before modifying ledger'
        statuses.append(status)
    (folder/'jobs.json').write_text(json.dumps(statuses,indent=2)+'\n')
    completed=next(row for row in statuses if row['id']==SOURCE)
    fetched={}
    for name in ['scene.blend','scene.json','report.json','author.py']:
        fetched[name]=await client.fetch(SOURCE,name)
    checkpoint=ROOT/'artifacts/blend/BowlingPair01.blend'
    assert not checkpoint.exists(), 'Existing canonical checkpoint must be reviewed before replacement'
    shutil.copy2(fetched['scene.blend']['path'],checkpoint)
    actual=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert actual==fetched['scene.blend']['sha256']
    evidence={'source_job':SOURCE,'source_manifest':completed['manifest'],'fetched':fetched,
              'canonical_checkpoint':str(checkpoint.relative_to(ROOT)),'checkpoint_sha256':actual,
              'failed_count':sum(row['state']=='failed' for row in statuses),
              'accepted_jobs':len(statuses),'pending_jobs':0,
              'scope':'Artifact integrity/state only; stage acceptance is independently audited.'}
    (folder/'reconciliation.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':
    asyncio.run(main())
