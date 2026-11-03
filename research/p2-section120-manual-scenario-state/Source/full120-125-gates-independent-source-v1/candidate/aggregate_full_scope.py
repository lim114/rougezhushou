"""Root-only actual receipt aggregation, without project reexecution or native decoding.

This new aggregate is not a metadata-only transport of the specialized115 finalizer.
It closes only the supplied current available full regression. It does not certify
the five features, section completion, publication, P2, native Windows, game or chat.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

BASE = Path('/workspace/.continuation')
CORE = 'CORE_0.70_VERIFICATION.json'
CORE_SHA = 'a75d9497ce34f68de787e3ba99704741f2c873c2c5fa9b5de01e6620b1f00f89'
LINUX_SOURCE_FUNCTION_AST_SHA = '5c4254d500a1102352522613aa39d8288fefe7a0ae9dae5894d2b21c99bd14d6'
CAPABILITY_IDS = frozenset((
    'tests.test_account_cache_093.AccountCache093Tests.test_dangling_symlink_file_not_found_is_not_genuinely_absent',
    'tests.test_account_cache_093.AccountCache093Tests.test_symlink_to_damaged_file_retains_link_and_target_bytes',
    'tests.test_run_persistence_099.RunPersistenceTests.test_actual_dangling_symlink_is_not_missing_until_explicit_manual_reset',
))
PNG_NAMES = ('wine-sown-tile-control-100.png', 'wine-movement-reference-100.png',
             'wine-medical-trait-100.png', 'wine-window-100.png')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(value, reason):
    if not value:
        raise AssertionError(reason)

def nonnegative(value, name):
    require(type(value) is int and value >= 0, 'Genuine nonnegative integer required: ' + name)
    return value

def public_path(value, *, directory=False):
    path = Path(value)
    require(path.is_absolute(), 'Absolute public workspace evidence path required')
    require(path.is_relative_to(BASE), 'Evidence must remain under public .continuation')
    require('..' not in path.parts, 'Parent traversal forbidden')
    for item in (path, *path.parents):
        require(not item.is_symlink(), 'Symlink evidence path forbidden: ' + str(item))
    require(path.is_dir() if directory else path.is_file(), 'Missing actual evidence: ' + str(path))
    return path

def normalized_reference_path(value):
    require(type(value) is str, 'Reference path must be text')
    if value.startswith('Z:\\workspace\\'):
        value = '/' + value[3:].replace('\\', '/')
    return str(public_path(value))

def checked_ref(reference, expected):
    path = public_path(expected)
    require(type(reference) is dict and set(reference) == {'path', 'bytes', 'sha256'}, 'Exact reference fields required')
    require(normalized_reference_path(reference['path']) == str(path), 'Actual evidence reference path differs')
    raw = path.read_bytes()
    require(type(reference['bytes']) is int and reference['bytes'] == len(raw)
            and reference['sha256'] == sha(raw), 'Actual evidence reference bytes differ')

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--section', type=int, required=True, choices=(120, 125))
    parser.add_argument('--root', default='/workspace/rougezhushou')
    for name in ('guard', 'adapters', 'capability', 'capability-primary', 'linux', 'linux-primary',
                 'wine', 'wine-primary', 'selected', 'selected-primary', 'linux-pip-log',
                 'linux-pip-primary', 'wine-pip-log', 'wine-pip-primary', 'window-supervisor',
                 'window-supervisor-primary', 'window-child-primary', 'window-out', 'saved',
                 'saved-primary', 'saved-auditor', 'visual', 'out'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    root = Path(args.root)
    require(root == Path('/workspace/rougezhushou') and root.is_dir() and not root.is_symlink(), 'Exact maintained Root required')
    output = Path(args.out)
    require(output.is_absolute() and output.is_relative_to(BASE) and not output.exists(), 'Fresh exclusive aggregate output required')
    public_path(str(output.parent), directory=True)
    require('..' not in output.parts and not output.is_symlink(), 'Unsafe output path')
    frozen = {}
    def raw(path):
        path = public_path(path)
        value = path.read_bytes()
        require(str(path) not in frozen or frozen[str(path)] == value, 'Input changed while aggregating')
        frozen[str(path)] = value
        return value
    def read(path):
        value = json.loads(raw(path))
        require(type(value) is dict, 'Object receipt required')
        return value
    def zero(path):
        require(raw(path) == b'0\n', 'Actual raw primary must be precisely0 LF: ' + str(path))
    for name in ('capability_primary','linux_primary','wine_primary','selected_primary',
                 'linux_pip_primary','wine_pip_primary','window_supervisor_primary',
                 'window_child_primary','saved_primary'):
        zero(getattr(args, name))
    raw(args.linux_pip_log); raw(args.wine_pip_log)
    guard = read(args.guard)
    require(type(guard['section']) is int and guard['section'] == args.section, 'Current typed actual section guard required')
    require(guard['source_additional_sha256'] == {CORE: CORE_SHA}, 'Unchanged exact public CORE guard required')
    require(type(guard['source_sha256']) is dict and guard['source_sha256'], 'Complete current Source map required')
    for name, digest in guard['source_sha256'].items():
        p = PurePosixPath(name)
        require(type(name) is str and not p.is_absolute() and '..' not in p.parts
                and p.parts[0] in ('rouge','tests','scripts') and p.suffix in ('.py','.json')
                and type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest), 'Unsafe Source map leaf')
    def source():
        actual = {}
        for directory in ('rouge','tests','scripts'):
            for path in sorted((root/directory).rglob('*')):
                if '__pycache__' in path.parts:
                    continue
                require(not path.is_symlink(), 'Maintained Source symlink forbidden: ' + str(path))
                if path.is_file() and path.suffix in ('.py','.json'):
                    actual[path.relative_to(root).as_posix()] = sha(path.read_bytes())
        require(actual == guard['source_sha256'], 'Actual complete Source set/bytes drifted from current guard')
        require((root/CORE).is_file() and not (root/CORE).is_symlink()
                and sha((root/CORE).read_bytes()) == CORE_SHA, 'CORE changed')
        return len(actual)
    count = source()
    # The maintained Linux runner records its exact original projection,
    # rather than the complete rouge/tests/scripts guard. Bind that projection
    # without weakening the separately checked full Source/CORE freeze.
    def linux_source():
        verifier = root / 'scripts/verify_full_available.py'
        verifier_raw = verifier.read_bytes()
        tree = ast.parse(verifier_raw)
        nodes = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name == 'source_hashes']
        require(len(nodes) == 1 and sha(ast.dump(nodes[0], include_attributes=False).encode('utf-8'))
                == LINUX_SOURCE_FUNCTION_AST_SHA,
                'Maintained Linux Source projection changed; new independent Source review required')
        files = [*root.glob('rouge/**/*.py'), *root.glob('rouge/data/**/*.json'),
                 *root.glob('tests/test_*.py'), verifier]
        projected = {}
        for path in sorted(set(files)):
            require(path.is_file() and not path.is_symlink(), 'Linux projection requires regular Source')
            name = path.relative_to(root).as_posix()
            digest = sha(path.read_bytes())
            require(guard['source_sha256'].get(name) == digest,
                    'Every exact Linux projection leaf must match the complete actual guard')
            projected[name] = digest
        require(projected, 'Nonempty actual maintained Linux Source projection required')
        return projected
    linux_receipt_source = linux_source()
    adapters = public_path(args.adapters, directory=True)
    names = (f'suite_common{args.section}.py', f'wine_capability_probe{args.section}.py',
             f'wine_full{args.section}.py', f'wine_selected{args.section}.py',
             'source-contract.json','README.md','manifest.json')
    actual_adapters = {name: sha(raw(adapters/name)) for name in names}
    require(actual_adapters == guard['adapter_source_sha256'], 'Exact sealed7 adapter bytes differ from current guard')
    capability = read(args.capability)
    checked_ref(guard['wine_capability_probe'], args.capability)
    checked_ref(guard['wine_capability_probe_primary_exit'], args.capability_primary)
    require(capability['passed'] is True and capability['source_sha256'] == actual_adapters
            and capability['source_drift'] == [] and capability['project_imports'] == capability['project_calls'] == 0
            and capability['private_state_access'] is False and capability['native_windows_integration_verified'] is False,
            'Independent actual capability receipt scope or Source differs')
    def wine_binding(value):
        require(type(value['section']) is int and value['section'] == args.section, 'Wrong Wine receipt section')
        require(value['platform'] == 'Windows' and value['wine_compatibility'] is True
                and value['native_windows_integration_verified'] is False, 'Wrong Wine/native scope')
        checked_ref(value['root_guard'], args.guard)
        checked_ref(value['independent_capability_probe'], args.capability)
        checked_ref(value['independent_capability_probe_primary_exit'], args.capability_primary)
        for key, expected in (('source_sha256', guard['source_sha256']),
                              ('source_additional_sha256', guard['source_additional_sha256']),
                              ('adapter_source_sha256', actual_adapters)):
            require(value[key] == value[key+'_after'] == expected, 'Wine before/after Source differs: ' + key)
        require(value['source_drift'] == value['source_additional_drift'] == value['adapter_source_drift'] == [], 'Wine Source drift')
        fresh = value['capability_probe']
        require(fresh['passed'] is True and fresh['identity'] == capability['identity']
                and fresh['default_temp'] == capability['default_temp']
                and fresh['admission_mode'] == capability['admission_mode']
                and fresh['source_sha256'] == actual_adapters and fresh['source_drift'] == [], 'Fresh capability differs from independent actual probe')
        require(datetime.datetime.fromisoformat(capability['checked_at']) <= datetime.datetime.fromisoformat(fresh['checked_at']), 'Fresh probe predates independent probe')
        records = value['capability_records']
        require(type(records) is list and len({item['test'] for item in records}) == len(records), 'Duplicate capability records')
        if records:
            require({item['test'] for item in records} == CAPABILITY_IDS
                    and capability['admission_mode'] == 'diagnosed_phantom_success', 'Only exact3 independently diagnosed fixtures may be skipped')
        else:
            require(capability['admission_mode'] != 'diagnosed_phantom_success', 'Diagnosed exact3 skips absent')
        for item in records:
            require(item['kind'] == 'environment_capability' and item['classification'] == 'declared_skip'
                    and item['pre_product_fixture_admission'] is True and item['actually_executed'] is False
                    and item['fixture_body_run'] is False and item['product_assertions_passed'] is False, 'Capability fixture was mislabeled as executed/pass')
        require(nonnegative(value['environment_capability_skips'], 'capability skip count') == len(records)
                and value['capability_skips_counted_passed'] == 0 and value['capability_rows_overlap_ordinary_skips'] is True,
                'Capability skip counting differs')
        require(value['historical_full095_reused_as_current_gate'] is False
                and value['historical_full095_evidence_written_by_adapter'] is False
                and value['full095_ui_retried_by_adapter'] is False and value['is_unittest_discover'] is False, 'Historical95 scope changed')
    full = {}
    for platform in ('linux','wine'):
        value = read(getattr(args, platform))
        require(value['available_checks_passed'] is True and value['source_drift'] == []
                and value['source_sha256'] == (guard['source_sha256'] if platform == 'wine' else linux_receipt_source)
                and type(value['failures']) is int and type(value['errors']) is int
                and value['failures'] == value['errors'] == 0, 'Actual full suite not passed in available scope')
        require(value['native_windows_integration_verified'] is False, 'Native Windows falsely claimed')
        if platform == 'wine':
            wine_binding(value)
        else:
            require(value['platform'] == 'Linux' and value['wine_compatibility'] is False, 'Wrong Linux receipt platform')
        summary = {key: nonnegative(value[key], key) for key in (
            'tests_run','tests_passed','historical_or_declared_skips','unavailable_records','unavailable_parent_count','failures','errors')}
        require(summary['tests_run'] > 0 and summary['tests_passed'] > 0, 'Nonempty actual full suite required')
        require(type(value['complete_repository_validation']) is bool, 'Typed completeness required')
        if summary['unavailable_records'] or (platform == 'wine' and value['environment_capability_skips']):
            require(value['complete_repository_validation'] is False, 'Unavailable/capability items cannot be complete validation')
        full[platform] = {**summary, 'complete_repository_validation': value['complete_repository_validation']}
    selected = read(args.selected)
    wine_binding(selected)
    require(selected['passed'] is True and type(selected['failures']) is int and type(selected['errors']) is int
            and selected['failures'] == selected['errors'] == 0
            and selected['passed_count_derived_from_run_minus_skipped'] is False, 'Actual selected suite scope failed')
    selected_summary = {key: nonnegative(selected[key], key) for key in ('tests_run','skipped','failures','errors')}
    require(selected_summary['tests_run'] > 0, 'Nonempty selected suite required')
    supervisor = read(args.window_supervisor)
    require(type(supervisor['after_section']) is int and supervisor['after_section'] == args.section
            and supervisor['status'] == 'completed' and supervisor['timed_out'] is False
            and type(supervisor['child_primary_exit']) is int and type(supervisor['supervisor_exit']) is int
            and supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0
            and supervisor['owned_session_closure']['no_live_owned_execution_verified'] is True
            and supervisor['global_wineserver_terminated'] is False, 'Actual owned window did not close cleanly')
    saved = read(args.saved)
    require(saved['passed'] is True and saved['workflow_complete'] is True and saved['source_drift'] == []
            and type(saved['after_section']) is int and saved['after_section'] == args.section
            and type(saved['main_source_files']) is int and saved['main_source_files'] == count
            and saved['actual_gui_checks'] == 4283 and saved['saved_states'] == 52
            and saved['selected_public_projections_equal_original_matrix_without_exceptions'] == 42
            and saved['ten_admitted_projection_comparison_copies_equal_original_matrix'] == 10
            and saved['no_live_owned_execution_verified'] is True
            and saved['native_aliases_verified_by_this_audit'] is False
            and saved['full_result_equality_to_old_gold_verified'] is False
            and saved['native_windows_game_chat_verified'] is False
            and saved['old095_complete_function_vector_measured'] is False, 'Actual Saved scope not closed')
    require(saved['source_guard_sha256'] == sha(raw(args.guard))
            and saved['supervisor_receipt_sha256'] == sha(raw(args.window_supervisor))
            and saved['audit_script_sha256'] == sha(raw(args.saved_auditor)), 'Saved receipt actual identity differs')
    for key in ('primary_exit','child_primary_exit','supervisor_exit'):
        require(type(saved[key]) is int and saved[key] == 0, 'Saved genuine integer exit required')
    visual = read(args.visual)
    require(visual['passed'] is True and visual['workflow_complete'] is True and visual['source_drift'] == []
            and visual['Root_actually_viewed_all4_PNGs'] is True
            and visual['native_windows_game_chat_verified'] is False
            and visual['PNG_all_report_text_coverage_claimed'] is False, 'Root actual visual inspection scope missing')
    require(visual['pngs'] == saved['png_hashes_checked']
            and tuple(item['file'] for item in visual['pngs']) == PNG_NAMES, 'Saved/Root actual4 PNG identities differ')
    window_out = public_path(args.window_out, directory=True)
    for item in visual['pngs']:
        image = raw(window_out/item['file'])
        require(type(item['bytes']) is int and len(image) == item['bytes']
                and sha(image) == item['sha256'] and image.startswith(b'\x89PNG\r\n\x1a\n'), 'Actual PNG bytes differ')
    source()
    require(linux_source() == linux_receipt_source, 'Exact Linux projection drifted during aggregate')
    for path, value in frozen.items():
        require(public_path(path).read_bytes() == value, 'Frozen actual receipt/source/PNG bytes changed during aggregate')
    result = {'kind': f'ROOT_ACTUAL_FULL{args.section}_AVAILABLE_REGRESSION_CLOSURE',
        'recorded_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'passed': True, 'workflow_complete': True, 'available_full_regression_closed': True,
        'after_section': args.section, 'source_files': count, 'source_drift': [], 'CORE_unchanged': True,
        **full, 'selected': selected_summary, 'selected_passed_count_derived': False,
        'linux_receipt_source_files': len(linux_receipt_source),
        'linux_receipt_source_projection_AST_sha256': LINUX_SOURCE_FUNCTION_AST_SHA,
        'linux_receipt_source_scope': 'Exact unchanged maintained source_hashes projection; complete current Source and CORE checked independently before and after all receipt reads.',
        'wine_environment_capability_skips': read(args.wine)['environment_capability_skips'],
        'wine_capability_skips_included_in_declared_skips_not_added_again': True,
        'legacy_gui_checks': saved['actual_gui_checks'], 'legacy_saved_states': saved['saved_states'],
        'legacy_projection_scope': {'unchanged_original_projections': saved['selected_public_projections_equal_original_matrix_without_exceptions'],
                                    'actual113_proved_window_metric_admissions': saved['ten_admitted_projection_comparison_copies_equal_original_matrix']},
        'actual_PNGs_Root_viewed': len(visual['pngs']), 'owned_no_live_execution': True,
        'owned_session_absence_verified': saved['owned_session_absence_verified'],
        'retained_zombies_reaped': saved['retained_zombies_reaped_by_supervisor'],
        'native_windows_game_chat_verified': False, 'legacy_alias_or_cycle_identity_verified': False,
        'old_full_result_GUI_Gold_equality_verified': False,
        'section_complete': False, 'batch_validation_closed': False,
        'specialists_and_publication_not_closed_by_this_script': True,
        'deferred095_and109_state_not_modified_by_this_script': True,
        'actual_receipt_pins': [{'path':path,'bytes':len(value),'sha256':sha(value)} for path,value in sorted(frozen.items())],
        'scope': 'Supplied current complete maintained Source/CORE and sealed adapters; actual available full/selected/dependency checks; actual bounded52 legacy GUI/Saved/Root PNG inspection. Five functional milestones, current specialist proofs, publications and125 batch stop must be bound separately by Root.'}
    with output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps({'actual_available_full_regression_closed': True, 'after_section': args.section,
                      'source_files': count, 'section_complete': False, 'batch_validation_closed': False}))

if __name__ == '__main__':
    main()
