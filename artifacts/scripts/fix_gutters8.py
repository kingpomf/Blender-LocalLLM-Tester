import bpy

# Remove existing gutters
for name in list(bpy.data.objects.keys()):
    if name.startswith("Gutter_"):
        obj = bpy.data.objects[name]
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

gutter_width = 0.24
gutter_depth = 0.12
gutter_length = 19.2

def create_gutter(name, x_center):
    # Create a box and remove top face to make open gutter
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_center, gutter_length / 2, -gutter_depth / 2))
    obj = bpy.context.active_object
    obj.name = name
    obj.parent = root
    static_col.objects.link(obj)
    
    # Scale to correct dimensions
    obj.scale.x = gutter_width
    obj.scale.y = gutter_length
    obj.scale.z = gutter_depth
    
    # Apply scale
    bpy.ops.object.transform_apply(scale=True)
    
    # Enter edit mode and remove top face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Select top face (highest Z)
    bpy.ops.mesh.select_face_by_tris()
    
    # Find and select the top face
    import bmesh
    bm = bmesh.from_edit_mesh(obj.data)
    top_face = None
    for f in bm.faces:
        if f.normal.z > 0.5:
            top_face = f
            break
    if top_face:
        top_face.select = True
        bmesh.ops.delete(bm, geom=[top_face], context='FACES')
    
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj

positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}
for name, x in positions.items():
    create_gutter(name, x)

report = {"gutters_created": 4, "box_minus_top": True}