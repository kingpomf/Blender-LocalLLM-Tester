import bpy
import json
import os
from mathutils import Vector

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    pres_col = bpy.data.collections['BP01_PRESENTATION']

    # Collect old camera names first
    old_cams = []
    for existing in pres_col.objects:
        if existing.name.startswith('CAM_BowlingPair01_'):
            old_cams.append(existing.name)
    for cam_name in old_cams:
        obj = bpy.data.objects.get(cam_name)
        if obj:
            if obj.users_collection:
                for c in obj.users_collection[:]:
                    c.objects.unlink(obj)
            if obj.type == 'CAMERA' and obj.data:
                if obj.data.users == 0:
                    bpy.data.cameras.remove(obj.data)
            if obj.users == 0:
                bpy.data.objects.remove(obj)

    has_light = any(o.type == 'LIGHT' for o in scene.objects)
    if not has_light:
        for i, (loc, energy) in enumerate([
            ((0, 5, 8), 50),
            ((-5, 10, 6), 30),
            ((5, 10, 6), 30),
            ((0, 15, 4), 20),
        ]):
            lt_data = bpy.data.lights.new(f'Light_{i}', 'POINT')
            lt_data.energy = energy
            lt_obj = bpy.data.objects.new(f'Light_{i}', lt_data)
            lt_obj.location = loc
            lt_obj.parent = root
            pres_col.objects.link(lt_obj)

    camera_configs = [
        ('CAM_BowlingPair01_Overview',
         Vector((-3.5, -8.0, 3.0)),
         Vector((0, 10, 0.5))),
        ('CAM_BowlingPair01_Player',
         Vector((-2.0, -2.5, 1.5)),
         Vector((-0.95, 18, 0.5))),
        ('CAM_BowlingPair01_PinDeck',
         Vector((0, 16, 2.5)),
         Vector((0, 18.5, 0.5))),
        ('CAM_BowlingPair01_Props',
         Vector((2.0, -2.0, 1.2)),
         Vector((0, -2.3, 0.1))),
    ]

    cameras = []
    for cam_name, location, target in camera_configs:
        cam_data = bpy.data.cameras.new(cam_name + '_data')
        cam_data.angle = 0.8
        cam_data.lens_unit = 'FOV'
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        cam_obj.location = location
        cam_obj.parent = root
        cam_obj.rotation_euler = (target - location).to_track_quat('-Z', 'Y').to_euler()
        pres_col.objects.link(cam_obj)
        cameras.append(cam_obj)

    rs = scene.render
    rs.image_settings.file_format = 'PNG'
    rs.filepath = '/job/renders'
    os.makedirs('/job/renders', exist_ok=True)
    rs.resolution_x = 1280
    rs.resolution_y = 720
    rs.film_transparent = True
    scene.cycles.samples = 16
    scene.cycles.use_denoising = False
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'

    # Store camera configs for external render calls
    cam_configs_out = []
    for cam in cameras:
        scene.camera = cam
        render_path = f'{cam.name.replace("CAM_BowlingPair01_", "")}.png'
        rs.filepath = f'/job/renders/{render_path}'
        cam_configs_out.append({'name': cam.name, 'render_file': render_path})
        try:
            bpy.ops.render.render()
        except Exception as e:
            errors.append(f"Render failed for {cam.name}: {str(e)}")

    render_files = [f for f in os.listdir('/job/renders') if f.endswith('.png')] if os.path.exists('/job/renders') else []

    passed = len(errors) == 0

    report = {
        "stage": "07",
        "name": "Presentation cameras and lighting",
        "passed": passed,
        "cameras": [c.name for c in cameras],
        "render_files": render_files,
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
