"""Run with the worker Python environment; no SSH or job submission."""
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from blender52_mcp import BINARY, EXPECTED, ProjectTransport, checked_runtime
from blender_worker.transport import SSHTransport


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    def test_wrong_executable_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'wrong executable'):
            checked_runtime({'version': 'Blender 4.5.14 LTS', 'runners': []})

    def test_wrong_queue_runner_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'another Blender binary'):
            checked_runtime({'version': 'Blender ' + EXPECTED,
                             'runners': [{'binary': '/old/blender'}]})

    def test_matching_runtime_accepted(self):
        checked_runtime({'version': 'Blender ' + EXPECTED, 'runners': [{'binary': BINARY}]})

    async def test_old_completed_source_rejected_before_submit(self):
        client = ProjectTransport('test', '/app', '/root', BINARY, '/tmp/unused')
        with patch.object(client, 'probe', new=AsyncMock(return_value={})), patch.object(
                SSHTransport, 'rpc', new=AsyncMock(return_value={
                    'state': 'completed', 'manifest': {'blender_version': '4.5.14 LTS'}})) as rpc:
            with self.assertRaisesRegex(ValueError, 'source must be completed'):
                await client.rpc('submit', {'operation': 'author', 'source_job': 'a' * 32, 'code': 'x=1'})
            self.assertEqual(rpc.call_count, 1)
            self.assertEqual(rpc.call_args.args[0], 'status')

    async def test_author_has_executing_runtime_assertion(self):
        client = ProjectTransport('test', '/app', '/root', BINARY, '/tmp/unused')
        with patch.object(client, 'probe', new=AsyncMock(return_value={})), patch.object(
                SSHTransport, 'rpc', new=AsyncMock(return_value={'state': 'queued'})) as rpc:
            await client.rpc('submit', {'operation': 'author', 'code': 'report = {}'})
            code = rpc.call_args.args[1]['code']
            self.assertIn('bpy.app.version[:3] == (5,2,3)', code)
            self.assertIn('report = {}', code)


if __name__ == '__main__':
    unittest.main()
