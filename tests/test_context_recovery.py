import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch

from scripts.context_recovery import is_context_overflow,context_exit_recoverable,reference_receipt
from scripts.submission_guard import GuardBlocked
from scripts import run_bowling


CONTEXT={'type':'error','sessionID':'old-session','error':{'name':'ContextOverflowError','data':{
    'message':'request (145862 tokens) exceeds the available context size (139264 tokens)'}}}


class ContextRecoveryTests(unittest.TestCase):
    def test_reference_rotation_requires_all_generation_acknowledgements_in_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);runtime=root/'.runtime/autonomous-run';runtime.mkdir(parents=True)
            events=runtime/'001-references.jsonl'
            (runtime/'state.json').write_text(json.dumps({'events_file':str(events.relative_to(root))}))
            event={'part':{'tool':'imageMCP_generate_image','state':{'status':'completed','output':json.dumps({'job_id':'edimg-known'})}}}
            events.write_text(json.dumps(event)+'\n')
            with self.assertRaisesRegex(GuardBlocked,'not recorded in manifest'):reference_receipt(root)
            refs=root/'artifacts/references';refs.mkdir(parents=True)
            (refs/'manifest.json').write_text(json.dumps({'images':[{'job_id':'edimg-known','state':'running'}]}))
            self.assertEqual(reference_receipt(root)['reference_job_ids'],['edimg-known'])
            event['part']['state']['status']='error';events.write_text(json.dumps(event)+'\n')
            with self.assertRaisesRegex(GuardBlocked,'outcome uncertain'):reference_receipt(root)
    def test_only_confirmed_context_failures_allow_recovery(self):
        self.assertTrue(is_context_overflow(CONTEXT))
        self.assertFalse(is_context_overflow({'type':'error','error':{'name':'APIError'}}))
        self.assertTrue(context_exit_recoverable(1,1,False,False))
        for args in [(1,0,False,False),(1,1,True,False),(1,1,False,True),(137,1,False,False),(-15,1,False,False)]:
            self.assertFalse(context_exit_recoverable(*args))

    def setup_root(self,folder):
        root=Path(folder)
        (root/'opencode.json').write_text(json.dumps({'mcp':{'bowling-blender52':{'command':['verified-python']}}}))
        return root

    def process(self,events,code):
        process=Mock(pid=12345)
        process.stdout=iter(json.dumps(event)+'\n' for event in events)
        process.wait.return_value=code;process.poll.return_value=code
        return process

    def test_context_exit_reconciles_and_rotates_session_before_continuing(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.setup_root(folder)
            first=self.process([CONTEXT],1)
            second=self.process([{'type':'text','sessionID':'new-session','part':{'text':'continued'}}],0)
            receipt={'passed':True,'source':'a'*32,'hard_streak':{},'pending_jobs':[]}
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen',side_effect=[first,second]) as spawn,patch.object(run_bowling.subprocess,'run',return_value=Mock(stdout=json.dumps(receipt))) as reconcile:
                run_bowling.main()
            self.assertEqual(spawn.call_count,2);reconcile.assert_called_once()
            self.assertNotIn('--session',spawn.call_args_list[1].args[0])
            self.assertIn('fresh context',spawn.call_args_list[1].args[0][-1])
            state=json.loads((root/'.runtime/autonomous-run/state.json').read_text())
            self.assertEqual(state['sessions']['coding'],'new-session')
            self.assertEqual(state['context_recoveries'][0]['previous_session'],'old-session')
            self.assertEqual(state['native_failures_since_progress'],{})

    def test_context_plus_other_client_error_is_not_retried(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.setup_root(folder)
            process=self.process([CONTEXT,{'type':'error','error':{'name':'APIError','message':'transport failure'}}],1)
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen',return_value=process) as spawn,patch.object(run_bowling.subprocess,'run') as reconcile:
                with self.assertRaisesRegex(RuntimeError,'no automatic replay'):run_bowling.main()
            spawn.assert_called_once();reconcile.assert_not_called()

    def test_context_plus_tool_transport_error_is_not_retried(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.setup_root(folder)
            error={'type':'tool_use','part':{'tool':'bowling-blender52_blender_scene_author','state':{'status':'error','error':'SSH bridge failed: connection interrupted'}}}
            process=self.process([CONTEXT,error],1)
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen',return_value=process) as spawn,patch.object(run_bowling.subprocess,'run') as reconcile:
                with self.assertRaisesRegex(RuntimeError,'no automatic replay'):run_bowling.main()
            spawn.assert_called_once();reconcile.assert_not_called()

    def test_failed_reconciliation_never_starts_a_second_client(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.setup_root(folder)
            process=self.process([CONTEXT],1)
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen',return_value=process) as spawn,patch.object(run_bowling.subprocess,'run',return_value=Mock(stdout='{"passed":false}')):
                with self.assertRaisesRegex(RuntimeError,'reconciliation did not verify'):run_bowling.main()
            spawn.assert_called_once()

    def test_repeated_overflow_without_new_checkpoint_is_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.setup_root(folder);path=root/'.runtime/autonomous-run/state.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'sessions':{},'turns':0,'state':'interrupted','consecutive_context_recoveries':3,'context_recovery_checkpoint':'a'*32}))
            receipt={'passed':True,'source':'a'*32,'hard_streak':{},'pending_jobs':[]}
            with patch.object(run_bowling,'ROOT',root),patch('sys.argv',['run_bowling.py','--resume']),patch.object(run_bowling,'workflow',lambda run,*args:run('coding')),patch.object(run_bowling.subprocess,'Popen',return_value=self.process([CONTEXT],1)) as spawn,patch.object(run_bowling.subprocess,'run',return_value=Mock(stdout=json.dumps(receipt))):
                with self.assertRaisesRegex(RuntimeError,'repeated context failures'):run_bowling.main()
            spawn.assert_called_once()
