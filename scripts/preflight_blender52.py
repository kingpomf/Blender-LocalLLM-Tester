"""Fresh MCP handshake + runtime check without submitting any build jobs."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    root = Path(__file__).resolve().parents[1]
    # Ask installed OpenCode for the effective merged config, not just JSON text.
    result = subprocess.run(['opencode', 'debug', 'config'], cwd=root,
                            capture_output=True, text=True, check=True)
    config = json.loads(result.stdout)
    assert config['mcp']['z6-blender-worker']['enabled'] is False
    mcp = config['mcp']['bowling-blender52']
    assert mcp['enabled']
    assert config['agent']['build']['steps'] == 60
    params = StdioServerParameters(command=mcp['command'][0], args=mcp['command'][1:],
                                   env=dict(os.environ), cwd=str(root))
    async with stdio_client(params) as streams:
        async with ClientSession(*streams, read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert len(tools.tools) == 9
            result = await session.call_tool('blender_capabilities', {})
            assert not result.isError, result.content
            value = result.structuredContent or json.loads(next(item.text for item in result.content if item.type == 'text'))
            assert value and value['runtime_verified']
            assert value['actual_version'] == 'Blender 5.2.3 LTS'
            evidence = {'passed': True, 'server': 'bowling-blender52',
                              'max_agent_steps': 60, 'tools': [t.name for t in tools.tools],
                              'capabilities': value}
            print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
