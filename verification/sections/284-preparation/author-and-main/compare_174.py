from pathlib import Path
from copy import deepcopy
import json,sys,hashlib
root=Path.cwd();sys.path.insert(0,str(root))
from rouge.damage import calculate_damage
b=json.loads(Path('.cache/section284-preparation/public-baseline.json').read_bytes());checks=[]
for item in b['cases']:
 s=item['scenario'];before=deepcopy(s);r=calculate_damage(s)
 keys=('attack','total_damage','total_healing','attack_speed','attack_speed_reference','base_attack_speed','base_attack_speed_reference','components','complete','warnings')
 selected={k:r.get(k) for k in keys};selected['estimate']={k:r['estimate'].get(k) for k in ('base_stats','skill','training','complete','warnings')}
 assert selected==item['result'],str(s)
 assert s==before
 q=r['panel_native_finalization'];assert q['actual_panel'] is None and not q['complete_native_panel']
 checks.append({'operator':s['operator'],'skill':s['skill'],'effects':bool(s.get('effects')),'old_model_unchanged':True,'actual_still_unknown':True})
p=Path('.cache/section284-preparation/after-model-174.json');assert not p.exists();p.write_text(json.dumps({'kind':'PUBLIC_BASELINE_COMPARISON_NOT_GAME','baseline_sha256':hashlib.sha256(Path('.cache/section284-preparation/public-baseline.json').read_bytes()).hexdigest(),'source_sha256':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in ('rouge/operator_engine.py','rouge/panel_native_bridge.py')},'passed':True,'cases':checks,'count':len(checks),'private_state_used':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'passed':True,'cases':len(checks)})
