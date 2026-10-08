"""Build one explicit final public manifest after both independent seals."""
import gzip
import hashlib
import io
import json
import shutil
from pathlib import Path

OUT = Path(__file__).resolve().parent
OLD = Path('/workspace/.continuation/p2-boolean-consumer-083-independent-source')
NUMERIC = Path('/workspace/.continuation/p2-neural-condition-text-input-083-independent-numeric')
PACKED = []


def digest(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def import_seal(source, prefix, manifest_name):
    manifest_path = source / manifest_name
    manifest = json.loads(manifest_path.read_text())
    for row in manifest['files']:
        path = source / row['archive_path']
        assert digest(path) == {'bytes': row['bytes'], 'sha256': row['sha256']}, path
        destination = OUT / prefix / row['archive_path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        if prefix == 'independent-numeric' and 'fixed-author-saved-results' in path.parts and path.suffix == '.json' and row['bytes'] > 1_000_000:
            original = path.read_bytes()
            buffer = io.BytesIO()
            with gzip.GzipFile(filename='', fileobj=buffer, mode='wb', compresslevel=9, mtime=0) as stream:
                stream.write(original)
            compressed = buffer.getvalue()
            destination = Path(str(destination) + '.gz')
            destination.write_bytes(compressed)
            restored = gzip.decompress(destination.read_bytes())
            assert restored == original
            PACKED.append({'original_source_path': str(path),
                'original_archive_path': prefix + '/' + row['archive_path'],
                'original_bytes': row['bytes'], 'original_sha256': row['sha256'],
                'compressed_source_path': str(destination),
                'compressed_archive_path': destination.relative_to(OUT).as_posix(),
                'compressed_bytes': len(compressed),
                'compressed_sha256': hashlib.sha256(compressed).hexdigest(),
                'decompressed_bytes': len(restored),
                'decompressed_sha256': hashlib.sha256(restored).hexdigest(),
                'lossless': True, 'gzip_filename': '', 'gzip_mtime': 0,
                'original_independent_manifest_preserved': True})
            continue
        if destination.exists():
            assert destination.read_bytes() == path.read_bytes()
        else:
            shutil.copy2(path, destination)
    destination = OUT / prefix / manifest_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == manifest_path.read_bytes()
    else:
        shutil.copy2(manifest_path, destination)
    return {'source_path': str(manifest_path), 'archive_path': prefix + '/' + manifest_name,
            **digest(manifest_path), 'listed_files': len(manifest['files'])}


old_seal = import_seal(OLD, 'independent-old-source', 'public-artifacts-manifest.json')
numeric_seal = import_seal(NUMERIC, 'independent-numeric', 'final-public-artifacts-manifest.json')
assert len(PACKED) == 2
(OUT / 'packed-independent-artifacts083.json').write_text(json.dumps({
    'passed': True, 'API_calls': 0, 'original_132_rows_all_verified_before_packing': True,
    'files': PACKED, 'restore_instruction':
    'Decompress each compressed_archive_path to original_archive_path and verify original SHA/bytes before replaying the unchanged independent 132-file manifest.'}, indent=2) + '\n')
formal = json.loads((OUT / 'formal-draft-freeze083.json').read_text())
comparison = json.loads((OUT / 'saved-comparison083.json').read_text())
assert comparison['passed']
related = json.loads((OUT / 'related-tests083.json').read_text())
assert related['passed'] and related['tests'] == 99 and related['skipped'] == 4
assert json.loads((OUT / 'root82-apply-check083.json').read_text())['passed']
test_name = 'tests/test_neural_condition_text_input.py'
new_test = OUT / 'draft' / test_name
assert digest(new_test) == formal['files'][test_name]
handoff = {
    'status': 'final_stable_author_and_two_independent_reviews_passed', 'section': 83,
    'baseline_commit': 'b5a40f30683bfc0945decaabbd4db5914c28427f',
    'old_source_probe_commit': 'ea7866be6f2a8e89d382ec2982a45f1cb9231141',
    'scope': 'Only two actual neural consumers reject str state after the existing report; all legacy errors execute first.',
    'production_patch': {'source_path': str(OUT / 'draft.patch'), 'archive_path': 'draft.patch',
        **digest(OUT / 'draft.patch'), 'source_only': True, 'numstat': '5\t0\trouge/damage.py\n'},
    'draft_damage': {'source_path': str(OUT / 'draft/rouge/damage.py'),
        'archive_path': 'draft/rouge/damage.py', **digest(OUT / 'draft/rouge/damage.py')},
    'new_test': {'source_path': str(new_test), 'archive_path': 'draft/' + test_name,
        **digest(new_test), 'module': 'test_neural_condition_text_input', 'tests': 9,
        'transport': 'Root copies only this exact frozen test; no test hunk in the source-only patch.'},
    'unchanged_engine_82_sha256': formal['files']['rouge/operator_engine.py']['sha256'],
    'archive_compression_proof': 'lossless-compression083.json',
    'independent_large_JSONs_original_manifest_restore_mapping': 'packed-independent-artifacts083.json',
    'author_matrix': {'pairs': 432, 'fresh_API_calls': 864, 'text_rejections': 116,
        'whole_JSON_and_three_text_reports_accepted_same': 256, 'exact_same_olderrors': 60,
        'hash_seed': '0 in both processes', 'random_seed_initial_matrix': False},
    'author_new_tests': {'tests': 9, 'passed': True, 'skipped': 0,
        'author_run_instrumented': False,
        'calls_reconstructed_from_same_frozen_test_independent_counter': 293,
        'independent_same_test_bytes_hash': formal['files'][test_name]['sha256']},
    'author_related_tests': related,
    'related_modules': [name.removesuffix('.py') for name in related['patterns']],
    'independent_old_source': {**old_seal, 'fresh_API_calls': 8,
        'accepted': 7, 'exact_olderrors': 1, 'tests_GUI_Wine': 0,
        'note': 'Two saved Orchid observations are a separate later candidate, unchanged and not rerun.'},
    'independent_formal_numeric_and_source': {**numeric_seal, 'pairs': 40,
        'fresh_pair_API_calls': 80, 'text_rejections': 11, 'whole_accepted_same': 15,
        'exact_olderrors_same': 14, 'new_tests': 9, 'new_test_API_calls': 293,
        'total_fresh_API_calls': 373, 'author_saved_432_API_calls': 0,
        'packaging_repair_review_API_calls': 0},
    'all_preparation_diagnostics': 'preparation-diagnostics083.json',
    'patch_transport_failed_attempts': 2, 'final_apply_check_attempt': 3,
    'final_apply_check_exit_code': 0, 'fourth_attempt': False,
    'root_current_source_script': {'source_path': str(OUT / 'root_current_source083.py'),
        'archive_path': 'root_current_source083.py', **digest(OUT / 'root_current_source083.py'),
        'API_calls': 0, 'expected_current_files': 721},
    'native_threshold_clock_attachment_verified_here': False,
    'new_public_fields': False, 'Qt_GUI_Wine_Windows_run_here': False,
    'tracked_mutations_here': False,
    'restart': 'Verify every final manifest SHA/bytes; verify lossless original hashes; use source-only patch and exact test bytes; root current 83 static source check before later guard changes; preserve all passed evidence and rerun only if a real new change or unresolved failure requires it.',
}
(OUT / 'handoff.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
selected = set()
for path in OUT.iterdir():
    if path.is_file() and path.name not in ('public-baseline083.json', 'public-draft083.json',
                                           'public-artifacts-manifest.json'):
        selected.add(path.relative_to(OUT).as_posix())
for name in (
    'rouge/damage.py', 'rouge/operator_engine.py', 'rouge/operator_options.py',
    'rouge/app.py', 'rouge/enemy_environment.py', 'rouge/run_modifiers.py',
    'rouge/reporting.py', 'rouge/catalog.py', 'rouge/relics.py',
    'rouge/data/catalog.json', 'rouge/data/previews.json',
    'rouge/data/operator-profiles.json', 'rouge/data/run-config.json',
    'rouge/data/enemy-difficulty-rules.json',
):
    selected.add('baseline/' + name)
selected.update(('draft/rouge/damage.py', 'draft/' + test_name))
for prefix in ('independent-old-source', 'independent-numeric'):
    for path in (OUT / prefix).rglob('*'):
        if path.is_file():
            selected.add(path.relative_to(OUT).as_posix())
rows = []
for name in sorted(selected):
    path = OUT / name
    rows.append({'source_path': str(path), 'archive_path': name, **digest(path)})
manifest = {'format_version': 1, 'status': 'final_stable', 'section': 83,
            'files': rows, 'bytes': sum(row['bytes'] for row in rows),
            'raw_large_JSONs_lossless_gzip_and_original_hashes': 'lossless-compression083.json',
            'independent_large_JSONs_lossless_restore_mapping': 'packed-independent-artifacts083.json',
            'new_API_calls_during_seal': 0}
(OUT / 'public-artifacts-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    assert digest(OUT / row['archive_path']) == {'bytes': row['bytes'], 'sha256': row['sha256']}
print(json.dumps({'passed': True, 'API_calls': 0, 'files': len(rows), 'bytes': manifest['bytes'],
    'handoff_sha256': digest(OUT / 'handoff.json')['sha256'],
    'manifest_sha256': digest(OUT / 'public-artifacts-manifest.json')['sha256']}))
