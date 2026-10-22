"""Read-only independent analysis of fetched scene metadata and delivered GLB."""
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any

base = Path(__file__).resolve().parents[2]
scene = json.loads((base / 'artifacts/reports/REVIEW_FINAL_SCENE.json').read_text())
objects = scene['objects']
asset = [o for o in objects if 'KART01_ASSET' in o['collections']]
findings: dict[str, Any] = {'cameras': {}, 'wheels': {}}
for obj in objects:
    if obj['type'] == 'CAMERA':
        matrix = obj['matrix_world']
        forward = [-matrix[i][2] for i in range(3)]
        target = [-obj['location'][0], -obj['location'][1], 0.3 - obj['location'][2]]
        dot = sum(a*b for a, b in zip(forward, target))
        angle = math.degrees(math.acos(max(-1, min(1, dot / math.sqrt(sum(v*v for v in target))))))
        findings['cameras'][obj['name']] = {'rotation': obj['rotation'], 'forward': forward, 'angle_to_kart_center_degrees': angle}
    if obj['name'] in ['Kart01_Wheel_FL', 'Kart01_Wheel_FR', 'Kart01_Wheel_RL', 'Kart01_Wheel_RR']:
        findings['wheels'][obj['name']] = {'dimensions_xyz_m': obj['dimensions'], 'bottom_z_m': obj['location'][2] - obj['dimensions'][2]/2}
findings['asset_faces'] = sum(o.get('topology', {}).get('faces', 0) for o in asset)
findings['asset_triangles'] = sum(o.get('topology', {}).get('triangles', 0) for o in asset)
blend = base / 'artifacts/blend/Kart01.blend'
checkpoint = base / 'artifacts/downloads/3fb3c4fd63e046f1a9768927e29eee1e/scene.blend'
findings['delivered_blend_matches_pre_fix_stage07'] = hashlib.sha256(blend.read_bytes()).digest() == hashlib.sha256(checkpoint.read_bytes()).digest()
glb = (base / 'artifacts/exports/Kart01.glb').read_bytes()
magic, version, total = struct.unpack_from('<4sII', glb)
assert magic == b'glTF' and version == 2 and total == len(glb)
size, kind = struct.unpack_from('<II', glb, 12)
assert kind == 0x4E4F534A
doc = json.loads(glb[20:20+size])
nodes = doc.get('nodes', [])
findings['glb'] = {'bytes': len(glb), 'nodes': [n.get('name') for n in nodes], 'meshes': len(doc.get('meshes', [])), 'cameras': len(doc.get('cameras', [])), 'root_present': any(n.get('name') == 'Kart01_Root' for n in nodes)}
print(json.dumps(findings, indent=2))
