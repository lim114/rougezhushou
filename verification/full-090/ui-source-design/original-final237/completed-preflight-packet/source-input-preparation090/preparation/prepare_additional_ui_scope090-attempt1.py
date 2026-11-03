"""Source/saved preparation for the approved new8 UI states; zero project calls."""
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
ROOT87 = '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
AUTHOR88 = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
AUTHOR89 = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}

def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

assert not (HERE / 'additional8-input-plan090.json').exists()
app = subprocess.check_output(['git', 'show', f'{ROOT87}:rouge/app.py'], cwd=REPO)
timing = subprocess.check_output(['git', 'show', f'{ROOT87}:rouge/timing.py'], cwd=REPO)
snapshot = HERE / 'source-production-boundary87'
snapshot.mkdir()
(snapshot / 'app.py').write_bytes(app)
(snapshot / 'timing.py').write_bytes(timing)
draftcondition = AUTHOR88 / 'draft/rouge/condition_inputs.py'
(snapshot / 'author088-condition_inputs.py').write_bytes(draftcondition.read_bytes())
save('producer-and-consumer-preparation090.json', {
    'status': 'SOURCE_ONLY_PRODUCER_AND_REVIEWED_DRAFT_CONSUMER_MAP_PENDING_ACTUAL_ROOT088',
    'actual_existing_producer_commit': ROOT87,
    'actual88_89_90_source_freeze_complete': False,
    'app_producer': describe(snapshot / 'app.py'),
    'timing_input_schema': describe(snapshot / 'timing.py'),
    'author088_helper_is_reviewed_draft_not_actual_root': describe(snapshot / 'author088-condition_inputs.py'),
    'checkbox': {'create_line': 566, 'defaultTrue_line': 567, 'visibility_line': 960,
        'serialization_line': 1028, 'native_value': 'QCheckBox.isChecked bool',
        'shared_global_state_requires_explicit_reset_each_owner_skill': True},
    'timing_editor': {'widget': 'QPlainTextEdit', 'creation_line': 607, 'visible_form_row_line': 612,
        'text_to_JSON_object_lines': [1139, 1143],
        'empty_target_ui_text': '{"target_windows": []}',
        'empty_target_supported_source': 'timing.py ranges/target selection; amiya_continuous_reference.source_state treats [] as empty',
        'actual_UI_editor_empty_target_executed': False},
    'consumer': {'private_ContextVar': 'None/False/True local state, finally reset(token) in isolated core',
        'bool_inputs_pass_through': True, 'active_text_lazy_only': True,
        'zero_public_condition_marker_added': True,
        'new8_scope': 'Real checkbox bool and exact existing native unknown/reference fields, not active-string guard or exception reset coverage',
        'string_guard_and_prior_error_cleanup_tests_reused_from_formal088_not_reexecuted': True},
    'actual_root_source_transport_before_new8_required': True,
    'project_API_helpers_formatter_Qt_Wine_tests_calls': 0})

common = {'potential': 1, 'trust': 100, 'module_id': None, 'module_level': 0,
    'window_seconds': 12.75, 'healing_targets': 1, 'deployment_elapsed_seconds': 0.0,
    'enemy_defense': 0.0, 'enemy_resistance': 0.0, 'relic_ids': []}
