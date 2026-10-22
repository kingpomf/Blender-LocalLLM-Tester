"""Z6 operator migration: copy one verified completed source, never replay a job.

The original queue and files remain unchanged. The copied ID retains its original
4.5 manifest/provenance; subsequent revisions run in the separate 5.2 queue.
"""
import json
from pathlib import Path
import shutil
import sys

APP = Path('/home/kingpomf/Development/blender-new-llm-setup')
sys.path.insert(0, str(APP))
from blender_worker.core import Worker, digest, write_json


def main():
    job = 'd5c68e4d5c834c378c60a77882ab00be'
    binary = APP / 'tools/blender-5.2.3-linux-x64/blender'
    old = Worker(APP / 'var/mcp-worker', binary)
    new = Worker(APP / 'var/bowling-blender52', binary)
    try:
        row = old.status(job)
        source = old.source(job)  # verifies completed state and manifest hash
        assert row['manifest']['blender_version'].startswith('4.5.')
        if new.db.execute('SELECT count(*) FROM jobs').fetchone()[0]:
            raise SystemExit('Test queue is not empty; reconcile instead of repeating migration.')
        shutil.copytree(old.jobdir(job), new.jobdir(job))
        assert digest(new.jobdir(job) / 'scene.blend') == digest(source)
        with new.transaction():
            new.db.execute('INSERT INTO jobs(id,state,spec,created,updated,cancel_requested,progress,error,manifest) VALUES(?,?,?,?,?,?,?,?,?)',
                           (row['id'], row['state'], json.dumps(row['spec']), row['created'],
                            row['updated'], row['cancel_requested'],
                            json.dumps(row['progress']) if row['progress'] else None,
                            row['error'], json.dumps(row['manifest'])))
        evidence = {'copied_source_job': job, 'original_version': row['manifest']['blender_version'],
                    'source_sha256': digest(source), 'original_root': str(old.root),
                    'test_root': str(new.root), 'replayed': False}
        write_json(new.root / 'source-migration.json', evidence)
        print(json.dumps(evidence, indent=2))
    finally:
        old.close()
        new.close()


if __name__ == '__main__':
    main()
