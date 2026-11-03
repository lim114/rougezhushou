"""Prepare-time argument/source/fixture checks; no test module or GUI execution."""
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from full290_runtime_common import (FREEZE, PYTHON, preparation_pins, sha,
                                    runner_api_snapshot, supplemental_public_inputs, write_new)
import prepare_full290_window as preparation
import run_full290_orchestration as orchestration
from supplementary290_launcher import SCRIPTS


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


checks = []
pins = preparation_pins()
for name in pins:
    compile((ROOT / name).read_bytes(), str(ROOT / name), 'exec')
check(len(pins) == 9, 'nine_compileable_exact_runtime_controllers')
check(not FREEZE.exists(), 'root_freeze_not_written_by_preparation')
preparation.preserved()
check(True, '862_assertions_552_maintry_case_generators_current30_29_preserved')
fake = Path('C:/full290-static-argv-never-created')
check(not fake.exists(), 'argv_only_namespace_not_created')
rows = orchestration.commands(fake)
check([name for name, _ in rows] == ['offline', 'legacy', 'current30', 'current29'], 'original_four_complete_order')
for name, argv in rows:
    check(argv[:4] == [str(PYTHON), '-X', 'utf8', str(HERE / 'legacy/supervisor275.py')], name + '_original_supervisor')
    check(argv[4:9] == ['--status', str(fake / name / 'supervisor.json'), '--timeout', '1800', '--'], name + '_owned_status_and_bound_timeout')
    child = argv[9:]
    if name == 'offline':
        expected = [str(PYTHON), '-X', 'utf8', str(HERE / 'legacy/offline290_launcher.py'),
                    '--root', str(ROOT), '--out', str(fake / name / 'actual/windows-offline.json')]
    else:
        expected = [str(PYTHON), '-X', 'utf8', str(HERE / ('legacy' if name == 'legacy' else 'current') / 'launcher275.py'),
                    '--root', str(ROOT), '--out', str(fake / name / 'actual'), '--mode', name]
    check(child == expected, name + '_exact_canonical_arguments')
maps = {}
for label in ('legacy', 'current'):
    folder = HERE / label
    draft = json.loads((folder / 'draft290.json').read_bytes())
    activation = json.loads((folder / 'activation275.json').read_bytes())
    check(activation == {'status': 'INACTIVE_DRAFT', 'binding_ready': False, 'actual_section': 290, 'runtime_executed': False}, label + '_inactive_not_run')
    check(draft['prepare_script_sha256'] == sha(HERE / 'prepare_full290_window.py'), label + '_prepare_tool_pin_matches')
    check(preparation.tools(folder) == draft['tools_sha256'], label + '_all_draft_tool_bytes')
    maps[label] = {'tool_count': len(draft['tools_sha256']), 'draft_sha256': sha(folder / 'draft290.json')}
proof_rows = json.loads((HERE / 'legacy/expected-map125.json').read_bytes())['proof_files']
check(len(proof_rows) == 7, 'seven_original_proofs_declared')
for label, row in proof_rows.items():
    path = HERE / 'legacy' / row['path']
    check(path.stat().st_size == row['bytes'] and sha(path) == row['sha256'], 'original_proof_' + label)
    check(json.loads((HERE / 'legacy/draft290.json').read_bytes())['tools_sha256'].get(row['path']) == row['sha256'], 'proof_bound_before_activation_' + label)
check(sha(HERE / 'offline290_launcher.py') == sha(HERE / 'legacy/offline290_launcher.py'), 'offline_launcher_already_in_inactive_tool_map')
snapshot = runner_api_snapshot()
previous = json.loads((ROOT / 'verification/full-290/source-freeze.json').read_bytes())
check(set(previous['selectors']) <= set(snapshot['selectors']), 'all_attempt1_430_selectors_retained')
check(set(previous['source_sha256']) <= set(snapshot['source_sha256']), 'all_attempt1_1221_source_paths_retained')
added = [name for name in snapshot['selectors'] if name not in previous['selectors']]
check(not added, 'repair_uses_exact_same_430_selector_list')
check(snapshot['selectors'] == previous['selectors'], 'same_full_ordered_selector_union_no_scope_change')
check(set(snapshot['source_sha256']) == set(previous['source_sha256']), 'same_1221_maintained_source_paths')
missing_modules = []
for selector in snapshot['selectors']:
    # Preserve original method selectors too. Resolve the longest real module
    # prefix statically; do not replace them by whole modules or import tests.
    parts = selector.split('.')
    located = False
    for count in range(len(parts), 0, -1):
        path = ROOT.joinpath(*parts[:count]).with_suffix('.py')
        if path.is_file():
            body = ast.parse(path.read_bytes()).body
            located = True
            for attribute in parts[count:]:
                matches = [node for node in body if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == attribute]
                if len(matches) != 1:
                    located = False
                    break
                body = matches[0].body
            break
    if not located:
        missing_modules.append(selector)
