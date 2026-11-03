"""Direct drone warmup trait overrides from the reviewed pinned module data.

These values feed the existing offline warmup reference. They establish no
independent drone timing, target ownership or hidden module activation script.
"""

REVIEWED_MODULES = {
    'char_328_cammou': 'uniequip_002_cammou',
    'char_1038_whitw2': 'uniequip_002_whitw2',
}


def _eligible(profile, scenario, candidate):
    """Use the same phase, level and potential rules as selected_talents."""
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    condition = candidate.get('unlockCondition')
    phase = int(condition['phase'][-1]) if condition else candidate['phase']
    minimum = condition['level'] if condition else candidate['level']
    rank = candidate.get('requiredPotentialRank', candidate.get('potential_rank', 0))
    return (phase <= elite and (phase < elite or minimum <= level)
            and rank <= scenario.get('potential', 1) - 1)


def _values(candidate):
    return {entry['key']: entry['value'] for entry in candidate['blackboard']}


def selected_drone_trait(profile, scenario, module_parts):
    """Select base parameters and eligible reviewed TRAIT_DATA_ONLY replacements.

    module_parts comes from selected_talents. Check its catalog provenance as
    well, so an unrelated or stale part cannot supply another operator's trait.
    Scripted traits, token parts and scoped module effects stay outside this
    parameter-only reference.
    """
    candidates = (profile.get('trait') or {}).get('candidates') or []
    candidates = [candidate for candidate in candidates
                  if _eligible(profile, scenario, candidate)]
    values = _values(candidates[-1]) if candidates else {}
    operator = scenario.get('operator')
    module_id = REVIEWED_MODULES.get(operator)
    if (profile.get('id') != operator or module_id is None
            or scenario.get('module_id') != module_id):
        return values
    module = next((item for item in profile['modules'] if item['id'] == module_id), None)
    stage = scenario.get('module_level', 0)
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    if (module is None or type(stage) is not int or not 1 <= stage <= len(module['levels'])
            or elite < module['unlock_elite'] or level < module['unlock_level']):
        return values
    catalog_parts = module['levels'][stage - 1]['parts']
    for part in module_parts or ():
        if (part not in catalog_parts or part.get('target') != 'TRAIT_DATA_ONLY'
                or part.get('isToken') or part.get('validInGameTag') is not None
                or part.get('validInMapTag') is not None):
            continue
        overrides = (part.get('overrideTraitDataBundle') or {}).get('candidates') or []
        overrides = [candidate for candidate in overrides
                     if _eligible(profile, scenario, candidate)]
        if overrides:
            # Both reviewed bundles provide the complete warmup parameters.
            values = _values(overrides[-1])
    return values
