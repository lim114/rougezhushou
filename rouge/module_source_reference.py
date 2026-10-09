"""Selected-module original data for reports; this reference adds no arithmetic.

Raw parts remain the catalog's pinned originals. The small supplemental
projection retains metadata, ownership and ordered attribute/token blackboards
that the numerical catalog does not retain. Qualification annotations describe
supplied cultivation only, never actual activation or native attachment.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


REFERENCE_KEY = 'selected_module_source_reference'
SECTION_ID = 'selected_module_source'
TECHNICAL_HEADING = '【所选模组原件追溯】'


@lru_cache(maxsize=1)
def _reference_data():
    return json.loads((Path(__file__).parent / 'data' /
                       'module-source-reference.json').read_text(encoding='utf-8'))


def _candidate_qualification(candidate, training, module_gate):
    condition = candidate['unlockCondition']
    phase = int(condition['phase'][-1])
    elite, level = training['elite'], training['level']
    phase_met = phase <= elite
    level_met = phase < elite or condition['level'] <= level
    potential_met = candidate.get('requiredPotentialRank', 0) <= training['potential'] - 1
    candidate_gate = phase_met and level_met and potential_met
    return {
        'phase_gate_met': phase_met,
        'level_gate_met': level_met,
        'potential_gate_met': potential_met,
        'candidate_cultivation_gate_met': candidate_gate,
        'module_cultivation_gate_met': module_gate,
        'eligible_under_supplied_cultivation': module_gate and candidate_gate,
        'actual_activation': None,
    }


def _existing_coverage(result, sections):
    """Return string links only; preserve every existing specialized object."""
    section_ids = {
        'talents', 'summons', 'mei_airborne_module', 'drone_trait',
        'drone_aura', 'drone_arrival', 'gnosis_isw_a', 'mizuki_amb_y',
        'haruka_healing', 'wisdel_summon_qualification',
    }
    report_links = [
        {'path': f'/report/sections/{i}', 'section_id': block['id'], 'title': block['title']}
        for i, block in enumerate(sections)
        if block['id'] in section_ids or block['id'].startswith(('token_duration_', 'relic_token_'))
    ]
    native_links = [
        '/' + key for key in (
            'mei_airborne_module_reference', 'drone_trait_reference',
            'drone_lifecycle_reference', 'gnosis_isw_a_reference',
            'mizuki_amb_y_reference', 'haruka_healing_reference',
            'wisdel_summon_qualification_reference', 'token_duration_references',
        ) if result.get(key)
    ]
    for i, token in enumerate(result.get('relic_token_stats', ())):
        for key in ('module_reference', 'module_cost_reference'):
            if token.get(key):
                native_links.append(f'/relic_token_stats/{i}/{key}')
    return {'report_sections': report_links, 'native_paths': native_links}


def selected_module_reference(profile, scenario, result, sections):
    """Read the validated selection after calculation and copy its source data."""
    module_id = scenario.get('module_id')
    if not module_id:
        return None
    module = next((m for m in profile['modules'] if m['id'] == module_id), None)
    training = result['estimate']['training']
    stage = training['module_level']
    # Existing calculation validation owns all error types, messages and order.
    if module is None or type(stage) is not int or not 1 <= stage <= len(module['levels']):
        return None
    supplement = _reference_data()
    raw = supplement['modules'][module_id]
    source_phase = raw['phases'][stage - 1]
    raw_phase = {
        'equipLevel': source_phase['equipLevel'],
        'parts': module['levels'][stage - 1]['parts'],
        'attributeBlackboard': source_phase['attributeBlackboard'],
        'tokenAttributeBlackboard': source_phase['tokenAttributeBlackboard'],
    }
    metadata = raw['metadata']
    gate = (training['elite'] >= int(metadata['unlockEvolvePhase'][-1]) and
            training['level'] >= metadata['unlockLevel'])
    selector = f'battle_equip_table.{module_id}.phases[{stage - 1}]'
    qualifications = {}
    for i, part in enumerate(raw_phase['parts']):
        for bundle in ('addOrOverrideTalentDataBundle', 'overrideTraitDataBundle'):
            for j, candidate in enumerate((part.get(bundle) or {}).get('candidates') or ()):
                candidate_selector = f'{selector}.parts[{i}].{bundle}.candidates[{j}]'
                qualifications[candidate_selector] = _candidate_qualification(candidate, training, gate)
    reference = {
        'schema_version': 1,
        'operator_id': profile['id'],
        'module_id': module_id,
        'module_name': module['name'],
        'module_type': module['type'],
        'module_level': stage,
        'source': {
            **supplement['source'],
            'selectors': {
                'metadata': f'uniequip_table.equipDict.{module_id}',
                'ownership': (f"uniequip_table.charEquip.{raw['owner']['charEquip_owner_id']}"
                              f"[{raw['owner']['membership_index']}]"),
                'phase': selector,
            },
        },
        'raw_metadata': metadata,
        'raw_owner': raw['owner'],
        'raw_phase': raw_phase,
        'cultivation_qualification': {
            'effective_training': {key: training[key] for key in ('elite', 'level', 'potential')},
            'uses_unconfirmed_preview_conditions': bool(scenario.get('unconfirmed_training')),
            'module_cultivation_gate_met': gate,
            'scope': 'supplied_cultivation_only',
            'account_mission_unlock': None,
            'actual_equipment': None,
            'mode_or_map_applicability': None,
            'native_attachment': None,
            'new_reference_adds_arithmetic': False,
        },
        'candidate_qualifications': qualifications,
        'existing_coverage': _existing_coverage(result, sections),
    }
    # Catalog parts, cached supplement, links and every result remain isolated.
    return deepcopy(reference)


def module_source_notes(reference, existing_sections, render_description):
    """Show original trait conditions; existing named-talent notes stay authoritative."""
    metadata = reference['raw_metadata']
    qualified = reference['cultivation_qualification']
    supplied = qualified['effective_training']
    gate_label = '满足' if qualified['module_cultivation_gate_met'] else '未满足'
    notes = [
        f"所选模组：{reference['module_name']} · {reference['module_type']} · {reference['module_level']}阶。",
        (f"原件培养门槛：精英{int(metadata['unlockEvolvePhase'][-1])}、等级{metadata['unlockLevel']}；"
         f"当前情景：精英{supplied['elite']}、等级{supplied['level']}、潜能{supplied['potential']}（{gate_label}培养门槛）。"),
    ]
    if qualified['uses_unconfirmed_preview_conditions']:
        notes.append('当前培养含未确认的档案预览条件；门槛对照不代表已读取的实际面板。')
    old_notes = [note for block in existing_sections for note in block['notes']]
    seen = set()
    selector = reference['source']['selectors']['phase']
    scoped = False
    for i, part in enumerate(reference['raw_phase']['parts']):
        candidates = (part.get('overrideTraitDataBundle') or {}).get('candidates') or ()
        for j, candidate in enumerate(candidates):
            values = {item['key']: item['value'] for item in candidate['blackboard']}
            for field in ('additionalDescription', 'overrideDescripton'):
                description = candidate.get(field)
                if not description:
                    continue
                text = render_description(description, values)
                if not text or text in seen or any(text in old for old in old_notes):
                    continue
                seen.add(text)
                eligible = reference['candidate_qualifications'][
                    f'{selector}.parts[{i}].overrideTraitDataBundle.candidates[{j}]'
                ]['eligible_under_supplied_cultivation']
                label = '原件条件资料' if eligible else '原件条件资料（当前培养未满足）'
                notes.append(label + '：' + text)
        scoped = scoped or part.get('validInGameTag') is not None or part.get('validInMapTag') is not None
    if scoped:
        notes.append('原件部分记录带有模式或地图限定；实际适用性仍需对应来源核验。')
    links = reference['existing_coverage']['report_sections']
    if links:
        notes.append('已有覆盖与待确认细节见：' + '、'.join(dict.fromkeys(link['title'] for link in links)) + '。')
    notes.extend([
        '这里新增的原件资料不额外参与数值运算；已有基础属性及已支持天赋、召唤物仍按原计算覆盖处理。',
        '账户任务解锁、实际装备与原生能力附着未确认；培养门槛满足不代表条件效果已实际激活。',
        '有序原始记录、隐藏候选及完整来源可在技术资料和结构化计算数据中查看。',
    ])
    return notes


def technical_source_trace(reference):
    """Exact raw strings bypass the report formatter's presentation replacements."""
    return TECHNICAL_HEADING + '\n' + json.dumps(reference, ensure_ascii=False, indent=2)
