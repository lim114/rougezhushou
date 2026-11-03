"""Reviewed Haruka/BLS-Y friendly-target parameters; no native event binding."""


def reference(profile, scenario, skill):
    if profile['id'] != 'char_4202_haruka':
        return None
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    potential_rank = scenario.get('potential', 1) - 1

    def eligible(candidate):
        condition = candidate['unlockCondition']
        phase = int(condition['phase'][-1])
        return (phase <= elite and (phase < elite or condition['level'] <= level)
            and candidate.get('requiredPotentialRank', 0) <= potential_rank)

    original = next(c for c in reversed(profile['trait']['candidates']) if eligible(c))
    original_values = {b['key']: b['value'] for b in original['blackboard']}
    selected = original_values
    module = next((m for m in profile['modules'] if m['id'] == scenario.get('module_id')), None)
    unlocked = bool(module and module['id'] == 'uniequip_002_haruka'
        and 1 <= scenario.get('module_level', 0) <= len(module['levels'])
        and elite >= module['unlock_elite'] and level >= module['unlock_level'])
    if unlocked:
        for part in module['levels'][scenario['module_level'] - 1]['parts']:
            if part.get('isToken') or part['target'] != 'TRAIT_DATA_ONLY':
                continue
            candidates = (part.get('overrideTraitDataBundle') or {}).get('candidates') or []
            for candidate in candidates:
                if eligible(candidate):
                    values = {b['key']: b['value'] for b in candidate['blackboard']}
                    if 'attack@max_target_heal' in values and 'heal_scale' in values:
                        selected = values
    # The sum is an isolated parameter reference. In particular, the module
    # base2 / skill+1 native property composition does not follow from addition.
    added = skill['values'].get('attack@max_target_heal_add', 0)
    return {
        'operator_id': profile['id'], 'module_id': scenario.get('module_id'),
        'module_level': scenario.get('module_level', 0), 'module_unlocked': unlocked,
        'original_trait_target_limit_parameter': int(original_values['attack@max_target_heal']),
        'selected_trait_target_limit_parameter': int(selected['attack@max_target_heal']),
        'skill_target_add_parameter': int(added),
        'conditional_target_limit_reference': int(selected['attack@max_target_heal'] + added),
        # These two independent sources support the existing reference range.
        # Taking their maximum does not establish a native stacking rule.
        'modeled_target_limit_reference': int(max(
            original_values['attack@max_target_heal'] + added,
            selected['attack@max_target_heal'])),
        'healing_scale_parameter': selected['heal_scale'],
        'skill_rank': scenario.get('skill_rank', 10),
        'reference_only': True,
        'actual_target_limit': None, 'actual_target_count': None,
        'actual_acquisition_times_seconds': None, 'native_composition_verified': False,
        'native_attachment_verified': False, 'live_state_verified': False,
        'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
        'source_selectors': [
            'character_table.char_4202_haruka.trait.candidates[0]',
            'uniequip_table.equipDict.uniequip_002_haruka',
            'battle_equip_table.uniequip_002_haruka.phases[*].parts[0].overrideTraitDataBundle.candidates',
            'skill_table.skchr_haruka_2.levels[*].blackboard']}


def conditional_input_limit(profile, scenario, skill):
    """Number of declared recipient references, never an actual native cap."""
    return reference(profile, scenario, skill)['conditional_target_limit_reference']
