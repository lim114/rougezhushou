"""Bound recovery of the actual full095 epoch; standard library and read-only Git only.

The original binding validator and its OUTPUT_NAMES stay byte-for-byte intact.
Never import a project, adapter, test, original context, or codec to validate files.
"""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
import ast
import json

from binding_validation095 import (EXECUTION_NAMES, bound_bytes, bound_json,
                                   canonical_file, exact_source_review, file_ref,
                                   require, validate_actual_inputs,
                                   wine_argument_for)

ORIGINAL_BINDING = {
    'path': '/workspace/.continuation/full095-regression-final-v1/actual-full095-source-binding.json',
    'bytes': 416844,
    'sha256': '8b11354e50fe7a3cd291df2a86c765b65285434c44ba8bd119ab01aa29e09245',
}
ORIGINAL_CONTEXT_RUNNER = {
    'path': '/workspace/.continuation/full095-regression-final-v1/full095_context_final.py',
    'bytes': 26404,
    'sha256': 'cc28fb21c3f62d4377ae9c79af4014dff6d6d38dfcd080db18b4dbe40af96afc',
}
REPLACED_EXECUTIONS = ('wine_full', 'wine_selected')
REPLACED_OUTPUTS = {
    'context_start': '/workspace/.compat/wine-validation-095-context-recovery-v1.json',
    'wine_full': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095.json',
    'wine_full_log': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095.log',
    'wine_full_console': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095-console.log',
    'wine_full_exit_code': '/workspace/.continuation/root-full095-wine_full-capability-retry-v1.exit-code',
}
EXPECTED_ADAPTER_PATHS = {
    'wine_full': '/workspace/.continuation/full095-wine-capability-retry-pending-v1/wine_full095_capability_retry.py',
    'wine_selected': '/workspace/.continuation/full095-wine-capability-retry-pending-v1/wine_selected095_capability.py',
}
FAILED_TEST_NAMES = {
    'tests.test_account_cache_093.AccountCache093Tests.test_dangling_symlink_file_not_found_is_not_genuinely_absent',
    'tests.test_account_cache_093.AccountCache093Tests.test_symlink_to_damaged_file_retains_link_and_target_bytes',
}


def references_in(value):
    """Only actual full references, never path reservations or future nulls."""
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= set(value):
            return [value]
        return [item for child in value.values() for item in references_in(child)]
    if isinstance(value, list):
        return [item for child in value for item in references_in(child)]
    return []