check(not missing_modules, 'all_selector_module_sources_exist_without_importing_tests')
supplemental = supplemental_public_inputs()
check(len(supplemental) > 2, 'all_four_complete_public_packets_and_two_prior_sources_present')
for mode, name in SCRIPTS.items():
    check(name in snapshot['source_sha256'], mode + '_canonical_script_in_maintained_freeze_scope')
    compile((ROOT / name).read_bytes(), str(ROOT / name), 'exec')
check(sha(ROOT / SCRIPTS['p3_290']) == 'f2e9586d9847c12dd4229db9a21f09eca81a46fceb0a419332d0d849c70aeb31', 'root_declared_final_290_native_script_matches')
check(snapshot == runner_api_snapshot() and supplemental == supplemental_public_inputs(), 'public_api_and_supplemental_inputs_stable_during_preflight')
check('timeout=1890' in (HERE / 'run_full290_orchestration.py').read_text(encoding='utf8'), 'outer_wait_1890')
supervisor = (HERE / 'legacy/supervisor275.py').read_text(encoding='utf8')
check('0<args.timeout<=1800' in supervisor and '0<args.timeout<=1200' not in supervisor, 'new_owned_supervisor_allows1800')
check("'--timeout', '1800'" in (HERE / 'run_p3_supplementary_windows_290.py').read_text(encoding='utf8'), 'five_supplementary_timeouts1800')
check("'--verbosity', '2'" in (HERE / 'offline290_launcher.py').read_text(encoding='utf8'), 'offline_verbosity2_explicit')
check('source-freeze-repair.json' in str(FREEZE), 'repair_freeze_path_only')
check('execution-attempt2' in (HERE / 'archive_full290_outputs.py').read_text(encoding='utf8'), 'main_attempt2_archive_only')
check('p3-supplementary-attempt2' in (HERE / 'archive_p3_supplementary_290.py').read_text(encoding='utf8'), 'supplementary_attempt2_archive_only')
adaptation = json.loads((HERE / 'controller-adaptation-290.json').read_bytes())
check(sha(ROOT / 'verification/full-290/source-freeze.json') == adaptation['prior_actual_attempt_freeze_sha256'], 'original_attempt1_freeze_unchanged')
check(all(sha(ROOT / path) == expected for path, expected in adaptation['prior_archives_unchanged'].items()), 'both_original_attempt1_archives_unchanged')
record = {
    'kind': 'FULL290_ATTEMPT2_STATIC_PREPARATION_NOT_FULL_VALIDATION', 'passed': True,
    'checks': checks, 'check_count': len(checks), 'preparation_tools_sha256': pins,
    'inactive_tool_maps': maps, 'original_attempt1_freeze_sha256': sha(ROOT / 'verification/full-290/source-freeze.json'),
    'previous_selector_count': len(previous['selectors']), 'current_selector_count': len(snapshot['selectors']),
    'previous_source_count': len(previous['source_sha256']), 'current_source_count': len(snapshot['source_sha256']),
    'current_snapshot_not_final_freeze': snapshot, 'supplemental_public_inputs_sha256': supplemental,
    'new_selectors': added, 'supplemental_public_input_count': len(supplemental),
    'canonical_supplementary_windows': SCRIPTS, 'all_original_862_552_and_current30_29_preserved': True,
    'root_freeze_produced': False, 'fixture_or_GUI_or_full_suite_executed': False,
    'game_or_chat_or_private_state_used': False, 'available_full_tests_passed_claimed': False,
}
write_new(HERE / 'orchestration-preparation-check-290-final.json', record)
print(json.dumps({k: v for k, v in record.items() if k not in ('checks', 'current_snapshot_not_final_freeze', 'supplemental_public_inputs_sha256', 'preparation_tools_sha256')}, ensure_ascii=False, indent=2))
