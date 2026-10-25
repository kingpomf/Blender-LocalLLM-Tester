import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene

    # --- Units and scale ---
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # --- Root object: Empty at origin (no geometry wrapper rejects empty mesh) ---
    root_obj = bpy.data.objects.new('BowlingPair01_ROOT', None)
    root_obj.location = (0.0, 0.0, 0.0)
    root_obj.rotation_euler = (0.0, 0.0, 0.0)
    root_obj.scale = (1.0, 1.0, 1.0)
    scene.collection.objects.link(root_obj)

    # --- Collections ---
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']

    for name in required_names:
        if name not in bpy.data.collections:
            col = bpy.data.collections.new(name)
            scene.collection.children.link(col)

    # --- Verification ---
    errors = []

    # Check units
    if scene.unit_settings.system != 'METRIC':
        errors.append(f"Units not METRIC: {scene.unit_settings.system}")
    if abs(scene.unit_settings.scale_length - 1.0) > 0.001:
        errors.append(f"Scale length wrong: {scene.unit_settings.scale_length}")

    # Check root exists and transforms
    root_found = 'BowlingPair01_ROOT' in bpy.data.objects
    if not root_found:
        errors.append("Root object BowlingPair01_ROOT not found")

    if root_found:
        root_loc = root_obj.location
        root_rot = root_obj.rotation_euler
        root_scl = root_obj.scale
        if abs(root_loc[0]) > 0.001 or abs(root_loc[1]) > 0.001 or abs(root_loc[2]) > 0.001:
            errors.append(f"Root location not at origin: {root_loc}")
        if abs(root_rot[0]) > 0.001 or abs(root_rot[1]) > 0.001 or abs(root_rot[2]) > 0.001:
            errors.append(f"Root rotation not identity: {root_rot}")
        if abs(root_scl[0] - 1.0) > 0.001 or abs(root_scl[1] - 1.0) > 0.001 or abs(root_scl[2] - 1.0) > 0.001:
            errors.append(f"Root scale not (1,1,1): {root_scl}")

    # Check collections exist
    for rc in required_names:
        if rc not in bpy.data.collections:
            errors.append(f"Missing collection: {rc}")

    passed = len(errors) == 0

    report = {
        "stage": "00",
        "name": "Contract and scene safety",
        "passed": passed,
        "units": {
            "system": scene.unit_settings.system,
            "scale_length": scene.unit_settings.scale_length,
        },
        "root": {
            "name": root_obj.name,
            "type": root_obj.type,
            "location": [round(x, 6) for x in root_obj.location],
            "rotation": [round(x, 6) for x in root_obj.rotation_euler],
            "scale": [round(x, 6) for x in root_obj.scale],
        },
        "collections": required_names,
        "errors": errors,
    }

    # Write output files
    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for obj in scene.collection.objects:
            obj_list.append({
                'name': obj.name,
                'type': obj.type,
                'location': [round(x, 6) for x in obj.location],
                'rotation': [round(x, 6) for x in obj.rotation_euler],
                'scale': [round(x, 6) for x in obj.scale],
            })
        scene_info = {
            'units': {
                'system': scene.unit_settings.system,
                'scale_length': scene.unit_settings.scale_length,
            },
            'objects': obj_list,
            'collections': [c.name for c in bpy.data.collections],
        }
        json.dump(scene_info, f, indent=2)

    return report

report = run_stage()
