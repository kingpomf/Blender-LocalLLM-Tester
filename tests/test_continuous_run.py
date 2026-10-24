import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from scripts.run_bowling import workflow
from scripts import run_bowling


class ContinuousRunTests(unittest.TestCase):
    def test_reference_then_coding_and_verified_stage_continuation(self):
        state={'status':'NOT_STARTED','passed':set()}
        references=[False]
        phases=[]
        def run(phase):
            phases.append(phase)
            if phase=='references':
                references[0]=True
            elif not state['passed']:
                state.update(status='IN_PROGRESS',passed={'00'})
            else:
                state.update(status='COMPLETE',passed={f'{i:02d}' for i in range(10)})
        workflow(run,lambda:dict(state),lambda:references[0],lambda:True)
        self.assertEqual(phases,['references','coding','coding'])

    def test_failed_reference_phase_never_launches_coding(self):
        phases=[]
        with self.assertRaisesRegex(RuntimeError,'Reference phase did not pass'):
            workflow(phases.append,lambda:{'status':'NOT_STARTED','passed':set()},lambda:False,lambda:True)
        self.assertEqual(phases,['references'])

    def test_blocked_trial_never_auto_restarts(self):
        phases=[]
        with self.assertRaisesRegex(RuntimeError,'blocked/failed'):
            workflow(phases.append,lambda:{'status':'BLOCKED','passed':set()},lambda:True,lambda:True)
        self.assertEqual(phases,[])

    def test_no_verified_progress_stops_instead_of_prompt_loop(self):
        phases=[]
        with self.assertRaisesRegex(RuntimeError,'without a verified stage advance'):
            workflow(phases.append,lambda:{'status':'IN_PROGRESS','passed':{'00'}},lambda:True,lambda:True)
        self.assertEqual(phases,['coding'])

    def test_existing_complete_does_not_submit_more_work(self):
        phases=[]
        workflow(phases.append,lambda:{'status':'COMPLETE','passed':{'00'}},lambda:True,lambda:True)
        self.assertEqual(phases,[])

    def test_uncertain_client_failure_is_not_retried(self):
        phases=[]
        def fail(phase):
            phases.append(phase)
            raise RuntimeError('Client transport interrupted')
        with self.assertRaisesRegex(RuntimeError,'transport interrupted'):
            workflow(fail,lambda:{'status':'NOT_STARTED','passed':set()},lambda:True,lambda:True)
        self.assertEqual(phases,['coding'])

    def test_detached_duplicate_is_rejected_before_spawning(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            state=root/'.runtime/autonomous-run/state.json'
            state.parent.mkdir(parents=True)
            state.write_text('{"state":"running"}')
            with patch.object(run_bowling,'ROOT',root), patch('sys.argv',['run_bowling.py','--detach']), patch('scripts.run_bowling.subprocess.Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError,'Run state exists'):
                    run_bowling.main()
                spawn.assert_not_called()


if __name__=='__main__':
    unittest.main()
