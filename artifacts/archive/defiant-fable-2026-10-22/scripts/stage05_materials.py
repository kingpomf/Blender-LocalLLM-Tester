# Stage 05 — Materials
import bpy

def stage05():
    root_coll = bpy.data.collections.get("KART01_ASSET")
    if not root_coll:
        raise RuntimeError("KART01_ASSET collection not found")

    # Remove old materials
    for mat in list(bpy.data.materials):
        if mat.name.startswith("MAT_Kart") or mat.name.startswith("MAT_Rubber") or \
           mat.name.startswith("MAT_Metal") or mat.name.startswith("MAT_Rim") or \
           mat.name.startswith("MAT_Seat"):
            bpy.data.materials.remove(mat, do_unlink=True)

    # Helper to create material
    def create_mat(name, base_color, roughness=0.5):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        principled = nodes.new(type="ShaderNodeBsdfPrincipled")
        principled.location = (200, 0)
        principled.base_color = base_color
        principled.roughness = roughness
        output = nodes.new(type="ShaderNodeOutputMaterial")
        output.location = (400, 0)
        links = mat.node_tree.links
        links.new(principled.outputs["BSDF"], output.inputs["Surface"])
        return mat

    # MAT_Kart_Red — chassis, bumpers, side pods
    mat_chassis = create_mat("MAT_Kart_Red", (0.78, 0.16, 0.16, 1.0), 0.3)

    # MAT_Rubber_Dark — tires
    mat_rubber = create_mat("MAT_Rubber_Dark", (0.09, 0.09, 0.09, 1.0), 0.7)

    # MAT_Metal_Dark — axles, steering column, pedals
    mat_metal = create_mat("MAT_Metal_Dark", (0.15, 0.15, 0.18, 1.0), 0.3)

    # MAT_Rim_Silver — rims
    mat_rim = create_mat("MAT_Rim_Silver", (0.6, 0.6, 0.65, 1.0), 0.2)

    # MAT_Seat_Black — seat and steering wheel
    mat_seat = create_mat("MAT_Seat_Black", (0.05, 0.05, 0.05, 1.0), 0.4)

    # Assign materials to objects
    for obj in root_coll.objects:
        if obj.name == "Kart01_Chassis" or obj.name in {"Kart01_Bumper_Front", "Kart01_Bumper_Rear",
                                                         "Kart01_SidePod_L", "Kart01_SidePod_R"}:
            if obj.data.materials:
                obj.data.materials[0] = mat_chassis
        elif obj.name == "Kart01_Floor":
            if obj.data.materials:
                obj.data.materials[0] = mat_metal
        elif obj.name in {"Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"}:
            if obj.data.materials:
                obj.data.materials[0] = mat_rubber
        elif obj.name in {"Kart01_Axle_Front", "Kart01_Axle_Rear",
                          "Kart01_SteeringColumn", "Kart01_Pedal_L", "Kart01_Pedal_R"}:
            if obj.data.materials:
                obj.data.materials[0] = mat_metal
        elif obj.name == "Kart01_Seat":
            if obj.data.materials:
                obj.data.materials[0] = mat_seat
        elif obj.name == "Kart01_SteeringWheel":
            if obj.data.materials:
                obj.data.materials[0] = mat_seat

    bpy.ops.outpath.rollover()
    bpy.ops.wm.save_as_mainfile(filepath="artifacts/blend/Kart01.blend")
    print("Stage 05 complete: Materials assigned")

if __name__ == "__main__":
    stage05()
