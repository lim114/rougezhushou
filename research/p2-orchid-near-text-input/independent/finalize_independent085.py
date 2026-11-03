"""Final exact independent seal, all public proof files and explicit type scope."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-orchid-near-text-085')
SUB = OUT / 'source-subreview'
sha = lambda data: hashlib.sha256(data).hexdigest()
sealed = json.loads((AUTHOR / 'author-freeze085.json').read_bytes())
assert sha((AUTHOR / 'author-freeze085.json').read_bytes()) == '96fa448ec78f4021122520a96e6e580289a3e4f113ed3835af2f803204169026'
for rel, key in [('section85.patch', 'patch_sha256'), ('draft/rouge/damage.py', 'draft_damage_sha256'),
                 ('draft/tests/test_orchid_near_text_input.py', 'new_test_sha256'),
                 ('public-baseline085.json', 'baseline_json_sha256'), ('public-draft085.json', 'draft_json_sha256')]:
    assert sha((AUTHOR / rel).read_bytes()) == sealed[key]
submanifest = json.loads((SUB / 'public-artifacts-manifest.json').read_bytes())
assert sha((SUB / 'public-artifacts-manifest.json').read_bytes()) == '67c4d21eb99bc7e7a09978247148b8246426fe3ff971623e7a93b8aada22aee7'
assert len(submanifest['files']) == 25 and submanifest['status'] == 'final_sealed_source_guard_transport_passed'
for proof in submanifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
assert sha((SUB / 'handoff.json').read_bytes()) == '8918d795838357e8610e49998613584860f263cd019465a044aab90c9d9ad67b'
assert sha((SUB / 'source-guard-review085.json').read_bytes()) == '26d2acf6b5cabed781034d2bbfaf58c94da90dd5693164e43ba0797355314926'
source = json.loads((SUB / 'source-guard-review085.json').read_bytes())
assert source['status'] == 'passed_no_blocker' and source['helper_actual_calls'] == 9 and source['calculate_damage_calls'] == 0
saved = json.loads((OUT / 'independent-saved-comparison085.json').read_bytes())
fresh = json.loads((OUT / 'independent-fresh-comparison085.json').read_bytes())
tests = json.loads((OUT / 'independent-new-tests085.json').read_bytes())
assert saved['status'] == fresh['status'] == 'PASS'
assert tests['passed'] and tests['tests_run'] == 9 and not tests['skipped'] and not tests['failures'] and not tests['errors']
boundary = (AUTHOR / 'EVIDENCE_BOUNDARY.md').read_bytes()
(OUT / 'author-EVIDENCE_BOUNDARY.md').write_bytes(boundary)
diagnostics = {'independent_saved_fresh_tests_product_failures': 0, 'independent_execution_preparation_failures': 0,
    'readonly_preparation': 'File listing excluded baseline/draft too narrowly at first and printed a truncated listing; guessed public85.py and top-level test path were absent, then actual listed matrix85.py and draft/tests file read. No dependent execution launched on those guessed files.',
    'source_subreview_preparation': source['preparation_diagnostics'],
    'original_author_source_only_diagnostics_preserved': True,
    'evidence_scope_corrections_without_repeated_calculation': [
        'Saved 197 records are JSON value trees, without pre-encoding native tuple/list distinction; different fresh12 preserve native trees.',
        'Saved E0S2/E1mastery level90 rows first fail level validation; fresh level43 confirms actual skill/mastery priority.'],
    'communication_correction': 'Initial commentary called the owner 兰契; actual pinned raw name is 焰狐龙梓兰. All code and probes used correct char_1048_orchd2 identity.'}
(OUT / 'preparation-diagnostics085.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_FROZEN', 'section': 85, 'baseline_commit': sealed['fixed_commit'],
    'operator': 'char_1048_orchd2', 'raw_name': '焰狐龙梓兰',
    'source_subreview_final_manifest_sha256': sha((SUB / 'public-artifacts-manifest.json').read_bytes()),
    'source_subreview_final_handoff_sha256': sha((SUB / 'handoff.json').read_bytes()),
    'source_guard_receipt_sha256': sha((SUB / 'source-guard-review085.json').read_bytes()),
    'source_only_original22_and_authorcopy_verified': True, 'baseline_git_blob_files': 720, 'unchanged_old_draft_files': 719,
    'full_four_original_tables_complete_character_three_skills_30ranks_all_module_parts_verified': True,
    'product_change': 'Only six CRLF lines after completed core report: Orchid str near condition and actual selected named 翔虫机动 -> exact ValueError.',
    'guard_does_not_invent_bool_text_decoding_timer_or_native_mechanics': True,
    'saved_unique_pairs_reviewed': 197, 'saved_counts': saved['counts'], 'author_394_matrix_calls_not_repeated': True,
    'saved_complete_JSON_value_types_and_three_reports_compared': True,
    'saved_encoding_preserves_original_native_tuple_list_distinction': False,
    'fresh_unique_inputs': 12, 'fresh_calculate_calls': 24, 'fresh_counts': fresh['counts'],
    'fresh_whole_native_types_saved_before_JSON_full_public_source_selections_and_three_reports_compared': True,
    'fresh_distinct_from_all_author_inputs': True,
    'new_tests_passed': 9, 'new_tests_skipped': 0, 'author40_related_and_1328_calls_not_repeated': True,
    'new_test_internal_calculate_or_helper_calls': 'Not instrumented; no aggregate all-public-call total is claimed.',
    'pure_source_helper_calls_outside_tests': {'source_static': 9, 'saved_qualification_cache': 11, 'fresh_accepted_source_selections': 14, 'total': 34},
    'scope_of_old_error_priority': 'All 24 saved exact old errors, fresh valid-level E0S2/E1mastery and late windup error; late per-core report guard. No universal promise about all conceivable outer-branch errors.',
    'E0_other_owner_nontext_aliases_double_charge_original_contract_and_unbound_clocks_preserved': True,
    'caller_cached_catalog_and_returned_result_isolation_verified': True,
    'normalization': None, 'prior_historical_two_source_cases_not_reused_as_current_matrix': True,
    'author_frozen_pending47_all_file_hashes_verified': True,
    'author_EVIDENCE_BOUNDARY_sha256': sha(boundary), 'preparation_diagnostics_preserved': True,
    'tracked_or_author_product_source_changes': False, 'GUI_Wine_native_Windows_game_validation': False,
    'root_requirements': 'Insert only approved six lines after current83/84 guards and report, preserve prior complete bytes; add exact new test and register it. Frozen author baseline patch is not proof of apply on current root. Complete current-root checks and section85 cadence full verification.',
    'frozen_author_hashes': {k: sealed[k] for k in ('patch_sha256', 'draft_damage_sha256', 'new_test_sha256', 'baseline_json_sha256', 'draft_json_sha256')},
    'unknowns_retained': source['unknowns_retained']}
(OUT / 'independent-review-final085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name != 'independent-public-manifest085.json':
        data = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})
for proof in submanifest['files']:
    path = Path(proof['source_path'])
    assert path.is_relative_to(SUB)
    files.append({**proof, 'archive_path': str(path.relative_to(OUT))})
path = SUB / 'public-artifacts-manifest.json'; data = path.read_bytes()
files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})
assert len({r['archive_path'] for r in files}) == len(files)
manifest = {'format_version': 1, 'status': 'FINAL_SEALED', 'section': 85, 'files': files,
    'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files),
    'manifest_self_excluded': True, 'public_artifacts_only': True,
    'whole_source_execution_copies_excluded': ['source-subreview/fixed-helper-package/', 'source-subreview/readonly-apply-target/']}
(OUT / 'independent-public-manifest085.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'file_count': len(files), 'total_bytes': manifest['total_bytes'],
    'FINAL_SHA': sha((OUT / 'independent-review-final085.json').read_bytes()),
    'manifest_sha256': sha((OUT / 'independent-public-manifest085.json').read_bytes())}, ensure_ascii=False))
