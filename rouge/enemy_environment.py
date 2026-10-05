"""Resolve an explicit stage enemy; never infer enemy identity from a boss stage."""
import json,math
from pathlib import Path
from functools import lru_cache
from .catalog import catalog,stage_previews
from .run_config import config_data

@lru_cache(maxsize=1)
def difficulty_rules():
    return json.loads((Path(__file__).with_name('data')/'enemy-difficulty-rules.json').read_text(encoding='utf-8'))

def damage_factor(scenario,dtype):
    return scenario.get('_run_damage_factor',1)*scenario.get('_enemy_type_factors',{}).get(dtype,1)

def resolve_enemy(scenario,resolution):
    # Weight may only come from the selected, pinned enemy reference.
    scenario.pop('enemy_weight',None)
    target=scenario.get('target_enemy')
    if not target:return
    if not isinstance(target,dict):raise ValueError('目标敌人需要关卡、敌人ID及引用等级。')
    sid=target.get('stage_id');stage=catalog()['stages'].get(sid);preview=stage_previews().get(sid)
    if not stage or not preview:raise ValueError('目标关卡没有固定敌人档案。')
    candidates=[e for e in preview['possible_enemies'] if e['id']==target.get('enemy_id') and e['level']==target.get('level')]
    if len(candidates)!=1:raise ValueError('目标敌人身份/等级必须与关卡引用唯一匹配。')
    record=candidates[0];stats=dict(record['reference_stats'])
    for key in ('maxHp','atk','def','magicResistance'):
        if not isinstance(stats.get(key),(int,float)) or not math.isfinite(stats[key]) or stats[key]<0:
            raise ValueError('目标敌人属性不完整。')
    enemy={**target,'name':record['name'],'stage_name':stage['name'],'stage_difficulty':stage['difficulty'],
        'level_type':record['level_type'],'reference_stats':dict(stats),'stats':stats,'steps':[],
        'damage_factor':1,'pending':[],'source':config_data()['source_url']}
    resolution['enemy']=enemy
    def multiply(label,values):
        for key,value in values.items():stats[key]*=value
        enemy['steps'].append({'label':label,'factors':values})
    for rune in preview['runes']:
        if rune['difficultyMask'] not in (stage['difficulty'],'ALL'):continue
        if rune['key']=='enemy_attribute_mul':
            if rune['professionMask']!=1023 or rune['buildableMask']!='ALL':
                enemy['pending'].append('关卡属性修正的目标范围尚未覆盖。');continue
            keys={'atk':'atk','def':'def','max_hp':'maxHp','magic_resistance':'magicResistance'}
            values={keys[b['key']]:b['value'] for b in rune['blackboard'] if b['key'] in keys}
            if len(values)!=len(rune['blackboard']):enemy['pending'].append('关卡存在未覆盖的属性修正字段。')
            multiply('关卡 '+stage['difficulty'],values)
        elif rune['key']!='level_hidden_group_enable':
            enemy['pending'].append('关卡脚本修正待核验：'+rune['key'])
    if preview['global_buffs']:enemy['pending'].append('关卡全局脚本效果尚未逐项计算。')
    difficulty=resolution.get('difficulty')
    if difficulty:
        grade=difficulty['value']
        rules=difficulty_rules()
        low=rules['exclusive_low_grades'].get(str(grade))
        if low:
            multiply('当前低难度独立减益（不累计）',low)
            enemy['steps'][-1]['evidence']={k:rules[k] for k in ('source_url','verification','source_note')}
        if grade>=5:multiply('保密等级5+生命',{'maxHp':1.3})
        if grade>=8 and record['level_type'] in ('ELITE','BOSS'):multiply('保密等级8+精英/领袖攻击',{'atk':1.15})
        if grade>=11 and record['level_type']=='BOSS':
            enemy['damage_factor']=.8
            enemy['steps'].append({'label':'保密等级11+领袖受伤降低20%','damage_factor':.8})
        for rule in rules['enemy_thresholds']:
            if grade>=rule['grade'] and record['id']==rule['enemy_id']:
                multiply('保密等级'+str(rule['grade'])+'+专属属性',rule['factors'])
                enemy['steps'][-1]['evidence']={k:rules[k] for k in ('source_url','verification','source_note')}
                enemy['pending'].append(rule['pending'])
        rate=config_data()['difficulties'][str(grade)]['bossValue']/100
        zone=(scenario.get('run_config') or {}).get('zone')
        main=(zone or {}).get('main_zone_index')
        if zone and zone.get('id') in config_data()['zones'] and zone['id'].split('_')[1].isdigit():
            # zone_4 and zone_4_1 are the same main-region depth.
            main=int(zone['id'].split('_')[1])
        if rate and isinstance(main,int) and not isinstance(main,bool) and main in range(1,7):multiply('区域增长（主区域含第1层，黑潭不新增层数）',{'maxHp':(1+rate)**main,'atk':(1+rate)**main})
        elif rate:enemy['pending'].append('主区域深度尚未确认，未套用区域增长。')
    else:enemy['pending'].append('本局保密等级尚未确认，未套用难度修正。')
    if record['level_type'] not in ('NORMAL','ELITE','BOSS'):enemy['pending'].append('敌人类别未确认。')
    if record['id']=='enemy_2148_shorbb':
        rule=difficulty_rules()['orb_active'];mode=target.get('orb_mode','unknown')
        if mode in rule['modes']:
            factor=rule['modes'][mode]
            enemy['type_factors']={'physical':factor,'magic':factor}
            scenario['_enemy_type_factors']=enemy['type_factors']
            enemy['steps'].append({'label':'源阶方全程行动模式；所有伤害来源均'+('在目标占据列内' if mode=='active_same_column' else '在目标占据列外'),
                'type_factors':enemy['type_factors'],'evidence':{k:rule[k] for k in ('source_url','verification','source_note')}})
            resolution['notes'].append('源阶方使用明确选择的固定行动模式与统一来源列情景；未自动读取站位，不模拟激活、无敌、模式切换或混合来源列。')
        elif mode=='unknown':
            enemy['pending'].append('源阶方阶段和来源列未确认；当前数值仅为未套用自身减伤的参考，不是实际承伤估计。')
        else:raise ValueError('源阶方行动情景无效。')
    # Identity-derived state wins over stale manual relic or operator options.
    scenario['enemy_defense']=stats['def'];scenario['enemy_resistance']=stats['magicResistance']
    weight=stats.get('massLevel')
    if isinstance(weight,(int,float)) and not isinstance(weight,bool) and math.isfinite(weight):
        scenario['enemy_weight']=weight
    scenario['enemy_is_boss']=record['level_type']=='BOSS';scenario['enemy_level_type']=record['level_type']
    scenario['_run_damage_factor']=enemy['damage_factor']
    resolution['pending'].extend(enemy['pending'])
    resolution['notes'].append('敌人候选不保证出场；当前以持续存活目标计算，未模拟敌人自身技能、阶段、阻挡/环境变化和实际死亡时刻。')
