"""Small, version-locked Blender MCP catalog for this repository's local-model trial."""
import argparse
import asyncio
import json
from pathlib import Path
import shlex
import sys
from typing import Literal

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT))
from scripts.submission_guard import SubmissionGuard
from scripts.check_references import check as check_references
from scripts.trial_settings import TRIAL
from scripts.workflow_tools import Workflow

APP = '/Users/start/Development/blender-new-llm-setup'
sys.path.insert(0, APP)
from mcp.server.fastmcp import FastMCP
from blender_worker.transport import SSHTransport
from blender_worker.schema import validate

REMOTE_APP = '/home/kingpomf/Development/blender-new-llm-setup'
BINARY = REMOTE_APP + '/tools/blender-5.2.3-linux-x64/blender'
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
    workflow = None if qualification else Workflow(PROJECT,client,guard)
    app = FastMCP('bowling-blender52', instructions=(
        'Blender 5.2.3 LTS on Z6, version-locked CPU-only trial. '
        'On any STOP/circuit-breaker error, checkpoint and return BLOCKED to the user; do not loop. '
        'Six failed submissions per source or twenty total require operator review. '
        'Unchanged failed code is rejected, uncertain submissions never replayed. '
        'Start with blender_workflow_status for the authoritative current source and measured stage results. '
        'Author scene/cameras only: inline rendering and output subdirectories are rejected before any attempt. '
        'Completed author jobs automatically publish the native checkpoint and queue the fixed validator. '
        'Poll its validation_job; validation updates both stage ledgers from measured evidence. '
        'Use blender_render_view(role) and poll its view- ID for camera selection, queued CPU render and verified publication. '
        'Use blender_validate and blender_checkpoint instead of shell commands. Never manually edit stage status/source files. '
        'Recoverable preflight/pending-work responses consume no attempt; diagnose them without treating them as STOP. '
        'Use unconditional authoring entry points and a top-level report.'))

    async def submit(spec):
        validate(spec)
        if workflow:
            return await workflow.call('submit_native',spec=spec,role=spec['operation'])
        row = await guard.submit(spec, client.rpc)
        return {k: row[k] for k in ('id', 'state', 'error', 'manifest') if k in row}

    @app.tool()
    async def blender_capabilities() -> dict:
        """Verify actual installed Blender and queue runner; report durable submission state. Read-only, no scene job."""
        evidence = await client.probe()
        summary=guard.summary()
        if workflow:
            accepted=summary.pop('accepted_jobs')
            summary['accepted_job_count']=len(accepted)
            summary['pending_jobs']=[r for r in accepted if r['state'] in {'queued','running'}]
        return {'runtime_verified': True, 'actual_version': evidence['version'],
                'binary': BINARY, 'root': root, 'runners': evidence['runners'],
                'authoring': {'available': True, 'fresh_scene_objects': [], 'execution_name': '__blender_author__'},
                'render_devices': ['CPU'], 'guard': summary,
                'workflow_tools_available':workflow is not None}

    @app.tool()
    async def blender_scene_author(code: str, source_job: str | None = None) -> dict:
        """Edit scene/cameras only. Common inline render/API/output mistakes return recoverable feedback before consuming attempts. Completed edits auto-checkpoint and auto-queue validation; poll returned IDs. Source defaults to authoritative current scene."""
        if workflow:return await workflow.call('author',code=code,source_job=source_job)
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
        if workflow:return workflow.error('use_delivery_export','Use blender_export_delivery for final selected GLBs and measured reimports; generic whole-scene export is not final delivery.')
        return await submit({'operation': 'export', 'source_job': source_job, 'formats': formats})

    @app.tool()
    async def blender_render(source_job: str, frames: list[int] = [1], resolution: list[int] = [1280,720],
                             samples: int = 8, device: Literal['CPU'] = 'CPU') -> dict:
        """Render actual scene on 5.2 CPU. Max 60 frames, 2048 pixels/side. Prefer one view per job."""
        if workflow:return await workflow.call('render',source_job=source_job,frames=frames,resolution=resolution,samples=samples)
        return await submit({'operation': 'render', 'source_job': source_job, 'frames': frames,
                             'resolution': resolution, 'samples': samples})

    @app.tool()
    async def blender_job_status(job_id: str) -> dict:
        """Poll accepted job. Completed execution is not a stage PASS."""
        if workflow:return await workflow.call('status',job_id=job_id)
        row = await client.rpc('status', {'job_id': job_id})
        for attempt in guard.rows():
            if attempt['job'] == job_id:
                guard.update(attempt['fingerprint'], row)
        return {k: row[k] for k in ('id', 'state', 'error', 'manifest', 'progress', 'diagnostics') if k in row}

    @app.tool()
    async def blender_job_diagnostics(job_id: str) -> dict:
        """Read bounded terminal CPU logs once; diagnose the actual error before changing code."""
        if workflow:return await workflow.call('diagnostics',job_id=job_id)
        return await client.rpc('diagnostics', {'job_id': job_id})

    @app.tool()
    async def blender_job_cancel(job_id: str) -> dict:
        """Cancel an accepted job; poll to terminal state. Does not reset failure budgets."""
        if workflow:return await workflow.call('cancel',job_id=job_id)
        return await client.rpc('cancel', {'job_id': job_id})

    @app.tool()
    async def blender_artifact_fetch(job_id: str, name: str) -> dict:
        """Fetch completed manifest artifact with hash verification. Failed jobs require diagnostics."""
        if workflow and job_id.startswith('view-'):
            result=await workflow.call('status',job_id=job_id)
            return result.get('artifact',workflow.error('view_not_ready','Poll the accepted view ID; no new job or artifact guess is needed.',view_id=job_id))
        return await client.fetch(job_id, name)

    if workflow:
        @app.tool()
        async def blender_workflow_status() -> dict:
            """Read authoritative current source, checkpoint, measured stages, current budget and pending IDs. Restores managed stage mirrors; no inference/render submission."""
            return await workflow.call('workflow_status')

        @app.tool()
        async def blender_checkpoint(job_id: str) -> dict:
            """Publish a completed current/direct-child scene with verified hashes, then auto-queue its fixed validation. Usually automatic through job_status. Never claims a stage PASS merely for execution."""
            return await workflow.call('checkpoint',job_id=job_id)

        @app.tool()
        async def blender_validate(source_job: str | None = None) -> dict:
            """Queue or recover the fixed read-only validator for the current source. Poll returned native ID. On completion merges actual local render proof and synchronizes both ledgers; no arbitrary code/check thresholds accepted."""
            return await workflow.call('validate',source_job=source_job)

        @app.tool()
        async def blender_render_view(role: Literal['overview','player','pindeck','props'], source_job: str | None = None,
                                      resolution: list[int] = [1280,720], samples: int = 8) -> dict:
            """Render one named view through the CPU queue. Returns a view- ID; poll it with blender_job_status. Camera-selection and render IDs are checkpointed automatically; completed image publishes with hash/provenance. Never render inline."""
            return await workflow.call('render_view',role=role,source_job=source_job,resolution=resolution,samples=samples)

        @app.tool()
        async def blender_publish_render(role: Literal['overview','player','pindeck','props'],job_id: str,
                                         asset_source_job: str | None = None) -> dict:
            """Recover/publish an existing completed native render from the current asset with lineage, mesh/material and hash checks. Does not rerender or invent visual acceptance."""
            return await workflow.call('publish',role=role,job_id=job_id,asset_source_job=asset_source_job)

        @app.tool()
        async def blender_review_presentation() -> dict:
            """Queue fixed pixel-based review of all four current beauty images. Poll its review- ID with job_status. Qwen3.6 stays the agent; an image-only helper records actual visibility and qualitative evidence, then refreshes measured validation."""
            return await workflow.call('review_presentation')

        @app.tool()
        async def blender_export_delivery() -> dict:
            """After current geometry/visual acceptance passes, queue fixed selection-specific GLB exports and measured reimports in an artifact-only job. Source/canonical geometry stays unchanged; poll returned native ID for automatic export publication."""
            return await workflow.call('export_delivery')

        @app.tool()
        async def blender_finish_delivery() -> dict:
            """Verify current measured acceptance, fixed export/reimport receipts, four reviewed current renders and written BUILD_REPORT/ASSET_GUIDE; build delivery hash manifest and set COMPLETE only if every requirement is present."""
            return await workflow.call('finish_delivery')

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification', action='store_true', help='Operator-only separate fixture queue/state')
    server(parser.parse_args().qualification).run()
