from pathlib import Path
from collections import Counter
from unittest.mock import patch
from hashlib import sha256
import json,sys,time
R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/current-enemy-forecast-review-20261031/matrix';out.mkdir(parents=True,exist_ok=False)
from rouge import current_battle_reference as current, expansion_reference as version
from rouge.current_enemy_forecast import forecasts
from rouge.battle_preview import enemy_preview
from rouge.run_config import config_data
p=current.packet();assert p is not None;config={'difficulty':{'value':15},'zone':{'id':'zone_6'}};rows=[];counts=Counter();started=time.perf_counter()
# One actually validated complete pinned packet is held for this offline
# component matrix; this is not a claim that repeated runtime I/O was measured.
with patch.object(current,'packet',return_value=p):
 for sid in p['version']['current']['details']['stages']:
  result=current.stage_reference(sid);projection=forecasts(result,config)
  assert len(projection)==len(result['enemies'])
  for enemy in result['enemies']:
   value=projection[enemy['key']];component=value['environment_component'];qualified=component is not None
   if qualified:
    original=enemy_preview(sid,enemy['id'],enemy['level'],config)
    assert component=={key:original['environment']['stats'][key]for key in('maxHp','atk','def','magicResistance')}
   assert value['complete_current_total']is None and not value['actual_gameplay_verified']
   counts['qualified'if qualified else'unqualified']+=1
   rows.append({'stage_id':sid,'reference_key':enemy['key'],'enemy_id':enemy['id'],'level':enemy['level'],'environment_component':component,'original_model_equal':True if qualified else None,'pending':value['pending'],'complete_current_total':None})
assert counts['qualified']==1050 and counts['unqualified']==1010 and len(rows)==2060,counts
difficulties=[]
for profile in p['version']['current']['details']['difficulties']:
 if profile['modeDifficulty']=='NORMAL'and str(profile['grade'])in config_data()['difficulties']:
  old=config_data()['difficulties'][str(profile['grade'])]
  equal=all(profile[key]==old[key]for key in('grade','modeDifficulty','bossValue','ruleDesc'));assert equal
  difficulties.append({'grade':profile['grade'],'four_fields_equal':equal})
result={'passed':True,'current_game_commit':version.NEW_COMMIT,'current_manifest':current.MANIFEST_SHA256,'stage_count':184,'reference_count':len(rows),'counts':dict(counts),'difficulty_profiles':difficulties,'conditions':config,'elapsed_seconds':time.perf_counter()-started,'rows':rows,'source_selection':'One source-verified public packet, no private state, capture or server inference.','not_independent_mechanism_calibration':True,'complete_current_totals_unknown':True,'game_operated':False,'chat_sent':False}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':True,'stages':184,'references':len(rows),'counts':dict(counts),'seconds':result['elapsed_seconds']},ensure_ascii=False))
