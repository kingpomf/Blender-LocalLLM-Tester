"""Project-only MCP entry point: isolated 5.2 queue, CPU rendering, shared code.

The shared gateway is pinned to another runtime and source queue. Never route
this project's 5.2 scenes there. No worker or gateway globals are modified.
"""
import os
import sys

APP = '/Users/start/Development/blender-new-llm-setup'
sys.path.insert(0, APP)

from blender_worker import mcp_server
from blender_worker.transport import SSHTransport


class ProjectTransport(SSHTransport):
    async def rpc(self, action, request):
        if action.startswith('gpu-'):
            raise ValueError('Bowling Blender 5.2 trial is CPU-only. Use blender_render device="CPU"; the shared GPU gateway is a different runtime/root.')
        result = await super().rpc(action, request)
        if action == 'capabilities':
            result['gateway'] = {'configured': False,
                                 'reason': 'Project-scoped Blender 5.2 trial; CPU rendering only'}
            result['project_runtime'] = {'expected_version': '5.2.3',
                                         'binary': self.blender, 'root': self.root,
                                         'render_devices': ['CPU']}
        return result


def transport():
    return ProjectTransport(os.environ['BLENDER_SSH_TARGET'], os.environ['BLENDER_REMOTE_APP'],
                            os.environ['BLENDER_REMOTE_ROOT'], os.environ['BLENDER_REMOTE_BINARY'],
                            os.environ['BLENDER_DOWNLOADS'])


if __name__ == '__main__':
    mcp_server.transport = transport
    original_factory = mcp_server.FastMCP

    def project_server(name, **kwargs):
        kwargs['instructions'] = ('Project-only Blender 5.2.3 on Z6. All authoring and rendering '
                        'uses this isolated CPU queue; blender_render requires device="CPU". '
                        'GPU/video/shape operations are unavailable in this trial. '
                        'Preserve accepted IDs, poll durable jobs, and fetch verified artifacts. '
                        'Author functions must execute unconditionally and assign report. '
                        'See AGENTS.md and RUNTIME_52.md for build state and provenance.')
        return original_factory(name, **kwargs)

    mcp_server.FastMCP = project_server
    app = mcp_server.server()
    app.run()
