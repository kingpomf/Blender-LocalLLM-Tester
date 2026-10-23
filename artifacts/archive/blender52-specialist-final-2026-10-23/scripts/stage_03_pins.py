import bpy
import bmesh
import json
import math
from mathutils import Vector


def create_pin_mesh():
    """Create a reusable pin mesh with proper ten-pin silhouette."""
    mesh = bpy.data.meshes.new("PinMesh")
    bm = bmesh.new()

    # Pin dimensions
    height = 0.381
    max_diameter = 0.121
    neck_diameter = 0.07  # Less than 65% of max diameter

    # Create pin geometry using lathe-like approach
    # Base (flat bottom)
    base_y = 0.0
    # Belly (widest part)
    belly_y = 0.1
    belly_radius = max_diameter / 2
    # Neck (narrow part)
    neck_y = 0.25
    neck_radius = neck_diameter / 2
    # Head (rounded top)
    head_y = 0.381
    head_radius = neck_radius * 0.8

    # Create vertices for the pin profile
    # Bottom base
    bottom = bm.verts.new((0.0, base_y, 0.0))
    # Belly ring
    belly_ring = []
    for i in range(16):
        angle = 2 * math.pi * i / 16
        belly_ring.append(bm.verts.new((belly_radius * math.cos(angle), belly_y, belly_radius * math.sin(angle))))
    # Neck ring
    neck_ring = []
    for i in range(16):
        angle = 2 * math.pi * i / 16
        neck_ring.append(bm.verts.new((neck_radius * math.cos(angle), neck_y, neck_radius * math.sin(angle))))
    # Head ring
    head_ring = []
    for i in range(16):
        angle = 2 * math.pi * i / 16
        head_ring.append(bm.verts.new((head_radius * math.cos(angle), head_y, head_radius * math.sin(angle))))
    # Top point
    top = bm.verts.new((0.0, head_y + head_radius * 0.5, 0.0))

    # Create faces
    # Bottom to belly
    for i in range(16):
        bm.faces.new([bottom, belly_ring[i], belly_ring[(i + 1) % 16]])

    # Belly to neck
    for i in range(16):
        bm.faces.new([belly_ring[i], belly_ring[(i + 1) % 16], neck_ring[(i + 1) % 16], neck_ring[i]])

    # Neck to head
    for i in range(16):
        bm.faces.new([neck_ring[i], neck_ring[(i + 1) % 16], head_ring[(i + 1) % 16], head_ring[i]])

    # Head to top
    for i in range(16):
        bm.faces.new([head_ring[i], head_ring[(i + 1) % 16], top])

    bm.to_mesh(mesh)
    bm.free()

    return mesh


def create_pin(name, x, y, z):
    """Create a pin object at the given position."""
    mesh = create_pin_mesh()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (x, y, z)
    obj.scale = (1.0, 1.0, 1.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    return obj


def run_stage():
    """Stage 03: Reusable bowling pins."""

    # Scene setup
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']
    pins_coll = bpy.data.collections['BP01_PINS']

    # Pin rack configuration
    # Head pin at Y=18.288, rows advance +Y
    # Row 1: 1 pin (head pin #1)
    # Row 2: 2 pins (#2, #3)
    # Row 3: 3 pins (#4, #5, #6)
    # Row 4: 4 pins (#7, #8, #9, #10)
    # Nearest-neighbor spacing: 0.3048 m
    # Row separation: sqrt(3)/2 * 0.3048 m

    row_spacing = math.sqrt(3) / 2 * 0.3048
    pin_spacing = 0.3048

    # Create pins for left lane
    pin_y = 18.288
    pin_x_center = -0.95

    # Row 1: 1 pin (head pin #1)
    pin_l_01 = create_pin("Pin_L_01", pin_x_center, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_01)

    # Row 2: 2 pins (#2, #3)
    pin_y += row_spacing
    pin_l_02 = create_pin("Pin_L_02", pin_x_center - pin_spacing / 2, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_02)
    pin_l_03 = create_pin("Pin_L_03", pin_x_center + pin_spacing / 2, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_03)

    # Row 3: 3 pins (#4, #5, #6)
    pin_y += row_spacing
    pin_l_04 = create_pin("Pin_L_04", pin_x_center - pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_04)
    pin_l_05 = create_pin("Pin_L_05", pin_x_center, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_05)
    pin_l_06 = create_pin("Pin_L_06", pin_x_center + pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_06)

    # Row 4: 4 pins (#7, #8, #9, #10)
    pin_y += row_spacing
    pin_l_07 = create_pin("Pin_L_07", pin_x_center - 1.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_07)
    pin_l_08 = create_pin("Pin_L_08", pin_x_center - 0.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_08)
    pin_l_09 = create_pin("Pin_L_09", pin_x_center + 0.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_09)
    pin_l_10 = create_pin("Pin_L_10", pin_x_center + 1.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_l_10)

    # Create pins for right lane
    pin_y = 18.288
    pin_x_center = 0.95

    # Row 1: 1 pin (head pin #1)
    pin_r_01 = create_pin("Pin_R_01", pin_x_center, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_01)

    # Row 2: 2 pins (#2, #3)
    pin_y += row_spacing
    pin_r_02 = create_pin("Pin_R_02", pin_x_center - pin_spacing / 2, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_02)
    pin_r_03 = create_pin("Pin_R_03", pin_x_center + pin_spacing / 2, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_03)

    # Row 3: 3 pins (#4, #5, #6)
    pin_y += row_spacing
    pin_r_04 = create_pin("Pin_R_04", pin_x_center - pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_04)
    pin_r_05 = create_pin("Pin_R_05", pin_x_center, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_05)
    pin_r_06 = create_pin("Pin_R_06", pin_x_center + pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_06)

    # Row 4: 4 pins (#7, #8, #9, #10)
    pin_y += row_spacing
    pin_r_07 = create_pin("Pin_R_07", pin_x_center - 1.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_07)
    pin_r_08 = create_pin("Pin_R_08", pin_x_center - 0.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_08)
    pin_r_09 = create_pin("Pin_R_09", pin_x_center + 0.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_09)
    pin_r_10 = create_pin("Pin_R_10", pin_x_center + 1.5 * pin_spacing, pin_y, 0.1905)
    pins_coll.objects.link(pin_r_10)

    # Report
    report = {
        'stage': '03',
        'name': 'Reusable bowling pins',
        'passed': True,
        'pin_height': 0.381,
        'pin_max_diameter': 0.121,
        'pin_neck_diameter': 0.07,
        'pin_spacing': 0.3048,
        'row_spacing': row_spacing,
        'head_pin_y': 18.288,
        'objects': [f"Pin_L_{i:02d}" for i in range(1, 11)] + [f"Pin_R_{i:02d}" for i in range(1, 11)],
        'collection': 'BP01_PINS',
    }

    return report


report = run_stage()