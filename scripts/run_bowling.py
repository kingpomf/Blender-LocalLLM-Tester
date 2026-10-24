"""One launch for reference review followed by continuous MTP coding; no GPU controls."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.check_references import check as reference_check
from scripts.check_resume import check as resume_check, fields
from scripts.trial_settings import MODEL


def live_status(root,state) -> dict:
    result=dict(state)
    path=Path(root)/'.runtime/blender52/submissions.sqlite'
    if path.exists():
        from scripts.continuation_preflight import guard_rows
        from scripts.submission_guard import budget_accounting, FAILURE_LIMIT_PER_SOURCE, FAILURE_LIMIT_TOTAL
        rows=guard_rows(root)
        accounting=budget_accounting(path,rows)
        result['live_failure_budget']={'current_failures':len(accounting['counted_failures']),
            'historical_failures_preserved':sum(r['state'] in {'failed','cancelled'} for r in rows),
            'per_source_limit':FAILURE_LIMIT_PER_SOURCE,'total_limit':FAILURE_LIMIT_TOTAL,
            'reset_id':accounting['reset_id']}
    return result


def snapshot():
    text=(ROOT/'BUILD_STATUS.md').read_text()
    metadata=fields(text)
    return {'status':metadata.get('Status'),
            'passed':set(re.findall(r'^\| (0[0-9]) \| [^|]+ \| PASS \|',text,re.MULTILINE))}


def workflow(run_phase, get_snapshot, references_ready, consistent, recover=None):
    """Advance on evidence; allow two diagnostic repairs, never bypass real STOPs."""
    initial=get_snapshot()
    if initial['status'] in {'BLOCKED','FAIL'}:
        raise RuntimeError('Existing trial is blocked/failed; operator reconciliation required')
    if initial['status']=='COMPLETE':
        if references_ready() and consistent():
            return
        raise RuntimeError('COMPLETE conflicts with reference or checkpoint evidence')
    repairs=0
    while not references_ready():
        result=run_phase('references') or {}
        if result.get('hard_stop') or get_snapshot()['status'] in {'BLOCKED','FAIL'}:
            raise RuntimeError('Reference phase reported an explicit STOP/BLOCKED/FAIL')
        if references_ready():
            break
        if repairs>=2:
            raise RuntimeError('Reference phase did not pass after two recovery turns; preserve its accepted IDs and diagnose')
        repairs+=1
        if recover:
            recover('references','Reference validation is incomplete. Diagnose it, use permitted tools and resume existing jobs; do not blindly resubmit.')
    repairs=0
    while True:
        before=get_snapshot()
        if not consistent() and repairs==0:
            raise RuntimeError('Ledger consistency failed; reconcile before further work')
        if before['status']=='COMPLETE':
            return
        if before['status'] in {'BLOCKED','FAIL'}:
            raise RuntimeError('Trial reported '+before['status'])
        result=run_phase('coding') or {}
        after=get_snapshot()
        if result.get('hard_stop'):
            raise RuntimeError('Coding client reported an explicit tool/transport STOP')
        if after['status'] in {'BLOCKED','FAIL'}:
            raise RuntimeError('Trial reported '+after['status'])
        if after['status']=='COMPLETE' and consistent():
            return
        if not consistent() or not after['passed'] > before['passed']:
            if repairs>=2:
                raise RuntimeError('Coding returned without a verified stage advance after two recovery turns; stop instead of looping')
            repairs+=1
            if recover:
                recover('coding','No verified stage advance yet. Inspect diagnostics/checkpoints and repair the concrete issue; preserve accepted jobs and all failure limits.')
        else:
            repairs=0
        # A model that returns after a successful stage is continued in the SAME
        # coding session automatically. Genuine failures and no-progress stop.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detach',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--status',action='store_true')
    parser.add_argument('--continuation',action='store_true',help='Use the explicit reconciled continuation handoff; requires --resume')
    parser.add_argument('--check-continuation',action='store_true',help='Verify the handoff without starting any session')
    args=parser.parse_args()
    runtime=ROOT/'.runtime/autonomous-run'
    path=runtime/'state.json'
    if args.check_continuation:
        from scripts.continuation_preflight import validate
        print(json.dumps(validate(ROOT),indent=2))
        return
    if args.continuation and not args.resume:
        parser.error('--continuation requires --resume')
    if args.status:
        state=json.loads(path.read_text()) if path.exists() else {'state':'not_started'}
        print(json.dumps(live_status(ROOT,state),indent=2))
        return
    if path.exists() and args.resume and not args.continuation and json.loads(path.read_text()).get('state')=='ready_to_continue':
        raise RuntimeError('This reconciled run requires --resume --continuation to load its authorized diagnostic handoff.')
    runtime.mkdir(parents=True,exist_ok=True)
    if args.detach:
        if path.exists() and not args.resume:
            raise RuntimeError('Run state exists. Inspect --status before an explicit --resume.')
        with (runtime/'controller.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.continuation:
            from scripts.continuation_preflight import validate
            validate(ROOT)
        command=[sys.executable,str(Path(__file__).resolve())]+(['--resume'] if args.resume else [])+(['--continuation'] if args.continuation else [])
        with (runtime/'controller.log').open('ab') as log:
            process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print(json.dumps({'controller_pid':process.pid,'state_file':str(path),'log':str(runtime/'controller.log'),
                          'next':'Use --status; do not launch a second controller.'}))
        return
    with (runtime/'controller.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if path.exists() and not args.resume:
            raise RuntimeError('Run state exists. Inspect --status; use --resume explicitly after reconciliation.')
        state=json.loads(path.read_text()) if path.exists() else {'sessions':{},'turns':0}
        if args.continuation:
            from scripts.continuation_preflight import validate
            plan=validate(ROOT)
            state['operator_continuation']=plan
            if plan.get('fresh_coding_session') and 'coding' in state['sessions']:
                state.setdefault('session_history',[]).append({'phase':'coding','session':state['sessions'].pop('coding'),
                    'reason':'Operator-corrected pin geometry and authorized counter reset; avoid stale failed-session assumptions'})
            state['recovery_context']=(
                f"The operator explicitly authorized this reconciled continuation with failure limits {plan['limits']['per_source']}/source and {plan['limits']['total']}/total. "
                'All prior failures remain. Read CONTROLLED_CONTINUATION.md and '+plan['diagnostic_report']+' before any submission. '
                'Use completed source '+plan['source_job']+' and the verified canonical checkpoint. '
                'Authorized measured repair scope: '+plan['scope']+' '
                'Use python3 scripts/checkpoint_bowling.py --source COMPLETED_ID to publish each native checkpoint, '
                'then python3 scripts/validate_checkpoint.py --campaign UNIQUE_ID and python3 scripts/checkpoint_bowling.py --sync-ledgers. '
                'Do not rely on the stale previous stage table or blind text substitutions. '
                'Do not restart empty, regenerate references, use failed jobs as sources, or replay unchanged failed code. '
                'This handoff supersedes the previous exhausted trial budget only; current guard limits and uncertainty checks still apply.')
        state.update(state='running',controller_pid=os.getpid())
        def save():
            temporary=path.with_suffix('.next')
            temporary.write_text(json.dumps(state,indent=2)+'\n')
            temporary.replace(path)
        save()
        def stopped(signum,frame):
            raise KeyboardInterrupt('Explicit controller stop')
        signal.signal(signal.SIGTERM,stopped)
        def run_phase(phase):
            command_name='bowling-references' if phase=='references' else 'bowling-start'
            model=MODEL
            command=['opencode','run','--format','json','--command',command_name,'--model',model]
            if phase in state['sessions']:
                command+=['--session',state['sessions'][phase]]
            if state.get('recovery_context'):
                command.append(state.pop('recovery_context'))
            if state.get('last_errors'):
                state.setdefault('previous_turn_errors',[]).append({'phase':state.get('phase'),'turn':state['turns'],'errors':state['last_errors']})
            state.update(phase=phase,model=model,turns=state['turns']+1,last_errors=[])
            state.pop('reason',None)
            save()
            events=runtime/f"{state['turns']:03d}-{phase}.jsonl"
            state['events_file']=str(events.relative_to(ROOT))
            with events.open('x') as log:
                process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=None,
                                         text=True,start_new_session=True)
                state['client_pid']=process.pid
                save()
                hard_stop=False
                errors=[]
                try:
                    assert process.stdout is not None
                    for line in process.stdout:
                        log.write(line)
                        log.flush()
                        try:event=json.loads(line)
                        except ValueError:continue
                        if event.get('type')=='error':
                            hard_stop=True
                            errors.append(str(event.get('error','Client error'))[:1500])
                        if event.get('type')=='tool_use' and event.get('part',{}).get('state',{}).get('status')=='error':
                            error=str(event['part']['state'].get('error',''))
                            errors.append(error[:1500])
                            state['last_errors']=errors[-4:]
                            save()
                            if any(marker in error.lower() for marker in ['stop:', 'circuit-breaker', 'failure budget exhausted','doom_loop']):
                                hard_stop=True
                        if event.get('sessionID'):
                            state['sessions'][phase]=event['sessionID']
                            save()
                        if event.get('type')=='text':
                            print(event.get('part',{}).get('text',''),flush=True)
                    code=process.wait()
                    if code:
                        raise RuntimeError(f'{phase} client exited {code}; no automatic replay')
                    state['last_errors']=errors[-4:]
                    return {'hard_stop':hard_stop,'errors':errors[-4:]}
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid,signal.SIGTERM)
                        try:process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid,signal.SIGKILL)
                            process.wait()
                    state.pop('client_pid',None)
                    save()
        def recover(phase,reason):
            checks=reference_check(ROOT) if phase=='references' else resume_check(ROOT)
            state.setdefault('recoveries',[]).append({'phase':phase,'reason':reason,'issues':checks['issues'],'errors':state.get('last_errors',[])})
            state['recovery_context']=(reason+'\nValidation: '+json.dumps(checks['issues'])+
                '\nRecent tool errors: '+json.dumps(state.get('last_errors',[]))+
                '\nThis is a bounded repair turn, not a new trial. For filesystem discovery use Read/Glob/Grep. '
                'Do not repeat a denied command; use permitted tools. Never bypass a STOP, release leases, or replay an uncertain submission.')
            save()
        try:
            workflow(run_phase,snapshot,lambda:reference_check(ROOT)['passed'],lambda:resume_check(ROOT)['passed'],recover)
            state.update(state='completed',finished=time.time())
        except BaseException as error:
            state.update(state='interrupted' if isinstance(error,KeyboardInterrupt) else 'blocked',reason=str(error))
            save()
            raise
        save()
        print(json.dumps({'state':'completed','sessions':state['sessions'],'checkpoint':str(ROOT/'BUILD_STATUS.md')}))


if __name__=='__main__':
    main()
