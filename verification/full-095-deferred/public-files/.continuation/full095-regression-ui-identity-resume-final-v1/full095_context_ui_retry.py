PENDING = False
if PENDING:
    raise SystemExit('PENDING SOURCE-only full095 UI identity retry: actual prior UI epoch, unknown outcomes and newly reviewed UI/saved source are not bound.')

"""Freeze and verify one available Linux/Wine regression batch."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from copy import deepcopy
from identity_binding095 import validate_recovery_inputs, validate_capability_receipt
from binding_validation095 import (EXECUTION_NAMES, OUTPUT_NAMES, bound_bytes, bound_json,
                                   canonical_file, file_ref, global_output_plan, pointer,
                                   require, source_map, validate_actual_inputs)

ROOT = Path('/workspace/rougezhushou')
OUT = Path('/workspace/.compat')
LOCAL = Path('/workspace/.continuation')
phase, number = sys.argv[1], 95
BOUND_BINDING_SHA256 = 'e818ba9aefa4d8cd739da561540ef2e49cbf38c70311346cd10c7b2d86be1bf6'
suffix = f'{number:03d}'
path = OUT / 'wine-validation-095-context-ui-identity-retry-v1.json'

def now():
    return datetime.now(timezone.utc).isoformat()

def hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def last_json(log):
    for line in reversed(log.read_text(encoding='utf-8', errors='replace').splitlines()):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and 'tests_run' in data:
            return data
    raise ValueError(f'No selected regression JSON in {log}')


def load_actual_binding():
    binding_path = Path(__file__).with_name('actual-full095-source-binding.json')
    binding_data = binding_path.read_bytes()
    require(hashlib.sha256(binding_data).hexdigest() == BOUND_BINDING_SHA256,
            'Actual recovery binding does not match final context seal')
    binding = json.loads(binding_data)
    require(binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
            and binding.get('actual_original_epoch_recovery') is True
            and binding.get('actual_ui_retry') is True
            and binding.get('actual_ui_identity_retry') is True,
            'A pending source plan is not an actual original-epoch recovery binding')
    for reference in binding['final_support_files']:
        bound_bytes(reference)
    require(bound_json(binding['recovery_spec_reference']) == binding['recovery_spec'],
            'Actual recovery root spec changed after sealing')
    immutable = binding['source_package_input_paths'] + [binding['recovery_spec_reference']['path']]
    immutable.extend([str(Path(__file__).resolve()), str(binding_path.resolve())])
    immutable.extend(row['path'] for row in binding['final_support_files'])
    original, original_context, actual = validate_recovery_inputs(binding['recovery_spec'], immutable)
    require(binding['root_spec'] == original['root_spec'] and actual == binding['actual_inputs'],
            'Original actual inputs or minimal reviewed recovery projection changed after sealing')
    return binding


def positive_int(value):
    return type(value) is int and value > 0


def nonnegative_int(value):
    return type(value) is int and value >= 0


def actual_exit_code(reference, expected_path):
    require(canonical_file(reference['path']) == canonical_file(expected_path),
            'Physical primary .exit-code reference differs from its unique planned status sink')
    data = bound_bytes(reference)
    require(data in (b'0\n', b'0\r\n'),
            'Physical primary status artifact must contain strict integer zero and one newline')
    actual_code = int(data.strip())
    require(actual_code == 0, 'Physical primary integer status is not zero')
    return actual_code


def require_primary_executions(binding, context, witness_path):
    outputs = binding['actual_inputs']['global_output_plan']['paths']
    require(canonical_file(str(witness_path)) == canonical_file(outputs['execution_witness']),
            'Root primary exit witness must use its declared fresh sink')
    witness = json.loads(witness_path.read_bytes())
    require(witness['format_version'] == 2 and witness['section'] == 95
            and witness.get('actual_root_observed_primary_exits') is True,
            'Root must record actual tool/process observations in the v2 eight-execution witness')
    executions = witness['executions']
    contracts = binding['actual_inputs']['execution_contracts']
    require(set(executions) == set(EXECUTION_NAMES) == set(contracts),
            'All eight exact main/saved-review actual executions are required')
    start = datetime.fromisoformat(context['started_at'])
    stop = datetime.now(timezone.utc)
    exit_files = []
    for name, entry in executions.items():
        contract = contracts[name]
        require(entry.get('actual_root_observed_primary_exit') is True
                and entry.get('primary_exit_code_captured') is True
                and type(entry['primary_exit_code']) is int and entry['primary_exit_code'] == 0
                and entry.get('fresh_execution') is True,
                f'{name} actual root-observed captured primary exit/freshness is incomplete')
        began = datetime.fromisoformat(entry['started_at'])
        ended = datetime.fromisoformat(entry['completed_at'])
        require(start <= began <= ended <= stop, f'{name} actual execution is outside this original full095 epoch')
        preserved = binding['recovery_spec']['preserved_passed_executions']
        if name in preserved:
            require(entry == bound_json(preserved[name]['observation']),
                    f'{name} current-epoch passed observation was substituted after recovery')
        if name in ('wine_full', 'wine_selected'):
            require(entry == bound_json(binding['recovery_spec']['preserved_recovery_passed_executions'][name]['observation']),
                    f'{name} actual earlier recovery pass was substituted or replayed')
            require(began >= datetime.fromisoformat(context['recovery_started_at']),
                    f'{name} adapter execution must be fresh after actual recovery, not the prior failed run')
        if name in ('wine_ui', 'saved_review'):
            require(began >= datetime.fromisoformat(context['ui_identity_retry_started_at']),
                    f'{name} execution must be fresh after the actual UI retry resume')
        require(entry['cwd'] == contract['cwd'] and entry['argv'] == contract['argv']
                and entry['entry_kind'] == contract['entry_kind']
                and entry['script_arg_index'] == contract['script_arg_index'],
                f'{name} exact executable/script-position/full CLI differs from reviewed launch contract')
        expected_stdout = outputs[contract['stdout_key']]
        require(canonical_file(entry['stdout_log']['path']) == canonical_file(expected_stdout),
                f'{name} actual stdout/stderr sink differs')
        bound_bytes(entry['stdout_log'])
        actual_code = actual_exit_code(entry['exit_code_file'], contract['exit_code_path'])
        require(actual_code == entry['primary_exit_code'], f'{name} physical exit status differs from root observation')
        exit_files.append(canonical_file(entry['exit_code_file']['path']))
        require(entry['runner'] == contract['runner'], f'{name} actual executed runner reference differs')
        if entry['runner'] is not None:
            bound_bytes(entry['runner'])
        if name == 'saved_review':
            require(entry['output_receipt'] == file_ref(outputs['saved_review_receipt']),
                    'Actual saved-review output receipt differs from its reviewed output sink')
    require(len(set(exit_files)) == len(EXECUTION_NAMES), 'All eight physical primary status files must be unique')
    return file_ref(witness_path), witness


def full_receipt(name, binding, historical):
    path = Path(OUTPUT_NAMES[name])
    value = json.loads(path.read_bytes())
    expected_platform = 'Windows' if name.startswith('wine_') else 'Linux'
    require(value['platform'] == expected_platform
            and value['wine_compatibility'] is name.startswith('wine_')
            and value['native_windows_integration_verified'] is False,
            f'{name} compatibility/platform claim differs')
    require(value['available_checks_passed'] is True and value['failures'] == value['errors'] == 0
            and not value['source_drift'], f'{name} available checks did not pass')
    require(value['source_sha256'] == binding['actual_inputs']['classifier_source_sha256'],
            f'{name} original full runner source scope differs from actual95')
    require(value['selectors'] == binding['actual_inputs']['full_selectors'],
            f'{name} must include exact current historical/new/selected selector order')
    require(positive_int(value['tests_run']) and all(nonnegative_int(value[k]) for k in
            ('tests_passed', 'historical_or_declared_skips', 'failures', 'errors',
             'unavailable_records', 'unavailable_parent_count')), f'{name} invalid actual counts')
    require(value['tests_passed'] <= value['tests_run'], f'{name} impossible success count')
    require(value['unavailable_records'] == len(value['unavailable'])
            and 0 <= value['unavailable_parent_count'] <= value['unavailable_records'],
            f'{name} unavailable rows/parents differ')
    require(value['historical_or_declared_skips'] == len(value['skips']), f'{name} skip count differs')
    require(len(value['failed_cases']) == value['failures'] + value['errors'],
            f'{name} failure record counts differ')
    require(all(row['kind'] in ('unmigrated_cache', 'environment_dependency')
                for row in value['unavailable']), f'{name} classifier taxonomy changed')
    require(value['complete_repository_validation'] is (not value['unavailable']),
            f'{name} absent evidence cannot be called complete validation')
    old_skips = {row['test']: row['reason'] for row in historical['retired_or_declared_skips']}
    new_skips = {row['test']: row['reason'] for row in value['skips']}
    require(all(new_skips.get(test) == reason for test, reason in old_skips.items()),
            f'{name} existing historical/declared skip classifications changed')
    return file_ref(path), value


def wine_full_receipt(name, binding, historical):
    require(name == 'wine_full', 'Only the SOURCE-reviewed Wine full may use capability qualification')
    path = Path(binding['actual_inputs']['global_output_plan']['paths'][name])
    value = json.loads(path.read_bytes())
    expected_platform = 'Windows' if name.startswith('wine_') else 'Linux'
    require(value['platform'] == expected_platform
            and value['wine_compatibility'] is name.startswith('wine_')
            and value['native_windows_integration_verified'] is False,
            f'{name} compatibility/platform claim differs')
    require(value['available_checks_passed'] is True and value['failures'] == value['errors'] == 0
            and not value['source_drift'], f'{name} available checks did not pass')
    require(value['source_sha256'] == binding['actual_inputs']['classifier_source_sha256'],
            f'{name} original full runner source scope differs from actual95')
    require(value['selectors'] == binding['actual_inputs']['full_selectors'],
            f'{name} must include exact current historical/new/selected selector order')
    require(positive_int(value['tests_run']) and all(nonnegative_int(value[k]) for k in
            ('tests_passed', 'historical_or_declared_skips', 'failures', 'errors',
             'unavailable_records', 'unavailable_parent_count')), f'{name} invalid actual counts')
    require(value['tests_passed'] <= value['tests_run'], f'{name} impossible success count')
    require(value['unavailable_records'] == len(value['unavailable'])
            and 0 <= value['unavailable_parent_count'] <= value['unavailable_records'],
            f'{name} unavailable rows/parents differ')
    require(value['historical_or_declared_skips'] == len(value['skips']), f'{name} skip count differs')
    require(len(value['failed_cases']) == value['failures'] + value['errors'],
            f'{name} failure record counts differ')
    require(all(row['kind'] in ('unmigrated_cache', 'environment_dependency')
                for row in value['unavailable']), f'{name} classifier taxonomy changed')
    validate_capability_receipt(value, binding, name)
    require(value['complete_repository_validation'] is False,
            'Actual admitted two Wine fixture skips prevent complete repository validation even without other unavailable rows')
    old_skips = {row['test']: row['reason'] for row in historical['retired_or_declared_skips']}
    new_skips = {row['test']: row['reason'] for row in value['skips']}
    require(all(new_skips.get(test) == reason for test, reason in old_skips.items()),
            f'{name} existing historical/declared skip classifications changed')
    return file_ref(path), value


def selected_receipt(name):
    path = Path(binding['actual_inputs']['global_output_plan']['paths'][name])
    value = last_json(path)
    require(value['passed'] is True and value['failures'] == value['errors'] == 0
            and nonnegative_int(value['failures']) and nonnegative_int(value['errors']),
            f'{name} selected checks did not pass')
    require(value['platform'] == ('Windows' if name.startswith('wine_') else 'Linux'),
            f'{name} selected platform differs')
    require(positive_int(value['tests_run']) and nonnegative_int(value['skipped'])
            and value['skipped'] <= value['tests_run'], f'{name} selected counts invalid')
    return file_ref(path), value


def actual_ui_receipt(binding):
    ui_contract = binding['root_spec']['ui']
    path = Path(ui_contract['receipt_path'])
    ui = json.loads(path.read_bytes())
    p = ui_contract['pointers']
    require(pointer(ui, p['passed']) is True and pointer(ui, p['complete']) is True
            and not pointer(ui, p['drift']), 'Actual fullUI095 did not fully pass its available scope')
    checks = pointer(ui, p['checks'])
    require(isinstance(checks, list) and checks and all(isinstance(row, dict)
            and row.get('passed') is not False for row in checks),
            'Actual fullUI095 has no actual checks or contains an explicit failure')
    require(ui['native_windows_verified'] is False and ui['game_captures'] == 0
            and ui['chat_requests'] == 0 and ui['private_state_isolated'] is True,
            'Actual fullUI must remain compatibility-only with public temporary state and no external operations')
    before = pointer(ui, p['source_before'])
    after = pointer(ui, p['source_after'])
    require(isinstance(before, dict) and before and before == after,
            'Actual fullUI095 own source scope drifted')
    maintained = source_map(binding['actual_inputs']['source_sha256'])
    source_map(before)
    source_map(after)
    expected_keys = set(binding['actual_inputs']['UI_expected_own_source_keys'])
    require(set(before) == set(after) == expected_keys and expected_keys <= set(maintained)
            and all(before[name] == maintained[name] for name in expected_keys),
            'Actual fullUI095 keys/digest types/scope do not equal source-qualified exact own selector')
    return file_ref(path), ui, len(checks)


def proof_file_binding(proof, contract, expected, full_reference_required=False):
    value = pointer(proof, contract['pointer'])
    projection = contract['projection']
    require(projection in ('full_ref', 'bytes_sha256'), 'Unknown saved proof file binding shape')
    if full_reference_required:
        require(projection == 'full_ref', 'Visual review must bind the actual current file path as well as bytes/hash')
    if projection == 'full_ref':
        require(value == expected, 'Actual saved/visual proof exact file reference differs')
    else:
        require(isinstance(value, dict) and value.get('bytes') == expected['bytes']
                and value.get('sha256') == expected['sha256'],
                'Actual saved proof file bytes/hash differs')
        if 'path' in value:
            require(value['path'] == expected['path'], 'Actual saved proof file path differs')


def saved_review_execution(row, witness):
    require(row['execution_name'] == 'saved_review', 'Saved proof must identify actual saved_review execution')
    execution = witness['executions']['saved_review']
    require(execution['output_receipt'] == row['file'],
            'Actual saved-review physical exit witness refers to a different proof receipt')
    return execution


def actual_ui_extra_acceptance(path, binding, current_ui_ref, witness):
    document = json.loads(path.read_bytes())
    require(document['format_version'] == 2 and document['section'] == 95,
            'Actual root fullUI additional acceptance schema differs')
    require(document['actual_ui_receipt'] == current_ui_ref,
            'Extra UI acceptance is not bound to the current actual full095 UI receipt')
    require(document['primary_exit_witness'] == file_ref(binding['actual_inputs']['global_output_plan']['paths']['execution_witness']),
            'Actual extraUI saved proof refers to a different eight-execution physical exit witness')
    artifacts = document['artifacts']
    require(isinstance(artifacts, list) and artifacts, 'Actual fullUI native/PNG artifacts required')
    actual_files = {}
    canonical_artifacts = set()
    output_plan_bound = binding['actual_inputs']['global_output_plan']
    declared = {output_plan_bound['canonical_paths'][f'ui_saved_output_{index}']
                for index, _ in enumerate(binding['root_spec']['ui']['required_saved_outputs'])}
    directories = [Path(path) for path in output_plan_bound['fresh_evidence_directories']]
    for item in artifacts:
        require(item['kind'] in ('native-evidence', 'screenshot'), 'Unknown fullUI artifact kind')
        reference = item['file']
        bound_bytes(reference)
        canonical = canonical_file(reference['path'])
        require(canonical not in canonical_artifacts, 'Actual native/PNG artifact paths alias one another')
        allowed_incremental = item['kind'] == 'native-evidence' and any(Path(canonical).is_relative_to(directory) for directory in directories)
        require(canonical in declared or allowed_incremental,
                'Actual native/PNG file is outside all source-qualified sinks and fresh native namespaces')
        canonical_artifacts.add(canonical)
        require(reference['path'] not in actual_files, 'Duplicate actual fullUI artifact binding')
        actual_files[reference['path']] = item
    planned = binding['root_spec']['ui']['required_saved_outputs']
    require(all(row['path'] in actual_files and actual_files[row['path']]['kind'] == row['kind']
                for row in planned), 'Actual native/PNG artifacts omit a declared finalUI source sink')
    for directory in directories:
        require(directory.is_dir() and not directory.is_symlink(), 'Actual native namespace missing or symlinked')
        physical = set()
        for artifact in directory.rglob('*'):
            require(not artifact.is_symlink() and (artifact.is_file() or artifact.is_dir()),
                    'Actual native namespace contains a symlink or nonregular entry')
            if artifact.is_file():
                physical.add(canonical_file(str(artifact)))
        covered_namespace = {name for name in canonical_artifacts if Path(name).is_relative_to(directory)}
        require(physical == covered_namespace, 'Actual saved proof does not cover the exact physical native namespace')
    screenshot_paths = {name for name, item in actual_files.items() if item['kind'] == 'screenshot'}
    require(screenshot_paths and any(item['kind'] == 'native-evidence' for item in artifacts),
            'Actual fullUI native and screenshot evidence must both exist')
    rows = document['receipts']
    output_plan = binding['actual_inputs']['global_output_plan']['paths']
    require(isinstance(rows, list) and {'saved-validation', 'visual-review'} <= {row['kind'] for row in rows},
            'Actual fullUI requires saved validation and real screenshot inspection')
    require(all(row['kind'] in ('saved-validation', 'visual-review') for row in rows)
            and len(rows) == 2, 'Exactly one saved and one visual acceptance receipt required')
    require(all(row['file']['path'] == output_plan['saved_review_receipt' if row['kind'] == 'saved-validation' else 'visual_review'] for row in rows),
            'Actual saved/visual receipt path differs from globally planned fresh sink')
    output = []
    for row in rows:
        require(row['kind'] in ('saved-validation', 'visual-review'), 'Unknown extraUI acceptance kind')
        proof = bound_json(row['file'])
        checks = row['required_true_pointers']
        require(isinstance(checks, list) and checks and all(pointer(proof, p) is True for p in checks),
                'Actual fullUI saved/visual acceptance not passed')
        visual = row['kind'] == 'visual-review'
        common = row['common_file_bindings']
        required_common = {'ui_receipt'} if visual else {'ui_receipt', 'ui_runner', 'source_guard'}
        expected_common = {'ui_receipt': current_ui_ref,
                           'ui_runner': file_ref(binding['root_spec']['ui']['runner']['path']),
                           'source_guard': file_ref(binding['root_spec']['completed_working_tree_chain'][-1]['source_guard']['path'])}
        require(isinstance(common, dict) and required_common <= set(common)
                and set(common) <= set(expected_common),
                'Actual saved/visual common source/receipt bindings incomplete')
        for name, contract in common.items():
            proof_file_binding(proof, contract, expected_common[name], visual)
        actual_saved_exit = None if visual else saved_review_execution(row, witness)
        if visual:
            require(pointer(proof, row['actual_view_image_pointer']) is True,
                    'Source descriptions cannot substitute for actual screenshot tool inspection')
        file_bindings = row['artifact_bindings']
        require(isinstance(file_bindings, list) and file_bindings, 'Actual proof artifact pointers required')
        covered = set()
        for contract in file_bindings:
            artifact_path = contract['artifact_path']
            require(artifact_path in actual_files and artifact_path not in covered,
                    'Actual proof has unrelated or duplicate artifact binding')
            proof_file_binding(proof, contract, actual_files[artifact_path]['file'], visual)
            covered.add(artifact_path)
        required = screenshot_paths if visual else set(actual_files)
        require(required <= covered, 'Actual saved/visual proof does not cover the required current artifacts')
        output.append({'kind': row['kind'], 'file': row['file'], 'checked_true_pointers': checks,
                       'checked_common_file_bindings': common,
                       'checked_artifact_bindings': file_bindings,
                       'actual_saved_review_primary_exit': actual_saved_exit})
    return file_ref(path), {'actual_ui_receipt': current_ui_ref, 'artifacts': artifacts, 'receipts': output}


binding = load_actual_binding()
actual = binding['actual_inputs']
require(hashes() == actual['source_sha256'], 'Actual maintained source differs immediately before context phase')
require(sys.argv[1] in ('resume', 'finish'), 'Expected resume or finish; do not replay original start')

if phase == 'resume':
    require(len(sys.argv) == 2, 'Usage: final recovery context resume')
    recovery_spec = binding['recovery_spec']
    original_context = bound_json(recovery_spec['original']['context'])
    prior_recovery_context = bound_json(recovery_spec['prior_recovery']['context'])
    prior_ui_context = bound_json(recovery_spec['prior_ui_retry']['context'])
    new_paths = recovery_spec['ui_retry_output_paths']
    require(all(not Path(name).exists() for name in new_paths.values())
            and all(not Path(name).exists() for name in actual['global_output_plan']['fresh_evidence_directories']),
            'A new UI retry/control/final sink or native namespace already exists; preserve it and diagnose')
    # started_at is the actual original epoch, never a claim of a backdated new run.
    # Every preserved pass was already checked against its physical original proof.
    ctx = deepcopy(prior_ui_context)
    ctx.update(status='ACTUAL_FULL095_STARTED_NOT_PASSED',
               actual_original_epoch_recovery=True,
               actual_ui_retry=True,
               ui_retry_started_at=prior_ui_context['ui_retry_started_at'],
               actual_ui_identity_retry=True,
               ui_identity_retry_started_at=now(),
               prior_ui_retry=recovery_spec['prior_ui_retry'],
               prior_incomplete_ui_cache=recovery_spec['prior_incomplete_ui_cache'],
               prior_recovery=recovery_spec['prior_recovery'],
               prior_incomplete_ui=recovery_spec['prior_incomplete_ui'],
               prior_selected_failed_execution=recovery_spec['prior_selected_failed_execution'],
               preserved_recovery_passed_executions=recovery_spec['preserved_recovery_passed_executions'],
               ui_retry_source=recovery_spec['ui_retry'],
               recovery_started_at=prior_recovery_context['recovery_started_at'],
               original_context=recovery_spec['original']['context'],
               original_source_binding=recovery_spec['original']['binding'],
               original_context_runner=recovery_spec['original']['runner'],
               original_started_at_preserved_without_new_start=True,
               preserved_passed_executions=recovery_spec['preserved_passed_executions'],
               prior_failed_execution=recovery_spec['prior_failed_execution'],
               binding=file_ref(Path(__file__).with_name('actual-full095-source-binding.json')),
               final_context_runner=file_ref(Path(__file__)),
               planned_fresh_sinks=new_paths,
               planned_current_epoch_sinks=actual['global_output_plan']['paths'],
               available_checks_passed=False,
               recovery_context_calls_project=0,
               original_successful_executions_replayed_by_context=0)
    require(ctx['started_at'] == original_context['started_at']
            and ctx['recovery_started_at'] == prior_recovery_context['recovery_started_at']
            and datetime.fromisoformat(ctx['started_at']) <= datetime.fromisoformat(ctx['recovery_started_at'])
            <= datetime.fromisoformat(ctx['ui_retry_started_at'])
            <= datetime.fromisoformat(ctx['ui_identity_retry_started_at']),
            'UI retry must retain both actual earlier epoch boundaries and add only its new real boundary')
    with path.open('x', encoding='utf-8') as stream:
        json.dump(ctx, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'section': number, 'source_files': len(ctx['source_sha256']),
                      'actual_base_HEAD': ctx['actual_base_HEAD'], 'status': ctx['status'],
                      'actual_original_epoch_recovery': True, 'actual_ui_retry': True,
                      'recovery_started_at': ctx['recovery_started_at'],
                      'ui_retry_started_at': ctx['ui_retry_started_at'],
                      'actual_ui_identity_retry': True,
                      'ui_identity_retry_started_at': ctx['ui_identity_retry_started_at'],
                      'preserved_passed_executions': sorted(ctx['preserved_passed_executions']),
                      'original_start_replayed': False}))
elif phase == 'finish':
    require(len(sys.argv) == 6 and sys.argv[2] == '--executions' and sys.argv[4] == '--ui-acceptance',
            'Usage: final context finish --executions actual-root-primary-exits.json --ui-acceptance actual-ui-acceptance.json')
    ctx = json.loads(path.read_bytes())
    require(ctx['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED' and ctx['section'] == 95
            and ctx.get('actual_original_epoch_recovery') is True and ctx.get('actual_ui_retry') is True
            and ctx.get('actual_ui_identity_retry') is True,
            'Actual UI retry recovery context missing')
    recovery_spec = binding['recovery_spec']
    original_context = bound_json(recovery_spec['original']['context'])
    require(ctx['original_context'] == recovery_spec['original']['context']
            and ctx['original_source_binding'] == recovery_spec['original']['binding']
            and ctx['original_context_runner'] == recovery_spec['original']['runner']
            and ctx['started_at'] == original_context['started_at']
            and ctx['original_started_at_preserved_without_new_start'] is True
            and ctx['preserved_passed_executions'] == recovery_spec['preserved_passed_executions']
            and ctx['prior_failed_execution'] == recovery_spec['prior_failed_execution']
            and ctx['planned_fresh_sinks'] == recovery_spec['ui_retry_output_paths']
            and ctx['prior_recovery'] == recovery_spec['prior_recovery']
            and ctx['prior_incomplete_ui'] == recovery_spec['prior_incomplete_ui']
            and ctx['prior_selected_failed_execution'] == recovery_spec['prior_selected_failed_execution']
            and ctx['preserved_recovery_passed_executions'] == recovery_spec['preserved_recovery_passed_executions']
            and ctx['ui_retry_source'] == recovery_spec['ui_retry']
            and ctx['prior_ui_retry'] == recovery_spec['prior_ui_retry']
            and ctx['prior_incomplete_ui_cache'] == recovery_spec['prior_incomplete_ui_cache']
            and ctx['ui_retry_started_at'] == bound_json(recovery_spec['prior_ui_retry']['context'])['ui_retry_started_at']
            and ctx['recovery_started_at'] == bound_json(recovery_spec['prior_recovery']['context'])['recovery_started_at']
            and ctx['planned_current_epoch_sinks'] == actual['global_output_plan']['paths']
            and datetime.fromisoformat(ctx['started_at']) <= datetime.fromisoformat(ctx['recovery_started_at'])
            <= datetime.fromisoformat(ctx['ui_retry_started_at'])
            <= datetime.fromisoformat(ctx['ui_identity_retry_started_at']) <= datetime.now(timezone.utc),
            'Actual UI retry altered an earlier epoch, passed outcome, prior failure/incomplete UI or reviewed planned sink')
    require(ctx['binding'] == file_ref(Path(__file__).with_name('actual-full095-source-binding.json'))
            and ctx['final_context_runner'] == file_ref(Path(__file__)),
            'Actual recovery context/binding changed since resume')
    require(ctx['source_sha256'] == actual['source_sha256'], 'Started context bound a different actual source')
    after = hashes()
    drift = [name for name in sorted(set(after) | set(ctx['source_sha256']))
             if after.get(name) != ctx['source_sha256'].get(name)]
    require(not drift, 'Maintained source drifted during the full095 suite')
    require(canonical_file(sys.argv[5]) == actual['global_output_plan']['canonical_paths']['ui_extra_acceptance'],
            'Actual extraUI acceptance path differs from globally disjoint planned sink')
    execution_ref, witness = require_primary_executions(binding, ctx, Path(sys.argv[3]))
    historical = json.loads(Path(__file__).with_name('historical-classifications090.json').read_bytes())
    linux_ref, linux = full_receipt('linux_full', binding, historical)
    wine_ref, wine = wine_full_receipt('wine_full', binding, historical)
    linux_selected_ref, linux_selected = selected_receipt('linux_selected')
    wine_selected_ref, wine_selected = selected_receipt('wine_selected')
    validate_capability_receipt(wine_selected, binding, 'wine_selected')
    for name in ('linux_pip', 'wine_pip'):
        require('No broken requirements found.' in Path(OUTPUT_NAMES[name]).read_text(encoding='utf-8', errors='replace'),
                f'{name} dependency check did not pass')
    ui_ref, ui, ui_checks = actual_ui_receipt(binding)
    ui_acceptance_ref, ui_acceptance = actual_ui_extra_acceptance(Path(sys.argv[5]), binding, ui_ref, witness)
    require(hashes() == after, 'Source drifted while saved outputs were reviewed')
    ctx.update(status='PASS_ACTUAL_FULL095_AVAILABLE_NOT_NATIVE_WINDOWS',
               completed_at=now(), source_sha256_after=after, source_drift=drift,
               available_checks_passed=True, complete_ui_validation=True, ui_checks=ui_checks,
               complete_repository_validation=linux['complete_repository_validation'] and wine['complete_repository_validation'],
               checks={'linux_full': linux_ref, 'wine_full': wine_ref,
                       'linux_selected': linux_selected_ref, 'wine_selected': wine_selected_ref,
                       'linux_pip': file_ref(OUTPUT_NAMES['linux_pip']), 'wine_pip': file_ref(OUTPUT_NAMES['wine_pip']),
                       'actual_ui': ui_ref, 'actual_ui_extra_acceptance': ui_acceptance_ref,
                       'root_primary_exits': execution_ref},
               actual_counts={'linux': {k: linux[k] for k in ('tests_run', 'tests_passed',
                   'historical_or_declared_skips', 'failures', 'errors', 'unavailable_records', 'unavailable_parent_count')},
                   'wine': {k: wine[k] for k in ('tests_run', 'tests_passed',
                   'historical_or_declared_skips', 'failures', 'errors', 'unavailable_records', 'unavailable_parent_count')},
                   'linux_selected': linux_selected, 'wine_selected': wine_selected, 'ui_checks': ui_checks},
               fresh_selected_executed_linux_and_wine=True, selected_reuse_performed=False,
               physical_primary_exit_files_verified=len(EXECUTION_NAMES), exact_execution_contracts_verified=True,
               actual_ui_acceptance=ui_acceptance, actual_root_primary_exits=witness,
               count_qualification='Unavailable row/subtest/parent totals may overlap; they are not successful tests or a disjoint subtraction from tests_run.',
               recovery_contract_projection_verified=True, original_context_immutable_verified=True,
               reused_passed_current_epoch_executions=sorted(recovery_spec['preserved_passed_executions']),
               prior_failed_wine_full_preserved=True, prior_incomplete_ui_preserved=True,
               prior_recovery_started_at_preserved=True, ui_retry_contract_projection_verified=True,
               prior_ui_retry_started_at_preserved=True, prior_incomplete_ui_cache_preserved=True,
               ui_identity_retry_contract_projection_verified=True,
               prior_failed_wine_selected_preserved=True,
               reused_passed_recovery_executions=sorted(recovery_spec['preserved_recovery_passed_executions']),
               outcome='Available Linux/Wine full and selected suites, both dependency checks and actual fullUI passed at exact completed95 bytes across the actual original epoch, with reviewed Wine capability adapters and immutable original failure/passed evidence.',
               next_authorized_action='Root archives exact full095 evidence, verifies staged/committed payload blobs, then performs the group commit and normal push to origin codex/p2-development; no force push.')
    final_path = Path(actual['global_output_plan']['paths']['context_final'])
    with final_path.open('x', encoding='utf-8') as stream:
        json.dump(ctx, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'section': 95, 'available_checks_passed': True,
                      'complete_repository_validation': ctx['complete_repository_validation'],
                      'complete_ui_validation': True, 'source_files': len(after), 'source_drift': drift,
                      'ui_checks': ui_checks, 'native_windows': False, 'commit_or_push_performed': False}))
