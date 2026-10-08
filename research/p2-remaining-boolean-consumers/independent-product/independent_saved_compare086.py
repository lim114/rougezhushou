"""Independent saved-only strict native/public/text audit; no project imports."""
import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-remaining-boolean-consumers-086-draft')
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def typed(v):
    if isinstance(v, dict): return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)): return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float): return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def decode(t):
    kind = t['type']
    if kind == 'dict':
        assert set(t) == {'type', 'items'}
        pairs = [(decode(k), decode(v)) for k, v in t['items']]
        result = dict(pairs)
        assert len(result) == len(pairs)
    elif kind in ('list', 'tuple'):
        assert set(t) == {'type', 'items'}
        result = [decode(v) for v in t['items']]
        if kind == 'tuple': result = tuple(result)
    elif kind == 'float':
        assert set(t) == {'type', 'hex'}
        result = float.fromhex(t['hex'])
    else:
        assert kind in ('str', 'bool', 'int', 'NoneType') and set(t) == {'type', 'value'}
        result = t['value']
        assert type(result).__name__ == kind
    assert canon(typed(result)) == canon(t)
    return result


def json_value(v):
    if isinstance(v, dict): return {k: json_value(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [json_value(x) for x in v]
    if isinstance(v, float) and not math.isfinite(v): return {'saved_nonfinite_float': v.hex()}
    return v


def read_saved(package, core=False):
    stem = package + ('-isolated-cores' if core else '-matrix')
    path = AUTHOR / (stem + ('.json.gz' if core else '.jsonl.gz'))
    compressed = path.read_bytes(); raw = gzip.decompress(compressed)
    summary = json.loads((AUTHOR / (stem + '-summary.json')).read_bytes())
    assert summary['passed'] and summary['gzip_sha256'] == hashlib.sha256(compressed).hexdigest()
    assert summary['gzip_bytes'] == len(compressed)
    assert summary['decoded_sha256'] == hashlib.sha256(raw).hexdigest() and summary['decoded_bytes'] == len(raw)
    rows = json.loads(raw) if core else [json.loads(line) for line in raw.splitlines()]
    return rows, {'path': str(path), 'sha256': hashlib.sha256(compressed).hexdigest(),
                  'bytes': len(compressed), 'decoded_sha256': hashlib.sha256(raw).hexdigest(), 'decoded_bytes': len(raw)}


def check_row(row, core):
    key = 'input_typed' if core else 'input_typed_before'
    assert canon(json_value(decode(row[key]))) == canon(row['input'])
    if core:
        decode(row['prepared_before']); decode(row['prepared_after'])
        assert row['original_caller_unchanged'] and row['catalog_unchanged']
    else:
        assert row['input_unchanged'] and row['catalog_unchanged']
        assert canon(row['input_typed_before']) == canon(row['input_typed_after'])
    if row['outcome'] == 'accepted':
        assert canon(json_value(decode(row['result_typed']))) == canon(row['result'])
        assert set(row['reports']) == {'estimate', 'user', 'technical'}
        assert all(type(v) is str for v in row['reports'].values())
    else:
        assert row['outcome'] == 'error' and type(row['error_message']) is str


def compare(a, b, core):
    check_row(a, core); check_row(b, core)
    output = {'result', 'result_typed', 'reports', 'outcome', 'error_type', 'error_message'}
    assert canon({k:v for k,v in a.items() if k not in output}) == canon({k:v for k,v in b.items() if k not in output})
    if a['expect'] == 'changed':
        assert a['outcome'] == 'accepted' and b['outcome'] == 'error'
        field = 'ranged_attack' if core else a['field']
        assert b['error_type'] == 'ValueError' and b['error_message'] == field + ' 不接受文本条件；请使用布尔值。'
        assert isinstance(decode(a['input_typed'] if core else a['input_typed_before']).get(field), str)
        assert set(a) - output == set(b) - output
        return 'qualified_text_rejected'
    assert canon(a) == canon(b), (a['index'], a.get('label'), 'whole row difference')
    if a['expect'] == 'old_error':
        assert a['outcome'] == 'error'
        return 'exact_old_error'
    assert a['expect'] == 'same' and a['outcome'] == 'accepted'
    return 'whole_accepted_native_and_three_reports_unchanged'


manifest_path = AUTHOR / 'archivable-author-review-manifest.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == '8e0d6a7607246573d16a97320a8cf71bf1db6e18765304b4f09916b99281443f'
manifest = json.loads(manifest_path.read_bytes()); assert len(manifest['files']) == 84
for proof in manifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert len(data) == proof['bytes'] and hashlib.sha256(data).hexdigest() == proof['sha256']
assert hashlib.sha256((AUTHOR / 'author-review-handoff.json').read_bytes()).hexdigest() == '8dc06b0dc0b5d8b73015e18b2e03eb40178d69c037e6d95b714c8983e99396f4'
freeze_path = AUTHOR / 'review-freeze86.json'
assert hashlib.sha256(freeze_path.read_bytes()).hexdigest() == 'aa066032869298b11b06819a2533fa53e78096dd725d4006f01bbde551edab55'
for proof in json.loads(freeze_path.read_bytes())['files']:
    data = Path(proof['source_path']).read_bytes()
    assert len(data) == proof['bytes'] and hashlib.sha256(data).hexdigest() == proof['sha256']
assert hashlib.sha256((AUTHOR / 'section86.patch').read_bytes()).hexdigest() == '4834ec66e47ebdf8df0e8ef0c57e19dafe1693d80f51e9061245879c33005f87'
groups = []; bindings = []
for core, count, expected in ((False,268,{'qualified_text_rejected':71,'whole_accepted_native_and_three_reports_unchanged':181,'exact_old_error':16}),
                             (True,8,{'qualified_text_rejected':2,'whole_accepted_native_and_three_reports_unchanged':6})):
    a, proof_a = read_saved('baseline', core); b, proof_b = read_saved('draft', core)
    assert len(a) == len(b) == count
    assert len({canon(row['input_typed' if core else 'input_typed_before']) + (str(row['phase_argument']) if core else '') for row in a}) == count
    counts = Counter(compare(x,y,core) for x,y in zip(a,b,strict=True)); assert dict(counts) == expected
    groups.append({'scope':'isolated_internal_core' if core else 'public_matrix','pairs':count,'counts':dict(counts)})
    bindings.extend([proof_a, proof_b])
result = {'status':'PASS','author_84_files_bytes_hash_verified':True,'author_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
          'groups':groups,'compressed_and_decoded_bindings':bindings,'fresh_public_calls':0,'fresh_project_helper_calls':0,
          'native_trees_decode_reencode_exact_and_full_public_bound':True,'whole_rows_and_three_texts_strict':True,
          'caller_catalog_saved_isolation':True,'prepared_before_after_old_to_draft_strict':True,'normalization':None,
          'scope_boundary':'8 isolated core phase arguments are internal compatibility only; saved public 536 calls and explicit core 24 helpers separately counted; no native clock or attachment conclusion.',
          'Qt':0,'Wine':0,'tracked_edits':0}
(OUT / 'independent-saved-comparison086.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
