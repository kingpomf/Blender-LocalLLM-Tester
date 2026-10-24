"""Read-only Blender audit; no geometry/material/transform mutation."""
import bpy
import bmesh
from collections import Counter
from math import hypot

scene=bpy.context.scene
depsgraph=bpy.context.evaluated_depsgraph_get()
objects=[]
for obj in sorted(scene.objects,key=lambda o:o.name):
    row={'name':obj.name,'type':obj.type,'parent':obj.parent.name if obj.parent else None,
         'collections':sorted(c.name for c in obj.users_collection),'location':list(obj.location),
         'scale':list(obj.scale),'rotation':list(obj.rotation_euler)}
    if obj.type=='MESH':
        evaluated=obj.evaluated_get(depsgraph)
        mesh=evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            coords=[obj.matrix_world@v.co for v in mesh.vertices]
            row.update(vertices=len(mesh.vertices),faces=len(mesh.polygons),triangles=len(mesh.loop_triangles),
                minimum=[min(v[i] for v in coords) for i in range(3)],
                maximum=[max(v[i] for v in coords) for i in range(3)],
                materials=[m.name if m else None for m in mesh.materials],
                material_face_counts=dict(Counter(str(p.material_index) for p in mesh.polygons)))
            if obj.name=='Pin_L_01':
                bm=bmesh.new()
                bm.from_mesh(mesh)
                row['boundary_edges']=sum(e.is_boundary for e in bm.edges)
                row['nonmanifold_edges']=sum(not e.is_manifold for e in bm.edges)
                bm.free()
                profile={}
                for v in mesh.vertices:
                    z=str(round(v.co.z,6))
                    profile[z]=max(profile.get(z,0),hypot(v.co.x,v.co.y))
                row['profile_max_radius_by_z']=profile
            if obj.name.startswith('Gutter_'):
                row['section_samples_x_z']=sorted({(round(v.x,6),round(v.z,6)) for v in coords})
        finally:
            evaluated.to_mesh_clear()
    objects.append(row)
report={'audit_only':True,'geometry_modified':False,'blender_version':bpy.app.version_string,
        'units':{'system':scene.unit_settings.system,'scale':scene.unit_settings.scale_length},
        'objects':objects,
        'bmesh_operators':{name:hasattr(bmesh.ops,name) for name in
            ['create_uvsphere','extrude_face_only','extrude_region_unshared','extrude_discrete_faces','extrude_face_region']},
        'principled_input_names':sorted({socket.name for material in bpy.data.materials if material.use_nodes and material.node_tree
            for node in material.node_tree.nodes if node.type=='BSDF_PRINCIPLED' for socket in node.inputs})}
