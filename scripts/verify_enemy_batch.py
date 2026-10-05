"""All skill outputs against identical defense/resistance, with independent boss reduction."""
import json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from rouge.catalog import catalog,stage_previews
from rouge.damage import calculate_damage
count=0
for op,p in catalog()['operators'].items():
    for number in range(1,len(p['skills'])+1):
        args={'operator':op,'skill':number,'skill_rank':10,'timing_mode':'frames',
            'target_enemy':{'stage_id':'ro6_b_3','enemy_id':'enemy_2143_shwksc','level':0}}
        ten=calculate_damage({**args,'run_config':{'difficulty':{'value':10},'zone':{'id':'zone_3'}}})
        eleven=calculate_damage({**args,'run_config':{'difficulty':{'value':11},'zone':{'id':'zone_3'}}})
        for key in ('total_damage','cycle_damage','cycle_dps','window_damage'):
            a=ten['estimate']['skill'].get(key);b=eleven['estimate']['skill'].get(key)
            if a is not None and op!='char_4204_mantra':assert b is not None and abs(b-a*.8)<=max(1e-6,abs(a)*1e-9),(op,number,key,a,b)
        if op=='char_4204_mantra':
            for a,b in zip(ten.get('components',[]),eleven.get('components',[])):
                if a['damage_type'] in ('physical','magic','true','elemental'):
                    assert abs(b['per_hit']-a['per_hit']*.8)<1e-6,(op,number,a['name'])
            if number==2:
                # Actual-damage neural buildup changes burst thresholds/hit counts;
                # final total cannot be obtained by multiplying an old total.
                assert abs(eleven['total_damage']-42562.08)<1e-6
                assert abs(ten['total_damage']-59768.85)<1e-6
        for key in ('initial_seconds','recharge_seconds','cycle_seconds'):
            assert ten['estimate']['skill'].get(key)==eleven['estimate']['skill'].get(key),(op,number,key)
        for a,b in zip(ten.get('components',[]),eleven.get('components',[])):
            if a['damage_type']=='healing':
                ratio=.8 if '伤害转治疗' in a['name'] else 1
                assert abs(b['total']-a['total']*ratio)<1e-6,(op,number,a['name'])
        if op not in ('char_1037_amiya3','char_1044_hsgma2'):
            for key in ('total_healing','cycle_healing','cycle_hps'):
                assert ten['estimate']['skill'].get(key)==eleven['estimate']['skill'].get(key),(op,number,key)
        count+=1
assert count==87
refs=sum(len(p['possible_enemies']) for p in stage_previews().values())
classes={e['level_type'] for p in stage_previews().values() for e in p['possible_enemies']}
assert classes<= {'NORMAL','ELITE','BOSS',None},classes
unknown=sum(e['level_type'] is None for p in stage_previews().values() for e in p['possible_enemies'])
receipt={'version':'0.15.0','verified_at':time.time(),'skill_profiles':count,'enemy_references':refs,
    'stages':len(stage_previews()),'boss_reduction_independent':True,'direct_healing_and_timing_unchanged':True,
    'unconfirmed_category_references':unknown,
    'damage_based_healing_tracks_actual_damage':True,
    'damage_based_buildup_recomputes_burst_counts':True,
    'chat_requests':0,'limits':['档案情景验证，不代表全部敌人已实机采样。','敌人自身动态机制、专属攻击效果及未覆盖关卡脚本仍待接入。']}
(root/'ENEMY_BATCH_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
