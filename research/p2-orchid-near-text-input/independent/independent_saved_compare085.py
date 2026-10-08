"""Strict full saved JSON value types, no pre-encoding native tree claimed."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-orchid-near-text-085')
ERROR = 'near_previous_deployment 不接受文本条件；请使用布尔值。'
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
sha = lambda v: hashlib.sha256(v).hexdigest()

def compare(old, new, selected):
    assert len(old) == len(new)
    counts = Counter()
    for index, (a, b) in enumerate(zip(old, new, strict=True)):
        assert a['case'] == b['case'] and canon(a['scenario']) == canon(b['scenario'])
        assert a['caller_input_preserved'] is b['caller_input_preserved'] is True
        assert a['expected'] == b['expected']
        if a['outcome'] == 'error':
            assert canon(a) == canon(b), (index, 'prior error changed')
            assert a['error'] != ERROR
            kind = 'same_error'
        elif b['outcome'] == 'error':
            assert a['outcome'] == 'accepted'
            assert b['error_type'] == 'ValueError' and b['error'] == ERROR
            scenario = a['scenario']
            assert scenario['operator'] == 'char_1048_orchd2'
            assert isinstance(scenario.get('near_previous_deployment'), str)
            assert any(t.get('name') == '翔虫机动' for t in selected(scenario))
            assert set(b) == {'case', 'scenario', 'expected', 'outcome', 'error_type', 'error', 'caller_input_preserved'}
            kind = 'text_rejected'
        else:
            assert a['outcome'] == b['outcome'] == 'accepted'
            assert canon(a) == canon(b), (index, 'complete JSON value/report drift')
            scenario = a['scenario']
            assert not (scenario['operator'] == 'char_1048_orchd2' and isinstance(scenario.get('near_previous_deployment'), str)
                        and any(t.get('name') == '翔虫机动' for t in selected(scenario)))
            kind = 'same_success'
        assert kind == a['expected'], (index, 'author label not supported by actual outcome')
        for row in (a, b):
            if row['outcome'] == 'accepted':
                assert isinstance(row['result'], dict)
                assert all(isinstance(row[key], str) and row[key] for key in ('estimate_text', 'report_text', 'technical_report_text'))
        counts[kind] += 1
    return dict(counts)

if __name__ == '__main__':
    sealed = json.loads((AUTHOR / 'author-freeze085.json').read_bytes())
    assert sha((AUTHOR / 'author-freeze085.json').read_bytes()) == '96fa448ec78f4021122520a96e6e580289a3e4f113ed3835af2f803204169026'
    sys.path.insert(0, str(AUTHOR / 'baseline'))
    from rouge.catalog import catalog
    from rouge.operator_engine import selected_talents
    profile = catalog()['operators']['char_1048_orchd2']
    cache = {}
    def selected(scenario):
        # The actual frozen selector reads only these scenario qualification fields.
        key = canon({k: scenario[k] for k in ('elite', 'level', 'potential', 'module_id', 'module_level') if k in scenario})
        if key not in cache:
            talents, parts = selected_talents(profile, scenario)
            cache[key] = {'selected_talents': talents, 'module_parts': parts}
        return cache[key]['selected_talents']
    inputs = {}; matrices = []
    for name, key in [('public-baseline085.json', 'baseline_json_sha256'), ('public-draft085.json', 'draft_json_sha256')]:
        raw = (AUTHOR / name).read_bytes(); assert sha(raw) == sealed[key]
        inputs[name] = {'sha256': sha(raw), 'bytes': len(raw)}
        matrix = json.loads(raw)
        assert matrix['record_count'] == matrix['public_calculate_damage_calls'] == len(matrix['records']) == 197
        assert matrix['catalog_preserved'] is True
        assert len({canon(row['scenario']) for row in matrix['records']}) == 197
        matrices.append(matrix['records'])
    counts = compare(*matrices, selected)
    assert counts == {'text_rejected': 94, 'same_success': 79, 'same_error': 24}
    receipt = {'status': 'PASS', 'saved_unique_pairs': 197, 'counts': counts, 'author_394_matrix_calls_repeated': 0,
        'input_hashes': inputs, 'actual_pure_qualification_helper_calls': len(cache), 'qualification_receipts': cache,
        'full_JSON_value_types_and_three_texts_strict': True, 'normalization': None,
        'saved_encoding_preserves': 'JSON bool/int/float/-0.0/string/null/array/object; complete JSON value trees and all three reports.',
        'saved_native_tuple_list_distinction_recorded_before_encoding': False,
        'old_E0S2_E1rank10_rows_actual_priority': 'Their level90 is invalid, so saved errors verify level validation priority, not skill unlock/mastery.',
        'fresh_native_tree_and_valid_level_cultivation_guards_required': True, 'new_public_API_calls': 0}
    (OUT / 'independent-saved-comparison085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'qualification_receipts'}, ensure_ascii=False))
