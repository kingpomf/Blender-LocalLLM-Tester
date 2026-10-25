import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene

    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"

    errors = []

    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']

    # Verify lanes exist (Stage01 repair)
    for r in ('Lane_L_Surface', 'Lane_R_Surface', 'Approach_L', 'Approach_R'):
        assert r in bpy.data.objects, f"Missing: {r}"

    # --- Materials ---
    mat_gutter = bpy.data.materials.new('Mat_Gutter')
    mat_gutter.use_nodes = True
    bg = mat_gutter.node_tree.nodes['Material Output']
    principled = mat_gutter.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)
    principled.inputs['Roughness'].default_value = 0.6
    mat_gutter.node_tree.links.new(principled.outputs['BSDF'], bg.inputs['Surface'])

    mat_pin_deck = bpy.data.materials.new('Mat_PinDeck')
    mat_pin_deck.use_nodes = True
    bg2 = mat_pin_deck.node_tree.nodes['Material Output']
    p2 = mat_pin_deck.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p2.inputs['Base Color'].default_value = (0.70, 0.50, 0.25, 1.0)
    p2.inputs['Roughness'].default_value = 0.5
    mat_pin_deck.node_tree.links.new(p2.outputs['BSDF'], bg2.inputs['Surface'])

    mat_pit = bpy.data.materials.new('Mat_Pit')
    mat_pit.use_nodes = True
    bg3 = mat_pit.node_tree.nodes['Material Output']
    p3 = mat_pit.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p3.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1.0)
    p3.inputs['Roughness'].default_value = 0.8
    mat_pit.node_tree.links.new(p3.outputs['BSDF'], bg3.inputs['Surface'])

    mat_rail = bpy.data.materials.new('Mat_Rail')
    mat_rail.use_nodes = True
    bg4 = mat_rail.node_tree.nodes['Material Output']
    p4 = mat_rail.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p4.inputs['Base Color'].default_value = (0.35, 0.30, 0.25, 1.0)
    p4.inputs['Roughness'].default_value = 0.4
    mat_rail.node_tree.links.new(p4.outputs['BSDF'], bg4.inputs['Surface'])

    gutter_length = 19.20
    gutter_depth = 0.10

    # --- Gutter builder with explicit boundaries ---
    # Left lane: -1.4834 to -0.4166
    # Right lane: 0.4166 to 1.4834
    # Left Outer gutter: X=-1.7334 to X=-1.4834 (0.25m wide)
    # Left Inner gutter: X=-0.6666 to X=-0.4166 (0.25m wide)
    # Right Inner gutter: X=0.4166 to X=0.6666 (0.25m wide)
    # Right Outer gutter: X=1.4834 to X=1.7334 (0.25m wide)

    def make_gutter(name, x_start, x_end, mat):
        """x_start is the lane-facing edge (higher x for left, lower for right)."""
        me = bpy.data.meshes.new(name + '_Mesh')
        # Concave profile: 7 vertices across width
        profile = [
            (x_start, 0.0),
            (x_start + (x_end - x_start)*0.03, -0.02),
            (x_start + (x_end - x_start)*0.15, -0.06),
            ((x_start + x_end)/2, -gutter_depth),
            (x_start + (x_end - x_start)*0.85, -0.06),
            (x_start + (x_end - x_start)*0.97, -0.02),
            (x_end, 0.002),
        ]
        y_start, y_end = 0.0, gutter_length
        y_segments = 20
        dy = (y_end - y_start) / y_segments
        verts = []
        faces = []
        for s in range(y_segments + 1):
            y = y_start + s * dy
            for px, pz in profile:
                verts.append((px, y, pz))
        nv = len(profile)
        for s in range(y_segments):
            for v in range(nv - 1):
                a = s * nv + v
                b = a + 1
                c = (s + 1) * nv + v + 1
                d = (s + 1) * nv + v
                faces.append((a, b, c, d))
        me.from_pydata(verts, [], faces)
        me.validate()
        obj = bpy.data.objects.new(name, me)
        obj.location = (0, 0, 0)
        if mat:
            me.materials.append(mat)
        obj.parent = root
        static_col.objects.link(obj)
        return obj

    # Remove old gutters
    for existing in static_col.objects[:]:
        if existing.name.startswith('Gutter_'):
            static_col.objects.unlink(existing)
            bpy.data.objects.remove(existing)

    # Create gutters with EXPLICIT boundaries
    # Left Outer: lane faces right at -1.4834, gutter extends left to -1.7334
    make_gutter('Gutter_L_Outer', -1.4834, -1.7334, mat_gutter)
    # Left Inner: lane faces left at -0.4166, gutter extends left to -0.6666
    make_gutter('Gutter_L_Inner', -0.4166, -0.6666, mat_gutter)
    # Right Inner: lane faces right at 0.4166, gutter extends right to 0.6666
    make_gutter('Gutter_R_Inner', 0.4166, 0.6666, mat_gutter)
    # Right Outer: lane faces left at 1.4834, gutter extends right to 1.7334
    make_gutter('Gutter_R_Outer', 1.4834, 1.7334, mat_gutter)

    # --- Central divider ---
    divider_width = 0.03
    divider_height = 0.02
    me_div = bpy.data.meshes.new('Divider_Cap_Mesh')
    obj_div = bpy.data.objects.new('Divider_Cap', me_div)
    div_verts = [
        (-divider_width/2, 0, 0), (divider_width/2, 0, 0),
        (divider_width/2, gutter_length, 0),
        (-divider_width/2, gutter_length, 0),
        (-divider_width/2, 0, -divider_height),
        (divider_width/2, 0, -divider_height),
        (divider_width/2, gutter_length, -divider_height),
        (-divider_width/2, gutter_length, -divider_height),
    ]
    div_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
    me_div.from_pydata(div_verts, [], div_faces)
    me_div.validate()
    me_div.materials.append(mat_gutter)
    obj_div.location = (0, 0, 0)
    obj_div.parent = root
    static_col.objects.link(obj_div)

    # --- Pin decks ---
    pin_deck_y_start = 18.0
    pin_deck_length = 1.20
    for pname, px in [('PinDeck_L', -0.95), ('PinDeck_R', 0.95)]:
        me_pd = bpy.data.meshes.new(pname + '_Mesh')
        obj_pd = bpy.data.objects.new(pname, me_pd)
        hw = 0.60
        pd_verts = [
            (px - hw, pin_deck_y_start, 0.001),
            (px + hw, pin_deck_y_start, 0.001),
            (px + hw, pin_deck_y_start + pin_deck_length, 0.001),
            (px - hw, pin_deck_y_start + pin_deck_length, 0.001),
        ]
        me_pd.from_pydata(pd_verts, [], [(0, 1, 2, 3)])
        me_pd.validate()
        me_pd.materials.append(mat_pin_deck)
        obj_pd.location = (0, 0, 0)
        obj_pd.parent = root
        static_col.objects.link(obj_pd)

    # --- Pit ---
    pit_start_y = 19.20
    pit_length = 0.80
    pit_width = 3.6
    me_pit = bpy.data.meshes.new('Pit_Catch_Mesh')
    obj_pit = bpy.data.objects.new('Pit_Catch', me_pit)
    pv = [
        (-pit_width/2, pit_start_y, -0.15), (pit_width/2, pit_start_y, -0.15),
        (pit_width/2, pit_start_y + pit_length, -0.15),
        (-pit_width/2, pit_start_y + pit_length, -0.15),
        (-pit_width/2, pit_start_y, -0.30), (pit_width/2, pit_start_y, -0.30),
        (pit_width/2, pit_start_y + pit_length, -0.30),
        (-pit_width/2, pit_start_y + pit_length, -0.30),
    ]
    pf = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
    me_pit.from_pydata(pv, [], pf)
    me_pit.validate()
    me_pit.materials.append(mat_pit)
    obj_pit.location = (0, 0, 0)
    obj_pit.parent = root
    static_col.objects.link(obj_pit)

    # --- Outer rails ---
    rail_width = 0.05
    rail_height = 0.08
    rail_y = -0.5
    rail_length = 20.0
    for rx, rname in [(-1.7334 - 0.01, 'OuterRail_L'), (1.7334 + 0.01, 'OuterRail_R')]:
        me_rail = bpy.data.meshes.new(rname + '_Mesh')
        obj_rail = bpy.data.objects.new(rname, me_rail)
        rv = [
            (rx - rail_width/2, rail_y, 0), (rx + rail_width/2, rail_y, 0),
            (rx + rail_width/2, rail_y + rail_length, 0),
            (rx - rail_width/2, rail_y + rail_length, 0),
            (rx - rail_width/2, rail_y, -rail_height),
            (rx + rail_width/2, rail_y, -rail_height),
            (rx + rail_width/2, rail_y + rail_length, -rail_height),
            (rx - rail_width/2, rail_y + rail_length, -rail_height),
        ]
        rf = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        me_rail.from_pydata(rv, [], rf)
        me_rail.validate()
        me_rail.materials.append(mat_rail)
        obj_rail.location = (0, 0, 0)
        obj_rail.parent = root
        static_col.objects.link(obj_rail)

    # --- Verification ---
    gutter_objs = [o for o in static_col.objects if o.name.startswith('Gutter_')]
    if len(gutter_objs) != 4:
        errors.append(f"Expected 4 gutters, got {len(gutter_objs)}")

    # Check gutter widths
    for go in gutter_objs:
        w = go.dimensions.x
        if abs(w - 0.25) > 0.005:
            errors.append(f"{go.name} width {w:.4f} not within 0.22-0.25")

    # Check left outer gutter X extent
    lo_gutter = [o for o in gutter_objs if o.name == 'Gutter_L_Outer'][0]
    bounds_x = [max(v.co.x for v in lo_gutter.data.vertices), min(v.co.x for v in lo_gutter.data.vertices)]
    if bounds_x[1] < -1.80:
        errors.append(f"Gutter_L_Outer extends to X={bounds_x[1]:.4f} outside envelope")

    # Other checks
    divider_exists = 'Divider_Cap' in [o.name for o in static_col.objects]
    if not divider_exists:
        errors.append("Missing Divider_Cap")

    pin_decks = [o for o in static_col.objects if o.name.startswith('PinDeck_')]
    if len(pin_decks) != 2:
        errors.append(f"Expected 2 pin decks, got {len(pin_decks)}")

    pit_exists = 'Pit_Catch' in [o.name for o in static_col.objects]
    if not pit_exists:
        errors.append("Missing Pit_Catch")

    rails = [o for o in static_col.objects if o.name.startswith('OuterRail_')]
    if len(rails) != 2:
        errors.append(f"Expected 2 outer rails, got {len(rails)}")

    for go in gutter_objs:
        if abs(go.dimensions.y - gutter_length) > 0.02:
            errors.append(f"{go.name} gutter Y length {go.dimensions.y} != {gutter_length}")

    for o in static_col.objects:
        if o.parent != root:
            errors.append(f"{o.name} not parented to root")

    passed = len(errors) == 0

    report = {
        "stage": "02",
        "name": "Gutters, decks and pit (repaired)",
        "passed": passed,
        "gutter_count": len(gutter_objs),
        "pin_deck_count": len(pin_decks),
        "has_divider": divider_exists,
        "has_pit": pit_exists,
        "rail_count": len(rails),
        "total_objects": len(static_col.objects),
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for col_name in required_names:
            col = bpy.data.collections[col_name]
            for o in col.objects:
                obj_list.append({
                    'name': o.name,
                    'type': o.type,
                    'location': [round(x, 6) for x in o.location],
                    'parent': o.parent.name if o.parent else None,
                    'collection': col_name,
                })
        scene_info = {
            'objects': obj_list,
            'collections': [c.name for c in bpy.data.collections],
        }
        json.dump(scene_info, f, indent=2)

    return report

report = run_stage()
