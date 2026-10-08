"""Pinned ISW-A data references without an invented ability or tick clock."""
from copy import deepcopy


OPERATOR = 'char_206_gnosis'
MODULE = 'uniequip_004_gnosis'
DOT_NAME = 'ISW-A寒冷冻结持续法术'
SOURCE_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'


def selected_reference(profile, module, stage, parts, original, eligible):
    if profile['id'] != OPERATOR or module['id'] != MODULE or not original:
        return None
    if original.get('name') != '坚冰' or set(original['values']) != {
            'cold', 'damage_scale_cold', 'damage_scale_freeze'}:
        return None
    records = []
    trait = description = None
    for part_index, part in enumerate(parts):
        if part.get('isToken'):
            continue
        for bundle, field in (('overrideTraitDataBundle', 'trait'),
                              ('addOrOverrideTalentDataBundle', 'talent')):
            candidates = [(i, c) for i, c in enumerate((part.get(bundle) or {}).get('candidates') or [])
                          if eligible(c)]
            if not candidates:
                continue
            candidate_index, candidate = candidates[-1]
            values = {b['key']: b['value'] for b in candidate['blackboard']}
            if field == 'trait' and part.get('target') == 'DISPLAY':
                description = candidate.get('additionalDescription')
            if (field == 'trait' and part.get('target') == 'TRAIT' and
                    part.get('resKey') == 'gnosis_equip_3_1_p1' and
                    part.get('validInGameTag') == 'roguelike' and
                    part.get('validInMapTag') is None and
                    values == {'atk_scale': .5, 'interval': .5}):
                trait = values
            if field == 'talent' and candidate.get('talentIndex') != 0:
                continue
            records.append({
                'kind': field, 'target': part.get('target'),
                'res_key': part.get('resKey'), 'is_token': part.get('isToken'),
                'valid_game_tag': part.get('validInGameTag'),
                'valid_map_tag': part.get('validInMapTag'),
                'talent_index': candidate.get('talentIndex'),
                'prefab_key': candidate.get('prefabKey'),
                'hidden': candidate.get('isHideTalent', False),
                'blackboard': values, 'raw_candidate': deepcopy(candidate),
                'attachment_verified': False,
                'source_selector': f'battle_equip_table.{MODULE}.phases[{stage-1}].parts[{part_index}].{bundle}.candidates[{candidate_index}]',
            })
    if trait is None or not description:
        return None
    if stage in (2, 3):
        abilities = [r for r in records if r['kind'] == 'talent']
        expected = {'#': (None, 'TALENT_DATA_ONLY', False),
                    '1': (f'gnosis_equip_3_{stage}_p2', 'TALENT', False),
                    '10_root': (f'gnosis_equip_3_{stage}_p3', 'TALENT', True),
                    '11_root': (f'gnosis_equip_3_{stage}_p4', 'TALENT', True)}
        if len(abilities) != 4 or {r['prefab_key'] for r in abilities} != set(expected):
            return None
        for record in abilities:
            if (record['res_key'], record['target'], record['hidden']) != expected[record['prefab_key']]:
                return None
            tag = None if record['prefab_key'] == '#' else 'roguelike'
            if record['valid_game_tag'] != tag or record['valid_map_tag'] is not None:
                return None
    return {
        'module_id': MODULE, 'module_level': stage, 'source_commit': SOURCE_COMMIT,
        'original_talent': {'name': original['name'], 'description': original['description'],
                            'talent_index': 0, 'prefab_key': '1',
                            'blackboard': dict(original['values']), 'reference_only': True,
                            'module_coexistence_verified': False},
        'module_records': records, 'trait_description': description,
        'dot_parameters': trait, 'game_tag_selection_engine_verified': False,
        'native_ability_attachment_verified': False,
        'stack_phase_reset_interaction_verified': False,
    }


def preserve_plan(components, reference, *, window, target_lifetime, per_tick):
    possible = window != 0 and target_lifetime != 0
    for component in components:
        component.pop('times_seconds', None)
        component.pop('instant_event', None)
        component['timing_reference'] = 'original talent conditional reference; ISW-A attachment/state clock unverified'
        if possible and component['hits']:
            component['actual_total'] = None
        elif not possible:
            component.pop('actual_total', None)
            component['hits'] = 0
            component['total'] = 0
    dot = {'name': DOT_NAME, 'damage_type': 'magic', 'hits': 0,
           'per_hit': per_tick, 'total': 0,
           'attack_scale_parameter': reference['dot_parameters']['atk_scale'],
           'tick_interval_parameter_seconds': reference['dot_parameters']['interval'],
           'timing_reference': 'conditional per-tick parameter; actual first tick/count/lifecycle unverified'}
    if possible:
        dot['actual_total'] = None
    components.append(dot)


def attach_result(result, reference, full, shown, normal, duration, cycle):
    from .uncertain_sources import mask_pending_damage
    dot = next(c for c in full['components'] if c['name'] == DOT_NAME)
    observed = next(c for c in shown['components'] if c['name'] == DOT_NAME)
    result['gnosis_isw_a_reference'] = {
        **reference, 'per_tick_damage_reference': dot['per_hit'],
        'window_per_tick_damage_reference': observed['per_hit'],
        'actual_first_tick_seconds': None, 'actual_tick_times_seconds': None,
        'actual_tick_count': None,
        'actual_dot_damage': None if 'actual_total' in observed else 0,
        'actual_cast_dot_damage': None if 'actual_total' in dot else 0,
        'cold_coverage_windows_seconds': None,
        'attack_snapshot_binding_verified': False,
        'post_skill_dot_lifecycle_verified': False,
        'events_scheduled': False,
        'source_possible': {'cast': 'actual_total' in dot,
                            'window': 'actual_total' in observed},
    }
    mask_pending_damage(result, full, shown, normal, duration, cycle)
    result['timing']['phase_clock_unbound'] = True
    result['timing']['resource_and_damage_shared_clock'] = False
    result['complete'] = result['estimate']['complete'] = False
    result['estimate']['notes'].append(
        'ISW-A原版坚冰保留条件参考；模组能力与原天赋的实际并存、隐藏附着和增长/重置顺序未核验。'
        '寒冷冻结持续法术仅保留50%攻击力及0.5秒间隔参数，首跳、实际跳数、攻击快照和技能后生命周期未知；初始未寒冷不证明后续不会寒冷。')
