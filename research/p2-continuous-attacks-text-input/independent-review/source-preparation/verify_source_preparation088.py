"""Bounded independent saved/source audit. Imports only Python standard library."""
import ast
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
SOURCE = Path('/workspace/.continuation/p2-section088-candidate-audit')
sha = lambda b: hashlib.sha256(b).hexdigest()
canon = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def bind(path):
    b = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(b), 'sha256': sha(b)}


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def decode(t):
    kind = t['type']
    if kind == 'dict':
        v = {decode(k): decode(x) for k, x in t['items']}
    elif kind in ('list', 'tuple'):
        v = [decode(x) for x in t['items']]
        if kind == 'tuple':
            v = tuple(v)
    elif kind == 'float':
        v = float.fromhex(t['hex'])
    else:
        assert kind in ('str', 'bool', 'int', 'NoneType')
        v = t['value']
        assert type(v).__name__ == kind
    assert canon(typed(v)) == canon(t)
    return v


manifest_path = SOURCE / 'public-artifacts-manifest-source088.json'
assert sha(manifest_path.read_bytes()) == '8ec63ee21862e89abe8ead88175c39268a515fded8a865bc39a18d1c68aea645'
manifest = json.loads(manifest_path.read_bytes())
assert manifest['format_version'] == 1
for row in manifest['files']:
    assert row['archive_path'] == str(Path(row['source_path']).relative_to(SOURCE))
    assert bind(Path(row['source_path'])) == {k: row[k] for k in ('source_path', 'bytes', 'sha256')}
assert len(manifest['files']) == 24
handoff_path = SOURCE / 'source-handoff088.json'
assert sha(handoff_path.read_bytes()) == 'b06d68e6d5c9ec0979d9d4316dcc002e3c0b7e84c4652a714ee2f0810dac34e6'

static = json.loads((SOURCE / 'continuous-condition-static088.json').read_bytes())
by_path = {row['source_path']: row for row in static['source_index']}
consumers = ('rouge/amiya_continuous_reference.py', 'rouge/estimate.py',
             'rouge/operator_engine.py', 'rouge/sp_events.py', 'rouge/timing.py')
bound = []
reads = []
for rel in (*consumers, 'rouge/damage.py', 'rouge/app.py'):
    path = REPO / rel
    row = bind(path)
    assert row == by_path[str(path)]
    target = OUT / 'bound-current87' / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(path.read_bytes())
    bound.append({'repository_path': rel, **row, 'copied_path': str(target)})
    if rel in consumers:
        tree = ast.parse(path.read_bytes())
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'get' and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and node.args[0].value == 'continuous_attacks'):
                reads.append({'path': rel, 'line': node.lineno, 'expression': ast.unparse(node)})
assert len(reads) == 12
assert Counter(row['path'] for row in reads) == Counter({consumers[0]: 1, consumers[1]: 3,
                                                       consumers[2]: 6, consumers[3]: 1, consumers[4]: 1})
assert sorted((x['path'], x['line'], x['expression']) for x in reads) == sorted(
    (x['path'], x['line'], x['expression']) for x in static['get_reads'])

originals = []
for row in static['fixed_original_sources'] + static['curated_profile_sources']:
    assert bind(Path(row['source_path'])) == {k: row[k] for k in ('source_path', 'bytes', 'sha256')}
    originals.append(row)
raw_characters = json.loads(Path(static['fixed_original_sources'][0]['source_path']).read_bytes())
raw_skills = json.loads(Path(static['fixed_original_sources'][1]['source_path']).read_bytes())
for record in static['selected_original_records']:
    selected = raw_characters[record['actual_character_id']]['skills'][record['skill_number'] - 1]
    assert selected == record['raw_character_skill_entry']
    assert raw_skills[selected['skillId']]['levels'][record['rank'] - 1] == record['raw_skill_level']
(OUT / 'original-target-source-records088.json').write_text(json.dumps({
    'bindings': originals, 'selected_four_records': static['selected_original_records'],
    'scope': 'Existing original selectors only; no native attachment or clock inferred.'
}, ensure_ascii=False, indent=2) + '\n')

saved_path = SOURCE / 'public-source16.jsonl.gz'
compressed = saved_path.read_bytes()
raw = gzip.decompress(compressed)
summary = json.loads((SOURCE / 'public-source16-summary.json').read_bytes())
assert summary['gzip_sha256'] == sha(compressed) and summary['gzip_bytes'] == len(compressed)
assert summary['decoded_sha256'] == sha(raw) and summary['decoded_bytes'] == len(raw)
rows = [json.loads(line) for line in raw.splitlines()]
assert len(rows) == 16 and summary['actual_public_calls'] == 16
for row in rows:
    assert row['outcome'] == 'accepted'
    assert canon(decode(row['result_typed'])) == canon(row['result'])
    assert canon(decode(row['input_typed_before'])) == canon(row['input'])
    assert row['input_typed_before'] == row['input_typed_after']
    assert row['catalog_native_sha256_before'] == row['catalog_native_sha256_after']
    assert set(row['reports']) == {'estimate', 'user', 'technical'}
groups = []
for start in range(0, 16, 4):
    group = rows[start:start + 4]
    signature = lambda r: canon({k: r[k] for k in ('result_typed', 'result', 'reports')})
    assert [r['input']['continuous_attacks'] for r in group] == [False, True, 'false', '']
    assert signature(group[2]) == signature(group[1])
    assert signature(group[3]) == signature(group[0])
    active = signature(group[0]) != signature(group[1])
    assert active == (start < 12)
    groups.append({'label': group[0]['label'], 'active_saved_control': active,
                   'native_full_JSON_and_three_texts_bound': True,
                   'fingerprints': [sha(signature(r).encode()) for r in group]})

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
assert head == '1ce970fd30aa3b42d8ef787cde02513f05682b66'
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=REPO, text=True) == ''
receipt = {
    'format_version': 1, 'status': 'PASS_INDEPENDENT_SOURCE_PREPARATION_ONLY',
    'current_baseline_commit': head, 'old_source16_scope': 'Current86 consumer bytes unchanged at current87.',
    'source_packet_manifest': bind(manifest_path), 'source_packet_handoff': bind(handoff_path),
    'source_packet_verified_files': len(manifest['files']),
    'source_packet_verified_bytes': sum(row['bytes'] for row in manifest['files']),
    'bound_consumer_producer_core_files': bound, 'literal_reads': sorted(reads, key=lambda r: (r['path'], r['line'])),
    'saved_source16': {**bind(saved_path), 'decoded_bytes': len(raw), 'decoded_sha256': sha(raw), 'groups': groups},
    'formatter_scope': 'Original16: 48 explicit three-text requests; internal entries were not instrumented. This review has zero formatter calls.',
    'new_public_API_calls': 0, 'new_product_helper_calls': 0, 'tests_run': 0,
    'Qt': 0, 'Wine': 0, 'network': 0, 'Spine_parse': 0, 'tracked_edits': 0,
    'mechanics_or_clock_inferred': False, 'author_freeze_formal_review': 'Pending; current preview is not a final product review.'
}
(OUT / 'independent-source-preparation-receipt088.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'literal_reads': 12, 'saved_rows': 16,
                  'source_packet_verified_files': 24, 'new_project_calls': 0}))
