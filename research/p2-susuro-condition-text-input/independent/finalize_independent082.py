"""Fresh narrow closure and manifest; frozen source/large calls remain untouched."""
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-empty-source-consumer-audit-after-080')
scope = {'__file__': str(OUT / 'independent_saved_compare082.py')}
exec((OUT / 'independent_saved_compare082.py').read_text().split('rows = []', 1)[0], scope)
rows = [json.loads(gzip.decompress((OUT / name).read_bytes())) for name in (
    'independent-public-baseline082.json.gz', 'independent-public-draft082.json.gz')]
counts = scope['compare'](*rows)
assert len(rows[0]) == 12 and counts == {'active_text_rejected': 3, 'whole_success_same': 6, 'old_errors_exact': 3}
source = json.loads((OUT / 'independent-source-static082.json').read_text())
saved = json.loads((OUT / 'independent-saved-comparison082.json').read_text())
assert source['status'] == saved['status'] == 'PASS'
sealed = json.loads((AUTHOR / 'review-freeze82.json').read_text())
for rel, key in [('section82.patch', 'patch_sha256'),
                  ('draft/rouge/operator_engine.py', 'engine_after_sha256'),
                  ('draft/tests/test_susuro_condition_text_input.py', 'test_sha256'),
                  ('source-receipt82.json', 'source_receipt_sha256')]:
    assert hashlib.sha256((AUTHOR / rel).read_bytes()).hexdigest() == sealed[key]
compression = json.loads((AUTHOR / 'compression-receipt82.json').read_text())
for row in compression['files']:
    raw = Path(row['source_raw']).read_bytes()
    compressed = Path(row['source_gzip']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['raw_sha256'] and len(raw) == row['raw_bytes']
    assert hashlib.sha256(compressed).hexdigest() == row['gzip_sha256'] and len(compressed) == row['gzip_bytes']
    assert gzip.decompress(compressed) == raw
log = (OUT / 'independent-new-tests082.log').read_text()
assert 'Ran 8 tests' in log and log.rstrip().endswith('OK')
diagnostic = {'review_code_test_preparation_failures': 0,
    'read_path_preparation': 'An initial read requested guessed compare82.py rather than actual listed compare-matrix82.py; missing file output retained as review metadata here; read-only and no dependent mutations/calls launched.',
    'author_preparation_preserved': ['system python source helper import missing cv2, retried with correct repository venv',
                                    'initial public discovery summary talents null came from absent field and was corrected in metadata without rerun'],
    'fresh_API_or_saved_matrix_failed_checks': 0, 'product_failures': 0}
(OUT / 'preparation-diagnostics082.json').write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_FROZEN', 'section': 82, 'baseline_commit': sealed['baseline_commit'],
    'source_static_receipt': source, 'native_typed_saved_pairs_reviewed': 426,
    'saved_counts': saved['counts'], 'author_saved_852_calls_not_repeated': True,
    'fresh_unique_inputs': 12, 'fresh_pairs': 12, 'fresh_calculate_calls': 24, 'fresh_counts': counts,
    'fresh_native_type_trees_complete_outputs_actual_source_selection_three_reports_compared': True,
    'new_tests_passed': 8, 'new_tests_skipped': 0, 'author_related_46_not_repeated': True,
    'actual_source_helper_selection_checks_separate_from_calculate_calls': 30,
    'lossless_author_gzip_full_bytes_verified': True,
    'normalization': None, 'only_supported_change': sealed['public_comparison']['only_allowed_change'],
    'qualified_zero_scope_does_not_hide_rejection': True,
    'E0_unselected_talent_other_owner_and_nontext_alias_outputs_preserved': True,
    'old_error_priority_preserved': True, 'caller_cached_catalog_native_types_unchanged': True,
    'tracked_or_author_source_changes': False, 'GUI_Wine_native_Windows_game_checks': False,
    'native_friendly_acquisition_overhealing_attachment_stacking_newly_inferred': False,
    'root81_relics_transport_absent': True,
    'root_requirements': 'Apply surgical patch after current81, register new test and complete relevant/root checks; current root behavior not claimed by frozen author/independent checks.',
    'frozen_hashes': {key: sealed[key] for key in ('patch_sha256', 'engine_after_sha256', 'test_sha256', 'source_receipt_sha256')},
    'prepared_diagnostics_preserved': True}
(OUT / 'independent-review-final082.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name != 'independent-public-manifest082.json' and '__pycache__' not in path.parts:
        raw = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)),
                      'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
manifest = {'format_version': 1, 'section': 82, 'status': 'FINAL_SEALED', 'file_count': len(files),
            'files': files, 'total_bytes': sum(row['bytes'] for row in files),
            'manifest_self_excluded': True, 'public_artifacts_only': True, 'whole_source_trees_excluded': True}
(OUT / 'independent-public-manifest082.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'fresh_counts': counts, 'file_count': len(files),
    'manifest_sha256': hashlib.sha256((OUT / 'independent-public-manifest082.json').read_bytes()).hexdigest(),
    'review_final_sha256': hashlib.sha256((OUT / 'independent-review-final082.json').read_bytes()).hexdigest()}, ensure_ascii=False))
