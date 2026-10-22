import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create MAT_Kart_Red (chassis, bumpers, side pods)
    mat_red = bpy.data.materials.new("MAT_Kart_Red")
    mat_red.use_nodes = True
    bsdf = mat_red.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.776, 0.157, 0.157, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5

    # Create MAT_Rubber_Dark (tires)
    mat_rubber = bpy.data.materials.new("MAT_Rubber_Dark")
    mat_rubber.use_nodes = True
    bsdf_rubber = mat_rubber.node_tree.nodes["Principled BSDF"]
    bsdf_rubber.inputs["Base Color"].default_value = (0.09, 0.09, 0.09, 1.0)
    bsdf_rubber.inputs["Roughness"].default_value = 0.7

    # Create MAT_Metal_Dark (axles, steering column, pedals)
    mat_metal = bpy.data.materials.new("MAT_Metal_Dark")
    mat_metal.use_nodes = True
    bsdf_metal = mat_metal.node_tree.nodes["Principled BSDF"]
    bsdf_metal.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    bsdf_metal.inputs["Metallic"].default_value = 0.8

    # Create MAT_Rim_Silver (visible rims)
    mat_rim = bpy.data.materials.new("MAT_Rim_Silver")
    mat_rim.use_nodes = True
    bsdf_rim = mat_rim.node_tree.nodes["Principled BSDF"]
    bsdf_rim.inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1.0)
    bsdf_rim.inputs["Metallic"].default_value = 0.9

    # Create MAT_Seat_Black (seat and steering wheel)
    mat_seat = bpy.data.materials.new("MAT_Seat_Black")
    mat_seat.use_nodes = True
    bsdf_seat = mat_seat.node_tree.nodes["Principled BSDF"]
    bsdf_seat.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
    bsdf_seat.inputs["Roughness"].default_value = 0.8

    # Assign materials to objects
    # Chassis, bumpers, side pods -> MAT_Kart_Red
    for obj_name in ["Kart01_Chassis", "Kart01_Bumper_Front", "Kart01_Bumper_Rear", "Kart01_SidePod_L", "Kart01_SidePod_R"]:
        obj = bpy.data.objects[obj_name]
        obj.data.materials.append(mat_red)

    # Floor -> MAT_Kart_Red (same color family)
    bpy.data.objects["Kart01_Floor"].data.materials.append(mat_red)

    # Axles -> MAT_Metal_Dark
    for obj_name in ["Kart01_Axle_Front", "Kart01_Axle_Rear"]:
        obj = bpy.data.objects[obj_name]
        obj.data.materials.append(mat_metal)

    # Wheels -> MAT_Rubber_Dark for tires, MAT_Rim_Silver for rims
    for obj_name in ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"]:
        obj = bpy.data.objects[obj_name]
        obj.data.materials.append(mat_rubber)
        obj.data.materials.append(mat_rim)

    # Steering column and pedals -> MAT_Metal_Dark
    for obj_name in ["Kart01_SteeringColumn", "Kart01_Pedal_L", "Kart01_Pedal_R"]:
        obj = bpy.data.objects[obj_name]
        obj.data.materials.append(mat_metal)

    # Seat and steering wheel -> MAT_Seat_Black
    for obj_name in ["Kart01_Seat_Base", "Kart01_Seat_Back", "Kart01_SteeringWheel"]:
        obj = bpy.data.objects[obj_name]
        obj.data.materials.append(mat_seat)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify materials exist
    assert "MAT_Kart_Red" in bpy.data.materials, "MAT_Kart_Red missing"
    assert "MAT_Rubber_Dark" in bpy.data.materials, "MAT_Rubber_Dark missing"
    assert "MAT_Metal_Dark" in bpy.data.materials, "MAT_Metal_Dark missing"
    assert "MAT_Rim_Silver" in bpy.data.materials, "MAT_Rim_Silver missing"
    assert "MAT_Seat_Black" in bpy.data.materials, "MAT_Seat_Black missing"

    return {
        "stage": "05",
        "passed": True,
        "materials": ["MAT_Kart_Red", "MAT_Rubber_Dark", "MAT_Metal_Dark", "MAT_Rim_Silver", "MAT_Seat_Black"],
        "material_assignments": {
            "chassis": "MAT_Kart_Red",
            "bumpers": "MAT_Kart_Red",
            "side_pods": "MAT_Kart_Red",
            "floor": "MAT_Kart_Red",
            "axles": "MAT_Metal_Dark",
            "wheels": ["MAT_Rubber_Dark", "MAT_Rim_Silver"],
            "steering_column": "MAT_Metal_Dark",
            "pedals": "MAT_Metal_Dark",
            "seat": "MAT_Seat_Black",
            "steering_wheel": "MAT_Seat_Black"
        }
    }

report = run_stage()
