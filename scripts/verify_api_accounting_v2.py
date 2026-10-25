"""Fresh MCP proof of source-linked API return errors and consistent failure responses."""
import asyncio
import argparse
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows
from scripts.run_bowling import native_outcome
from scripts.workflow_tools import atomic_json


async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--after-reset',action='store_true');args=parser.parse_args()
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
            original=await call('blender_workflow_status',{})
            lookup=await call('blender_api_lookup',{'query':'Object.children'})
            assert lookup['runtime_return']['python_type']=='tuple'
            job='bd557eba1416427cb8c9c2ed428fa43f'
            rejected=await call('blender_scene_author',{'code':(ROOT/f'artifacts/scripts/accepted_{job}.py').read_text()})
            assert rejected['code']=='api_correction' and rejected['attempt_consumed'] is False
            assert any(i['code']=='unsupported_return_member' for i in rejected['issues'])
            diagnostic=await call('blender_job_diagnostics',{'job_id':job})
            status=await call('blender_job_status',{'job_id':job})
            for result in [diagnostic,status]:
                assert result['hard_failure'] is False and result['correction']['origin']=='Object.children'
                event={'type':'tool_use','part':{'tool':'bowling-blender52_blender_job_status','state':{'output':json.dumps(result)}}}
                assert native_outcome(event,{},{}) is None
            geometry=await call('blender_job_diagnostics',{'job_id':'82d3d39a52f34fce88177515528a1998'})
            assert geometry['hard_failure'] is True
            after=await call('blender_workflow_status',{})
            assert not after['pending_jobs'] and original['current_source']==after['current_source']
            assert guard_rows(ROOT)==before
            if args.after_reset:
                assert after['guard']['failed_count']==0 and after['guard']['api_correction_count']==0 and after['guard']['failure_budget_reset_id']==3
                assert status['historical_failure'] and geometry['historical_failure']
                event={'type':'tool_use','part':{'tool':'bowling-blender52_blender_job_diagnostics','state':{'output':json.dumps(geometry)}}}
                assert native_outcome(event,{},{}) is None
            evidence={'passed':True,'lookup':lookup,'preflight':rejected,'classification':status,
                'diagnostics_same_category':diagnostic['failure_category']==status['failure_category'],
                'geometry_exception':geometry['exception'],'guard':after['guard'],
                'attempt_rows_unchanged':True,'source_unchanged':True}
            filename='mcp-after-reset.json' if args.after_reset else 'mcp-acceptance.json'
            atomic_json(ROOT/'testing/api-accounting-reset-20261025'/filename,evidence)
            print(json.dumps(evidence,indent=2))


if __name__=='__main__':asyncio.run(main())
