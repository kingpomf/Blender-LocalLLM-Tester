# Stage 07 — Presentation Cameras and Lighting
import bpy
import math

def stage07():
    root_coll = bpy.data.collections.get("KART01_ASSET")
    pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
    if not root_coll:
        raise RuntimeError("KART01_ASSET collection not found")
    if not pres_coll:
        raise RuntimeError("KART01_PRESENTATION collection not found")

    for obj in list(pres_coll.objects):
        if obj.name.startswith(("CAM_Kart01", "LIGHT_Kart01", "Kart01_Ground", "REF_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    def create_camera(name, loc, rot):
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam["collection"] = pres_coll
        bpy.context.scene.objects.link(cam)
        cam.data.lens = 50
        cam.data.clip_end = 100
        cam.location = loc
        cam.rotation_euler = rot
        return cam

    create_camera("CAM_Kart01_Perspective", (0.6, -0.8, 1.2), 
                  (math.radians(30), math.radians(45), 0))
    create_camera("CAM_Kart01_Front", (0.6, -0.8, 1.0), 
                  (math.radians(30), math.radians(90), 0))
    create_camera("CAM_Kart01_Side", (1.2, -0.8, 0.6), 
                  (math.radians(30), math.radians(0), 0))
    create_camera("CAM_Kart01_Rear", (0.6, -0.8, 0.8), 
                  (math.radians(30), math.radians(180), 0))

    ground = bpy.data.objects.new("Kart01_Ground", bpy.data.meshes.new("Ground"))
    ground["collection"] = pres_coll
    bpy.context.scene.objects.link(ground)
    mesh = ground.data
    verts = [(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    mesh.polygons.add(1)
    mesh.polygons[0].vertices = (0, 1, 2, 3)
    ground.scale = (1.0, 1.0, 1.0)
    ground.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    def create_light(name, loc, type_):
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, type=type_))
        light["collection"] = pres_coll
        bpy.context.scene.objects.link(light)
        light.location = loc
        light.energy = 100
        return light

    create_light("LIGHT_Kart01_Key", (1.5, -1.0, 2.0), "POINT")
    create_light("LIGHT_Kart01_Fill", (-1.5, -1.0, 2.0), "POINT")
    create_light("LIGHT_Kart01_Rim", (0.0, 2.0, 3.0), "POINT")

    bpy.context.scene.camera = bpy.data.objects["CAM_Kart01_Perspective"]

    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 07 complete: Cameras and lighting created")

if __name__ == "__main__":
    stage07()