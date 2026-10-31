from pathlib import Path
from types import ModuleType
from copy import deepcopy
import sys,json,cv2,numpy as np
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
old=ModuleType('rouge._recognition_before443');old.__package__='rouge';old.__file__=str(R/'rouge/recognition.py')
exec(compile((R/'research/shop-price-443/before-recognition.py').read_bytes(),'<own-before-recognition443>','exec'),old.__dict__)
readers={'before':old.ScreenReader(),'after':ScreenReader()};out=R/'verification/sections/443-sample-pairs';rows=[]
for i,path in enumerate(sorted((R/'samples/native-client').glob('*.png'))):
    image=cv2.imdecode(np.fromfile(path,np.uint8),1);values={};row={'case':i+1,'milliseconds':{}}
    for name in ('before','after')if i%2==0 else('after','before'):
        value=readers[name].read(image);row['milliseconds'][name]=value['performance']['total_ms']
        value.pop('performance',None);value.pop('observed_at',None);values[name]=value
    before,after=deepcopy(values['before']),deepcopy(values['after']);is_shop=after['page']=='shop'
    if is_shop:
        after['page']=before['page'];after['run'].pop('shop')
        if before['run']is None and after['run']=={'page':'shop','operators':[],'relics':{'ids':[],'icons':[],'count':None,'source':'unread'}}:after['run']=None
    same=before==after
    row.update(prior_facts_equal_except_deliberate_shop_observation=same,new_shop_page=is_shop);rows.append(row)
    print(json.dumps({'pairs_completed':len(rows),'equal':same}),flush=True)
    if not same:
        (R/'.cache/shop443-private-pair-difference.json').write_text(json.dumps(values,ensure_ascii=False,indent=2),'utf8')
        break
passed=len(rows)==20 and all(r['prior_facts_equal_except_deliberate_shop_observation']for r in rows)
(out/'results.json').write_text(json.dumps({'passed':passed,'pairs':rows,'scope':'Existing private development images stay local. Only deliberate shop page/run.shop additions may differ; all other interpreted facts compared in RAM. No images, names, text, quantities or pixel hashes published. Not independent accuracy or a performance/FPS claim.'},indent=2)+'\n','utf8')
raise SystemExit(0 if passed else 1)
