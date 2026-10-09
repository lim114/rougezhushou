"""Root-only stdlib SOURCE metadata assembly; no product/test/codec/UI/Git calls."""
import argparse
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re

ROOT = Path('/workspace/rougezhushou')
SOURCE = Path('/workspace/.continuation/full095-regression-ui-identity-resume-source-v1')
PRODUCER = Path('/workspace/.continuation/full095-ui-identity-retry-source-v1')
SAVED = Path('/workspace/.continuation/full095-saved-validator-ui-identity-source-v1')
PRELAUNCH = Path('/workspace/.continuation/root-full095-ui-identity-retry-v1-prelaunch.json')
SPEC = Path('/workspace/.continuation/root-full095-ui-identity-retry-v1-actual-spec.json')
PINS = {
    str(SOURCE / 'public-artifacts-manifest-ui-retry095.json'):
        (3578, 'bacdf2336d69c08e994f06df41c184d7ce7086900b935207e797515af7ac297c'),
    str(PRODUCER / 'public-artifacts-manifest-identity-retry095.json'):
        (2290, '6ca4fd70d8acf5a9eb6b58927874c881e2196c8ccf0ab0de1e90d096983542c8'),
    str(PRODUCER / 'source-contract-identity-retry095.json'):
        (20635, '05ca7f22bdcb531368985ff71c3613b519167afd5f38c6dee119fc3718f4934f'),
    str(PRODUCER / 'wine-full-ui-095-identity-retry.py'):
        (1185253, '0e8a0bc1ed4e890cd6a0cf762c7437ced1080dba6ac82e48c680e8d6dc226b0d'),
    str(SAVED / 'public-artifacts-manifest-source-preparation095.json'):
        (2303, '47251cbe499c14253bf5c6f0636fdf43d951c6624f47c05f7ef9edea05e7f81b'),
    str(SAVED / 'saved.py'):
        (98186, '6d94c3effb6c56987ece108af152b885ce35485f6220533596ed888d259f41ff'),
    '/workspace/.continuation/root-source-095-v2.json':
        (84227, '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'),
    '/workspace/.continuation/ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json':
        (530488, 'bcbf9e5e3f9aeff1745387221cd0b293aca149d52cbf566750cb0afea3d80eb6'),
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def file_ref(path):
    path = Path(path)
    require(path.is_absolute() and path.is_file() and not path.is_symlink(),
            'Physical absolute nonsymlink regular file required: ' + str(path))
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}

def bound_bytes(reference):
    require(isinstance(reference, dict) and set(reference) == {'path', 'bytes', 'sha256'}
            and type(reference['bytes']) is int and reference['bytes'] >= 0
            and isinstance(reference['sha256'], str) and re.fullmatch('[0-9a-f]{64}', reference['sha256']),
            'Nonempty exact path/bytes/SHA reference required')
    require(file_ref(reference['path']) == reference, 'Actual physical bytes/SHA changed: ' + reference['path'])
    return Path(reference['path']).read_bytes()

def bound_json(reference):
    return json.loads(bound_bytes(reference))

def pinned(path):
    path = Path(path)
    count, sha = PINS[str(path)]
    reference = {'path': str(path), 'bytes': count, 'sha256': sha}
    return reference, bound_json(reference) if path.suffix == '.json' else bound_bytes(reference)

def pointer(value, location):
    require(isinstance(location, str) and location.startswith('/'), 'RFC6901 pointer required')
    for key in location.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value

def source_review(path, expected_sha, pointers, runner, argv, own_keys=None):
    require(re.fullmatch('[0-9a-f]{64}', expected_sha) is not None,
            'Actual independent Source review SHA must be explicit, never pending')
    reference = file_ref(path)
    require(reference['sha256'] == expected_sha, 'Independent Source review SHA differs')
    value = bound_json(reference)
    require(pointer(value, pointers['source_pass']) is True
            and pointer(value, pointers['runtime_pass']) is False
            and pointer(value, pointers['runner_sha256']) == runner['sha256']
            and pointer(value, pointers['argv']) == argv,
            'Actual independent review must approve exact Source runner/argv without runtime claim')
    if own_keys is not None:
        require(pointer(value, pointers['source_keys']) == own_keys,
                'Own UI source scope differs from the unchanged exact 129-key Source scope')
    return reference

def verify_source_packet(manifest_ref, manifest, here):
    rows = manifest['payload_files']
    require(manifest['STOPWRITE'] is True and manifest['runtime_executed'] is False
            and manifest['available_checks_passed'] is False,
            'Context Source preparation is not a runtime result')
    for row in rows:
        require(Path(row['path']).parent == here, 'Context Source member escaped its packet')
        bound_bytes(row)
    require({path.name for path in here.iterdir()}
            == {Path(row['path']).name for row in rows}
               | {'public-artifacts-manifest-ui-retry095.json', 'handoff-ui-retry095.json'},
            'Context packet physical set differs from its frozen manifest')

