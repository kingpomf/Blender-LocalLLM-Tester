# Stage 00 — Contract and Scene Safety
# Objective: Prepare an isolated Blender scene for Kart01
import bpy

def stage00():
    # Remove default objects if they exist
    for obj in bpy.data.objects:
        if obj.name in {"Cube", "Camera", "Light"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create required collections
    asset_coll = bpy.data.collections.new("KART01_ASSET")
    pres_coll = bpy.data.collections.new("KART01_PRESENTATION")

    bpy.context.scene.collection.children.link(asset_coll)
    bpy.context.scene.collection.children.link(pres_coll)

    # Create ground plane for reference (will be in presentation)
    ground = bpy.data.objects.new("Kart01_Ground", bpy.data.meshes.new("Ground"))
    ground["collection"] = pres_coll
    bpy.context.collection.objects.link(ground)

    # Save the scene
    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")

    print("Stage 00 complete: Scene prepared with collections and ground reference")

if __name__ == "__main__":
    stage00()
