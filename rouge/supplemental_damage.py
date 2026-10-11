"""Qualified target DEF/penetration and single damage-scale references."""
from .relics import mechanics


def supported_damage(rule):
    return bool(rule.get('_verified_rule') and not rule.get('token_only') and (
        rule['kind']=='enemy_def_delta' or
        rule['kind']=='defense_penetration' and rule.get('relic_id')=='rogue_6_from_relic_5' or
        rule['kind']=='damage_taken' and rule.get('source_buff_key')=='global_buff_stack_base_one'
            and rule.get('damage_type') in ('physical','magic','true')))


def damage_reference(scenario,rules,records):
    selected=[r for r in rules if supported_damage(r)]
    penetration=sum(r['value'] for r in selected if r['kind']=='defense_penetration')
    pending_defense=[];warnings=[]
    for record in records:
        entry=mechanics()['relics'].get(record['id']) or mechanics()['char_buffs'].get(record['id'])
        if entry and (record['pending'] or record['missing_conditions']) and any(e['kind']=='enemy_def_delta' for e in entry['effects']):
            pending_defense.append(record['name'])
    factors={}
    for dtype in ('physical','magic','true'):
        values=[r['value'] for r in selected if r['kind']=='damage_taken' and r['damage_type']==dtype]
        factors[dtype]=None if len(values)>1 else 1+values[0] if values else 1
        if len(values)>1:warnings.append('同类型多来源受伤倍率未在补充干员路径取得组合证据；'+dtype+'伤害组合未知。')
    return {'effective_target_defense':None if pending_defense else scenario['enemy_defense']*max(0,1-penetration),
        'penetration_ratio':penetration,'damage_factors':factors,'pending_defense':pending_defense,'warnings':warnings}


def apply_damage_reference(result,reference):
    for row in result['rows']:
        dtype={'物理伤害':'physical','期望伤害':'physical','法术伤害':'magic'}.get(row['unit'])
        if dtype is None:continue
        factor=reference['damage_factors'][dtype]
        row['value']=(None if factor is None or dtype=='physical' and reference['pending_defense'] else
                      row['value']*factor if row['value'] is not None else None)
        if row['declared_total_applicable']:
            row['declared_total']=row['value']*result['preview']['count'] if row['value'] is not None else None
