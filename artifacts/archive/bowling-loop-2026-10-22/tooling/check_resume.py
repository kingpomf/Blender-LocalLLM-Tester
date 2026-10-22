"""Read-only handoff consistency check; never infers stage PASS from artifact names."""
import argparse
import json
from pathlib import Path
import re

JOB = re.compile(r'\b(?:gpu-)?[a-f0-9]{32}\b')


def fields(text):
    return dict(re.findall(r'^- ([^:\n]+):\s*(.*)$', text, re.MULTILINE))


def check(root):
    root = Path(root)
    status_path = root / 'BUILD_STATUS.md'
    handoff_path = root / 'HANDOFF.md'
    issues = []
    if not status_path.is_file() or not handoff_path.is_file():
        return {'passed': False, 'issues': ['BUILD_STATUS.md and HANDOFF.md are required; reconstruct existing progress before submitting work.']}
    text = status_path.read_text()
    status = fields(text)
    handoff = fields(handoff_path.read_text())
    stages = re.findall(r'^\| (0[0-9]) \| ([^|]+) \| ([A-Z_]+) \|([^|]*)\|$', text, re.MULTILINE)
    if [s[0] for s in stages] != [f'{n:02d}' for n in range(10)]:
        issues.append('Stage ledger must contain exactly ordered stages 00–09.')
    passed = [s for s in stages if s[2] == 'PASS']
    for number, _, state, evidence in stages:
        if state not in {'PASS', 'FAIL', 'BLOCKED', 'IN_PROGRESS', 'NOT_STARTED'}:
            issues.append(f'Stage {number} has an unknown result: {state}.')
        if state in {'PASS', 'FAIL', 'BLOCKED'} and not evidence.strip():
            issues.append(f'Stage {number} needs objective evidence for {state}.')
    source = status.get('Active source job', '').strip('`')
    accepted = status.get('Accepted job IDs', '')
    run_status = status.get('Status', '')
    if run_status not in {'NOT_STARTED', 'IN_PROGRESS', 'FAIL', 'BLOCKED', 'COMPLETE'}:
        issues.append('Status must be NOT_STARTED, IN_PROGRESS, FAIL, BLOCKED, or COMPLETE.')
    active_files = []
    for folder in ('blend', 'exports', 'renders', 'downloads', 'reports', 'scripts'):
        for path in (root / 'artifacts' / folder).rglob('*'):
            if path.is_file() and path.name != '.gitkeep' and not (folder == 'scripts' and path.name == 'check_z6_models.py'):
                active_files.append(str(path.relative_to(root)))
    if run_status == 'NOT_STARTED':
        if any(s[2] != 'NOT_STARTED' for s in stages) or source != 'none' or JOB.search(accepted):
            issues.append('NOT_STARTED contradicts stage results or recorded job/source identities.')
        if active_files:
            issues.append('NOT_STARTED contradicts existing active artifacts/scripts. Reconcile progress; do not start over or delete them.')
    if passed:
        if not JOB.fullmatch(source) or source.startswith('gpu-'):
            issues.append('Passed stages require a last verified same-host CPU source job ID.')
        if not JOB.search(accepted):
            issues.append('Passed stages require accepted job IDs in the metadata summary.')
        if not (root / 'artifacts/blend/BowlingPair01.blend').is_file():
            issues.append('Passed stages require the saved local BowlingPair01.blend checkpoint.')
    incomplete = next((s[0] for s in stages if s[2] != 'PASS'), None)
    if incomplete and not status.get('Next stage', '').startswith(incomplete + ' '):
        issues.append('Next stage must identify the first non-PASS stage.')
    if run_status == 'COMPLETE' and (len(passed) != 10):
        issues.append('COMPLETE requires all ten stages PASS.')
    if handoff.get('Run status') != run_status:
        issues.append('HANDOFF.md Run status differs from BUILD_STATUS.md.')
    if handoff.get('Last verified source job', '').strip('`') != source:
        issues.append('HANDOFF.md source differs from the active source in BUILD_STATUS.md.')
    pending = handoff.get('Pending job', '').strip('`')
    if pending != 'none' and (not JOB.fullmatch(pending) or pending not in text):
        issues.append('Pending job must be none or an accepted job ID recorded in BUILD_STATUS.md.')
    candidates = sorted({p.parent.name for p in (root / 'artifacts/downloads').glob('*/scene.json') if JOB.fullmatch(p.parent.name)})
    return {'passed': not issues, 'run_status': run_status, 'next_stage': incomplete,
            'last_verified_source': source, 'pending_job': pending, 'issues': issues,
            'active_file_count': len(active_files), 'candidate_jobs_to_inspect': candidates[:20],
            'note': 'Consistency only: inspect actual scenes/reports/hashes before accepting or resuming work.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    result = check(parser.parse_args().root)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
