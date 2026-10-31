from pathlib import Path
from types import ModuleType
from copy import deepcopy
import subprocess,sys,json,time
import cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
from rouge import run_recognition
old=ModuleType('rouge.before_resources');old.__package__='rouge';old.__file__=str(R/'rouge/resource_recognition.py')
exec(compile(subprocess.check_output(['git','show','HEAD:rouge/resource_recognition.py']),'<before-resources>','exec'),old.__dict__)
current=run_recognition.read_resources
out=R/'verification/sections/441-hud-sample-pairs';out.mkdir(parents=True,exist_ok=False)
rows=[];readers={'before':ScreenReader(),'after':ScreenReader()};keys={'life','shield','command','hope','action','valuation'}
def facts(value,drop=False):
    v=deepcopy(value);v.pop('performance',None);v.pop('observed_at',None)
    if drop and v.get('run'):
        v['run']['resources']={k:r for k,r in v['run']['resources'].items()if k not in keys}
    return v
for i,path in enumerate(sorted((R/'samples/native-client').glob('*.png'))):
    image=cv2.imdecode(np.fromfile(path,np.uint8),1);values={};row={'case':i+1,'milliseconds':{}}
    for name in ('before','after')if i%2==0 else('after','before'):
        run_recognition.read_resources=(lambda im,tx,engine:old.read_resources(im,tx))if name=='before'else current
        v=readers[name].read(image);values[name]=v;row['milliseconds'][name]=v['performance']['total_ms']
    same=facts(values['before'])==facts(values['after'],True);assert same,{'case':i+1}
    row.update(prior_facts_equal_except_new_resources=True,new_HUD_fields=len(keys&set((values['after'].get('run')or{}).get('resources',{}))))
    rows.append(row);print(json.dumps({'completed_pairs':len(rows)}),flush=True)
run_recognition.read_resources=current
result={'passed':True,'pairs':rows,'scope':'Existing local development images; compare all interpreted facts in RAM except six deliberately added resource keys. No pixels, text, actual quantities, sample names or pixel hashes published. Not independent game accuracy or FPS.'}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'pairs':len(rows)}),flush=True)
