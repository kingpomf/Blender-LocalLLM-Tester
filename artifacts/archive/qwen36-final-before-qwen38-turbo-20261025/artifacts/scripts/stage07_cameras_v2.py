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

    # Clean up old cameras
    for existing in list(pres_col.objects):
        if existing.name.startswith('CAM_BowlingPair01_'):
            pres_col.objects.unlink(existing)
            if existing.type == 'CAMERA':
                bpy.data.cameras.remove(existing.data)
            bpy.data.objects.remove(existing)

    # Ensure lighting exists
    has_light = any(o.type == 'LIGHT' for o in scene.objects)
    if not has_light:
        # Add ambient-like lighting
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

    # Camera configurations: name, location, target, tracking
    camera_configs = [
        ('CAM_BowlingPair01_Overview',
         Vector((-3.5, -8.0, 3.0)),
         Vector((0, 10, 0.5)),
         'TRACK_TO'),
        ('CAM_BowlingPair01_Player',
         Vector((-2.0, -2.5, 1.5)),
         Vector((-0.95, 18, 0.5)),
         'TRACK_TO'),
        ('CAM_BowlingPair01_PinDeck',
         Vector((0, 16, 2.5)),
         Vector((0, 18.5, 0.5)),
         'TRACK_TO'),
        ('CAM_BowlingPair01_Props',
         Vector((2.0, -2.0, 1.2)),
         Vector((0, -2.3, 0.1)),
         'TRACK_TO'),
    ]

    cameras = []
    for cam_name, location, target, track_type in camera_configs:
        cam_data = bpy.data.cameras.new(cam_name + '_data')
        cam_data.angle = 0.8
        cam_data.lens_unit = 'FOV'
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        cam_obj.location = location
        cam_obj.parent = root

        # Add track-to constraint
        constraint = cam_obj.constraints.new('TRACK_TO')
        constraint.target = root
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        # Set empty as track target
        track_target = bpy.data.objects.new(cam_name + '_target', None)
        track_target.location = target
        track_target.parent = root
        constraint.target = root
        # Use a simpler approach: just set location and let the renderer use it
        cam_obj.rotation_euler = (target - location).to_track_quat('-Z', 'Y').to_euler()

        pres_col.objects.link(cam_obj)
        cameras.append(cam_obj)

    # Set up render settings
    scene.render.image_format = 'PNG'
    scene.render.filepath = '/job/renders'
    os.makedirs('/job/renders', exist_ok=True)
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.film_transparent = True
    scene.cycles.samples = 64
    scene.cycles.use_denoising = False

    # Use Cycles for rendering
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'

    # Render each camera
    rendered = []
    for cam in cameras:
        scene.camera = cam
        render_path = f'/job/renders/{cam.name.replace("CAM_BowlingPair01_", "")}.png'
        scene.render.filepath = render_path
        try:
            bpy.ops.render.render()
            rendered.append(cam.name)
        except Exception as e:
            errors.append(f"Render failed for {cam.name}: {str(e)}")

    # Verify cameras exist and aren't parented to root visually
    for cam in cameras:
        if cam.parent and cam.parent == root:
            errors.append(f"{cam.name} parented to visual root")

    # Also verify cameras are in PRESENTATION collection
    for cam in cameras:
        in_pres = 'BP01_PRESENTATION' in [c.name for c in cam.users_collection]
        if not in_pres:
            errors.append(f"{cam.name} not in BP01_PRESENTATION")

    # Count render files
    render_files = [f for f in os.listdir('/job/renders') if f.endswith('.png')] if os.path.exists('/job/renders') else []

    passed = len(errors) == 0

    report = {
        "stage": "07",
        "name": "Presentation cameras and lighting",
        "passed": passed,
        "cameras": [c.name for c in cameras],
        "rendered": rendered,
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
