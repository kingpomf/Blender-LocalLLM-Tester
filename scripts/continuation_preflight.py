"""Read-only validation of the operator-authorized continuation handoff."""
import hashlib
import json
from pathlib import Path
import sqlite3
from contextlib import closing

from scripts.check_resume import check as resume_check
from scripts.check_references import check as reference_check
from scripts.submission_guard import FAILURE_LIMIT_PER_SOURCE, FAILURE_LIMIT_TOTAL
from scripts.trial_settings import MODEL, TRIAL


def guard_rows(root):
    path=Path(root)/'.runtime/blender52/submissions.sqlite'
    with closing(sqlite3.connect(f'file:{path}?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        return [dict(row) for row in db.execute('SELECT fingerprint,source,operation,job,state FROM attempts ORDER BY rowid')]


def rows_hash(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate(root):
    root=Path(root)
    pointer=root/'testing/ACTIVE_CONTINUATION.json'
    selected=json.loads(pointer.read_text())['path'] if pointer.exists() else 'testing/reconciliation-20261024/continuation.json'
    plan_path=(root/selected).resolve()
    assert plan_path.is_relative_to((root/'testing').resolve()), 'Continuation plan escapes testing directory'
    plan=json.loads(plan_path.read_text())
    assert plan['model']==MODEL and plan['trial']==TRIAL, 'Continuation model/trial changed'
    assert plan['limits']=={'per_source':FAILURE_LIMIT_PER_SOURCE,'total':FAILURE_LIMIT_TOTAL}, 'Failure limits differ from authorization'
    rows=guard_rows(root)
    assert rows_hash(rows)==plan['guard_rows_sha256'], 'Guard history changed since reconciliation; inspect before this continuation'
    assert all(row['job'] and row['state'] in {'completed','failed','cancelled'} for row in rows), 'Pending or uncertain work must be reconciled'
    assert any(row['job']==plan['source_job'] and row['state']=='completed' for row in rows)
    checkpoint=root/plan['checkpoint']
    assert checkpoint.is_file() and hashlib.sha256(checkpoint.read_bytes()).hexdigest()==plan['checkpoint_sha256'], 'Canonical checkpoint changed'
    for key,relative in [('validation_sha256','artifacts/reports/validation.json'),
                         ('validator_sha256','artifacts/scripts/validate_bowling_pair01.py')]:
        if key in plan:
            assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==plan[key], 'Authorized validation report/script changed'
    for check in [reference_check,resume_check]:
        result=check(root)
        assert result['passed'], result['issues']
        if check is resume_check:
            assert result['last_verified_source']==plan['source_job'], 'Ledger source differs from authorized repair base'
    failures=[row for row in rows if row['state'] in {'failed','cancelled'}]
    on_source=sum(row['source']==plan['source_job'] for row in failures)
    assert len(failures)<FAILURE_LIMIT_TOTAL and on_source<FAILURE_LIMIT_PER_SOURCE, 'No authorized failure budget remains'
    return {'passed':True,**plan,'failures_retained':len(failures),'source_failures_retained':on_source,
            'remaining_total':FAILURE_LIMIT_TOTAL-len(failures),'remaining_on_source':FAILURE_LIMIT_PER_SOURCE-on_source}
