import bpy
import bmesh

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
    half = gutter_width / 2
    # Create a U-channel with solid walls using bmesh
    # Profile: bottom + 2 walls, extruded along Y
    bm = bmesh.new()
    
    # Bottom face vertices
    v_bl = bm.verts.new((x_center - half, 0, -gutter_depth))
    v_br = bm.verts.new((x_center + half, 0, -gutter_depth))
    # Wall top vertices
    v_tll = bm.verts.new((x_center - half, 0, 0))
    v_tlr = bm.verts.new((x_center - half + 0.01, 0, 0))
    v_trl = bm.verts.new((x_center + half - 0.01, 0, 0))
    v_trr = bm.verts.new((x_center + half, 0, 0))
    
    # Bottom face
    bm.faces.new([v_bl, v_br, v_trl, v_tlr])
    # Left wall face
    bm.faces.new([v_bl, v_tll, v_tlr])
    # Right wall face
    bm.faces.new([v_br, v_trr, v_trl])
    
    # Extrude along Y
    bmesh.ops.extrude_region(bm, geom=bm.faces[:], use_loop=False)
    bmesh.ops.translate(bm, verts=bm.verts[-4:], vec=(0, gutter_length, 0))
    
    # Create mesh from bmesh
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    return obj

positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}
for name, x in positions.items():
    create_gutter(name, x)

report = {"gutters_created": 4, "bmesh_u_channel": True}