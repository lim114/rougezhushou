import json
import math
from functools import lru_cache
from pathlib import Path


POTENTIAL_FIELDS = {
    'ATK': 'attack', 'MAX_HP': 'hp', 'DEF': 'defense', 'MAGIC_RESISTANCE': 'resistance',
    'RESPAWN_TIME': 'redeploy_seconds', 'ATTACK_SPEED': 'attack_speed',
    'BLOCK_CNT': 'block_count', 'COST': 'deployment_cost',
}
MODULE_FIELDS = {
    'atk': 'attack', 'def': 'defense', 'max_hp': 'hp', 'magic_resistance': 'resistance',
    'attack_speed': 'attack_speed', 'respawn_time': 'redeploy_seconds',
}
UNRESOLVED_MODULE_FIELDS = {'block_cnt': 'block_count', 'cost': 'deployment_cost'}


class CultivationInputError(ValueError):
    """Cultivation or equipment selection is outside the supported input range."""


@lru_cache(maxsize=1)
def catalog():
    return json.loads((Path(__file__).parent / 'data' / 'catalog.json').read_text(encoding='utf-8'))

@lru_cache(maxsize=1)
def tactical_tools():
    return json.loads((Path(__file__).parent/'data/inventory-items.json').read_text(encoding='utf-8'))['active_tools']

@lru_cache(maxsize=1)
def operator_profiles():
    profiles=json.loads((Path(__file__).parent/'data/operator-profiles.json').read_text(encoding='utf-8'))['operators']
    for key,profile in catalog()['operators'].items():
        profiles[key]={**profiles[key],**profile}
    return profiles

@lru_cache(maxsize=1)
def stage_previews():
    return json.loads((Path(__file__).parent / 'data' / 'previews.json').read_text(encoding='utf-8'))['stages']

def talent_candidate_eligible(candidate, elite, level, potential_rank):
    condition = candidate.get('unlockCondition')
    phase = int(condition['phase'][-1]) if condition else candidate['phase']
    minimum = condition['level'] if condition else candidate['level']
    rank = candidate.get('requiredPotentialRank', candidate.get('potential_rank', 0))
    return (phase <= elite and (phase < elite or minimum <= level)
            and rank <= potential_rank)


def resolve_cultivation(profile,scenario):
    """Resolve operator level at a standalone reference entry."""
    elite=scenario.get('elite',2)
    maximum=profile['phases'][elite]['max_level']
    level=scenario.get('level')
    if level is None:level=maximum
    if type(level) is not int or not 1<=level<=maximum:
        raise ValueError('干员等级需要为当前精英阶段范围内的整数。')
    return elite,level



def operator_attributes(operator, elite=2, level=None, trust=100, potential=1,module_id=None,module_level=0):
    return _operator_attribute_reference(operator,elite,level,trust,potential,module_id,module_level)[0]


def _operator_attribute_reference(operator, elite=2, level=None, trust=100, potential=1,module_id=None,module_level=0):
    """Return attributes, resolved equipment and its applied/unlocked state."""
    profile = operator_profiles()[operator]
    phase, level = _attribute_level(profile, elite, level)
    if not math.isfinite(trust) or not 0 <= trust <= 100:
        raise CultivationInputError('等级或信赖超出范围（信赖按加成进度 0–100%）。')
    return _attribute_values(profile, phase, elite, level, trust, potential, module_id, module_level)


def _training_in_range(value, low, high, field, exact):
    if exact:
        if type(value) is not int:
            raise CultivationInputError(field + '需要整数。')
    elif not isinstance(value, int) or isinstance(value, bool):
        return False
    return low <= value <= high


def _attribute_level(profile, elite, level, *, exact=False):
    if not _training_in_range(elite, 0, len(profile['phases']) - 1, 'elite', exact):
        raise CultivationInputError('精英阶段需要为 0、1 或 2。')
    phase = profile['phases'][elite]
    if level is None and not exact:
        level = phase['max_level']
    if not _training_in_range(level, 1, phase['max_level'], 'level', exact):
        raise CultivationInputError('等级或信赖超出范围（信赖按加成进度 0–100%）。')
    return phase, level


def _attribute_values(profile, phase, elite, level, trust, potential, module_id, module_level, *, exact=False):
    if not _training_in_range(potential, 1, 6, 'potential', exact):
        raise CultivationInputError('潜能需要为 1–6。')
    first, last = phase['frames'][0], phase['frames'][-1]
    fraction = (level - first['level']) / (last['level'] - first['level']) if last['level'] != first['level'] else 0
    stats={field:first[field]+fraction*(last[field]-first[field]) for field in last if field!='level'}
    for field in ('hp','attack','defense'):
        stats[field]=math.floor(stats[field]+.5)+math.floor(profile['trust_stats'][field]*trust/100+.5)
    unresolved = set()
    for modifiers in profile['potential_bonuses'][:potential-1]:
        for modifier in modifiers:
            key = modifier['attributeType']
            field = POTENTIAL_FIELDS.get(key)
            if field is not None and modifier['formulaItem'] == 'ADDITION':
                stats[field] += modifier['value']
            else:
                unresolved.add(field or key)
    module=None
    module_applied=False
    if module_id:
        module=next((m for m in profile['modules'] if m['id']==module_id),None)
        if not module or not isinstance(module_level,int) or isinstance(module_level,bool) or not 1<=module_level<=len(module['levels']):
            raise CultivationInputError('模组身份或等级尚无可用规则。')
        module_applied=elite>=module['unlock_elite'] and level>=module['unlock_level']
        if module_applied:
            for attr,value in module['levels'][module_level-1]['attributes'].items():
                field = MODULE_FIELDS.get(attr)
                if field is None:
                    unresolved.add(UNRESOLVED_MODULE_FIELDS.get(attr, attr))
                else:
                    stats[field] += value
    for field in sorted(unresolved):
        stats[field] = None
    return stats,module,module_applied
