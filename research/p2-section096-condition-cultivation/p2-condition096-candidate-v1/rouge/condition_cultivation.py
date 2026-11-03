"""Current-cultivation explanations for nine existing scenario controls.

The existing selector determines whether a named talent was selected. Original
coordinates explain that selection; they do not prove account unlock, equipment
attachment, event timing or actual field conditions. Calculation inputs and
reports are never modified by this presentation helper.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

TARGET_OPERATORS = ('char_2025_shu', 'char_298_susuro', 'char_1048_orchd2',
                    'char_4087_ines', 'char_437_mizuki', 'char_1044_hsgma2')
TARGET_FIELDS = ('three_professions', 'three_same_profession', 'four_sui',
                 'low_cost_healing_target', 'near_previous_deployment', 'power_coating',
                 'stolen_enemy_count', 'enemy_below_half', 'current_hp_ratio')
_TRAINING_FIELDS = ('elite', 'level', 'potential', 'module_id', 'module_level')
_FIELD_LABELS = {'elite': '精英阶段', 'level': '等级', 'potential': '潜能',
                 'module_id': '模组', 'module_level': '模组阶段'}
_SOURCE_LABELS = {'run_confirmed': '本局确认', 'account_reference': '账号参考（本局未确认）',
                  'preview_unconfirmed': '来源缺失，采用预览', 'simulated_override': '手动等级预览'}


@lru_cache(maxsize=1)
def _source_data():
    return json.loads((Path(__file__).parent / 'data' / 'condition-cultivation-source.json')
                      .read_text(encoding='utf-8'))


def _eligible(candidate, profile, scenario):
    """Only locate provenance using the existing selector's source predicate."""
    elite = scenario.get('elite', 2)
    level = scenario.get('level') or profile['phases'][elite]['max_level']
    condition = candidate.get('unlockCondition')
    phase = int(condition['phase'][-1]) if condition else candidate['phase']
    minimum = condition['level'] if condition else candidate['level']
    rank = candidate.get('requiredPotentialRank', candidate.get('potential_rank', 0))
    return (phase <= elite and (phase < elite or minimum <= level) and
            rank <= scenario.get('potential', 1) - 1)


