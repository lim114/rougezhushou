from pathlib import Path
import collections, copy, datetime, hashlib, json

base = Path(__file__).parent
before = json.loads((base / 'baseline-results075.json').read_bytes())
after = json.loads((base / 'draft-results075.json').read_bytes())
source = json.loads((base / 'source-receipt075.json').read_bytes())
KEY = 'stage_move_speed_rune_reference'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


assert before['public_calls'] == after['public_calls'] == len(before['records']) == len(after['records'])
counts = collections.Counter()
pairs = []
mismatches = []
for old, new in zip(before['records'], after['records']):
    assert (old['api'], old['group'], old['request']) == (new['api'], new['group'], new['request'])
    for row in (old, new):
        if 'full_result' in row:
            assert row['full_result_sha256'] == digest(row['full_result'])
    if 'error' in old:
        kind = 'prior_complete_error_unchanged'
        passed = old['error'] == new.get('error')
    elif old['api'] == 'enemy_preview' and old['request']['stage_id'] == 'ro6_e_3_6':
        kind = 'only_exact_selected_parameter_reference_and_four_technical_lines_added'
        trimmed = copy.deepcopy(new['full_result'])
        move = trimmed['preview']['movement_reference']
        ref = move.pop(KEY, None)
        expected_ref = {'parameter': 1.5, 'rune_key': 'enemy_attribute_mul', 'blackboard_key': 'move_speed',
                        'source_selector': '$.runes[0].blackboard[2]',
                        'source': {k: source['raw_stage_source'][k] for k in ('url', 'sha256', 'bytes')},
                        'difficulty_mask_parameter': 'FOUR_STAR', 'profession_mask_parameter': 1023,
                        'buildable_mask_parameter': 'ALL', 'native_target_writer_layer_verified': False,
                        'combined_with_stage_multiplier_speed': None, 'complete_effective_speed_verified': False}
        subtotal = move['base_times_stage_speed']
        subtotal_text = '未知' if subtotal is None else f'{subtotal:g}'
        additions = ['关卡移速符文参数参考：1.5', '基础移速×关卡倍率小计：' + subtotal_text,
                     '符文与关卡倍率合成的移速：未知；原生目标、写入及叠加层尚未核验。',
                     '关卡移速参数来源：' + expected_ref['source']['url']]
        lines = trimmed['technical_text'].splitlines()
        exact_once = all(lines.count(line) == 1 for line in additions)
        for line in additions:
            if line in lines:
                lines.remove(line)
        trimmed['technical_text'] = '\n'.join(lines)
        passed = ref == expected_ref and exact_once and trimmed == old['full_result']
    else:
        kind = 'inactive_preview_or_all_calculations_complete_json_and_text_unchanged'
        passed = old['full_result'] == new.get('full_result')
    counts[kind] += 1
    pair = {'api': old['api'], 'group': old['group'], 'request': old['request'], 'kind': kind,
            'passed': passed, 'before_result_sha256': old.get('full_result_sha256'),
            'after_result_sha256': new.get('full_result_sha256'),
            'before_error': old.get('error'), 'after_error': new.get('error')}
    pairs.append(pair)
    if not passed:
        mismatches.append(pair)
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'paired_scenarios': len(pairs),
       'public_calls': before['public_calls'] + after['public_calls'], 'counts': dict(counts),
       'pairs': pairs, 'mismatches': mismatches,
       'all_105_stages_all_selected_enemy_references_compared': before['selected_enemy_references'],
       'strict_comparison_removes_only_one_new_parameter_location_and_exact_four_technical_lines': True,
       'existing_math_training_status_unknown_clocks_and_complete_errors_unchanged': not mismatches,
       'callers_and_public_static_caches_preserved': before['callers_and_public_static_caches_preserved'] and after['callers_and_public_static_caches_preserved']}
(base / 'matrix-comparison075.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k not in ('pairs', 'mismatches')})
assert not mismatches
