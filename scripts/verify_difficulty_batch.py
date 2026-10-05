"""Pinned mechanism evidence and all supported skills through calculate_damage."""
import json,hashlib,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

dbfile=root/'.cache/game-data/levels/enemydata/enemy_database.json'
database=json.loads(dbfile.read_text(encoding='utf-8'))
orb=next(e for e in database['enemies'] if e['Key']=='enemy_2148_shorbb')
bb={b['key']:b['value'] for b in orb['Value'][0]['enemyData']['talentBlackboard']}
assert bb['DamageScale.damage_scale']==.3 and bb['DamageScale.damage_scale_in_range']==.7
checks=0;nonlinear=[]
for op,profile in catalog()['operators'].items():
    for number in range(1,len(profile['skills'])+1):
        args={'operator':op,'skill':number,'skill_rank':10,'timing_mode':'frames',
              'target_enemy':{'stage_id':'ro6_b_5','enemy_id':'enemy_2148_shorbb','level':0},
              'run_config':{'difficulty':{'value':11}}}
        neutral=calculate_damage(args)
        assert any('阶段和来源列未确认' in warning for warning in neutral['warnings'])
        for mode,factor in [('active_same_column',.7),('active_other_column',.3)]:
            actual=calculate_damage({**args,'target_enemy':{**args['target_enemy'],'orb_mode':mode}})
            for key in ('initial_seconds','recharge_seconds','cycle_seconds'):
                assert actual['estimate']['skill'][key]==neutral['estimate']['skill'][key],(op,number,key)
            # Compare per-hit values, not a post-hoc scaling of mixed totals.
            before={(c['name'],c['damage_type']):c for c in neutral.get('components',[]) if 'per_hit' in c}
            after={(c['name'],c['damage_type']):c for c in actual.get('components',[]) if 'per_hit' in c}
            for (name,dtype),value in before.items():
                if dtype not in ('physical','magic','true','elemental'):continue
                if (name,dtype) not in after:continue
                expected=value['per_hit']*(factor if dtype in ('physical','magic') else 1)
                assert abs(after[(name,dtype)]['per_hit']-expected)<1e-6,(op,number,name,dtype)
            for value in actual.get('components',[]):
                if value['damage_type']=='healing' and '伤害转治疗' not in value['name']:
                    original=next(c for c in neutral['components'] if c['name']==value['name'])
                    assert abs(value['total']-original['total'])<1e-6,(op,number,value['name'])
            if op=='char_4204_mantra' and number==2:
                nonlinear.append({'mode':mode,'total':actual['total_damage'],
                    'burst_count':next(c['hits'] for c in actual['components'] if c['name']=='神经损伤爆发')})
            checks+=1
assert checks==174
receipt={'version':'0.15.0','verified_at':time.time(),'skill_profiles':87,'orb_skill_scenarios':checks,
    'unknown_context_reference_labelled':True,'per_hit_type_specific':True,'timing_and_direct_healing_preserved':True,
    'buildup_recomputed':nonlinear,'chat_requests':0,
    'primary_evidence':{'enemy_database_sha256':hashlib.sha256(dbfile.read_bytes()).hexdigest(),
        'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','orb_blackboard':{k:bb[k] for k in ['DamageScale.damage_scale','DamageScale.damage_scale_in_range']}},
    'rules_sha256':hashlib.sha256((root/'rouge/data/enemy-difficulty-rules.json').read_bytes()).hexdigest(),
    'limitations':['情景计算，不是敌人阶段/站位自动识别或实机准确率证明。','固定行动模式且所有来源使用同一种列关系；无敌、模式切换和混合来源列未模拟。']}
(root/'DIFFICULTY_0.15_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
