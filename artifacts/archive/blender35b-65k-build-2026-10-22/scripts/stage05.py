import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create MAT_Kart_Red
    mat_red = bpy.data.materials.new(name="MAT_Kart_Red")
    mat_red.use_nodes = True
    bsdf = mat_red.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.776, 0.157, 0.157, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

    # Create MAT_Rubber_Dark
    mat_rubber = bpy.data.materials.new(name="MAT_Rubber_Dark")
    mat_rubber.use_nodes = True
    bsdf_rubber = mat_rubber.node_tree.nodes["Principled BSDF"]
    bsdf_rubber.inputs["Base Color"].default_value = (0.09, 0.09, 0.09, 1.0)
    bsdf_rubber.inputs["Roughness"].default_value = 0.8

    # Create MAT_Metal_Dark
    mat_metal = bpy.data.materials.new(name="MAT_Metal_Dark")
    mat_metal.use_nodes = True
    bsdf_metal = mat_metal.node_tree.nodes["Principled BSDF"]
    bsdf_metal.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
    bsdf_metal.inputs["Metallic"].default_value = 0.9
    bsdf_metal.inputs["Roughness"].default_value = 0.3

    # Create MAT_Rim_Silver
    mat_rim = bpy.data.materials.new(name="MAT_Rim_Silver")
    mat_rim.use_nodes = True
    bsdf_rim = mat_rim.node_tree.nodes["Principled BSDF"]
    bsdf_rim.inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1.0)
    bsdf_rim.inputs["Metallic"].default_value = 0.95
    bsdf_rim.inputs["Roughness"].default_value = 0.2

    # Create MAT_Seat_Black
    mat_seat = bpy.data.materials.new(name="MAT_Seat_Black")
    mat_seat.use_nodes = True
    bsdf_seat = mat_seat.node_tree.nodes["Principled BSDF"]
    bsdf_seat.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
    bsdf_seat.inputs["Roughness"].default_value = 0.9

    # Assign materials to objects
    bpy.data.objects["Kart01_Chassis"].data.materials.append(mat_red)
    bpy.data.objects["Kart01_Bumper_Front"].data.materials.append(mat_red)
    bpy.data.objects["Kart01_Bumper_Rear"].data.materials.append(mat_red)
    bpy.data.objects["Kart01_SidePod_L"].data.materials.append(mat_red)
    bpy.data.objects["Kart01_SidePod_R"].data.materials.append(mat_red)

    bpy.data.objects["Kart01_Wheel_FL"].data.materials.append(mat_rubber)
    bpy.data.objects["Kart01_Wheel_FR"].data.materials.append(mat_rubber)
    bpy.data.objects["Kart01_Wheel_RL"].data.materials.append(mat_rubber)
    bpy.data.objects["Kart01_Wheel_RR"].data.materials.append(mat_rubber)

    bpy.data.objects["Kart01_SteeringColumn"].data.materials.append(mat_metal)
    bpy.data.objects["Kart01_Pedal_L"].data.materials.append(mat_metal)
    bpy.data.objects["Kart01_Pedal_R"].data.materials.append(mat_metal)

    bpy.data.objects["Kart01_SteeringWheel"].data.materials.append(mat_seat)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "materials": ["MAT_Kart_Red", "MAT_Rubber_Dark", "MAT_Metal_Dark", "MAT_Rim_Silver", "MAT_Seat_Black"],
        "assignments": {
            "MAT_Kart_Red": ["Kart01_Chassis", "Kart01_Bumper_Front", "Kart01_Bumper_Rear", "Kart01_SidePod_L", "Kart01_SidePod_R"],
            "MAT_Rubber_Dark": ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"],
            "MAT_Metal_Dark": ["Kart01_SteeringColumn", "Kart01_Pedal_L", "Kart01_Pedal_R"],
            "MAT_Rim_Silver": ["Kart01_SteeringWheel"],
            "MAT_Seat_Black": ["Kart01_SteeringWheel"]
        }
    }

report = run_stage()
