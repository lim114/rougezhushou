"""Check saved six public outcomes, strict types and the three draft texts. No API."""
import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def native(value):
    if value is None:return ['none']
    if type(value) is bool:return ['bool', value]
    if type(value) is int:return ['int', str(value)]
    if type(value) is float:return ['float', value.hex()]
    if type(value) is str:return ['str', value]
    if type(value) is list:return ['list', [native(v) for v in value]]
    if type(value) is tuple:return ['tuple', [native(v) for v in value]]
    if type(value) is dict:return ['dict', [[native(k), native(v)] for k, v in value.items()]]
    raise TypeError(type(value).__name__)

def sha(raw):return hashlib.sha256(raw).hexdigest()

target = OUT / 'saved-comparison.json'
if target.exists():raise RuntimeError('Comparison receipt already exists; do not replace results')
base = json.loads((OUT / 'public-baseline.json').read_text())
draft = json.loads((OUT / 'public-draft.json').read_text())
assert base['status'] == draft['status'] == 'THREE_PUBLIC_ENTRIES_COMPLETE'
assert base['public_API_entries'] == draft['public_API_entries'] == 3
assert base['explicit_formatter_entries'] == 0 and draft['explicit_formatter_entries'] == 3
qualification = '以上为所选触手持续在场且技能回复持续覆盖时的速度参考，包含本次采用的生命回复效果倍率；实际在场、回复首跳和结束尚未核验，实际回复总量未知。'
checks = []
for left, right in zip(base['records'], draft['records'], strict=True):
    assert left['id'] == right['id']
    for row in (left, right):
        assert row['status'] == 'returned'
        assert row['caller_json_unchanged'] and row['caller_native_unchanged']
        assert native(row['result']) == row['result_native']
        assert canonical(row['result']) == row['result_json']
    result = copy.deepcopy(right['result'])
    scenario = right['input']
    s1 = scenario['skill'] == 1
    note_inversions = []
    if s1:
        count = float(scenario['summon_count'])
        nominal = 30.0
        for observed in (False, True):
            duration = min(nominal, scenario['window_seconds']) if observed else nominal
            scope = f'观察窗口中 {duration:g} 秒的名义技能覆盖假设' if observed else f'名义技能持续参数 {duration:g} 秒'
            new = f'触手数量 {count:g}（局外假设）；{scope}下，按基础每只 70 生命/秒连续覆盖的回复参考 {70*duration*count:g}（未计生命回复效果倍率）；实际触手在场、技能回复覆盖及时钟未核验，实际回复总量未知，生命回复不计直接治疗。'
            old = f'触手数量 {count:g}；技能生命回复 {70*duration*count:g}，生命回复不计直接治疗。'
            assert result['estimate']['notes'].count(new) == 1
            i = result['estimate']['notes'].index(new)
            result['estimate']['notes'][i] = old
            note_inversions.append({'scope': 'observed' if observed else 'nominal',
                                    'duration_seconds': duration, 'base_rate': 70,
                                    'base_reference_total': 70*duration*count, 'old': old, 'new': new})
        block = next(b for b in result['report']['sections'] if b['id'] == 'regeneration')
        assert block['notes'].count(qualification) == 1
        block['notes'].remove(qualification)
        rates = {m['key']: m['value'] for m in block['metrics']}
        assert rates == {'per_token_rate': 84.0, 'all_tokens_rate': 168.0}
        assert right['result']['relic_regeneration_multiplier'] == 1.2
        text = right['formatted_text']
        assert all(item['new'] in text for item in note_inversions)
        assert qualification in text and '实际回复总量未知' in text
        assert '每只触手生命回复速度：84' in text
        assert '所选触手合计回复速度：168' in text
    else:
        assert not any(n.startswith('触手数量 ') for n in result['estimate']['notes'])
        assert '按基础每只' not in right['formatted_text']
        assert qualification not in right['formatted_text']
    assert native(result) == left['result_native'], right['id'] + ': native full-result inverse mismatch'
    assert canonical(result) == left['result_json'], right['id'] + ': JSON full-result inverse mismatch'
    assert right['formatter_preserved_result_native'] and right['formatter_preserved_result_json']
    checks.append({'id': right['id'], 's1_qualified_note_inversions': note_inversions,
                   'entire_native_result_inverse_exact': True, 'entire_JSON_result_inverse_exact': True,
                   'all_numbers_fields_HPS_timelines_other_notes_exact': True,
                   'caller_native_and_JSON_preserved': True, 'draft_formatter_result_preserved': True,
                   'draft_text_validated': True, 'S2_full_result_exact': not s1})
receipt = {'status': 'SIX_PUBLIC_OUTCOMES_AND_THREE_TEXTS_PASS', 'checks': checks,
           'calls': {'baseline_public_API': 3, 'draft_public_API': 3, 'total_public_API': 6,
                     'draft_formatter': 3, 'comparison_public_API': 0,
                     'explicit_helper': 0, 'new_tests': 0, 'Qt': 0, 'Wine': 0, 'network': 0},
           'source_both_trees_unchanged': base['source_unchanged'] and draft['source_unchanged'],
           'baseline_receipt_sha256': sha((OUT / 'public-baseline.json').read_bytes()),
           'draft_receipt_sha256': sha((OUT / 'public-draft.json').read_bytes()),
           'native_regeneration_actual_total_clock_hotupdate_certified': False,
           'application_callbacks_or_new_game_rules_added': False}
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': receipt['status'], 'pairs': len(checks), 'new_API_entries': 0,
                  'saved_receipt_sha256': sha(target.read_bytes())}))
