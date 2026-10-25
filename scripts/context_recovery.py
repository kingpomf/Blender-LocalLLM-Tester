"""Checkpoint-based context rotation; no model call, replay, counter reset or asset code."""
import asyncio
import json
from pathlib import Path
import time

from scripts.check_references import check as reference_check
from scripts.check_resume import check as resume_check
from scripts.submission_guard import budget_accounting,GuardBlocked,FAILURE_LIMIT_PER_SOURCE,FAILURE_LIMIT_TOTAL

MAX_CONTEXT_RECOVERIES=3


def is_context_overflow(event):
    error=event.get('error',{})
    return event.get('type')=='error' and isinstance(error,dict) and error.get('name')=='ContextOverflowError'


def context_exit_recoverable(code,overflows,fatal_error,hard_stop):
    return code in {0,1} and bool(overflows) and not fatal_error and not hard_stop


def recovery_prompt(receipt,phase):
    return ('Automatic recovery from a confirmed context overflow, not an asset failure. '
        'This is a fresh context for the SAME trial; previous sessions/accepted IDs are archived. '
        'Read AGENTS.md and CONTROLLED_CONTINUATION.md, then call blender_workflow_status. '
        'Trust measured tool state, never prior prose/compaction PASS claims. '
        'Verified asset source: '+str(receipt.get('source') or 'none')+'. '
        'Use blender_scene_summary with a few exact names and blender_validation_details for a selected stage/check. '
        'Do not fetch/read an entire scene.json or full validation report; these compact tools avoid another overflow. '
        'No reset, empty rebuild, uncertain replay or duplicate submission is authorized. '
        +('References are verified READY; do not regenerate them. Repair the FIRST failing stage, including hierarchy/parenting, '
          'with one small validated edit before repeatedly rebuilding pins. Poll accepted jobs and their validation IDs. '
          if phase=='coding' else 'Continue reference work from the saved accepted image IDs; do not regenerate completed references. '))


def reference_receipt(root):
    root=Path(root)
    manifest=root/'artifacts/references/manifest.json'
    images=json.loads(manifest.read_text()).get('images',[]) if manifest.exists() else []
    known={image.get('job_id') for image in images if image.get('job_id')}
    if any(image.get('state') not in {'completed','failed','cancelled'} and not image.get('job_id') for image in images):
        raise GuardBlocked('STOP: uncertain reference request prevents automatic context recovery')
    state=json.loads((root/'.runtime/autonomous-run/state.json').read_text())
    events=(root/state['events_file']).resolve()
    if not events.is_relative_to((root/'.runtime/autonomous-run').resolve()):raise GuardBlocked('STOP: unexpected reference event path')
    for line in events.read_text().splitlines():
        try:event=json.loads(line)
        except ValueError:continue
        part=event.get('part',{});tool=part.get('tool','');saved=part.get('state',{})
        if tool!='imageMCP_generate_image':continue
        if saved.get('status')!='completed':raise GuardBlocked('STOP: reference generation outcome uncertain; preserve its request, no replay')
        try:result=json.loads(saved.get('output',''))
        except ValueError:raise GuardBlocked('STOP: reference generation acknowledgement cannot be verified') from None
        job=result.get('job_id') if isinstance(result,dict) else None
        if not job or job not in known:raise GuardBlocked('STOP: accepted reference ID is not recorded in manifest; reconcile before retry')
    return {'passed':True,'source':None,'checkpoint_sha256':None,'pending_jobs':[],
            'hard_streak':{},'reference_job_ids':sorted(known),'phase':'references'}


async def reconcile(root,workflow,guard,timeout:float=240.0,poll_interval:float=2.0,phase='coding'):
    root=Path(root);deadline=time.monotonic()+timeout;observed=[]
    while True:
        status=await workflow.call('workflow_status')
        if status.get('code')=='workflow_busy':
            if time.monotonic()>=deadline:raise GuardBlocked('STOP: context reconciliation could not acquire workflow state')
            await asyncio.sleep(poll_interval);continue
        pending=status.get('pending_jobs',[])
        if not pending:
            source=status.get('current_source');validation=status.get('validation')
            if source and (not validation or validation['source_job']!=source):
                result=await workflow.call('validate')
                if result.get('recoverable'):raise GuardBlocked('STOP: fixed validation unavailable during context reconciliation')
                if time.monotonic()>=deadline:raise GuardBlocked('STOP: context recovery validation incomplete')
                await asyncio.sleep(poll_interval);continue
            break
        if time.monotonic()>=deadline:raise GuardBlocked('STOP: accepted work still pending; context recovery will not replay it')
        for job in dict.fromkeys(pending):
            result=await workflow.call('status',job_id=job)
            observed.append({'id':job,'state':result.get('state'),'code':result.get('code')})
        await asyncio.sleep(poll_interval)
    rows=guard.rows()
    if any(not row['job'] or row['state'] not in {'completed','failed','cancelled'} for row in rows):
        raise GuardBlocked('STOP: uncertain or pending native work prevents context recovery')
    if phase=='references':
        if rows:raise GuardBlocked('STOP: native build history conflicts with reference-only recovery')
        return reference_receipt(root)
    source=status.get('current_source')
    for check in [reference_check,resume_check]:
        result=check(root)
        if not result['passed']:raise GuardBlocked('STOP: context checkpoint consistency failed: '+str(result['issues'])[:600])
    accounting=budget_accounting(guard.path,rows)
    hard=accounting['counted_failures']
    if len(hard)>=FAILURE_LIMIT_TOTAL or sum(r['source']==source for r in hard)>=FAILURE_LIMIT_PER_SOURCE:
        raise GuardBlocked('STOP: hard failure budget exhausted; context recovery cannot bypass it')
    source_index=next((i for i,row in enumerate(rows) if row['job']==source),-1)
    after_source={r['job'] for r in rows[source_index+1:]}
    streak={r['job']:'Hard failure observed during context reconciliation' for r in hard if r['job'] in after_source}
    if len(streak)>=2:raise GuardBlocked('STOP: two hard failures without asset advance; context recovery cannot bypass the circuit breaker')
    checkpoint=json.loads((root/'artifacts/reports/checkpoint.json').read_text()) if source else {}
    return {'passed':True,'source':source,'checkpoint_sha256':checkpoint.get('sha256'),'hard_streak':streak,
        'hard_failures':len(hard),'api_corrections':len(accounting['api_corrections']),
        'epoch':accounting['reset_id'],'pending_jobs':[],'observed_jobs':observed[-20:]}
