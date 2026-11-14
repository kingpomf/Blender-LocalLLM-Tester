"""GLB round-trip check in isolated job; final source artifacts are never modified.
rev2: compare unique rounded world positions (glTF re-indexes vertices; raw counts
and per-face splits differ legitimately while geometry is identical)."""
import bpy
import os

def descendant_of(obj, root):
    p = obj.parent
    while p:
        if p is root:
            return True
        p = p.parent
    return False

root = bpy.data.objects.get('Kart01_Root')

def capture():
    out = {}
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        ev = obj.evaluated_get(deps)
        data = ev.to_mesh()
        try:
            data.calc_loop_triangles()
            tris = len(data.loop_triangles)
            mw = ev.matrix_world
            pos = set()
            for v in data.vertices:
                w = mw @ v.co
                pos.add((round(w.x, 5), round(w.y, 5), round(w.z, 5)))
        finally:
            ev.to_mesh_clear()
        out[obj.name] = dict(
            unique_positions=len(pos),
            positions=sorted(pos),
            tris=tris,
            mats=[m.name if m else None for m in obj.data.materials],
        )
    return out

expected = capture()
report = dict(expected_meshes=sorted(expected),
              expected_root=bool(root and root.type == 'EMPTY'))

bpy.ops.object.select_all(action='DESELECT')
sel = [root] + [o for o in bpy.data.objects if descendant_of(o, root)]
for o in sel:
    o.select_set(True)
bpy.context.view_layer.objects.active = root
bpy.ops.export_scene.gltf(filepath='/job/Kart01.glb', export_format='GLB',
                          use_selection=True, export_apply=True,
                          export_materials='EXPORT', export_normals=True,
                          export_yup=True)
report['exported_glb_bytes'] = os.path.getsize('/job/Kart01.glb')

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    if m.users == 0:
        bpy.data.meshes.remove(m)
for m in list(bpy.data.materials):
    if m.users == 0:
        bpy.data.materials.remove(m)

bpy.ops.import_scene.gltf(filepath='/job/Kart01.glb')
actual = capture()

names_ok = sorted(actual) == sorted(expected)
report['names_match'] = names_ok
geo = {}
for name in expected:
    if name in actual:
        e, a = expected[name], actual[name]
        geo[name] = dict(
            tris_match=e['tris'] == a['tris'],
            mats_match=e['mats'] == a['mats'],
            position_set_match=e['positions'] == a['positions'],
        )
    else:
        geo[name] = dict(missing=True)
report['geometry'] = geo
report['materials_after'] = sorted(m.name for m in bpy.data.materials)
report['wheel_two_slots'] = sorted(n for n, v in actual.items()
                                   if n.startswith('Kart01_Wheel_') and len(v['mats']) == 2)
forbidden = ('CAM_', 'LIGHT_', 'REF_', 'Kart01_Ground', 'MAT_Ground')
report['presentation_absent'] = not any(
    o.name.startswith(forbidden) for o in bpy.data.objects) and not any(
    m.name.startswith(forbidden) for m in bpy.data.materials)
imported_root = bpy.data.objects.get('Kart01_Root')
report['root_reimported'] = bool(imported_root and imported_root.type == 'EMPTY')
report['geometry_all_match'] = (names_ok and all(
    g.get('tris_match') and g.get('mats_match') and g.get('position_set_match')
    for g in geo.values()))
report['passed'] = bool(report['geometry_all_match'] and report['presentation_absent']
                        and report['root_reimported'] and len(report['wheel_two_slots']) == 4
                        and {'MAT_Kart_Red', 'MAT_Rubber_Dark', 'MAT_Rim_Silver',
                             'MAT_Metal_Dark', 'MAT_Seat_Black'} <= set(report['materials_after']))
