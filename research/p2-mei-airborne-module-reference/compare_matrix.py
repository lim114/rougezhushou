"""Strict full outcome comparison, allowing only this qualified source reference."""
import copy
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def load(name):
    with gzip.open(ROOT / name, 'rt', encoding='utf-8') as f:
        return json.load(f)

baseline, draft = load('public-baseline.json.gz'), load('public-draft.json.gz')
assert len(baseline) == len(draft)
counts = {'qualified_reference_only_changes': 0, 'whole_success_unchanged': 0, 'old_errors_unchanged': 0}
for index, (old, new) in enumerate(zip(baseline, draft)):
    assert old['scenario'] == new['scenario'] and old['label'] == new['label']
    args = new['scenario']
    actual = new['outcome']
    if 'error' in old['outcome']:
        assert old == new, ('old error changed', index, old, new)
        counts['old_errors_unchanged'] += 1
        continue
    assert 'result' in actual, ('new error', index, actual)
    elite = args.get('elite', 2)
    level = args.get('level', 60 if elite == 2 else 60 if elite == 1 else 45)
    expected = (args['operator'] == 'char_133_mm' and args.get('module_id') == 'uniequip_002_mm'
                and elite == 2 and level >= 40 and args.get('module_level') in (1, 2, 3))
    result = actual['result']
    has_ref = 'mei_airborne_module_reference' in result
    blocks = [s for s in result['report']['sections'] if s['id'] == 'mei_airborne_module']
    assert has_ref == expected and len(blocks) == int(expected), (index, expected, has_ref, blocks)
    if expected:
        ref = result['mei_airborne_module_reference']
        assert ref['attack_scale_parameter'] == 1.1
        assert ref['module_level'] == args['module_level']
        assert ref['actual_target_is_airborne'] is None and ref['actual_conditional_damage'] is None
        assert ref['reference_only'] is True and ref['applied_to_numeric_estimate'] is False
        assert ref['native_attachment_verified'] is False and ref['damage_composition_verified'] is False
        assert ref['live_state_verified'] is False
        copy_result = copy.deepcopy(result)
        copy_result.pop('mei_airborne_module_reference')
        copy_result['report']['sections'] = [s for s in copy_result['report']['sections'] if s['id'] != 'mei_airborne_module']
        assert copy_result == old['outcome']['result'], ('unpermitted output change', index)
        counts['qualified_reference_only_changes'] += 1
    else:
        assert old == new, ('inactive output change', index)
        counts['whole_success_unchanged'] += 1
receipt = {'passed': True, 'pairs': len(draft), 'fresh_public_calls': len(draft) * 2,
           **counts, 'comparison': 'Complete JSON outcomes; only one reference field and one report section removed for qualified cases',
           'numeric_clock_scope_complete_and_all_other_report_fields_unchanged': True}
(ROOT / 'matrix-comparison.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
