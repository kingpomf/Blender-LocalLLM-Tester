# Stage 06 — Hierarchy and Transforms
import bpy

def stage06():
    root_coll = bpy.data.collections.get("KART01_ASSET")
    pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
    if not root_coll:
        raise RuntimeError("KART01_ASSET collection not found")
    if not pres_coll:
        raise RuntimeError("KART01_PRESENTATION collection not found")

    # Apply scale to all asset meshes
    for obj in root_coll.objects:
        if obj.type == "MESH":
            if obj.scale != (1.0, 1.0, 1.0):
                obj.update_tag()
                bpy.ops.object.transform_apply(scale=True)

    # Apply rotation to all asset meshes (except wheels which have intentional rotation)
    for obj in root_coll.objects:
        if obj.type == "MESH" and obj.name not in \
           {"Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"}:
            if obj.rotation_euler != (0, 0, 0):
                obj.update_tag()
                bpy.ops.object.transform_apply(rotation=True)

    # Parent all asset objects to Kart01_Root
    root = bpy.data.objects.get("Kart01_Root")
    if not root:
        raise RuntimeError("Kart01_Root not found")

    for obj in list(root_coll.objects):
        if obj != root and obj.type in {"MESH", "EMPTY"}:
            obj.parent = root

    # Ensure Kart01_Root is at origin with identity transforms
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)

    # Check for duplicate suffixes
    names = [obj.name for obj in bpy.data.objects]
    duplicates = [n for n in names if n.endswith(".001") or n.endswith(".002")]
    if duplicates:
        raise RuntimeError(f"Duplicate object names found: {duplicates}")

    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 06 complete: Hierarchy and transforms applied")

if __name__ == "__main__":
    stage06()
