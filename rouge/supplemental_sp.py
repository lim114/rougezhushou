"""SP parameter arithmetic; intentionally no charge/acquisition/end clock."""
from .relics import effective_skill,recharge_requirement,mechanics

SP_KINDS={'initial_sp','sp_cost_factor','end_sp'}


def supported_sp(rule):
    return bool(rule.get('_verified_rule') and not rule.get('token_only') and rule['kind'] in SP_KINDS)


def sp_reference(skill,rules,records):
    selected=[r for r in rules if supported_sp(r)]
    scenario={'_relic_rules':selected}
    adjusted=effective_skill({'sp_cost':skill['spData']['spCost'],'initial_sp':skill['spData']['initSp']},scenario)
    cost_pending=[];initial_pending=[];end_pending=[]
    for record in records:
        entry=mechanics()['relics'].get(record['id']) or mechanics()['char_buffs'].get(record['id'])
        if not entry or not (record['pending'] or record['missing_conditions']):continue
        for key,kind in ((cost_pending,'sp_cost_factor'),(initial_pending,'initial_sp'),(end_pending,'end_sp')):
            if any(e['kind']==kind for e in entry['effects']):key.append(record['name'])
    cost=None if cost_pending else adjusted['sp_cost']
    initial=None if initial_pending else adjusted['initial_sp']
    end=None if end_pending else sum(r['value'] for r in selected if r['kind']=='end_sp')
    return {'sp_type':skill['spData']['spType'],'cost_parameter':cost,'initial_parameter':initial,
        'initial_requirement':max(0,cost-initial) if cost is not None and initial is not None else None,
        'end_return_parameter':end,
        'recharge_requirement':recharge_requirement(scenario,cost) if cost is not None and end is not None else None,
        'unresolved_cost_sources':cost_pending,'unresolved_initial_sources':initial_pending,
        'unresolved_end_sources':end_pending,'initial_seconds':None,'recharge_seconds':None,'cycle_seconds':None}
