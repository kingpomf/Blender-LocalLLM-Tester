import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import json
from unittest.mock import Mock

from scripts.run_bowling import workflow
from scripts import run_bowling


class ContinuousRunTests(unittest.TestCase):
    @staticmethod
    def native_event(job,state='failed',**extra):
        return {'type':'tool_use','part':{'tool':'bowling-blender52_blender_job_status','state':{
            'status':'completed','output':json.dumps({'id':job,'state':state,'error':'blender_exit_1',**extra})}}}

    def test_native_failures_count_successful_mcp_responses_once_per_job(self):
        failures={};progress={};event=self.native_event('a'*32)
        self.assertIn('failed',run_bowling.native_outcome(event,failures,progress) or '')
        self.assertIsNone(run_bowling.native_outcome(event,failures,progress))
        self.assertEqual(len(failures),1)
        run_bowling.native_outcome(self.native_event('b'*32,'completed',operation='validation'),failures,progress)
        self.assertEqual(len(failures),1)
        success=self.native_event('c'*32,'completed',operation='asset',execution_succeeded=True,checkpoint={'source_job':'c'*32})
        run_bowling.native_outcome(success,failures,progress)
        self.assertEqual(failures,{})
        self.assertIsNone(run_bowling.native_outcome(event,failures,progress))
        run_bowling.native_outcome(self.native_event('d'*32),failures,progress)
        run_bowling.native_outcome(success,failures,progress)
        self.assertEqual(set(failures),{'d'*32})

    def test_view_failure_and_native_diagnostics_count_once(self):
        failures={};progress={}
        run_bowling.native_outcome(self.native_event('view-'+'a'*32,native_job='b'*32),failures,progress)
        self.assertEqual(set(failures),{'b'*32})
        self.assertIsNone(run_bowling.native_outcome(self.native_event('b'*32),failures,progress))
        cancelled_view=self.native_event('view-'+'c'*32,'cancelled',native_job='d'*32,native_state='completed')
        self.assertIsNone(run_bowling.native_outcome(cancelled_view,failures,progress))
        self.assertEqual(set(failures),{'b'*32})

    def test_retained_failure_streak_blocks_client_spawn(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);state=root/'.runtime/autonomous-run/state.json'
            state.parent.mkdir(parents=True)
            state.write_text(json.dumps({'sessions':{},'turns':1,'state':'blocked','native_failures_since_progress':{'a'*32:'failed','b'*32:'failed'}}))
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py','--resume']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError,'retained native failure streak'):
                    run_bowling.main()
                spawn.assert_not_called()

    def test_startup_sync_failure_records_blocked_state_without_spawning(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py','--resume','--continuation']),patch('scripts.continuation_preflight.validate',return_value={'workflow_managed':True,'limits':{'per_source':6,'total':20},'source_job':'a'*32,'diagnostic_report':'test','scope':'test'}),patch('scripts.checkpoint_bowling.sync_ledgers',side_effect=RuntimeError('sync failed')),patch.object(run_bowling.subprocess,'Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError,'sync failed'):
                    run_bowling.main()
                spawn.assert_not_called()
            state=json.loads((root/'.runtime/autonomous-run/state.json').read_text())
            self.assertEqual(state['state'],'blocked')

    def test_two_native_failures_terminate_client_before_another_event(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);process=Mock(pid=12345)
            consumed=[]
            def events():
                for job in ['a'*32,'b'*32,'c'*32]:
                    consumed.append(job)
                    yield json.dumps(self.native_event(job))+'\n'
            process.stdout=events();process.poll.return_value=None
            def run_only_coding(run,*args):return run('coding')
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py']),patch.object(run_bowling,'workflow',run_only_coding),patch.object(run_bowling.subprocess,'Popen',return_value=process),patch.object(run_bowling.os,'killpg') as kill:
                with self.assertRaisesRegex(RuntimeError,'two distinct native jobs'):
                    run_bowling.main()
                kill.assert_called_once_with(12345,run_bowling.signal.SIGTERM)
            self.assertEqual(consumed,['a'*32,'b'*32])
            state=json.loads((root/'.runtime/autonomous-run/state.json').read_text())
            self.assertEqual(state['state'],'blocked')
            self.assertEqual(len(state['last_errors']),2)
            self.assertNotIn('client_pid',state)

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
