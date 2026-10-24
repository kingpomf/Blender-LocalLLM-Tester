"""Fixed selection exports and measured GLB reimports; restores the authored scene."""
import bpy
import re
from mathutils import Matrix

scene=bpy.context.scene
root=bpy.data.objects['BowlingPair01_ROOT']
original_selection=[o for o in scene.objects if o.select_get()]
original_active=bpy.context.view_layer.objects.active
visual=[o for name in ['BP01_STATIC','BP01_PINS','BP01_BALLS'] for o in bpy.data.collections[name].objects if o.type=='MESH']
collision=[o for o in bpy.data.collections['BP01_COLLISION'].objects if o.type=='MESH']

def bounds(objects):
    points=[o.matrix_world@v.co for o in objects for v in o.data.vertices if o.type=='MESH']
    assert points
    return [[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]

def normalize(name):return re.sub(r'\.\d+$','',name)

roundtrips=[]
temporary=[]
try:
    bundles=[('BowlingPair01.glb',visual+[root],'pair'),
             ('BowlingPair01_Collision.glb',collision,'collision')]
    for name,source in [('BowlingPin01',bpy.data.objects['Pin_L_01'])]+[(f'BowlingBall{i:02d}',bpy.data.objects[f'Ball_{i:02d}']) for i in range(1,4)]:
        copy=source.copy();copy.data=source.data;copy.parent=None;copy.matrix_world=Matrix.Identity(4)
        copy.name=name;scene.collection.objects.link(copy);temporary.append(copy)
        bundles.append((name+'.glb',[copy],'pin' if name=='BowlingPin01' else 'ball'))
    for filename,selected,kind in bundles:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected:obj.select_set(True)
        expected=bounds([o for o in selected if o.type=='MESH'])
        result=bpy.ops.export_scene.gltf(filepath='/job/'+filename,export_format='GLB',
            use_selection=True,export_yup=True,export_cameras=False,export_lights=False,
            export_materials='EXPORT',export_extras=True)
        assert 'FINISHED' in result
        existing=set(bpy.data.objects)
        imported=[]
        try:
            bpy.ops.import_scene.gltf(filepath='/job/'+filename)
            imported=[o for o in bpy.data.objects if o not in existing]
            meshes=[o for o in imported if o.type=='MESH']
            actual=bounds(meshes)
            tolerance=.003
            assert all(abs(actual[end][axis]-expected[end][axis])<=tolerance for end in range(2) for axis in range(3)),filename+' round-trip bounds differ'
            names=[normalize(o.name) for o in meshes]
            assert all(o.type not in {'LIGHT','CAMERA'} for o in imported)
            if kind=='pair':
                assert len([n for n in names if n.startswith('Pin_')])==20
                assert len([n for n in names if n.startswith('Ball_')])==3
                assert not any(n.startswith('COL_') for n in names)
                assert len(meshes)==len(visual)
            elif kind=='collision':
                assert len(meshes)==len(collision) and all(n.startswith('COL_') for n in names)
            else:
                assert len(meshes)==1
                center=[(actual[0][i]+actual[1][i])/2 for i in range(3)]
                if kind=='pin':
                    assert abs(actual[0][2])<=.001 and abs(actual[1][2]-.381)<=.003
                    assert max(abs(center[i]) for i in [0,1])<=.001
                else:
                    assert max(abs(v) for v in center)<=.001
                    assert abs(max(actual[1][i]-actual[0][i] for i in range(3))-.216)<=.003
            assert all(any(slot.material for slot in o.material_slots) for o in meshes)
            roundtrips.append({'file':filename,'kind':kind,'passed':True,'expected_bounds':expected,
                              'imported_bounds':actual,'mesh_count':len(meshes),'mesh_names':names})
        finally:
            for obj in imported:bpy.data.objects.remove(obj,do_unlink=True)
finally:
    for obj in temporary:
        if obj.name in bpy.data.objects:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in original_selection:obj.select_set(True)
    bpy.context.view_layer.objects.active=original_active

report={'passed':len(roundtrips)==6,'fixed_export_pipeline':True,'roundtrip_checks':roundtrips,
        'axes':'glTF Y-up export; imported back to Blender Z-up for bounds verification',
        'source_geometry_modified':False}
