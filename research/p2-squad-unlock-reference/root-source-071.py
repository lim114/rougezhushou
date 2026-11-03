import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.run_config import config_data
from rouge.technology import technology_gates,technology_nodes
from rouge.squad_unlock_reference import squad_unlock_reference
source=Path('/workspace/.continuation/p2-run-environment-audit-after-070/roguelike_topic_table.json');b=source.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
raw=json.loads(b);details=raw['details']['rogue_6'];common=raw['customizeData']['rogue_6']['commonDevelopment'];data=config_data()
strict=lambda obj:json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
expected={key:{**band,**details['items'][key],'buffs':details['relics'][key]['buffs']} for key,band in details['bandRef'].items()}
assert strict(data['squads'])==strict(expected)
assert strict(technology_gates())==strict(common['developmentsDifficultyNodeInfos'])
assert strict(technology_nodes())==strict(list(common['developments'].values()))
checks=0;nodes=0
for key,band in details['bandRef'].items():
 ref=squad_unlock_reference(key)
 if band['bandLevel']!=1:assert ref is None;continue
 assert ref['unlock_condition_reference']==details['items'][key]['unlockCondDesc']
 assert ref['base_squad_id']==band['normalBandId'];assert ref['account_unlocked'] is None and ref['actual_activation'] is None
 if ref['technology_node_reference']:
  node=common['developments'][ref['technology_node_reference']['id']]
  assert ref['unlock_condition_reference']=='生命游戏中激活“'+node['buffName']+'”'
  assert '“'+details['items'][key]['name']+'”效果提升' in node['rawDesc'];nodes+=1
 else:assert key=='rogue_6_band_22' and ref['unlock_condition_reference']=='机械师提升至精英二阶段'
 checks+=1
assert checks==7 and nodes==6
print(json.dumps({'section':71,'passed':True,'fresh_full_original_hash':sha,'all_squad_records_strict_json':22,'all_technology_nodes_strict_json':57,'all_gates_strict_json':3,'strengthened_source_conditions':checks,'bidirectional_named_node_bindings':nodes,'account_or_actual_activation_inferred':False,'native_validation':False}))
