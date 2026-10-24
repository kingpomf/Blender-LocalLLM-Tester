"""Run the fixed read-only validator through the existing guard; merge local render proof."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sys
import importlib.util
import os

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__' and importlib.util.find_spec('mcp') is None:
    python=ROOT.parent/'blender-new-llm-setup/.venv/bin/python'
    os.execv(str(python),[str(python),str(Path(__file__).resolve()),*sys.argv[1:]])
sys.path.insert(0,str(ROOT/'scripts'))
import blender52_mcp as worker
from submission_guard import SubmissionGuard
from check_references import check as check_references, image_dimensions
from check_resume import fields


def local_render_checks(root,source):
    root=Path(root)
    path=root/'artifacts/reports/render-manifest.json'
    results=[]
    def add(key,observed,passed):
        results.append({'id':'S07_local_'+key,'stage':'07','expected':'verified same-asset four distinct1280x720 renders with visual review',
            'observed':observed,'passed':bool(passed),'status':'PASS' if passed else 'FAIL','objects':[],'tolerance':''})
    if not path.exists():
        add('manifest','missing render-manifest.json',False)
        return results
    manifest=json.loads(path.read_text())
    images=manifest.get('images',[])
    add('roles',[i.get('role') for i in images],len(images)==4 and {i.get('role') for i in images}=={'overview','player','pindeck','props'})
    add('source',manifest.get('asset_source'),manifest.get('asset_source')==source)
    add('distinct',len({i.get('sha256') for i in images}),len({i.get('sha256') for i in images})==4)
    for image in images:
        file=(root/image['path']).resolve()
        safe=file.is_relative_to((root/'artifacts/renders').resolve()) and file.is_file()
        actual=hashlib.sha256(file.read_bytes()).hexdigest() if safe else None
        try:
            size=image_dimensions(file) if safe else (0,0)
        except Exception as error:
            add(image['role']+'_decode',str(error),False)
            size=(0,0)
        add(image['role']+'_artifact',{'path':image['path'],'size':list(size),'sha256':actual},safe and actual==image['sha256'] and file.stat().st_size==image['bytes'] and size[0]>=1280 and size[1]>=720)
        review=image.get('visual_review',{})
        add(image['role']+'_visibility',review,review.get('sha256')==actual and review.get('passed') is True and len(review.get('observations',''))>=40)
    return results


def qualitative_evidence(root,source):
    """Resolve only explicitly unresolved criteria using hash-bound review, never geometry FAILs."""
    root=Path(root)
    path=root/'artifacts/reports/qualitative-evidence.json'
    if not path.exists():return {}
    data=json.loads(path.read_text())
    assert data['asset_source']==source, 'Qualitative review belongs to another scene'
    renders=json.loads((root/'artifacts/reports/render-manifest.json').read_text())
    assert renders['asset_source']==source
    verified={i['sha256']:i for i in renders['images']}
    accepted={}
    for criterion in data.get('criteria',[]):
        image=verified.get(criterion.get('render_sha256'))
        assert image is not None and criterion.get('reviewer') and len(criterion.get('observations',''))>=80, 'Review needs actual image hash, identified reviewer and detailed observations'
        file=(root/image['path']).resolve()
        assert file.is_relative_to((root/'artifacts/renders').resolve())
        assert hashlib.sha256(file.read_bytes()).hexdigest()==criterion['render_sha256']
        assert criterion.get('passed') in {True,False}
        accepted[criterion['id']]=criterion
    return accepted


def merge_report(report,local,source,job_id,reviews=None):
    report=dict(report)
    report['checks']=[c for c in report['checks'] if c['id'] not in {'S07_local_renders','S07_actual_render_visibility'}]+local
    for stage in range(8):
        if not any(c.get('stage')==f'{stage:02d}' for c in report['checks']):
            report['checks'].append({'id':f'S{stage:02d}_coverage','stage':f'{stage:02d}',
                'expected':'measured required stage criteria','observed':'no checks supplied',
                'status':'UNRESOLVED','passed':False,'objects':[],'tolerance':''})
    if reviews:
        replaced=[]
        for original in report['checks']:
            criterion=reviews.get(original['id'])
            if criterion and original['status']=='UNRESOLVED':
                original={**original,'status':'PASS' if criterion['passed'] else 'FAIL',
                          'passed':criterion['passed'],'observed':criterion}
            replaced.append(original)
        report['checks']=replaced
    report['asset_source_job']=source
    report['validation_job']=job_id
    report['passed']=all(c['status']=='PASS' for c in report['checks'])
    for status,key in [('PASS','pass_count'),('FAIL','fail_count'),('UNRESOLVED','unresolved_count')]:
        report[key]=sum(c['status']==status for c in report['checks'])
    report['check_count']=len(report['checks'])
    report['stage_results']={f'{i:02d}':('FAIL' if any(c['status']=='FAIL' for c in report['checks'] if c['stage']==f'{i:02d}') else
        'UNRESOLVED' if any(c['status']=='UNRESOLVED' for c in report['checks'] if c['stage']==f'{i:02d}') else 'PASS') for i in range(8)}
    return report


async def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source')
    parser.add_argument('--campaign',default='current')
    args=parser.parse_args()
    assert args.campaign.replace('-','').isalnum()
    source=args.source or fields((ROOT/'BUILD_STATUS.md').read_text()).get('Active source job','').strip('`')
    folder=ROOT/'.runtime/validation'/args.campaign
    folder.mkdir(parents=True,exist_ok=True)
    state_path=folder/'state.json'
    code=(ROOT/'artifacts/scripts/validate_bowling_pair01.py').read_text()
    code_hash=hashlib.sha256(code.encode()).hexdigest()
    assert check_references(ROOT)['passed']
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,
                                   worker.BINARY,str(ROOT/'artifacts/downloads'))
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    if state_path.exists():
        state=json.loads(state_path.read_text())
        assert state.get('id') and state['source']==source and state['code_sha256']==code_hash, 'Existing audit differs or acceptance uncertain; reconcile before any new request'
    else:
        state={'state':'submission_uncertain','source':source,'code_sha256':code_hash}
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        job=await guard.submit({'operation':'author','source_job':source,'code':code},client.rpc)
        state.update(id=job['id'],state=job['state'])
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            with (ROOT/name).open('a') as file:
                file.write(f'\n- Operator validation pending: {job["id"]}; source {source}; read-only measurement\n')
        print(json.dumps({'accepted_validation_job':job['id'],'source':source}),flush=True)
    for _ in range(120):
        job=await client.rpc('status',{'job_id':state['id']})
        row=next(r for r in guard.rows() if r['job']==job['id'])
        guard.update(row['fingerprint'],job)
        state.update(state=job['state'])
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        if job['state'] in {'completed','failed','cancelled'}:break
        await asyncio.sleep(2)
    if job['state']!='completed':
        if job['state'] in {'failed','cancelled'}:
            diagnosis=await client.rpc('diagnostics',{'job_id':job['id']})
            (folder/'diagnostics.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
            print(json.dumps(diagnosis,indent=2))
        raise RuntimeError('Validation job did not complete; no automatic resubmission')
    fetched=await client.fetch(job['id'],'validation.json')
    report=json.loads(Path(fetched['path']).read_text())
    assert report['read_only'] and report['source_fingerprint_before']==report['source_fingerprint_after']
    merged=merge_report(report,local_render_checks(ROOT,source),source,job['id'],qualitative_evidence(ROOT,source))
    destination=ROOT/'artifacts/reports/validation.json'
    if destination.exists():
        previous=folder/('previous-'+hashlib.sha256(destination.read_bytes()).hexdigest()+'.json')
        if not previous.exists():previous.write_bytes(destination.read_bytes())
    destination.write_text(json.dumps(merged,indent=2)+'\n')
    (folder/'merged.json').write_text(json.dumps(merged,indent=2)+'\n')
    print(json.dumps({key:merged[key] for key in ['passed','validation_job','stage_results','pass_count','fail_count','unresolved_count']},indent=2))


if __name__=='__main__':
    asyncio.run(main())