def inverse_context_source():
    inverse = json.loads((SOURCE / 'ui-retry-context-inverse095.json').read_bytes())
    recovered = bound_bytes(inverse['pending_context_reference']).decode()
    for row in reversed(inverse['changes']):
        require(row['count'] == 1 and recovered.count(row['after']) == 1,
                'Each original context inverse span must be unique')
        recovered = recovered.replace(row['after'], row['before'], 1)
    require(recovered.encode() == bound_bytes(inverse['baseline_context_reference']),
            'Pending context failed its complete prior context byte inverse')

def maintained_hashes():
    return {path.relative_to(ROOT).as_posix(): digest(path.read_bytes())
            for name in ('rouge', 'tests', 'scripts')
            for path in sorted((ROOT / name).rglob('*'))
            if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}

def exclusive_json(path, value):
    data = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with path.open('xb') as stream:
        stream.write(data)
    return file_ref(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ui-formal', type=Path, required=True)
    parser.add_argument('--ui-formal-sha256', required=True)
    parser.add_argument('--saved-formal', type=Path, required=True)
    parser.add_argument('--saved-formal-sha256', required=True)
    parser.add_argument('--prelaunch', type=Path,
                        help='Validate an existing actual Root prelaunch instead of creating one')
    parser.add_argument('--prelaunch-sha256',
                        help='Required with --prelaunch; pins an existing actual Root prelaunch')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.output == SPEC and not args.output.exists(),
            'Use the reserved new unused actual Source spec path; preserve every older output')
    require((args.prelaunch is None) == (args.prelaunch_sha256 is None),
            'Existing actual prelaunch requires both exact path and SHA')
    if args.prelaunch is None:
        require(not PRELAUNCH.exists(), 'Prelaunch already exists: preserve it and use pinned existing mode')
    else:
        require(args.prelaunch == PRELAUNCH, 'Existing prelaunch must use the exact planned identity sink')

    context_manifest_ref, context_manifest = pinned(SOURCE / 'public-artifacts-manifest-ui-retry095.json')
    verify_source_packet(context_manifest_ref, context_manifest, SOURCE)
    inverse_context_source()
    template = json.loads((SOURCE / 'root-ui-retry-input-template095.json').read_bytes())
    require(template['status'] == 'SOURCE_ONLY_PENDING_ACTUAL_ROOT_UI_RETRY_BINDING',
            'The frozen pending template status changed')
    prior = bound_json(template['prior_ui_retry']['binding'])
    require(prior['actual_inputs']['source_files'] == 735
            and prior['actual_inputs']['actual_base_HEAD'] == 'f509d186e501bfcfd042e45b46e398ec756840ec'
            and prior['actual_inputs']['branch'] == 'codex/p2-development',
            'Preserve the actual paused section95 source/base/branch')
    for row in template['prior_ui_retry'].values():
        bound_bytes(row)
    require(bound_bytes(template['prior_ui_retry']['resume_exit_code']) in (b'0\n', b'0\r\n'),
            'Prior actual UI retry resume primary zero must remain unchanged')
    guard_ref, guard = pinned('/workspace/.continuation/root-source-095-v2.json')
    maintained = maintained_hashes()
    require(len(maintained) == 735 and maintained == guard['source_sha256_after']
            == prior['actual_inputs']['source_sha256'],
            'All current735 maintained Source files must match the immutable section95 guard')
    loss_ref, loss = pinned('/workspace/.continuation/ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json')
    require(template['prior_incomplete_ui_cache'] == loss_ref
            and loss['primary_exit_code'] is None and loss['primary_exit_code_captured'] is False
            and loss['actual_root_requested_process_termination'] is False
            and loss['cause_of_external_session_loss'] == 'UNKNOWN'
            and loss['same_UI_execution_problem_incomplete_attempt_count'] == 2
            and loss['third_attempt_failure_requires_deferral'] is True,
            'Second unknown UI outcome may not be replaced with failure/PASS or new cause')
    six = {name: row['observation']
           for field in ('preserved_passed_executions', 'preserved_recovery_passed_executions')
           for name, row in template[field].items()}
    require(six == loss['six_completed_primary_observations_preserved'] and len(six) == 6,
            'All six real completed observations must remain byte-identical')
    for name, row in six.items():
        value = bound_json(row)
        require(value['actual_root_observed_primary_exit'] is True
                and value['primary_exit_code_captured'] is True and type(value['primary_exit_code']) is int
                and value['primary_exit_code'] == 0
                and bound_bytes(value['exit_code_file']) in (b'0\n', b'0\r\n'),
                'Existing actual primary zero proof changed: ' + name)
        bound_bytes(value['stdout_log'])

    manifest_ref, manifest = pinned(PRODUCER / 'public-artifacts-manifest-identity-retry095.json')
    contract_ref, contract = pinned(PRODUCER / 'source-contract-identity-retry095.json')
    runner_ref, runner_source = pinned(PRODUCER / 'wine-full-ui-095-identity-retry.py')
    require(manifest['status'] == 'STOPWRITE_IDENTITY_RETRY_SOURCE_ONLY_RUNTIME_UNRUN'
            and manifest['STOPWRITE'] is True and manifest['runtime_calls'] == 0,
            'Frozen actual producer Source package required')
    for name, metadata in manifest['artifacts'].items():
        require(Path(name).name == name, 'Producer payload must be direct package files')
        bound_bytes({'path': str(PRODUCER / name), **metadata})
    require({path.name for path in PRODUCER.iterdir()}
            == set(manifest['artifacts']) | {'public-artifacts-manifest-identity-retry095.json', 'handoff-identity-retry095.json'},
            'Producer Source physical set changed')
    saved_manifest_ref, saved_manifest = pinned(SAVED / 'public-artifacts-manifest-source-preparation095.json')
    saved_ref, saved_source = pinned(SAVED / 'saved.py')
    require(saved_manifest['STOPWRITE'] is True and saved_manifest['runtime_pass'] is False
            and saved_manifest['target_execution_calls'] == 0,
            'Frozen Saved Source package required; no runtime credit')
    for name, row in saved_manifest['files'].items():
        require(Path(row['path']).parent == SAVED and Path(row['path']).name == name,
                'Saved Source payload escaped its frozen package')
        bound_bytes(row)
    ast.parse(runner_source); ast.parse(saved_source)
    assertions = sum(isinstance(node, ast.Assert) for node in ast.walk(ast.parse(runner_source)))
    require(assertions == 907, 'The original exact907 producer assertions must remain')
    require(contract['runner'] == runner_ref and contract['source_guard'] == guard_ref
            and contract['source_keys'] == prior['actual_inputs']['UI_expected_own_source_keys']
            and len(contract['source_keys']) == 129,
            'The new runner Source guard/129-own-key selectors changed')
    mapping = prior['actual_inputs']['wine_path_mapping']
    wine_argument = str(PureWindowsPath(mapping['drive'] + '\\').joinpath(
        *Path(runner_ref['path']).relative_to(mapping['linux_root']).parts))
    argv = [prior['root_spec']['wine_wrapper']['path'], wine_argument]
    require(contract['execution_argv'] == argv and contract['execution_cwd'] == str(ROOT),
            'Producer actual Source launch CLI must equal the unchanged Wine mapping')
    retry = template['ui_retry']
    ui_formal_ref = source_review(args.ui_formal, args.ui_formal_sha256, retry['review_pointers'],
                                  runner_ref, argv, prior['actual_inputs']['UI_expected_own_source_keys'])
    saved_row = retry['saved_review_source']
    saved_argv = saved_row['argv']
    require(saved_argv == [prior['root_spec']['linux_python_entry'], saved_ref['path'],
                           '--spec', template['ui_retry_output_paths']['saved_review_input'],
                           '--output', template['ui_retry_output_paths']['saved_review_receipt']],
            'Saved exact planned Source CLI changed')
    saved_formal_ref = source_review(args.saved_formal, args.saved_formal_sha256,
                                     saved_row['review_pointers'], saved_ref, saved_argv)
    expected_ui_outputs = {key: value for key, value in template['ui_retry_output_paths'].items()
                           if key in ('wine_ui', 'wine_ui_console', 'wine_ui_exit_code')
                           or key.startswith(('ui_saved_output_', 'ui_optional_output_'))}
    require(contract['replacement_output_paths'] == expected_ui_outputs,
            'Producer output paths must equal the exact reviewed identity projection')
    expected_native = contract['fresh_evidence_directories']
    require(expected_native == ['/workspace/.compat/full095-ui-native-identity-retry-v1'],
            'Fresh native namespace differs')
    require(all(not Path(value).exists() for value in template['ui_retry_output_paths'].values())
            and all(not Path(value).exists() for value in expected_native),
            'An actual identity output already exists: preserve it and diagnose')

    prelaunch_template = json.loads((PRODUCER / 'root-prelaunch-template-identity-retry095.json').read_bytes())
    if args.prelaunch is None:
        prelaunch = deepcopy(prelaunch_template)
        prelaunch.update(status='SOURCE_APPROVED_ACTUAL_ROOT_UI_IDENTITY_RETRY_PRELAUNCH_RUNTIME_UNRUN',
                         source_gate_passed=True, runtime_pass=False, outputs_absent=True,
                         recorded_at=datetime.now(timezone.utc).isoformat(),
                         formal_source_review=ui_formal_ref,
                         second_UI_loss_capsule_Root_binding_required=loss_ref,
                         actual_Root_epoch_binding=template['prior_ui_retry']['binding'],
                         final_manifest=manifest_ref, actual_source_files_verified=735,
                         actual_assertions_in_source=assertions, target_execution_performed=False,
                         actual_section95_already_completed=True,
                         actual95_receipt=file_ref(ROOT / 'verification/sections/095.json'),
                         actual95_archive_closure=file_ref('/workspace/.continuation/section095-archived-working-tree-closure.json'),
                         native_Windows_game_chat_verified=False,
                         root_source_assembler=file_ref(Path(__file__).resolve()),
                         next_section_development_paused=True)
    else:
        prelaunch_ref = file_ref(args.prelaunch)
        require(prelaunch_ref['sha256'] == args.prelaunch_sha256, 'Existing actual prelaunch SHA differs')
        prelaunch = bound_json(prelaunch_ref)
    require(prelaunch['source_gate_passed'] is True and prelaunch['runtime_pass'] is False
            and prelaunch['outputs_absent'] is True and prelaunch['runner'] == runner_ref
            and prelaunch['actual_argv'] == argv and prelaunch['cwd'] == str(ROOT)
            and prelaunch['formal_source_review'] == ui_formal_ref
            and prelaunch['source_contract'] == contract_ref
            and prelaunch['source_guard'] == guard_ref
            and prelaunch['second_UI_loss_capsule_Root_binding_required'] == loss_ref
            and prelaunch['actual_Root_epoch_binding'] == template['prior_ui_retry']['binding']
            and prelaunch['actual_source_files_verified'] == 735
            and prelaunch['actual_assertions_in_source'] == 907
            and prelaunch['target_execution_performed'] is False,
            'Actual prelaunch must bind the existing b83 epoch without a new binding SHA cycle')
    require(datetime.fromisoformat(prelaunch['recorded_at']) <= datetime.now(timezone.utc),
            'Actual Root prelaunch timestamp may not be authored in the future')

    ui = deepcopy(prior['root_spec']['ui'])
    ui.update(runner=runner_ref, receipt_path=expected_ui_outputs['wine_ui'],
              console_log_path=expected_ui_outputs['wine_ui_console'],
              required_saved_outputs=[{'kind': 'native-evidence' if i < 2 else 'screenshot',
                                      'path': expected_ui_outputs['ui_saved_output_' + str(i)]}
                                     for i in range(6)],
              optional_output_paths=[expected_ui_outputs['ui_optional_output_' + str(i)] for i in range(3)],
              fresh_evidence_directories=expected_native)
    ui['execution_contract'].update(argv=argv, source_review=ui_formal_ref,
        review_pointers={key: retry['review_pointers'][key]
                         for key in ('source_pass', 'runtime_pass', 'runner_sha256', 'argv')})
    ui['own_source_scope'].update(source_review=ui_formal_ref,
        review_pointers={key: retry['review_pointers'][key]
                         for key in ('source_pass', 'runtime_pass', 'runner_sha256', 'source_keys')})
    require(contract['required_saved_outputs'] == ui['required_saved_outputs']
            and contract['optional_output_paths'] == ui['optional_output_paths'],
            'The required native/screenshot/optional outputs changed kind, order or path')
    retry.update(manifest=manifest_ref, source_contract=contract_ref, runner=runner_ref,
                 source_review=ui_formal_ref, ui=ui)
    saved_row.update(runner=saved_ref, source_review=saved_formal_ref)
    template['status'] = 'ROOT_BOUND_ACTUAL_FULL095_UI_IDENTITY_RETRY_SOURCE_INPUTS'
    require(maintained_hashes() == maintained, 'Source drifted during metadata assembly')
    # No writes occur until every actual Source/metadata check succeeds.
    if args.prelaunch is None:
        prelaunch_ref = exclusive_json(PRELAUNCH, prelaunch)
    template['root_ui_prelaunch'] = prelaunch_ref
    spec_ref = exclusive_json(args.output, template)
    print(json.dumps({'status': 'ACTUAL_ROOT_IDENTITY_SPEC_ASSEMBLED_SOURCE_ONLY_RUNTIME_PENDING',
                      'actual_source_spec': spec_ref, 'actual_prelaunch': prelaunch_ref,
                      'source_files_verified': 735, 'own_UI_source_keys': 129,
                      'actual_runtime_executions': 0, 'actual_UI_primary_exit_code': None,
                      'available_checks_passed': False, 'next_section_development_paused': True,
                      'commit_or_push_performed': False}))

if __name__ == '__main__':
    main()
