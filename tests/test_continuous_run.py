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
        self.assertEqual(phases,['references']*3)

    def test_blocked_trial_never_auto_restarts(self):
        phases=[]
        with self.assertRaisesRegex(RuntimeError,'blocked/failed'):
            workflow(phases.append,lambda:{'status':'BLOCKED','passed':set()},lambda:True,lambda:True)
        self.assertEqual(phases,[])

    def test_no_verified_progress_stops_instead_of_prompt_loop(self):
        phases=[]
        with self.assertRaisesRegex(RuntimeError,'without a verified stage advance'):
            workflow(phases.append,lambda:{'status':'IN_PROGRESS','passed':{'00'}},lambda:True,lambda:True)
        self.assertEqual(phases,['coding']*3)

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

    def test_startup_permission_error_gets_diagnostic_recovery(self):
        state={'status':'NOT_STARTED','passed':set()}
        ready=[False]
        calls=[]
        repairs=[]
        def run(phase):
            calls.append(phase)
            if len(calls)==1:
                return {'hard_stop':False,'errors':['permission denied for optional shell listing']}
            if phase=='references':
                ready[0]=True
            else:
                state.update(status='COMPLETE',passed={f'{i:02d}' for i in range(10)})
        workflow(run,lambda:dict(state),lambda:ready[0],lambda:True,lambda *args:repairs.append(args))
        self.assertEqual(calls,['references','references','coding'])
        self.assertEqual(len(repairs),1)

    def test_actual_guard_stop_is_not_retried(self):
        calls=[]
        def run(phase):
            calls.append(phase)
            return {'hard_stop':True,'errors':['STOP: durable failure budget exhausted']}
        with self.assertRaisesRegex(RuntimeError,'explicit'):
            workflow(run,lambda:{'status':'NOT_STARTED','passed':set()},lambda:False,lambda:True)
        self.assertEqual(calls,['references'])

    def test_primary_model_is_qwen36_for_every_command(self):
        import json
        from scripts.trial_settings import MODEL
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(MODEL,'z6-llama/qwen36-35b-a3b-mtp-q8')
        config=json.loads((root/'opencode.json').read_text())
        self.assertEqual(config['model'],MODEL)
        self.assertEqual(config['agent']['build']['model'],MODEL)
        for name in ['bowling-run','bowling-references','bowling-start','bowling-continue']:
            self.assertIn('model: '+MODEL,(root/'.opencode/commands'/f'{name}.md').read_text())

    def test_reconciled_state_requires_explicit_continuation_flag(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            state=root/'.runtime/autonomous-run/state.json'
            state.parent.mkdir(parents=True)
            state.write_text('{"state":"ready_to_continue"}')
            with patch.object(run_bowling,'ROOT',root), patch('sys.argv',['run_bowling.py','--resume','--detach']), patch('scripts.run_bowling.subprocess.Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError,'requires --resume --continuation'):
                    run_bowling.main()
                spawn.assert_not_called()

    def test_status_distinguishes_current_and_historical_failure_counts(self):
        from scripts.submission_guard import SubmissionGuard
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            guard=SubmissionGuard(root/'.runtime/blender52/submissions.sqlite')
            with guard.connect() as db:
                db.execute("INSERT INTO attempts VALUES('old','source','author','job','failed')")
                db.execute("INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(1,'explicit user authorization',1)")
            result=run_bowling.live_status(root,{'state':'running'})
            self.assertEqual(result['live_failure_budget']['current_failures'],0)
            self.assertEqual(result['live_failure_budget']['historical_failures_preserved'],1)
            self.assertEqual(result['live_failure_budget']['total_limit'],20)


if __name__=='__main__':
    unittest.main()
