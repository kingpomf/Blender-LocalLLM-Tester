# Stage 03 — Axles and Wheels
import bpy

def stage03():
    root_coll = bpy.data.collections.get("KART01_ASSET")
    pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
    if not root_coll:
        raise RuntimeError("KART01_ASSET collection not found")
    if not pres_coll:
        raise RuntimeError("KART01_PRESENTATION collection not found")

    for obj in list(root_coll.objects):
        if obj.name in {"Kart01_Axle_Front", "Kart01_Axle_Rear",
                        "Kart01_Wheel_FL", "Kart01_Wheel_FR",
                        "Kart01_Wheel_RL", "Kart01_Wheel_RR"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Front axle
    axle_f = bpy.data.objects.new("Kart01_Axle_Front", bpy.data.meshes.new("AF"))
    axle_f["collection"] = root_coll
    bpy.context.scene.objects.link(axle_f)
    mesh = axle_f.data
    verts = [(-0.40, 0, 0.08), (0.40, 0, 0.08),
             (-0.40, 0.04, 0.08), (0.40, 0.04, 0.08),
             (-0.40, 0, 0.16), (0.40, 0, 0.16),
             (-0.40, 0.04, 0.16), (0.40, 0.04, 0.16)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 3, 6),
             (4, 5, 0), (4, 0, 1), (7, 6, 2), (7, 2, 3), (7, 3, 6)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    axle_f.location = (0, 0.10, 0.08)
    axle_f.scale = (1.0, 1.0, 1.0)
    axle_f.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Rear axle
    axle_r = bpy.data.objects.new("Kart01_Axle_Rear", bpy.data.meshes.new("AR"))
    axle_r["collection"] = root_coll
    bpy.context.scene.objects.link(axle_r)
    mesh = axle_r.data
    verts = [(-0.40, 0, 0.08), (0.40, 0, 0.08),
             (-0.40, 0.04, 0.08), (0.40, 0.04, 0.08),
             (-0.40, 0, 0.16), (0.40, 0, 0.16),
             (-0.40, 0.04, 0.16), (0.40, 0.04, 0.16)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 3, 6),
             (4, 5, 0), (4, 0, 1), (7, 6, 2), (7, 2, 3), (7, 3, 6)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    axle_r.location = (0, -0.50, 0.08)
    axle_r.scale = (1.0, 1.0, 1.0)
    axle_r.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Wheel function
    def create_wheel(name, loc_y, loc_z):
        wheel = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        wheel["collection"] = root_coll
        bpy.context.scene.objects.link(wheel)
        mesh = wheel.data
        verts = [(-0.07, -0.07, 0.0), (0.07, -0.07, 0.0),
                 (0.07, 0.07, 0.0), (-0.07, 0.07, 0.0),
                 (-0.07, -0.07, 0.17), (0.07, -0.07, 0.17),
                 (0.07, 0.07, 0.17), (-0.07, 0.07, 0.17)]
        mesh.vertices.add(len(verts))
        for i, v in enumerate(verts):
            mesh.vertices[i].co = v
        faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 3, 6),
                 (4, 5, 0), (4, 0, 1), (7, 6, 2), (7, 2, 3), (7, 3, 6)]
        mesh.polygons.add(len(faces))
        for f in faces:
            mesh.polygons[-1].vertices = f
        wheel.location = (0, loc_y, loc_z)
        wheel.rotation_euler = (math.radians(90), 0, 0)
        wheel.scale = (1.0, 1.0, 1.0)
        wheel.update_tag()
        bpy.ops.object.transform_apply(scale=True)
        return wheel

    # Four wheels (FL, FR, RL, RR)
    create_wheel("Kart01_Wheel_FL", 0.44, 0.17)
    create_wheel("Kart01_Wheel_FR", -0.44, 0.17)
    create_wheel("Kart01_Wheel_RL", 0.44, -0.50)
    create_wheel("Kart01_Wheel_RR", -0.44, -0.50)

    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 03 complete: Axles and wheels created")

if __name__ == "__main__":
    stage03()
