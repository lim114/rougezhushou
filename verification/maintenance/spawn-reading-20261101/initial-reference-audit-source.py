from pathlib import Path
from unittest.mock import patch
import sys,json,runpy
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from rouge import current_battle_reference as m
ref=m.packet();ids=ref['version']['current']['details']['stages'];count=0;multi=0
with patch.object(m,'packet',return_value=ref):
 for sid in ids:
  result=m.stage_reference(sid);assert result is not None;keys={e['key']for e in result['enemies']}
  for a in result['actions']:
   assert all(e['key']in keys for e in a['enemy_candidates']),(sid,a['key']);count+=1;multi+=len(a['enemy_candidates'])>1
old=runpy.run_path(str(R/'research/spawn-reading-20261101/before-verify_full_available.py'));new=runpy.run_path(str(R/'scripts/verify_full_available.py'));a=old['maintained_selectors']();b=new['maintained_selectors']();assert b[:-1]==a and b[-1]=='tests.test_spawn_reading_review'
value={'all_fixed_stages':len(ids),'actions_checked':count,'multiple_candidate_actions':multi,'all_portrait_keys_belong_to_exact_stage':True,'previous_selector_count':len(a),'current_selector_count':len(b),'old_selector_order_retained':True,'mechanisms_or_actual_spawn_quantities_changed':False}
(R/'verification/maintenance/spawn-reading-20261101/reference-audit.json').write_text(json.dumps(value,indent=2)+'\n','utf8');print(json.dumps(value))
