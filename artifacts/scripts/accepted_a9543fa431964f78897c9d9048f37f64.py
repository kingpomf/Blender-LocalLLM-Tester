import bpy
import math

lane_left_x = -0.95
lane_right_x = 0.95
lane_width = 1.0668
half_lane = lane_width / 2

dark_mat = bpy.data.materials.get("Marking_Dark")
if dark_mat is None:
    dark_mat = bpy.data.materials.new(name="Marking_Dark")
    dark_mat.diffuse_color = (0.05, 0.05, 0.05, 1.0)

root = bpy.data.objects["BowlingPair01_ROOT"]

for lane_x, name in [(lane_left_x, "FoulLine_L"), (lane_right_x, "FoulLine_R")]:
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = root
    x_min = lane_x - half_lane
    x_max = lane_x + half_lane
    vertices = [
        (x_min, 0, 0.0001),
        (x_max, 0, 0.0001),
        (x_max, 0.03, 0.0001),
        (x_min, 0.03, 0.0001)
    ]
    faces = [(0, 1, 2, 3)]
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj.data.materials.append(dark_mat)

arrow_y = 4.57
arrow_size = 0.08
arrow_base = 0.06

for lane_x, name_prefix in [(lane_left_x, "ArrowTri_L"), (lane_right_x, "ArrowTri_R")]:
    for i in range(7):
        offset = (i - 3) * 0.11
        x_pos = lane_x + offset
        name = f"{name_prefix}_{i+1}"
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.parent = root
        vertices = [
            (x_pos, arrow_y, 0.0001),
            (x_pos - arrow_base/2, arrow_y + arrow_size, 0.0001),
            (x_pos + arrow_base/2, arrow_y + arrow_size, 0.0001)
        ]
        faces = [(0, 1, 2)]
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        obj.data.materials.append(dark_mat)

dot_y = -1.0
dot_radius = 0.025

for lane_x, name_prefix in [(lane_left_x, "Dot_L"), (lane_right_x, "Dot_R")]:
    for i in range(7):
        offset = (i - 3) * 0.11
        x_pos = lane_x + offset
        name = f"{name_prefix}_{i+1}"
        mesh = bpy.data.meshes.new(f"{name}_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.parent = root
        segments = 12
        verts = []
        faces = []
        for j in range(segments):
            angle = 2 * math.pi * j / segments
            vx = x_pos + dot_radius * math.cos(angle)
            vy = dot_y + dot_radius * math.sin(angle)
            verts.append((vx, vy, 0.0001))
        for j in range(1, segments - 1):
            faces.append((0, j, j + 1))
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj.data.materials.append(dark_mat)

report = {
    "foul_lines": 2,
    "arrows_per_lane": 7,
    "dots_per_lane": 7,
    "lanes": ["left", "right"]
}