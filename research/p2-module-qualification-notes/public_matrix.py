import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.reporting import format_report

OUT = Path(sys.argv[2])
EXAMPLES = Path(sys.argv[3])

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def without_notes(value):
    if isinstance(value, dict): return {k: without_notes(v) for k, v in value.items() if k != 'notes'}
    if isinstance(value, list): return [without_notes(v) for v in value]
    return value

def numeric_projection(result):
    return {k: result.get(k) for k in ('attack', 'total_damage', 'total_healing', 'attack_speed',
                                      'base_attack_speed', 'interval_seconds', 'components', 'timing')}, {
        'base_stats': result['estimate']['base_stats'], 'skill': result['estimate']['skill']}

rows = []
examples = []
cached_before = digest(catalog())
for op, profile in catalog()['operators'].items():
    for module in profile['modules']:
        boundaries = [('E0', 0, profile['phases'][0]['max_level']),
                      ('E1', 1, profile['phases'][1]['max_level']),
                      ('below_level', 2, module['unlock_level'] - 1),
                      ('at_level', 2, module['unlock_level']),
                      ('cap', 2, profile['phases'][2]['max_level'])]
        for boundary, elite, level in boundaries:
            for stage in (1, 2, 3):
                for mode in ('frames', 'continuous'):
                    scenario = {'operator': op, 'elite': elite, 'level': level, 'skill': 1,
                                'skill_rank': 1 if elite == 0 else 7, 'timing_mode': mode,
                                'module_id': module['id'], 'module_level': stage}
                    plain = {k: v for k, v in scenario.items() if k not in ('module_id', 'module_level')}
                    frozen = copy.deepcopy(scenario)
                    requested = calculate_damage(scenario)
                    absent = calculate_damage(plain)
                    assert scenario == frozen
                    qualified = elite >= module['unlock_elite'] and level >= module['unlock_level']
                    selected, parts = selected_talents(profile, scenario)
                    base_selected, base_parts = selected_talents(profile, plain)
                    attributes = operator_attributes(op, elite, level, module_id=module['id'], module_level=stage)
                    base_attributes = operator_attributes(op, elite, level)
                    if not qualified:
                        assert attributes == base_attributes
                        assert selected == base_selected and parts == base_parts == []
                        assert numeric_projection(requested) == numeric_projection(absent)
                    text = format_report(requested)
                    claims = [n for n in requested['estimate']['notes'] if '模组' in n]
                    record = {'scenario': scenario, 'boundary': boundary, 'eligible_under_existing_gate': qualified,
                              'numeric_result_and_clock_equal_to_no_module': numeric_projection(requested) == numeric_projection(absent),
                              'training_request_preserved': requested['estimate']['training']['module_id'] == module['id'] and requested['estimate']['training']['module_level'] == stage,
                              'full_result_sha256': digest(requested), 'without_notes_sha256': digest(without_notes(requested)),
                              'no_module_full_result_sha256': digest(absent), 'notes': claims,
                              'complete': requested['estimate']['complete'], 'no_module_complete': absent['estimate']['complete'],
                              'false_applied_claim': not qualified and '当前模组基础属性已参与估算' in text,
                              'selected_talent_names': [t['name'] for t in selected], 'selected_module_parts': len(parts)}
                    rows.append(record)
                    if op in ('mechanist', 'char_298_susuro', 'char_437_mizuki') and stage in (1, 3):
                        examples.append({'scenario': scenario, 'eligible_under_existing_gate': qualified,
                                         'requested_result': requested, 'no_module_result': absent,
                                         'formatted_report': text})

assert digest(catalog()) == cached_before
obj = {'baseline_or_draft_root': sys.argv[1], 'calculation_cases': len(rows), 'full_public_calls': len(rows) * 2,
       'locked_cases': sum(not x['eligible_under_existing_gate'] for x in rows),
       'false_applied_claim_cases': sum(x['false_applied_claim'] for x in rows),
       'catalog_unchanged': True, 'integer_module_matrix_not_native_attachment_evidence': True, 'records': rows}
OUT.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
EXAMPLES.write_text(json.dumps(examples, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: v for k, v in obj.items() if k != 'records'}, ensure_ascii=False))
