"""Prepare the specifically authorized operator-corrected/reset continuation; no launch."""
import fcntl
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows,rows_hash,validate
from scripts.submission_guard import budget_accounting
from scripts.trial_settings import MODEL,TRIAL

folder=ROOT/'testing/pin-correction-reset-20261024'
path=folder/'continuation.json'
assert not path.exists(), 'Continuation authorization already recorded; inspect before changing it'
receipt=json.loads((ROOT/'artifacts/reports/checkpoint.json').read_text())
report=json.loads((ROOT/'artifacts/reports/validation.json').read_text())
assert receipt['source_job']=='78c0eaf6afba483694c2ca2c6eec4472'
assert report['asset_source_job']==receipt['source_job']
assert all(report['stage_results'][f'{i:02d}']=='PASS' for i in range(4))
rows=guard_rows(ROOT)
accounting=budget_accounting(ROOT/'.runtime/blender52/submissions.sqlite',rows)
assert accounting['reset_id']==1 and not accounting['counted_failures']
assert sum(r['state']=='failed' for r in rows)==18
assert all(r['job'] and r['state'] in {'completed','failed','cancelled'} for r in rows)
plan={'authorization':'User explicitly authorized pin correction/checkpoint reconciliation, zero active error counts with preserved archives, and launching the detached Qwen3.6 continuation.',
      'model':MODEL,'trial':TRIAL,'source_job':receipt['source_job'],'checkpoint':receipt['path'],
      'checkpoint_sha256':receipt['sha256'],'guard_rows_sha256':rows_hash(rows),
      'validation_sha256':hashlib.sha256((ROOT/'artifacts/reports/validation.json').read_bytes()).hexdigest(),
      'validator_sha256':hashlib.sha256((ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_bytes()).hexdigest(),
      'limits':{'per_source':6,'total':20},'failure_budget_reset_id':1,
      'fresh_coding_session':True,'first_stage':'04','diagnostic_report':'testing/PIN_CORRECTION_RESET.md',
      'handoff':'CONTROLLED_CONTINUATION.md',
      'scope':'Preserve independently verified Stages00–03 including the operator-corrected pins. Remaining Stage04 visual grips depend on Stage05 floor/rack/return and Stage07 camera/occlusion repairs; fix these dependencies before declaring04 PASS, then06 collision,07 useful rerenders,08 validation,09 export/roundtrip. Use validation_summary.py and fixed checkpoint/validation tools. Do not modify solved pin geometry, restart empty, regenerate references or reset counters again.'}
path.write_text(json.dumps(plan,indent=2)+'\n')
pointer=ROOT/'testing/ACTIVE_CONTINUATION.json'
(folder/'active-plan.before.json').write_bytes(pointer.read_bytes())
pointer.write_text(json.dumps({'path':str(path.relative_to(ROOT))},indent=2)+'\n')
checked=validate(ROOT)
for name in ['validation.json','checkpoint.json','render-manifest.json']:
    (folder/name).write_bytes((ROOT/'artifacts/reports'/name).read_bytes())
(folder/'attempts.after.json').write_text(json.dumps(rows,indent=2)+'\n')
runtime=ROOT/'.runtime/autonomous-run'
with (runtime/'controller.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state=json.loads((runtime/'state.json').read_text())
    assert state['state']=='blocked' and 'client_pid' not in state
    state.setdefault('stop_history',[]).append({'reason':state.get('reason'),'last_errors':state.get('last_errors',[]),
        'controller_pid':state.pop('controller_pid',None)})
    if 'operator_continuation' in state:
        state.setdefault('operator_continuation_history',[]).append(state.pop('operator_continuation'))
    state.update(state='ready_to_continue',last_errors=[],reason='Operator pin correction verified, active errors zero, detached launch explicitly authorized.',
        reconciliation_plan=str(path.relative_to(ROOT)),prepared_continuation=checked,
        continuation_command='python3 scripts/run_bowling.py --resume --continuation --detach')
    temp=runtime/'state.next';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(runtime/'state.json')
print(json.dumps({'state':'ready_to_continue','started':False,**checked},indent=2))
