"""Seal bounded negative source review, with no product calls or patches."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-after086-finite-input-source')
SUB = OUT / 'guard-subreview'
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest_bytes = (SUB / 'public-artifacts-manifest.json').read_bytes()
assert sha(manifest_bytes) == '11503a0293bc0bcb889767d519a9fce769234728148fb9c6a7173b8c83fa74d2'
submanifest = json.loads(manifest_bytes)
assert len(submanifest['files']) == 6
for proof in submanifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
assert sha((SUB / 'guard-subreceipt.json').read_bytes()) == 'e5ad4c2bcc9ffd6df40c0225a713e42a8418a837a7b6cca464351a7f6e29aa24'
artifacts = json.loads((OUT / 'fixed-artifacts-review085.json').read_bytes())
bridge = json.loads((OUT / 'run-preparation-bridge085.json').read_bytes())
assert artifacts['status'] == 'PASS_BOUNDED_SOURCE_ARTIFACTS_ONLY' and bridge['status'] == 'PASS_STATIC_FIXED_RUN_BRIDGE'
assert artifacts['fixed_commit'] == bridge['fixed_commit'] == '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
author_manifest = (AUTHOR / 'public-artifacts-manifest.json').read_bytes()
author_handoff = (AUTHOR / 'handoff.json').read_bytes()
assert sha(author_manifest) == '58d25683715beef74e048b26c3e27014616e7c6b33cfded4d147ce9a8a825bb1'
assert sha(author_handoff) == 'ffa3cc6943d8833efb65a897a4fc64d12ee37278bdfd3e3cd627f05d4af4c5b1'
for proof in json.loads(author_manifest)['files']:
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
diagnostics = {'product_API_helper_test_failures': 0,
    'parent_bridge_script_preparation_failure': {'attempts': 1, 'exception': 'ValueError: min() iterable argument is empty',
        'cause': 'Initial static AST assertion guessed resolve_relics, while fixed _prepare_damage imports relics.prepare.',
        'correction': 'Use actual prepare alias and preserve original script/log. Corrected static capture passed.',
        'new_project_call_or_mutation_during_failure': False},
    'subreview_preparation': 'One CRLF representation mismatch on excerpt comparison, corrected against the same newline layer; raw hash checks stayed exact. Initial script/trace/diagnostic preserved in sealed6. One edit context mismatch caused no mutation and was recorded.',
    'runtime_tests_or_probes_retried': 0}
(OUT / 'preparation-diagnostics085.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_BOUNDED_NEGATIVE_SOURCE_ONLY', 'numbered_section': False,
    'fixed_commit': artifacts['fixed_commit'], 'actionable_candidates': [],
    'author38_public_artifact_hashes_verified': True, 'author29_source_history_git_blobs_verified': True,
    'actual_guard_entries_full_AST_excerpts_verified': 18, 'numeric_AST_calls_independently_rebuilt': 133,
    'historical_number_types_and_zero_alias_JSON_receipts_verified': 5,
    'historical_receipts_do_not_count_as_fresh_current_runtime': True,
    'actual_consumer_raw_bool_capability_and_ignored_identity_overwritten_fields_scoped': True,
    'additional_run_modifiers_prepare_run_static_bridge': {'git_blob': bridge['git_blob'],
        'whole_byte_sha256': bridge['whole_git_blob_sha256'], 'receipt_sha256': sha((OUT / 'run-preparation-bridge085.json').read_bytes()),
        'scope': 'Exact same fixed commit; bridge sends copied scenario through resolve_enemy before later relic/rune/engine evaluation. No new public call or universal old-error promise.'},
    'guard_subreview_receipt_sha256': sha((SUB / 'guard-subreceipt.json').read_bytes()),
    'guard_subreview_manifest_sha256': sha(manifest_bytes),
    'negative_conclusion': 'No source-supported absent finite gate confirmed within the bounded traced actual consumers.',
    'not_proved': ['Fresh NaN/inf rejection', 'Every possible public field or dynamic route',
                   'Every derived arithmetic overflow or fixed-point boundary', 'Native protection, game state, clocks or attachment',
                   'Universal current-runtime old-error ordering'],
    'new_UI_derived_numeric_bounds_or_global_type_policy_inferred': False,
    'new_API_project_helpers_tests_Qt_Wine_product_patches_matrices_tracked_edits': 0,
    'separate086_module_qualification_boolean_probe_search_repeated': False,
    'source_preparation_failure_originals_and_diagnostics_preserved': True,
    'author_source_manifest_sha256': sha(author_manifest), 'author_source_handoff_sha256': sha(author_handoff),
    'restart': 'Only a named active float consumer with an exact missing finite gate and existing or separately authorized qualified old public evidence warrants reopening. Stop this appendix; do not manufacture a section or repeat old matrices.'}
(OUT / 'handoff-independent-finite085.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name != 'public-artifacts-manifest-independent-finite085.json':
        data = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})
for proof in submanifest['files']:
    path = Path(proof['source_path']); assert path.is_relative_to(SUB)
    files.append({**proof, 'archive_path': str(path.relative_to(OUT))})
path = SUB / 'public-artifacts-manifest.json'
files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(manifest_bytes), 'bytes': len(manifest_bytes)})
assert len({r['archive_path'] for r in files}) == len(files)
manifest = {'format_version': 1, 'status': 'FINAL_SEALED_BOUNDED_SOURCE_ONLY', 'numbered_section': False,
    'files': files, 'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files), 'manifest_self_excluded': True,
    'public_artifacts_only': True, 'unchanged_original_author38_hash_bound_not_duplicated': sha(author_manifest),
    'whole_source_or_private_execution_trees_included': False}
(OUT / 'public-artifacts-manifest-independent-finite085.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'file_count': len(files), 'total_bytes': manifest['total_bytes'],
    'FINAL_SHA': sha((OUT / 'handoff-independent-finite085.json').read_bytes()),
    'manifest_sha256': sha((OUT / 'public-artifacts-manifest-independent-finite085.json').read_bytes())}, ensure_ascii=False))
