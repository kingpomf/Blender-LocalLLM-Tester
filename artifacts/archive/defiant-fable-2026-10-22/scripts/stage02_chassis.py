# Stage 02 — Chassis and Bumpers
import bpy
import math

def stage02():
    # Ensure collections exist
    root_coll = bpy.data.collections.get("KART01_ASSET")
    pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
    if not root_coll:
        root_coll = bpy.data.collections.new("KART01_ASSET")
        bpy.context.scene.collection.children.link(root_coll)
    if not pres_coll:
        raise RuntimeError("KART01_PRESENTATION collection not found")

    # Remove old chassis objects
    for obj in list(root_coll.objects):
        if obj.name in {"Kart01_Root", "Kart01_Chassis", "Kart01_Floor", 
                        "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
                        "Kart01_SidePod_L", "Kart01_SidePod_R"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create root empty at origin
    root = bpy.data.objects.new("Kart01_Root", None)
    root["collection"] = root_coll
    bpy.context.scene.objects.link(root)

    # Main chassis: low-poly wedge shape, centered on X=0
    chassis = bpy.data.objects.new("Kart01_Chassis", bpy.data.meshes.new("Chassis"))
    chassis["collection"] = root_coll
    bpy.context.scene.objects.link(chassis)

    mesh = chassis.data
    verts = [(0, 0, 0.17),   # rear center
             (0.5, 0, 0.17),  # rear right
             (0.5, -0.45, 0.17), # rear right corner
             (0.5, 0.45, 0.17), # rear left corner
             (0.3, 0, 0.20),   # mid rear
             (0.3, -0.35, 0.20), # mid rear right
             (0.3, 0.35, 0.20), # mid rear left
             (0.15, 0, 0.22),  # mid front
             (0.15, -0.30, 0.22), # mid front right
             (0.15, 0.30, 0.22), # mid front left
             (0.08, 0, 0.24),   # front center
             (0.08, -0.28, 0.24), # front right corner
             (0.08, 0.28, 0.24), # front left corner
             (-0.05, 0, 0.26),  # nose tip
             (-0.05, -0.22, 0.26), # nose right
             (-0.05, 0.22, 0.26), # nose left
             (0.08, 0, 0.24)]   # close loop

    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v

    # Create faces for a low-poly wedge
    faces = [
        (0, 1, 2), (1, 3, 2), (0, 3, 1),  # rear face
        (4, 5, 6), (4, 6, 7), (4, 7, 5),  # mid rear
        (7, 8, 9), (7, 9, 10), (7, 10, 8), # mid front
        (10, 11, 12), (10, 12, 13), (10, 13, 11), # front section
        (13, 14, 15), (13, 15, 16), (13, 16, 14), # nose section
        (16, 17, 15), (16, 15, 10), (16, 10, 14), # nose sides
        (3, 11, 12), (3, 12, 13), (3, 13, 11),  # rear to front right
        (2, 10, 13), (2, 13, 12), (2, 12, 10),  # rear to front left
        (1, 14, 15), (1, 15, 13), (1, 13, 14),  # rear to nose
        (0, 4, 7), (0, 7, 10), (0, 10, 4),      # bottom face
        (0, 1, 2), (0, 2, 10), (0, 10, 1),     # bottom sides
    ]

    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f

    # Apply scale
    chassis.scale = (1.0, 1.0, 1.0)
    chassis.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Floor: flat driver floor
    floor = bpy.data.objects.new("Kart01_Floor", bpy.data.meshes.new("Floor"))
    floor["collection"] = root_coll
    bpy.context.scene.objects.link(floor)

    mesh = floor.data
    verts = [(0.0, -0.35, 0.05),
             (0.4, -0.35, 0.05),
             (0.4, 0.35, 0.05),
             (0.0, 0.35, 0.05)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    mesh.polygons.add(1)
    mesh.polygons[0].vertices = (0, 1, 2, 3)
    floor.scale = (1.0, 1.0, 1.0)
    floor.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Front bumper
    front_bumper = bpy.data.objects.new("Kart01_Bumper_Front", bpy.data.meshes.new("BF"))
    front_bumper["collection"] = root_coll
    bpy.context.scene.objects.link(front_bumper)

    mesh = front_bumper.data
    verts = [(-0.08, 0, 0.18),
             (0.08, 0, 0.18),
             (0.08, 0.10, 0.18),
             (-0.08, 0.10, 0.18),
             (-0.08, 0, 0.22),
             (0.08, 0, 0.22),
             (0.08, 0.10, 0.22),
             (-0.08, 0.10, 0.22)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (4, 6, 7), (4, 7, 5),
             (0, 1, 5), (1, 3, 5), (0, 3, 0), (4, 5, 2), (5, 2, 6), (0, 7, 6)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    front_bumper.scale = (1.0, 1.0, 1.0)
    front_bumper.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Rear bumper
    rear_bumper = bpy.data.objects.new("Kart01_Bumper_Rear", bpy.data.meshes.new("BR"))
    rear_bumper["collection"] = root_coll
    bpy.context.scene.objects.link(rear_bumper)

    mesh = rear_bumper.data
    verts = [(0.35, 0, 0.18),
             (0.45, 0, 0.18),
             (0.45, 0.08, 0.18),
             (0.35, 0.08, 0.18),
             (0.35, 0, 0.22),
             (0.45, 0, 0.22),
             (0.45, 0.08, 0.22),
             (0.35, 0.08, 0.22)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (0, 3, 1), (4, 5, 6), (4, 6, 7), (4, 7, 5),
             (0, 1, 5), (1, 3, 5), (0, 3, 0), (4, 5, 2), (5, 2, 6), (0, 7, 6)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    rear_bumper.scale = (1.0, 1.0, 1.0)
    rear_bumper.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Side pods (mirrored)
    sidepod = bpy.data.objects.new("Kart01_SidePod_L", bpy.data.meshes.new("SP"))
    sidepod["collection"] = root_coll
    bpy.context.scene.objects.link(sidepod)

    mesh = sidepod.data
    verts = [(0.15, 0.35, 0.12),
             (0.15, 0.35, 0.20),
             (0.10, 0.35, 0.22),
             (0.05, 0.35, 0.22),
             (0.05, 0.35, 0.12),
             (0.10, 0.35, 0.12),
             (0.15, 0.42, 0.16),
             (0.15, 0.35, 0.20),
             (0.15, 0.42, 0.12)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (1, 2, 4), (1, 4, 5), (1, 5, 6), (1, 6, 7),
             (7, 8, 6), (7, 6, 5), (0, 1, 7), (0, 7, 8), (0, 8, 2)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    sidepod.scale = (1.0, 1.0, 1.0)
    sidepod.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    sidepod_r = bpy.data.objects.new("Kart01_SidePod_R", bpy.data.meshes.new("SPR"))
    sidepod_r["collection"] = root_coll
    bpy.context.scene.objects.link(sidepod_r)
    sidepod_r.data = bpy.data.meshes.new("SPR")
    mesh = sidepod_r.data
    verts = [(0.15, -0.35, 0.12),
             (0.15, -0.35, 0.20),
             (0.10, -0.35, 0.22),
             (0.05, -0.35, 0.22),
             (0.05, -0.35, 0.12),
             (0.10, -0.35, 0.12),
             (0.15, -0.42, 0.16),
             (0.15, -0.35, 0.20),
             (0.15, -0.42, 0.12)]
    mesh.vertices.add(len(verts))
    for i, v in enumerate(verts):
        mesh.vertices[i].co = v
    faces = [(0, 1, 2), (1, 3, 2), (1, 2, 4), (1, 4, 5), (1, 5, 6), (1, 6, 7),
             (7, 8, 6), (7, 6, 5), (0, 1, 7), (0, 7, 8), (0, 8, 2)]
    mesh.polygons.add(len(faces))
    for f in faces:
        mesh.polygons[-1].vertices = f
    sidepod_r.scale = (1.0, 1.0, 1.0)
    sidepod_r.update_tag()
    bpy.ops.object.transform_apply(scale=True)

    # Save
    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 02 complete: Chassis and bumpers created")

if __name__ == "__main__":
    stage02()
