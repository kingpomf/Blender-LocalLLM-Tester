import bpy
import math

# Remove existing pins
pins_coll = bpy.data.collections['BP01_PINS']
for obj in list(pins_coll.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create pin from stacked cone segments, oriented along Z (up)
segments = [
    ('base', 0.047, 0.047, 0.01),
    ('belly', 0.047, 0.0605, 0.08),
    ('body', 0.0605, 0.045, 0.10),
    ('neck', 0.045, 0.030, 0.07),
    ('head', 0.030, 0.040, 0.04),
    ('tip', 0.040, 0.005, 0.06),
    ('top', 0.005, 0.0, 0.021),
]

z = 0.0
parts = []
for name, r_bot, r_top, h in segments:
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=r_bot, radius2=r_top, depth=h, calc_uvs=True)
    obj = bpy.context.active_object
    obj.name = f'pin_{name}'
    obj.location.z = z + h/2
    parts.append(obj)
    z += h

bpy.ops.object.select_all(action='DESELECT')
for part in parts:
    part.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

pin = parts[0]
pin.name = 'BowlingPinBase'
# Set origin to base center
pin.location = (0, 0, 0)

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

# Remove template
bpy.data.objects.remove(pin, do_unlink=True)

report = {
    "stage": "stage03_pins_fixed",
    "pins_per_lane": 10,
    "head_pin_y": HEAD_PIN_Y,
    "pin_height": sum(s[3] for s in segments)
}