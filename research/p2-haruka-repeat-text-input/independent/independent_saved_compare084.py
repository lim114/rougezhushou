"""Independent complete saved typed output and exact error comparison, zero API calls."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-haruka-repeat-text-input-084')
ERROR = {'type': 'ValueError', 'message': 'haruka_repeat 不接受文本条件；请使用布尔值。'}

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)

def decode(tree):
    tag = tree[0]
    if tag == 'none':
        assert len(tree) == 1
        return None
    assert len(tree) == 2
    if tag == 'bool':
        assert type(tree[1]) is bool
        return tree[1]
    if tag == 'int':
        assert type(tree[1]) is int
        return tree[1]
    if tag == 'str':
        assert type(tree[1]) is str
        return tree[1]
    if tag == 'float':
        value = float(tree[1]); assert repr(value) == tree[1]
        return value
    if tag in ('list', 'tuple'):
        result = [decode(v) for v in tree[1]]
        return tuple(result) if tag == 'tuple' else result
    assert tag == 'dict'
    result = {}
    for key, value in tree[1]:
        key = decode(key); assert key not in result
        result[key] = decode(value)
    return result

def compare(old, new):
    assert len(old) == len(new)
    counts = Counter()
    for index, (a, b) in enumerate(zip(old, new, strict=True)):
        assert a['label'] == b['label'] and canonical(a['scenario']) == canonical(b['scenario'])
        for row in (a, b):
            if 'result' in row:
                assert canonical(decode(row['typed_result'])) == canonical(row['result']), (index, 'native tree not bound to public result')
                assert set(row) == {'label', 'scenario', 'result', 'typed_result', 'estimate_text', 'report_text', 'technical_report_text', 'actual_source_selection'}
                assert all(type(row[key]) is str and row[key] for key in ('estimate_text', 'report_text', 'technical_report_text'))
        if 'error' in a:
            assert canonical(a) == canonical(b), (index, 'old error drift')
            counts['old_errors_exact'] += 1
        elif 'error' in b:
            assert b['error'] == ERROR
            assert a['scenario']['operator'] == 'char_4202_haruka' and a['scenario']['skill'] == 2
            assert a['scenario']['elite'] >= 1 and isinstance(a['scenario'].get('haruka_repeat'), str)
            assert set(b) == {'label', 'scenario', 'error'}
            counts['active_text_rejected'] += 1
        else:
            assert canonical(a['typed_result']) == canonical(b['typed_result']), (index, 'native typed result drift')
            assert canonical(a) == canonical(b), (index, 'whole public output/reports/source drift')
            assert not (a['scenario']['operator'] == 'char_4202_haruka' and a['scenario']['skill'] == 2
                and isinstance(a['scenario'].get('haruka_repeat'), str))
            counts['whole_success_same'] += 1
    return dict(counts)

if __name__ == '__main__':
    sealed = json.loads((AUTHOR / 'review-freeze84.json').read_bytes())
    inputs = {}; rows = []
    cases = json.loads((AUTHOR / 'public-cases84.json').read_bytes())
    assert len({canonical(row['scenario']) for row in cases}) == len(cases) == 216
    for name in ('baseline-public84.json', 'draft-public84.json'):
        raw = (AUTHOR / name).read_bytes()
        inputs[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        assert inputs[name]['sha256'] == sealed['public_comparison']['raw_sha256'][name]
        parsed = json.loads(raw)
        assert [{'label': r['label'], 'scenario': r['scenario']} for r in parsed] == cases
        rows.append(parsed)
    counts = compare(*rows)
    assert counts == {'whole_success_same': 134, 'active_text_rejected': 64, 'old_errors_exact': 18}
    compression = json.loads((AUTHOR / 'compression-receipt84.json').read_bytes())
    for proof in compression['files']:
        raw = Path(proof['source_raw']).read_bytes(); compressed = Path(proof['source_gzip']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == proof['raw_sha256'] and len(raw) == proof['raw_bytes']
        assert hashlib.sha256(compressed).hexdigest() == proof['gzip_sha256'] and len(compressed) == proof['gzip_bytes']
        assert gzip.decompress(compressed) == raw
    receipt = {'status': 'PASS', 'saved_unique_pairs_reviewed': 216, 'counts': counts,
        'author_432_matrix_calls_repeated': 0, 'input_hashes': inputs,
        'native_type_trees_before_JSON_verified_against_complete_result': True,
        'complete_public_outputs_actual_source_selections_three_reports_strict': True,
        'author_gzip_full_raw_bytes_lossless_verified': True, 'normalization': None, 'new_public_API_calls': 0}
    (OUT / 'independent-saved-comparison084.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(receipt, ensure_ascii=False))