groups = [
    {'id': '088-native-checkbox-mechanist-S1', 'operator': 'mechanist', 'skill': 1,
        'elite': 2, 'level': 60, 'skill_rank': 10, 'timing_mode': 'frames',
        'control_display': 'visible Attack-SP',
        'contract_source': 'Existing legacy initial/recharge/cycle and normal gate; native bool preserved, exact keys from final source'},
    {'id': '088-hidden-checkbox-amiya-E2-S1-bounded-reference', 'operator': 'char_002_amiya', 'skill': 1,
        'elite': 2, 'level': 80, 'skill_rank': 10, 'timing_mode': 'continuous',
        'timing': {'target_disappears_seconds': 5.75},
        'control_display': 'hidden natural-SP checkbox still globally serialized',
        'contract_source': 'Actual caster reference flag and qualified talent parameter; actual acquisition/impact/recharge/cycle remain unknown'},
    {'id': '088-hidden-checkbox-chen3-S3-active-warrior67', 'operator': 'char_1050_chen3', 'skill': 3,
        'elite': 2, 'level': 90, 'skill_rank': 10, 'timing_mode': 'continuous',
        'relic_ids': ['rogue_6_relic_legacy_67'],
        'control_display': 'hidden natural-SP checkbox and actual applicable manual relic list item',
        'contract_source': 'Prepare-resolved active warrior attack-SP affects first charge; do not require masked final totals/cycle to differ'},
    {'id': '088-hidden-checkbox-amiya-E0-S1-empty-target-reference', 'operator': 'char_002_amiya', 'skill': 1,
        'elite': 0, 'level': 50, 'skill_rank': 7, 'timing_mode': 'continuous',
        'timing': {'target_windows': []},
        'control_display': 'hidden natural-SP checkbox; actual QPlainTextEdit object JSON target_windows=[]',
        'contract_source': 'E0 no emotion-absorption attack credit; true/false changes existing reference enabled flag, not actual native clock or damage supply'}]
cases = []
for group in groups:
    fields = {key: value for key, value in group.items() if key not in ('id', 'control_display', 'contract_source')}
    for checked in (False, True):
        request = {**common, **fields, 'continuous_attacks': checked}
        cases.append({'pair_id': group['id'], 'widget_checked': checked,
            'control_display_source': group['control_display'], 'input': request,
            'required_source_contract': group['contract_source'],
            'base_attack': 'omitted; actual read-only cultivation auto-calculated',
            'UI_actual_execution': False})
assert len(cases) == len({json.dumps(row['input'], sort_keys=True) for row in cases}) == 8
old44 = json.loads(Path('/workspace/.continuation/ui-090-draft/cases090-section086.json').read_bytes())
oldrows = old44['cases'] if isinstance(old44, dict) else old44
old44args = {json.dumps(row['input'], sort_keys=True) for row in oldrows}
assert not any(json.dumps(row['input'], sort_keys=True) in old44args for row in cases)
save('additional8-input-plan090.json', {
    'format_version': 1, 'status': 'FROZEN_APPROVED_UNIQUE8_INPUTS_PENDING_ACTUAL_ROOT088_TRANSPORT',
    'pair_groups': 4, 'UI_state_design_records': 8, 'unique_requested_inputs': 8,
    'public_API_calls_maximum': 8, 'explicit_three_text_requests_maximum': 24,
    'planned_formatter_entries_if_unchanged_estimate_delegate': {'format_estimate': 8, 'default': 16, 'technical': 8, 'total': 32},
    'formatter_entries_measured_so_far': 0,
    'requested_API_calls_so_far': 0, 'Qt_Wine_calls_so_far': 0,
    'conditions_are_native_bool_not_string_API_regressions': True,
    'all_states_fixed_window_seconds': 12.75, 'manual_base_attack_not_produced': True,
    'pairs': groups, 'cases': cases,
    'earliest_call_requirement': 'Actual root088 tagged source transported and named public package byte-exact; never execute against619 draft',
    'final_entire_root90_source_freeze_requirement': 'Actual root088/089/090 all committed; final maintained/public hashes frozen after all three, prior8 records reused only under source-domain zero-drift proof',
    'new_API_necessity': 'Tie the distinct genuine readonly Qt inputs and bool hidden/reference/qualified source boundaries to actual root088 once; not repeat existing author/manual-base16/60 or old UI44/1154/4217.',
    'Amiya_empty_target_is_real_editor_JSON_source_closed_not_yet_actual_Qt_pass': True,
    'old44_argument_identity_not_reused': True,
    'saved_only_consumer_and_result_keys_closed_before_calls': True,
    'actual_private_context_error_cleanup_or_text_rejection_not_claimed_by_these_bool8': True})

