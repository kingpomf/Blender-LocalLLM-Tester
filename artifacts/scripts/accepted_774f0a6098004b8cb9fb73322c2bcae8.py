import bpy
import math

# Remove existing pins
pins_coll = bpy.data.collections['BP01_PINS']
for obj in list(pins_coll.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Pin profile
profile_points = [
    (0.0, 0.047),
    (0.01, 0.047),
    (0.09, 0.0605),
    (0.19, 0.045),
    (0.27, 0.020),
    (0.30, 0.035),
    (0.35, 0.015),
    (0.381, 0.0),
]

# Create profile as edge chain
coords = [(r, 0.0, z) for z, r in profile_points]
edge_indices = [(i, i + 1) for i in range(len(profile_points) - 1)]

pin_mesh = bpy.data.meshes.new('BowlingPinMesh')
pin_mesh.from_pydata(coords, edge_indices, [])

pin_obj = bpy.data.objects.new('BowlingPinBase', pin_mesh)
bpy.context.scene.collection.objects.link(pin_obj)
bpy.context.view_layer.objects.active = pin_obj
pin_obj.select_set(True)

# Spin the profile
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.spin(
    steps=32,
    angle=math.radians(360),
    axis=(0.0, 0.0, 1.0),
    use_auto_merge=True,
)

# Fill top and bottom
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.fill()
bpy.ops.object.mode_set(mode='OBJECT')

# Materials
red_mat = bpy.data.materials.new('PinRedStripe')
red_mat.diffuse_color = (0.8, 0.1, 0.1, 1.0)
white_mat = bpy.data.materials.new('PinWhite')
white_mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)

pin_obj.data.materials.append(white_mat)
pin_obj.data.materials.append(red_mat)

# Assign red to neck region - check in edit mode with proper selection
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
# Select faces in the neck region (z between 0.21 and 0.29)
for face in pin_obj.data.polygons:
    if 0.21 <= face.center.z <= 0.29:
        face.select = True
if any(f.select for f in pin_obj.data.polygons):
    bpy.ops.object.material_slot_assign()
bpy.ops.object.mode_set(mode='OBJECT')

# Create pin racks
SPACING = 0.3048
ROW_SPACING = math.sqrt(3) / 2.0 * SPACING
HEAD_PIN_Y = 18.288

def create_rack(lane_prefix, lane_center_x):
    positions = [
        (0.0, 0.0, 1),
        (-SPACING/2, ROW_SPACING, 2),
        (SPACING/2, ROW_SPACING, 3),
        (-SPACING, 2*ROW_SPACING, 4),
        (0.0, 2*ROW_SPACING, 5),
        (SPACING, 2*ROW_SPACING, 6),
        (-1.5*SPACING, 3*ROW_SPACING, 7),
        (-0.5*SPACING, 3*ROW_SPACING, 8),
        (0.5*SPACING, 3*ROW_SPACING, 9),
        (1.5*SPACING, 3*ROW_SPACING, 10),
    ]
    for dx, dy, pin_num in positions:
        pin_copy = pin_obj.copy()
        pin_copy.data = pin_obj.data.copy()
        pin_copy.name = f'Pin_{lane_prefix}_{pin_num:02d}'
        pin_copy.location = (lane_center_x + dx, HEAD_PIN_Y + dy, 0.0)
        bpy.context.scene.collection.objects.link(pin_copy)
        pins_coll.objects.link(pin_copy)

create_rack('L', -0.95)
create_rack('R', 0.95)
bpy.data.objects.remove(pin_obj, do_unlink=True)

report = {
    "stage": "stage03_pins_filled",
    "pin_height": 0.381,
    "closed_mesh": True
}