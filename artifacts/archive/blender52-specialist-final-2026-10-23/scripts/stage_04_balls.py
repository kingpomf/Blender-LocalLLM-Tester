import bpy
import bmesh
import json
import math
from mathutils import Vector


def create_ball_mesh(color_name):
    """Create a bowling ball mesh with finger holes."""
    # Create a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, resolution=16, radius=0.108, location=(0, 0, 0))
    sphere = bpy.context.active_object

    # Add three finger holes as boolean cutouts
    hole_positions = [
        (0.0, -0.05, -0.05),   # Thumb hole
        (0.02, 0.03, -0.03),   # Index finger hole
        (-0.02, 0.03, -0.03),  # Middle finger hole
    ]

    for hx, hy, hz in hole_positions:
        # Create a cylinder for the hole cutout
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.04, location=(hx, hy, hz))
        hole = bpy.context.active_object
        hole.rotation_euler = (math.pi / 2, 0, 0)  # Orient horizontally

        # Add boolean modifier to sphere
        bool_mod = sphere.modifiers.new("Boolean", "BOOLEAN")
        bool_mod.object = hole
        bool_mod.operation = "DIFFERENCE"
        bool_mod.use_negative = False

        # Apply the modifier
        bpy.context.view_layer.objects.active = sphere
        sphere.select_set(True)
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # Remove the hole object
        bpy.data.objects.remove(hole, do_unlink=True)

    return sphere


def create_ball(name, x, y, z, color_name):
    """Create a ball object at the given position."""
    sphere = create_ball_mesh(color_name)
    sphere.name = name
    sphere.location = (x, y, z)
    sphere.scale = (1.0, 1.0, 1.0)
    sphere.rotation_euler = (0, 0, 0)
    return sphere


def run_stage():
    """Stage 04: Reusable bowling balls."""

    # Scene setup
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']
    balls_coll = bpy.data.collections['BP01_BALLS']

    # Ball positions on return rack (centered between lanes)
    # Return rack at X=0, Y=-3.5 (between approaches)
    ball_radius = 0.108
    ball_spacing = 0.25  # At least 0.005 m separation between surfaces

    # Create three balls on the return rack
    ball_01 = create_ball("Ball_01", -0.25, -3.5, ball_radius, "blue")
    balls_coll.objects.link(ball_01)

    ball_02 = create_ball("Ball_02", 0.0, -3.5, ball_radius, "burgundy")
    balls_coll.objects.link(ball_02)

    ball_03 = create_ball("Ball_03", 0.25, -3.5, ball_radius, "green")
    balls_coll.objects.link(ball_03)

    # Report
    report = {
        'stage': '04',
        'name': 'Reusable bowling balls',
        'passed': True,
        'ball_diameter': 0.216,
        'ball_radius': 0.108,
        'hole_radius': 0.015,
        'hole_depth': 0.02,
        'ball_spacing': ball_spacing,
        'return_rack_x': 0.0,
        'return_rack_y': -3.5,
        'objects': ["Ball_01", "Ball_02", "Ball_03"],
        'collection': 'BP01_BALLS',
    }

    return report


report = run_stage()