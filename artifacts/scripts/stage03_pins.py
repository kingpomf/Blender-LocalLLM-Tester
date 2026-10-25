import bpy
import math

# Create pin profile and spin into 3D shape
def create_pin_mesh():
    # Profile points (x=radius, y=height) for half the pin
    # Pin: height 0.381, max diameter 0.121
    profile_points = [
        (0.047, 0.0),      # base center
        (0.047, 0.005),    # base edge
        (0.055, 0.05),     # lower belly
        (0.0605, 0.10),    # max radius
        (0.058, 0.15),     # body
        (0.045, 0.20),     # tapering
        (0.030, 0.25),     # neck
        (0.035, 0.28),     # neck curve
        (0.040, 0.30),     # head start
        (0.038, 0.32),     # head
        (0.025, 0.35),     # head taper
        (0.005, 0.37),     # head tip
        (0.0, 0.381),      # top center
    ]
    
    # Create curve from profile
    curve_data = bpy.data.curves.new(name="PinProfile", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    spline.points.add(len(profile_points) - 1)
    
    for i, (x, y) in enumerate(profile_points):
        spline.points[i].co = (x, y, 0.0, 1.0)
    
    curve_obj = bpy.data.objects.new("PinProfileCurve", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # Spin modifier to create 3D shape
    modifier = curve_obj.modifiers.new("Spin", 'ARRAY')
    # Actually use spin via mesh conversion
    
    # Convert to mesh
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.convert(target='MESH')
    pin = bpy.context.active_object
    pin.name = "BowlingPinBase"
    
    return pin

# Simpler approach: create pin from a series of cylinders/segments
def create_pin_simple():
    """Create pin from stacked segments."""
    segments = [
        # (name, radius_bottom, radius_top, height)
        ('base', 0.047, 0.047, 0.01),
        ('belly', 0.047, 0.0605, 0.08),
        ('body', 0.0605, 0.045, 0.10),
        ('neck', 0.045, 0.030, 0.07),
        ('head', 0.030, 0.040, 0.04),
        ('tip', 0.040, 0.005, 0.06),
        ('top', 0.005, 0.0, 0.021),
    ]
    
    y = 0.0
    parts = []
    for name, r_bot, r_top, h in segments:
        bpy.ops.mesh.primitive_cone_add(
            vertices=32, radius1=r_bot, radius2=r_top, depth=h,
            calc_uvs=True
        )
        obj = bpy.context.active_object
        obj.name = f'pin_{name}'
        obj.location.y = y + h/2
        parts.append(obj)
        y += h
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for part in parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    
    pin = parts[0]
    pin.name = 'BowlingPinBase'
    # Center at base
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
    return pin

# Create pin mesh
pin = create_pin_simple()

# Create 10 pins for left lane and 10 for right lane
# Standard triangular rack: 1-2-3-4 rows
# Head pin #1 at (lane_center_x, 18.288, 0)
# Row spacing: sqrt(3)/2 * 0.3048 = 0.2639m
# Pin spacing: 0.3048m

import math
SPACING = 0.3048
ROW_SPACING = math.sqrt(3) / 2.0 * SPACING

def create_rack(lane_prefix, lane_center_x):
    """Create 10 pins in triangular rack."""
    pins = []
    
    # Row positions relative to head pin
    # Row 0: pin 1 at (0, 0)
    # Row 1: pins 2,3 at (-spacing/2, row_spacing), (spacing/2, row_spacing)
    # Row 2: pins 4,5,6 at (-spacing, 2*row_spacing), (0, 2*row_spacing), (spacing, 2*row_spacing)
    # Row 3: pins 7,8,9,10 at (-1.5*spacing, 3*row_spacing), ...
    
    positions = []
    # Row 0
    positions.append((0.0, 0.0, 1))
    # Row 1
    positions.append((-SPACING/2, ROW_SPACING, 2))
    positions.append((SPACING/2, ROW_SPACING, 3))
    # Row 2
    positions.append((-SPACING, 2*ROW_SPACING, 4))
    positions.append((0.0, 2*ROW_SPACING, 5))
    positions.append((SPACING, 2*ROW_SPACING, 6))
    # Row 3
    positions.append((-1.5*SPACING, 3*ROW_SPACING, 7))
    positions.append((-0.5*SPACING, 3*ROW_SPACING, 8))
    positions.append((0.5*SPACING, 3*ROW_SPACING, 9))
    positions.append((1.5*SPACING, 3*ROW_SPACING, 10))
    
    head_pin_y = 18.288
    
    for dx, dy, pin_num in positions:
        # Duplicate pin mesh
        pin_obj = pin.copy()
        pin_obj.data = pin.data.copy()
        pin_obj.name = f'Pin_{lane_prefix}_{pin_num:02d}'
        pin_obj.location = (lane_center_x + dx, head_pin_y + dy, 0.0)
        pin_obj.rotation_euler = (0.0, 0.0, 0.0)
        pin_obj.scale = (1.0, 1.0, 1.0)
        
        # Link to scene and pins collection
        bpy.context.scene.collection.objects.link(pin_obj)
        pins_coll = bpy.data.collections['BP01_PINS']
        pins_coll.objects.link(pin_obj)
        
        pins.append(pin_obj)
    
    return pins

# Create racks
left_pins = create_rack('L', -0.95)
right_pins = create_rack('R', 0.95)

# Remove base pin template from scene (keep as linked data for export)
bpy.context.scene.collection.objects.unlink(pin)

report = {
    "stage": "stage03_pins",
    "left_pins": len(left_pins),
    "right_pins": len(right_pins),
    "head_pin_y": 18.288,
    "pin_spacing": SPACING,
    "row_spacing": ROW_SPACING
}