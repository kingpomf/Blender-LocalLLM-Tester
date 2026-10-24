"""Save versionable copies of completed validation/checkpoint/render proof; no jobs."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows

folder=ROOT/'testing/reconciliation-v2-20261024'
proof={}
for name in ['validation.json','checkpoint.json','render-manifest.json']:
    source=ROOT/'artifacts/reports'/name
    destination=folder/name
    if destination.exists():
        assert destination.read_bytes()==source.read_bytes(), 'Snapshot changed; preserve old evidence before any revision'
    else:
        destination.write_bytes(source.read_bytes())
    proof[name]={'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}
rows=guard_rows(ROOT)
assert all(r['state'] in {'completed','failed','cancelled'} for r in rows)
(folder/'guard-after.json').write_text(json.dumps(rows,indent=2)+'\n')
(folder/'proof-manifest.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'snapshotted':proof,'terminal_jobs':len(rows),'failed':sum(r['state']=='failed' for r in rows)},indent=2))
