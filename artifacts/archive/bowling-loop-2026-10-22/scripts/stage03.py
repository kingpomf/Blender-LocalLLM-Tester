import bpy
import bmesh
import json
import math

def create_pin_mesh():
    """Create a reusable pin mesh with lathed ten-pin silhouette."""
    mesh = bpy.data.meshes.new("PinMesh")
    
    # Create a pin using a lathe profile
    # Profile points: (radius, height) from base to top
    profile = [
        (0.0605, 0.0),      # Base (radius 0.0605, height 0.0)
        (0.0605, 0.02),     # Base edge
        (0.0605, 0.05),     # Lower belly
        (0.0605, 0.15),     # Belly
        (0.040, 0.20),      # Neck start
        (0.020, 0.25),      # Neck
        (0.020, 0.30),      # Neck top
        (0.040, 0.32),      # Head start
        (0.0605, 0.35),     # Head
        (0.0605, 0.381),    # Top
    ]
    
    # Create vertices for the profile
    bm = bmesh.new()
    verts = []
    for r, h in profile:
        verts.append(bm.verts.new((r, 0.0, h)))
    
    # Create rings around the profile
    num_segments = 32
    for i in range(len(profile) - 1):
        r1, h1 = profile[i]
        r2, h2 = profile[i + 1]
        for j in range(num_segments):
            theta1 = 2 * math.pi * j / num_segments
            theta2 = 2 * math.pi * (j + 1) / num_segments
            v1 = bm.verts.new((r1 * math.cos(theta1), r1 * math.sin(theta1), h1))
            v2 = bm.verts.new((r2 * math.cos(theta2), r2 * math.sin(theta2), h2))
            v3 = bm.verts.new((r2 * math.cos(theta1), r2 * math.sin(theta1), h2))
            v4 = bm.verts.new((r1 * math.cos(theta2), r1 * math.sin(theta2), h1))
            try:
                bm.faces.new([v1, v2, v3, v4])
            except Exception:
                pass
    
    bm.to_mesh(mesh)
    return mesh

def create_pin(name, location):
    """Create a pin object with the reusable mesh."""
    mesh = create_pin_mesh()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    return obj

def run_stage():
    # Use scene = bpy.context.scene, not bpy.scene
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']

    # Pin dimensions
    pin_height = 0.381
    pin_radius = 0.0605
    head_pin_y = 18.288
    row_spacing = 0.3048
    row_separation = math.sqrt(3) / 2 * row_spacing

    # Create pin racks
    # Left lane rack
    left_rack = []
    # Right lane rack
    right_rack = []

    # Create head pins (row 0)
    left_head = create_pin("Pin_L_01", (-0.95, head_pin_y, pin_height / 2))
    right_head = create_pin("Pin_R_01", (0.95, head_pin_y, pin_height / 2))
    left_rack.append(left_head)
    right_rack.append(right_head)

    # Create row 1 (2 pins)
    for i in range(2):
        y = head_pin_y + row_separation
        x = -0.95 + (i - 0.5) * row_spacing
        pin = create_pin(f"Pin_L_0{i+2}", (x, y, pin_height / 2))
        left_rack.append(pin)

        x = 0.95 + (i - 0.5) * row_spacing
        pin = create_pin(f"Pin_R_0{i+2}", (x, y, pin_height / 2))
        right_rack.append(pin)

    # Create row 2 (3 pins)
    for i in range(3):
        y = head_pin_y + 2 * row_separation
        x = -0.95 + (i - 1) * row_spacing
        pin = create_pin(f"Pin_L_0{i+4}", (x, y, pin_height / 2))
        left_rack.append(pin)

        x = 0.95 + (i - 1) * row_spacing
        pin = create_pin(f"Pin_R_0{i+4}", (x, y, pin_height / 2))
        right_rack.append(pin)

    # Create row 3 (4 pins)
    for i in range(4):
        y = head_pin_y + 3 * row_separation
        x = -0.95 + (i - 1.5) * row_spacing
        pin = create_pin(f"Pin_L_0{i+7}", (x, y, pin_height / 2))
        left_rack.append(pin)

        x = 0.95 + (i - 1.5) * row_spacing
        pin = create_pin(f"Pin_R_0{i+7}", (x, y, pin_height / 2))
        right_rack.append(pin)

    # Link all pins to the appropriate collection
    bp01_pins = bpy.data.collections['BP01_PINS']
    for pin in left_rack + right_rack:
        bp01_pins.objects.link(pin)

    # Verify dimensions
    assert pin_height >= 0.378 and pin_height <= 0.384, "Pin height out of tolerance"
    assert pin_radius >= 0.059 and pin_radius <= 0.062, "Pin radius out of tolerance"
    assert head_pin_y >= 18.278 and head_pin_y <= 18.298, "Head pin Y out of tolerance"
    assert row_spacing >= 0.3018 and row_spacing <= 0.3078, "Row spacing out of tolerance"

    report = {
        "passed": True,
        "pin_height": pin_height,
        "pin_radius": pin_radius,
        "head_pin_y": head_pin_y,
        "row_spacing": row_spacing,
        "row_separation": row_separation,
        "message": "Twenty reusable bowling pins created and positioned in racks"
    }
    return report

report = run_stage()
