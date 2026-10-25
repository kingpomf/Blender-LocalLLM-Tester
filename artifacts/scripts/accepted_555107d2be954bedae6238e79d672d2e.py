import bpy

# Stage 01: Lane surfaces and approaches
LANE_WIDTH = 1.0668
LANE_LEFT_CENTER_X = -0.95
LANE_RIGHT_CENTER_X = 0.95
APPROACH_LENGTH = 4.572
LANE_LENGTH = 19.20
SURFACE_Z = 0.0
LANE_THICKNESS = 0.05

def create_surface(name, x, y_start, y_end, width, z, thickness):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, y_end - y_start, thickness)
    obj.location = (x, (y_start + y_end) / 2.0, z - thickness / 2.0)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    return obj

lane_l = create_surface('Lane_L_Surface', LANE_LEFT_CENTER_X, 0.0, LANE_LENGTH, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
lane_r = create_surface('Lane_R_Surface', LANE_RIGHT_CENTER_X, 0.0, LANE_LENGTH, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
approach_l = create_surface('Approach_L', LANE_LEFT_CENTER_X, -APPROACH_LENGTH, 0.0, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
approach_r = create_surface('Approach_R', LANE_RIGHT_CENTER_X, -APPROACH_LENGTH, 0.0, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)

static_coll = bpy.data.collections['BP01_STATIC']
for obj in [lane_l, lane_r, approach_l, approach_r]:
    static_coll.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)

report = {
    "stage": "stage01_lanes",
    "objects_created": ["Lane_L_Surface", "Lane_R_Surface", "Approach_L", "Approach_R"],
    "lane_width": LANE_WIDTH,
    "lane_centers_x": [LANE_LEFT_CENTER_X, LANE_RIGHT_CENTER_X],
    "lane_y_range": [0.0, LANE_LENGTH],
    "approach_y_range": [-APPROACH_LENGTH, 0.0],
    "surface_z": SURFACE_Z
}