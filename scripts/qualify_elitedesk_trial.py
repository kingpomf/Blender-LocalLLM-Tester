"""Small real author+CUDA fixture in separate local evidence, never the model asset ledger."""
import asyncio
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import blender52_mcp as w
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import atomic_json

CODE="""import bpy
from mathutils import Vector
assert bpy.app.version[:3]==(5,2,3)
assert len(bpy.data.objects)==0
scene=bpy.context.scene
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0.5))
mat=bpy.data.materials.new('QualificationBlue');mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.04,0.2,0.7,1)
bpy.context.object.data.materials.append(mat)
cam=bpy.data.objects.new('QualificationCamera',bpy.data.cameras.new('QualificationCamera'))
scene.collection.objects.link(cam);cam.location=(2,-3,2)
cam.rotation_euler=(Vector((0,0,0.5))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
light=bpy.data.objects.new('QualificationArea',bpy.data.lights.new('QualificationArea','AREA'))
scene.collection.objects.link(light);light.location=(1,-2,4);light.data.energy=1000
scene.render.engine='CYCLES'
report={'passed':True,'purpose':'infrastructure fixture, not bowling asset','version':bpy.app.version_string}
"""


async def main():
    directory=ROOT/'.runtime/elitedesk-qualification';directory.mkdir(exist_ok=True)
    path=directory/'state.json';state=json.loads(path.read_text()) if path.exists() else {}
    guard=SubmissionGuard(directory/'submissions.sqlite')
    client=w.ProjectTransport(w.WORKER_HOST,w.REMOTE_APP,w.WORKER_ROOT,w.BINARY,str(directory/'downloads'),dedicated_gpu=True)
    async def stage(label,spec):
        if label in state:row=await client.rpc('status',{'job_id':state[label]})
        else:
            row=await guard.submit(spec,client.rpc);state[label]=row['id'];atomic_json(path,state)
        for _ in range(120):
            row=await client.rpc('status',{'job_id':row['id']})
            for attempt in guard.rows():
                if attempt['job']==row['id']:guard.update(attempt['fingerprint'],row)
            if row['state'] in {'completed','failed','cancelled'}:break
            await asyncio.sleep(1)
        if row['state']=='failed':
            if not row['id'].startswith('gpu-'):print(json.dumps(await client.rpc('diagnostics',{'job_id':row['id']})))
            raise RuntimeError('Qualification failed; preserve IDs, no replay')
        assert row['state']=='completed',row
        return row
    built=await stage('author',{'operation':'author','code':CODE})
    rendered=await stage('render',{'operation':'render','source_job':built['id'],'frames':[1],'resolution':[512,512],'samples':8})
    manifest=rendered['manifest'];assert manifest['blender_version']=='5.2.3 LTS'
    assert manifest['device']['backend']=='CUDA' and manifest['device']['cpu_enabled'] is False
    image=await client.fetch(rendered['id'],'frame-0001.png')
    evidence={'passed':True,'author':built['id'],'render':rendered['id'],'manifest':manifest,'artifact':image}
    atomic_json(directory/'result.json',evidence)
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':asyncio.run(main())
