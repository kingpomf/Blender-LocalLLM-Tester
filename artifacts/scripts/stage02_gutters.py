import bpy
import bmesh

LANE_WIDTH = 1.0668
LANE_LEFT_X = -0.95 - LANE_WIDTH / 2.0  # -1.4834
LANE_LEFT_X_R = -0.95 + LANE_WIDTH / 2.0  # -0.4166
LANE_RIGHT_X = 0.95 - LANE_WIDTH / 2.0  # 0.4166
LANE_RIGHT_X_R = 0.95 + LANE_WIDTH / 2.0  # 1.4834
GUTTER_WIDTH = 0.24
GUTTER_DEPTH = 0.10
GUTTER_Y_START = 0.0
GUTTER_Y_END = 19.20

def create_gutter(name, x_center, y_start, y_end, width, depth):
    """Create a U-shaped open gutter with walls."""
    # Create bottom slab
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    w, l = width, y_end - y_start
    obj.scale = (w, l, 0.02)
    obj.location = (x_center, (y_start + y_end) / 2.0, -depth - 0.01)
    bpy.ops.object.transform_apply(scale=True, location=False)
    
    # Left wall
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    lw = bpy.context.active_object
    lw.name = name + '_lw'
    lw.scale = (0.02, l, depth)
    lw.location = (x_center - w/2 + 0.01, (y_start + y_end) / 2.0, -depth/2)
    bpy.ops.object.transform_apply(scale=True, location=False)
    
    # Right wall
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    rw = bpy.context.active_object
    rw.name = name + '_rw'
    rw.scale = (0.02, l, depth)
    rw.location = (x_center + w/2 - 0.01, (y_start + y_end) / 2.0, -depth/2)
    bpy.ops.object.transform_apply(scale=True, location=False)
    
    # Join walls to bottom
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    lw.select_set(True)
    rw.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    
    return obj

# Four gutters
gutter_lo = create_gutter('Gutter_L_Outer', (LANE_LEFT_X - GUTTER_WIDTH/2 - 0.001), GUTTER_Y_START, GUTTER_Y_END, GUTTER_WIDTH, GUTTER_DEPTH)
gutter_li = create_gutter('Gutter_L_Inner', (LANE_LEFT_X_R + GUTTER_WIDTH/2 + 0.001), GUTTER_Y_START, GUTTER_Y_END, GUTTER_WIDTH, GUTTER_DEPTH)
gutter_ri = create_gutter('Gutter_R_Inner', (LANE_RIGHT_X - GUTTER_WIDTH/2 - 0.001), GUTTER_Y_START, GUTTER_Y_END, GUTTER_WIDTH, GUTTER_DEPTH)
gutter_ro = create_gutter('Gutter_R_Outer', (LANE_RIGHT_X_R + GUTTER_WIDTH/2 + 0.001), GUTTER_Y_START, GUTTER_Y_END, GUTTER_WIDTH, GUTTER_DEPTH)

# Pin decks (flat surfaces at rear of each lane)
def create_surface(name, x, y_start, y_end, width, z):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, y_end - y_start, 0.02)
    obj.location = (x, (y_start + y_end) / 2.0, z - 0.01)
    bpy.ops.object.transform_apply(scale=True, location=False)
    return obj

deck_l = create_surface('PinDeck_L', -0.95, 18.5, 19.2, LANE_WIDTH, 0.0)
deck_r = create_surface('PinDeck_R', 0.95, 18.5, 19.2, LANE_WIDTH, 0.0)

# Rear pit (catch area)
pit = create_surface('RearPit', 0.0, 19.2, 19.9, 3.6, -0.3)

# Move all to BP01_STATIC
static_coll = bpy.data.collections['BP01_STATIC']
for obj in [gutter_lo, gutter_li, gutter_ri, gutter_ro, deck_l, deck_r, pit]:
    static_coll.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)

report = {
    "stage": "stage02_gutters",
    "gutters_created": ["Gutter_L_Outer", "Gutter_L_Inner", "Gutter_R_Inner", "Gutter_R_Outer"],
    "decks_created": ["PinDeck_L", "PinDeck_R"],
    "pit_created": "RearPit",
    "gutter_width": GUTTER_WIDTH,
    "gutter_depth": GUTTER_DEPTH
}