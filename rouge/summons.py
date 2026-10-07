"""Shared independent token cultivation and explicitly verified module references.

Only a documented token/module pair is handled. Verified module multipliers
share the ordinary talent layer, after relic/squad runes and their integer write.
"""
import json
import math
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _duration_rules():
    return json.loads((Path(__file__).with_name('data')/'token-duration-reference.json').read_text(encoding='utf-8'))


def duration_reference(profile,scenario,token_id):
    """Return an isolated duration parameter; actual token presence is unknown.

    The product's current theme is rogue_6. An explicit map_tag allows callers
    to inspect another map without inheriting its conditional module override.
    No parameter here schedules deployment, withdrawal, death or damage.
    """
    from copy import deepcopy
    data=_duration_rules()
    rule=next((r for r in data['rules'] if r['operator_id']==profile['id'] and
        r['token_id']==token_id and token_id in profile.get('tokens',{})),None)
    if rule is None:return None
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    potential=scenario.get('potential',1)-1
    def eligible(candidate):
        phase=candidate['unlock_elite']
        return phase<=elite and (phase<elite or candidate['unlock_level']<=level) and candidate['required_potential_rank']<=potential
    candidates=[c for c in rule['base_candidates'] if eligible(c)]
    base=candidates[-1] if candidates else None
    map_tag=scenario.get('map_tag','rogue_6')
    override=next((o for o in rule['module_overrides'] if base and
        scenario.get('module_id')==rule['module_id'] and
        scenario.get('module_level',0)==o['module_level'] and
        elite>=rule['module_unlock_elite'] and level>=rule['module_unlock_level'] and
        eligible(o) and map_tag==o['map_tag'] and
        any(m['id']==rule['module_id'] for m in profile['modules'])),None)
    state='locked' if base is None else 'unlimited' if override else 'finite'
    return {'scope':data['scope'],'operator_id':rule['operator_id'],'token_id':token_id,
        'token_name':rule['token_name'],'unlocked':base is not None,'state':state,
        'duration_seconds':base['duration_seconds'] if state=='finite' else None,
        'base_duration_seconds':base['duration_seconds'] if base else None,
        'parameter_key':rule['parameter_key'],
        'parameter_value':override['parameter_value'] if override else base['duration_seconds'] if base else None,
        'map_tag':map_tag,'map_context':'explicit' if 'map_tag' in scenario else 'current_product_theme',
        'base_source_selector':base['source_selector'] if base else None,
        'module_override':{'module_id':rule['module_id'],'unlock_elite':rule['module_unlock_elite'],
            'unlock_level':rule['module_unlock_level'],'applied':override is not None,
            'conditions':deepcopy(rule['module_overrides']),
            'source_selector':override['source_selector'] if override else None},
        'source_commit':data['source_commit'],'sources':deepcopy(data['sources']),
        'deployment_completed_seconds':None,'actual_exit_seconds':None,'actual_alive_seconds':None,
        'live_state_verified':False,'damage_timing_applied':False}


def finish_duration_references(scenario,result):
    """Expose documented token parameters separately from relic stat panels."""
    from .catalog import catalog
    profile=catalog()['operators'][scenario['operator']]
    references=[r for token_id in profile.get('tokens',{}) if
        (r:=duration_reference(profile,scenario,token_id)) is not None]
    if references:result['token_duration_references']=references


@lru_cache(maxsize=1)
def module_rules():
    return json.loads((Path(__file__).with_name('data')/'summon-module-rules.json').read_text(encoding='utf-8'))


def module_reference(profile,scenario,token_id):
    module_id=scenario.get('module_id');rule=module_rules().get(module_id)
    if not rule or rule['operator']!=scenario['operator'] or rule['token_id']!=token_id:return None
    module=next((m for m in profile['modules'] if m['id']==module_id),None)
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    stage=rule['stages'].get(str(scenario.get('module_level',0)))
    if not module or not stage or elite<module['unlock_elite'] or level<module['unlock_level']:return None
    return {'module_id':module_id,'module_level':scenario['module_level'],**stage,
            'held_limit':rule['base_held_limit']+stage['stock_add'],
            'concurrent_limit':rule['concurrent_limit'],
            'hp_composition_verified':rule['hp_composition_verified'],
            'source_url':rule['source_url']}


@lru_cache(maxsize=1)
def _token_cost_rules():
    return json.loads((Path(__file__).with_name('data')/'token-module-cost-reference.json').read_text(encoding='utf-8'))


