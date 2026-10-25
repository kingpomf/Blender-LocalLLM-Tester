import bpy
import math

# Remove existing pins
pins_coll = bpy.data.collections['BP01_PINS']
for obj in list(pins_coll.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Pin segments - cone has base at z=0, tip at z=depth
segments = [
    ('base', 0.047, 0.047, 0.01),
    ('belly', 0.047, 0.0605, 0.08),
    ('body', 0.0605, 0.045, 0.10),
    ('neck', 0.045, 0.020, 0.08),
    ('head', 0.020, 0.035, 0.03),
    ('tip', 0.035, 0.015, 0.05),
    ('top', 0.015, 0.0, 0.031),
]

z = 0.0
parts = []
for name, r_bot, r_top, h in segments:
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r_bot, radius2=r_top, depth=h, calc_uvs=True)
    obj = bpy.context.active_object
    obj.name = f'pin_{name}'
    # Cone base is at z=0 in local space, so location.z = desired base position
    obj.location.z = z
    parts.append(obj)
    z += h

bpy.ops.object.select_all(action='DESELECT')
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

pin = parts[0]
pin.name = 'BowlingPinBase'

# Materials
red_mat = bpy.data.materials.new('PinRedStripe')
red_mat.diffuse_color = (0.8, 0.1, 0.1, 1.0)
white_mat = bpy.data.materials.new('PinWhite')
white_mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)

pin.data.materials.append(white_mat)
pin.data.materials.append(red_mat)

# Assign red to neck region
for face in pin.data.polygons:
    face.material_index = 0
    if 0.21 <= face.center.z <= 0.29:
        face.material_index = 1

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
        pin_obj = pin.copy()
        pin_obj.data = pin.data.copy()
        pin_obj.name = f'Pin_{lane_prefix}_{pin_num:02d}'
        pin_obj.location = (lane_center_x + dx, HEAD_PIN_Y + dy, 0.0)
        bpy.context.scene.collection.objects.link(pin_obj)
        pins_coll.objects.link(pin_obj)

create_rack('L', -0.95)
create_rack('R', 0.95)
bpy.data.objects.remove(pin, do_unlink=True)

report = {
    "stage": "stage03_pins_cylinder_corrected",
    "cone_base_at_origin": True
}