from pathlib import Path
from types import ModuleType
from copy import deepcopy
import subprocess,sys,json,time
import cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
from rouge import hud_resources
old=ModuleType('rouge.before_resources');old.__package__='rouge';old.__file__=str(R/'rouge/hud_resources.py')
exec(compile((R/'research/resource-capacity-442/before-hud_resources.py').read_bytes(),'<before-resources>','exec'),old.__dict__)
current=hud_resources.read_hud_resources
out=R/'verification/sections/442-capacity-sample-pairs';out.mkdir(parents=True,exist_ok=False)
rows=[];readers={'before':ScreenReader(),'after':ScreenReader()};keys={'hope'}
def facts(value,drop=False):
    v=deepcopy(value);v.pop('performance',None);v.pop('observed_at',None)
    if drop and v.get('run'):
        
        if 'hope' in v['run']['resources']:v['run']['resources']['hope'].pop('capacity',None)
    return v
for i,path in enumerate(sorted((R/'samples/native-client').glob('*.png'))):
    image=cv2.imdecode(np.fromfile(path,np.uint8),1);values={};row={'case':i+1,'milliseconds':{}}
    for name in ('before','after')if i%2==0 else('after','before'):
        hud_resources.read_hud_resources=old.read_hud_resources if name=='before'else current
        v=readers[name].read(image);values[name]=v;row['milliseconds'][name]=v['performance']['total_ms']
    same=facts(values['before'])==facts(values['after'],True);assert same,{'case':i+1}
    row.update(prior_facts_equal_except_new_hope_capacity=True,hope_capacity_added=int('capacity' in (values['after'].get('run') or {}).get('resources',{}).get('hope',{})))
    rows.append(row);print(json.dumps({'completed_pairs':len(rows)}),flush=True)
hud_resources.read_hud_resources=current
result={'passed':True,'pairs':rows,'scope':'Existing local development images; compare all interpreted facts in RAM except the deliberately added hope.capacity field. No pixels, text, actual quantities, sample names or pixel hashes published. Not independent game accuracy or FPS.'}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'pairs':len(rows)}),flush=True)
