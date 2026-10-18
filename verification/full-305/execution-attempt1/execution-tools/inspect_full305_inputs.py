"""Read-only pre-305 inventory. Never import tests/Qt or declare a final freeze."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast
import importlib.metadata
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def pin(path):
    raw = path.read_bytes()
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def json_file(name): return json.loads((ROOT / name).read_bytes())


def assign_value(relative, name):
    tree = ast.parse((ROOT / relative).read_bytes())
    matches = [node.value for node in tree.body if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    if len(matches) != 1: raise ValueError('One literal selector assignment required: ' + name)
    return ast.literal_eval(matches[0])


def maintained_api_snapshot():
    path = ROOT / 'scripts/verify_full_available.py'; raw = path.read_bytes()
    # This existing maintained body defines stdlib classes/functions only.
    # main/AvailableResult construction/test-loader/Qt are deliberately not called.
    api = {'__file__': str(path), '__name__': '_read_only305_maintained_api'}
    exec(compile(raw, str(path), 'exec'), api)
    new = list(assign_value('scripts/verify_full_available.py', 'NEW_MODULES'))
    cloud = list(assign_value('scripts/verify_cloud.py', 'MODULES'))
    old = json_file('CORE_0.70_VERIFICATION.json')['test_modules']
    selectors = list(dict.fromkeys(old + new + cloud))
    sources = api['source_hashes']()
    assert path.read_bytes() == raw
    return {'selector_inputs': {'historical': old, 'NEW_MODULES': new, 'cloud_MODULES': cloud},
            'selectors': selectors, 'source_sha256': sources,
            'maintained_runner': pin(path), 'cloud_runner': pin(ROOT / 'scripts/verify_cloud.py'),
            'main_or_test_loader_or_Qt_called': False}


def inspect_environment():
    record = {'sys_platform': sys.platform, 'sys_executable': sys.executable, 'sys_version': sys.version,
              'windows_version_raw': list(sys.getwindowsversion()) if sys.platform == 'win32' else None,
              'command_paths': {name: shutil.which(name) for name in ('wsl.exe', 'wine', 'wine64', 'bash', 'docker')},
              'packages': {}, 'tests_Qt_or_gui_launched': False}
    for name in ('PySide6', 'pywin32', 'Pillow', 'numpy'):
        try: record['packages'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: record['packages'][name] = None
    wsl = record['command_paths']['wsl.exe']
    if wsl:
        argv = [wsl, '--list', '--quiet']
        try:
            process = subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, timeout=15, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            stdout, stderr = process.stdout, process.stderr
            def decode(raw):
                return raw.decode('utf-16-le' if b'\0' in raw else 'utf8', errors='replace').lstrip('\ufeff')
            (HERE / 'wsl-list.stdout.bin').write_bytes(stdout); (HERE / 'wsl-list.stderr.bin').write_bytes(stderr)
            record['wsl_list_actual'] = {'argv': argv, 'exit_code': process.returncode,
                 'stdout': decode(stdout), 'stderr': decode(stderr), 'timed_out': False,
                 'stdout_raw': pin(HERE / 'wsl-list.stdout.bin'), 'stderr_raw': pin(HERE / 'wsl-list.stderr.bin')}
        except subprocess.TimeoutExpired as error:
            record['wsl_list_actual'] = {'argv': argv, 'exit_code': None, 'timed_out': True,
                                        'stdout_hex': (error.stdout or b'').hex(), 'stderr_hex': (error.stderr or b'').hex()}
    record['symlink_prerequisite_created_by_preparation'] = False
    record['symlink_boundary'] = '290 actual1314 is historical. 305 AvailableResult must run its original fresh same-kind probe and preserve actual exceptions; no privilege/config change or link substitute.'
    return record


def legacy_static():
    base = ROOT / 'verification/full-290/legacy-retry-attempt4/executed-legacy-bundle'
    path = base / 'window.py'; source = path.read_text(encoding='utf8'); tree = ast.parse(source)
    asserts = sorted((node for node in ast.walk(tree) if isinstance(node, ast.Assert)), key=lambda node: (node.lineno, node.col_offset))
    body = [node for node in tree.body if isinstance(node, ast.Try) and sum(isinstance(item, ast.Assert) for item in ast.walk(node)) == 552]
    assert len(body) == 1
    segment = ast.get_source_segment(source, body[0]).encode('utf8')
    ledger = json.loads((base / 'expected-map125.json').read_bytes())
    static = json.loads((base / 'static-preservation.json').read_bytes())
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    case_checks = {}
    for name, expected in static['case_function_raw_sha256'].items():
        raw = ast.get_source_segment(source, functions[name]).replace('\r\n', '\n').encode()
        case_checks[name] = sha256(raw).hexdigest() == expected
    return {'basis_window': {'path': path.relative_to(ROOT).as_posix(), **pin(path)},
            'assert_AST_count': len(asserts), 'main_try_asserts': 552,
            'main_try_sha256': sha256(segment).hexdigest(),
            'same_original_552_physical_body': sha256(segment).hexdigest() == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922',
            'original_case_functions_match_recorded_raw_hashes': case_checks,
            'exact_bridge_indices': [row['literal_index'] for row in ledger['rows']],
            'optional_platform_platform_calls_in_fixture': source.count('platform.platform()'),
            'original_typed_auditor': {'path': (base / 'audit_full261_saved_readback.py').relative_to(ROOT).as_posix(), **pin(base / 'audit_full261_saved_readback.py')},
            'observer_function_present': '_install_narrow_observers100' in functions,
            'source_code_only_no_fixture_executed': True}


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    if (HERE / 'PLAN.json').exists(): raise FileExistsError('Preserve the first preparation plan.')
    historical = json_file('verification/full-290/summary.json')
    old_freeze = json_file('verification/full-290/source-freeze-final-A3.json')
    actual = maintained_api_snapshot()
    current_tests = {name for name in actual['source_sha256'] if name.startswith('tests/test_') and name.endswith('.py')}
    new_tests = sorted(current_tests - set(old_freeze['source_sha256']))
    new_modules = ['tests.' + Path(name).stem for name in new_tests]
    missing_modules = [name for name in new_modules if name not in actual['selectors']]
    proposed = list(dict.fromkeys(actual['selectors'] + missing_modules))
    supplement_scripts = sorted(name for name in actual['source_sha256']
                                if name.startswith('scripts/verify_') and '_window_' in name and name.endswith('.py')
                                and 286 <= int(name.rsplit('_', 1)[1][:-3]) <= 304)
    available_originals = [
        '.cache/p3-full290-final-A3-prep/final_common.py', '.cache/p3-full290-final-A3-prep/run_segment.py',
        '.cache/p3-full290-final-A3-prep/run_readback.py', '.cache/p3-full290-final-A3-prep/archive_segment.py',
        '.cache/p3-full290-final-A3-prep/supervisor3690.py',
        '.cache/p3-full290-repair-prep/run_full290_orchestration.py',
        '.cache/p3-full290-repair-prep/full290_runtime_common.py',
        '.cache/p3-full290-prep/prepare_full290_window.py',
        '.cache/p3-full290-repair-prep/run_p3_supplementary_windows_290.py',
        '.cache/p3-full290-repair-prep/supplementary290_launcher.py',
        'verification/full-290/execution-attempt2/executed-tools/current/window.py',
        'verification/full-290/execution-attempt2/executed-tools/current/window29.py',
    ]
    tools = {name: pin(ROOT / name) if (ROOT / name).is_file() else None for name in available_originals}
    environment = inspect_environment(); legacy = legacy_static()
    snapshot_path = HERE / 'current-maintained-scope-snapshot.json'
    snapshot_path.write_bytes(encoded(actual))
    (HERE / 'environment-inventory.json').write_bytes(encoded(environment))
    (HERE / 'legacy-static-preservation.json').write_bytes(encoded(legacy))
    plan = {'section': 305, 'kind': 'READ_ONLY_PERIODIC_FULL_VALIDATION_PREPARATION_NOT_ACTIVATED_OR_PASSED',
        'at_utc': datetime.now(timezone.utc).isoformat(), 'functional_scope_305_pending': True,
        'source_freeze_declared': False, 'tests_Qt_windows_or_full_execution_started': False,
        'business_private_docs_Git_or_old_receipts_modified': False,
        'snapshot': {'path': snapshot_path.relative_to(ROOT).as_posix(), **pin(snapshot_path)},
        'current_maintained_selector_count': len(actual['selectors']), 'current_maintained_source_file_count': len(actual['source_sha256']),
        'current_selector_union_equals_290_order': actual['selectors'] == old_freeze['selectors'],
        'new_public_test_files_since290': new_tests, 'new_module_names_since290': new_modules,
        'missing_new_modules_from_current_maintained_union': missing_modules,
        'proposed_append_only_selector_union_before305_function': proposed,
        'proposed_selector_count_before305_function': len(proposed),
        'selectors_are_not_expanded_test_case_count': True,
        'selector_blocker': 'Root must add actual291-304 modules and future305 modules to the maintained selector API before the final freeze. No module/test loader was called during this audit.',
        'historical290_summary': {'path': 'verification/full-290/summary.json', **pin(ROOT / 'verification/full-290/summary.json'),
             'available_checks_passed_then': historical['available_checks_passed'], 'single_execution_all_green_then': historical['single_execution_all_green'],
             'complete_repository_validation_then': historical['complete_repository_validation'],
             'scope': {key: historical[key] for key in ('maintained_selectors', 'source_files', 'supplemental_public_input_files', 'legacy_native_sources', 'legacy_additional_sources')},
             'offline_then': historical['offline_windows'], 'legacy_then': historical['legacy_window'],
             'current_then': historical['current_window'], 'component_freezes': historical['component_freezes'],
             'historical_reuse_does_not_establish305_pass': True},
        'components_to_execute_fresh_after305_promotion': [
            {'mode': 'offline', 'entry': 'scripts/verify_full_available.py --output <owned-temp>/offline/actual/windows-offline.json --verbosity 2',
             'environment': 'QT_QPA_PLATFORM=offscreen; use exact .venv Python and maintained AvailableResult/Qt cleanup; do not globally mock network/subprocess APIs used by tests.',
             'scope': 'Complete old ordered selector set plus all maintained post290 additions including305; actual IDs/failures/skips/unavailable/JSON and actual child/supervisor exits.',
             'deadline_basis_seconds': {'owned_supervisor': 3600, 'outer_observer': 3690}, 'deadlines_not_executed_or_guaranteed': True},
            {'mode': 'legacy', 'entry': '<new305-bound-bundle>/launcher275.py --root <ROOT> --out <owned-temp>/legacy/actual --mode legacy',
             'scope': 'Original862 assert AST/order and552 maintry physical bytes/generators/observers;52 actual typed states/4283 records/156 text requests/42 projections/exact10 bridges/26 real empty traces.',
             'deadline_basis_seconds': {'internal_watchdog': 3600, 'owned_supervisor': 3690, 'outer_observer': 3780},
             'followup': 'After actual terminal success, unchanged original audit_full261_saved_readback.py with real container/bundle/new305 freeze in separate owned job120/outer210; inspect actual four PNGs.'},
            {'mode': 'current30', 'entry': '<new305-current-bundle>/launcher275.py --root <ROOT> --out <owned-temp>/current30/actual --mode current30',
             'scope': 'Execute full original30; retain real failure/exception if symlink privilege1314. Do not convert the raw failure to PASS or replace with hardlink/junction/plainfile.'},
            {'mode': 'current29', 'entry': '<new305-current-bundle>/launcher275.py --root <ROOT> --out <owned-temp>/current29/actual --mode current29',
             'scope': 'Execute unchanged independent29 original workflows even when current30 fails its genuine symlink prerequisite.'},
            {'mode': 'p3_supplementary', 'mandatory_prior_full_scripts': [name for name in supplement_scripts if int(name.rsplit('_',1)[1][:-3]) <= 290],
             'post290_native_scripts_for_root_scope_review': [name for name in supplement_scripts if int(name.rsplit('_',1)[1][:-3]) > 290],
             'scope': 'Never substitute recent section receipts for fresh305 scope; retain prior286-290 five native ranges. Bind meaningful new291-305 UI flows explicitly; script assertions and original counts cannot be silently discarded.',
             'entry': '<new305-supplementary-launcher> canonical script per owned serial process with source before/after and Qt cleanup.'}],
        'native_script_count_available_through304': len(supplement_scripts),
        'existing_tools_fresh_pins_for_reuse': tools,
        'legacy_static_preservation': {'path': (HERE / 'legacy-static-preservation.json').relative_to(ROOT).as_posix(), **pin(HERE / 'legacy-static-preservation.json')},
        'environment': {'path': (HERE / 'environment-inventory.json').relative_to(ROOT).as_posix(), **pin(HERE / 'environment-inventory.json')},
        'known_rebinding_blockers_and_required_adaptations': [
            'Do not execute final_common290 unchanged: it hard-pins oldA2, exactly two old nonproduction changes/1219 other files, old430/42/86 and the historical15-test receipt.305 needs new current input declaration, not weakened old guard.',
            'Use actually successful290 legacy4 bundle, not275/290 A2 window with internal1200 watchdog or retry3 platform.platform metadata. Keep non-WMI native metadata distinction and all6 watchdog3600 placements; do not claim WMI caused previous crash.',
            'Current original30/29 must get full new source freeze, not the legacy map which substitutes offline_scope_retirement forCORE. Preserve separate native map and original extra helper/additional inputs.',
            'Current source_hashes excludes research HTML/PNG and historic public input counterparts: add exact public inputs from actual source-manifests/native bound_files/required historical replay lists, plus actual local/public dualguard inputs where truly consumed. Do not put.cache in standard public source map.',
            'Old294 canonical source_contract demands DATA hash equal original58-point build output63ec..., while current DATA dc43... has107 points. Fresh current execution would stop on that known preflight. Prepare a separately reviewed305 copy preserving every old assertion and source18-point identities, with new frozen DATA identity plus full old58 record-preservation proof; do not erase old294 source/receipt, trim coverage, or call old receipt305PASS.',
            'Several canonical supplementary scripts bind exact section paths/old placeholders/source pins. Audit their actual code/selected inputs and adapt only proven stale fixture assumptions, preserving raw failures and scope. Do not blanket monkeypatch sources, results, oldassertions, game APIs or platform.',
            'Root must run serial once; retained Popen/owned Windows Job + genuine child/supervisor/exit/closure + no-live cleanup is authority. A controller0 that only says terminal is not PASS; PID alone is not ownership. Launch and actualQt PIDs can differ.',
            'Freeze only after305 implementation and all maintenance/promoted scripts are final; no source/test/doc/index change until every active ownedjob is terminal/closed. Archive exact executed tools and failed attempts; no dependency clone/private contents copied wholesale.'
        ],
        'final_freeze_required_fields': ['section305', 'root_declared', 'actual_parent_commit', 'maintained_runner_sha256',
            'cloud_selector_api_sha256', 'ordered_complete_selectors', 'current_source_sha256', 'supplemental_public_input_sha256',
            'legacy_native_source_sha256', 'legacy_additional_source_sha256', 'current_full_source_sha256',
            'canonical_native_scripts_and_selected_input_union', 'explicit_local_public_input_bindings_if_consumed',
            'all_preparation_controller_supervisor_bound_bundle_and_auditor_pins'],
        'final_acceptance': 'Require actual complete offline JSON/exit0/noF-E/source stable; complete legacy0+original typed0+fresh52 data; genuine current30 result and independent29 actual; all explicitly bound native supplemental results/visual review; all same final305 production source. Remain complete_repository_validation:false for unavailable original/private/Linux/game/chat scopes.',
        'platform_boundary': 'Native Windows Qt is required for Windows GUI; offline offscreen is separate; historical wine labels remain raw labels, not actual Linux/Wine or historical original Windows certification.',
        'no_current_usage_percentage_inferred': True,
        'root_next_action': 'Fix maintained selector coverage; select and finish305 useful function; review new305 controllers/bindings and old-native stale assumption repairs; then root explicitly declares/activates/runs the complete serial scope.'}
    (HERE / 'PLAN.json').write_bytes(encoded(plan))
    print(json.dumps({'PLAN': str(HERE / 'PLAN.json'), **pin(HERE / 'PLAN.json'),
        'observed_current_selectors': len(actual['selectors']), 'new_public_test_modules': len(new_modules),
        'missing_maintained_modules': len(missing_modules), 'proposed_append_only_selectors_before305': len(proposed),
        'current_source_files': len(actual['source_sha256']), 'native_scripts_available': len(supplement_scripts),
        'legacy_assert_AST': legacy['assert_AST_count'], 'legacy552_unchanged': legacy['same_original_552_physical_body'],
        'WSL_actual_exit': environment.get('wsl_list_actual', {}).get('exit_code'), 'tests_Qt_or_windows_executed': False}, ensure_ascii=False))


if __name__ == '__main__': main()
