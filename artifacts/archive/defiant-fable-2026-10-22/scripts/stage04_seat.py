# Stage 04 — Seat and Steering
import bpy
import math

def stage04():
    root_coll = bpy.data.collections.get("KART01_ASSET")
    if not root_coll:
        raise RuntimeError("KART01_ASSET collection not found")

    for obj in list(root_coll.objects):
        if obj.name in {"Kart01_Seat", "Kart01_SteeringColumn", "Kart01_SteeringWheel",
                        "Kart01_Pedal_L", "Kart01_Pedal_R"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Seat: base + back as one mesh, centered on X=0 in rear half
    seat = bpy.data.objects.new("Kart01_Seat", bpy.data.meshes.new("Seat"))
    seat["collection"] = root_coll
    bpy.context.scene.objects.link(seat)
    mesh = seat.data
    verts = [(0.10, -0.20, 0.05), (0.30, -0.20, 0.05), (0.30, -0.10, 0.05),
             (0.10, -0.10, 0.05), (0.10, -0.20, 0.10), (0.30, -0.20, 0.10),
             (0.30, -0.10, 0.10), (0.10, -0.10, 0.10),
             (0.15, -0.05, 0.15), (0.28, -0.05, 0.15), (0.28, 0.05, 0.15),
             (0.15, 0.05, 0.15), (0.15, -0.05, 0.20), (0.28, -0.05, 0.20),
             (0.28, 0.05, 0.20), (0.15, 0.05, 0.20)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 7, 6), (4, 7, 6),
             (8, 9, 10), (9, 11, 10), (8, 11, 10), (12, 13, 14), (13, 15, 14),
             (12, 15, 14), (8, 9, 12), (9, 11, 12), (8, 11, 8), (0, 4, 8),
             (0, 8, 12), (1, 5, 9), (1, 9, 13), (4, 8, 12), (4, 12, 0), (5, 9, 13),
             (5, 13, 1), (7, 11, 15), (7, 15, 14), (7, 14, 11), (11, 15, 14)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    seat.location = (0, 0.15, 0.12)
    seat.scale = (1.0, 1.0, 1.0)
    seat.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Steering column: simple tube
    col = bpy.data.objects.new("Kart01_SteeringColumn", bpy.data.meshes.new("Col"))
    col["collection"] = root_coll
    bpy.context.scene.objects.link(col)
    mesh = col.data
    verts = [(-0.02, 0.00, 0.00), (0.02, 0.00, 0.00),
             (-0.02, 0.00, 0.20), (0.02, 0.00, 0.20),
             (-0.02, 0.00, 0.00), (0.02, 0.00, 0.20),
             (-0.02, 0.04, 0.20), (0.02, 0.04, 0.20)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 3, 6),
             (4, 5, 0), (4, 0, 1), (7, 6, 2), (7, 2, 3), (7, 3, 6)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    col.location = (0, 0.05, 0.08)
    col.rotation_euler = (math.radians(-15), 0, 0)
    col.scale = (1.0, 1.0, 1.0)
    col.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Steering wheel: simple ring
    wheel = bpy.data.objects.new("Kart01_SteeringWheel", bpy.data.meshes.new("SW"))
    wheel["collection"] = root_coll
    bpy.context.scene.objects.link(wheel)
    mesh = wheel.data
    verts = [(0.05, -0.12, 0.08), (0.15, -0.05, 0.08), (0.15, 0.05, 0.08),
             (0.05, 0.12, 0.08), (-0.05, 0.12, 0.08), (-0.15, 0.05, 0.08),
             (-0.15, -0.05, 0.08), (0.05, -0.12, 0.08)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (1, 3, 7), (1, 7, 6), (1, 6, 5), (1, 5, 4),
             (1, 4, 3), (0, 1, 2), (7, 3, 1), (7, 2, 1), (7, 6, 5), (7, 5, 4)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    wheel.location = (0, 0.08, 0.32)
    wheel.rotation_euler = (math.radians(-90), 0, 0)
    wheel.scale = (1.0, 1.0, 1.0)
    wheel.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Pedals (two ahead of seat)
    def create_pedal(name, loc_y, loc_z):
        pedal = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        pedal["collection"] = root_coll
        bpy.context.scene.objects.link(pedal)
        mesh = pedal.data
        verts = [(-0.08, 0, 0.02), (0.08, 0, 0.02), (0.08, 0.04, 0.02),
                 (-0.08, 0.04, 0.02), (-0.08, 0, 0.06), (0.08, 0, 0.06),
                 (0.08, 0.04, 0.06), (-0.08, 0.04, 0.06)]
        mesh.vertices.add(len(verts))
        for i, v in enumerate(verts):
            mesh.vertices[i].co = v
        faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (5, 3, 6),
                 (4, 5, 0), (4, 0, 1), (7, 6, 2), (7, 2, 3), (7, 3, 6)]
        mesh.polygons.add(len(faces))
        for f in faces:
            mesh.polygons[-1].vertices = f
        pedal.location = (0, loc_y, loc_z)
        pedal.scale = (1.0, 1.0, 1.0)
        pedal.update_tag()
        bpy.ops.object.transform_apply(scale=True)
        return pedal

    create_pedal("Kart01_Pedal_L", 0.22, 0.14)
    create_pedal("Kart01_Pedal_R", 0.22, 0.14)

    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 04 complete: Seat and steering created")

if __name__ == "__main__":
    stage04()
