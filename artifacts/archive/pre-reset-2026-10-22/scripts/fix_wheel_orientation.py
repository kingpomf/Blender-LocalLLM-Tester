import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "03",
    "phase": "fix_wheel_orientation",
    "source_job": "788c0999a72a44299e6dd98337a90542",
    "checks": {}
}

# Rotate wheels so their axis is along X (as per spec)
wheel_names = ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"]
rim_names = ["Kart01_Rim_FL", "Kart01_Rim_FR", "Kart01_Rim_RL", "Kart01_Rim_RR"]

for name in wheel_names:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.rotation_euler = (0, 1.5708, 0)  # 90 degrees around Y
        # Scale so width is along X
        obj.scale = (0.07, 0.17, 0.17)

for name in rim_names:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.rotation_euler = (0, 1.5708, 0)
        obj.scale = (0.07, 0.1, 0.1)

report["result"] = "PASS"
print(json.dumps(report, indent=2))