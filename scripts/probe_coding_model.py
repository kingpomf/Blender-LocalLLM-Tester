"""Read advertised gateway model identity without loading/switching GPU workloads."""
import json
from pathlib import Path
import urllib.request
import argparse


def probe(model):
    config=json.loads((Path.home()/'.config/opencode/opencode.json').read_text())
    provider,model_id=model.split('/',1)
    settings=config['provider'][provider];options=settings['options'];metadata=settings['models'][model_id]
    secret=options['apiKey'];assert secret.startswith('{file:') and secret.endswith('}')
    token=Path(secret[6:-1]).read_text().strip()
    request=urllib.request.Request(options['baseURL'].rstrip('/')+'/models',headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(request,timeout=30) as response:data=json.load(response)
    available={item['id']:item for item in data['data']}
    assert model_id in available, 'Requested model is not advertised by the installed gateway'
    return {'model':model,'advertised':True,'context':metadata['limit']['context'],'output':metadata['limit']['output'],
            'tool_call':metadata.get('tool_call'),'reasoning':metadata.get('reasoning'),
            'gateway_model':{k:v for k,v in available[model_id].items() if k in {'id','object','owned_by','context_size','context_length','enabled','status'}}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('model');args=parser.parse_args()
    print(json.dumps(probe(args.model),indent=2))
