"""Read-only fresh-state/config/Strata/worker proof; does not submit a scene or inference."""
import asyncio
import ast
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
from trial_settings import MODEL,CONTEXT,OUTPUT,QUEUE

ROOT=Path(__file__).resolve().parents[1]


async def main():
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    subprocess.run(['python3',str(ROOT/'scripts/check_resume.py')],cwd=ROOT,check=True)
    state=json.loads((ROOT/'RUN_STATE.json').read_text())
    assert state['status']=='NOT_STARTED' and not state['jobs'] and not state['verified_source']
    config=json.loads(subprocess.check_output(['opencode','debug','config'],cwd=ROOT,text=True))
    assert config['model']==config['small_model']==config['agent']['build']['model']==MODEL
    assert config['command']['kart-start']['model']==MODEL
    profile=config['provider']['z6-llama']['models']['qwen38-flash-next']
    assert profile['limit']=={'context':CONTEXT,'output':OUTPUT}
    assert profile['interleaved']=={'field':'reasoning_content'}
    assert config['permission']['bash']['sleep 15']=='allow'
    assert config['experimental']['continue_loop_on_deny'] is True
    settings=config['mcp']['z6-blender-worker'];env={**os.environ,**settings['environment']}
    assert env['BLENDER_REMOTE_ROOT'].endswith('/'+QUEUE)
    assert Path(env['BLENDER_DOWNLOADS'])==ROOT/'artifacts/downloads'
    probe=("import json,sqlite3,subprocess,sys;from pathlib import Path;"
        "c=json.loads((Path.home()/'Development/z6-gpu-gateway/shared/production-config.json').read_text());"
        "r=json.loads(Path(c['coding_registry']).read_text());m=next(x for x in r['models'] if x['id']=='qwen38-flash-next');"
        "db=Path(sys.argv[1])/'queue.sqlite';count=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True).execute('SELECT count(*) FROM jobs').fetchone()[0] if db.exists() else 0;"
        "print(json.dumps({'id':m['id'],'backend':m.get('backend'),'context':m['context_size'],'enabled':m.get('enabled',True),'queue_jobs':count,'version':subprocess.check_output([sys.argv[2],'--version'],text=True).splitlines()[0]}))")
    command=shlex.join(['python3','-c',probe,env['BLENDER_REMOTE_ROOT'],env['BLENDER_REMOTE_BINARY']])
    installed=json.loads(subprocess.check_output(['ssh','-T','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',env['BLENDER_SSH_TARGET'],command],text=True,timeout=30))
    assert installed['backend']=='strata' and installed['enabled'] and installed['context']==CONTEXT
    assert installed['version']=='Blender 5.2.3 LTS' and installed['queue_jobs']==0
    hashes={}
    for name in ['helpers.py','presentation.py','validate.py']:
        path=ROOT/'support/kart'/name;data=path.read_bytes();ast.parse(data)
        original=subprocess.check_output(['git','show','HEAD:support/kart/'+name],cwd=ROOT)
        assert data==original,'Supplied assistance must be unchanged'
        hashes[name]=hashlib.sha256(data).hexdigest()
    params=StdioServerParameters(command=settings['command'][0],args=settings['command'][1:],cwd=str(ROOT),env=env)
    async with stdio_client(params) as streams:
        async with ClientSession(*streams,read_timeout_seconds=timedelta(seconds=90)) as session:
            await session.initialize()
            tools=[tool.name for tool in (await session.list_tools()).tools]
            assert {'blender_scene_author','blender_render','blender_job_status','blender_job_diagnostics'}<=set(tools)
            result=await session.call_tool('blender_capabilities',{});assert not result.isError,result.content
            capabilities=result.structuredContent or json.loads(next(item.text for item in result.content if item.type=='text'))
            assert capabilities['cpu_available'] and capabilities['authoring']['available']
    evidence={'passed':True,'model':MODEL,'backend':'strata','context':CONTEXT,'output':OUTPUT,'queue':QUEUE,
        'installed':installed,'support_hashes':hashes,'capabilities':capabilities,'scene_jobs_submitted':0,'inference_submitted':False}
    directory=ROOT/'.runtime';directory.mkdir(exist_ok=True)
    (directory/'preflight.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({key:evidence[key] for key in ['passed','model','backend','context','output','queue','scene_jobs_submitted']},indent=2))


if __name__=='__main__':asyncio.run(main())
