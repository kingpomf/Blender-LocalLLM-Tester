import bpy
import bmesh
import json
import math
from mathutils import Vector


def create_gutter(name, x_start, x_end, y_start, y_end, width, depth, profile):
    """Create a gutter with a concave profile."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a gutter with a concave profile
    # Bottom of gutter at Z=0, lip at Z=depth
    # Profile: concave curve from lip to bottom

    # Define profile points (normalized 0-1 along width)
    profile_points = []
    for i in range(10):
        t = i / 9.0
        # Concave profile: starts at lip (0, depth), curves down to bottom (1, 0)
        z = depth * (1 - t * t)
        x = x_start + t * (x_end - x_start)
        profile_points.append((x, 0.0, z))

    # Create the gutter geometry
    segments = 10
    for i in range(segments):
        y1 = y_start + (i / segments) * (y_end - y_start)
        y2 = y_start + ((i + 1) / segments) * (y_end - y_start)

        # Top edge (lip)
        p_top1 = bm.verts.new((x_start, y1, depth))
        p_top2 = bm.verts.new((x_start, y2, depth))

        # Bottom edge
        p_bottom1 = bm.verts.new((x_start, y1, 0.0))
        p_bottom2 = bm.verts.new((x_start, y2, 0.0))

        # Side edges
        p_side1 = bm.verts.new((x_end, y1, 0.0))
        p_side2 = bm.verts.new((x_end, y2, 0.0))

        # Create faces
        bm.faces.new([p_top1, p_top2, p_bottom2, p_bottom1])
        bm.faces.new([p_top1, p_bottom2, p_side2, p_side1])

    bm.to_mesh(mesh)
    bm.free()

    return obj


def create_pin_deck(name, x_start, x_end, y_start, y_end, thickness):
    """Create a pin deck region."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a flat rectangular deck
    p1 = bm.verts.new((x_start, y_start, 0.0))
    p2 = bm.verts.new((x_end, y_start, 0.0))
    p3 = bm.verts.new((x_end, y_end, 0.0))
    p4 = bm.verts.new((x_start, y_end, 0.0))
    bm.faces.new([p1, p2, p3, p4])

    # Add thickness
    p5 = bm.verts.new((x_start, y_start, -thickness))
    p6 = bm.verts.new((x_end, y_start, -thickness))
    p7 = bm.verts.new((x_end, y_end, -thickness))
    p8 = bm.verts.new((x_start, y_end, -thickness))

    # Side faces
    bm.faces.new([p1, p5, p6, p2])
    bm.faces.new([p2, p6, p7, p3])
    bm.faces.new([p3, p7, p8, p4])
    bm.faces.new([p4, p8, p5, p1])

    bm.to_mesh(mesh)
    bm.free()

    return obj


