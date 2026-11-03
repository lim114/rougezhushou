"""Reuse proven single healing/regen factors; never synthesize tick events."""
from .relics import mechanics
from .relic_healing_factors import healing_factor,regeneration_factor,COMPOSITION_EVIDENCE

HEAL_KINDS={'self_heal','heal_boost'}
REGEN_KINDS={'regeneration','regeneration_hp_ratio','regeneration_factor'}


def supported_healing(rule,kind):
    return bool(rule.get('_verified_rule') and not rule.get('token_only') and
        (rule['kind'] in REGEN_KINDS or rule['kind']=='healing_factor' and kind in HEAL_KINDS))


def apply_healing_reference(result,rules,records,kind):
    selected=[r for r in rules if supported_healing(r,kind)]
    healing=[r for r in selected if r['kind']=='healing_factor']
    regeneration=[r for r in selected if r['kind']=='regeneration_factor']
    pending_healing=[];pending_regen=[]
    for record in records:
        entry=mechanics()['relics'].get(record['id']) or mechanics()['char_buffs'].get(record['id'])
        if not entry or not (record['pending'] or record['missing_conditions']):continue
        if kind in HEAL_KINDS and any(e['kind']=='healing_factor' for e in entry['effects']):pending_healing.append(record['name'])
        if any(e['kind'] in REGEN_KINDS for e in entry['effects']):pending_regen.append(record['name'])
    factor=None if pending_healing else healing_factor(healing)
    regen_factor=None if pending_regen else regeneration_factor(regeneration)
    flat=sum(r['value'] for r in selected if r['kind']=='regeneration')
    ratio=sum(r['value'] for r in selected if r['kind']=='regeneration_hp_ratio')
    rate=(flat+result['attributes']['hp']*ratio)*regen_factor if regen_factor is not None else None
    if kind in HEAL_KINDS:
        for row in result['rows']:
            if row['name'] in ('普通单次治疗','技能单次治疗'):
                row['value']=row['value']*factor if factor is not None else None
                if row['declared_total_applicable']:
                    row['declared_total']=row['value']*result['preview']['count'] if row['value'] is not None else None
        amount=next(r['value'] for r in result['rows'] if r['name']=='技能单次治疗')
        potential=amount*result['preview']['count'] if amount is not None else None
        effective=min(potential,result['preview']['missing_hp']) if potential is not None else None
        for row in result['rows']:
            if row['name']=='声明次数有效治疗合计':row['value']=effective
            if row['name']=='声明次数过量治疗合计':row['value']=potential-effective if potential is not None else None
    if flat or ratio or pending_regen:
        result['rows'].append({'name':'藏品常态生命回复','value':rate,'unit':'生命/秒',
                              'declared_total':None,'declared_total_applicable':False})
    return {'healing_factor':factor,'regeneration_factor':regen_factor,'flat_regeneration':flat,
        'composition_evidence':COMPOSITION_EVIDENCE if len({r['relic_id']for r in healing+regeneration})>1 else None,
        'healing_source_ids':list(dict.fromkeys(r['relic_id'] for r in healing)),
        'regeneration_source_ids':list(dict.fromkeys(r['relic_id'] for r in regeneration)),
        'hp_regeneration_ratio':ratio,'relic_regeneration_rate':rate,'pending_healing':pending_healing,
        'pending_regeneration':pending_regen,'actual_ticks_verified':False}
