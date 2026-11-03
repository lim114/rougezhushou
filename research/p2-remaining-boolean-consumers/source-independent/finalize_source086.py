"""Final v1 seal for source-only review, never import or run product modules."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-remaining-boolean-consumers-086-source')
SUB = OUT / 'boundary-subreview'
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest_bytes = (SUB / 'public-artifacts-manifest086.json').read_bytes()
assert sha(manifest_bytes) == '35581c4c3fc7edfd4f47de9abc4465a9dd9023ec6f2acb05cc4983fc41df6f30'
submanifest = json.loads(manifest_bytes)
assert submanifest['status'] == 'FINAL_SEALED' and len(submanifest['files']) == 9
for proof in submanifest['files']:
    data = Path(proof['source_path']).read_bytes()
    assert sha(data) == proof['sha256'] and len(data) == proof['bytes']
assert sha((SUB / 'handoff-boundary-final086.json').read_bytes()) == '79c6538f7a2f016732c5ee7689d2cda93be1605491fd5887f153cfd7b8c87a94'
assert sha((SUB / 'receipt-boundary-final086.json').read_bytes()) == '4f02bc91507f7ba959354f8ba275d64332904f2e0fcaae2ad535f0277971cbb9'
source = json.loads((OUT / 'source-saved-review086.json').read_bytes())
literal = json.loads((OUT / 'all-literal-field-inventory086.json').read_bytes())
boundary = json.loads((SUB / 'receipt-boundary-final086.json').read_bytes())
assert source['status'] == 'PASS_SOURCE_AND_SAVED_ONLY' and literal['status'] == 'PASS_STATIC_LITERAL_INVENTORY'
assert boundary['status'] == 'PASS_FINAL_STATIC_BOUNDARY_ONLY'
assert source['new_calculate_damage_calls'] == source['new_helper_calls'] == boundary['new_calculate_damage_calls'] == 0
author_manifest = (AUTHOR / 'archivable-public-manifest.json').read_bytes()
author_handoff = (AUTHOR / 'source-handoff.json').read_bytes()
assert sha(author_manifest) == '43fb5c6cfd2806cca065c734bbc0e30e20dc2a447ff0a2ade5d45baa71647de8'
assert sha(author_handoff) == 'babbe184f0c7d69f546d257c780f6e059aaf463576338e1f7530a69920749a5f'
diagnostics = {'product_API_helper_test_failures': 0, 'source_review_execution_failures': 0,
    'initial_read_schema_preparation_failure': {'exception': "AttributeError: 'list' object has no attribute 'items'",
        'cause': 'Initial inline inspection tried .items() on original-source-hash-receipt, which is a list.',
        'correction': 'Read actual schema; independent audit loops through the four receipt rows.',
        'dependent_product_API_helper_mutation_started': False},
    'subreview_read_only_path_and_schema_preparation_preserved': boundary['preparation_read_diagnostics'],
    'author_first_source_preparation_failure_kept': 'Original named/hidden candidate comparator corrected to match frozen build_catalog name filtering; original raw hidden groups retained; no dependent API began during failure.',
    'source_unknowns_reclassified_as_mechanism': False}
(OUT / 'preparation-diagnostics086.json').write_text(json.dumps(diagnostics, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_SOURCE_ONLY', 'planned_section': 86, 'completed_product_section': False,
    'fixed_source_product_commit': source['base_commit'], 'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
    'author_source_handoff_sha256': sha(author_handoff), 'author_source_manifest_sha256': sha(author_manifest),
    'author_source28_files_rehashed': True, 'exact125_frozen_git_blob_files_and8_excerpts_verified': True,
    'owner_count': 8, 'flags': 12, 'raw_skill_ranks': 240,
    'all_descriptions_blackboards_duration_durationType_five_SP_fields_bound_to_catalog': True,
    'module_identity_and_all_original_parts_bindings': 12, 'module102_semantic_audit_repeated': False,
    'original_null_label_talent_candidates_retained': source['original_hidden_candidates_preserved_count'],
    'catalog_named_candidates_verified': source['catalog_named_candidate_bindings'],
    'exact17_get_AST_sites_rebuilt_positive_and_negative_contexts_reviewed': True,
    'all84_frozen_public_python_files_literal_read_inventory_has_no_additional_literal_read_sites': True,
    'actual_Qt_bool_producer_static_only': True,
    'saved36_native_result_trees_rebound_to_full_JSON_and_input_before_after_native_trees': True,
    'saved12_False_True_pairs_whole_native_trees_different': True,
    'saved12_text_false_whole_native_JSON_and_three_reports_exact_True': True,
    'cached_catalog_isolation_scope': 'Saved true isolation flags and original probe capture code reviewed; no new catalog runtime or probes executed.',
    'original_probe_scope': 'Only 12 qualified E2 no-module frames requests, False/True/text false; no cross-product matrix, E0/E1/module/error fresh proof.',
    'qualification_boundaries': {
        'Mizuki_enemy_below_half': 'Actual selected named 反移情 is E2; E0/E1 field read multiplies missing talent default zero and does not qualify as active numeric effect.',
        'Oblvns_ranged_attack': 'Qualified module may overwrite skill ranged factor to1; normal retains .8/1 and public normal contribution has cycle/continuous runtime gates. Module alone does not prove field inactive or every request numerically affected.',
        'Orchid_double_charge': 'Four source gets: S1 extra arrows, conditional parameter, initial/recharge SP, event-SP cost. S2/S3 ignore; normal does not fire added arrows.',
        'Orchid_power_coating': 'Field expression may read in normal plan, but numeric ratio is1 there; syntax read alone does not prove active effect.'},
    'existing_error_order_boundary': 'Static public preparation/cultivation/engine/timing/finish/report order only. Later product work must validate exact observed old errors; no all-outer-branch guarantee.',
    'new_calculate_damage_calls': 0, 'new_product_helper_calls': 0, 'new_tests': 0,
    'GUI_Qt_Wine_native_game_tracked_mutations_product_draft': False,
    'normalization_of_saved_evidence': None,
    'native_clock_attachment_hidden_script_tick_phase_and_live_state_inferred': False,
    'boundary_subreview_handoff_sha256': sha((SUB / 'handoff-boundary-final086.json').read_bytes()),
    'boundary_subreview_receipt_sha256': sha((SUB / 'receipt-boundary-final086.json').read_bytes()),
    'boundary_subreview_manifest_sha256': sha(manifest_bytes), 'preparation_diagnostics_preserved': True,
    'next_stage_requirement': 'Wait for full085 archive and root authorization; any later product draft/matrix must capture approved current83/84/85 root snapshot, preserving those guards. This b5 source-only seal is not a product completion or fresh current-root validation.'}
(OUT / 'handoff-independent-source086.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name != 'public-artifacts-manifest-independent086.json':
        data = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(data), 'bytes': len(data)})
for proof in submanifest['files']:
    path = Path(proof['source_path']); assert path.is_relative_to(SUB)
    files.append({**proof, 'archive_path': str(path.relative_to(OUT))})
path = SUB / 'public-artifacts-manifest086.json'
files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)), 'sha256': sha(manifest_bytes), 'bytes': len(manifest_bytes)})
assert len({r['archive_path'] for r in files}) == len(files)
manifest = {'format_version': 1, 'status': 'FINAL_SEALED_SOURCE_ONLY', 'planned_section': 86,
    'files': files, 'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files), 'manifest_self_excluded': True,
    'public_artifacts_only': True, 'author_source28_bound_by_sealed_manifest_not_duplicated': sha(author_manifest),
    'excluded': ['frozen whole execution package copies', 'entire pinned raw tables whose four byte hashes are bound upstream', 'original36 probes already archived in unchanged upstream28']}
(OUT / 'public-artifacts-manifest-independent086.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'file_count': len(files), 'total_bytes': manifest['total_bytes'],
    'FINAL_SHA': sha((OUT / 'handoff-independent-source086.json').read_bytes()),
    'manifest_sha256': sha((OUT / 'public-artifacts-manifest-independent086.json').read_bytes())}, ensure_ascii=False))
