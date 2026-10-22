"""Exercise a fresh project MCP process, durable 5.2 jobs and verified artifacts."""
import asyncio
import argparse
from datetime import timedelta
import hashlib
import json
import os
from pathlib import Path
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'testing/blender52-guarded'
EVIDENCE = OUT / 'runtime-evidence.json'

AUTHOR = '''
import bpy
from mathutils import Vector
assert bpy.app.version[:3] == (5,2,3), bpy.app.version_string
assert len(bpy.data.objects) == 0
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
collection = bpy.data.collections.new('RuntimeFixture')
scene.collection.children.link(collection)
mesh = bpy.data.meshes.new('TriangleMesh')
mesh.from_pydata([(-1,0,0),(1,0,0),(0,0,1.5)], [], [(0,1,2)])
obj = bpy.data.objects.new('FixtureTriangle',mesh)
collection.objects.link(obj)
root = bpy.data.objects.new('FixtureRoot',None)
scene.collection.objects.link(root)
obj.parent = root
mat = bpy.data.materials.new('FixtureBlue')
mat.diffuse_color = (0.05,0.3,0.8,1)
mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.05,0.3,0.8,1)
obj.data.materials.append(mat)
cam = bpy.data.objects.new('FixtureCamera',bpy.data.cameras.new('FixtureCamera'))
scene.collection.objects.link(cam)
cam.location = (2,-5,2)
cam.rotation_euler = (Vector((0,0,0.6))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.camera = cam
light = bpy.data.objects.new('FixtureLight',bpy.data.lights.new('FixtureLight','AREA'))
scene.collection.objects.link(light)
light.location = (0,-3,4)
light.rotation_euler = (Vector((0,0,0.5))-light.location).to_track_quat('-Z','Y').to_euler()
light.data.energy = 500
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
root.select_set(True)
bpy.ops.export_scene.gltf(filepath='/job/fixture.glb',export_format='GLB',use_selection=True)
report = {'version':bpy.app.version_string,'scene_linked':collection.name in scene.collection.children,
          'parent':obj.parent.name,'objects':len(scene.objects),'passed':True}
'''

