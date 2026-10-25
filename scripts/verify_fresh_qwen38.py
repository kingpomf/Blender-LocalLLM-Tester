"""Prove the new model trial has no retired asset/session/guard state before launch."""
import asyncio
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.check_resume import check
from scripts.continuation_preflight import guard_rows
from scripts.probe_coding_model import probe
from scripts.trial_settings import MODEL,TRIAL,CONTEXT,OUTPUT
from scripts.workflow_tools import atomic_json


async def main():
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    folder=ROOT/'testing/qwen38-turbo-fresh-20261025'
    assert not (ROOT/'.runtime/autonomous-run/state.json').exists(),'A controller state already exists; inspect status, do not relaunch'
    assert guard_rows(ROOT)==[]
    consistency=check(ROOT);assert consistency['passed'] and consistency['run_status']=='NOT_STARTED' and consistency['active_file_count']==0
    archive=ROOT/'artifacts/archive/qwen36-final-before-qwen38-turbo-20261025'
    manifest=json.loads((archive/'ARCHIVE_MANIFEST.json').read_text())
    assert manifest['state']=='archived_fresh_state_ready'
    for relative,digest in manifest['preserved_tools'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
    config=json.loads(subprocess.check_output(['opencode','debug','config'],cwd=ROOT,text=True))
    assert config['model']==MODEL==config['agent']['bowling-coder']['model']==config['agent']['build']['model']
    assert config['provider']['z6-llama']['models']['qwen38-turbo']['limit']=={'context':CONTEXT,'output':OUTPUT}
    settings=config['mcp']['bowling-blender52']
    params=StdioServerParameters(command=settings['command'][0],args=settings['command'][1:],cwd=str(ROOT),env=dict(os.environ))
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            async def call(tool,args):
                result=await session.call_tool(tool,args);assert not result.isError,result.content
                return result.structuredContent or json.loads(next(c.text for c in result.content if c.type=='text'))
            status=await call('blender_workflow_status',{})
            api=await call('blender_api_lookup',{'query':'Object.children'})
            capabilities=await call('blender_capabilities',{})
            assert status['current_source'] is None and status['checkpoint'] is None
            assert not status['pending_jobs'] and not status['views'] and not status['reviews']
            assert capabilities['guard']['accepted_job_count']==0 and capabilities['root'].endswith('/'+TRIAL)
            assert api['runtime_return']['python_type']=='tuple'
    assert guard_rows(ROOT)==[]
    evidence={'passed':True,'model_probe':probe(MODEL),'model':MODEL,'trial':TRIAL,'context':CONTEXT,'output':OUTPUT,
        'consistency':consistency,'status':status,'capabilities':capabilities,'api_lookup':api,
        'preserved_tool_hashes_verified':True,'old_attempts_archived':manifest['old_attempts'],
        'old_failures_archived':manifest['old_failures'],'no_old_asset_or_session':True,'new_attempts':0}
    atomic_json(folder/'prelaunch.json',evidence)
    print(json.dumps({'passed':True,'model':MODEL,'trial':TRIAL,'source':None,'attempts':0,
        'old_attempts_archived':manifest['old_attempts'],'old_failures_archived':manifest['old_failures']},indent=2))


if __name__=='__main__':asyncio.run(main())
