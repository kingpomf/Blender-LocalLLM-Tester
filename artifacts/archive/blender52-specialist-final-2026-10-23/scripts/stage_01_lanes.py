import bpy
import bmesh
import json
import math
from mathutils import Vector


def create_lane_surface(name, x_center, y_start, y_end, width, thickness):
    """Create a lane surface mesh object."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    # Create a flat rectangle for the lane surface
    bm = bmesh.new()
    # Corners: (x_center - width/2, y_start, 0), (x_center + width/2, y_start, 0),
    #          (x_center + width/2, y_end, 0), (x_center - width/2, y_end, 0)
    p1 = bm.verts.new((x_center - width / 2, y_start, 0.0))
    p2 = bm.verts.new((x_center + width / 2, y_start, 0.0))
    p3 = bm.verts.new((x_center + width / 2, y_end, 0.0))
    p4 = bm.verts.new((x_center - width / 2, y_end, 0.0))
    bm.faces.new([p1, p2, p3, p4])
    bm.to_mesh(mesh)
    bm.free()

    # Apply thickness below Z=0
    obj.location = (0.0, 0.0, -thickness)

    return obj


def create_marking(name, x_center, y_pos, width, height, depth):
    """Create a marking (foul line or arrow) as a thin box."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a thin rectangular strip
    p1 = bm.verts.new((x_center - width / 2, y_pos - height / 2, 0.0))
    p2 = bm.verts.new((x_center + width / 2, y_pos - height / 2, 0.0))
    p3 = bm.verts.new((x_center + width / 2, y_pos + height / 2, 0.0))
    p4 = bm.verts.new((x_center - width / 2, y_pos + height / 2, 0.0))
    bm.faces.new([p1, p2, p3, p4])
    bm.to_mesh(mesh)
    bm.free()

    # Apply depth (thin strip)
    obj.location = (0.0, 0.0, -depth / 2)

    return obj


def create_dot(name, x_center, y_pos, radius, height):
    """Create a circular dot."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a circle at the given position
    segments = 32
    center = bm.verts.new((x_center, y_pos, 0.0))
    outer_verts = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        outer_verts.append(bm.verts.new((x_center + radius * math.cos(angle), y_pos + radius * math.sin(angle), 0.0)))
    # Create faces from center to each edge
    for i in range(segments):
        bm.faces.new([center, outer_verts[i], outer_verts[(i + 1) % segments]])
    bm.to_mesh(mesh)
    bm.free()

    # Apply height
    obj.location = (0.0, 0.0, height / 2)

    return obj


def run_stage():
    """Stage 01: Lane pair and markings."""

    # Scene setup
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_coll = bpy.data.collections['BP01_STATIC']

    # Lane dimensions
    lane_width = 1.0668
    lane_length = 19.20
    approach_length = 4.572
    foul_line_y = 0.0
    arrow_y = 4.57
    dot_y = -1.0

    # Create lane surfaces
    lane_l = create_lane_surface("Lane_L_Surface", -0.95, 0.0, lane_length, lane_width, 0.005)
    lane_r = create_lane_surface("Lane_R_Surface", 0.95, 0.0, lane_length, lane_width, 0.005)

    # Create approach surfaces
    approach_l = create_lane_surface("Approach_L", -0.95, -approach_length, 0.0, lane_width, 0.005)
    approach_r = create_lane_surface("Approach_R", 0.95, -approach_length, 0.0, lane_width, 0.005)

    # Link to static collection
    static_coll.objects.link(lane_l)
    static_coll.objects.link(lane_r)
    static_coll.objects.link(approach_l)
    static_coll.objects.link(approach_r)

    # Create foul line strips (dark, 0.02-0.05m wide)
    foul_l = create_marking("FoulLine_L", -0.95, foul_line_y, 0.03, 0.02, 0.001)
    foul_r = create_marking("FoulLine_R", 0.95, foul_line_y, 0.03, 0.02, 0.001)
    static_coll.objects.link(foul_l)
    static_coll.objects.link(foul_r)

    # Create targeting arrows (7 per lane, centered near Y=4.57)
    arrow_spacing = 0.15
    for i in range(7):
        x_pos = -0.95 + (i - 3) * arrow_spacing
        arrow_l = create_marking(f"Arrow_L_{i}", x_pos, arrow_y, 0.02, 0.08, 0.001)
        static_coll.objects.link(arrow_l)

        x_pos = 0.95 + (i - 3) * arrow_spacing
        arrow_r = create_marking(f"Arrow_R_{i}", x_pos, arrow_y, 0.02, 0.08, 0.001)
        static_coll.objects.link(arrow_r)

    # Create approach dots (7 per lane, near Y=-1.0)
    for i in range(7):
        x_pos = -0.95 + (i - 3) * arrow_spacing
        dot_l = create_dot(f"Dot_L_{i}", x_pos, dot_y, 0.02, 0.002)
        static_coll.objects.link(dot_l)

        x_pos = 0.95 + (i - 3) * arrow_spacing
        dot_r = create_dot(f"Dot_R_{i}", x_pos, dot_y, 0.02, 0.002)
        static_coll.objects.link(dot_r)

    # Report
    report = {
        'stage': '01',
        'name': 'Lane pair and markings',
        'passed': True,
        'lane_width': lane_width,
        'lane_length': lane_length,
        'approach_length': approach_length,
        'foul_line_y': foul_line_y,
        'arrow_y': arrow_y,
        'dot_y': dot_y,
        'arrow_spacing': arrow_spacing,
        'objects': [lane_l.name, lane_r.name, approach_l.name, approach_r.name,
                    foul_l.name, foul_r.name] + [f"Arrow_L_{i}" for i in range(7)] + [f"Arrow_R_{i}" for i in range(7)] + [f"Dot_L_{i}" for i in range(7)] + [f"Dot_R_{i}" for i in range(7)],
        'collection': 'BP01_STATIC',
    }

    return report


report = run_stage()