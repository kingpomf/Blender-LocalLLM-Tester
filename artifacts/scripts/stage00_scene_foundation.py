import bpy


def run():
    scene = bpy.context.scene

    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

    root = bpy.data.objects.new("BowlingPair01_ROOT", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.5
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)

    created = []
    for cname in ("BP01_STATIC", "BP01_PINS", "BP01_BALLS",
                  "BP01_COLLISION", "BP01_PRESENTATION"):
        coll = bpy.data.collections.new(cname)
        scene.collection.children.link(coll)
        created.append(cname)

    scene.collection.children["BP01_STATIC"].objects.link(root)

    report = {
        "stage": "00",
        "units": {
            "system": scene.unit_settings.system,
            "scale_length": float(scene.unit_settings.scale_length),
            "length_unit": scene.unit_settings.length_unit,
        },
        "axes": "X/Y ground plane, Z up, +Y toward pins, +X right from approach",
        "root": {
            "name": root.name,
            "location": [float(root.location[i]) for i in range(3)],
            "rotation_euler": [float(root.rotation_euler[i]) for i in range(3)],
            "scale": [float(root.scale[i]) for i in range(3)],
            "parent": root.parent.name if root.parent else None,
        },
        "collections": created,
        "scene_object_names": sorted(o.name for o in bpy.data.objects),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
