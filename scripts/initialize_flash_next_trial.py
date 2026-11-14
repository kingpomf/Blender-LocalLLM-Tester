"""Clean only the new linked worktree's inherited active artifacts; preserve original trials."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.checkpoint_bowling import STAGES
from scripts.submission_guard import SubmissionGuard
from scripts.trial_settings import MODEL,TRIAL,WORKER_HOST,WORKER_ROOT
from scripts.workflow_tools import atomic_json


def main():
    archive=ROOT/'.runtime/inherited-template'
    assert not archive.exists(),'Already initialized; inspect current trial state'
    archive.mkdir(parents=True)
    validator=ROOT/'artifacts/scripts/validate_bowling_pair01.py'
    expected=hashlib.sha256(validator.read_bytes()).hexdigest()
    for name in ['scripts','references','blend','exports','renders','reports','downloads']:
        source=ROOT/'artifacts'/name;target=archive/name
        if source.exists():shutil.move(str(source),str(target))
        source.mkdir()
        (source/'.gitkeep').touch()
    shutil.copy2(archive/'scripts/validate_bowling_pair01.py',validator)
    assert hashlib.sha256(validator.read_bytes()).hexdigest()==expected
    original=Path('/Users/start/Development/Blender-LocalLLM-Tester/artifacts/reports')
    for name in ['blender-api-catalog.json','blender-api-catalog-receipt.json']:
        shutil.copy2(original/name,ROOT/'artifacts/reports'/name)
    for name in ['BUILD_STATUS.md','HANDOFF.md']:
        shutil.copy2(ROOT/name,archive/name)
    source='none'
    fields={'Default model':MODEL,'Actual model used':'not started','Trial queue':WORKER_ROOT,
        'Execution host':WORKER_HOST,'Controller':'NOT_STARTED; fresh launch authorized','Reference phase':'NOT_STARTED',
        'Pending reference job':'none','Pending job':'none','Pending source job':'none','Accepted job IDs':'none',
        'Next action':'Generate fresh references, then author Stage00. Strata stays on Z6; Blender5.2/CUDA run on EliteDesk.'}
    metadata='\n'.join('- '+key+': '+value for key,value in fields.items())
    rows='\n'.join(f'| {i:02d} | {name} | NOT_STARTED | Fresh Flash-Next trial. |' for i,name in enumerate(STAGES))
    (ROOT/'BUILD_STATUS.md').write_text('# BowlingPair01 — Flash-Next / EliteDesk\n\n- Status: NOT_STARTED\n- Next stage: 00 — Contract and scene safety\n- Active source job: '+source+'\n'+metadata+'\n\n## Stage ledger\n\n| Stage | Name | Result | Evidence |\n| --- | --- | --- | --- |\n'+rows+'\n\n## Next action\n\n'+fields['Next action']+'\n')
    (ROOT/'HANDOFF.md').write_text('# Flash-Next / EliteDesk fresh handoff\n\n- Run status: NOT_STARTED\n- Current stage: 00 — Contract and scene safety\n- Last verified source job: none\n'+metadata+'\n')
    (ROOT/'testing/ACTIVE_CONTINUATION.json').unlink(missing_ok=True)
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite');assert not guard.rows()
    atomic_json(ROOT/'.runtime/fresh-trial.json',{'model':MODEL,'trial':TRIAL,'worker':WORKER_HOST,'created':time.time(),'archive':str(archive.relative_to(ROOT))})
    print(json.dumps({'initialized':True,'model':MODEL,'trial':TRIAL,'source':None,'attempts':0,'validator_sha256':expected},indent=2))


if __name__=='__main__':main()
