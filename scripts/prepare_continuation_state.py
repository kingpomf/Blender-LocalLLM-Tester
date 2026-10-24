"""Mark the stopped controller ready for explicit continuation; never launches it."""
import fcntl
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import validate

validated=validate(ROOT)
runtime=ROOT/'.runtime/autonomous-run'
path=runtime/'state.json'
with (runtime/'controller.lock').open('a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    state=json.loads(path.read_text())
    assert state['state']=='blocked' and state['model']==validated['model']
    assert 'client_pid' not in state
    state['prior_stop']={'state':state['state'],'reason':state['reason'],
                         'last_errors':state.get('last_errors',[]),'controller_pid':state.pop('controller_pid',None)}
    state.update(state='ready_to_continue',last_errors=[],
                 reason='Operator reconciliation complete; awaiting explicit continuation command.',
                 reconciliation_plan='testing/reconciliation-20261024/continuation.json',
                 continuation_command='python3 scripts/run_bowling.py --resume --continuation --detach')
    temporary=path.with_suffix('.next')
    temporary.write_text(json.dumps(state,indent=2)+'\n')
    temporary.replace(path)
print(json.dumps({'state':'ready_to_continue','started':False,'remaining_total':validated['remaining_total'],
                  'remaining_on_source':validated['remaining_on_source'],'command':state['continuation_command']},indent=2))
