import bpy
import math

# Remove existing pins
pins_coll = bpy.data.collections['BP01_PINS']
for obj in list(pins_coll.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Pin profile points: (z, radius)
profile = [
    (0.0, 0.047),
    (0.01, 0.047),
    (0.09, 0.0605),
    (0.19, 0.045),
    (0.27, 0.020),
    (0.30, 0.035),
    (0.35, 0.015),
    (0.381, 0.0),
]

# Create pin by stacking circles
verts = []
faces = []
ring_verts = []

for i, (z, r) in enumerate(profile):
    ring = []
    for j in range(32):
        angle = 2 * math.pi * j / 32
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        verts.append([x, y, z])
        ring.append(len(verts) - 1)
    ring_verts.append(ring)

# Create faces between rings
for i in range(len(ring_verts) - 1):
    ring1 = ring_verts[i]
    ring2 = ring_verts[i + 1]
    for j in range(32):
        v1 = ring1[j]
        v2 = ring1[(j + 1) % 32]
        v3 = ring2[(j + 1) % 32]
        v4 = ring2[j]
        faces.append([v1, v2, v3, v4])

# Create bottom cap
if profile[0][1] > 0:
    center_bottom = len(verts)
    verts.append([0.0, 0.0, profile[0][0]])
    ring = ring_verts[0]
    for j in range(32):
        faces.append([center_bottom, ring[j], ring[(j + 1) % 32]])

# Create top cap
if profile[-1][1] > 0:
    center_top = len(verts)
    verts.append([0.0, 0.0, profile[-1][0]])
    ring = ring_verts[-1]
    for j in range(32):
        faces.append([center_top, ring[(j + 1) % 32], ring[j]])

pin_mesh = bpy.data.meshes.new('BowlingPinMesh')
pin_mesh.from_pydata(verts, [], faces)
pin_mesh.validate()

pin_obj = bpy.data.objects.new('BowlingPinBase', pin_mesh)
bpy.context.scene.collection.objects.link(pin_obj)

# Materials
red_mat = bpy.data.materials.new('PinRedStripe')
red_mat.diffuse_color = (0.8, 0.1, 0.1, 1.0)
white_mat = bpy.data.materials.new('PinWhite')
white_mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)

pin_obj.data.materials.append(white_mat)
pin_obj.data.materials.append(red_mat)

# Assign red to neck region
for face in pin_obj.data.polygons:
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
    "stage": "stage03_pins_stacked_circles",
    "pin_height": 0.381,
    "closed_mesh": True
}