REOPEN = '''
import bpy
assert bpy.app.version[:3] == (5,2,3)
assert bpy.data.objects['FixtureTriangle'].parent.name == 'FixtureRoot'
assert 'RuntimeFixture' in bpy.context.scene.collection.children
bpy.ops.export_scene.gltf(filepath='/job/roundtrip.glb',export_format='GLB')
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.import_scene.gltf(filepath='/job/roundtrip.glb')
obj = bpy.data.objects['FixtureTriangle']
assert obj.parent.name == 'FixtureRoot'
assert len(obj.data.vertices) == 3
assert len(obj.data.materials) == 1
report = {'passed':True,'version':bpy.app.version_string,'imported_vertices':len(obj.data.vertices),
          'materials':len(obj.data.materials),'parent':obj.parent.name}
'''


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if EVIDENCE.exists() and not args.resume:
        raise SystemExit('Evidence already exists. Resume its accepted IDs; do not replay qualification.')
    config = json.loads((ROOT / 'opencode.json').read_text())['mcp']['bowling-blender52']
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = (json.loads(EVIDENCE.read_text()) if EVIDENCE.exists()
                else {'passed': False, 'jobs': {}, 'artifacts': []})

    def save():
        EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n')

    save()
    params = StdioServerParameters(command=config['command'][0], args=config['command'][1:] + ['--qualification'],
                                   env=dict(os.environ), cwd=str(ROOT))
    with (OUT / 'mcp.log').open('w') as log:
        async with stdio_client(params, errlog=log) as streams:
            async with ClientSession(*streams, read_timeout_seconds=timedelta(seconds=90)) as session:
                await session.initialize()

                async def tool(name, arguments):
                    result = await session.call_tool(name, arguments)
                    if result.isError:
                        raise RuntimeError(str(result.content))
                    if result.structuredContent:
                        return result.structuredContent
                    text = next(item.text for item in result.content if item.type == 'text')
                    return json.loads(text)

                async def job(label, name, arguments, expected='completed'):
                    previous = evidence['jobs'].get(label)
                    if previous:
                        if 'id' not in previous:
                            raise RuntimeError('Uncertain submission: operator must reconcile ' + label)
                        row = await tool('blender_job_status', {'job_id': previous['id']})
                    else:
                        evidence['jobs'][label] = {'state': 'submission_uncertain'}
                        save()
                        row = await tool(name, arguments)
                    evidence['jobs'][label] = row
                    save()
                    deadline = time.monotonic() + 210
                    while row['state'] in ('queued', 'running'):
                        if time.monotonic() > deadline:
                            raise TimeoutError('Resume accepted job ' + row['id'])
                        await asyncio.sleep(1)
                        row = await tool('blender_job_status', {'job_id': row['id']})
                        evidence['jobs'][label] = row
                        save()
                    if row['state'] != expected:
                        if row['state'] == 'failed':
                            evidence['diagnostics'] = await tool('blender_job_diagnostics', {'job_id': row['id']})
                            save()
                        raise AssertionError(row)
                    if expected == 'completed':
                        assert row['manifest']['blender_version'].startswith('5.2.3')
                    return row

                async def fetch(row, name):
                    item = await tool('blender_artifact_fetch', {'job_id': row['id'], 'name': name})
                    content = Path(item['path']).read_bytes()
                    assert hashlib.sha256(content).hexdigest() == item['sha256']
                    if item not in evidence['artifacts']:
                        evidence['artifacts'].append(item)
                    save()
                    return content

                evidence['capabilities'] = await tool('blender_capabilities', {})
                assert evidence['capabilities']['runtime_verified']
                assert evidence['capabilities']['actual_version'] == 'Blender 5.2.3 LTS'
                tools = await session.list_tools()
                assert 'blender_job_diagnostics' in {t.name for t in tools.tools}
                assert len(tools.tools) == 9
                built = await job('author', 'blender_scene_author', {'code': AUTHOR})
                assert json.loads(await fetch(built, 'report.json'))['passed']
                assert (await fetch(built, 'fixture.glb'))[:4] == b'glTF'
                await fetch(built, 'scene.blend')
                await fetch(built, 'scene.json')
                reopened = await job('reopen_roundtrip', 'blender_scene_author', {'code': REOPEN, 'source_job': built['id']})
                assert json.loads(await fetch(reopened, 'report.json'))['passed']
                rendered = await job('cpu_render', 'blender_render', {'source_job': built['id'], 'device': 'CPU',
                                    'frames': [1], 'resolution': [320,240], 'samples': 4})
                assert (await fetch(rendered, 'frame-0001.png')).startswith(b'\x89PNG\r\n\x1a\n')
                denied = await session.call_tool('blender_render', {'source_job': built['id'], 'device': 'CUDA'})
                assert denied.isError
                evidence['gpu_rejected_before_submission'] = True
                failed = await job('intentional_failure_1', 'blender_scene_author',
                                   {'source_job': built['id'], 'code': "raise ValueError('guard fixture 1')"}, expected='failed')
                diagnostics = await tool('blender_job_diagnostics', {'job_id': failed['id']})
                assert 'Blender 5.2.3' in diagnostics['logs']['blender.log']['text']
                evidence['failure_diagnostics'] = diagnostics
                denied = await session.call_tool('blender_scene_author',
                          {'source_job': built['id'], 'code': "# unchanged repair\nraise ValueError('guard fixture 1')\n"})
                assert denied.isError and 'unchanged submission' in str(denied.content)
                evidence['duplicate_failed_code_blocked'] = True
                for n in (2,3):
                    await job(f'intentional_failure_{n}', 'blender_scene_author',
                              {'source_job': built['id'], 'code': f"raise ValueError('guard fixture {n}')"}, expected='failed')
                denied = await session.call_tool('blender_scene_author',
                          {'source_job': built['id'], 'code': "raise ValueError('fourth attempt')"})
                assert denied.isError and 'budget exhausted' in str(denied.content)
                evidence['fourth_failure_attempt_blocked'] = True
                evidence['final_capabilities'] = await tool('blender_capabilities', {})
                assert len(evidence['final_capabilities']['guard']['accepted_jobs']) == 6
                evidence['passed'] = True
                save()
                print(json.dumps({'passed': True, 'evidence': str(EVIDENCE),
                                  'jobs': {k:v['id'] for k,v in evidence['jobs'].items()}}, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
