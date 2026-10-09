"""Seal independent SOURCE review only; standard library, no reviewed functions."""
import gzip
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent
SHA = lambda raw: hashlib.sha256(raw).hexdigest()

def ref(value):
    p = Path(value); raw = p.read_bytes()
    return {'path':str(p),'bytes':len(raw),'sha256':SHA(raw)}

def read(value):
    return json.loads(Path(value).read_bytes())

def save(name, value):
    p = P/name
    with p.open('xb') as f:
        f.write(json.dumps(value,ensure_ascii=False,allow_nan=False,indent=2).encode()+b'\n')
    return ref(p)

source = read(P/'source-check-result095.json')
assert source['passed'] and len(source['checks']) == 27
assert (P/'source-check095.exit-code').read_bytes() == b'1\n'
assert (P/'source-check095-v2.exit-code').read_bytes() == b'0\n'
binding = read('/workspace/.continuation/full095-ui-final-v1/root-bound-input095.json')
data = json.loads(gzip.decompress(Path('/workspace/.compat/focused095-window-attempt2/wine-module-report-window-095-records.json.gz').read_bytes()))
baseline = json.loads(gzip.decompress(Path('/workspace/.compat/wine-module-report-baseline-094-for095-records.json.gz').read_bytes()))
states = {r['id']:r for r in data['states']}; differences = []
for case in binding['cases']:
    if case['comparison'] != 'paired_actual094' or case['delta']['has_addition']: continue
    old = baseline
    for k in case['baseline_pointer'][1:].split('/'):
        old = old[int(k)] if isinstance(old,list) else old[k]
    for mode in ('automatic','manual') if 'manual' in states[case['id']] else ('automatic',):
        actual,before = states[case['id']][mode],old[mode]
        a,b = actual['three_texts'],before['three_texts']
        keys = [k for k in sorted(set(a)|set(b)) if a.get(k) != b.get(k)]
        if not keys: continue
        assert keys == ['all_project_entries']
        ca,cb = a['all_project_entries'],b['all_project_entries']
        delta = {k:{'actual95':ca.get(k,0),'actual94':cb.get(k,0),'difference':ca.get(k,0)-cb.get(k,0)} for k in sorted(set(ca)|set(cb)) if ca.get(k,0) != cb.get(k,0)}
        assert actual['damage_result']['native'] == before['damage_result']['native'] and actual['visible_status'] == before['visible_status'] and a['strings'] == b['strings'] and a['applicable'] == b['applicable']
        differences.append({'id':case['id'],'mode':mode,'differing_metadata_fields':keys,'entire_actual95_all_project_entries':ca,'entire_actual94_all_project_entries':cb,'exact_count_deltas':delta,'full_native_exact':True,'all_three_actual_strings_exact':True,'visible_status_exact':True})
