"""Small, version-locked Blender MCP catalog for this repository's local-model trial."""
import argparse
import asyncio
import json
from pathlib import Path
import shlex
import sys
from typing import Literal

APP = '/Users/start/Development/blender-new-llm-setup'
sys.path.insert(0, APP)
from mcp.server.fastmcp import FastMCP
from blender_worker.transport import SSHTransport
from blender_worker.schema import validate
from submission_guard import SubmissionGuard
from check_references import check as check_references

PROJECT = Path(__file__).resolve().parents[1]
REMOTE_APP = '/home/kingpomf/Development/blender-new-llm-setup'
BINARY = REMOTE_APP + '/tools/blender-5.2.3-linux-x64/blender'
TRIAL = 'bowling52-qwen36-mtp-q8-20261023'
EXPECTED = '5.2.3 LTS'

# Read-only host probe: verifies the executable and any runner owning this queue.
PROBE = '''
import json,subprocess,sys
from pathlib import Path
binary,root=sys.argv[1:]
version=subprocess.check_output([binary,'--version'],text=True).splitlines()[0]
runners=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
    try: args=p.read_bytes().decode().split('\\0')
    except (OSError,UnicodeError): continue
    if 'blender_worker' in args and 'run' in args and '--root' in args and args[args.index('--root')+1]==root:
        actual=args[args.index('--blender')+1] if '--blender' in args else None
        runners.append({'pid':p.parent.name,'binary':actual})
print(json.dumps({'version':version,'runners':runners}))
'''


def checked_runtime(evidence):
    if evidence['version'] != 'Blender ' + EXPECTED:
        raise RuntimeError('STOP: wrong executable version: ' + evidence['version'])
    if any(r['binary'] != BINARY for r in evidence['runners']):
        raise RuntimeError('STOP: this queue has a runner using another Blender binary.')
    return evidence


class ProjectTransport(SSHTransport):
    async def probe(self):
        command = shlex.join(['python3', '-c', PROBE, self.blender, self.root])
        process = await asyncio.create_subprocess_exec(
            'ssh', '-T', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'ConnectTimeout=8', self.target, command,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), 20)
        except BaseException:
            process.kill()
            await process.wait()
            raise
        if process.returncode:
            raise RuntimeError('Runtime probe failed: ' + stderr.decode()[:1000])
        return checked_runtime(json.loads(stdout))

    async def rpc(self, action, request):
        if action.startswith('gpu-') or str(request.get('job_id', '')).startswith('gpu-'):
            raise ValueError('STOP: this trial is CPU-only; no GPU gateway routing.')
        if action == 'submit':
            await self.probe()
            if request.get('source_job'):
                source = await super().rpc('status', {'job_id': request['source_job']})
                if source['state'] != 'completed' or (source.get('manifest') or {}).get('blender_version') != EXPECTED:
                    raise ValueError('STOP: source must be completed on Blender 5.2.3 in this trial queue.')
            if request['operation'] == 'author':
                # Assert in the executing process too, not just its configured path.
                original = request['code']
                code = ('import bpy\n'
                        "assert bpy.app.version[:3] == (5,2,3), 'Wrong runtime: '+bpy.app.version_string\n"
                        f"exec(compile({original!r}, '/job/submitted.py', 'exec'), globals())\n")
                request = {**request, 'code': code}
                validate(request)
        result = await super().rpc(action, request)
        if result.get('state') == 'completed' and (result.get('manifest') or {}).get('blender_version') != EXPECTED:
            raise RuntimeError('STOP: completed job has the wrong runtime; operator review required.')
        return result


