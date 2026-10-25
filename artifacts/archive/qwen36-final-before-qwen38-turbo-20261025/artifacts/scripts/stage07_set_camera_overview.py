import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene
    cam_name = 'CAM_BowlingPair01_Overview'

    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj is None or cam_obj.type != 'CAMERA':
        raise ValueError(f"Camera {cam_name} not found")

    scene.camera = cam_obj
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64

    report = {
        "stage": "07",
        "camera": cam_name,
        "passed": True,
        "errors": []
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for cn in ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']:
            col = bpy.data.collections[cn]
            for o in col.objects:
                obj_list.append({'name': o.name, 'type': o.type,
                    'location': [round(x,6) for x in o.location],
                    'parent': o.parent.name if o.parent else None, 'collection': cn})
        json.dump({'objects': obj_list, 'collections': [c.name for c in bpy.data.collections]}, f, indent=2)

    return report

report = run_stage()