assert len(differences) == 6
diagnostic = save('reviewer-source-checker-diagnostic095.json',{
    'format_version':1,'status':'REVIEWER_SOURCE_CHECKER_ONLY_ATTEMPT1_OVERSTRONG_CAPTURE_METADATA_COMPARISON_CORRECTED_V2',
    'first_checker':ref(P/'review_source_full_ui095.py'),'first_log':ref(P/'source-check095.log'),'first_primary_exit':ref(P/'source-check095.exit-code'),
    'corrected_checker':ref(P/'review_source_full_ui095-v2.py'),'corrected_log':ref(P/'source-check095-v2.log'),'corrected_primary_exit':ref(P/'source-check095-v2.exit-code'),
    'same_reviewer_checker_issue_attempts':2,'reviewed_harness_Wine_API_replayed':False,'old_native_report_math_alias_comparison_relaxed':False,'actual_three_string_character_comparison_relaxed':False,
    'metadata_only_differences_preserved':differences,
    'cause':'The reviewer originally compared the entire three_texts capture dict, including measured all_project_entries. The reviewed strict-baseline contract compares applicability, every original three string and visible status; source-qualified whole native wrapper comparisons remain unchanged. Every measured count is retained here; no raw count delta is labelled a numerical-model difference.',
    'separate_reviewer_packet_sealing_diagnostic':{'tool_session':7351,'actual_completion_exit':1,'failure_before_any_packet_payload_write':True,'cause':'The initial packet assembly mistakenly predicted eight differing metadata captures; actual saved data has six. Only this reviewer assembly count was corrected, without modifying SOURCE checks, reviewed code or evidence.','corrected_actual_count':6}
})
runner = ref('/workspace/.continuation/full095-ui-final-v1/wine-full-ui-095-final.py')
mf = ref('/workspace/.continuation/full095-ui-final-v1/public-artifacts-manifest-final095.json')
bound = ref('/workspace/.continuation/full095-ui-final-v1/root-bound-input095.json')
guard = ref('/workspace/.continuation/root-source-095-v2.json')
argv = ['/workspace/.compat/run-wine-python.sh','Z:\\workspace\\.continuation\\full095-ui-final-v1\\wine-full-ui-095-final.py']
assert runner['sha256'] == '83c412ce7e456109dc32a6415f7a61526955d48b01d25dbb72198870e6cf18ee'
bridge = next(r['detail'] for r in source['checks'] if r['id'].startswith('F18_'))
receipt = save('formal-source-review-full095-ui-FINAL-v1.json',{
    'format_version':1,'status':'PASS_FORMAL_SOURCE_ONLY_ACTUAL_FINAL_FULL095_UI_FRESH_RUNTIME_UNRUN',
    'source_gate_passed':True,'runtime_pass':False,'runner_sha256':runner['sha256'],'source_keys':source['source_keys'],'execution_argv':argv,
    'execution_cwd':'/workspace/rougezhushou','script_arg_index':1,'source_guard_sha256':guard['sha256'],'guard_sha256':guard['sha256'],'binding_sha256':bound['sha256'],'final_manifest_sha256':mf['sha256'],
    'formal_review_completed':True,
    'review_scope':'Independent SOURCE review of actual FINAL full095 UI instrumentation and root-bound saved evidence. Reviewer did not author this UI harness; own product code and own data builder are immutable binding inputs and not independently reapproved here. No reviewed harness, codec, helper, product API, Qt, Wine or tests was imported or executed.',
    'source_artifacts':{
        'actual_FINAL_runner':runner,'actual_FINAL_manifest':mf,'actual_FINAL_binding':bound,'actual_current_guard735_v2':guard,
        'actual_FINAL_handoff':ref('/workspace/.continuation/full095-ui-final-v1/handoff-final095.json'),
        'approved_root_Wine_wrapper_execution_contract_only':ref(argv[0]),
        'prior_PENDING_v3_formal_source_review':ref('/workspace/.continuation/full095-ui-pending-independent-review-v3/formal-source-review-full095-ui-v3.json'),
        'independent_data_builder_formal_source_review':ref('/workspace/.continuation/p2-full095-ui-binding-data-builder-formal-source-review-v1/formal-source-review-data-builder095-v1.json'),
        'actual_data_build_receipt':ref('/workspace/.continuation/root-full095-ui-binding-data-v1/binding-data-build-receipt095.json'),
        'actual_saved_focused_v4_proof':ref('/workspace/.continuation/root-saved-focused095-review.json')},
    'independent_standard_library_review':{'checks':27,'passed':27,'blocked':0,'actual_input_refs':838,'complete_actual_maintained_sources':735,'original_source_keys_rouge_own_scope':129,
        'results':ref(P/'source-check-result095.json'),'true_primary_exit':ref(P/'source-check095-v2.exit-code'),'log':ref(P/'source-check095-v2.log'),'source_checker':ref(P/'review_source_full_ui095-v2.py'),'diagnostic':diagnostic},
    'whole_SOURCE_inverse':{'FINAL_unique_substitutions':2,'FINAL_to_PENDING_byteexact':True,'PENDING_inverse_operations':79,'original_bytes':729181,'original_sha256':'9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9',
        'original_external_and_committed_full090_byteexact':True,'old_assertions':826,'old_assertions_AST_exact':822,'preapproved_3filename_1visibility_assert_deltas':[2365,2528,2687,3011],
        'protected_helpers':14,'protected_helpers_wholebyte_exact':13,'sole_train_delta':'Original lawful AccountCache fixture id equals mapping key','protected_literals_wholebyte_exact':4,'approved_flatnative_inverse_snapshot_bytes_functions_source_byteexact':9,'codec_functions_executed':0},
    'root_bound_cases':bridge,
    'strict_runtime_comparison_source_contract':{
        'whole_native_damage_wrapper_scenario_result_types_keyorders_aliases':True,'allowed_report_key_only':'selected_module_source_reference','allowed_section_only':'selected_module_source','new_section_unique_last_metrics_empty':True,
        'all_old_report_metrics_notes_and_section_order_exact_after_explicit_inverse':True,'no_module_and_None_whole_native_and_texts_exact':True,
        'each_actual_formatter_three_string_insertion_reconstructed_without_strip_or_whitespace_normalization':True,'technical_tail_exact_prefix':'\n\n【所选模组原件追溯】\n',
        'actual_reference_equals_already_saved_independent_fresh_reference_graph':True,'pinned_original_metadata_phase_owner_and_coverage_qualifiers_from_actual_saved_proof':True,
        'all_project_entry_counts_measured_retained_not_falsely_declared_old_numeric_call_equality':True},
    'original_runtime_assertions_and_receipt_fields':{
        'legacy085_prefix4217_and_full090_additional66':True,'original4283_count_assertion_before_new21_append':True,'actual_total_checks095_computed_after_new_subgroup':True,'original_source_hashes_selector_and_fields_own_rouge_129_preserved':True,
        'full_maintained_source_guard095_before_after_whole735_separate':True,'exact_AccountCache_record_alias_backup_clear_update_restore_and_RunState_boundary_inherited_v3_source_wholeinverse':True,
        'real_raw_tables_and_direct_method_assertions_preserved_by_whole_source_inverse_and826_assert_ledger':True,'actual_API_and_preparedtuple_native_return_originalcaller_before_after_exception_None_records':True,'all_Rouge_mainthread_phase_counts_materialized_in_receipt_and_chunk_index':True},
    'runtime_output_contract':{
        'receipt':'/workspace/.compat/wine-ui-095.json','fresh_native_directory':'/workspace/.compat/full095-ui-native-v3','fresh_directory_absent_admission_before_project_imports':True,'native_index':'/workspace/.compat/full095-ui-native-v3/wine-ui-full-native-index-095.json',
        'dynamic_native_chunks':'full095-ui-native-v3/wine-ui-full-native-095-%06d.json.gz','predicted_actual_chunk_count':None,'actual_recursive_physical_regular_files_receipt_pointer':'/full_native095/files','complete_compat_relative_file_bytes_sha_each':True,
        'full_context_fresh_directory_contract':'All actual regular physical files equal declared native acceptance artifact set; symlink/nonregular rejected by independent full-context gate.',
        'four_required_screenshots':['/workspace/.compat/wine-window-095.png','/workspace/.compat/wine-movement-reference-095.png','/workspace/.compat/wine-sown-tile-control-095.png','/workspace/.compat/wine-medical-trait-095.png'],'only_materialized_stdlib_save_pause_finally_restore_hooks':True},
    'actual_section95_archive_state_distinct_from_SOURCE_packet_field':{
        'receipt':ref('/workspace/rougezhushou/verification/sections/095.json'),'actual_focused_section95_passed_and_workflow_complete':True,'root_actual_checkpoint_completed_sections':95,
        'legacy_SOURCE_binding_actual95_section_completed_value':False,'legacy_SOURCE_false_interpretation':'Required by already reviewed sealer admission-before-full095 contract; does not replace actual archived focused section95 receipt/checkpoint.','full095_runtime_completed':False},
    'blocking_findings':[],
    'execution_counts':{'reviewed_harness_functions':0,'native_codec_functions':0,'existing_helper_product_API_import_test_calls':0,'Qt_Wine_Git_network_calls':0,'tracked_repository_writes':0,'private_state_reads':0,'candidate_payload_mutations':0},
    'completed_section_increment':0,'full095_runtime_pass':False,'STOPWRITE_after_handoff':True
})
files = [ref(q) for q in sorted(P.iterdir())]
manifest = save('public-artifacts-manifest-full095-ui-FINAL-review-v1.json',{'format_version':1,'status':'STOPWRITE_INDEPENDENT_SOURCE_PASS_ACTUAL_FINAL_FULL095_UI_RUNTIME_UNRUN','files':files,'formal_receipt':receipt,'runtime_pass':False,'completed_section_increment':0})
handoff = save('handoff-full095-ui-FINAL-review-v1.json',{
    'format_version':1,'status':'FINAL_SOURCE_GATE_PASS_ROOT_SOLE_WINE_RUNTIME_PENDING','manifest':manifest,'formal_review':receipt,
    'five_top_pointers':{'source_gate_passed':'/source_gate_passed','runtime_pass':'/runtime_pass','runner_sha256':'/runner_sha256','source_keys':'/source_keys','execution_argv':'/execution_argv'},
    'additional_top_pointers':{'guard_sha256':'/guard_sha256','binding_sha256':'/binding_sha256','final_manifest_sha256':'/final_manifest_sha256','execution_cwd':'/execution_cwd','script_arg_index':'/script_arg_index'},
    'five_values':{'source_gate_passed':True,'runtime_pass':False,'runner_sha256':runner['sha256'],'source_keys_count':129,'execution_argv':argv},'source_checks':27,'blocking_findings':0,'reviewed_function_execution':0,'runtime_pass':False,'completed_section_increment':0,'STOPWRITE':True})
for r in files+[manifest,handoff]:assert ref(r['path']) == r
assert {q.name for q in P.iterdir()} == {Path(r['path']).name for r in files+[manifest,handoff]}
print(json.dumps({'formal_review':receipt,'manifest':manifest,'handoff':handoff,'payload_files':len(files),'STOPWRITE':True},ensure_ascii=False))