def _typed_equal(left, right):
    """Raw JSON equality preserves scalar types, float representation and order."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (list(left) == list(right) and
                all(_typed_equal(left[key], right[key]) for key in left))
    if isinstance(left, list):
        return len(left) == len(right) and all(_typed_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, float):
        return left.hex() == right.hex()
    return left == right


def _original_source(operator, source, profile, scenario, selected, parts, index):
    """Use base identity or actual ordered module coordinates, never value alone."""
    for candidate_index, candidate in enumerate(profile['talents'][index]):
        if candidate is selected:
            raw = source['raw_character_talents'][index]['candidates'][candidate_index]
            condition = raw['unlockCondition']
            projection = {'phase': int(condition['phase'][-1]), 'level': condition['level'],
                          'potential_rank': raw['requiredPotentialRank'], 'name': raw['name'],
                          'description': raw['description'],
                          'values': {b['key']: b['value'] for b in raw['blackboard']}}
            if not _typed_equal(candidate, projection):
                return None
            return {'table': 'character_table',
                    'path': f'{operator}.talents[{index}].candidates[{candidate_index}]',
                    'talent_index': index, 'candidate_index': candidate_index,
                    'raw_candidate': deepcopy(raw)}
    # The selector returns the exact applied stage's parts list. A below-gate
    # module cannot replace a base source, even when its identity is supplied.
    module = None
    stage = None
    for proposed in profile['modules']:
        for stage_index, level in enumerate(proposed['levels']):
            if level['parts'] is parts:
                module, stage = proposed, stage_index + 1
                break
        if module is not None:
            break
    if module is None or module['id'] != scenario.get('module_id'):
        return None
    replacement = None
    for part_index, part in enumerate(parts):
        if part.get('isToken'):
            continue
        grouped = {}
        candidates = (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []
        for candidate_index, candidate in enumerate(candidates):
            talent_index = candidate.get('talentIndex', -1)
            if talent_index >= 0 and _eligible(candidate, profile, scenario):
                grouped[talent_index] = (part_index, candidate_index, candidate)
        if index in grouped:
            replacement = grouped[index]
    if replacement is None:
        return None
    part_index, candidate_index, candidate = replacement
    projection = {'name': candidate.get('name'), 'description': candidate.get('upgradeDescription'),
                  'values': {b['key']: b['value'] for b in candidate['blackboard']}}
    if not _typed_equal(projection, selected):
        return None
    raw = source['modules'][module['id']]['raw_phases'][stage - 1]['parts'][part_index]
    raw = raw['addOrOverrideTalentDataBundle']['candidates'][candidate_index]
    if not _typed_equal(raw, candidate):
        return None
    return {'table': 'battle_equip_table',
            'path': (f'{module["id"]}.phases[{stage - 1}].parts[{part_index}]'
                     f'.addOrOverrideTalentDataBundle.candidates[{candidate_index}]'),
            'module_id': module['id'], 'module_name': module['name'], 'module_stage': stage,
            'talent_index': index, 'part_index': part_index, 'candidate_index': candidate_index,
            'raw_candidate': deepcopy(raw)}


def _provenance(state, level_override):
    # Read the already merged public view; do not copy an AccountCache, RunState,
    # opaque caller or its fields/ranks/history. No new precedence is introduced.
    state = state or {}
    fields = state.get('fields', {})
    confirmed = state.get('run_confirmed_fields', ()) if state.get('scope') == 'run' else ()
    return {key: ('simulated_override' if key == 'level' and level_override else
                  'preview_unconfirmed' if key not in fields else
                  'run_confirmed' if key in confirmed else 'account_reference')
            for key in _TRAINING_FIELDS}


def explanations(profile, scenario, *, state=None, level_override=False, values=None):
    """Return isolated explanation rows, without changing any input or report.

    No operator/skill placeholder or unrelated operator calls the selector. A
    presentation selection error is visible as unavailable source information;
    the original calculation still handles the same raw values/errors itself.
    """
    operator = scenario.get('operator')
    skill = scenario.get('skill')
    if operator not in TARGET_OPERATORS or profile is None or not skill:
        return []
    source = _source_data()['operators'][operator]
    definitions = [row for row in source['fields'] if skill in row['skills']]
    if not definitions:
        return []
    from .operator_engine import selected_talents
    selection_error = None
    try:
        selected, parts = selected_talents(profile, scenario)
    except (ValueError, TypeError, KeyError, IndexError) as error:
        selected, parts = [], []
        selection_error = {'type': type(error).__name__, 'message': str(error)}
    provenance = _provenance(state, level_override)
    relevant = ('elite', 'level', 'potential') + (('module_id', 'module_level')
                                               if scenario.get('module_id') else ())
    rows = []
    for definition in definitions:
        matching = [talent for talent in selected if talent.get('name') == definition['talent_name']]
        talent = matching[0] if len(matching) == 1 else None
        original = None
        if talent is not None:
            try:
                original = _original_source(operator, source, profile, scenario, talent, parts,
                                            definition['talent_index'])
            except (ValueError, TypeError, KeyError, IndexError):
                original = None
        rows.append({
            'operator': operator, 'field': definition['field'], 'label': definition['label'],
            'talent_name': definition['talent_name'], 'talent_index': definition['talent_index'],
            'eligibility_status': ('unavailable' if selection_error else 'met' if talent else 'unmet'),
            'source_status': ('located' if original else 'missing' if talent or selection_error else 'not_selected'),
            'selected_talent': deepcopy(talent), 'original_source': original,
            'first_original_gate': deepcopy(definition['first_original_gate']),
            'modeled_parameter_keys': list(definition['modeled_parameter_keys']),
            'effective_training': {key: scenario.get(key) for key in _TRAINING_FIELDS},
            'training_provenance': dict(provenance),
            'uses_unconfirmed_preview': any(provenance[key] in ('preview_unconfirmed', 'simulated_override')
                                           for key in relevant),
            'uses_account_reference': any(provenance[key] == 'account_reference' for key in relevant),
            'condition_value': (values or {}).get(definition['field']),
            'scope_note': definition['scope_note'], 'selection_error': deepcopy(selection_error),
            'account_unlock_verified': None, 'actual_activation': None, 'native_attachment': None,
            'new_arithmetic_applied': False,
        })
    return rows


def format_explanation(row):
    """Plain UI text; original markup, hashes and URLs stay in structured data."""
    prefix = row['label'] + '｜' + row['talent_name'] + '：'
    if row['eligibility_status'] == 'unavailable':
        status = '培养来源暂不可解读；原计算流程继续处理输入与错误。'
    elif row['eligibility_status'] == 'unmet':
        gate = row['first_original_gate']
        status = (f'当前测算培养未选中该天赋（基础来源从精英{gate["elite"]} '
                  f'Lv{gate["level"]}、潜能{gate["potential_one_based"]}开放）。')
    else:
        status = ('预览培养资格满足' if row['uses_unconfirmed_preview'] else '当前测算培养资格满足')
        original = row['original_source']
        if original is None:
            status += '；原件坐标来源缺失。'
        elif original['table'] == 'battle_equip_table':
            status += f'；所选来源：{original["module_name"]} · 模组阶段{original["module_stage"]}。'
        else:
            status += '；所选来源：基础天赋。'
    sources = '；'.join(_FIELD_LABELS[key] + '：' + _SOURCE_LABELS[row['training_provenance'][key]]
                       for key in ('elite', 'level', 'potential'))
    if row['effective_training']['module_id']:
        sources += '；' + '；'.join(_FIELD_LABELS[key] + '：' + _SOURCE_LABELS[row['training_provenance'][key]]
                                  for key in ('module_id', 'module_level'))
    value = row['condition_value']
    declared = ('是' if value else '否') if type(value) is bool else ('未声明' if value is None else str(value))
    return (prefix + status + '\n培养来源：' + sources + '。当前局外条件声明：' + declared + '。\n' +
            row['scope_note'] + ' 培养资格不确认实际触发、账号任务解锁或原生附着。')
