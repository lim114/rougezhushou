import json
import math
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def catalog():
    return json.loads((Path(__file__).parent / 'data' / 'catalog.json').read_text(encoding='utf-8'))

@lru_cache(maxsize=1)
def tactical_tools():
    return json.loads((Path(__file__).parent/'data/inventory-items.json').read_text(encoding='utf-8'))['active_tools']

@lru_cache(maxsize=1)
def operator_profiles():
    profiles=json.loads((Path(__file__).parent/'data/operator-profiles.json').read_text(encoding='utf-8'))['operators']
    for key,profile in catalog()['operators'].items():
        profiles[key]={**profiles[key],**profile}
    return profiles

@lru_cache(maxsize=1)
def stage_previews():
    return json.loads((Path(__file__).parent / 'data' / 'previews.json').read_text(encoding='utf-8'))['stages']

def operator_attack(operator, elite=2, level=None, trust=100):
    return operator_attributes(operator,elite,level,trust)['attack']

def operator_attributes(operator, elite=2, level=None, trust=100, potential=1,module_id=None,module_level=0):
    profile = operator_profiles()[operator]
    if not isinstance(elite,int) or not 0<=elite<len(profile['phases']):
        raise ValueError('精英阶段需要为 0、1 或 2。')
    phase = profile['phases'][elite]
    level = phase['max_level'] if level is None else level
    if not isinstance(level,int) or not 1 <= level <= phase['max_level'] or not math.isfinite(trust) or not 0 <= trust <= 100:
        raise ValueError('等级或信赖超出范围（信赖按加成进度 0–100%）。')
    if not isinstance(potential,int) or not 1<=potential<=6:
        raise ValueError('潜能需要为 1–6。')
    first, last = phase['frames'][0], phase['frames'][-1]
    fraction = (level - first['level']) / (last['level'] - first['level']) if last['level'] != first['level'] else 0
    stats={field:first[field]+fraction*(last[field]-first[field]) for field in last if field!='level'}
    for field in ('hp','attack','defense'):
        stats[field]=math.floor(stats[field]+.5)+math.floor(profile['trust_stats'][field]*trust/100+.5)
    mapping={'ATK':'attack','MAX_HP':'hp','DEF':'defense','MAGIC_RESISTANCE':'resistance',
             'RESPAWN_TIME':'redeploy_seconds','ATTACK_SPEED':'attack_speed','BLOCK_CNT':'block_count','COST':'deployment_cost'}
    for modifiers in profile['potential_bonuses'][:potential-1]:
        for modifier in modifiers:
            field=mapping.get(modifier['attributeType'])
            if field and modifier['formulaItem']=='ADDITION':stats[field]+=modifier['value']
    if module_id:
        module=next((m for m in profile['modules'] if m['id']==module_id),None)
        if not module or not isinstance(module_level,int) or not 1<=module_level<=len(module['levels']):
            raise ValueError('模组身份或等级尚无可用规则。')
        if elite>=module['unlock_elite'] and level>=module['unlock_level']:
            for attr,value in module['levels'][module_level-1]['attributes'].items():
                field={'atk':'attack','def':'defense','max_hp':'hp','magic_resistance':'resistance','attack_speed':'attack_speed'}.get(attr)
                if field:stats[field]+=value
    return stats
