"""SOURCE-bound UI cache retry within the actual original full095 recovery epoch.

The original b7a6 binding validator and ad1b capability binder remain whole-byte
copies. The capability binder validates the original epoch before this UI-only
projection. Nothing here imports a project, codec, adapter, test or UI runner.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from binding_validation095 import (EXECUTION_NAMES, bound_bytes, bound_json,
                                   canonical_file, exact_source_review, file_ref,
                                   require, wine_argument_for)
from capability_binding095 import (REPLACED_OUTPUTS as CAPABILITY_OUTPUTS,
                                   check_observation, references_in, validate_capability_receipt,
                                   validate_recovery_inputs as validate_capability_inputs)


PRIOR_BINDING = {
    'path': '/workspace/.continuation/full095-regression-capability-resume-final-v1/actual-full095-source-binding.json',
    'bytes': 383874,
    'sha256': 'af943d5f3b0c5996c83fb5d1ee82f793c96a7937e7ed493604fa126a4bbf73f3',
}
PRIOR_RUNNER = {
    'path': '/workspace/.continuation/full095-regression-capability-resume-final-v1/full095_context_recovery.py',
    'bytes': 32395,
    'sha256': '9e341441992d616bea7d91f22f4b14745d58799bde9f2e738f5b2d9434315403',
}
PRIOR_CONTEXT = {
    'path': '/workspace/.compat/wine-validation-095-context-recovery-v1.json',
    'bytes': 126014,
    'sha256': '46f5906ee1f54f65478503948888f6911072b45b673efa923f3a1af246a9b43a',
}
INCOMPLETE_UI = {
    'path': '/workspace/.continuation/ROOT_CURRENT_WORK_095_UI_SESSION_LOST_PRIMARY_UNAVAILABLE.json',
    'bytes': 5556,
    'sha256': 'ec0dead7b1ca4d6551828af6d8105ec6ef9f917445624f15281b82faf1b5dcc5',
}
UI_OUTPUTS = {
    'wine_ui': '/workspace/.compat/wine-ui-095-cache-retry-v1.json',
    'wine_ui_console': '/workspace/.continuation/root-full095-ui-cache-retry-v1-console.log',
    'wine_ui_exit_code': '/workspace/.continuation/root-full095-wine_ui-cache-retry-v1.exit-code',
    'ui_saved_output_0': '/workspace/.compat/wine-ui-new-states-095-cache-retry-v1.json.gz',
    'ui_saved_output_1': '/workspace/.compat/full095-ui-native-cache-retry-v1/wine-ui-full-native-index-095.json',
    'ui_saved_output_2': '/workspace/.compat/wine-window-095-cache-retry-v1.png',
    'ui_saved_output_3': '/workspace/.compat/wine-movement-reference-095-cache-retry-v1.png',
    'ui_saved_output_4': '/workspace/.compat/wine-sown-tile-control-095-cache-retry-v1.png',
    'ui_saved_output_5': '/workspace/.compat/wine-medical-trait-095-cache-retry-v1.png',
    'ui_optional_output_0': '/workspace/.compat/wine-ui-failure-095-cache-retry-v1.png',
    'ui_optional_output_1': '/workspace/.compat/wine-ui-subgroup-failure-095-cache-retry-v1.png',
    'ui_optional_output_2': '/workspace/.compat/wine-ui-report-difference-095-cache-retry-v1.json',
}
CONTROL_OUTPUTS = {
    'context_start': '/workspace/.compat/wine-validation-095-context-ui-cache-retry-v1.json',
    'context_final': '/workspace/.compat/wine-validation-095-context-ui-cache-retry-v1-final.json',
    'execution_witness': '/workspace/.continuation/root-full095-ui-cache-retry-v1-primary-exits.json',
    'saved_review_input': '/workspace/.continuation/root-full095-ui-cache-retry-v1-saved-input-spec.json',
    'saved_review_receipt': '/workspace/.continuation/root-full095-ui-cache-retry-v1-saved-review.json',
    'saved_review_stdout': '/workspace/.continuation/root-full095-ui-cache-retry-v1-saved-console.log',
    'saved_review_exit_code': '/workspace/.continuation/root-full095-ui-cache-retry-v1-saved_review.exit-code',
    'visual_review': '/workspace/.continuation/root-full095-ui-cache-retry-v1-visual-review.json',
    'ui_extra_acceptance': '/workspace/.continuation/root-full095-ui-cache-retry-v1-ui-extra-acceptance.json',
}
NEW_OUTPUTS = {**UI_OUTPUTS, **CONTROL_OUTPUTS}
SELECTED_RETRY_OUTPUTS = {
    'wine_selected': '/workspace/.compat/wine-cloud-095-capability-retry-v2.log',
    'wine_selected_exit_code': '/workspace/.continuation/root-full095-wine_selected-capability-retry-v2.exit-code',
}
REPLACED_OUTPUTS = {**CAPABILITY_OUTPUTS, **NEW_OUTPUTS, **SELECTED_RETRY_OUTPUTS}
SELECTED_FAILURE = {
    'observation': {
        'path': '/workspace/.continuation/root-full095-wine_selected-capability-v1-failed-observation.json',
        'bytes': 2151,
        'sha256': 'e2775c58999de669d2409742317cf06d47cd17e541d01225ca3c88fb18eb17c0',
    },
    'actual_launch': {
        'path': '/workspace/.continuation/root-full095-wine_selected-capability-v1-actual-launch.json',
        'bytes': 923,
        'sha256': 'd1e4aeac62c8864d0072bb2398ce514be86c05b8181c609b4f8eac8e830c052c',
    },
    'actual_completion': {
        'path': '/workspace/.continuation/root-full095-wine_selected-capability-v1-actual-completion.json',
        'bytes': 1194,
        'sha256': '688f80f17435e9797ee91fcca5acd72117aba411138996ebd3979f4385bec93e',
    },
}
NATIVE_DIRECTORIES = ['/workspace/.compat/full095-ui-native-cache-retry-v1']
UI_RUNNER_PATH = '/workspace/.continuation/full095-ui-cache-retry-source-v1/wine-full-ui-095-cache-retry.py'
UI_CONTRACT_PATH = '/workspace/.continuation/full095-ui-cache-retry-source-v1/source-contract-cache-retry095.json'
SAVED_RUNNER_PATH = '/workspace/.continuation/full095-saved-validator-ui-cache-pending-v4/saved.py'
PRELAUNCH_PATH = '/workspace/.continuation/root-full095-ui-cache-retry-v1-prelaunch.json'


def check_prior_recovery(spec, prior, original_context, actual):
    row = spec['prior_recovery']
    require(set(row) == {'binding', 'runner', 'context', 'resume_console', 'resume_exit_code'}
            and row['binding'] == PRIOR_BINDING and row['runner'] == PRIOR_RUNNER
            and row['context'] == PRIOR_CONTEXT,
            'UI retry must preserve the actual bounded prior recovery binding/runner/context')
    context = bound_json(row['context'])
    bound_bytes(row['runner'])
    require(row['resume_console']['path'] == '/workspace/.continuation/root-resume-full095-recovery.log'
            and row['resume_exit_code']['path'] == '/workspace/.continuation/root-resume-full095-recovery.exit-code'
            and bound_bytes(row['resume_exit_code']) in (b'0\n', b'0\r\n'),
            'Preserve the actual primary-zero prior recovery resume proof')
    import json
    console = json.loads(bound_bytes(row['resume_console']))
    require(console['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and console['section'] == 95 and console['source_files'] == actual['source_files']
            and console['actual_base_HEAD'] == actual['actual_base_HEAD']
            and console['actual_original_epoch_recovery'] is True
            and console['original_start_replayed'] is False,
            'Prior recovery resume console is not its actual start result')
    require(context['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and context['available_checks_passed'] is False
            and context['section'] == 95 and context['actual_original_epoch_recovery'] is True
            and context['binding'] == row['binding'] and context['final_context_runner'] == row['runner']
            and context['started_at'] == original_context['started_at']
            and context['recovery_started_at'] == '2026-10-08T23:36:41.779450+00:00'
            and context['source_sha256'] == actual['source_sha256']
            and context['preserved_passed_executions'] == prior['recovery_spec']['preserved_passed_executions']
            and context['prior_failed_execution'] == prior['recovery_spec']['prior_failed_execution']
            and context['planned_fresh_sinks'] == prior['recovery_spec']['replacement_output_paths']
            and context['planned_current_epoch_sinks'] == actual['global_output_plan']['paths'],
            'Prior actual recovery/source/earlier outcomes or Wine contracts were substituted')
    require(datetime.fromisoformat(context['started_at'])
            <= datetime.fromisoformat(context['recovery_started_at']) <= datetime.now(timezone.utc),
            'Prior actual recovery boundary is outside the original epoch')
    return context


def check_incomplete_ui(spec, prior, actual):
    require(spec['prior_incomplete_ui'] == INCOMPLETE_UI,
            'Preserve the actual incomplete UI capsule; an inferred failure/zero cannot replace it')
    capsule = bound_json(spec['prior_incomplete_ui'])
    require(capsule['section'] == 95
            and capsule['status'] == 'INCOMPLETE_UI_EXECUTION_SESSION_LOST_PRIMARY_UNAVAILABLE'
            and capsule['actual_original_UI_session_id'] == 61366
            and capsule['primary_exit_code'] is None and capsule['primary_exit_code_captured'] is False
            and capsule['actual_root_requested_process_termination'] is False
            and capsule['raw_primary_status_absent'] is True and capsule['final_UI_receipt_absent'] is True
            and capsule['native_outcome'] == 'pending'
            and capsule['closed_native_chunks'] == 275
            and capsule['full_validation_passed'] is False
            and capsule['source_files_unchanged'] == actual['source_files'] and capsule['source_drift'] == [],
            'The lost UI session remains incomplete with its actual unknown primary outcome')
    expected = {name: value['observation'] for name, value in prior['recovery_spec']['preserved_passed_executions'].items()}
    require(capsule['four_completed_primary_observations_preserved'] == expected,
            'Incomplete UI capsule must preserve the same four actual primary-zero proofs')
    refs = references_in(capsule)
    for reference in refs:
        bound_bytes(reference)
    index = bound_json(capsule['native_index'])
    require(index['outcome'] == 'pending' and len(index['chunks']) == capsule['closed_native_chunks']
            and index['records_completed'] == capsule['closed_targeted_records'],
            'Original incomplete native index changed outcome or its actual closed counts')
    chunk_refs = []
    for row in index['chunks']:
        path = Path('/workspace/.compat') / row['file']
        require(path.parent == Path('/workspace/.compat/full095-ui-native-v3'),
                'Original incomplete native chunk path escaped its actual namespace')
        reference = {'path': str(path), 'bytes': row['bytes'], 'sha256': row['sha256']}
        bound_bytes(reference)
        chunk_refs.append(reference)
    return refs + chunk_refs


def ui_retry_projection(spec, prior, actual):
    retry = spec['ui_retry']
    require(set(retry) == {'manifest', 'source_contract', 'runner', 'source_review',
                          'review_pointers', 'ui', 'saved_review_source', 'planned_root_prelaunch_path', 'planned_saved_input_path'},
            'Exact SOURCE-bound UI/saved retry inputs are required')
    require(retry['runner']['path'] == UI_RUNNER_PATH
            and retry['source_contract']['path'] == UI_CONTRACT_PATH
            and retry['planned_root_prelaunch_path'] == PRELAUNCH_PATH
            and retry['planned_saved_input_path'] == CONTROL_OUTPUTS['saved_review_input'],
            'Retry source/control paths differ from their reserved SOURCE contract')
    contract = bound_json(retry['source_contract'])
    manifest = bound_json(retry['manifest'])
    package = Path(UI_CONTRACT_PATH).parent
    require(retry['manifest']['path'] == str(package / 'public-artifacts-manifest-cache-retry095.json')
            and manifest['status'] == 'STOPWRITE_CACHE_RETRY_SOURCE_ONLY_RUNTIME_UNRUN'
            and manifest['STOPWRITE'] is True and manifest['runtime_calls'] == 0,
            'Exact frozen producer SOURCE manifest required')
    declared = []
    for name, metadata in manifest['artifacts'].items():
        require(Path(name).name == name and set(metadata) == {'bytes', 'sha256'},
                'Producer SOURCE artifacts must be direct filename/bytes/SHA entries')
        declared.append({'path': str(package / name), **metadata})
    require(retry['runner'] in declared and retry['source_contract'] in declared,
            'Producer manifest must bind the exact UI runner and source contract')
    for reference in declared:
        bound_bytes(reference)
    require(contract['runner'] == retry['runner']
            and contract['replacement_output_paths'] == UI_OUTPUTS
            and contract['fresh_evidence_directories'] == NATIVE_DIRECTORIES,
            'Only the exact producer-reviewed UI recording cache and fresh output literals may change')
    ui = deepcopy(prior['root_spec']['ui'])
    ui.update(runner=retry['runner'], receipt_path=UI_OUTPUTS['wine_ui'],
              console_log_path=UI_OUTPUTS['wine_ui_console'],
              required_saved_outputs=[{'kind': 'native-evidence' if i < 2 else 'screenshot',
                                       'path': UI_OUTPUTS[f'ui_saved_output_{i}']} for i in range(6)],
              optional_output_paths=[UI_OUTPUTS[f'ui_optional_output_{i}'] for i in range(3)],
              fresh_evidence_directories=NATIVE_DIRECTORIES)
    argv = [prior['root_spec']['wine_wrapper']['path'], wine_argument_for(retry['runner']['path'], actual['wine_path_mapping'])]
    ui['execution_contract'].update(argv=argv, source_review=retry['source_review'],
                                    review_pointers={key: retry['review_pointers'][key] for key in
                                                     ('source_pass', 'runtime_pass', 'runner_sha256', 'argv')})
    ui['own_source_scope'].update(source_review=retry['source_review'],
                                  review_pointers={key: retry['review_pointers'][key] for key in
                                                   ('source_pass', 'runtime_pass', 'runner_sha256', 'source_keys')})
    require(retry['ui'] == ui and contract['execution_argv'] == argv
            and contract['source_keys'] == actual['UI_expected_own_source_keys']
            and contract['required_saved_outputs'] == ui['required_saved_outputs']
            and contract['optional_output_paths'] == ui['optional_output_paths'],
            'UI projection changed a source selector, schema pointer, exact CLI or declared output kind/path')
    exact_source_review(retry['source_review'], retry['review_pointers'], retry['runner'],
                        argv=argv, keys=actual['UI_expected_own_source_keys'])
    saved = deepcopy(prior['root_spec']['saved_review'])
    row = retry['saved_review_source']
    require(set(row) == {'runner', 'source_review', 'review_pointers', 'argv'}
            and row['runner']['path'] == SAVED_RUNNER_PATH,
            'Saved source must be the reviewed minimal v4 inverse/path extension')
    bound_bytes(row['runner'])
    saved_argv = [prior['root_spec']['linux_python_entry'], SAVED_RUNNER_PATH,
                  '--spec', CONTROL_OUTPUTS['saved_review_input'], '--output', CONTROL_OUTPUTS['saved_review_receipt']]
    require(row['argv'] == saved_argv, 'Saved v4 exact new control/receipt CLI differs')
    exact_source_review(row['source_review'], row['review_pointers'], row['runner'], argv=saved_argv)
    saved.update(runner=row['runner'], receipt_path=CONTROL_OUTPUTS['saved_review_receipt'],
                 stdout_log_path=CONTROL_OUTPUTS['saved_review_stdout'])
    saved['execution_contract'].update(argv=saved_argv, source_review=row['source_review'],
                                       review_pointers=row['review_pointers'])
    return ui, saved, declared


def check_recovery_passes(spec, prior, context):
    import json
    passed = spec['preserved_recovery_passed_executions']
    require(set(passed) == {'wine_full', 'wine_selected'},
            'Preserve both actual completed unchanged Wine adapter proofs without replay')
    entries = {}
    for name, row in passed.items():
        require(set(row) == {'observation', 'receipt'}, 'Preserved Wine pass must explicitly declare receipt or null')
        observed_contract = prior
        if name == 'wine_selected':
            observed_contract = deepcopy(prior)
            observed_contract['actual_inputs']['global_output_plan']['paths'].update(SELECTED_RETRY_OUTPUTS)
            observed_contract['actual_inputs']['execution_contracts'][name]['exit_code_path'] = SELECTED_RETRY_OUTPUTS['wine_selected_exit_code']
        entry = check_observation(row['observation'], name, observed_contract, context, 0)
        require(datetime.fromisoformat(entry['started_at']) >= datetime.fromisoformat(context['recovery_started_at']),
                name + ' actual pass must belong to the earlier real recovery boundary')
        if name == 'wine_selected':
            failed = bound_json(spec['prior_selected_failed_execution']['observation'])
            require(datetime.fromisoformat(entry['started_at']) >= datetime.fromisoformat(failed['completed_at']),
                    'Selected2 actual pass must be fresh after preserved selected1 failure')
        if name == 'wine_full':
            require(row['receipt'] == file_ref(prior['actual_inputs']['global_output_plan']['paths'][name]),
                    'Preserved Wine full receipt differs from the unchanged adapter output')
            receipt = bound_json(row['receipt'])
            require(receipt['available_checks_passed'] is True and receipt['failures'] == receipt['errors'] == 0
                    and receipt['source_drift'] == []
                    and receipt['source_sha256'] == prior['actual_inputs']['classifier_source_sha256']
                    and receipt['selectors'] == prior['actual_inputs']['full_selectors'],
                    'Preserved Wine full available pass/source/selectors differ')
        else:
            require(row['receipt'] is None, 'Preserved Wine selected receipt is the actual console JSON')
            summaries = []
            for line in bound_bytes(entry['stdout_log']).decode('utf-8', errors='replace').splitlines():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict) and 'tests_run' in value:
                    summaries.append(value)
            require(summaries and summaries[-1]['passed'] is True
                    and summaries[-1]['failures'] == summaries[-1]['errors'] == 0,
                    'Preserved Wine selected actual console did not pass')
            receipt = summaries[-1]
        validate_capability_receipt(receipt, prior, name)
        entries[name] = entry
    return entries


def check_selected_failure(spec, prior, context):
    import json
    require(spec['prior_selected_failed_execution'] == SELECTED_FAILURE,
            'Preserve the exact actual selected1 primary-one observation/launch/completion')
    failed = SELECTED_FAILURE
    entry = check_observation(failed['observation'], 'wine_selected', prior, context, 1)
    launch = bound_json(failed['actual_launch'])
    completion = bound_json(failed['actual_completion'])
    require(entry['actual_tool_observation'] == {'session_id': 77283, 'completion_tool_chunk': '18a892'}
            and entry['actual_completion'] == failed['actual_completion']
            and completion['primary_exit_code'] == 1 and completion['last_tool_result']['exit_code'] == 1
            and completion['completion_tool_chunk'] == '18a892'
            and completion['started_at'] == launch['started_at'] == entry['started_at']
            and completion['completed_at'] == entry['completed_at']
            and launch['launch_result']['session_id'] == 77283
            and all(completion[key] == launch[key] == entry[key]
                    for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')),
            'Selected1 must retain its actual failed tool/process observation without zero credit')
    summary = None
    for line in reversed(bound_bytes(entry['stdout_log']).decode('utf-8', errors='replace').splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and 'tests_run' in value:
            summary = value
            break
    require(isinstance(summary, dict), 'Preserved selected1 actual receipt JSON is missing')
    require(summary['passed'] is False and summary['failures'] == 0 and summary['errors'] == 1
            and entry['issue']['error'] == 'subprocess.TimeoutExpired'
            and entry['issue']['timeout_seconds'] == 20
            and entry['issue']['test_body_success_claimed'] is False,
            'Preserved selected1 actual error may not be rewritten or counted passed')
    return entry


def project_outputs(base_plan, spec, immutable, preserved):
    plan = deepcopy(base_plan)
    plan['paths'].update(NEW_OUTPUTS)
    plan['paths'].update(SELECTED_RETRY_OUTPUTS)
    plan['canonical_paths'] = {key: canonical_file(value) for key, value in plan['paths'].items()}
    plan['immutable_input_paths'] = sorted(set(plan['immutable_input_paths']) | {canonical_file(value) for value in immutable})
    plan['fresh_evidence_directories'] = NATIVE_DIRECTORIES
    canonical = plan['canonical_paths']
    inputs = plan['immutable_input_paths']
    require(len(set(canonical.values())) == len(canonical)
            and all(not Path(other).is_relative_to(Path(path))
                    for name, path in canonical.items() for other_name, other in canonical.items() if name != other_name),
            'UI retry output files must be canonically disjoint and cannot contain one another')
    preserved_paths = {canonical_file(value) for value in preserved}
    require(set(inputs).intersection(canonical.values()) == preserved_paths
            and all(not Path(other).is_relative_to(Path(path))
                    for path in canonical.values() for other in inputs if other != path),
            'New UI/control outputs overlap immutable input beyond the six unchanged actual passed sinks')
    for directory in NATIVE_DIRECTORIES:
        require(not any(Path(value).is_relative_to(Path(directory)) or Path(directory).is_relative_to(Path(value))
                        for value in inputs), 'New UI native namespace overlaps an immutable input')
        for name, output in canonical.items():
            require(not Path(directory).is_relative_to(Path(output)), 'Retry output contains native namespace')
            if not name.startswith(('ui_saved_output_', 'ui_optional_output_')):
                require(not Path(output).is_relative_to(Path(directory)), 'Nonnative retry output lies inside native namespace')
    return plan


def validate_recovery_inputs(spec, extra_immutable_paths=()):
    require(spec.get('format_version') == 3 and spec.get('section') == 95
            and spec.get('status') == 'ROOT_BOUND_ACTUAL_FULL095_UI_RETRY_SOURCE_INPUTS',
            'Actual ROOT-bound UI retry spec required; pending/future references cannot seal')
    require(spec['prior_recovery']['binding'] == PRIOR_BINDING, 'UI retry prior recovery binding differs')
    prior = bound_json(PRIOR_BINDING)
    base_spec = prior['recovery_spec']
    for key in ('original', 'preserved_passed_executions', 'prior_failed_execution', 'adapters'):
        require(spec[key] == base_spec[key], 'UI retry changed an original recovery field: ' + key)
    require(spec['ui_retry_output_paths'] == NEW_OUTPUTS
            and spec['selected_retry_output_paths'] == SELECTED_RETRY_OUTPUTS
            and spec['replacement_output_paths'] == REPLACED_OUTPUTS,
            'Retry may change only exact reviewed UI/saved/control sinks; Wine adapters retain their original retry sinks')
    for reference in prior['final_support_files']:
        bound_bytes(reference)
    require(bound_json(prior['recovery_spec_reference']) == base_spec, 'Prior physical root recovery spec changed')
    prior_immutable = prior['source_package_input_paths'] + [prior['recovery_spec_reference']['path']]
    prior_immutable.extend([PRIOR_BINDING['path'], PRIOR_RUNNER['path']])
    prior_immutable.extend(reference['path'] for reference in prior['final_support_files'])
    # The unchanged capability binder calls the unchanged b7a6 validator before any projection.
    original, original_context, actual = validate_capability_inputs(base_spec, prior_immutable)
    require(original['root_spec'] == prior['root_spec'] and actual == prior['actual_inputs'],
            'Original actual inputs or reviewed two-Wine recovery projection changed')
    recovery_context = check_prior_recovery(spec, prior, original_context, actual)
    selected_failure = check_selected_failure(spec, prior, recovery_context)
    recovery_passes = check_recovery_passes(spec, prior, recovery_context)
    incomplete_refs = check_incomplete_ui(spec, prior, actual)
    ui, saved, ui_refs = ui_retry_projection(spec, prior, actual)
    projected_root = deepcopy(original)
    projected_root['root_spec']['ui'] = ui
    projected_root['root_spec']['saved_review'] = saved
    projected_root['root_spec']['io_plan']['exit_code_paths'].update(wine_ui=UI_OUTPUTS['wine_ui_exit_code'],
                                                                    saved_review=CONTROL_OUTPUTS['saved_review_exit_code'],
                                                                    wine_selected=SELECTED_RETRY_OUTPUTS['wine_selected_exit_code'])
    projected_root['root_spec']['io_plan'].update(visual_review_path=CONTROL_OUTPUTS['visual_review'],
                                                ui_extra_acceptance_path=CONTROL_OUTPUTS['ui_extra_acceptance'])
    projected = deepcopy(actual)
    projected['UI_source_binding'] = ui
    projected['ui_retry'] = spec['ui_retry']
    projected['execution_contracts']['wine_ui'].update(runner=ui['runner'], argv=ui['execution_contract']['argv'],
                                                       exit_code_path=UI_OUTPUTS['wine_ui_exit_code'])
    projected['execution_contracts']['saved_review'].update(runner=saved['runner'], argv=saved['execution_contract']['argv'],
                                                            exit_code_path=CONTROL_OUTPUTS['saved_review_exit_code'])
    projected['execution_contracts']['wine_selected']['exit_code_path'] = SELECTED_RETRY_OUTPUTS['wine_selected_exit_code']
    refs = references_in(spec) + incomplete_refs + ui_refs
    for reference in refs:
        bound_bytes(reference)
    immutable = [reference['path'] for reference in refs] + list(extra_immutable_paths)
    immutable.extend(reference['path'] for reference in references_in(selected_failure))
    preserved = []
    for row in base_spec['preserved_passed_executions'].values():
        entry = bound_json(row['observation'])
        immutable.extend(reference['path'] for reference in references_in(entry))
        preserved.extend((entry['stdout_log']['path'], entry['exit_code_file']['path']))
        if row['receipt'] is not None:
            preserved.append(row['receipt']['path'])
    for name, entry in recovery_passes.items():
        immutable.extend(reference['path'] for reference in references_in(entry))
        preserved.extend((entry['stdout_log']['path'], entry['exit_code_file']['path']))
        receipt = spec['preserved_recovery_passed_executions'][name]['receipt']
        if receipt is not None:
            preserved.append(receipt['path'])
    projected['global_output_plan'] = project_outputs(actual['global_output_plan'], spec, immutable, preserved)
    return projected_root, original_context, projected
