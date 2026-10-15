from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import json,sys,hashlib
r=Path.cwd();sys.path.insert(0,str(r))
from rouge import calibration as c
from rouge.catalog import catalog
from rouge.damage import calculate_damage
observed=[];calls=[]
def wrapped(s):
 v=calculate_damage(s);calls.append((deepcopy(s),v));return v
for op,p in catalog()['operators'].items():
 s={'operator':op,'skill':1};before=deepcopy(s)
 with patch.object(c,'calculate_damage',side_effect=wrapped):
  start=len(calls);m=c.skill_matrix(s,operators=[op]);new=calls[start:]
 assert s==before and len(m['rows'])==len(p['skills'])==len(new)
 for row,(sc,result) in zip(m['rows'],new):
  assert row['native_panel_reference']==result['panel_native_finalization']
  assert row['native_panel_reference'] is not result['panel_native_finalization']
  assert row['declared_components']==result['components']
  assert not row['native_verified'] and not row['native_clock_verified']
  assert row['full_skill_damage'] in (None,0) and row['full_skill_healing'] in (None,0)
  observed.append({'operator_key':op,'skill_id':row['skill_id'],'skill':row['skill'],'same_main_native_reference':True,'actual_totals_not_certified':True})
 with patch.object(c,'calculate_damage',side_effect=wrapped):
  start=len(calls);panel=c.panel_layers(s);new=calls[start:]
 assert len(new)==1 and panel['native_panel_reference']==new[0][1]['panel_native_finalization']
 assert len(panel['native_panel_reference']['fields'])==17
out=Path('.cache/section285-preparation/actual-catalog-main-reuse-87.json');assert not out.exists();out.write_text(json.dumps({'kind':'PUBLIC_ACTUAL_MODEL_EXECUTION_NOT_GAME','passed':True,'catalog_keys':32,'skill_rows':87,'main_calculations':len(calls),'actual_panel_calls':32,'rows':observed,'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ('rouge/calibration.py','rouge/offline_tools_view.py','tests/test_extended_calibration_285.py','rouge/operator_engine.py','rouge/panel_native_bridge.py')},'private_state_used':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print({'passed':True,'catalog_keys':32,'skills':len(observed),'real_main_calls':len(calls)})
