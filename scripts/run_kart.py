"""Detached single-agent launch; RUN_STATE.json alone owns asset progress."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from trial_settings import MODEL

ROOT=Path(__file__).resolve().parents[1]


def save(path,data):
    temporary=path.with_suffix('.next');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--detach',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--status',action='store_true');args=parser.parse_args()
    directory=ROOT/'.runtime';path=directory/'kart-client.json'
    if args.status:
        print(json.dumps({'process':json.loads(path.read_text()) if path.exists() else {'state':'not_started'},
            'asset':json.loads((ROOT/'RUN_STATE.json').read_text())},indent=2));return
    directory.mkdir(exist_ok=True)
    if path.exists() and not args.resume:raise RuntimeError('Run state exists; inspect before any explicit resume')
    if args.detach:
        with (directory/'kart-client.lock').open('a') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with (directory/'kart-controller.log').open('ab') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve())]+(['--resume'] if args.resume else []),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print(json.dumps({'controller_pid':child.pid,'status':'python3 scripts/run_kart.py --status'}));return
    with (directory/'kart-client.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        subprocess.run(['python3',str(ROOT/'scripts/check_resume.py')],cwd=ROOT,check=True)
        previous=json.loads(path.read_text()) if path.exists() else {}
        record={'state':'running','controller_pid':os.getpid(),'model':MODEL,'started':time.time()}
        command=['opencode','run','--format','json','--command','kart-start','--model',MODEL]
        if args.resume and previous.get('session'):command+=['--session',previous['session']]
        command.append('User authorized a fresh simplified kart run with Qwen3.8 Flash-Next through Strata. Use supplied helpers, rig and unchanged validator; author the actual kart yourself. Follow BUILD -> REVIEW -> DELIVER with RUN_STATE.json as the only asset ledger. Poll accepted IDs to terminal using permitted bounded waits. Diagnose failures once, genuinely correct the code, stop after three unsuccessful repairs of the same issue, and never replay uncertainty. Do not claim unseen pixels or round-trip checks. If real visual review is unavailable record BLOCKED. Preserve protected GPU work and do not install or change models/infrastructure.')
        events=directory/('kart-events.jsonl' if not args.resume else f'kart-events-{time.time_ns()}.jsonl')
        record['events']=str(events.relative_to(ROOT));save(path,record)
        client=None
        def stop(signum,frame):raise KeyboardInterrupt('Explicit operator stop')
        signal.signal(signal.SIGTERM,stop)
        try:
            with events.open('x') as log:
                client=subprocess.Popen(command,cwd=ROOT,stdout=subprocess.PIPE,text=True,start_new_session=True)
                record['client_pid']=client.pid;save(path,record)
                assert client.stdout is not None
                for line in client.stdout:
                    log.write(line);log.flush()
                    try:event=json.loads(line)
                    except ValueError:continue
                    if event.get('sessionID'):record['session']=event['sessionID'];save(path,record)
                    if event.get('type')=='error':record['last_client_error']=event.get('error',{}).get('name','ClientError');save(path,record)
                code=client.wait();record.update(state='client_exited' if code==0 else 'blocked',exit_code=code,finished=time.time())
        except BaseException as error:
            record.update(state='interrupted' if isinstance(error,KeyboardInterrupt) else 'blocked',reason=str(error),finished=time.time());raise
        finally:
            if client and client.poll() is None:
                os.killpg(client.pid,signal.SIGTERM)
                try:client.wait(timeout=10)
                except subprocess.TimeoutExpired:os.killpg(client.pid,signal.SIGKILL);client.wait()
            record.pop('client_pid',None);save(path,record)
        print(json.dumps({'process':record,'asset':json.loads((ROOT/'RUN_STATE.json').read_text())},indent=2))


if __name__=='__main__':main()
