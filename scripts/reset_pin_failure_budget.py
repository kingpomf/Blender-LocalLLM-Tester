"""One explicit user-authorized counter reset; preserve rows, artifacts and old database."""
import asyncio
from contextlib import closing
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.submission_guard import SubmissionGuard
from scripts.checkpoint_bowling import publish_source
import blender52_mcp as worker

SOURCE='e8630f4b79ba468ebd18ef53e2f1d51d'


async def main():
    folder=ROOT/'testing/pin-correction-reset-20261024'
    assert not folder.exists(), 'Reset already attempted; inspect existing evidence, never silently reset again'
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=json.loads((runtime/'state.json').read_text())
        assert state['state']=='blocked' and 'client_pid' not in state
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        with guard.locked():
            before=guard.rows()
            assert len(before)==48 and sum(row['state']=='failed' for row in before)==18
            assert all(row['job'] and row['state'] in {'completed','failed','cancelled'} for row in before)
            client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,
                worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
            for row in before:
                observed=await client.rpc('status',{'job_id':row['job']})
                assert observed['state']==row['state'], 'Remote state changed; reconcile before reset'
            folder.mkdir()
            for name in ['BUILD_STATUS.md','HANDOFF.md','CONTROLLED_CONTINUATION.md','artifacts/scripts/stage03_pins_v2.py']:
                target=folder/'before'/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,target)
            shutil.copy2(runtime/'state.json',folder/'controller.before.json')
            shutil.copy2(ROOT/'artifacts/blend/BowlingPair01.blend',folder/'checkpoint.before.blend')
            with closing(sqlite3.connect(guard.path)) as source, closing(sqlite3.connect(folder/'guard.before.sqlite')) as backup:
                source.backup(backup)
            (folder/'attempts.before.json').write_text(json.dumps(before,indent=2)+'\n')
            receipt=await publish_source(ROOT,SOURCE)
            with guard.connect() as db:
                cutoff=db.execute('SELECT max(rowid) FROM attempts').fetchone()[0]
                db.execute('INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(?,?,?)',
                    (cutoff,'User explicitly requested zeroing the error count after pin correction/checkpoint reconciliation and launching detach',time.time()))
                reset_id=db.execute('SELECT last_insert_rowid()').fetchone()[0]
            assert guard.rows()==before
            summary=guard.summary()
            assert summary['failed_count']==0 and summary['historical_failed_count']==18
            evidence={'reset_id':reset_id,'cutoff_rowid':cutoff,'counted_failures':0,
                      'historical_failures_preserved':18,'attempt_rows_unchanged':True,
                      'same_trial':worker.TRIAL,'source_job':SOURCE,'checkpoint':receipt,
                      'archive':str(folder.relative_to(ROOT)),
                      'duplicate_failed_submission_protection':'retained'}
            (folder/'reset-receipt.json').write_text(json.dumps(evidence,indent=2)+'\n')
            print(json.dumps(evidence,indent=2))


if __name__=='__main__':asyncio.run(main())