authorrecords_path = AUTHOR89 / 'new-tests-native-records089.json.gz'
raw = authorrecords_path.read_bytes()
records = json.loads(gzip.decompress(raw))['records']
by_sequence = {row['sequence']: row for row in records}
selected = []
for sequence, name in ((19, 'None unread retained'), (9, 'False unread retained'),
        (3, 'True unread preserves other member'), (22, 'integer0 complete empty'),
        (6, 'integer1 complete singleton')):
    row = by_sequence[sequence]
    assert row['method'] == 'apply' and row['role'] == 'subject_apply'
    assert row['caller_whole_typed_unchanged'] is True
    state = row['state_after']
    selected.append({'saved_sequence': sequence, 'label': name,
        'observed': row['observed_before'], 'observed_native': row['observed_before_typed'],
        'state': state, 'state_native': row['state_after_typed'],
        'record_original_json_sha256': sha(json.dumps(row, ensure_ascii=False, separators=(',', ':')).encode()),
        'crew_observed_type': type(row['observed_before'].get('crew_count')).__name__,
        'crew_stored_type': type(state['crew_count']).__name__, 'crew_stored_value': state['crew_count'],
        'members': {owner: {'present': member['present'], 'fields': member['fields'],
            'skill_ranks': member['skill_ranks'], 'sources': member['sources'], 'scope': member['scope']}
            for owner, member in state['operators'].items()},
        'producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR': True})
save('saved89-five-state-UI-consumer-design090.json', {
    'status': 'SAVED38_NATIVE_PROJECTION_FOR_FUTURE_REAL_WINDOW_CONSUMERS_PENDING_ACTUAL_ROOT089',
    'original_saved38': describe(authorrecords_path), 'original_records': len(records),
    'selected_saved_records': selected, 'UI_consumer_state_count': 5,
    'prep_RunState_constructor_calls': 0, 'prep_RunState_apply_calls': 0,
    'prep_application_API_or_Qt_Wine_calls': 0,
    'future_window_method': 'Replay exact saved public mapping into the already isolated window.run temporary state, then actual recruited_operator_ids/current_operator_state/training labels; never call this replay apply pipeline or native observation.',
    'future_init_load_constructors_counted_if_run': True,
    'actual_member_flag_name': 'present', 'no_invented_operator_present_result_key': True,
    'training_producer_app_lines': [742, 778],
    'all_selected_stored_source_maps_are_empty_original_values_not_fake_receipts': True,
    'observed_count_bool_vs_stored_count_int_native_types_preserved': True,
    'no_real_private_or_local_state_read_or_written': True,
    'native_departure_or_OCR_skill_buff_rules_not_inferred': True,
    'damage_API_new_requests_for89': 0,
    'AccountFallback': 'When use_run_training and member present=False, actual app current_operator_state ignores that member and returns the explicit isolated account/preview observation; no cultivation number inferred from crew count alone.'})
save('preparation-discovery-diagnostics090.json', {
    'status': 'RESOLVED_READ_ONLY_CONSUMER_FILENAME_DISCOVERY',
    'mistaken_source_paths': ['rouge/continuous_attack_condition.py', 'draft/rouge/continuous_attacks_condition.py'],
    'actual_discovered_file': str(draftcondition), 'resolution': 'rg --files then read actual condition_inputs.py',
    'project_calls_in_discovery': 0, 'no_product_call_or_test_failure': True,
    'raw_guessed_path_output_not_recreated': True,
    'same_issue_three_failed_attempts_rule_triggered': False})
print(json.dumps({'status': 'APPROVED_NEW8_AND_SAVED89_SOURCE_PLAN_FROZEN_NO_CALLS',
    'new8_plan': describe(HERE / 'additional8-input-plan090.json'),
    'saved89_design': describe(HERE / 'saved89-five-state-UI-consumer-design090.json')}, ensure_ascii=False))
