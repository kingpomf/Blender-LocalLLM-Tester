"""Compact read-only failure report for the coding agent; no shell pipelines needed."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'artifacts/reports/validation.json').read_text())
print(json.dumps({'asset_source_job':report['asset_source_job'],'stage_results':report['stage_results'],
    'passed':report['passed'],'fail_count':report['fail_count'],'unresolved_count':report['unresolved_count'],
    'remaining_checks':[{'id':c['id'],'status':c['status'],'expected':c['expected'],
                         'observed':str(c['observed'])[:500]} for c in report['checks'] if c['status']!='PASS']},indent=2))
