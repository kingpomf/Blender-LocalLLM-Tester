"""Record the user-authorized20-total continuation, preserving prior plans/history."""
import fcntl
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows, rows_hash, validate
from scripts.trial_settings import MODEL, TRIAL
from scripts.submission_guard import FAILURE_LIMIT_PER_SOURCE, FAILURE_LIMIT_TOTAL

folder=ROOT/'testing/reconciliation-v2-20261024'
path=folder/'continuation.json'
assert not path.exists(), 'Plan already exists; do not overwrite authorization'
receipt=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
report=json.loads((ROOT/'artifacts/reports/validation.json').read_text())
assert report['asset_source_job']==receipt['source_job']
rows=guard_rows(ROOT)
assert sum(r['state'] in {'failed','cancelled'} for r in rows)==12
assert all(r['job'] and r['state'] in {'completed','failed','cancelled'} for r in rows)
assert (FAILURE_LIMIT_PER_SOURCE,FAILURE_LIMIT_TOTAL)==(6,20)
plan={'authorization':'User requested reconciling latest scene/renders, repairing validation/checkpoints and raising total failures to20.',
      'model':MODEL,'trial':TRIAL,'source_job':receipt['source_job'],'checkpoint':receipt['path'],
      'checkpoint_sha256':receipt['sha256'],'guard_rows_sha256':rows_hash(rows),
      'validation_sha256':hashlib.sha256((ROOT/'artifacts/reports/validation.json').read_bytes()).hexdigest(),
      'validator_sha256':hashlib.sha256((ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_bytes()).hexdigest(),
      'limits':{'per_source':6,'total':20},'diagnostic_report':'testing/VALIDATION_RECONCILIATION_V2.md',
      'handoff':'CONTROLLED_CONTINUATION.md','first_stage':'02',
      'scope':'Preserve measured Stage00/01 passes; repair Stage02 gutter adjacency, Stage03 pin topology/bands, Stage04 grip visibility, Stage05 floor/return/dressing, Stage06 collision, Stage07 framing/occlusion. Revalidate Stage08 and finish Stage09 only after all required checks pass. Do not restart or repeat solved ball API failures.'}
path.write_text(json.dumps(plan,indent=2)+'\n')
pointer=ROOT/'testing/ACTIVE_CONTINUATION.json'
if pointer.exists():
    (folder/'active-plan.before.json').write_bytes(pointer.read_bytes())
pointer.write_text(json.dumps({'path':str(path.relative_to(ROOT))},indent=2)+'\n')
checked=validate(ROOT)
runtime=ROOT/'.runtime/autonomous-run'
with (runtime/'controller.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state=json.loads((runtime/'state.json').read_text())
    assert state['state']=='blocked' and 'client_pid' not in state
    state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
                                               'controller_pid':state.pop('controller_pid',None)})
    state.update(state='ready_to_continue',last_errors=[],reason='Latest scene/renders reconciled; fixed validator completed. Awaiting explicit operator continuation.',
                 reconciliation_plan=str(path.relative_to(ROOT)),continuation_command='python3 scripts/run_bowling.py --resume --continuation --detach',
                 prepared_continuation=checked)
    temporary=runtime/'state.next'
    temporary.write_text(json.dumps(state,indent=2)+'\n')
    temporary.replace(runtime/'state.json')
print(json.dumps({'state':'ready_to_continue','started':False,**checked},indent=2))