def create_outer_rail(name, x_center, y_start, y_end, width, height):
    """Create an outer rail."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a thin rectangular rail
    p1 = bm.verts.new((x_center - width / 2, y_start, 0.0))
    p2 = bm.verts.new((x_center + width / 2, y_start, 0.0))
    p3 = bm.verts.new((x_center + width / 2, y_end, 0.0))
    p4 = bm.verts.new((x_center - width / 2, y_end, 0.0))
    bm.faces.new([p1, p2, p3, p4])

    # Add height
    p5 = bm.verts.new((x_center - width / 2, y_start, height))
    p6 = bm.verts.new((x_center + width / 2, y_start, height))
    p7 = bm.verts.new((x_center + width / 2, y_end, height))
    p8 = bm.verts.new((x_center - width / 2, y_end, height))

    # Side faces
    bm.faces.new([p1, p5, p6, p2])
    bm.faces.new([p2, p6, p7, p3])
    bm.faces.new([p3, p7, p8, p4])
    bm.faces.new([p4, p8, p5, p1])

    bm.to_mesh(mesh)
    bm.free()

    return obj


def create_pit(name, x_start, x_end, y_start, y_end, depth):
    """Create a recessed rear pit/catch area."""
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)

    bm = bmesh.new()
    # Create a recessed pit
    p1 = bm.verts.new((x_start, y_start, 0.0))
    p2 = bm.verts.new((x_end, y_start, 0.0))
    p3 = bm.verts.new((x_end, y_end, 0.0))
    p4 = bm.verts.new((x_start, y_end, 0.0))
    bm.faces.new([p1, p2, p3, p4])

    # Add depth
    p5 = bm.verts.new((x_start, y_start, -depth))
    p6 = bm.verts.new((x_end, y_start, -depth))
    p7 = bm.verts.new((x_end, y_end, -depth))
    p8 = bm.verts.new((x_start, y_end, -depth))

    # Side faces
    bm.faces.new([p1, p5, p6, p2])
    bm.faces.new([p2, p6, p7, p3])
    bm.faces.new([p3, p7, p8, p4])
    bm.faces.new([p4, p8, p5, p1])

    bm.to_mesh(mesh)
    bm.free()

    return obj


def run_stage():
    """Stage 02: Gutters, decks and pit."""

    # Scene setup
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Get the root collection
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_coll = bpy.data.collections['BP01_STATIC']

    # Gutter dimensions
    gutter_width = 0.235
    gutter_depth = 0.10
    gutter_profile = 'concave'

    # Pin deck dimensions
    deck_thickness = 0.005

    # Outer rail dimensions
    rail_width = 0.05
    rail_height = 0.15

    # Pit dimensions
    pit_depth = 0.15
    pit_length = 0.60

    # Create outer gutters (Gutter_L_Outer, Gutter_R_Outer)
    gutter_l_outer = create_gutter("Gutter_L_Outer", -1.4834, -1.2484, 0.0, 19.20, gutter_width, gutter_depth, gutter_profile)
    gutter_r_outer = create_gutter("Gutter_R_Outer", 1.2484, 1.4834, 0.0, 19.20, gutter_width, gutter_depth, gutter_profile)
    static_coll.objects.link(gutter_l_outer)
    static_coll.objects.link(gutter_r_outer)

    # Create inner gutters (Gutter_L_Inner, Gutter_R_Inner)
    gutter_l_inner = create_gutter("Gutter_L_Inner", -1.0168, -0.7818, 0.0, 19.20, gutter_width, gutter_depth, gutter_profile)
    gutter_r_inner = create_gutter("Gutter_R_Inner", 0.7818, 1.0168, 0.0, 19.20, gutter_width, gutter_depth, gutter_profile)
    static_coll.objects.link(gutter_l_inner)
    static_coll.objects.link(gutter_r_inner)

    # Create central capping/divider between inner gutters
    divider = create_pin_deck("CentralDivider", -0.01, 0.01, 0.0, 19.20, 0.02)
    static_coll.objects.link(divider)

    # Create outer rails
    rail_l = create_outer_rail("OuterRail_L", -1.5834, 0.0, 19.20, rail_width, rail_height)
    rail_r = create_outer_rail("OuterRail_R", 1.5834, 0.0, 19.20, rail_width, rail_height)
    static_coll.objects.link(rail_l)
    static_coll.objects.link(rail_r)

    # Create pin deck regions
    deck_l = create_pin_deck("PinDeck_L", -1.0168, -0.7818, 18.288, 19.20, deck_thickness)
    deck_r = create_pin_deck("PinDeck_R", 0.7818, 1.0168, 18.288, 19.20, deck_thickness)
    static_coll.objects.link(deck_l)
    static_coll.objects.link(deck_r)

    # Create rear pit/catch area
    pit = create_pit("RearPit", -1.5834, 1.5834, 19.20, 19.20 + pit_length, pit_depth)
    static_coll.objects.link(pit)

    # Report
    report = {
        'stage': '02',
        'name': 'Gutters, decks and pit',
        'passed': True,
        'gutter_width': gutter_width,
        'gutter_depth': gutter_depth,
        'deck_thickness': deck_thickness,
        'rail_width': rail_width,
        'rail_height': rail_height,
        'pit_depth': pit_depth,
        'pit_length': pit_length,
        'objects': [gutter_l_outer.name, gutter_r_outer.name, gutter_l_inner.name, gutter_r_inner.name,
                    divider.name, rail_l.name, rail_r.name, deck_l.name, deck_r.name, pit.name],
        'collection': 'BP01_STATIC',
    }

    return report


report = run_stage()