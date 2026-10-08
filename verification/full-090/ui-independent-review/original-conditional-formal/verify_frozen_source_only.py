"""Independent frozen runner review: stdlib/Git read operations only, no project execution."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

HERE = Path(__file__).resolve().parent
PACKET = Path('/workspace/.continuation/ui-090-final')
ROOT = Path('/workspace/rougezhushou')
COMMIT = '5e2ff697402d06e78b239e01f0b4307b50dd5633'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def literal_named(tree, name):
    values = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    assert len(values) == 1, (name, len(values))
    return ast.literal_eval(values[0])


def cut_marked(raw, start, finish, blank_after=False):
    assert raw.count(start) == raw.count(finish) == 1
    a = raw.index(start)
    b = raw.index(finish, a) + len(finish)
    assert raw[b:b + 1] == b'\n'
    b += 1
    if blank_after:
        assert raw[b:b + 1] == b'\n'
        b += 1
    return raw[:a] + raw[b:]


manifest_path = PACKET / 'public-artifacts-manifest-final-runner090.json'
manifest_raw = manifest_path.read_bytes()
assert digest(manifest_raw) == '7675565345cd55711cb975c83dc49c433d1be7cfe0054634bc68938576822e10'
manifest = json.loads(manifest_raw)
assert manifest['format_version'] == 1 and len(manifest['files']) == 237
seen = set()
for row in manifest['files']:
    path = Path(row['source_path'])
    name = row['archive_path']
    rel = PurePosixPath(name)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    assert name == rel.as_posix() and not rel.is_absolute() and '\\' not in name
    assert rel.parts and not any(part in ('.', '..', '.git') for part in rel.parts)
    assert name not in seen
    seen.add(name)
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
assert sum(row['bytes'] for row in manifest['files']) == 6695962

runner_path = PACKET / 'wine-ui-smoke-090-final.py'
runner_raw = runner_path.read_bytes()
assert digest(runner_raw) == 'bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a'
tree = ast.parse(runner_raw)
rows = literal_named(tree, 'rows090')
states89 = literal_named(tree, 'saved89_states090')
counts = Counter(row['section'] for row in rows)
assert counts == {86: 44, 88: 8}
assert rows == json.loads((PACKET / 'saved52-UI-producer-inputs-and-public-projections090.json').read_bytes())['rows']
assert len({json.dumps(row['input'], sort_keys=True, separators=(',', ':')) for row in rows}) == 39
assert [r['saved_sequence'] for r in states89] == [19, 9, 3, 22, 6]
contract = json.loads((PACKET / 'review-saved89-source/expected-ten-state-contract089.json').read_bytes())['rows']
assert len(contract) == 10 and {(r['saved_sequence'], r['use_run_training']) for r in contract} == {
    (seq, use) for seq in (19, 9, 3, 22, 6) for use in (False, True)}

binding_path = PACKET / 'actual-root090-source-binding.json'
binding_raw = binding_path.read_bytes()
assert digest(binding_raw) == '0175e121f0df09f724949a85c1a3e4f8c0ab28c671867977c6579c422529879f'
binding = json.loads(binding_raw)
source_map = {r['root_relative_path']: r['sha256'] for r in binding['rows']}
assert len(source_map) == len(binding['rows']) == 730
assert literal_named(tree, '_SOURCE090') == source_map
ctx_path = Path('/workspace/.compat/wine-validation-090-context.json')
ctx = json.loads(ctx_path.read_bytes())
assert ctx['commit'] == COMMIT and ctx['source_sha256'] == source_map
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
assert head == COMMIT
working_map = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
               for folder in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / folder).rglob('*'))
               if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert working_map == source_map
proc = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
    input=('\n'.join(COMMIT + ':' + row['root_relative_path'] for row in binding['rows']) + '\n').encode(),
    check=True, capture_output=True)
cursor = 0
for row in binding['rows']:
    end = proc.stdout.index(b'\n', cursor)
    header = proc.stdout[cursor:end].split()
    assert header[1] == b'blob' and header[0].decode() == row['git_blob']
    size = int(header[2])
    raw = proc.stdout[end + 1:end + 1 + size]
    assert size == row['bytes'] and digest(raw) == row['sha256']
    assert raw == (ROOT / row['root_relative_path']).read_bytes()
    cursor = end + 1 + size + 1
assert cursor == len(proc.stdout)
runtime_ui_map = {name: sha for name, sha in source_map.items() if name.startswith('rouge/')}
assert len(runtime_ui_map) == 126

# Remove independently identified additive spans, reverse six exact metadata
# changes and only output suffixes. This reads no author generation executable.
inverse_proof = json.loads((PACKET / 'old4217-byte-inverse-proof090.json').read_bytes())
inverse = cut_marked(runner_raw, b'# BEGIN FINAL090 SOURCE GUARD', b'# END FINAL090 SOURCE GUARD', True)
helpers = (PACKET / 'runner-helpers090.txt').read_bytes() + b'\n'
assert inverse.count(helpers) == 1
inverse = inverse.replace(helpers, b'', 1)
inverse = cut_marked(inverse, b'        # BEGIN FINAL090 STARTUP INSTRUMENTATION', b'        # END FINAL090 STARTUP INSTRUMENTATION')
inverse = cut_marked(inverse, b'        # BEGIN FINAL090 STARTUP SNAPSHOT', b'        # END FINAL090 STARTUP SNAPSHOT')
inverse = cut_marked(inverse, b'        # BEGIN FINAL090 ACTUAL SOURCE-BOUND ADDITIONS', b'        # END FINAL090 ACTUAL SOURCE-BOUND ADDITIONS', True)
inverse = cut_marked(inverse, b'    # BEGIN FINAL090 LOSSLESS NEW STATE OUTPUT', b'    # END FINAL090 LOSSLESS NEW STATE OUTPUT')
for row in inverse_proof['six_preserved_count_only_metadata_adjustments_reversed']:
    old, new = row['old'].encode(), row['new'].encode()
    assert inverse.count(new) == 1
    inverse = inverse.replace(new, old, 1)
metadata = b"        receipt['preserved_full_085_checks']=len(checks)-(group090_end-group090_start)\n        assert receipt['preserved_full_085_checks']==4217,receipt['preserved_full_085_checks']\n        assert len(checks)==4283,len(checks)\n"
assert inverse.count(metadata) == 1
inverse = inverse.replace(metadata, b'', 1).replace(b'-090', b'-085')
old_raw = Path(inverse_proof['old_actual085']['source_path']).read_bytes()
assert digest(old_raw) == 'b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306'
assert inverse == old_raw

result = {
    'format_version': 1, 'status': 'STATIC_HASH_SOURCE_INVERSE_PASS_NO_PROJECT_EXECUTION',
    'public_manifest': {'source_path': str(manifest_path), 'sha256': digest(manifest_raw), 'files': 237, 'bytes': 6695962},
    'runner': {'source_path': str(runner_path), 'sha256': digest(runner_raw), 'AST_parsed_without_import_or_execution': True},
    'actual_commit': COMMIT, 'all730_Git_working_context_guard_equal': True,
    'source_binding_sha256': digest(binding_raw),
    'runtime_UI_source_hash_scope': {'files': 126, 'selector': 'rouge .py/.json excluding __pycache__',
        'separate_root_context_scope': 730, 'UI_runtime_map_must_not_be_described_as730': True},
    'old4217_inverse': {'all_old_bytes_exact': True, 'bytes': len(inverse), 'sha256': digest(inverse)},
    'new_rows': {'86': 44, '87': 4, '88': 8, '89': 10, 'total': 66, 'planned_total': 4283},
    'rows52': {'unique_requested_inputs': 39, 'sealed_plan_exact': True},
    'saved89': {'sequence_ids': [19, 9, 3, 22, 6], 'both_training_modes': 10},
    'project_calls': {'API': 0, 'helper': 0, 'tests': 0, 'Qt': 0, 'Wine': 0},
    'actual_GUI_pass_claimed': False,
}
(HERE / 'static-hash-source-inverse-receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
