from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r))
from rouge.damage import calculate_damage
from rouge.calibration import panel_layers
baseline=json.loads((r/'.cache/section283-main-integration/before-model.json').read_bytes())
def select(result):
 return {k:deepcopy(result.get(k)) for k in ('attack','total_damage','total_healing','attack_speed','attack_speed_reference','base_attack_speed','base_attack_speed_reference','components','complete','warnings')}|{
 'estimate':{k:deepcopy(result['estimate'].get(k)) for k in ('base_stats','skill','training','complete','warnings')}}
rows=[]
for entry in baseline['cases']:
 s=deepcopy(entry['scenario']);before=deepcopy(s);result=calculate_damage(s)
 assert s==before and select(result)==entry['legacy_model'],s
 native=result['panel_native_finalization'];assert len(native['fields'])==17 and not native['complete_native_panel'] and native['actual_panel'] is None
 assert '_panel_native_terms' not in result['estimate']
 if 'calibration' in entry:
  panel=panel_layers(s);assert {k:panel[k] for k in entry['calibration']}==entry['calibration'],s
  assert panel['native_panel_reference']==native,s
 assert any(b['id']=='panel_native_finalization' for b in result['report']['sections'])
 rows.append({'scenario':s,'legacy_models_unchanged':True,'native_fields':len(native['fields']),
              'main_calibration_exact_reference_reuse':'calibration' in entry,'actual_native_complete':False})
record={'kind':'ACTUAL_PUBLIC_MAIN_PATH_BEFORE_AFTER_COMPARISON','passed':True,'public_cases':len(rows),'cases':rows,
 'before_receipt_sha256':hashlib.sha256((r/'.cache/section283-main-integration/before-model.json').read_bytes()).hexdigest(),
 'private_state_used':False,'game_or_chat_operated':False,'source_maths_reference_not_actual_panel':True}
dest=r/'.cache/section283-main-integration/after-model-first.json';assert not dest.exists();dest.write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'passed':True,'public_cases':len(rows),'legacy_outputs_unchanged':True,'native_main_reference_reused_by_calibration':True}))