def check_observation(reference, name, original, context, expected_code):
    entry = bound_json(reference)
    contract = original['actual_inputs']['execution_contracts'][name]
    outputs = original['actual_inputs']['global_output_plan']['paths']
    require(entry.get('actual_root_observed_primary_exit') is True
            and entry.get('primary_exit_code_captured') is True
            and type(entry['primary_exit_code']) is int
            and entry['primary_exit_code'] == expected_code
            and entry.get('fresh_execution') is True,
            name + ' original primary observation is not the actual captured outcome')
    require(all(entry[key] == contract[key] for key in
                ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')),
            name + ' original observation does not match the original exact contract')
    require(canonical_file(entry['stdout_log']['path'])
            == canonical_file(outputs[contract['stdout_key']])
            and canonical_file(entry['exit_code_file']['path'])
            == canonical_file(contract['exit_code_path']),
            name + ' original stdout/status does not use its original sinks')
    bound_bytes(entry['stdout_log'])
    require(bound_bytes(entry['exit_code_file']) in
            (str(expected_code).encode() + b'\n', str(expected_code).encode() + b'\r\n'),
            name + ' original raw status differs from actual root observation')
    if entry['runner'] is not None:
        bound_bytes(entry['runner'])
    began = datetime.fromisoformat(entry['started_at'])
    ended = datetime.fromisoformat(entry['completed_at'])
    require(datetime.fromisoformat(context['started_at']) <= began <= ended
            <= datetime.now(timezone.utc),
            name + ' original execution is outside the actual original epoch')
    tool = entry['actual_tool_observation']
    require(type(tool['session_id']) is int and tool['session_id'] > 0
            and isinstance(tool['completion_tool_chunk'], str) and tool['completion_tool_chunk'],
            name + ' must preserve the actual completing root tool observation')
    return entry


def check_preserved_passes(spec, original, context):
    passed = spec['preserved_passed_executions']
    require(isinstance(passed, dict) and {'linux_full', 'linux_pip'} <= set(passed)
            and set(passed) <= set(EXECUTION_NAMES) - set(REPLACED_EXECUTIONS),
            'Preserve actual Linux full/pip and only completed unchanged contracts')
    outputs = original['actual_inputs']['global_output_plan']['paths']
    observed = {}
    for name, row in passed.items():
        require(set(row) == {'observation', 'receipt'}, 'Preserved pass must explicitly declare receipt or null')
        entry = check_observation(row['observation'], name, original, context, 0)
        log = bound_bytes(entry['stdout_log']).decode('utf-8', errors='replace')
        if name == 'linux_full':
            require(row['receipt'] == file_ref(outputs[name]), 'Preserved Linux full receipt sink differs')
            receipt = bound_json(row['receipt'])
            require(receipt['available_checks_passed'] is True
                    and receipt['failures'] == receipt['errors'] == 0
                    and receipt['source_drift'] == []
                    and receipt['source_sha256'] == original['actual_inputs']['classifier_source_sha256']
                    and receipt['selectors'] == original['actual_inputs']['full_selectors'],
                    'Preserved actual Linux full receipt is not a pass at original95 source/selectors')
        elif name.endswith('_pip'):
            require(row['receipt'] is None and 'No broken requirements found.' in log,
                    name + ' actual dependency check proof differs')
        elif name.endswith('_selected'):
            require(row['receipt'] is None, 'Original selected receipt is its actual console JSON')
            summaries = []
            for line in log.splitlines():
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict) and 'tests_run' in value:
                    summaries.append(value)
            require(summaries and summaries[-1]['passed'] is True
                    and summaries[-1]['failures'] == summaries[-1]['errors'] == 0,
                    name + ' original actual selected console did not pass')
        elif name == 'wine_ui':
            require(row['receipt'] == file_ref(outputs[name]), 'Preserved actual UI receipt path differs')
            receipt = bound_json(row['receipt'])
            from binding_validation095 import pointer
            pointers = original['root_spec']['ui']['pointers']
            require(pointer(receipt, pointers['passed']) is True
                    and pointer(receipt, pointers['complete']) is True
                    and pointer(receipt, pointers['drift']) == []
                    and pointer(receipt, pointers['source_before']) == pointer(receipt, pointers['source_after']),
                    'Preserved actual UI available scope/source check did not pass')
        elif name == 'saved_review':
            require(row['receipt'] == file_ref(outputs['saved_review_receipt'])
                    and entry['output_receipt'] == row['receipt'],
                    'Preserved actual saved review output differs from its primary observation')
        observed[name] = entry
    return observed


def check_prior_failure(spec, original, context):
    failed = spec['prior_failed_execution']
    require(set(failed) == {'execution_name', 'observation', 'receipt', 'runner_log'}
            and failed['execution_name'] == 'wine_full', 'Only the actual prior Wine full failure may be recorded')
    entry = check_observation(failed['observation'], 'wine_full', original, context, 1)
    require(entry['actual_tool_observation'] == {'session_id': 37864, 'completion_tool_chunk': '6e35c0'},
            'Prior failed Wine full must preserve the actual completing root tool session/chunk')
    outputs = original['actual_inputs']['global_output_plan']['paths']
    require(failed['receipt'] == file_ref(outputs['wine_full'])
            and failed['runner_log'] == file_ref(outputs['wine_full_log']),
            'Prior failed Wine full receipt/log must remain at the immutable original sinks')
    receipt = bound_json(failed['receipt'])
    bound_bytes(failed['runner_log'])
    require(receipt['available_checks_passed'] is False
            and receipt['failures'] == 1 and receipt['errors'] == 1
            and receipt['source_drift'] == []
            and receipt['source_sha256'] == original['actual_inputs']['classifier_source_sha256']
            and receipt['selectors'] == original['actual_inputs']['full_selectors']
            and {row['test'] for row in receipt['failed_cases']} == FAILED_TEST_NAMES
            and len(receipt['failed_cases']) == 2,
            'Preserved failure must be the actual two fixture-capability failures without source drift')
    return entry


