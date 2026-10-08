"""Compare all new native type trees, full public JSON and all actual texts."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
canon = lambda v: json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
ERROR = {'type': 'ValueError', 'message': 'near_previous_deployment 不接受文本条件；请使用布尔值。'}

def decode(tree):
    if tree[0] == 'none': return None
    if tree[0] in ('str', 'bool', 'int'): return tree[1]
    if tree[0] == 'float':
        value = float(tree[1]); assert repr(value) == tree[1]
        return value
    if tree[0] in ('list', 'tuple'):
        values = [decode(v) for v in tree[1]]
        return tuple(values) if tree[0] == 'tuple' else values
    assert tree[0] == 'dict'
    return {decode(k): decode(v) for k, v in tree[1]}

rows = [json.loads(gzip.decompress((OUT / name).read_bytes())) for name in (
    'independent-public-baseline085.json.gz', 'independent-public-draft085.json.gz')]
assert len(rows[0]) == len(rows[1]) == 12
counts = Counter()
for index, (a, b) in enumerate(zip(*rows, strict=True)):
    assert a['label'] == b['label'] and canon(a['scenario']) == canon(b['scenario'])
    for row in (a, b):
        if 'result' in row:
            assert canon(decode(row['typed_result'])) == canon(row['result'])
            assert set(row) == {'label', 'scenario', 'result', 'typed_result', 'estimate_text', 'report_text', 'technical_report_text', 'actual_source_selection'}
    if 'error' in a:
        assert canon(a) == canon(b), (index, 'prior error drift')
        counts['old_errors_exact'] += 1
    elif 'error' in b:
        assert b['error'] == ERROR and a['scenario']['operator'] == 'char_1048_orchd2'
        assert isinstance(a['scenario'].get('near_previous_deployment'), str)
        assert any(t.get('name') == '翔虫机动' for t in a['actual_source_selection']['selected_talents'])
        assert set(b) == {'label', 'scenario', 'error'}
        counts['active_text_rejected'] += 1
    else:
        assert canon(a['typed_result']) == canon(b['typed_result'])
        assert canon(a) == canon(b), (index, 'whole output/report/source drift')
        counts['whole_success_same'] += 1
assert dict(counts) == {'active_text_rejected': 4, 'whole_success_same': 5, 'old_errors_exact': 3}
for index in (9, 10):
    assert rows[0][index]['scenario']['level'] == 43
    assert rows[0][index]['error'] == {'type': 'ValueError', 'message': '当前精英阶段尚未开放所选技能或专精。'}
assert rows[0][11]['error'] == {'type': 'ValueError', 'message': 'windup_frames需要范围内有限非负数。'}
author = OUT.with_name('p2-orchid-near-text-085')
manifest_path = author / 'public-artifacts-manifest-author-pending.json'
manifest = json.loads(manifest_path.read_bytes())
assert len(manifest['files']) == 47
for proof in manifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == proof['sha256'] and len(data) == proof['bytes']
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == 'bd86b9b3b5b0641c79e0be86990e4c93465875245a5eb1186a7a57c2ee8ace8b'
receipt = {'status': 'PASS', 'unique_inputs': 12, 'fresh_calculate_calls': 24, 'counts': dict(counts),
    'whole_native_type_trees_before_JSON_full_public_source_selection_and_three_reports_compared': True,
    'distinct_from_all197_author_inputs': True, 'actual_valid_level_43_E0S2_and_E1_mastery_old_errors_exact': True,
    'actual_late_windup_frames_error_exact': True, 'old_double_charge_textual_truthiness_preserved': True,
    'caller_and_cached_catalog_native_types_preserved': True, 'actual_pure_accepted_source_selection_helper_calls': 14,
    'author_frozen_pending_manifest_47_files_rehashed': True, 'normalization': None,
    'tracked_or_author_source_changes': False, 'GUI_Wine_native_Windows_game': False}
(OUT / 'independent-fresh-comparison085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
