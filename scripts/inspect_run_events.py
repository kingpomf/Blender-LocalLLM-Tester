"""Print concise native outcomes and exception tails from a saved controller event log."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.authoring_preflight import inspect_authoring


def inspect(path):
    outcomes=[]
    for line in Path(path).read_text().splitlines():
        try:event=json.loads(line)
        except ValueError:continue
        part=event.get('part',{});state=part.get('state',{})
        if not part.get('tool','').startswith('bowling-blender52_'):continue
        try:result=json.loads(state.get('output',''))
        except (ValueError,TypeError):continue
        if part['tool'].endswith('blender_scene_author') and result.get('id'):
            checked=inspect_authoring(state.get('input',{}).get('code',''))
            outcomes.append({'job':result['id'],'current_preflight_ok':checked['ok'],'issues':checked.get('issues',[])})
        if result.get('state')=='failed' or 'logs' in result:
            item={'tool':part['tool'],'input':state.get('input'),'state':result.get('state'),'error':result.get('error')}
            if 'logs' in result:
                item['log_tails']={name:'\n'.join(line for line in log.get('text','').splitlines() if len(line)<1000 and line.strip(' ^'))[-1800:] for name,log in result['logs'].items()}
            outcomes.append(item)
    return outcomes


if __name__=='__main__':print(json.dumps(inspect(sys.argv[1]),indent=2))
