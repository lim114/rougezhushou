"""Verified ordinary token card counts; no automatic/skill/current state inference."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

@lru_cache(maxsize=1)
def count_rules():
    return json.loads((Path(__file__).with_name('data')/'token-count-reference.json').read_text(encoding='utf8'))

def token_count_reference(profile,scenario,token_id):
    data=count_rules()
    if profile['id']!=data['operator_id'] or scenario['operator']!=data['operator_id'] or token_id!=data['token_id'] or token_id not in profile.get('tokens',{}):return None
    elite=scenario.get('elite',2);level=scenario.get('level') or profile['phases'][elite]['max_level']
    potential=scenario.get('potential',1)-1
    phase=next(p for p in data['phases'] if p['elite']==elite)
    eligible=[p for p in data['potential_candidates'] if p['elite']<=elite and
        (p['elite']<elite or p['level']<=level) and p['required_potential_rank']<=potential]
    candidate=eligible[-1] if eligible else None
    module=next((m for m in profile['modules'] if m['id']==data['module_id']),None)
    module_applied=bool(module and scenario.get('module_id')==data['module_id'] and
        elite>=data['module_unlock_elite'] and level>=data['module_unlock_level'])
    stage=next((s for s in data['module_stages'] if s['module_level']==scenario.get('module_level')),None) if module_applied else None
    held=phase['held_base']+(candidate['held_add'] if candidate else 0)+(stage['held_add'] if stage else 0)
    concurrent=phase['manual_concurrent_base']+(candidate['manual_concurrent_add'] if candidate else 0)+(stage['manual_concurrent_add'] if stage else 0)
    return {'scope':data['scope'],'operator_id':data['operator_id'],'token_id':token_id,
        'held_limit':int(held),'concurrent_limit':int(concurrent),
        'base_counts':deepcopy(phase),'potential_counts':deepcopy(candidate),
        'module_counts':deepcopy(stage),'module_applied':stage is not None,
        'actual_presence':None,'actual_available_stock':None,'actual_deployable':None,
        'automatic_extra_concurrent_limit':None,'skill_modified_limits':None,
        'source_commit':data['source_commit'],'sources':deepcopy(data['sources']),
        'compiled_native_reference':deepcopy(data['compiled_native_reference']),
        'limits':list(data['limitations'])}
