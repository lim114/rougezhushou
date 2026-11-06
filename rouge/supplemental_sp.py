"""SP parameter arithmetic; intentionally no charge/acquisition/end clock."""
from .relics import effective_skill,recharge_requirement,mechanics

SP_KINDS={'initial_sp','sp_cost_factor','end_sp'}
NATURAL_SP_SOURCES={
    'rogue_6_relic_legacy_2':('global_buff_stack',0,'modify_sp_recover[normal]',.2),
    'rogue_6_relic_legacy_3':('global_buff_stack',0,'modify_sp_recover[normal]',.35),
    'rogue_6_relic_legacy_4':('global_buff_stack',0,'modify_sp_recover[normal]',.5),
    'rogue_6_relic_legacy_74':('global_buff_normal',0,'modify_sp_recover[medic]',.3),
    'rogue_6_from_relic_15':('char_ability_new',0,None,.8),
}


def supported_sp(rule):
    if not rule.get('_verified_rule') or rule.get('token_only'):return False
    if rule['kind'] in SP_KINDS:return True
    source=NATURAL_SP_SOURCES.get(rule.get('relic_id'))
    return bool(source and rule.get('kind')=='sp_recovery' and
        (rule.get('source_buff_key'),rule.get('source_buff_index'),
         rule.get('group'),rule.get('value'))==source)


def sp_reference(skill,selected,records):
    """Calculate from effects already accepted by supported_sp."""
    scenario={'_relic_rules':selected}
    adjusted=effective_skill({'sp_cost':skill['spData']['spCost'],'initial_sp':skill['spData']['initSp']},scenario)
    cost_pending=[];initial_pending=[];end_pending=[];recovery_pending=[]
    for record in records:
        data=mechanics()
        entry=data['relics'].get(record['id']) or data['char_buffs'].get(record['id'])
        if not entry or not (record['pending'] or record['missing_conditions']):continue
        kinds={e['kind'] for e in entry['effects']}
        for key,kind in ((cost_pending,'sp_cost_factor'),(initial_pending,'initial_sp'),(end_pending,'end_sp')):
            if kind in kinds:key.append(record['name'])
        if record['missing_conditions']:
            kinds.update(e['kind'] for binding in entry.get('bound_char_buffs',[])
                for e in data['char_buffs'].get(binding['id'],{}).get('effects',[]))
        if 'sp_recovery' in kinds:recovery_pending.append(record['name'])
    cost=None if cost_pending else adjusted['sp_cost']
    initial=None if initial_pending else adjusted['initial_sp']
    end=None if end_pending else sum(r['value'] for r in selected if r['kind']=='end_sp')
    natural=[r for r in selected if r['kind']=='sp_recovery']
    natural_applicable=skill['spData']['spType']=='INCREASE_WITH_TIME'
    bonus=sum(r['value'] for r in natural) if natural_applicable else 0
    rate=(None if recovery_pending else skill['spData']['increment']+bonus) if natural_applicable else None
    return {'sp_type':skill['spData']['spType'],'cost_parameter':cost,'initial_parameter':initial,
        'initial_requirement':max(0,cost-initial) if cost is not None and initial is not None else None,
        'end_return_parameter':end,
        'recharge_requirement':recharge_requirement(scenario,cost) if cost is not None and end is not None else None,
        'unresolved_cost_sources':cost_pending,'unresolved_initial_sources':initial_pending,
        'unresolved_end_sources':end_pending,
        'natural_recovery_applicable':natural_applicable,'natural_recovery_bonus':bonus,
        'natural_recovery_rate_parameter':rate,
        'natural_recovery_sources':[r['relic_id'] for r in natural],
        'unresolved_recovery_sources':recovery_pending,
        'natural_recovery_source_scope':'sp-attributes-066/native-proof.json; installed_native_baseline',
        'current_hotfix_equivalence_proven':False,
        'initial_seconds':None,'recharge_seconds':None,'cycle_seconds':None}