def projected_outputs(original_plan, immutable_paths, preserved_output_paths):
    plan = deepcopy(original_plan)
    plan['paths'].update(REPLACED_OUTPUTS)
    plan['canonical_paths'] = {name: canonical_file(path) for name, path in plan['paths'].items()}
    plan['immutable_input_paths'] = sorted(set(plan['immutable_input_paths'])
                                          | {canonical_file(path) for path in immutable_paths})
    canonical = plan['canonical_paths']
    inputs = plan['immutable_input_paths']
    require(len(set(canonical.values())) == len(canonical), 'Recovery output files alias one another')
    require(all(not Path(other).is_relative_to(Path(path))
                for name, path in canonical.items() for other_name, other in canonical.items()
                if name != other_name), 'Recovery output file cannot contain another output file')
    preserved = {canonical_file(path) for path in preserved_output_paths}
    require(preserved <= set(canonical.values()), 'Preserved actual outputs must retain original planned sinks')
    require(set(inputs).intersection(canonical.values()) == preserved
            and all(not Path(other).is_relative_to(Path(path))
                    for path in canonical.values() for other in inputs if other != path),
            'Recovery output overlaps an input beyond the exact immutable current-epoch passed outputs')
    directories = plan['fresh_evidence_directories']
    require(directories == original_plan['fresh_evidence_directories'], 'Original UI native namespaces must be unchanged')
    for directory in directories:
        require(not any(Path(path).is_relative_to(Path(directory))
                        or Path(directory).is_relative_to(Path(path)) for path in inputs),
                'Recovery immutable input overlaps the unchanged UI native namespace')
        for name, output in canonical.items():
            require(not Path(directory).is_relative_to(Path(output)), 'Recovery output contains native namespace')
            if not name.startswith(('ui_saved_output_', 'ui_optional_output_')):
                require(not Path(output).is_relative_to(Path(directory)),
                        'Recovery nonnative output may not be placed inside native namespace')
    return plan


