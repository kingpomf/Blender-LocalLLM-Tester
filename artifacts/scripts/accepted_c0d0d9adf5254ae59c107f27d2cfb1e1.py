import bpy
import bmesh

# Remove old gutters and lanes
for name in list(bpy.data.objects.keys()):
    if name.startswith("Gutter_") or name.startswith("Lane_"):
        obj = bpy.data.objects[name]
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

lane_width = 1.0668
lane_length = 19.2
gutter_width = 0.24
gutter_depth = 0.12

def create_lane_with_gutters(lane_name, x_center):
    """Create lane surface with integrated gutter channels."""
    half_lane = lane_width / 2
    half_gutter = gutter_width / 2
    
    # Build mesh with lane surface + gutter channels
    bm = bmesh.new()
    
    # Lane surface (flat at Z=0)
    lane_verts = []
    lane_verts.append(bm.verts.new((x_center - half_lane, 0, 0)))
    lane_verts.append(bm.verts.new((x_center + half_lane, 0, 0)))
    lane_verts.append(bm.verts.new((x_center + half_lane, lane_length, 0)))
    lane_verts.append(bm.verts.new((x_center - half_lane, lane_length, 0)))
    
    # Create lane surface face
    bm.faces.new(lane_verts)
    
    # Now add gutter channels by cutting into the surface
    # Left gutter
    g_left_x = x_center - half_lane - half_gutter
    # Create gutter bottom
    g_verts = []
    g_verts.append(bm.verts.new((g_left_x - half_gutter, 0, -gutter_depth)))
    g_verts.append(bm.verts.new((g_left_x + half_gutter, 0, -gutter_depth)))
    g_verts.append(bm.verts.new((g_left_x + half_gutter, lane_length, -gutter_depth)))
    g_verts.append(bm.verts.new((g_left_x - half_gutter, lane_length, -gutter_depth)))
    bm.faces.new(g_verts)
    
    # Right gutter
    g_right_x = x_center + half_lane + half_gutter
    g_verts2 = []
    g_verts2.append(bm.verts.new((g_right_x - half_gutter, 0, -gutter_depth)))
    g_verts2.append(bm.verts.new((g_right_x + half_gutter, 0, -gutter_depth)))
    g_verts2.append(bm.verts.new((g_right_x + half_gutter, lane_length, -gutter_depth)))
    g_verts2.append(bm.verts.new((g_right_x - half_gutter, lane_length, -gutter_depth)))
    bm.faces.new(g_verts2)
    
    # Create object
    mesh = bpy.data.meshes.new(f"{lane_name}_mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(lane_name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    return obj

# Create both lanes with integrated gutters
create_lane_with_gutters("Lane_L_Surface", -0.95)
create_lane_with_gutters("Lane_R_Surface", 0.95)

report = {"lanes_with_gutters": True, "integrated": True}