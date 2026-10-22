from pathlib import Path
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
        path = self.root / 'artifacts/blend/Kart01.blend'
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
        path = self.root / 'artifacts/blend/Kart01.blend'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fixture only')
        self.assertTrue(check(self.root)['passed'])

    def test_pass_without_evidence_and_incomplete_complete_are_rejected(self):
        self.write_state('COMPLETE', 'PASS', self.job, self.job)
        result = check(self.root)
        self.assertFalse(result['passed'])
        self.assertTrue(any('objective evidence' in issue for issue in result['issues']))
        self.assertTrue(any('all ten' in issue for issue in result['issues']))


if __name__ == '__main__':
    unittest.main()
