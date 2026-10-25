"""Fresh MCP handshake + runtime check without submitting any build jobs."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from trial_settings import TRIAL, MODEL, CONTEXT, OUTPUT, COMPACTION_RESERVE


async def main():
    root = Path(__file__).resolve().parents[1]
    # Ask installed OpenCode for the effective merged config, not just JSON text.
    result = subprocess.run(['opencode', 'debug', 'config'], cwd=root,
                            capture_output=True, text=True, check=True)
    config = json.loads(result.stdout)
    assert config['model'] == MODEL
    assert config['small_model'] == config['model']
    assert config['agent']['build']['model'] == MODEL
    assert config['agent']['bowling-coder']['model']==MODEL
    assert config['agent']['bowling-coder']['tools']['bash'] is False
    assert config['command']['bowling-start']['agent']=='bowling-coder'
    assert all(config['command'][name]['model']==MODEL for name in ['bowling-run','bowling-references','bowling-start','bowling-continue'])
    assert config['experimental']['continue_loop_on_deny'] is True
    model_profile=config['provider']['z6-llama']['models'][MODEL.split('/',1)[1]]
    coding_context=model_profile['limit']['context']
    assert coding_context == CONTEXT and model_profile['limit']['output']==OUTPUT
    assert config['mcp']['z6-blender-worker']['enabled'] is False
    assert config['mcp']['imageMCP']['enabled'] is True
    assert config['provider']['z6-llama']['models']['qwen38-27b']['attachment'] is True
    mcp = config['mcp']['bowling-blender52']
    assert mcp['enabled']
    assert config.get('agent',{}).get('build',{}).get('steps') is None
    assert config['compaction']['auto'] is True
    assert config['compaction']['prune'] is True
    assert config['compaction']['reserved'] == COMPACTION_RESERVE
    assert config['tool_output']=={'max_lines':160,'max_bytes':12000}
    params = StdioServerParameters(command=mcp['command'][0], args=mcp['command'][1:],
                                   env=dict(os.environ), cwd=str(root))
    async with stdio_client(params) as streams:
        async with ClientSession(*streams, read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            tools = await session.list_tools()
            required={'blender_scene_summary','blender_validation_details','blender_api_lookup','blender_workflow_status','blender_checkpoint','blender_validate','blender_render_view',
                      'blender_publish_render','blender_review_presentation','blender_export_delivery','blender_finish_delivery'}
            assert required<={tool.name for tool in tools.tools}
            result = await session.call_tool('blender_capabilities', {})
            assert not result.isError, result.content
            value = result.structuredContent or json.loads(next(item.text for item in result.content if item.type == 'text'))
            assert value and value['runtime_verified']
            assert value['actual_version'] == 'Blender 5.2.3 LTS'
            assert value['root'].endswith('/var/'+TRIAL)
            assert value['guard']['failure_limit_per_source']==6
            assert value['guard']['failure_limit_total']==20
            evidence = {'passed': True, 'server': 'bowling-blender52',
                               'selected_model': config['model'], 'context_size': coding_context,
                               'max_agent_steps': None, 'compaction':config['compaction'],
                               'tools': [t.name for t in tools.tools],
                              'capabilities': value}
            print(json.dumps(evidence, indent=2))
    image = config['mcp']['imageMCP']
    params = StdioServerParameters(command=image['command'][0], args=image['command'][1:],
        env={**os.environ, **image.get('environment', {})}, cwd=str(root))
    async with stdio_client(params) as streams:
        async with ClientSession(*streams, read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            image_tools = await session.list_tools()
            result_tool = next(tool for tool in image_tools.tools if tool.name == 'image_job_result')
            assert 'output_dir' in result_tool.inputSchema['properties']
            caps = await session.call_tool('image_capabilities', {})
            models = await session.call_tool('image_models', {})
            assert not caps.isError and not models.isError
            def payload(result):
                return result.structuredContent or json.loads(next(item.text for item in result.content if item.type == 'text'))
            capabilities, catalog = payload(caps), payload(models)
            assert capabilities['provider'] == 'available-workers'
            assert 'text-to-image' in capabilities['operations']
            assert any(model['id'] == 'qwen-image-2.1-turbo' for model in catalog['models'])
            assert any(model['id'] == 'qwen-image-2.1-q4' for model in catalog['models'])
            assert capabilities['workers']['elitedesk']['idempotent_submission'] is True
            print(json.dumps({'imageMCP_read_only_preflight':True,
                              'capabilities':capabilities, 'models':catalog}, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
