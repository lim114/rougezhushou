"""Strictly compare saved records; perform no new API evaluations."""
import gzip
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
def load(label):
    path = OUT / ('public-' + label + '083.json')
    data = path.read_bytes() if path.exists() else gzip.decompress(Path(str(path) + '.gz').read_bytes())
    return json.loads(data)


old = load('baseline')
new = load('draft')
assert len(old) == len(new)
changed = []
same_success = []
same_errors = []
for before, after in zip(old, new, strict=True):
    assert before['index'] == after['index'] and before['scenario'] == after['scenario']
    args = before['scenario']
    if before == after:
        (same_errors if 'error' in before else same_success).append(before['index'])
        continue
    assert 'result' in before and 'error' in after, (before['index'], 'Only accepted text becomes an error')
    assert args['operator'] in ('char_1042_phatm2', 'char_4204_mantra')
    fields = ['enemy_in_neural_break']
    if not args.get('target_enemy'):
        fields.insert(0, 'enemy_is_boss')
    field = next(field for field in fields if isinstance(args.get(field), str))
    assert after['error'] == {'type': 'ValueError',
        'message': field + ' 不接受文本条件；请使用布尔值。'}, before['index']
    assert set(after) == {'index', 'scenario', 'error'}
    changed.append({'index': before['index'], 'field': field, 'operator': args['operator'],
                    'skill': args['skill'], 'legacy_success': True})
assert changed and same_success and same_errors
assert {r['skill'] for r in changed if r['operator'] == 'char_4204_mantra'} == {1, 2, 3}
assert {r['skill'] for r in changed if r['operator'] == 'char_1042_phatm2'} == {1, 2, 3}
receipt = {'passed': True, 'API_calls': 0, 'saved_pairs': len(old),
    'accepted_to_explicit_text_error': changed, 'whole_record_same_accepted': same_success,
    'exact_same_olderrors': same_errors, 'comparison':
    'Complete JSON and all three texts are exactly equal for accepted unchanged inputs; old error type and message remain exactly equal.'}
(OUT / 'saved-comparison083.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'passed': True, 'API_calls': 0, 'pairs': len(old),
    'text_rejections': len(changed), 'whole_accepted_same': len(same_success),
    'exact_olderrors_same': len(same_errors)}))
