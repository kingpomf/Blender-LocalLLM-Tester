from pathlib import Path
import json
import hashlib
import tempfile
import unittest

from scripts.check_resume import check


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = 'a' * 32
        self.write_state()

    def write_state(self, run='NOT_STARTED', first='NOT_STARTED', source='none', accepted='none', evidence=''):
        rows = [f'| {i:02d} | Stage | {first if i == 0 else "NOT_STARTED"} | {evidence if i == 0 else ""} |' for i in range(10)]
        next_stage = '01' if first == 'PASS' else '00'
        (self.root / 'BUILD_STATUS.md').write_text(f'- Status: {run}\n- Next stage: {next_stage} — Stage\n- Active source job: {source}\n- Accepted job IDs: {accepted}\n' + '\n'.join(rows))
        (self.root / 'HANDOFF.md').write_text(f'- Run status: {run}\n- Last verified source job: {source}\n- Pending job: none\n')

    def test_clean_fresh_state(self):
        self.assertTrue(check(self.root)['passed'])

    def test_stale_native_checkpoint_cannot_match_a_new_source_by_markdown_only(self):
        self.write_state('IN_PROGRESS','PASS',self.job,self.job,'fixture stage proof')
        path=self.root/'artifacts/blend/BowlingPair01.blend'
        path.parent.mkdir(parents=True);path.write_bytes(b'old native scene')
        receipt=self.root/'artifacts/reports/checkpoint.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text(json.dumps({'source_job':'b'*32,'path':'artifacts/blend/BowlingPair01.blend',
                                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
        result=check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('receipt source differs' in issue for issue in result['issues']))

    def test_pending_reference_and_conflicting_ledgers_are_reconciled(self):
        for name,phase in [('BUILD_STATUS.md','READY'),('HANDOFF.md','NOT_STARTED')]:
            path=self.root/name
            path.write_text(path.read_text()+f'\n- Reference phase: {phase}\n- Pending reference job: none\n')
        path=self.root/'artifacts/references/manifest.json'
        path.parent.mkdir(parents=True)
        job='edimg-'+'b'*32
        path.write_text(json.dumps({'images':[{'job_id':job,'state':'queued'}]}))
        result=check(self.root)
        self.assertFalse(result['passed'])
        self.assertEqual(result['pending_reference_jobs'],[job])
        self.assertTrue(any('Reference phase differs' in issue for issue in result['issues']))

    def test_uncertain_reference_never_looks_like_fresh_start(self):
        for name in ['BUILD_STATUS.md','HANDOFF.md']:
            path=self.root/name
            path.write_text(path.read_text()+'\n- Reference phase: IN_PROGRESS\n- Pending reference job: uncertain\n')
        path=self.root/'artifacts/references/manifest.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'images':[{'request_id':'saved','state':'uncertain'}]}))
        result=check(self.root)
        self.assertFalse(result['passed'])
        self.assertEqual(result['pending_reference_jobs'],['uncertain'])

    def test_stale_not_started_ledger_with_pass_is_rejected(self):
        self.write_state(first='PASS', evidence='claimed pass')
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('contradicts stage' in issue for issue in result['issues']))

    def test_artifacts_without_ledger_progress_cannot_silently_restart(self):
        path = self.root / 'artifacts/downloads' / self.job / 'scene.json'
        path.parent.mkdir(parents=True)
        path.write_text('{}')
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertEqual(result['candidate_jobs_to_inspect'], [self.job])

    def test_consistent_resume_still_requires_independent_scene_verification(self):
        self.write_state('IN_PROGRESS', 'PASS', self.job, self.job, 'verified scene and report')
        path = self.root / 'artifacts/blend/BowlingPair01.blend'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fixture only')
        result = check(self.root)
        self.assertTrue(result['passed'])
        self.assertEqual(result['last_verified_source'], self.job)

    def test_handoff_mismatch_and_unrecorded_pending_job_are_rejected(self):
        (self.root / 'HANDOFF.md').write_text(f'- Run status: IN_PROGRESS\n- Last verified source job: {self.job}\n- Pending job: {self.job}\n')
        self.assertFalse(check(self.root)['passed'])

    def test_markdown_formatted_source_ids_are_accepted(self):
        self.write_state('IN_PROGRESS', 'PASS', f'`{self.job}`', self.job, 'verified evidence')
        path = self.root / 'artifacts/blend/BowlingPair01.blend'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fixture only')
        self.assertTrue(check(self.root)['passed'])

    def test_pass_without_evidence_and_incomplete_complete_are_rejected(self):
        self.write_state('COMPLETE', 'PASS', self.job, self.job)
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('objective evidence' in issue for issue in result['issues']))
        self.assertTrue(any('all ten' in issue for issue in result['issues']))

    def test_historical_kart_checkpoint_cannot_satisfy_bowling_resume(self):
        self.write_state('IN_PROGRESS', 'PASS', self.job, self.job, 'claimed evidence')
        path = self.root / 'artifacts/blend/Kart01.blend'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'historical fixture only')
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('BowlingPair01.blend' in issue for issue in result['issues']))

    def test_source_annotation_has_actionable_error(self):
        self.write_state(source=self.job + ' (Stage 03 in progress)')
        result = check(self.root)
        self.assertTrue(any('bare 32-character' in issue for issue in result['issues']))

    def test_tool_ledger_rejects_failed_source_claimed_as_pass(self):
        from scripts.submission_guard import SubmissionGuard
        self.write_state('IN_PROGRESS', 'PASS', self.job, self.job, 'claimed evidence')
        checkpoint = self.root / 'artifacts/blend/BowlingPair01.blend'
        checkpoint.parent.mkdir(parents=True)
        checkpoint.write_bytes(b'fixture')
        guard = SubmissionGuard(self.root / '.runtime/blender52/submissions.sqlite')
        with guard.connect() as db:
            db.execute('INSERT INTO attempts VALUES(?,?,?,?,?)', ('hash', 'EMPTY', 'author', self.job, 'failed'))
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('not completed in this trial' in issue for issue in result['issues']))


if __name__ == '__main__':
    unittest.main()