def server(qualification=False):
    # Keep existing infrastructure fixtures in their original queue. They are
    # never sources or budget entries for a fresh model evaluation.
    queue = 'bowling52-guarded-20261022-qualification' if qualification else TRIAL
    root = REMOTE_APP + '/var/' + queue
    local = PROJECT / ('testing/blender52-guarded' if qualification else '.runtime/blender52')
    downloads = local / 'downloads' if qualification else PROJECT / 'artifacts/downloads'
    client = ProjectTransport('kingpomf@z6-llm', REMOTE_APP, root, BINARY, str(downloads))
    guard = SubmissionGuard(local / 'submissions.sqlite')
    app = FastMCP('bowling-blender52', instructions=(
        'Blender 5.2.3 LTS on Z6, version-locked CPU-only trial. '
        'On any STOP/circuit-breaker error, checkpoint and return BLOCKED to the user; do not loop. '
        'Three failed submissions per source or six total require operator review. '
        'Unchanged failed code is rejected, uncertain submissions never replayed. '
        'Call blender_capabilities first. Poll accepted jobs; inspect actual scene/report evidence. '
        'Use unconditional authoring entry points and a top-level report.'))

    async def submit(spec):
        validate(spec)
        row = await guard.submit(spec, client.rpc)
        return {k: row[k] for k in ('id', 'state', 'error', 'manifest') if k in row}

    @app.tool()
    async def blender_capabilities() -> dict:
        """Verify actual installed Blender and queue runner; report durable submission state. Read-only, no scene job."""
        evidence = await client.probe()
        return {'runtime_verified': True, 'actual_version': evidence['version'],
                'binary': BINARY, 'root': root, 'runners': evidence['runners'],
                'authoring': {'available': True, 'fresh_scene_objects': [], 'execution_name': '__blender_author__'},
                'render_devices': ['CPU'], 'guard': guard.summary()}

    @app.tool()
    async def blender_scene_author(code: str, source_job: str | None = None) -> dict:
        """Submit original Blender Python (48KB including runtime wrapper). Empty scene only for Stage 00. Later use completed 5.2 source. Assign report and call functions unconditionally. Identical failed code and exhausted retry budgets are blocked."""
        if not qualification:
            references = check_references(PROJECT)
            if not references['passed']:
                raise ValueError('STOP: imageMCP references must be ready before Blender authoring. '
                                 + '; '.join(references['issues']))
        return await submit({'operation': 'author', 'code': code, **({'source_job': source_job} if source_job else {})})

    @app.tool()
    async def blender_scene_inspect(source_job: str) -> dict:
        """Reopen a completed 5.2 native scene and inspect saved geometry; fetch scene.json."""
        return await submit({'operation': 'inspect', 'source_job': source_job})

    @app.tool()
    async def blender_export(source_job: str, formats: list[Literal['glb', 'obj', 'stl']]) -> dict:
        """Export meshes from a completed 5.2 scene. Use authoring for selection-specific exports."""
        return await submit({'operation': 'export', 'source_job': source_job, 'formats': formats})

    @app.tool()
    async def blender_render(source_job: str, frames: list[int] = [1], resolution: list[int] = [1280,720],
                             samples: int = 8, device: Literal['CPU'] = 'CPU') -> dict:
        """Render actual scene on 5.2 CPU. Max 60 frames, 2048 pixels/side. Prefer one view per job."""
        return await submit({'operation': 'render', 'source_job': source_job, 'frames': frames,
                             'resolution': resolution, 'samples': samples})

    @app.tool()
    async def blender_job_status(job_id: str) -> dict:
        """Poll accepted job. Completed execution is not a stage PASS."""
        row = await client.rpc('status', {'job_id': job_id})
        for attempt in guard.rows():
            if attempt['job'] == job_id:
                guard.update(attempt['fingerprint'], row)
        return {k: row[k] for k in ('id', 'state', 'error', 'manifest', 'progress', 'diagnostics') if k in row}

    @app.tool()
    async def blender_job_diagnostics(job_id: str) -> dict:
        """Read bounded terminal CPU logs once; diagnose the actual error before changing code."""
        return await client.rpc('diagnostics', {'job_id': job_id})

    @app.tool()
    async def blender_job_cancel(job_id: str) -> dict:
        """Cancel an accepted job; poll to terminal state. Does not reset failure budgets."""
        return await client.rpc('cancel', {'job_id': job_id})

    @app.tool()
    async def blender_artifact_fetch(job_id: str, name: str) -> dict:
        """Fetch completed manifest artifact with hash verification. Failed jobs require diagnostics."""
        return await client.fetch(job_id, name)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification', action='store_true', help='Operator-only separate fixture queue/state')
    server(parser.parse_args().qualification).run()
