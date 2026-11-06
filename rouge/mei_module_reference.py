"""Mei MAR-X conditional parameters; no target or native formula inference."""
from .catalog import resolve_cultivation


def reference(profile, scenario, module_parts=Ellipsis, *, module=None):
    """Return parameters and stage parts; omission selects catalog entries."""
    if profile.get('id') != 'char_133_mm' or scenario.get('operator') != 'char_133_mm':
        return None, ()
    module_id = 'uniequip_002_mm'
    if scenario.get('module_id') != module_id:
        return None, ()
    if module is None:
        module = next((m for m in profile['modules'] if m['id'] == module_id), None)
    stage = scenario.get('module_level', 0)
    elite, level = resolve_cultivation(profile, scenario)
    if (module is None or type(stage) is not int or not 1 <= stage <= len(module['levels'])
            or elite < module['unlock_elite'] or level < module['unlock_level']):
        return None, ()
    catalog_parts = module['levels'][stage - 1]['parts']
    selected_parts = catalog_parts if module_parts is Ellipsis else module_parts or ()
    for part in selected_parts:
        part_index = next((i for i, original in enumerate(catalog_parts) if original == part), None)
        if (part_index is None or part.get('target') != 'TRAIT'
                or part.get('isToken') or part.get('validInGameTag') is not None
                or part.get('validInMapTag') is not None):
            continue
        candidates = (part.get('overrideTraitDataBundle') or {}).get('candidates') or []
        for index, candidate in enumerate(candidates):
            condition = candidate['unlockCondition']
            phase = int(condition['phase'][-1])
            if (phase > elite or phase == elite and condition['level'] > level
                    or candidate.get('requiredPotentialRank', 0) > scenario.get('potential', 1) - 1):
                continue
            values = {b['key']: b['value'] for b in candidate['blackboard']}
            if 'atk_scale' not in values:
                continue
            return {
                'operator_id': profile['id'], 'module_id': module_id,
                'module_name': module['name'], 'module_level': stage,
                'unlock_elite': module['unlock_elite'], 'unlock_level': module['unlock_level'],
                'candidate_unlock_condition': dict(condition),
                'required_potential_rank': candidate.get('requiredPotentialRank', 0),
                'trait_description': candidate['additionalDescription'],
                'attack_scale_parameter': values['atk_scale'],
                'actual_target_is_airborne': None,
                'actual_conditional_damage': None,
                'reference_only': True, 'applied_to_numeric_estimate': False,
                'native_attachment_verified': False, 'damage_composition_verified': False,
                'live_state_verified': False,
                'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
                'source_selectors': [
                    'character_table.char_133_mm',
                    'uniequip_table.equipDict.uniequip_002_mm',
                    'battle_equip_table.uniequip_002_mm.phases[' + str(stage - 1)
                    + '].parts[' + str(part_index) + '].overrideTraitDataBundle.candidates['
                    + str(index) + ']']}, catalog_parts
    return None, catalog_parts
