"""Freeze a complete independent review; never rerun author calculations."""
import gzip
import hashlib
import json
from pathlib import Path
from independent_saved_compare084 import compare

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-haruka-repeat-text-input-084')
sha = lambda value: hashlib.sha256(value).hexdigest()
rows = [json.loads(gzip.decompress((OUT / name).read_bytes())) for name in (
    'independent-public-baseline084.json.gz', 'independent-public-draft084.json.gz')]
counts = compare(*rows)
assert len(rows[0]) == 12 and counts == {'active_text_rejected': 4, 'whole_success_same': 5, 'old_errors_exact': 3}
source = json.loads((OUT / 'independent-source-static084.json').read_bytes())
saved = json.loads((OUT / 'independent-saved-comparison084.json').read_bytes())
duration = json.loads((OUT / 'independent-source-duration084.json').read_bytes())
assert source['status'] == saved['status'] == duration['status'] == 'PASS'
tests = json.loads((OUT / 'independent-new-tests084.json').read_bytes())
assert tests['passed'] and tests['tests_run'] == 8 and not tests['skipped'] and not tests['failures'] and not tests['errors']
sealed = json.loads((AUTHOR / 'review-freeze84.json').read_bytes())
assert sha((AUTHOR / 'review-freeze84.json').read_bytes()) == '39a94eed44a24b6add84f874e970310aaae5f9b7d7ed8f5b8d577d19ac38dd19'
for rel, key in [('section84.patch', 'patch_sha256'), ('draft/rouge/damage.py', 'damage_after_sha256'),
                 ('draft/tests/test_haruka_repeat_text_input.py', 'test_sha256'), ('source-receipt84.json', 'source_receipt_sha256')]:
    assert sha((AUTHOR / rel).read_bytes()) == sealed[key]
diagnostics = {'review_product_failures': 0, 'fresh_or_saved_public_comparison_failures': 0,
    'test_runner_preparation_failure': {'attempts': 1, 'exception': 'ImportError: Start directory is not importable',
        'cause': 'Frozen public tests directory has no __init__.py; unittest discover with explicit parent expected a package.',
        'correction': 'Load the exact frozen test file by importlib.util.spec_from_file_location, then loadTestsFromModule.',
        'old_runner_and_failure_log_retained': True, 'zero_tests_executed_in_failed_preparation': True},
    'static_duration_preparation_failure': {'attempts': 1, 'exception': "TypeError: string indices must be integers, not 'str'",
        'cause': 'Inline static read treated operators dict iteration as list entries.',
        'correction': 'Use the verified actual operators dict key in independent_duration084.py.',
        'calculate_or_helper_calls': 0},
    'author_preparation_preserved': [
        'Initial 7 pass / 1 failed test assumed inactive initial_target_windows was consumed for time-SP S2; corrected test only with actual source evidence.',
        'Inherited baseline field label corrected in metadata, old receipt retained; code/source/matrix hashes unchanged.',
        'Transport helper output path resolved after cwd-related preparation failure; initial script/log/patch retained.'],
    'delegation_attempt': 'Independent source sub-agent spawn rejected by active thread limit; source review completed directly by independent reviewer.'}
(OUT / 'preparation-diagnostics084.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_FROZEN', 'section': 84, 'baseline_commit': sealed['baseline_commit'],
    'source_static_receipt': source, 'source_duration_receipt': duration,
    'saved_unique_native_typed_pairs_reviewed': 216, 'saved_counts': saved['counts'],
    'author_saved_432_calls_not_repeated': True, 'fresh_unique_inputs': 12, 'fresh_pairs': 12,
    'fresh_calculate_calls': 24, 'fresh_counts': counts, 'fresh_inputs_different_from_all_author_inputs': True,
    'fresh_native_type_trees_complete_outputs_source_selection_and_three_reports_compared': True,
    'new_test_methods_passed': 8, 'new_test_methods_skipped': 0, 'author_related_39_not_repeated': True,
    'independent_static_actual_source_helper_selection_calls': 6,
    'author_gzip_lossless_full_bytes_verified': True, 'normalization': None,
    'only_supported_change': sealed['public_comparison']['only_allowed_change'],
    'qualified_E1S2_independent_of_E2_flower_talent': True,
    'inactive_S1_S3_other_owner_nontext_aliases_and_all_unknowns_preserved': True,
    'prior_error_priority_verified_bubble_timing_cultivation_and_author_outer_deployment_wine': True,
    'caller_cached_catalog_native_types_unchanged': True,
    'tracked_or_author_product_source_changes': False, 'GUI_Wine_native_Windows_game_checks': False,
    'root_requirements': 'Surgical exact two-line insertion after approved83 current guards/report; preserve83 bytes. Register new test and run required current-root checks. Current-root runtime is not certified by frozen draft checks.',
    'four_prior_readonly_files_must_be_individually_archived_by_author': source['readonly_boundary_four_files'],
    'frozen_author_hashes': {key: sealed[key] for key in ('patch_sha256', 'damage_after_sha256', 'test_sha256', 'source_receipt_sha256')},
    'preparation_diagnostics_preserved': True}
(OUT / 'independent-review-final084.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name != 'independent-public-manifest084.json' and '__pycache__' not in path.parts:
        data = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})
manifest = {'format_version': 1, 'section': 84, 'status': 'FINAL_SEALED', 'file_count': len(files),
    'files': files, 'total_bytes': sum(row['bytes'] for row in files), 'manifest_self_excluded': True,
    'public_artifacts_only': True, 'whole_source_trees_excluded': True}
(OUT / 'independent-public-manifest084.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'fresh_counts': counts, 'file_count': len(files),
    'manifest_sha256': sha((OUT / 'independent-public-manifest084.json').read_bytes()),
    'FINAL_SHA': sha((OUT / 'independent-review-final084.json').read_bytes())}, ensure_ascii=False))
