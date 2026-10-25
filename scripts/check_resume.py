"""Read-only consistency check for the simplified branch."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def errors(root=ROOT):
    s=json.loads((root/'RUN_STATE.json').read_text()); out=[]
    if s.get('phase') not in ('BUILD','REVIEW','DELIVER'): out.append('Invalid phase')
    if s.get('status') not in ('NOT_STARTED','RUNNING','FAIL','BLOCKED','COMPLETE'): out.append('Invalid status')
    jobs=s.get('jobs',[])
    ids=[j.get('id') for j in jobs]
    if len(ids)!=len(set(ids)) or any(not i for i in ids): out.append('Missing/duplicate job IDs')
    for key in ('pending_job','verified_source'):
        if s.get(key) and s[key] not in ids: out.append(key+' absent from jobs')
    cp=s.get('checkpoint')
    if cp:
        path=root/cp['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=cp.get('sha256'): out.append('Checkpoint missing/hash mismatch')
    if s.get('verified_source') and not cp: out.append('Verified source requires checkpoint')
    if s.get('status')=='NOT_STARTED':
        for folder in ('blend','exports','renders','downloads','reports','scripts'):
            allowed={'.gitkeep','check_z6_models.py'}
            if any(f.is_file() and f.name not in allowed for f in (root/'artifacts'/folder).rglob('*')): out.append('Fresh state has active outputs: '+folder)
        if jobs or cp or s.get('pending_job') or s.get('verified_source'): out.append('Fresh state has recorded work')
    if s.get('status')=='COMPLETE':
        if s.get('pending_job') or not cp or s.get('phase')!='DELIVER': out.append('Incomplete completion metadata')
        for key in ('numeric','visual','round_trip','delivery'):
            if not s.get('evidence',{}).get(key,{}).get('passed'): out.append('Missing completion evidence: '+key)
    return out
if __name__=='__main__':
    issues=errors()
    print('\n'.join(issues) if issues else 'Resume consistency PASS (not asset acceptance)')
    raise SystemExit(bool(issues))
