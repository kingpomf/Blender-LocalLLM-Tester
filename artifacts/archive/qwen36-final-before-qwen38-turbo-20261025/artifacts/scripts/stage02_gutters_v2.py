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

    # Materials
    def make_mat(name, color, rough=0.5):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bg = mat.node_tree.nodes['Material Output']
        p = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = rough
        mat.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])
        return mat

    mat_gutter = make_mat('Mat_Gutter', (0.15, 0.15, 0.15, 1.0), 0.6)
    mat_pin_deck = make_mat('Mat_PinDeck', (0.70, 0.50, 0.25, 1.0), 0.5)
    mat_pit = make_mat('Mat_Pit', (0.10, 0.10, 0.12, 1.0), 0.8)
    mat_rail = make_mat('Mat_Rail', (0.35, 0.30, 0.25, 1.0), 0.4)

    gutter_length = 19.20
    gutter_depth = 0.10

    def make_gutter(name, x_start, x_end, mat):
        me = bpy.data.meshes.new(name + '_Mesh')
        profile = [
            (x_start, 0.0),
            (x_start + (x_end-x_start)*0.03, -0.02),
            (x_start + (x_end-x_start)*0.15, -0.06),
            ((x_start+x_end)/2, -gutter_depth),
            (x_start + (x_end-x_start)*0.85, -0.06),
            (x_start + (x_end-x_start)*0.97, -0.02),
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
                a = s*nv+v; b=a+1; c=(s+1)*nv+v+1; d=(s+1)*nv+v
                faces.append((a, b, c, d))
        me.from_pydata(verts, [], faces)
        me.validate()
        obj = bpy.data.objects.new(name, me)
        me.materials.append(mat)
        obj.parent = root
        static_col.objects.link(obj)
        return obj

    # Remove old gutters
    for existing in static_col.objects[:]:
        if existing.name.startswith('Gutter_'):
            static_col.objects.unlink(existing)
            bpy.data.objects.remove(existing)

    # CORRECTED gutter positions - inner gutters now ADJACENT to lanes, not overlapping
    # Left lane spans X=-1.4834 to X=-0.4166
    # Left outer gutter: X=-1.7334 to X=-1.4834 (outside lane)
    # Left inner gutter: X=-0.4166 to X=-0.1666 (between lane and center)
    # Right inner gutter: X=0.1666 to X=0.4166 (between center and lane)
    # Right outer gutter: X=1.4834 to X=1.7334 (outside lane)
    make_gutter('Gutter_L_Outer', -1.7334, -1.4834, mat_gutter)
    make_gutter('Gutter_L_Inner', -0.4166, -0.1666, mat_gutter)
    make_gutter('Gutter_R_Inner', 0.1666, 0.4166, mat_gutter)
    make_gutter('Gutter_R_Outer', 1.4834, 1.7334, mat_gutter)

    # Central divider
    me_div = bpy.data.meshes.new('Divider_Cap_Mesh')
    obj_div = bpy.data.objects.new('Divider_Cap', me_div)
    dw, dh = 0.03, 0.02
    dv = [(-dw/2,0,0),(dw/2,0,0),(dw/2,gutter_length,0),(-dw/2,gutter_length,0),
          (-dw/2,0,-dh),(dw/2,0,-dh),(dw/2,gutter_length,-dh),(-dw/2,gutter_length,-dh)]
    df = [(0,1,2,3),(4,5,6,7),(0,4,5,1),(3,2,1,0),(4,0,3,7),(5,4,7,6)]
    me_div.from_pydata(dv, [], df)
    me_div.validate()
    me_div.materials.append(mat_gutter)
    obj_div.parent = root
    static_col.objects.link(obj_div)

    # Pin decks
    for pname, px in [('PinDeck_L', -0.95), ('PinDeck_R', 0.95)]:
        me_pd = bpy.data.meshes.new(pname + '_Mesh')
        obj_pd = bpy.data.objects.new(pname, me_pd)
        hw = 0.60
        me_pd.from_pydata([(px-hw,18.0,0.001),(px+hw,18.0,0.001),(px+hw,19.20,0.001),(px-hw,19.20,0.001)], [], [(0,1,2,3)])
        me_pd.validate()
        me_pd.materials.append(mat_pin_deck)
        obj_pd.parent = root
        static_col.objects.link(obj_pd)

    # Pit
    me_pit = bpy.data.meshes.new('Pit_Catch_Mesh')
    obj_pit = bpy.data.objects.new('Pit_Catch', me_pit)
    pw, pl = 3.6, 0.80
    me_pit.from_pydata([(-pw/2,19.20,-0.15),(pw/2,19.20,-0.15),(pw/2,20.00,-0.15),(-pw/2,20.00,-0.15),
                        (-pw/2,19.20,-0.30),(pw/2,19.20,-0.30),(pw/2,20.00,-0.30),(-pw/2,20.00,-0.30)],
                       [], [(0,1,2,3),(4,5,6,7),(0,4,5,1),(3,2,1,0),(4,0,3,7),(5,4,7,6)])
    me_pit.validate()
    me_pit.materials.append(mat_pit)
    obj_pit.parent = root
    static_col.objects.link(obj_pit)

    # Outer rails
    rw, rh, ry, rl = 0.05, 0.08, -0.5, 20.0
    for rx, rname in [(-1.7434, 'OuterRail_L'), (1.7434, 'OuterRail_R')]:
        me_rail = bpy.data.meshes.new(rname + '_Mesh')
        obj_rail = bpy.data.objects.new(rname, me_rail)
        rv = [(rx-rw/2,ry,0),(rx+rw/2,ry,0),(rx+rw/2,ry+rl,0),(rx-rw/2,ry+rl,0),
              (rx-rw/2,ry,-rh),(rx+rw/2,ry,-rh),(rx+rw/2,ry+rl,-rh),(rx-rw/2,ry+rl,-rh)]
        me_rail.from_pydata(rv, [], [(0,1,2,3),(4,5,6,7),(0,4,5,1),(3,2,1,0),(4,0,3,7),(5,4,7,6)])
        me_rail.validate()
        me_rail.materials.append(mat_rail)
        obj_rail.parent = root
        static_col.objects.link(obj_rail)

    # Verification
    gutter_objs = [o for o in static_col.objects if o.name.startswith('Gutter_')]
    if len(gutter_objs) != 4:
        errors.append(f"Expected 4 gutters, got {len(gutter_objs)}")
    for go in gutter_objs:
        w = go.dimensions.x
        if abs(w - 0.25) > 0.005:
            errors.append(f"{go.name} width {w:.4f} not 0.22-0.25")
    lo = [o for o in gutter_objs if o.name == 'Gutter_L_Outer']
    if lo:
        mx = min(v.co.x for v in lo[0].data.vertices)
        if mx < -1.80:
            errors.append(f"Gutter_L_Outer X={mx:.4f} outside envelope")
    for go in gutter_objs:
        if abs(go.dimensions.y - gutter_length) > 0.02:
            errors.append(f"{go.name} Y wrong")
    # Check inner gutters don't overlap lanes
    li = [o for o in gutter_objs if o.name == 'Gutter_L_Inner']
    if li:
        mx = min(v.co.x for v in li[0].data.vertices)
        if mx < -0.42:
            errors.append(f"Gutter_L_Inner X={mx:.4f} overlaps lane")
    ri = [o for o in gutter_objs if o.name == 'Gutter_R_Inner']
    if ri:
        mn = max(v.co.x for v in ri[0].data.vertices)
        if mn > 0.42:
            errors.append(f"Gutter_R_Inner X={mn:.4f} overlaps lane")
    for o in static_col.objects:
        if o.parent != root:
            errors.append(f"{o.name} not parented to root")

    passed = len(errors) == 0

    report = {
        "stage": "02",
        "name": "Gutters, decks and pit (repaired inner adjacency)",
        "passed": passed,
        "gutter_count": len(gutter_objs),
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for cn in required_names:
            col = bpy.data.collections[cn]
            for o in col.objects:
                obj_list.append({'name': o.name, 'type': o.type,
                    'location': [round(x,6) for x in o.location],
                    'parent': o.parent.name if o.parent else None, 'collection': cn})
        json.dump({'objects': obj_list, 'collections': [c.name for c in bpy.data.collections]}, f, indent=2)

    return report

report = run_stage()
