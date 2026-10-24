"""Record this explicitly requested continuation; does not launch any session/job."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows, rows_hash, validate
from scripts.trial_settings import MODEL, TRIAL

folder=ROOT/'testing/reconciliation-20261024'
path=folder/'continuation.json'
assert not path.exists(), 'Authorization already recorded; inspect rather than overwrite'
rows=guard_rows(ROOT)
assert len([row for row in rows if row['state']=='failed'])==6
assert len(rows)==13 and all(row['state'] in {'completed','failed'} for row in rows)
checkpoint=ROOT/'artifacts/blend/BowlingPair01.blend'
plan={'authorization':'User explicitly requested reconciliation, doubled limits, ball diagnostics and an operator-invoked controlled continuation.',
      'model':MODEL,'trial':TRIAL,'source_job':'d1ce998472c349ac9f9fc2775afefdf6',
      'checkpoint':str(checkpoint.relative_to(ROOT)),
      'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
      'guard_rows_sha256':rows_hash(rows),'limits':{'per_source':6,'total':12},
      'diagnostic_report':'testing/BALL_GENERATION_DIAGNOSTICS.md',
      'handoff':'CONTROLLED_CONTINUATION.md','first_stage':'01',
      'scope':'Repair measured defects in01–04 from existing source, then continue05–09; no empty restart or failure reset.'}
path.write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(validate(ROOT),indent=2))