def token_cost_reference(profile,scenario,token_id):
    """Only the pinned direct token cost addition is applied.

    Hidden talents, token deployment limits and actual lifecycle remain separate
    from this cultivation cost. The existing SUM-Y path is not duplicated.
    """
    from copy import deepcopy
    data=_token_cost_rules()
    rule=next((r for r in data['rules'] if r['operator_id']==profile['id'] and
        r['token_id']==token_id and r['module_id']==scenario.get('module_id') and
        token_id in profile.get('tokens',{})),None)
    if rule is None:return None
    module=next((m for m in profile['modules'] if m['id']==rule['module_id']),None)
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    stage=next((s for s in rule['stages'] if s['module_level']==scenario.get('module_level',0)),None)
    if (not module or not stage or elite<rule['module_unlock_elite'] or
            level<rule['module_unlock_level'] or elite<module['unlock_elite'] or level<module['unlock_level']):return None
    return {'scope':data['scope'],'operator_id':rule['operator_id'],'token_id':token_id,
        'module_id':rule['module_id'],'module_level':stage['module_level'],'cost_add':stage['cost_add'],
        'source_selector':stage['source_selector'],'module_source_selector':rule['module_source_selector'],
        'source_commit':data['source_commit'],'sources':deepcopy(data['sources']),
        'actual_deployment_count':None,'actual_alive_seconds':None,'live_state_verified':False}


def token_concurrent_limit(profile,scenario,token_id):
    """Verified per-token cap for a normal operator, not global free slots.

    SUM-Y directly adds MAX_DEPLOY_COUNT; its stock addition is independent.
    Cultivation/unlock checks are shared with the other token module effects.
    Unknown pairs never infer a concurrent cap from the held inventory.
    """
    rule=next((r for r in module_rules().values() if
        r['operator']==scenario['operator'] and r['token_id']==token_id and
        r.get('concurrent_limit_verified')),None)
    if rule is None:return None
    base=rule['base_concurrent_limits'].get(str(scenario.get('elite',2)))
    reference=module_reference(profile,scenario,token_id)
    return reference['concurrent_limit'] if reference else base


def token_attributes(profile,scenario,token_id,hp_pct=0,*,rune_effects=()):
    phases=profile['tokens'][token_id]['phases'];elite=scenario.get('elite',2)
    phase=phases[min(elite,len(phases)-1)]
    level=min(scenario.get('level') or profile['phases'][elite]['max_level'],phase['max_level'])
    first,last=phase['frames'][0],phase['frames'][-1]
    ratio=(level-first['level'])/(last['level']-first['level']) if last['level']!=first['level'] else 0
    stats={k:first[k]+ratio*(v-first[k]) for k,v in last.items() if k!='level'}
    for k in ('hp','attack','defense'):stats[k]=math.floor(stats[k]+.5)
    base_hp=stats['hp']
    from .relic_attributes import apply_attribute_runes
    stats=apply_attribute_runes(stats,rune_effects)
    rune_hp=stats['hp']!=base_hp
    ordinary_base_hp=stats['hp']
    stats['hp']*=1+hp_pct
    reference=module_reference(profile,scenario,token_id)
    if reference:
        stats['deployment_cost']=max(0,stats['deployment_cost']+reference['cost_add'])
        reference={**reference,'module_only_hp':base_hp*(1+reference['hp_pct']),
                   'other_sources_only_hp':stats['hp'],'hp_composition_pending':False}
        if reference['hp_pct']:
            if reference['hp_composition_verified']:
                # SUM-Y's token talent is MAX_HP / MULTIPLIER, not a rune
                # and not an independent final scaler (summon-068 proof).
                stats['hp']=ordinary_base_hp*max(0,1+hp_pct+reference['hp_pct'])
            elif hp_pct or rune_hp:
                # The blackboard and general attribute formula alone do not
                # prove this module's layer. Preserve both isolated references.
                stats['hp']=None;reference['hp_composition_pending']=True
            else:stats['hp']=reference['module_only_hp']
        stats['module_reference']=reference
    cost_reference=token_cost_reference(profile,scenario,token_id)
    if cost_reference:
        base_cost=stats['deployment_cost']
        stats['deployment_cost']=max(0,base_cost+cost_reference['cost_add'])
        stats['module_cost_reference']={**cost_reference,'base_cost':base_cost,
            'module_only_cost':stats['deployment_cost']}
    duration=duration_reference(profile,scenario,token_id)
    if duration is not None:stats['duration_reference']=duration
    return stats
