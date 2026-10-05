"""Extract only animation event numbers; no downloaded code is executed."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'.cache/research/timing/arkdps_data_collection/customdata/dps_anim.json'
COMMIT='31269be4ca10124ca3f994ab33382dfc3d502991'
URL=f'https://github.com/xulai1001/arkdps_data_collection/blob/{COMMIT}/customdata/dps_anim.json'
raw=json.loads(SOURCE.read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'rouge/data/catalog.json').read_text(encoding='utf-8'))
bindings={
 'char_133_mm':{1:'Attack_Loop',2:'Skill_Loop'},
 'char_1037_amiya3':{1:'Skill_1_Attack',2:'Skill_2_Attack'},
 'char_2025_shu':{2:'Skill_2_Attack',3:'Skill_3_Attack_1'},
 'char_328_cammou':{2:'Skill2_Loop'},
 'char_1038_whitw2':{1:'Skill_1_Loop',2:'Skill_2_Loop',3:'Skill_3_Loop'},
 'char_1041_angel2':{1:'Skill_1_Loop',2:'Skill_2_Loop',3:'Skill_3_Loop'},
 'char_1035_wisdel':{1:'Skill_1',2:'Skill_2_Loop',3:'Skill_3_Loop'},
 'char_4087_ines':{2:'Skill_2_Attack'},
 'char_4107_vrdant':{2:'Skill_2_Loop'},
 'char_437_mizuki':{2:'Skill_2_Loop'},
}

def extract(anims,name):
    a=anims.get(name)
    if not isinstance(a,dict) or 'OnAttack' not in a:return None
    return {'animation':name,'windup_frames':a['OnAttack'],
        'recovery_frames':max(0,a['duration']-a['OnAttack']),
        'animation_frames':a['duration'],'source':URL}

operators={}
for key,p in catalog['operators'].items():
    anims=raw.get(p['id'],{})
    normal=next((extract(anims,n) for n in ('Attack','Attack_Loop','Attack1','Attack_1','Attack_A') if extract(anims,n)),None)
    skills={}
    for n,name in bindings.get(p['id'],{}).items():
        a=extract(anims,name)
        if a:skills[str(n)]=a
    operators[key]={'id':p['id'],'normal':normal,'skills':skills,'binding_status':'reference_only',
        'missing':'客户端攻击模板、皮肤、技能重置/阻回绑定未经实测'}
output={'fps':30,'source_commit':COMMIT,'source_url':URL,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'operators':operators,'limits':'提取的是Spine动画事件值；并非所有实际伤害/多段判定均由单个OnAttack事件触发。'}
(ROOT/'rouge/data/timing-profiles.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'normal_animation_profiles':sum(bool(p['normal']) for p in operators.values()),
    'explicit_skill_animation_references':sum(len(p['skills']) for p in operators.values())}))
