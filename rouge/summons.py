"""Shared independent token cultivation and explicitly verified module references.

Only a documented token/module pair is handled. Verified module multipliers
share the ordinary talent layer, after relic/squad runes and their integer write.
"""
import json
import math
from functools import lru_cache
from pathlib import Path


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
    return stats
