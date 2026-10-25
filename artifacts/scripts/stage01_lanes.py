import bpy

# Stage 01: Lane surfaces and approaches
# Lane width: 1.0668m, lane centers at X=-0.95 and +0.95
# Lane surfaces: Y=0 to 19.20, approaches: Y=-4.572 to 0

LANE_WIDTH = 1.0668
LANE_LEFT_CENTER_X = -0.95
LANE_RIGHT_CENTER_X = 0.95
APPROACH_LENGTH = 4.572
LANE_LENGTH = 19.20
SURFACE_Z = 0.0
LANE_THICKNESS = 0.05

# Helper to create a flat box
def create_surface(name, x, y_start, y_end, width, z, thickness):
    # Create cube, then scale to dimensions
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    # Scale to dimensions: width(x) x length(y) x thickness(z)
    obj.scale = (width, y_end - y_start, thickness)
    # Position: center of the surface
    obj.location = (x, (y_start + y_end) / 2.0, z - thickness / 2.0)
    # Apply scale so dimensions are exact
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    return obj

# Left lane surface
lane_l = create_surface('Lane_L_Surface', LANE_LEFT_CENTER_X, 0.0, LANE_LENGTH, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
# Right lane surface
lane_r = create_surface('Lane_R_Surface', LANE_RIGHT_CENTER_X, 0.0, LANE_LENGTH, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
# Left approach
approach_l = create_surface('Approach_L', LANE_LEFT_CENTER_X, -APPROACH_LENGTH, 0.0, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)
# Right approach
approach_r = create_surface('Approach_R', LANE_RIGHT_CENTER_X, -APPROACH_LENGTH, 0.0, LANE_WIDTH, SURFACE_Z, LANE_THICKNESS)

# Assign all to BP01_STATIC collection
static_coll = bpy.data.collections['BP01_STATIC']
for obj in [lane_l, lane_r, approach_l, approach_r]:
    # Link to static collection
    static_coll.objects.link(obj)
    # Remove from scene collection
    bpy.context.scene.collection.objects.unlink(obj)

# Measure and report
report = {
    "stage": "stage01_lanes",
    "objects_created": ["Lane_L_Surface", "Lane_R_Surface", "Approach_L", "Approach_R"],
    "lane_width": LANE_WIDTH,
    "lane_centers_x": [LANE_LEFT_CENTER_X, LANE_RIGHT_CENTER_X],
    "lane_y_range": [0.0, LANE_LENGTH],
    "approach_y_range": [-APPROACH_LENGTH, 0.0],
    "surface_z": SURFACE_Z
}