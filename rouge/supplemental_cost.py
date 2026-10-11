"""Source-qualified ordinary first-card costs; no live deployment state."""
from .deployment import (native_deployment_cost,_rune_cost_add,_rune_cost_mul,
                         _runtime_cost_delta,_first_card_factor)

COST_KINDS={'deployment_cost_add','deployment_cost_pct','first_deployment_cost_factor','skill_start_dp'}


def supported_cost(rule):
    if rule.get('token_only') or not rule.get('_verified_rule'):return False
    if rule['kind']=='deployment_cost_add':return _rune_cost_add(rule) or _runtime_cost_delta(rule)
    if rule['kind']=='deployment_cost_pct':return _rune_cost_mul(rule)
    if rule['kind']=='first_deployment_cost_factor':return _first_card_factor(rule)
    return (rule['kind']=='skill_start_dp' and rule.get('relic_id')=='rogue_6_relic_book_1'
            and rule.get('source_buff_key')=='global_buff_normal' and rule.get('source_buff_index')==0)


def cost_reference(stats,talents,rules,records):
    selected=[r for r in rules if supported_cost(r)]
    native=native_deployment_cost(stats['deployment_cost'],
        rune_additions=[r['value'] for r in selected if r['kind']=='deployment_cost_add' and _rune_cost_add(r)],
        rune_multipliers=[r['value'] for r in selected if r['kind']=='deployment_cost_pct'],
        card_factors=[r['value'] for r in selected if r['kind']=='first_deployment_cost_factor'],
        runtime_deltas=[r['value'] for r in selected if _runtime_cost_delta(r)])
    talent=sum(b['value'] for t in talents for b in t['blackboard'] if b['key']=='cost')
    missing=sorted({c for record in records if any(
        e['kind'] in COST_KINDS for e in record['applied']) or record['id']=='rogue_6_relic_cargo_3'
        for c in record['missing_conditions']})
    unresolved=[r for r in rules if r['kind'] in COST_KINDS and not supported_cost(r)]
    modified=any(r['kind'] in ('deployment_cost_add','deployment_cost_pct') and r['value']!=0 or
                 r['kind']=='first_deployment_cost_factor' and r['value']!=1 for r in selected)
    # A parameter saying cost=-1 does not prove where a talent attaches in the
    # native rune/card chain. Preserve the established no-relic reference only.
    talent_pending=bool(talent and modified)
    cost=None if missing or unresolved or talent_pending else (
        max(0,stats['deployment_cost']+talent) if talent else native['estimated_cost'])
    return {'estimated_cost':cost,'native_without_talent':native,'talent_cost_parameter':talent,
        'talent_composition_pending':talent_pending,'missing_conditions':missing,
        'first_card_only':any(r['kind']=='first_deployment_cost_factor' for r in selected),
        'actual_cost':None,'live_first_deployment_verified':False,
        'skill_start_dp':sum(r['value'] for r in selected if r['kind']=='skill_start_dp')}
