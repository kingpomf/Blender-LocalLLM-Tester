"""Local structure checks; visual and GLB round-trip review remain mandatory."""
import hashlib
import json
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check(root=ROOT):
    out=[]; hashes={}; pngs=[]
    names=['blend/Kart01.blend','exports/Kart01.glb','reports/validation.json','reports/BUILD_REPORT.md']
    names+=['renders/Kart01_'+v+'.png' for v in ('perspective','front','side','rear')]
    for name in names:
        path=root/'artifacts'/name
        if not path.is_file() or not path.stat().st_size:
            out.append('Missing/empty '+name); continue
        data=path.read_bytes(); hashes[name]=hashlib.sha256(data).hexdigest()
        if name.endswith('.blend') and not data.startswith(b'BLENDER'): out.append('Invalid uncompressed blend header')
        if name.endswith('.png'):
            if data[:8]!=b'\x89PNG\r\n\x1a\n' or len(data)<24 or struct.unpack('>II',data[16:24])!=(512,512): out.append('Invalid PNG size/header '+name)
            pngs.append(hashes[name])
        if name.endswith('validation.json'):
            try:
                report=json.loads(data)
                if not report.get('passed') or not report.get('checks') or any(c.get('passed') is not True for c in report['checks']): out.append('Numeric validation not passed')
            except (ValueError,KeyError,TypeError): out.append('Invalid validation report')
        if name.endswith('.glb'):
            if len(data)<20 or data[:4]!=b'glTF' or struct.unpack('<II',data[4:12])!=(2,len(data)): out.append('Invalid GLB header')
            else:
                try:
                    size,kind=struct.unpack('<II',data[12:20]); doc=json.loads(data[20:20+size])
                    if kind!=0x4e4f534a or not doc.get('meshes') or not doc.get('materials'): out.append('GLB lacks geometry/materials')
                    if doc.get('cameras') or 'KHR_lights_punctual' in doc.get('extensions',{}): out.append('GLB includes presentation')
                    forbidden=('CAM_','LIGHT_','REF_','Kart01_Ground')
                    if any(n.get('name','').startswith(forbidden) for n in doc.get('nodes',[])): out.append('GLB includes presentation nodes')
                except (ValueError,KeyError,TypeError): out.append('Invalid GLB JSON')
    if len(set(pngs))<len(pngs): out.append('Identical PNG files; inspect camera selection')
    return dict(passed=not out,errors=out,sha256=hashes,scope='Structure checks only; inspect decoded images and perform Blender GLB round-trip')
if __name__=='__main__':
    result=check(); print(json.dumps(result,indent=2)); raise SystemExit(not result['passed'])
