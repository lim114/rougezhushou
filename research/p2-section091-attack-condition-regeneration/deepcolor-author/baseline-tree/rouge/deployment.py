"""Stable offline deployment cost references; no combat HP-loss estimates."""
import math
import struct

from .relics import mechanics,matches
from .offline_scope import active_effects

_Q32=1<<32
_NATIVE_SOURCE={'scope':'installed_native_baseline',
    'game_dll_sha256':'6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce',
    'metadata_sha256':'ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118',
    'evidence':'p1-native-cost-054/verification.json',
    'current_hotfix_equivalence_proven':False}
_EMPTY_BED='rogue_6_relic_cargo_3'
_EMPTY_BED_SOURCE={**_NATIVE_SOURCE,'evidence':'empty-bed-cost-057/verification.json',
    'component':'Torappu.Battle.Rogue6GlobalCardBuffByInventory',
    'lifecycle':'ALL_THE_TIME; condition checked from inventory limit minus count on initialization'}


def _single(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError('费用计算参数需要有限数值。')
    try:return struct.unpack('<f',struct.pack('<f',value))[0]
    except (OverflowError,struct.error) as exc:raise ValueError('费用计算参数超出原生数值范围。') from exc


def _fp(value):
    scaled=_single(_single(value)*_Q32)
    if not math.isfinite(scaled) or not -(1<<63)<=scaled<(1<<63):
        raise ValueError('费用计算参数超出原生FP范围。')
    return int(scaled)


def _fp_product(left,right):
    raw=(left*right)>>32
    if not -(1<<63)<=raw<(1<<63):
        raise ValueError('费用叠加超出原生FP范围。')
    return raw


def native_deployment_cost(cultivation_cost,*,rune_additions=(),rune_multipliers=(),
                           card_factors=(),runtime_deltas=(),redeploy_factor=1):
    """Pure native-baseline oracle; factors are explicit, not sampled combat state.

    The native rune writer converts FP to float then rounds ObscuredInt with
    ties to even. Raw card cost floors redeployment scaling, then its runtime
    scale floors separately before integer deltas and the initial 0..99 clamp.
    Only proven callers may supply modifier sources or redeployment factors.
    """
    _single(cultivation_cost)
    if cultivation_cost<0 or not float(cultivation_cost).is_integer():
        raise ValueError('培养档案费用需要非负整数。')
    base=_fp(cultivation_cost)
    addition=sum(_fp(v) for v in rune_additions)
    factor=_Q32+sum(_fp(v) for v in rune_multipliers)
    value=_fp_product(base+addition,factor)
    rune_float=_single(_single(value)/_Q32)
    attribute_cost=max(0,round(rune_float))
    raw_cost=_fp_product(attribute_cost*_Q32,_fp(redeploy_factor))//_Q32
    scale=_Q32
    for value in card_factors:scale=_fp_product(scale,_fp(value))
    scaled_cost=_fp_product(raw_cost*_Q32,scale)//_Q32
    delta=0
    for value in runtime_deltas:
        _single(value)
        if not float(value).is_integer():raise ValueError('原生卡片费用加减需要整数。')
        delta+=int(value)
    return {'attributes_cost':attribute_cost,'unrounded_rune_reference':max(0,rune_float),
        'raw_card_cost':raw_cost,'card_factor':scale/_Q32,
        'scaled_card_cost':scaled_cost,'runtime_delta':delta,
        'estimated_cost':min(99,max(0,scaled_cost+delta)),
        'rounding':['rune_float_ties_to_even','redeploy_floor','runtime_scale_floor'],
        'native_reference':dict(_NATIVE_SOURCE)}


def _rune_cost_mul(rule):
    item=mechanics()['relics'].get(rule['relic_id'],{})
    if rule.get('condition'):return False
    return any(buff['key']=='char_attribute_mul' and any(
        entry['key']=='cost' and entry['value']==rule['value']
        for entry in buff['blackboard']) for buff in item.get('raw_buffs',[]))


def _rune_cost_add(rule):
    """Classify only proven char_attribute_add costs, not script discounts."""
    item = mechanics()['relics'].get(rule['relic_id'], {})
    if rule.get('condition'):
        return False
    return any(buff['key'] == 'char_attribute_add' and any(
        entry['key'] == 'cost' and entry['value'] == rule['value']
        for entry in buff['blackboard']) for buff in item.get('raw_buffs', []))


def _runtime_cost_delta(rule):
    """Only the source-bound, proven empty-bed card delta; no generic scripts.

    Its native component supplies an integer delta and FP1 to
    RuntimeCostModifier. The card's existing scale floors before this delta.
    Zero is a confirmed inactive condition, not a missing value.
    """
    if (rule.get('relic_id')!=_EMPTY_BED or rule.get('token_only') or
            rule.get('kind')!='deployment_cost_add' or
            rule.get('source_buff_index')!=0 or rule.get('source_buff_key')!='global_buff_normal' or
            rule.get('condition')!='empty_slots' or rule.get('predicate')!='at_least' or
            not rule.get('scale_by_condition')):
        return False
    raw=mechanics()['relics'].get(_EMPTY_BED,{}).get('raw_buffs',[])
    if len(raw)!=1 or raw[0]['key']!='global_buff_normal':return False
    board={e['key']:e['valueStr'] if e.get('valueStr') is not None else e['value']
        for e in raw[0]['blackboard']}
    return (board.get('key')=='rogue_6_relic_inventory_cost' and
        board.get('cnt')==rule.get('threshold')==4 and board.get('value')==-6 and
        rule.get('value') in (0,-6) and
        board.get('selector.profession','').lower()==rule.get('profession'))


def _first_card_factor(rule):
    item=mechanics()['relics'].get(rule['relic_id'],{})
    if rule.get('condition'):return False
    for buff in item.get('raw_buffs',[]):
        if buff['key']!='deck_card_buff':continue
        board={v['key']:v['value'] for v in buff['blackboard']}
        if board.get('cost_scale')==rule['value'] and board.get('card_buff_life_type')==0:
            return True
    return False


def finish_deployment(result, resolution, attributes, profile):
    rules = [r for r in resolution['rules'] if not r.get('token_only')]
    cost_rules = [r for r in rules if r['kind'] == 'deployment_cost_pct']
    first_rules = [r for r in rules if r['kind'] == 'first_deployment_cost_factor']
    runtime_rules=[r for r in rules if _runtime_cost_delta(r)]
    bed_selected=any(record['id']==_EMPTY_BED and any(matches(e,profile) for e in
        active_effects(mechanics()['relics'].get(_EMPTY_BED,{'effects':[],'pending':[]}),_EMPTY_BED))
        for record in resolution['records'])
    if not cost_rules and not first_rules and not bed_selected:
        return
    reference = {'scope': 'offline_deployment_reference', 'live_state_verified': False}
    if cost_rules or bed_selected:
        additions = [r for r in rules if r['kind'] == 'deployment_cost_add']
        rune_additions = [r for r in additions if _rune_cost_add(r)]
        other = [r['relic_id'] for r in additions if r['value'] and
            not _rune_cost_add(r) and not _runtime_cost_delta(r)] + [r['relic_id'] for r in first_rules]
        other += [r['relic_id'] for r in cost_rules if not _rune_cost_mul(r)]
        missing = sorted(set(condition for record in resolution['records']
            if any(e['kind'] == 'deployment_cost_add' and matches(e,profile) for e in
                   active_effects(mechanics()['relics'].get(record['id'], {'effects': [], 'pending': []}),record['id']))
            for condition in record['missing_conditions']))
        additive = sum(r['value'] for r in rune_additions)
        factor = 1 + sum(r['value'] for r in cost_rules)
        native=native_deployment_cost(attributes['deployment_cost'],rune_additions=[r['value'] for r in rune_additions],
            rune_multipliers=[r['value'] for r in cost_rules if _rune_cost_mul(r)],
            runtime_deltas=[r['value'] for r in runtime_rules])
        unrounded = native['unrounded_rune_reference']
        estimated=None if other or missing else native['estimated_cost']
        reference['cost'] = {'cultivation_cost': attributes['deployment_cost'],
            'rune_addition': additive, 'rune_factor': factor,
            'unrounded_rune_reference': unrounded,
            'combined_reference': estimated,'estimated_cost':estimated,
            'attributes_cost':native['attributes_cost'],'native_trace':native,
            'actual_cost': None, 'rounding_verified': True,
            'excluded_script_discounts': sorted(set(other)), 'missing_conditions': missing,
            'formula': 'ties_to_even((cultivation_cost + rune_addition) * (1 + sum(cost_pct))); card_floor_then_delta'}
        if bed_selected:reference['cost'].update(runtime_discount_sources=[r['relic_id'] for r in runtime_rules],
            runtime_discount_reference=dict(_EMPTY_BED_SOURCE))
        # Do not expose the old unmodified cost as this item's actual cost.
        result['deployment_cost'] = estimated
    if first_rules:
        # DCardBuff preserves the specified UNTIL_NEXT_SPAWN life type; the
        # native spawn path deducts this displayed cost before removing it.
        kinds={'deployment_cost_add','deployment_cost_pct','first_deployment_cost_factor'}
        proven={r['relic_id'] for r in rules if
            r['kind']=='deployment_cost_add' and (_rune_cost_add(r) or _runtime_cost_delta(r)) or
            r['kind']=='deployment_cost_pct' and _rune_cost_mul(r) or
            r['kind']=='first_deployment_cost_factor' and _first_card_factor(r)}
        sources={r['relic_id'] for r in rules if r['kind'] in kinds and r['value'] and r['relic_id'] not in proven}
        missing=set()
        for record in resolution['records']:
            entry=mechanics()['relics'].get(record['id'],{'effects':[],'pending':[]})
            if any(e['kind'] in kinds and matches(e,profile) for e in active_effects(entry,record['id'])):
                missing.update(record['missing_conditions'])
                if (record['pending'] or record['missing_conditions']) and record['id'] not in proven:
                    sources.add(record['id'])
        rule=first_rules[0]
        other=sorted(sources)
        native=native_deployment_cost(attributes['deployment_cost'],
            rune_additions=[r['value'] for r in rules if r['kind']=='deployment_cost_add' and _rune_cost_add(r)],
            rune_multipliers=[r['value'] for r in cost_rules if _rune_cost_mul(r)],
            card_factors=[r['value'] for r in first_rules if _first_card_factor(r)],
            runtime_deltas=[r['value'] for r in runtime_rules])
        estimated=None if other or missing else native['estimated_cost']
        unrounded=attributes['deployment_cost']*rule['value']
        reference['first_deployment_cost']={'relic_id':rule['relic_id'],'first_deployment_only':True,
            'cultivation_cost':attributes['deployment_cost'],'card_factor':rule['value'],
            'unrounded_single_item_reference':unrounded,
            'combined_reference':estimated,'estimated_cost':estimated,
            'excluded_discount_sources':other,'missing_conditions':sorted(missing),
            'actual_cost':None,'rounding_verified':_first_card_factor(rule),
            'native_trace':native,'live_first_deployment_verified':False,
            'lifecycle':'UNTIL_NEXT_SPAWN; removed after successful spawn cost deduction'}
        if bed_selected:reference['first_deployment_cost'].update(
            runtime_discount_sources=[r['relic_id'] for r in runtime_rules],
            runtime_discount_reference=dict(_EMPTY_BED_SOURCE))
        if reference.get('cost'):
            reference['cost'].update(combined_reference=estimated,estimated_cost=estimated,native_trace=native,
                excluded_script_discounts=other,missing_conditions=sorted(missing))
        result['deployment_cost']=estimated
    result['deployment_reference'] = reference