def validate_recovery_inputs(spec, extra_immutable_paths=()):
    require(spec.get('format_version') == 2 and spec.get('section') == 95
            and spec.get('status') == 'ROOT_BOUND_ACTUAL_FULL095_RECOVERY_SOURCE_INPUTS',
            'An actual ROOT-bound recovery spec is required; pending/future references cannot seal')
    require(spec['original']['binding'] == ORIGINAL_BINDING
            and spec['original']['runner'] == ORIGINAL_CONTEXT_RUNNER,
            'Recovery must bind the exact actual original context source/binding')
    original = bound_json(spec['original']['binding'])
    require(original['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS', 'Original actual source binding status differs')
    require(bound_json(original['root_spec_reference']) == original['root_spec'],
            'Original immutable root spec physical bytes no longer match the original sealed value')
    bound_bytes(spec['original']['runner'])
    for reference in original['final_support_files']:
        bound_bytes(reference)
    immutable = original['source_package_input_paths'] + [original['root_spec_reference']['path']]
    # This call uses the original module and its unchanged OUTPUT_NAMES, before any recovery projection.
    actual = validate_actual_inputs(original['root_spec'], immutable)
    require(actual == original['actual_inputs'], 'Original source/completion/index/binding no longer validates exactly')
    context = bound_json(spec['original']['context'])
    require(bound_bytes(spec['original']['start_exit_code']) in (b'0\n', b'0\r\n')
            and spec['original']['start_exit_code']['path']
            == '/workspace/.continuation/root-start-full095-context.exit-code'
            and spec['original']['start_console']['path']
            == '/workspace/.continuation/root-start-full095-context.log',
            'Preserve the physical actual original context-start primary zero and console')
    console = bound_bytes(spec['original']['start_console']).decode('utf-8')
    started = json.loads(console)
    require(started['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and started['section'] == 95 and started['source_files'] == actual['source_files']
            and started['actual_base_HEAD'] == actual['actual_base_HEAD'],
            'Original actual primary-zero start console differs from the original source epoch')
    require(context['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED' and context['section'] == 95
            and context['binding'] == spec['original']['binding']
            and context['final_context_runner'] == spec['original']['runner']
            and context['source_sha256'] == actual['source_sha256']
            and context['planned_fresh_sinks'] == actual['global_output_plan']['paths']
            and context['branch'] == actual['branch'] and context['actual_base_HEAD'] == actual['actual_base_HEAD'],
            'Recovery original immutable start is not the actual started95 source epoch')
    require(canonical_file(spec['original']['context']['path'])
            == actual['global_output_plan']['canonical_paths']['context_start'],
            'Original immutable context path differs')
    datetime.fromisoformat(context['started_at'])
    preserved_entries = check_preserved_passes(spec, original, context)
    prior_failed_entry = check_prior_failure(spec, original, context)
    require(spec['replacement_output_paths'] == REPLACED_OUTPUTS, 'Recovery may replace only five fixed planned paths')
    adapters = spec['adapters']
    require(set(adapters) == {'manifest', 'source_contract', 'source_evidence', 'executions'}
            and set(adapters['executions']) == set(REPLACED_EXECUTIONS),
            'Recovery requires the two precise SOURCE-reviewed adapter contracts')
    manifest = bound_json(adapters['manifest'])
    require(isinstance(manifest, dict), 'Adapter actual manifest object required')
    contract = bound_json(adapters['source_contract'])
    require(adapters['source_contract']['path']
            == '/workspace/.continuation/full095-wine-capability-retry-pending-v1/source-contract-wine-capability095.json'
            and contract['allowlisted_test_ids']
            == [row['test'] for row in bound_json(spec['prior_failed_execution']['receipt'])['failed_cases']],
            'Adapter SOURCE contract must identify the exact original two unrun capability cases')
    declared = [{key: row[key] for key in ('path', 'bytes', 'sha256')}
                for row in references_in(manifest)]
    require(adapters['source_contract'] in declared and contract['shared_admission'] in declared,
            'Adapter manifest must bind exact SOURCE contract and shared admission source')
    for reference in declared:
        bound_bytes(reference)
    require(isinstance(adapters['source_evidence'], list) and adapters['source_evidence'],
            'Actual authoritative capability diagnosis/source references required')
    for reference in adapters['source_evidence']:
        bound_bytes(reference)
    contracts = deepcopy(actual['execution_contracts'])
    mapping = actual['wine_path_mapping']
    for name in REPLACED_EXECUTIONS:
        row = adapters['executions'][name]
        require(set(row) == {'runner', 'argv', 'source_review', 'review_pointers'},
                name + ' SOURCE adapter contract shape differs')
        runner = row['runner']
        require(runner['path'] == EXPECTED_ADAPTER_PATHS[name], name + ' adapter entry path differs')
        bound_bytes(runner)
        require(runner == contract['runners'][name] and runner in declared
                and row['argv'] == contract['execution_argv'][name],
                name + ' runner/CLI must be the exact manifest/producer SOURCE contract')
        exact_source_review(row['source_review'], row['review_pointers'], runner, argv=row['argv'])
        expected = [original['root_spec']['wine_wrapper']['path'], wine_argument_for(runner['path'], mapping), '--wine']
        if name == 'wine_full':
            expected += ['--output', wine_argument_for(REPLACED_OUTPUTS['wine_full'], mapping)]
        require(row['argv'] == expected, name + ' adapter executable/script/explicit Wine/full CLI differs')
        contracts[name]['runner'] = runner
        contracts[name]['argv'] = expected
        if name == 'wine_full':
            contracts[name]['exit_code_path'] = REPLACED_OUTPUTS['wine_full_exit_code']
    projected = deepcopy(actual)
    projected['execution_contracts'] = contracts
    references = references_in(spec)
    for reference in references:
        bound_bytes(reference)
    immutable_paths = [row['path'] for row in references]
    # Physical stdout/raw/receipt references inside observations are immutable too.
    for entry in (*preserved_entries.values(), prior_failed_entry):
        immutable_paths.extend(row['path'] for row in references_in(entry))
    immutable_paths.extend(extra_immutable_paths)
    preserved_output_paths = []
    for name, entry in preserved_entries.items():
        preserved_output_paths.extend((entry['stdout_log']['path'], entry['exit_code_file']['path']))
        if spec['preserved_passed_executions'][name]['receipt'] is not None:
            preserved_output_paths.append(spec['preserved_passed_executions'][name]['receipt']['path'])
    projected['global_output_plan'] = projected_outputs(actual['global_output_plan'], immutable_paths,
                                                       preserved_output_paths)
    return original, context, projected


def validate_capability_receipt(value, binding, name):
    """Saved receipt inspection only; do not import/execute the adapter or probe."""
    require(name in REPLACED_EXECUTIONS, 'Only the two reviewed Wine adapters may use capability acceptance')
    adapters = binding['recovery_spec']['adapters']
    contract = bound_json(adapters['source_contract'])
    shared = bound_bytes(contract['shared_admission'])
    tree = ast.parse(shared)
    skip_assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'SKIP_REASON'
                                for target in node.targets)]
    require(len(skip_assignments) == 1, 'Actual SOURCE-qualified full skip reason literal missing')
    reason = ast.literal_eval(skip_assignments[0].value)
    require(isinstance(reason, str) and reason, 'Actual full capability skip reason required')
    ids = contract['allowlisted_test_ids']
    require(set(ids) == FAILED_TEST_NAMES and len(ids) == 2, 'Only the two exact original fixture IDs may be declared unrun')
    expected_records = [
        {'test': test_id, 'kind': 'environment_capability', 'classification': 'declared_skip',
         'reason': reason, 'pre_product_fixture_admission': True, 'actually_executed': False,
         'fixture_body_run': False, 'product_assertions_passed': False,
         'capability_probe_pointer': '/capability_probe', 'original_failure_preserved': True}
        for test_id in ids]
    require(value['capability_records'] == expected_records
            and all(set(row) == set(expected_records[index])
                    and row['pre_product_fixture_admission'] is True
                    and row['actually_executed'] is False and row['fixture_body_run'] is False
                    and row['product_assertions_passed'] is False and row['original_failure_preserved'] is True
                    for index, row in enumerate(value['capability_records']))
            and type(value['environment_capability_skips']) is int and value['environment_capability_skips'] == 2
            and type(value['capability_skips_counted_passed']) is int and value['capability_skips_counted_passed'] == 0
            and value['complete_repository_validation'] is False,
            'Wine capability records must identify exactly two honestly unexecuted cases, zero passed credit and incomplete repository scope')
    skips = value['skips']
    require([(row['test'], row['reason']) for row in skips if row['test'] in ids]
            == [(test_id, reason) for test_id in ids],
            'The actual unittest skip list must contain exactly the same two SOURCE-qualified full reasons')
    count_key = 'historical_or_declared_skips' if name == 'wine_full' else 'skipped'
    require(value[count_key] == len(skips), 'Wine actual declared skip counts differ from actual result rows')
    require(value['wine_compatibility'] is True and value['native_windows_integration_verified'] is False,
            'Capability acceptance cannot represent native Windows validation')
    probe = value['capability_probe']
    evidence = contract['runtime_evidence_references']
    require(probe['runtime_evidence_references'] == evidence
            and type(probe['old_failed_full_primary_exit']) is int and probe['old_failed_full_primary_exit'] == 1
            and probe['old_failed_full_receipt_preserved'] is True
            and probe['prior_failed_source_sha256'] == binding['actual_inputs']['classifier_source_sha256']
            and probe['native_windows_integration_verified'] is False
            and type(probe['project_calls_during_capability_probe']) is int
            and probe['project_calls_during_capability_probe'] == 0,
            'Actual capability probe must bind immutable original failure/source evidence without project calls')
    for reference in evidence.values():
        bound_bytes(reference)
    identity = probe['identity']
    require(identity['wine_specific_export'] == 'ntdll.wine_get_version'
            and isinstance(identity['actual_version'], str) and identity['actual_version']
            and identity['actual_version'].isascii(),
            'Actual Wine-specific identity export proof is required')
    for role, filename in (('active_kernelbase', 'kernelbase.dll'), ('active_ntdll', 'ntdll.dll')):
        active = identity[role]
        expected = evidence['installed_kernelbase' if role == 'active_kernelbase' else 'installed_ntdll']
        module_path = PureWindowsPath(active['path'])
        require(module_path.is_absolute() and module_path.name.casefold() == filename
                and active['sha256'] == expected['sha256'] and active['bytes'] == expected['bytes'],
                'Actual active Wine module must match the independently diagnosed installed source/bytes/SHA: ' + role)
    default_temp = PureWindowsPath(probe['default_temp'])
    observations = probe['observations']
    require(default_temp.is_absolute() and isinstance(observations, list) and len(observations) == 2,
            'Two actual independent fresh default-Temp observations required')
    for row, present in zip(observations, (False, True), strict=True):
        target, link = PureWindowsPath(row['target']), PureWindowsPath(row['link'])
        require(target.is_absolute() and link.is_absolute() and target.parent == link.parent
                and target.parent.parent == default_temp
                and target.drive.casefold() == default_temp.drive.casefold()
                and row['target_present'] is present
                and row['creation'] == {'returned_type': 'NoneType', 'returned_repr': 'None'}
                and row['is_symlink'] is False and row['exists'] is False
                and row['target_bytes_unchanged'] is True
                and row['actual_directory_entries'] == ([target.name] if present else []),
                'Saved actual fresh fixture must preserve the exact pre-product phantom-success pattern')
        for operation in ('lstat', 'readlink'):
            require(row[operation]['error_type'] == 'FileNotFoundError' and row[operation]['winerror'] == 2,
                    'Saved actual fresh fixture must show no link for each direct filesystem observation')
        require(row['read_bytes']['error_type'] == 'FileNotFoundError'
                and row['read_bytes']['winerror'] is None,
                'CPython buffered file open reports the source-diagnosed errno form, without inventing WinError')
    before, after = value['adapter_sources_before'], value['adapter_sources_after']
    expected_sources = {
        'wine_full095_capability_retry.py': adapters['executions']['wine_full']['runner'],
        'wine_selected095_capability.py': adapters['executions']['wine_selected']['runner'],
        'wine_symlink_capability095.py': contract['shared_admission'],
        'source-contract-wine-capability095.json': adapters['source_contract'],
    }
    require(before == after and set(before) == set(expected_sources) and value['adapter_source_drift'] == [],
            'Actual adapter/helper/contract source map must be complete and drift-free')
    mapping = binding['actual_inputs']['wine_path_mapping']
    for source_name, expected in expected_sources.items():
        observed = before[source_name]
        require(observed == {'path': wine_argument_for(expected['path'], mapping),
                             'bytes': expected['bytes'], 'sha256': expected['sha256']},
                'Actual Windows adapter source reference differs from the bound Linux original: ' + source_name)
    require(value['actual_python_argv'] == binding['actual_inputs']['execution_contracts'][name]['argv'][1:],
            'Actual adapter Python argv must match exact source-bound script/full CLI')
    if name == 'wine_full':
        require(value['original_classifier'] == evidence['original_full_classifier']
                and value['original_failed_full095_not_overwritten'] is True,
                'Actual Wine full must bind original classifier and preserve its prior failure')
