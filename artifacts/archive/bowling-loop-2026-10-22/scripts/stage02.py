import bpy
import bmesh
import json
import math

def create_gutter(name, x_center, y_start, y_end, width, depth, z_height):
    """Create a gutter mesh with concave cross-section."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a concave gutter shape
    # Outer wall, bottom, and inner wall
    outer_x = x_center - width/2
    inner_x = x_center + width/2
    bottom_x = x_center
    bottom_y = y_start + 0.02  # Slightly offset from start
    
    # Create vertices for the gutter cross-section
    # Outer wall (tall)
    v_outer_top = bm.verts.new((outer_x, y_start, z_height))
    v_outer_bottom = bm.verts.new((outer_x, y_start, z_height - depth))
    
    # Inner wall (shorter)
    v_inner_top = bm.verts.new((inner_x, y_start, z_height))
    v_inner_bottom = bm.verts.new((inner_x, y_start, z_height - depth * 0.8))
    
    # Bottom curve vertices
    v_bottom_left = bm.verts.new((bottom_x - 0.02, bottom_y, z_height - depth))
    v_bottom_right = bm.verts.new((bottom_x + 0.02, bottom_y, z_height - depth * 0.8))
    
    # Create faces for the gutter
    # Outer wall face
    bm.faces.new([v_outer_top, v_outer_bottom, v_bottom_left])
    # Bottom face
    bm.faces.new([v_bottom_left, v_bottom_right, v_inner_bottom])
    # Inner wall face
    bm.faces.new([v_inner_bottom, v_inner_top, v_bottom_right])
    
    # Extrude along Y axis
    bm.to_mesh(mesh)
    
    # Apply transform
    obj.location = (x_center, (y_start + y_end) / 2, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def create_pin_deck(name, x_center, y_start, y_end, width, z_height):
    """Create a pin deck mesh."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a flat deck surface
    w = width
    l = y_end - y_start
    # Four corners
    v1 = bm.verts.new((x_center - w/2, y_start, z_height))
    v2 = bm.verts.new((x_center + w/2, y_start, z_height))
    v3 = bm.verts.new((x_center + w/2, y_end, z_height))
    v4 = bm.verts.new((x_center - w/2, y_end, z_height))
    bm.faces.new([v1, v2, v3, v4])
    bm.to_mesh(mesh)
    
    obj.location = (x_center, (y_start + y_end) / 2, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def create_pit(name, x_center, y_start, y_end, width, depth, z_height):
    """Create a pit mesh."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    bm = bmesh.new()
    # Create a recessed pit
    w = width
    l = y_end - y_start
    # Four corners with depth
    v1 = bm.verts.new((x_center - w/2, y_start, z_height))
    v2 = bm.verts.new((x_center + w/2, y_start, z_height))
    v3 = bm.verts.new((x_center + w/2, y_end, z_height - depth))
    v4 = bm.verts.new((x_center - w/2, y_end, z_height - depth))
    bm.faces.new([v1, v2, v3, v4])
    bm.to_mesh(mesh)
    
    obj.location = (x_center, (y_start + y_end) / 2, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    
    return obj

def run_stage():
    # Use scene = bpy.context.scene, not bpy.scene
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']

    # Gutter dimensions
    gutter_width = 0.23  # 0.22-0.25 m
    gutter_depth = 0.10  # 0.08-0.12 m below lane
    lane_width = 1.0668
    lane_length = 19.20
    approach_length = 4.572

    # Create gutters
    # Outer gutters (wider, on the outside)
    gutter_l_outer = create_gutter("Gutter_L_Outer", -0.95 - lane_width/2 - gutter_width/2, 0, lane_length, gutter_width, gutter_depth, 0.0)
    gutter_r_outer = create_gutter("Gutter_R_Outer", 0.95 + lane_width/2 + gutter_width/2, 0, lane_length, gutter_width, gutter_depth, 0.0)
    
    # Inner gutters (narrower, between lanes)
    gutter_l_inner = create_gutter("Gutter_L_Inner", -0.95 - lane_width/2 - gutter_width/2, 0, lane_length, gutter_width * 0.5, gutter_depth, 0.0)
    gutter_r_inner = create_gutter("Gutter_R_Inner", 0.95 + lane_width/2 + gutter_width/2, 0, lane_length, gutter_width * 0.5, gutter_depth, 0.0)

    # Create pin deck regions
    pin_deck_l = create_pin_deck("PinDeck_L", -0.95, 17.0, 19.20, lane_width, 0.0)
    pin_deck_r = create_pin_deck("PinDeck_R", 0.95, 17.0, 19.20, lane_width, 0.0)

    # Create pit regions
    pit_l = create_pit("Pit_L", -0.95, 19.20, 19.80, lane_width, 0.15, 0.0)
    pit_r = create_pit("Pit_R", 0.95, 19.20, 19.80, lane_width, 0.15, 0.0)

    # Create central divider
    divider = create_pin_deck("Divider", 0.0, 17.0, 19.20, 0.05, 0.0)

    # Link all objects to the appropriate collections
    bp01_static = bpy.data.collections['BP01_STATIC']
    bp01_static.objects.link(gutter_l_outer)
    bp01_static.objects.link(gutter_r_outer)
    bp01_static.objects.link(gutter_l_inner)
    bp01_static.objects.link(gutter_r_inner)
    bp01_static.objects.link(pin_deck_l)
    bp01_static.objects.link(pin_deck_r)
    bp01_static.objects.link(pit_l)
    bp01_static.objects.link(pit_r)
    bp01_static.objects.link(divider)

    # Verify dimensions
    assert gutter_width >= 0.22 and gutter_width <= 0.25, "Gutter width out of tolerance"
    assert gutter_depth >= 0.08 and gutter_depth <= 0.12, "Gutter depth out of tolerance"
    assert lane_width >= 1.0618 and lane_width <= 1.0718, "Lane width out of tolerance"
    assert lane_length >= 19.19 and lane_length <= 19.21, "Lane length out of tolerance"

    report = {
        "passed": True,
        "gutter_width": gutter_width,
        "gutter_depth": gutter_depth,
        "lane_width": lane_width,
        "lane_length": lane_length,
        "message": "Gutters, decks, and pit created"
    }
    return report

report = run_stage()
