import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'draft'))
from rouge.damage import calculate_damage
cases=[
 ('default_s2',{'operator':'char_196_sunbr','skill':2,'base_attack':1000,'window_seconds':11}),
 ('back_skill_stage',{'operator':'char_196_sunbr','skill':2,'base_attack':1000,'window_seconds':11,'timing':{'animation_reference':'char_196_sunbr:Back:Attack'}}),
 ('back_normal_s1',{'operator':'char_196_sunbr','skill':1,'base_attack':1000,'timing':{'normal_animation_reference':'char_196_sunbr:Back:Attack'}}),
 ('generic_skill_rejected',{'operator':'char_196_sunbr','skill':2,'timing':{'animation_reference':'char_196_sunbr:Back:Skill'}}),
]
items=[]
for label,scenario in cases:
 try:
  result=calculate_damage(scenario)
  items.append({'label':label,'scenario':scenario,'accepted':True,'result':result})
  print(json.dumps({'label':label,'healing':result.get('total_healing'),'timing':result.get('timing'),'estimate_skill':result.get('estimate',{}).get('skill')},ensure_ascii=False))
 except Exception as e:
  items.append({'label':label,'scenario':scenario,'accepted':False,'error_type':type(e).__name__,'error':str(e)})
  print(json.dumps({'label':label,'error':str(e)},ensure_ascii=False))
p=Path(__file__).resolve().parent/'initial-public-inspection.json'
p.write_text(json.dumps({'version':1,'API_calls':len(cases),'items':items},ensure_ascii=False,indent=2)+'\n')
