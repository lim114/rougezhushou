from pathlib import Path
from copy import deepcopy
import json,hashlib,sys
root=Path.cwd();sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
out=root/'.cache/section284-preparation/public-baseline.json'
assert not out.exists()
rows=[]
for op,p in catalog()['operators'].items():
 for n in range(1,len(p['skills'])+1):
  for mode in ('default','effects'):
   s={'operator':op,'skill':n}
   if mode=='effects':s['effects']=[{'kind':'attack_pct','value':.25},{'kind':'attack_speed','value':60},{'kind':'hp_pct','value':.5}]
   before=deepcopy(s)
   try:
    result=calculate_damage(s)
    # Added reference/report are outside unchanged legacy model selection.
    keys=('attack','total_damage','total_healing','attack_speed','attack_speed_reference','base_attack_speed','base_attack_speed_reference','components','complete','warnings')
    legacy={k:result.get(k) for k in keys}
    legacy['estimate']={k:result['estimate'].get(k) for k in ('base_stats','skill','training','complete','warnings')}
    rows.append({'scenario':s,'result':legacy})
   except Exception as ex:rows.append({'scenario':s,'error':type(ex).__name__+':'+str(ex)})
   assert s==before
obj={'kind':'PRE284_PUBLIC_MODEL_BASELINE_NOT_NATIVE_OR_GAME','source_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ('rouge/operator_engine.py','rouge/panel_native_bridge.py')},'catalog_keys':len(catalog()['operators']),'skills':sum(len(p['skills']) for p in catalog()['operators'].values()),'cases':rows,'count':len(rows),'private_state_used':False}
out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'cases':len(rows),'errors':sum('error'in row for row in rows),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
