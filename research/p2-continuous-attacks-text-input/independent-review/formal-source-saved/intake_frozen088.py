"""Source/saved review intake: bytes only, never import any project module."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
MF = AUTHOR / 'author-review-public-manifest088.json'
EXPECTED = {'author-review-public-manifest088.json': '4772c026843a995921c6013fb435fd547e2cb5a67d8f4f6e73245b7e5dbcc445',
    'author-review-handoff088.json': '7092e9b91019882657f797fc25aa89a2c9337fe1b19e5b40b60b730ae441e7b8',
    'review-freeze088.json': '10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99'}
for name, expected in EXPECTED.items():
    assert hashlib.sha256((AUTHOR / name).read_bytes()).hexdigest() == expected
manifest = json.loads(MF.read_bytes())
assert manifest['format_version'] == 1 and manifest['file_count'] == len(manifest['files']) == 89
assert sum(row['bytes'] for row in manifest['files']) == manifest['total_bytes'] == 1871550
snapshot = OUT / 'snapshots'
snapshot.mkdir(exist_ok=False)
selected_names = {'author-review-handoff088.json', 'review-freeze088.json', 'fixed-source-index088.json',
    'matrix-plan088.json', 'baseline-public60.jsonl.gz', 'draft-public60.jsonl.gz',
    'baseline-public60-summary.json', 'draft-public60-summary.json', 'run_matrix088.py',
    'test_continuous_attacks_text_input.py', 'final-test-binding088.json',
    'EVIDENCE_BOUNDARY.md', 'tail-observer-supplement088.md', 'qualification-supplement088.md',
    'preparation-diagnostics088.json', 'section88.patch'}
verified, copied = [], []
for row in manifest['files']:
    path = Path(row['source_path'])
    relative = Path(row['archive_path'])
    assert path.is_absolute() and '.local' not in path.parts
    assert path.is_relative_to(AUTHOR) or path.is_relative_to(Path('/workspace/.continuation/p2-section088-candidate-audit'))
    assert not relative.is_absolute() and '..' not in relative.parts
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], path
    verified.append(row)
    if row['archive_path'] in selected_names or row['archive_path'].startswith(('product/', 'baseline-source/')):
        destination = snapshot / relative
        assert not destination.exists()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        copied.append({'original_source_path': str(path), 'source_path': str(destination),
            'archive_path': destination.relative_to(OUT).as_posix(), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()})
(snapshot / MF.name).write_bytes(MF.read_bytes())
assert len(copied) == len(selected_names) + 13
freeze = json.loads((snapshot / 'review-freeze088.json').read_bytes())
for name, expected in freeze['product_and_test_files'].items():
    path = snapshot / ('test_continuous_attacks_text_input.py' if name.startswith('tests/') else 'product/' + name)
    raw = path.read_bytes()
    assert len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256']
receipt = {'status': 'PASS_AUTHOR89_EXPLICIT_MAPPING_ALL_BYTES_BOUND_SELECTED29_COPIES',
    'manifest_original_path': str(MF), 'manifest_sha256': EXPECTED[MF.name],
    'original_files_verified': 89, 'original_bytes_verified': 1871550,
    'all_original_bindings': verified, 'copied_key_file_count': len(copied), 'copied_bindings': copied,
    'mapping_scope': 'Actual source_path read; relative archive_path is a transport mapping, not assumed author-root-relative source path.',
    'test_actual_root_path': str(AUTHOR / 'test_continuous_attacks_text_input.py'),
    'no_source16_decode_or_rerun': True, 'no_application_calls': True,
    'calls': {'calculate_API': 0, 'production_helper': 0, 'formatter': 0, 'tests': 0,
        'network': 0, 'source_parser': 0, 'Qt': 0, 'Wine': 0, 'tracked': 0},
    'initial_local_discovery': {'cmd': 'sed -n 1,100p author-review-manifest088.json', 'exit': 2,
        'actual_stderr': 'sed: can\'t read /workspace/.continuation/p2-continuous-attacks-text-088-draft/author-review-manifest088.json: No such file or directory\n',
        'actual_file': str(MF), 'failed_discovery_attempts': 1, 'project_calls': 0},
    'initial_output_truncation_scope': 'Broad rg/full saved comparison tool displays were truncated; no omitted data inferred. All frozen rows/results subsequently read strictly by stdlib scripts.'}
with (OUT / 'frozen-intake088.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'verified_original_files': 89,
    'copied_key_files': len(copied), 'new_project_calls': 0}))
