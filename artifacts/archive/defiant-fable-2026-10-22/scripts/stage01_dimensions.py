# Stage 01 — Coordinate System and Dimensions
# Create reference guides for the kart envelope
import bpy
import math

def stage01():
    # Ensure we're in the KART01_PRESENTATION collection
    pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
    if not pres_coll:
        raise RuntimeError("KART01_PRESENTATION collection not found")

    # Remove old references if they exist
    for obj in list(pres_coll.objects):
        if obj.name.startswith("REF_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Create X-axis reference (1.20m width)
    ref_x = bpy.data.objects.new("REF_X_Width", bpy.data.meshes.new("RefX"))
    ref_x["collection"] = pres_coll
    ref_x["type"] = "reference"
    bpy.context.collection.objects.link(ref_x)

    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0, 0, 0.525))
    ref_x.data.name = "RefX"
    ref_x["name"] = "REF_X_Width"

    # Create Y-axis reference (1.80m length)
    ref_y = bpy.data.objects.new("REF_Y_Length", bpy.data.meshes.new("RefY"))
    ref_y["collection"] = pres_coll
    ref_y["type"] = "reference"
    bpy.context.collection.objects.link(ref_y)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.6, 0, 0.525))
    ref_y.data.name = "RefY"
    ref_y["name"] = "REF_Y_Length"

    # Create Z-axis reference (1.05m height)
    ref_z = bpy.data.objects.new("REF_Z_Height", bpy.data.meshes.new("RefZ"))
    ref_z["collection"] = pres_coll
    ref_z["type"] = "reference"
    bpy.context.collection.objects.link(ref_z)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.6, 0.9, 0.525))
    ref_z.data.name = "RefZ"
    ref_z["name"] = "REF_Z_Height"

    # Create wheelbase reference (1.10m)
    ref_wb = bpy.data.objects.new("REF_Wheelbase", bpy.data.meshes.new("RefWB"))
    ref_wb["collection"] = pres_coll
    ref_wb["type"] = "reference"
    bpy.context.collection.objects.link(ref_wb)

    bpy.ops.mesh.primitive_cube_add(size=1.1, location=(0.6, 0, 0.525))
    ref_wb.data.name = "RefWB"
    ref_wb["name"] = "REF_Wheelbase"

    # Create front track reference (0.92m)
    ref_ft = bpy.data.objects.new("REF_FrontTrack", bpy.data.meshes.new("RefFT"))
    ref_ft["collection"] = pres_coll
    ref_ft["type"] = "reference"
    bpy.context.collection.objects.link(ref_ft)

    bpy.ops.mesh.primitive_cube_add(size=0.92, location=(0.6, 0.46, 0.525))
    ref_ft.data.name = "RefFT"
    ref_ft["name"] = "REF_FrontTrack"

    # Create rear track reference (0.96m)
    ref_rt = bpy.data.objects.new("REF_RearTrack", bpy.data.meshes.new("RefRT"))
    ref_rt["collection"] = pres_coll
    ref_rt["type"] = "reference"
    bpy.context.collection.objects.link(ref_rt)

    bpy.ops.mesh.primitive_cube_add(size=0.96, location=(0.6, -0.48, 0.525))
    ref_rt.data.name = "RefRT"
    ref_rt["name"] = "REF_RearTrack"

    # Create wheel diameter reference (0.34m)
    ref_dia = bpy.data.objects.new("REF_WheelDia", bpy.data.meshes.new("RefDia"))
    ref_dia["collection"] = pres_coll
    ref_dia["type"] = "reference"
    bpy.context.collection.objects.link(ref_dia)

    bpy.ops.mesh.primitive_cube_add(size=0.34, location=(0.17, 0.9, 0.525))
    ref_dia.data.name = "RefDia"
    ref_dia["name"] = "REF_WheelDia"

    # Create wheel width reference (0.14m)
    ref_wid = bpy.data.objects.new("REF_WheelWidth", bpy.data.meshes.new("RefWid"))
    ref_wid["collection"] = pres_coll
    ref_wid["type"] = "reference"
    bpy.context.collection.objects.link(ref_wid)

    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(0.17, 0.9, 0.525))
    ref_wid.data.name = "RefWid"
    ref_wid["name"] = "REF_WheelWidth"

    # Save the scene
    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")

    print("Stage 01 complete: Reference guides created")

if __name__ == "__main__":
    stage01()
