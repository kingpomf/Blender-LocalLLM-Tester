"""Verify fresh MCP API guidance and reconcile known failures without new jobs."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows
from scripts.workflow_tools import atomic_json


async def main():
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    config=json.loads(subprocess.check_output(['opencode','debug','config'],cwd=ROOT,text=True))
    settings=config['mcp']['bowling-blender52']
    params=StdioServerParameters(command=settings['command'][0],args=settings['command'][1:],cwd=str(ROOT),env=dict(os.environ))
    before=guard_rows(ROOT)
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            async def call(tool,args):
                result=await session.call_tool(tool,args)
                assert not result.isError,result.content
                return result.structuredContent or json.loads(next(c.text for c in result.content if c.type=='text'))
            tools=[t.name for t in (await session.list_tools()).tools]
            assert 'blender_api_lookup' in tools
            unsupported=await call('blender_api_lookup',{'query':'Mesh.calc_normals_use_fit_sharp'})
            assert unsupported['available'] is False
            supported=await call('blender_api_lookup',{'query':'Mesh.update'})
            assert supported['available'] is True
            source=(await call('blender_workflow_status',{}))['current_source']
            rejected=await call('blender_scene_author',{'code':(ROOT/'artifacts/scripts/accepted_6a3c128b6ab54880b0f6449b85e2fab0.py').read_text()})
            assert rejected['code']=='api_correction' and rejected['attempt_consumed'] is False
            api=await call('blender_job_status',{'job_id':'6a3c128b6ab54880b0f6449b85e2fab0'})
            assert api['recoverable'] and api['hard_failure'] is False
            geometry=await call('blender_job_status',{'job_id':'82d3d39a52f34fce88177515528a1998'})
            assert geometry['state']=='failed' and geometry.get('hard_failure') is not False
            after=await call('blender_workflow_status',{})
            assert after['current_source']==source and not after['pending_jobs']
            assert guard_rows(ROOT)==before
            assert after['guard']['failed_count']==3 and after['guard']['api_correction_count']==1
            evidence={'passed':True,'tools':tools,'unsupported_lookup':unsupported,'supported_lookup':supported,
                'preflight':rejected,'runtime_api_correction':api,'geometry_failure':geometry,
                'guard':after['guard'],'attempt_rows_unchanged':True,'asset_source_unchanged':True,'source':source}
            atomic_json(ROOT/'testing/blender-api-policy/mcp-acceptance.json',evidence)
            print(json.dumps({'passed':True,'preflight_no_attempt':True,'runtime_api_recoverable':True,
                'geometry_still_hard':True,'attempt_rows_unchanged':True,'guard':after['guard']},indent=2))


if __name__=='__main__':asyncio.run(main())
