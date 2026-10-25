import bpy
import math
import bmesh
from mathutils import Vector

# ============================================================
# Fix Gutter Collision Meshes - recreate with concave U-profile
# Spec: concave cross-section, trough bottom 0.08-0.12m below lane
# ============================================================

def remove_gutter_coll(name):
    """Safely remove old gutter collision object and mesh."""
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(mesh)

def create_gutter_mesh(center_x, width=0.25, trough_depth=0.10, length=19.2):
    """Create concave U-profile gutter mesh using bmesh.
    
    Cross-section: flat lips at Z=0, semicircular trough bottom at Z=-trough_depth.
    """
    bm = bmesh.new()
    half_w = width / 2.0
    
    # Create cross-section vertices along a U-profile
    # Left lip edge → curve down → trough → curve up → right lip edge
    n_curve = 10  # steps along the semicircular portion
    
    # Pre-allocate vertex list: 2 rows × (n_curve + 2) vertices
    # Row 0: Y=0 (front), Row 1: Y=length (back)
    all_verts = []
    
    # Front row (Y=0)
    # Left flat lip vertex
    v0 = bm.verts.new((-half_w, 0, 0))
    all_verts.append(v0)
    
    # Semicircular trough
    for i in range(1, n_curve + 1):
        t = i / n_curve  # 0 to 1
        angle = math.pi * t  # 0 to pi
        # Parameterize semicircle: x = -half_w + half_w*(1-cos(angle)), z = -trough_depth*sin(angle)
        x = -half_w + half_w * (1.0 - math.cos(angle))
        z = -trough_depth * math.sin(angle)
        v = bm.verts.new((x, 0, z))
        all_verts.append(v)
    
    # Right flat lip vertex
    vr = bm.verts.new((half_w, 0, 0))
    all_verts.append(vr)
    
    # Back row (Y=length) - duplicate with offset
    back_verts = []
    for v in all_verts:
        bv = bm.verts.new((v.co.x, length, v.co.z))
        back_verts.append(bv)
    
    # Build faces between front and back rows
    n = len(all_verts)
    for i in range(n - 1):
        fl = all_verts[i]
        fr = all_verts[i + 1]
        bl = back_verts[i]
        br = back_verts[i + 1]
        bm.faces.new((fl, fr, br, bl))
    
    # Create mesh from bmesh
    me = bpy.data.meshes.new("Gutter_Mesh")
    bm.to_mesh(me)
    bm.free()
    
    return me

# Remove old flat collision meshes
for name in ["COL_Gutter_L_Outer", "COL_Gutter_L_Inner",
             "COL_Gutter_R_Inner", "COL_Gutter_R_Outer"]:
    remove_gutter_coll(name)

# Create new gutter collision objects with bmesh
root = bpy.data.objects.get("BowlingPair01_ROOT")
scene = bpy.context.scene

gutter_positions = [
    ("COL_Gutter_L_Outer", -1.608),
    ("COL_Gutter_L_Inner", -0.542),
    ("COL_Gutter_R_Inner", 0.542),
    ("COL_Gutter_R_Outer", 1.608),
]

for name, cx in gutter_positions:
    me = create_gutter_mesh(cx, width=0.25, trough_depth=0.10, length=19.2)
    obj = bpy.data.objects.new(name, me)
    obj.location = Vector((cx, 9.6, 0.0))
    obj.parent = root
    scene.collection.objects.link(obj)
