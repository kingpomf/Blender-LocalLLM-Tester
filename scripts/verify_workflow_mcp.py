"""Explicit native MCP workflow proof; durable IDs, no blind retries."""
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


async def main():
    folder=ROOT/'testing/workflow-hardening-20261024'
    path=folder/'mcp-acceptance.json'
    assert not path.exists(), 'Existing MCP qualification must be reconciled, not replayed'
    config=json.loads(subprocess.check_output(['opencode','debug','config'],cwd=ROOT,text=True))
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    settings=config['mcp']['bowling-blender52']
    params=StdioServerParameters(command=settings['command'][0],args=settings['command'][1:],cwd=str(ROOT),env=dict(os.environ))
    evidence={'passed':False,'state':'starting'}
    def save():path.write_text(json.dumps(evidence,indent=2)+'\n')
    save()
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            async def call(name,args):
                result=await session.call_tool(name,args)
                assert not result.isError,result.content
                return result.structuredContent or json.loads(next(c.text for c in result.content if c.type=='text'))
            tools=await session.list_tools();evidence['tools']=[tool.name for tool in tools.tools]
            status=await call('blender_workflow_status',{})
            before=guard_rows(ROOT)
            rejected=await call('blender_scene_author',{'code':'import bpy\nbpy.ops.render.render(write_still=True)'})
            assert rejected['recoverable'] and not rejected['submitted'] and not rejected['attempt_consumed']
            api=await call('blender_scene_author',{'code':"scene=bpy.context.scene\nscene.render.image_format='PNG'"})
            assert api['recoverable'] and guard_rows(ROOT)==before
            evidence.update(preflight_no_attempt_verified=True,current_source=status['current_source'])
            save()
            evidence['state']='view_submission_uncertain';save()
            view=await call('blender_render_view',{'role':'overview','samples':4})
            assert view.get('id','').startswith('view-'),view
            evidence.update(state='view_accepted',view_id=view['id'],camera_job=view.get('camera_job'));save()
            for _ in range(100):
                result=await call('blender_job_status',{'job_id':view['id']})
                evidence['last_status']=result;save()
                if result.get('state') in {'completed','failed','cancelled'}:break
                await asyncio.sleep(2)
            assert result.get('state')=='completed',result
            after=await call('blender_workflow_status',{})
            assert after['current_source']==status['current_source']
            assert after['guard']['failed_count']==0
            evidence.update(passed=True,state='completed',canonical_source_unchanged=True,
                            budget=after['guard'],artifact=result['artifact'])
            save()
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            result=await session.call_tool('blender_workflow_status',{})
            assert not result.isError
            data=result.structuredContent or json.loads(next(c.text for c in result.content if c.type=='text'))
            assert data['current_source']==evidence['current_source']
            assert evidence['view_id'] in data['views']
            evidence['fresh_process_recovery_verified']=True;save()
    print(json.dumps({k:evidence[k] for k in ['passed','view_id','preflight_no_attempt_verified','canonical_source_unchanged','fresh_process_recovery_verified','artifact']},indent=2))


if __name__=='__main__':asyncio.run(main())
