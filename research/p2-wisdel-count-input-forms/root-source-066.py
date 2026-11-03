import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS
receipt=json.loads(Path('/workspace/.continuation/p2-wisdel-integer-report-audit-066/final-source-closure.json').read_text())
raw={}
for name,r in receipt['sources'].items():
 b=Path(r['path']).read_bytes(); assert hashlib.sha256(b).hexdigest()==r['sha256']; raw[name]=json.loads(b)
op='char_1035_wisdel';token='token_10035_wisdel_wward';p=catalog()['operators'][op]
checks=0
for i,s in enumerate(p['skills']):
 assert raw['character_table'][op]['skills'][i]['skillId']==s['id']
 for a,b in zip(s['levels'],raw['skill_table'][s['id']]['levels']):
  assert a['values']=={r['key']:r['value'] for r in b['blackboard']};checks+=1
mapping={'maxHp':'hp','atk':'attack','def':'defense','magicResistance':'resistance','attackSpeed':'attack_speed','baseAttackTime':'interval','blockCnt':'block_count','cost':'deployment_cost','respawnTime':'redeploy_seconds'}
frames=0
for phase,source in zip(p['tokens'][token]['phases'],raw['character_table'][token]['phases']):
 for frame,keyframe in zip(phase['frames'],source['attributesKeyFrames']):
  assert frame['level']==keyframe['level']
  for k,v in mapping.items():assert frame[v]==keyframe['data'][k]
  frames+=1
assert [list(r[:4])+[list(r[4])] for r in OPTIONS[op] if r[0] in ('ghost_count','ghost_casts')]==receipt['controls']
print(json.dumps({'passed':True,'skill_ranks':checks,'token_frames':frames,'fields_per_token_frame':9,'actual_raw_sources_rehashed':True,'current_checkout_catalog_controls_match':True,'native_validation':False}))
