"""Operator-authorized recovery of the completed-reference wait-timeout block."""
import asyncio
import fcntl
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.check_references import check as reference_check
from scripts.check_resume import check as resume_check,fields
from scripts.checkpoint_bowling import backup_and_write,update_fields
from scripts.context_recovery import reconcile
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import Workflow,atomic_json
import blender52_mcp as worker


async def main():
    runtime=ROOT/'.runtime/autonomous-run'
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        path=runtime/'state.json';state=json.loads(path.read_text())
        assert state['state']=='blocked' and not state.get('client_pid')
        assert state['phase']=='references' and 'coding' not in state['sessions']
        assert state['reason']=='Reference phase reported an explicit STOP/BLOCKED/FAIL'
        checks={'references':reference_check(ROOT),'resume':resume_check(ROOT)}
        assert all(result['passed'] for result in checks.values()),checks
        assert checks['resume']['last_verified_source']=='none'
        events=[json.loads(line) for line in (ROOT/state['events_file']).read_text().splitlines() if line.strip()]
        assert not any(event.get('type')=='error' for event in events)
        errors=[event['part'] for event in events if event.get('type')=='tool_use'
                and event.get('part',{}).get('state',{}).get('status')=='error']
        assert len(errors)==3
        assert all(part['tool']=='imageMCP_wait_image_job'
                   and part['state']['error']=='MCP error -32001: Request timed out' for part in errors)
        known={image['job_id'] for image in json.loads((ROOT/'artifacts/references/manifest.json').read_text())['images']}
        assert {part['state']['input']['job_id'] for part in errors}==known
        guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
        assert not guard.rows(),'Native history is not reference-only'
        client=worker.ProjectTransport(worker.WORKER_HOST,worker.REMOTE_APP,worker.WORKER_ROOT,
            worker.BINARY,str(ROOT/'artifacts/downloads'),dedicated_gpu=worker.DEDICATED_GPU)
        receipt=await reconcile(ROOT,Workflow(ROOT,client,guard),guard,phase='references')
        assert receipt['passed'] and not receipt['pending_jobs'] and not receipt['source']
        for filename in ['BUILD_STATUS.md','HANDOFF.md']:
            metadata=fields((ROOT/filename).read_text())
            assert metadata['Reference phase'].startswith('READY')
            assert metadata['Pending job']=='none' and metadata['Pending reference job']=='none'
        archive=runtime/('reference-wait-recovery-'+str(time.time_ns()))
        archive.mkdir()
        atomic_json(archive/'state.before.json',state)
        for filename in ['BUILD_STATUS.md','HANDOFF.md']:
            (archive/filename).write_text((ROOT/filename).read_text())
        recovery={'at':time.time(),'authorization':'User requested checking/clearing the blocker and a new detached process.',
            'cause':'Read-only image waits exceeded the MCP 60-second call deadline; all accepted images subsequently completed.',
            'receipt':receipt,'checks':checks,'prior_errors':state.get('last_errors',[]),
            'prior_reason':state['reason'],'archive':str(archive.relative_to(ROOT)),
            'counters_reset':False}
        atomic_json(archive/'recovery.json',recovery)
        state.setdefault('operator_recoveries',[]).append(recovery)
        state.update(state='reconciled',last_errors=[],reason='Completed references verified; user-authorized Stage00 launch ready.',
            recovery_context='Operator reconciled the completed reference-only phase after read-only image wait timeouts. '
            'References are verified READY; do not regenerate them. No native source or accepted stages exist yet. '
            'Begin fresh Stage00 through bowling-blender52 on EliteDesk, preserving all counters and safety gates. '
            'Read AGENTS.md and CONTROLLED_CONTINUATION.md, then call blender_workflow_status.')
        for filename,key in [('BUILD_STATUS.md','Status'),('HANDOFF.md','Run status')]:
            backup_and_write(ROOT,filename,update_fields((ROOT/filename).read_text(),{
                key:'IN_PROGRESS','Controller':'RECONCILED: reference waits diagnosed; detached Stage00 relaunch authorized',
                'Next action':'Use verified READY references; begin Stage00 in a fresh detached coding session.'}))
        atomic_json(path,state)
        print(json.dumps(recovery,indent=2))


if __name__=='__main__':asyncio.run(main())
