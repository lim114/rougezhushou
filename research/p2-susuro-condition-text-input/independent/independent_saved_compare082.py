"""Complete saved native type trees and reports; no calc, no normalization."""
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-empty-source-consumer-audit-after-080')
ERROR = {'type': 'ValueError', 'message': 'low_cost_healing_target 不接受文本条件；请使用布尔值。'}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def compare(old, new):
    assert len(old) == len(new)
    counts = Counter()
    for index, (a, b) in enumerate(zip(old, new, strict=True)):
        assert a['label'] == b['label'] and canonical(a['scenario']) == canonical(b['scenario'])
        if 'error' in a:
            assert canonical(a) == canonical(b), (index, 'old error changed')
            counts['old_errors_exact'] += 1
        elif 'error' in b:
            assert b['error'] == ERROR
            assert a['scenario']['operator'] == 'char_298_susuro'
            assert isinstance(a['scenario'].get('low_cost_healing_target'), str)
            assert any(t['name'] == '微创治疗' for t in a['actual_source_selection']['selected_talents'])
            assert set(b) == {'label', 'scenario', 'error'}
            counts['active_text_rejected'] += 1
        else:
            assert canonical(a['typed_result']) == canonical(b['typed_result']), (index, 'native typed tree drift')
            assert canonical(a) == canonical(b), (index, 'whole public JSON/reports/source selection drift')
            # No selected, active Susuro text may survive as a success.
            assert not (a['scenario']['operator'] == 'char_298_susuro'
                        and isinstance(a['scenario'].get('low_cost_healing_target'), str)
                        and any(t['name'] == '微创治疗' for t in a['actual_source_selection']['selected_talents']))
            counts['whole_success_same'] += 1
    return dict(counts)


rows = []
inputs = {}
for name in ('baseline-public82.json', 'draft-public82.json'):
    raw = (AUTHOR / name).read_bytes()
    inputs[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    assert inputs[name]['sha256'] == json.loads((AUTHOR / 'review-freeze82.json').read_text())['public_comparison']['raw_sha256'][name]
    rows.append(json.loads(raw))
counts = compare(*rows)
assert len(rows[0]) == 426 and counts == {'whole_success_same': 260, 'active_text_rejected': 130, 'old_errors_exact': 36}
receipt = {'status': 'PASS', 'saved_pairs_reviewed': len(rows[0]), 'counts': counts,
           'author_852_matrix_calls_repeated': 0, 'input_hashes': inputs,
           'native_type_trees_before_JSON_preserved': True,
           'complete_public_output_source_selection_and_three_reports_strict': True,
           'normalization': None, 'new_public_API_calls': 0}
(OUT / 'independent-saved-comparison082.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
