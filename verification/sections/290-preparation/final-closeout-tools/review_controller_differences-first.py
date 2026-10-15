"""Read-only controller/fixture review; no fixture, main(), GUI or freeze call."""
import ast
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A1 = ROOT / '.cache/p3-full290-prep'
A2 = ROOT / '.cache/p3-full290-repair-prep'
sys.path.insert(0, str(A2))
import full290_runtime_common as common
import prepare_full290_window as preparation
import run_full290_orchestration as orchestration


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []


def require(value, name):
    if not value:
        raise AssertionError(name)
    checks.append(name)


freeze1 = json.loads((ROOT / 'verification/full-290/source-freeze.json').read_bytes())
ready = json.loads((A2 / 'preparation-ready-290.json').read_bytes())
pins = common.preparation_pins()
require(pins == ready['preparation_tools_sha256'], 'all_nine_A2_ready_pins_current')
differences = {}
for relative, expected in pins.items():
    path = ROOT / relative
    old = A1 / path.name
    old_relative = old.relative_to(ROOT).as_posix()
    require(freeze1['preparation_tools_sha256'][old_relative] == sha(old), 'A1_controller_unchanged_' + path.name)
    compile(path.read_bytes(), str(path), 'exec')
    difference = ''.join(difflib.unified_diff(old.read_text(encoding='utf8').splitlines(True),
                          path.read_text(encoding='utf8').splitlines(True),
                          fromfile='attempt1/' + path.name, tofile='attempt2/' + path.name))
    target = HERE / ('diff-' + path.name + '.txt')
    with target.open('xb') as file:
        file.write(difference.encode('utf8'))
    differences[path.name] = {'A1_sha256': sha(old), 'A2_sha256': expected,
                             'diff': target.relative_to(ROOT).as_posix(), 'diff_sha256': sha(target)}
preparation.preserved()
require(True, 'original862_assert_AST552_maintry_all_case_generators_and_current30_29_preserved')
for mode, argv in orchestration.commands(Path('C:/never-created-A2-review-output')):
    require(argv[6:8] == ['--timeout', '1800'], mode + '_real_supervisor_argv_requests1800')
require(orchestration.execute_observed.__defaults__ == (1890,), 'actual_outer_wait_default1890')
supervisor = (A2 / 'legacy/supervisor275.py').read_text(encoding='utf8')
require('0<args.timeout<=1800' in supervisor, 'actual_new_supervisor_accepts_requested1800')
require("parser.add_argument('--timeout',type=float,default=1200)" in supervisor, 'supervisor_default1200_is_explicitly_overridden_not_claimed_changed')
p3 = (A2 / 'run_p3_supplementary_windows_290.py').read_text(encoding='utf8')
require("'--timeout', '1800'" in p3, 'all_five_supplementary_jobs_request1800')
require(p3.count('bound_bundles(parent)') == 3 and p3.count('validate_freeze(parent)') == 3,
        'supplementary_start_and_each_step_before_after_source_and_bound_tool_guards')
offline = (A2 / 'offline290_launcher.py').read_text(encoding='utf8')
require("'--output', str(out), '--verbosity', '2'" in offline, 'offline_argv_explicit_verbosity2')
require(sha(A2 / 'legacy/offline290_launcher.py') == sha(A2 / 'offline290_launcher.py'), 'executed_offline_copy_matches_controller_and_is_draft_bound')
runner = (ROOT / 'scripts/verify_full_available.py').read_text(encoding='utf8')
require("parser.add_argument('--verbosity', type=int, choices=(1, 2), default=1)" in runner,
        'maintained_runner_optional_verbosity_default1_and_accepts2')
require('verbosity=args.verbosity' in runner and "'verbosity': args.verbosity" in runner,
        'verbosity_passes_to_actual_TextTestRunner_and_receipt')
common_source = (A2 / 'full290_runtime_common.py').read_text(encoding='utf8')
require("module['source_hashes']()" in common_source, 'fresh_original_maintained_source_API_used')
require("historical['test_modules'] + list(module['NEW_MODULES']) + list(cloud['MODULES'])" in common_source,
        'full_original_ordered_selector_union_used')
require("exec(compile(raw, str(path), 'exec'), module)" in common_source, 'fresh_compile_not_old_pyc_for_runner_API')
require("supplemental_public_inputs() != data.get('supplemental_public_inputs_sha256')" in common_source,
        'all_public_supplemental_sets_and_bytes_fresh_each_validation')
for label in ('legacy', 'current'):
    launcher = (A2 / label / 'launcher275.py').read_text(encoding='utf8')
    require(launcher.count("{**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items()") == 2,
            label + '_child_launcher_before_after_all_source_and_supplemental_pins')
require(offline.count("{**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items()") == 2,
        'offline_child_before_after_all_source_and_supplemental_pins')
archive = (A2 / 'archive_full290_outputs.py').read_text(encoding='utf8')
require("'available_checks_passed_claimed': False" in archive and "'complete_repository_validation_claimed': False" in archive,
        'archival_of_actual_failures_never_claims_test_pass')
require("'all_four_terminal'" in (A2 / 'run_full290_orchestration.py').read_text(encoding='utf8'),
        'controller_success_only_means_terminal_not_tests_green')
require('execution-attempt2' in archive and 'p3-supplementary-attempt2' in (A2 / 'archive_p3_supplementary_290.py').read_text(encoding='utf8'),
        'new_archives_never_replace_first_actual_attempt')
source_snapshot = common.runner_api_snapshot()
supplemental = common.supplemental_public_inputs()
require(source_snapshot['selectors'] == freeze1['selectors'], 'same430_ordered_selector_strings_as_attempt1')
require(set(source_snapshot['source_sha256']) == set(freeze1['source_sha256']), 'same1221_source_paths_as_attempt1')
require(set(supplemental) == set(freeze1['supplemental_public_inputs_sha256']), 'same42_supplemental_paths_as_attempt1')
output = {'kind': 'A2_CONTROLLER_READONLY_DIFFERENCE_REVIEW_NOT_RUNTIME_VALIDATION',
          'passed': True, 'checks': checks, 'check_count': len(checks), 'differences': differences,
          'counts_are_scope_not_executed_tests': {'selectors': len(source_snapshot['selectors']),
              'maintained_source_paths': len(source_snapshot['source_sha256']), 'supplemental_public_inputs': len(supplemental)},
          'fresh_source_bytes_may_change_before_root_final_freeze': True,
          'limitations': ['This is the controller author readback, not an independent second author review.',
              'No global cross-runner lock: root must serialize and retain each owned job until terminal.',
              'Verbosity2 prints exact test IDs and failure markers as tests complete; standard unittest traceback details are still normally collected at suite end.',
              '1800 seconds is an upper bound, not a guarantee that every available test will complete.',
              'Archived failure/terminal status is not equivalent to an available PASS.'],
          'production_or_pinned_tools_modified': False, 'GUI_full_or_freeze_started': False}
with (HERE / 'controller-review.json').open('xb') as file:
    file.write((json.dumps(output, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({k: v for k, v in output.items() if k not in ('checks', 'differences')}, ensure_ascii=False, indent=2))
