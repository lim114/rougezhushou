"""Source-qualified ordinary first-card costs; no live deployment state."""
from .deployment import (native_deployment_cost,_rune_cost_add,_rune_cost_mul,
                         _runtime_cost_delta,_first_card_factor)

COST_KINDS={'deployment_cost_add','deployment_cost_pct','first_deployment_cost_factor','skill_start_dp'}
FANG_COST_SOURCE={
    'scope':'installed_native_baseline_observed_2026_10_12',
    'game_dll_sha256':'583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
    'metadata_sha256':'d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f',
    'evidence':'research/p2-fang-cost-chain-current/receipt.json',
    'component':'Torappu.Battle.DeckTalentToAddCardCost',
    'layer':'after_rune_integer_before_redeploy_and_first_card_scale',
    'current_hotfix_equivalence_proven':False,
}


def cost_layer(rule):
    if rule.get('token_only') or not rule.get('_verified_rule'):return None
    if rule['kind']=='deployment_cost_add':
        if _rune_cost_add(rule):return 'rune_additions'
        if _runtime_cost_delta(rule):return 'runtime_deltas'
    elif rule['kind']=='deployment_cost_pct':
        if _rune_cost_mul(rule):return 'rune_multipliers'
    elif rule['kind']=='first_deployment_cost_factor':
        if _first_card_factor(rule):return 'card_factors'
    elif (rule['kind']=='skill_start_dp' and rule.get('relic_id')=='rogue_6_relic_book_1'
            and rule.get('source_buff_key')=='global_buff_normal' and rule.get('source_buff_index')==0):
        return 'skill_start_dp'
    return None


def cost_reference(stats,talents,classified,unresolved,records,*,operator=None):
    """Calculate from (layer, effect) pairs qualified by cost_layer at entry."""
    cost_inputs={'rune_additions':[],'rune_multipliers':[],'card_factors':[],'runtime_deltas':[]}
    skill_start_dp=0
    for layer,effect in classified:
        if layer=='skill_start_dp':skill_start_dp+=effect['value']
        else:cost_inputs[layer].append(effect['value'])
    native=native_deployment_cost(stats['deployment_cost'],**cost_inputs)
    talent=sum(b['value'] for t in talents for b in t['blackboard'] if b['key']=='cost')
    missing=sorted({c for record in records if any(
        e['kind'] in COST_KINDS for e in record['applied']) or record['id']=='rogue_6_relic_cargo_3'
        for c in record['missing_conditions']})
    modified=(any(value!=0 for layer in ('rune_additions','rune_multipliers','runtime_deltas')
                  for value in cost_inputs[layer]) or any(value!=1 for value in cost_inputs['card_factors']))
    # Only the prefab- and method-bound Fang talent may enter this new layer.
    # Do not classify another talent by a shared blackboard key.
    fang_verified=bool(operator=='char_123_fang' and talent==-1 and any(
        t.get('prefabKey')=='1' and t.get('unlockCondition',{}).get('phase')=='PHASE_1'
        and t.get('name')=='轻量化' and t.get('blackboard')==[
            {'key':'cost','value':-1.0,'valueStr':None}] for t in talents))
    with_talent=native_deployment_cost(stats['deployment_cost'],
        deck_base_deltas=[talent],**cost_inputs) if fang_verified else None
    talent_pending=bool(talent and modified and not fang_verified)
    cost=None if missing or unresolved or talent_pending else (
        with_talent['estimated_cost'] if with_talent else
        max(0,stats['deployment_cost']+talent) if talent else native['estimated_cost'])
    return {'estimated_cost':cost,'native_without_talent':native,'talent_cost_parameter':talent,
        'native_with_talent':with_talent,'talent_source':dict(FANG_COST_SOURCE) if fang_verified else None,
        'talent_composition_pending':talent_pending,'missing_conditions':missing,
        'first_card_only':bool(cost_inputs['card_factors']),
        'actual_cost':None,'live_first_deployment_verified':False,
        'skill_start_dp':skill_start_dp}
