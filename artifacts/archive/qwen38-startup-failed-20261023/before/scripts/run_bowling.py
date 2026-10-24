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


def snapshot():
    text=(ROOT/'BUILD_STATUS.md').read_text()
    metadata=fields(text)
    return {'status':metadata.get('Status'),
            'passed':set(re.findall(r'^\| (0[0-9]) \| [^|]+ \| PASS \|',text,re.MULTILINE))}


def workflow(run_phase, get_snapshot, references_ready, consistent):
    """Only advance after validated evidence; never retry a blocked/no-progress run."""
    initial=get_snapshot()
    if initial['status'] in {'BLOCKED','FAIL'}:
        raise RuntimeError('Existing trial is blocked/failed; operator reconciliation required')
    if initial['status']=='COMPLETE':
        if references_ready() and consistent():
            return
        raise RuntimeError('COMPLETE conflicts with reference or checkpoint evidence')
    if not references_ready():
        run_phase('references')
        if not references_ready():
            raise RuntimeError('Reference phase did not pass; preserve its accepted IDs and diagnose')
    while True:
        before=get_snapshot()
        if not consistent():
            raise RuntimeError('Ledger consistency failed; reconcile before further work')
        if before['status']=='COMPLETE':
            return
        if before['status'] in {'BLOCKED','FAIL'}:
            raise RuntimeError('Trial reported '+before['status'])
        run_phase('coding')
        after=get_snapshot()
        if after['status'] in {'BLOCKED','FAIL'}:
            raise RuntimeError('Trial reported '+after['status'])
        if after['status']=='COMPLETE' and consistent():
            return
        if not consistent() or not after['passed'] > before['passed']:
            raise RuntimeError('Coding returned without a verified stage advance; checkpoint and diagnose instead of looping')
        # A model that returns after a successful stage is continued in the SAME
        # coding session automatically. Genuine failures and no-progress stop.


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detach',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--status',action='store_true')
    args=parser.parse_args()
    runtime=ROOT/'.runtime/autonomous-run'
    path=runtime/'state.json'
    if args.status:
        print(path.read_text() if path.exists() else json.dumps({'state':'not_started'}))
        return
    runtime.mkdir(parents=True,exist_ok=True)
    if args.detach:
        if path.exists() and not args.resume:
            raise RuntimeError('Run state exists. Inspect --status before an explicit --resume.')
        with (runtime/'controller.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        command=[sys.executable,str(Path(__file__).resolve())]+(['--resume'] if args.resume else [])
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
            model='z6-llama/qwen38-27b' if phase=='references' else 'z6-llama/qwen36-35b-a3b-mtp-q8'
            command=['opencode','run','--format','json','--command',command_name,'--model',model]
            if phase in state['sessions']:
                command+=['--session',state['sessions'][phase]]
            state.update(phase=phase,model=model,turns=state['turns']+1)
            save()
            events=runtime/f"{state['turns']:03d}-{phase}.jsonl"
            with events.open('x') as log:
                process=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=None,
                                         text=True,start_new_session=True)
                state['client_pid']=process.pid
                save()
                try:
                    assert process.stdout is not None
                    for line in process.stdout:
                        log.write(line)
                        log.flush()
                        try:event=json.loads(line)
                        except ValueError:continue
                        if event.get('sessionID'):
                            state['sessions'][phase]=event['sessionID']
                            save()
                        if event.get('type')=='text':
                            print(event.get('part',{}).get('text',''),flush=True)
                    code=process.wait()
                    if code:
                        raise RuntimeError(f'{phase} client exited {code}; no automatic replay')
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid,signal.SIGTERM)
                        try:process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid,signal.SIGKILL)
                            process.wait()
                    state.pop('client_pid',None)
                    save()
        try:
            workflow(run_phase,snapshot,lambda:reference_check(ROOT)['passed'],lambda:resume_check(ROOT)['passed'])
            state.update(state='completed',finished=time.time())
        except BaseException as error:
            state.update(state='interrupted' if isinstance(error,KeyboardInterrupt) else 'blocked',reason=str(error))
            save()
            raise
        save()
        print(json.dumps({'state':'completed','sessions':state['sessions'],'checkpoint':str(ROOT/'BUILD_STATUS.md')}))


if __name__=='__main__':
    main()
