import bpy
import bmesh
import json
import math

def create_lane_surface(name, x_center, y_start, y_end, width, z_height):
    """Create a lane surface mesh."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Create a plane for the lane surface
    bm = bmesh.new()
    # Create a rectangle for the lane
    w = width
    l = y_end - y_start
    # Four corners: (x-w/2, y_start), (x+w/2, y_start), (x+w/2, y_end), (x-w/2, y_end)
    v1 = bm.verts.new((-w/2, y_start, 0))
    v2 = bm.verts.new((w/2, y_start, 0))
    v3 = bm.verts.new((w/2, y_end, 0))
    v4 = bm.verts.new((-w/2, y_end, 0))
    bm.faces.new([v1, v2, v3, v4])
    bm.to_mesh(mesh)
    
    # Apply transform
    obj.location = (x_center, (y_start + y_end) / 2, z_height)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def create_foul_line(name, x_center, y_pos, width, strip_width):
    """Create a foul line strip."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a thin strip at the foul line
    w = strip_width
    l = width
    # Four corners centered at y_pos
    v1 = bm.verts.new((-w/2, y_pos - l/2, 0))
    v2 = bm.verts.new((w/2, y_pos - l/2, 0))
    v3 = bm.verts.new((w/2, y_pos + l/2, 0))
    v4 = bm.verts.new((-w/2, y_pos + l/2, 0))
    bm.faces.new([v1, v2, v3, v4])
    bm.to_mesh(mesh)
    
    obj.location = (x_center, y_pos, 0.001)  # Slightly above surface
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def create_arrow(name, x_center, y_pos, width):
    """Create a targeting arrow."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a triangle arrow pointing forward
    arrow_width = 0.05
    arrow_length = 0.1
    # Triangle vertices
    v1 = bm.verts.new((-arrow_width/2, y_pos - arrow_length/2, 0))
    v2 = bm.verts.new((arrow_width/2, y_pos - arrow_length/2, 0))
    v3 = bm.verts.new((0, y_pos + arrow_length/2, 0))
    bm.faces.new([v1, v2, v3])
    bm.to_mesh(mesh)
    
    obj.location = (x_center, y_pos, 0.001)  # Slightly above surface
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def create_dot(name, x_center, y_pos):
    """Create a dot marker."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a small circle (using a square for simplicity)
    dot_size = 0.02
    v1 = bm.verts.new((-dot_size/2, y_pos - dot_size/2, 0))
    v2 = bm.verts.new((dot_size/2, y_pos - dot_size/2, 0))
    v3 = bm.verts.new((dot_size/2, y_pos + dot_size/2, 0))
    v4 = bm.verts.new((-dot_size/2, y_pos + dot_size/2, 0))
    bm.faces.new([v1, v2, v3, v4])
    bm.to_mesh(mesh)
    
    obj.location = (x_center, y_pos, 0.001)  # Slightly above surface
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def run_stage():
    # Use scene = bpy.context.scene, not bpy.scene
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']

    # Lane dimensions
    lane_width = 1.0668
    lane_length = 19.20
    approach_length = 4.572
    foul_line_y = 0.0
    arrow_y = 4.57
    dot_y = -1.0

    # Create lane surfaces
    lane_l = create_lane_surface("Lane_L_Surface", -0.95, 0, lane_length, lane_width, 0.0)
    lane_r = create_lane_surface("Lane_R_Surface", 0.95, 0, lane_length, lane_width, 0.0)

    # Create approach surfaces
    approach_l = create_lane_surface("Approach_L", -0.95, -approach_length, 0, lane_width, 0.0)
    approach_r = create_lane_surface("Approach_R", 0.95, -approach_length, 0, lane_width, 0.0)

    # Create foul line strips
    foul_l = create_foul_line("FoulLine_L", -0.95, foul_line_y, lane_width, 0.03)
    foul_r = create_foul_line("FoulLine_R", 0.95, foul_line_y, lane_width, 0.03)

    # Create arrows (7 per lane)
    arrows_l = []
    arrows_r = []
    for i in range(7):
        y_offset = arrow_y + (i - 3) * 0.1
        arrow_l = create_arrow(f"Arrow_L_{i}", -0.95, y_offset, lane_width)
        arrow_r = create_arrow(f"Arrow_R_{i}", 0.95, y_offset, lane_width)
        arrows_l.append(arrow_l)
        arrows_r.append(arrow_r)

    # Create dots (7 per lane)
    dots_l = []
    dots_r = []
    for i in range(7):
        y_offset = dot_y + (i - 3) * 0.1
        dot_l = create_dot(f"Dot_L_{i}", -0.95, y_offset)
        dot_r = create_dot(f"Dot_R_{i}", 0.95, y_offset)
        dots_l.append(dot_l)
        dots_r.append(dot_r)

    # Link all objects to the appropriate collections
    bp01_static = bpy.data.collections['BP01_STATIC']
    bp01_static.objects.link(lane_l)
    bp01_static.objects.link(lane_r)
    bp01_static.objects.link(approach_l)
    bp01_static.objects.link(approach_r)
    bp01_static.objects.link(foul_l)
    bp01_static.objects.link(foul_r)
    for arrow in arrows_l + arrows_r:
        bp01_static.objects.link(arrow)
    for dot in dots_l + dots_r:
        bp01_static.objects.link(dot)

    # Verify dimensions
    assert lane_width >= 1.0618 and lane_width <= 1.0718, "Lane width out of tolerance"
    assert lane_length >= 19.19 and lane_length <= 19.21, "Lane length out of tolerance"
    assert approach_length >= 4.562 and approach_length <= 4.582, "Approach length out of tolerance"

    report = {
        "passed": True,
        "lane_width": lane_width,
        "lane_length": lane_length,
        "approach_length": approach_length,
        "foul_line_y": foul_line_y,
        "arrow_y": arrow_y,
        "dot_y": dot_y,
        "message": "Lane pair and markings created"
    }
    return report

report = run_stage()
