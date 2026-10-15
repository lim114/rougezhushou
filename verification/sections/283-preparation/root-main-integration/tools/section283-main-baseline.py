from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r))
from rouge.damage import calculate_damage
from rouge.calibration import panel_layers
dest=r/'.cache/section283-main-integration';dest.mkdir(exist_ok=True)
cases=[]
for op in ('kaltsit','silverash','mechanist'):
 for skill in (1,2,3):
  for relic in (None,'rogue_6_relic_legacy_16','rogue_6_relic_legacy_90'):
   cases.append({'operator':op,'skill':skill,**({'relic_ids':[relic]} if relic else {})})
for op,skill in (('char_1041_angel2',3),('char_151_myrtle',2),('char_437_mizuki',2)):
 cases.append({'operator':op,'skill':skill})
for op in ('kaltsit','silverash','mechanist'):
 cases.append({'operator':op,'skill':1,'effects':[{'kind':'attack_pct','value':.25},{'kind':'hp_pct','value':.5},
  {'kind':'defense_pct','value':.4},{'kind':'resistance_flat','value':20},{'kind':'attack_speed','value':800}]})
def select(result):
 return {k:deepcopy(result.get(k)) for k in ('attack','total_damage','total_healing','attack_speed','attack_speed_reference','base_attack_speed','base_attack_speed_reference','components','complete','warnings')}|{
 'estimate':{k:deepcopy(result['estimate'].get(k)) for k in ('base_stats','skill','training','complete','warnings')}}
rows=[]
for s in cases:
 before=deepcopy(s);result=calculate_damage(s);assert s==before
 row={'scenario':s,'legacy_model':select(result)}
 if s['operator'] in ('kaltsit','silverash','mechanist'):
  p=panel_layers(s);row['calibration']={k:p[k] for k in ('context','context_token','rows','panels','model_complete','native_verified')}
 rows.append(row)
files=('rouge/relic_attributes.py','rouge/damage.py','rouge/estimate.py','rouge/operator_engine.py','rouge/relics.py','rouge/calibration.py','rouge/reporting.py','rouge/offline_tools_view.py')
for f in files:(dest/(Path(f).stem+'-before.py')).write_bytes((r/f).read_bytes())
out={'kind':'PRE_CHANGE_PUBLIC_MODEL_BASELINE_NOT_NATIVE_VALIDATION','cases':rows,'count':len(rows),
 'source_sha256':{f:hashlib.sha256((r/f).read_bytes()).hexdigest() for f in files},'private_state_used':False,'game_or_chat_operated':False}
path=dest/'before-model.json';assert not path.exists();path.write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'public_cases':len(rows),'source_snapshots':len(files),'baseline_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
