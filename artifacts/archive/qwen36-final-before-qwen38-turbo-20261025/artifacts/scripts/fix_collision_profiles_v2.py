import bpy
import math
import bmesh
from mathutils import Vector

# ============================================================
# Collision-only fix v2: lane widths + gutter concave profiles
# Uses bmesh; open U-profile (no end caps) for gutters
# ============================================================

LANE_HALF_WIDTH = 0.5334
LANE_CENTER_X_L = -0.95
LANE_CENTER_X_R = 0.95
LANE_LENGTH = 19.2
LANE_BED_HEIGHT = 0.02

GUTTER_WIDTH = 0.25
GUTTER_TROUGH_DEPTH = 0.10
GUTTER_LENGTH = 19.2
GUTTER_CENTERS = [-1.608, -0.542, 0.542, 1.608]
GUTTER_NAMES = [
    "COL_Gutter_L_Outer",
    "COL_Gutter_L_Inner",
    "COL_Gutter_R_Inner",
    "COL_Gutter_R_Outer",
]

def remove_coll_obj(name):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        me = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.meshes.remove(me)

def add_coll_obj(name, mesh, loc):
    root = bpy.data.objects.get("BowlingPair01_ROOT")
    scene = bpy.context.scene
    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    if root is not None:
        obj.parent = root
    scene.collection.objects.link(obj)
    return obj

def create_lane_bed(lane_center_x):
    hw = LANE_HALF_WIDTH
    h = LANE_BED_HEIGHT
    half_l = LANE_LENGTH / 2.0
    bm = bmesh.new()
    v_fl = bm.verts.new((lane_center_x - hw, -half_l, 0.0))
    v_fr = bm.verts.new((lane_center_x + hw, -half_l, 0.0))
    v_br = bm.verts.new((lane_center_x + hw,  half_l, 0.0))
    v_bl = bm.verts.new((lane_center_x - hw,  half_l, 0.0))
    v_fl_b = bm.verts.new((lane_center_x - hw, -half_l, -h))
    v_fr_b = bm.verts.new((lane_center_x + hw, -half_l, -h))
    v_br_b = bm.verts.new((lane_center_x + hw,  half_l, -h))
    v_bl_b = bm.verts.new((lane_center_x - hw,  half_l, -h))
    bm.faces.new((v_fl, v_fr, v_br, v_bl))
    bm.faces.new((v_fl_b, v_bl_b, v_br_b, v_fr_b))
    bm.faces.new((v_fl_b, v_fr_b, v_fr, v_fl))
    bm.faces.new((v_bl, v_br, v_br_b, v_bl_b))
    bm.faces.new((v_fr_b, v_br_b, v_br, v_fr))
    bm.faces.new((v_fl, v_bl, v_bl_b, v_fl_b))
    me = bpy.data.meshes.new("COL_LaneBed_Mesh")
    bm.to_mesh(me)
    bm.free()
    me.validate()
    return me

def create_gutter_profile(center_x):
    hw = GUTTER_WIDTH / 2.0
    d = GUTTER_TROUGH_DEPTH
    half_l = GUTTER_LENGTH / 2.0
    n_curve = 12
    bm = bmesh.new()
    front_verts = []
    front_verts.append(bm.verts.new((center_x - hw, -half_l, 0.0)))
    for i in range(1, n_curve + 1):
        t = i / n_curve
        angle = math.pi * t
        x = center_x - hw + hw * (1.0 - math.cos(angle))
        z = -d * math.sin(angle)
        front_verts.append(bm.verts.new((x, -half_l, z)))
    front_verts.append(bm.verts.new((center_x + hw, -half_l, 0.0)))
    back_verts = []
    for v in front_verts:
        back_verts.append(bm.verts.new((v.co.x, half_l, v.co.z)))
    for i in range(len(front_verts) - 1):
        bm.faces.new((front_verts[i], front_verts[i + 1],
                      back_verts[i + 1], back_verts[i]))
    me = bpy.data.meshes.new("COL_Gutter_Mesh")
    bm.to_mesh(me)
    bm.free()
    me.validate()
    return me

# Remove old collision objects
for name in ["COL_LaneBed_L", "COL_LaneBed_R"]:
    remove_coll_obj(name)
for name in GUTTER_NAMES:
    remove_coll_obj(name)

# Create corrected lane beds
me_l = create_lane_bed(LANE_CENTER_X_L)
me_r = create_lane_bed(LANE_CENTER_X_R)
add_coll_obj("COL_LaneBed_L", me_l, (0, 0, 0))
add_coll_obj("COL_LaneBed_R", me_r, (0, 0, 0))

# Create corrected gutter profiles
for name, cx in zip(GUTTER_NAMES, GUTTER_CENTERS):
    me = create_gutter_profile(cx)
    add_coll_obj(name, me, (cx, 9.6, 0.0))

print("Collision v2 fix applied.")
