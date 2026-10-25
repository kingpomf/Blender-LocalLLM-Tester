"""Fresh MCP compact-output and checkpoint proof, without submitting new jobs."""
import asyncio
from datetime import timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.continuation_preflight import guard_rows
from scripts.workflow_tools import atomic_json


async def main():
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    config=json.loads(subprocess.check_output(['opencode','debug','config'],cwd=ROOT,text=True))
    assert config['compaction']['reserved']==32768 and config['tool_output']=={'max_lines':160,'max_bytes':12000}
    settings=config['mcp']['bowling-blender52'];before=guard_rows(ROOT)
    params=StdioServerParameters(command=settings['command'][0],args=settings['command'][1:],cwd=str(ROOT),env=dict(os.environ))
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            async def call(tool,args):
                result=await session.call_tool(tool,args);assert not result.isError,result.content
                return result.structuredContent or json.loads(next(item.text for item in result.content if item.type=='text'))
            tools=[tool.name for tool in (await session.list_tools()).tools]
            status=await call('blender_workflow_status',{})
            scene=await call('blender_scene_summary',{'names':['BowlingPair01_ROOT','Lane_L_Surface','Pin_L_01']})
            details=await call('blender_validation_details',{'stage':'00'})
            for value in [status,scene,details]:assert len(json.dumps(value).encode())<12000
            assert scene['source']==status['current_source']==details['source']
            assert any(check['id']=='S00_hierarchy' and check['status']=='FAIL' for check in details['checks'])
            assert guard_rows(ROOT)==before and not status['pending_jobs']
    result=subprocess.run([settings['command'][0],str(ROOT/'scripts/reconcile_context_checkpoint.py')],cwd=ROOT,
        text=True,capture_output=True,check=True,timeout=300)
    checkpoint=json.loads(result.stdout);assert checkpoint['passed'] and not checkpoint['pending_jobs']
    assert checkpoint['hard_failures']==0 and checkpoint['api_corrections']==0 and guard_rows(ROOT)==before
    evidence={'passed':True,'tools':tools,'compaction':config['compaction'],'tool_output':config['tool_output'],
        'scene_summary':scene,'validation_details':details,'reconciliation':checkpoint,'attempt_rows_unchanged':True,
        'response_bytes':{name:len(json.dumps(value).encode()) for name,value in [('status',status),('scene',scene),('details',details)]}}
    atomic_json(ROOT/'testing/context-recovery-reset-20261025/mcp-acceptance.json',evidence)
    print(json.dumps({'passed':True,'tools':len(tools),'response_bytes':evidence['response_bytes'],'reconciliation':checkpoint},indent=2))


if __name__=='__main__':asyncio.run(main())
