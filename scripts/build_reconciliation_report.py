"""Summarize immutable native audit and existing failure diagnostics; no asset edits."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'testing/reconciliation-20261024'
audit=json.loads((folder/'native-audit.json').read_text())
scene=json.loads((ROOT/'artifacts/downloads/d1ce998472c349ac9f9fc2775afefdf6/scene.json').read_text())
objects={o['name']:o for o in audit['objects']}
root=objects['BowlingPair01_ROOT']
required={'BP01_STATIC','BP01_PINS','BP01_BALLS','BP01_COLLISION','BP01_PRESENTATION'}
foundation=(root['type']=='EMPTY' and root['location']==[0,0,0] and root['rotation']==[0,0,0]
            and root['scale']==[1,1,1] and audit['units']=={'system':'METRIC','scale':1.0}
            and required <= {c['name'] for c in scene['collections']}
            and all(o['parent']=='BowlingPair01_ROOT' for o in objects.values() if o['type']=='MESH'))
markings=[o for name,o in objects.items() if name.startswith(('ArrowTri_','Dot_','Foul_'))]
floating=[{'name':o['name'],'minimum_z':o['minimum'][2],'maximum_z':o['maximum'][2]} for o in markings
          if max(abs(o['minimum'][2]),abs(o['maximum'][2]))>.002]
gutters={name:{'width':o['maximum'][0]-o['minimum'][0],'minimum':o['minimum'],'maximum':o['maximum']}
         for name,o in objects.items() if name.startswith('Gutter_')}
pins=[o for name,o in objects.items() if name.startswith('Pin_')]
backward=[{'name':o['name'],'y':o['location'][1]} for o in pins if not o['name'].endswith('_01') and o['location'][1]<18.288]
red_faces=sum(o['material_face_counts'].get('1',0) for o in pins)
failures=[]
ball_attempt=0
for line in (ROOT/'.runtime/autonomous-run/002-coding.jsonl').read_text().splitlines():
    event=json.loads(line)
    part=event.get('part',{})
    state=part.get('state',{})
    if event.get('type')=='tool_use' and part.get('tool','').endswith('blender_scene_author') and 'Ball_01' in state.get('input',{}).get('code',''):
        ball_attempt+=1
        saved=folder/f'stage04-submission-{ball_attempt:02d}.py'
        code=state['input']['code']
        assert not saved.exists() or saved.read_text()==code
        saved.write_text(code)
    if event.get('type')=='tool_use' and part.get('tool','').endswith('blender_job_diagnostics') and state.get('status')=='completed':
        data=json.loads(state['output'])
        failures.append({'job_id':data['id'],'source_job':data.get('source_job'),
            'exceptions':[line for line in data['logs']['blender.log']['text'].splitlines()
                          if re.match(r'^\w*(?:Error|Exception):',line) and not line.startswith('Error: script failed')]})
result={'source_job':'d1ce998472c349ac9f9fc2775afefdf6','audit_job':'4f572bf507534fe184d09d7014e0d60c',
        'foundation_passed':foundation,'floating_markings':floating,'gutters':gutters,
        'pin_count':len(pins),'backward_pins':backward,'red_pin_faces':red_faces,
        'pin_boundary_edges':objects['Pin_L_01']['boundary_edges'],
        'stage_results':{'00':'PASS' if foundation else 'FAIL','01':'FAIL','02':'FAIL','03':'FAIL','04':'FAIL'},
        'failed_jobs':failures,'bmesh_operators':audit['bmesh_operators'],
        'scope':'Read-only measurements; no asset geometry or model-authored script was changed.'}
assert foundation and floating and backward and red_faces==0 and len(failures)==6
(folder/'findings.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'foundation_passed':foundation,'floating_marking_count':len(floating),
    'gutter_widths':{n:r['width'] for n,r in gutters.items()},'backward_pin_count':len(backward),
    'red_pin_faces':red_faces,'pin_boundary_edges':result['pin_boundary_edges'],'failed_jobs':failures},indent=2))
