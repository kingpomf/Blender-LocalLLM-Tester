"""Durable project submission circuit breaker; no Blender or MCP dependency.

This is an accidental-loop guard, not a security boundary against a malicious
agent with shell/file access. Only an operator should reconcile/reset its state.
"""
import ast
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import sqlite3

FAILURE_LIMIT_PER_SOURCE = 6
FAILURE_LIMIT_TOTAL = 20


class GuardBlocked(RuntimeError):
    pass


def fingerprint(request):
    normalized = dict(request)
    if normalized.get('operation') == 'author':
        # Ignore formatting/comments, but retain executable code and constants.
        normalized['code'] = ast.dump(ast.parse(normalized['code']), include_attributes=False)
    return hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()


class SubmissionGuard:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS attempts (fingerprint TEXT PRIMARY KEY, source TEXT NOT NULL, operation TEXT NOT NULL, job TEXT UNIQUE, state TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS failure_budget_resets (id INTEGER PRIMARY KEY AUTOINCREMENT, cutoff_rowid INTEGER NOT NULL, reason TEXT NOT NULL, created REAL NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @contextmanager
    def locked(self):
        with self.path.with_suffix('.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise GuardBlocked('STOP: another submission is being reconciled. Do not submit concurrently.') from None
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def rows(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM attempts ORDER BY rowid')]

    def update(self, key, row):
        with self.connect() as db:
            db.execute('UPDATE attempts SET job=?,state=? WHERE fingerprint=?',
                       (row['id'], row['state'], key))

    def summary(self):
        rows = self.rows()
        accounting=budget_accounting(self.path,rows)
        return {'accepted_jobs': [r for r in rows if r['job']],
                'uncertain_submissions': [r['fingerprint'] for r in rows if not r['job']],
                'failed_count': len(accounting['counted_failures']),
                'historical_failed_count':sum(r['state'] in ('failed','cancelled') for r in rows),
                'failure_budget_reset_id':accounting['reset_id'],
                'failure_limit_per_source': FAILURE_LIMIT_PER_SOURCE, 'failure_limit_total': FAILURE_LIMIT_TOTAL}

    async def submit(self, request, rpc):
        key = fingerprint(request)  # Syntax failures never reach remote worker.
        source = request.get('source_job') or 'EMPTY'
        with self.locked():
            rows = self.rows()
            if any(not r['job'] for r in rows):
                raise GuardBlocked('STOP: submission outcome is uncertain. Operator must reconcile the saved fingerprint/job; no replay is allowed.')
            # Refresh accepted pending jobs, even if the model never polled them.
            for r in rows:
                if r['state'] in ('queued', 'running'):
                    status = await rpc('status', {'job_id': r['job']})
                    self.update(r['fingerprint'], status)
            rows = self.rows()
            previous = next((r for r in rows if r['fingerprint'] == key), None)
            if previous:
                if previous['state'] == 'completed':
                    return await rpc('status', {'job_id': previous['job']})
                raise GuardBlocked(f"STOP: unchanged submission already {previous['state']}; job {previous['job']}. Read diagnostics and make a real code change, or report BLOCKED. No new job was submitted.")
            if any(r['state'] in ('queued', 'running') for r in rows):
                raise GuardBlocked('STOP: an accepted job is still pending. Poll/reconcile it before another submission.')
            failures = budget_accounting(self.path,rows)['counted_failures']
            if sum(r['source'] == source for r in failures) >= FAILURE_LIMIT_PER_SOURCE or len(failures) >= FAILURE_LIMIT_TOTAL:
                raise GuardBlocked(f'STOP: durable failure budget exhausted ({FAILURE_LIMIT_PER_SOURCE} per source / {FAILURE_LIMIT_TOTAL} total). Report BLOCKED and ask the operator. Do not change source, clear state, or retry.')
            if source == 'EMPTY' and any(r['operation'] == 'author' and r['state'] == 'completed' for r in rows):
                raise GuardBlocked('STOP: a completed scene already exists. Supply its verified source_job; do not silently restart.')
            # Commit reservation BEFORE network submission. Transport errors leave
            # an uncertain reservation, intentionally blocking automatic replay.
            with self.connect() as db:
                db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)',
                           (key, source, request['operation'], None, 'uncertain'))
            result = await rpc('submit', request)
            self.update(key, result)
            return result


def budget_accounting(path,rows) -> dict:
    """Read-only accounting epoch; prior failed requests still block identical replay."""
    db=sqlite3.connect(f'file:{Path(path)}?mode=ro',uri=True)
    try:
        exists=db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='failure_budget_resets'").fetchone()
        reset=db.execute('SELECT id,cutoff_rowid FROM failure_budget_resets ORDER BY id DESC LIMIT 1').fetchone() if exists else None
        reset_id,cutoff=reset if reset else (0,0)
        fingerprints={r[0] for r in db.execute('SELECT fingerprint FROM attempts WHERE rowid>?',(cutoff,))}
        return {'reset_id':reset_id,'cutoff_rowid':cutoff,
                'counted_failures':[row for row in rows if row['fingerprint'] in fingerprints and row['state'] in {'failed','cancelled'}]}
    finally:
        db.close()
