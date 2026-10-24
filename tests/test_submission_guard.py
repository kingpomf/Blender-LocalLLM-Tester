import asyncio
from pathlib import Path
import tempfile
import unittest

from scripts.submission_guard import GuardBlocked, SubmissionGuard


class GuardTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'guard.sqlite'
        self.guard = SubmissionGuard(self.path)
        self.jobs = {}
        self.calls = 0

    async def rpc(self, action, request):
        if action == 'status':
            return self.jobs[request['job_id']]
        self.calls += 1
        job = f'{self.calls:032x}'
        row = {'id': job, 'state': 'queued'}
        self.jobs[job] = row
        return row

    def request(self, code='x=1', source='a' * 32):
        return {'operation': 'author', 'source_job': source, 'code': code}

    async def fail(self, code='x=1', source='a' * 32):
        row = await self.guard.submit(self.request(code, source), self.rpc)
        row['state'] = 'failed'  # deliberately skip status polling by the model
        return row

    async def test_same_code_comments_and_formatting_block_across_restart(self):
        first = await self.fail()
        restarted = SubmissionGuard(self.path)
        with self.assertRaisesRegex(GuardBlocked, first['id']):
            await restarted.submit(self.request('# fake repair\nx = 1\n'), self.rpc)
        self.assertEqual(self.calls, 1)

    async def test_real_changed_code_allowed_until_sixth_failure(self):
        for n in range(6):
            await self.fail(f'x={n}')
        with self.assertRaisesRegex(GuardBlocked, 'budget exhausted'):
            await self.guard.submit(self.request('x=99'), self.rpc)
        self.assertEqual(self.calls, 6)

    async def test_total_budget_cannot_be_evaded_with_different_sources(self):
        for n in range(12):
            await self.fail(f'x={n}', f'{n:032x}')
        with self.assertRaisesRegex(GuardBlocked, 'budget exhausted'):
            await self.guard.submit(self.request('x=99', 'f' * 32), self.rpc)
        self.assertEqual(self.calls, 12)

    async def test_existing_failures_are_retained_under_doubled_limits(self):
        for n in range(3):
            await self.fail(f'x={n}')
        restarted=SubmissionGuard(self.path)
        row=await restarted.submit(self.request('x=3'),self.rpc)
        self.assertEqual(row['state'],'queued')
        self.assertEqual(restarted.summary()['failed_count'],3)
        self.assertEqual(restarted.summary()['failure_limit_per_source'],6)
        self.assertEqual(restarted.summary()['failure_limit_total'],12)

    async def test_pending_job_blocks_changed_submission(self):
        await self.guard.submit(self.request(), self.rpc)
        with self.assertRaisesRegex(GuardBlocked, 'still pending'):
            await self.guard.submit(self.request('x=2'), self.rpc)
        self.assertEqual(self.calls, 1)

    async def test_completed_duplicate_reuses_job(self):
        first = await self.guard.submit(self.request(), self.rpc)
        first['state'] = 'completed'
        second = await self.guard.submit(self.request(), self.rpc)
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(self.calls, 1)

    async def test_uncertain_transport_never_replays_on_restart(self):
        async def disconnected(action, request):
            raise TimeoutError('reply lost')
        with self.assertRaises(TimeoutError):
            await self.guard.submit(self.request(), disconnected)
        with self.assertRaisesRegex(GuardBlocked, 'uncertain'):
            await SubmissionGuard(self.path).submit(self.request('x=2'), self.rpc)
        self.assertEqual(self.calls, 0)

    async def test_syntax_error_is_not_submitted_or_reserved(self):
        with self.assertRaises(SyntaxError):
            await self.guard.submit(self.request('x='), self.rpc)
        self.assertEqual(self.guard.rows(), [])

    async def test_no_silent_fresh_restart(self):
        request = {'operation': 'author', 'code': 'x=1'}
        row = await self.guard.submit(request, self.rpc)
        row['state'] = 'completed'
        with self.assertRaisesRegex(GuardBlocked, 'silently restart'):
            await self.guard.submit({**request, 'code': 'x=2'}, self.rpc)

    async def test_concurrent_submission_rejected_before_network(self):
        with self.guard.locked():
            with self.assertRaisesRegex(GuardBlocked, 'concurrently'):
                await SubmissionGuard(self.path).submit(self.request(), self.rpc)
        self.assertEqual(self.calls, 0)


if __name__ == '__main__':
    unittest.main()
