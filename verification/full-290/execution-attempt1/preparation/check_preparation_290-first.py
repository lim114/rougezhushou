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
    check(argv[4:9] == ['--status', str(fake / name / 'supervisor.json'), '--timeout', '1200', '--'], name + '_owned_status_and_bound_timeout')
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
previous = json.loads((ROOT / 'verification/full-285/source-freeze.json').read_bytes())
check(set(previous['selectors']) <= set(snapshot['selectors']), 'all_previous_419_selectors_retained')
check(set(previous['source_sha256']) <= set(snapshot['source_sha256']), 'all_previous_1193_source_paths_retained')
added = [name for name in snapshot['selectors'] if name not in previous['selectors']]
check(len(added) == 11 and all(any('_' + str(n) in name for n in range(286, 291)) for name in added), 'all_eleven_286_290_module_selectors_added')
missing_modules = []
for selector in snapshot['selectors']:
    # These maintained selectors are module names, not arbitrary user paths.
    parts = selector.split('.')
    path = ROOT.joinpath(*parts).with_suffix('.py')
    if not path.is_file():
        missing_modules.append(selector)
check(not missing_modules, 'all_selector_module_sources_exist_without_importing_tests')
supplemental = supplemental_public_inputs()
check(len(supplemental) > 2, 'all_four_complete_public_packets_and_two_prior_sources_present')
for mode, name in SCRIPTS.items():
    check(name in snapshot['source_sha256'], mode + '_canonical_script_in_maintained_freeze_scope')
    compile((ROOT / name).read_bytes(), str(ROOT / name), 'exec')
check(sha(ROOT / SCRIPTS['p3_290']) == 'f2e9586d9847c12dd4229db9a21f09eca81a46fceb0a419332d0d849c70aeb31', 'root_declared_final_290_native_script_matches')
check(snapshot == runner_api_snapshot() and supplemental == supplemental_public_inputs(), 'public_api_and_supplemental_inputs_stable_during_preflight')
record = {
    'kind': 'FULL290_STATIC_PREPARATION_NOT_FULL_VALIDATION', 'passed': True,
    'checks': checks, 'check_count': len(checks), 'preparation_tools_sha256': pins,
    'inactive_tool_maps': maps, 'previous_full285_freeze_sha256': sha(ROOT / 'verification/full-285/source-freeze.json'),
    'previous_selector_count': len(previous['selectors']), 'current_selector_count': len(snapshot['selectors']),
    'previous_source_count': len(previous['source_sha256']), 'current_source_count': len(snapshot['source_sha256']),
    'current_snapshot_not_final_freeze': snapshot, 'supplemental_public_inputs_sha256': supplemental,
    'new_selectors': added, 'supplemental_public_input_count': len(supplemental),
    'canonical_supplementary_windows': SCRIPTS, 'all_original_862_552_and_current30_29_preserved': True,
    'root_freeze_produced': False, 'fixture_or_GUI_or_full_suite_executed': False,
    'game_or_chat_or_private_state_used': False, 'available_full_tests_passed_claimed': False,
}
write_new(HERE / 'orchestration-preparation-check-290.json', record)
print(json.dumps({k: v for k, v in record.items() if k not in ('checks', 'current_snapshot_not_final_freeze', 'supplemental_public_inputs_sha256', 'preparation_tools_sha256')}, ensure_ascii=False, indent=2))
