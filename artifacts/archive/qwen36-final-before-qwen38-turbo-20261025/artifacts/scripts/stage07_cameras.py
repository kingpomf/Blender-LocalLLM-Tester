import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []

    # Create presentation collection if not exists
    if 'BP01_PRESENTATION' not in bpy.data.collections:
        bpy.data.collections.new('BP01_PRESENTATION')

    pres_col = bpy.data.collections['BP01_PRESENTATION']

    # Remove old presentation cameras
    for existing in pres_col.objects[:]:
        if existing.type == 'CAMERA':
            pres_col.objects.unlink(existing)
            bpy.data.cameras.remove(existing.data)
            bpy.data.objects.remove(existing)

    # Materials for lighting
    mat_lightbar = bpy.data.materials.new('Mat_LightBar_Pres') if 'Mat_LightBar_Pres' not in [m.name for m in bpy.data.materials] else bpy.data.materials['Mat_LightBar_Pres']
    mat_lightbar.use_nodes = True
    bg = mat_lightbar.node_tree.nodes['Material Output']
    p = mat_lightbar.node_tree.nodes.new('ShaderNodeEmission')
    p.inputs['Color'].default_value = (1.0, 0.95, 0.80, 1.0)
    p.inputs['Strength'].default_value = 10.0
    mat_lightbar.node_tree.links.new(p.outputs['Emission'], bg.inputs['Surface'])

    # Lighting - balanced alley lighting
    # Key light
    key_light = bpy.data.lights.new('KeyLight', 'AREA')
    key_light.energy = 500
    key_light.size = 5.0
    obj_key = bpy.data.objects.new('KeyLight', key_light)
    obj_key.location = (2.0, 10.0, 6.0)
    pres_col.objects.link(obj_key)

    # Fill light
    fill_light = bpy.data.lights.new('FillLight', 'AREA')
    fill_light.energy = 300
    fill_light.size = 4.0
    obj_fill = bpy.data.objects.new('FillLight', fill_light)
    obj_fill.location = (-3.0, 8.0, 5.0)
    pres_col.objects.link(obj_fill)

    # Rim light
    rim_light = bpy.data.lights.new('RimLight', 'AREA')
    rim_light.energy = 400
    rim_light.size = 3.0
    obj_rim = bpy.data.objects.new('RimLight', rim_light)
    obj_rim.location = (0.0, 15.0, 8.0)
    pres_col.objects.link(obj_rim)

    # Ambient
    amb_light = bpy.data.lights.new('AmbientLight', 'SUN')
    amb_light.energy = 0.5
    obj_amb = bpy.data.objects.new('AmbientLight', amb_light)
    obj_amb.location = (0.0, 0.0, 0.0)
    obj_amb.rotation_euler = (0.8, 0.0, 0.5)
    pres_col.objects.link(obj_amb)

    # Set world background
    world = bpy.data.worlds.get('World')
    if world is None:
        world = bpy.data.worlds.new('World')
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Strength'].default_value = 0.3

    # Cameras - NOT children of visual root
    cameras = []

    # 1. Overview camera
    cam_overview = bpy.data.cameras.new('CAM_BowlingPair01_Overview')
    obj_overview = bpy.data.objects.new('CAM_BowlingPair01_Overview', cam_overview)
    obj_overview.location = (3.0, 8.0, 5.0)
    obj_overview.rotation_euler = (1.2, 0.0, -0.3)
    cam_overview.lens = 35
    pres_col.objects.link(obj_overview)
    cameras.append(('overview', obj_overview))

    # 2. Player camera (from left approach toward left pins)
    cam_player = bpy.data.cameras.new('CAM_BowlingPair01_Player')
    obj_player = bpy.data.objects.new('CAM_BowlingPair01_Player', cam_player)
    obj_player.location = (-1.5, 2.0, 1.5)
    obj_player.rotation_euler = (1.3, 0.0, 0.1)
    cam_player.lens = 50
    pres_col.objects.link(obj_player)
    cameras.append(('player', obj_player))

    # 3. Pin deck camera (both racks)
    cam_pindeck = bpy.data.cameras.new('CAM_BowlingPair01_PinDeck')
    obj_pindeck = bpy.data.objects.new('CAM_BowlingPair01_PinDeck', cam_pindeck)
    obj_pindeck.location = (0.0, 10.0, 4.0)
    obj_pindeck.rotation_euler = (1.4, 0.0, 0.0)
    cam_pindeck.lens = 35
    pres_col.objects.link(obj_pindeck)
    cameras.append(('pindeck', obj_pindeck))

    # 4. Props camera (balls on return)
    cam_props = bpy.data.cameras.new('CAM_BowlingPair01_Props')
    obj_props = bpy.data.objects.new('CAM_BowlingPair01_Props', cam_props)
    obj_props.location = (0.5, -1.5, 1.0)
    obj_props.rotation_euler = (1.0, 0.0, -0.1)
    cam_props.lens = 85
    pres_col.objects.link(obj_props)
    cameras.append(('props', obj_props))

    # Report cameras
    report = {
        "stage": "07",
        "name": "Presentation cameras and lighting",
        "passed": True,
        "camera_count": len(cameras),
        "light_count": 4,
        "cameras": [{"name": c[0], "location": [round(x, 3) for x in c[1].location], "lens": c[1].data.lens} for c in cameras],
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

    # Return camera objects for rendering
    return cameras, pres_col

cameras, pres_col = run_stage()
