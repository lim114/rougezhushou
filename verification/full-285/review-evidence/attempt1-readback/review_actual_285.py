"""Independent pure-file final285 review; never execute a fixture or import app."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.cache/full285-preparation'
FREEZE = ROOT / 'verification/full-285/source-freeze.json'
EXPECTED_INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]
STEP_NAMES = ['offline', 'legacy', 'current30', 'current29']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordered(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--container', required=True, type=Path)
    args = parser.parse_args()
    source = args.container.resolve()
    control = json.loads((source / 'orchestration.json').read_bytes())
    if control.get('status') != 'all_four_terminal':
        print(json.dumps({'review_started': False, 'reason': 'Actual four-command execution is not terminal',
                          'observed_status': control.get('status')}))
        return 3
    frozen = json.loads(FREEZE.read_bytes())
    results = {'kind': 'INDEPENDENT_FULL285_ACTUAL_OUTPUT_SCOPE_REVIEW',
               'checked_at': datetime.now(timezone.utc).isoformat(),
               'container': str(source), 'source_freeze_sha256': sha(FREEZE),
               'reviewer_sha256': sha(Path(__file__)),
               'checks': [], 'failures': [], 'steps': {},
               'full_suite_or_window_reexecuted': False,
               'original_typed_auditor_executed_by_this_review': False,
               'PNG_visual_inspection_claimed': False,
               'Linux_Wine_original_private_game_chat_verified': False,
               'unavailable_checks_counted_as_passed': False,
               'production_private_state_or_frozen_tool_changes': False}

    def check(name, condition, detail=None):
        row = {'name': name, 'passed': bool(condition)}
        if detail is not None:
            row['detail'] = detail
        results['checks'].append(row)
        if not condition:
            results['failures'].append(row)

    check('root declaration section285', frozen.get('root_declared') is True and frozen.get('section') == 285)
    check('actual control binding', control.get('source_freeze_sha256') == sha(FREEZE)
          and control.get('parent_commit') == frozen.get('parent_commit'))
    check('four mandatory ordered steps', [r['name'] for r in control['steps']] == STEP_NAMES)
    parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    check('unchanged current parent and development branch', parent == frozen['parent_commit'] and branch == 'codex/p2-development')
    previous = json.loads((ROOT / 'verification/full-275/source-freeze-reset-repair.json').read_bytes())
    check('all previous275 selectors retained', set(previous['selectors']) <= set(frozen['selectors']))
    check('all previous275 source filenames retained', set(previous['source_sha256']) <= set(frozen['source_sha256']))
    drift = [p for p, expected in frozen['source_sha256'].items()
             if not (ROOT / p).is_file() or (ROOT / p).is_symlink() or sha(ROOT / p) != expected]
    check('fresh all frozen source bytes', not drift, {'source_count': len(frozen['source_sha256']), 'drift': drift})
    prep_drift = [p for p, expected in frozen['preparation_tools_sha256'].items() if sha(ROOT / p) != expected]
    check('fresh all frozen controller bytes', not prep_drift, prep_drift)

    for label in ('legacy', 'current'):
        binding_path = BASE / label / 'activation275.json'
        binding = json.loads(binding_path.read_bytes())
        changed = [p for p, expected in binding['execution_tools_sha256'].items() if sha(BASE / label / p) != expected]
        check(label + ' activated source identity and all exact used tools',
              not changed and binding['root_freeze_sha256'] == sha(FREEZE)
              and binding['tested_worktree_parent_commit'] == parent, {'tool_count': len(binding['execution_tools_sha256']), 'drift': changed})

    for name in STEP_NAMES:
        folder = source / name
        supervisor = json.loads((folder / 'supervisor.json').read_bytes())
        observed = json.loads((folder / 'controller-process.json').read_bytes())
        origin = json.loads((folder / 'process-exit-origin.json').read_bytes())
        exit_value = int((folder / 'process.exit').read_text(encoding='ascii').strip())
        check(name + ' true observed supervisor exit matches raw file and child status',
              observed.get('status') == 'completed' and supervisor.get('status') == 'completed'
              and type(supervisor.get('child_primary_exit')) is int
              and type(exit_value) is int and observed.get('actual_observed_popen_exit') == exit_value == supervisor.get('supervisor_exit'))
        check(name + ' actual original exit origin, not derived',
              origin.get('kind') == 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT'
              and origin.get('derived_from_supervisor_json') is False
              and origin.get('actual_observed_popen_exit') == exit_value
              and origin.get('process_exit_sha256') == sha(folder / 'process.exit'))
        check(name + ' retained handle/job closed and no timeout',
              supervisor.get('owned_handle_retained') is True and supervisor.get('owned_job_assigned') is True
              and supervisor.get('owned_job_no_live_execution_verified') is True and supervisor.get('timed_out') is False)
        for log_key in ('stdout', 'stderr'):
            declaration = supervisor[log_key]
            log = folder / declaration['file']
            check(name + ' original child ' + log_key + ' hash/size',
                  log.stat().st_size == declaration['bytes'] and sha(log) == declaration['sha256'])
        results['steps'][name] = {'actual_supervisor_exit': exit_value,
                                 'actual_child_exit': supervisor['child_primary_exit'],
                                 'elapsed_seconds': supervisor['elapsed_seconds'],
                                 'owned_job_closed': supervisor['owned_job_no_live_execution_verified'],
                                 'supervisor_sha256': sha(folder / 'supervisor.json')}

    offline_path = source / 'offline/actual/windows-offline.json'
    offline = json.loads(offline_path.read_bytes())
    closure = json.loads((source / 'offline/actual/offline285-source-closure.json').read_bytes())
    check('offline exact source and complete selector union', offline['source_sha256'] == frozen['source_sha256'] and offline['selectors'] == frozen['selectors'])
    check('offline no failures/errors/drift and available pass', offline['available_checks_passed'] is True
          and offline['failures'] == offline['errors'] == 0 and offline['source_drift'] == []
          and results['steps']['offline']['actual_child_exit'] == results['steps']['offline']['actual_supervisor_exit'] == 0)
    check('offline wrapper genuine freeze closure', closure['available_checks_passed'] is True
          and closure['actual_suite_exit'] == 0 and closure['source_drift'] == []
          and closure['actual_selector_list_matches_root_freeze'] is True
          and closure['suite_source_map_matches_root_freeze'] is True
          and closure['actual_suite_receipt_sha256'] == sha(offline_path)
          and closure['root_freeze_sha256'] == sha(FREEZE))
    check('offline unavailable records never passed',
          len(offline['unavailable']) == offline['unavailable_records']
          and all(r.get('counted_as_passed') is False for r in offline['unavailable']))
    check('offline native Qt cleanup', offline['qt_shutdown_error'] is None
          and offline['qt_shutdown']['application_destroyed'] is True
          and offline['qt_shutdown']['valid_wrappers_after_shutdown'] == 0)
    results['offline'] = {key: offline[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                         'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'complete_repository_validation')}
    results['offline'].update(selectors=len(offline['selectors']), source_files=len(offline['source_sha256']),
                              unavailable_winerrors=dict(Counter(str(r.get('winerror')) for r in offline['unavailable'])))

    legacy_folder = source / 'legacy/actual'
    legacy_path = legacy_folder / 'wine-ui-100.json'
    legacy = json.loads(legacy_path.read_bytes())
    legacy_closure = json.loads((legacy_folder / 'native275-launcher-closure.json').read_bytes())
    check('legacy original complete4283 checks', legacy['passed'] is True and legacy['complete_ui_validation'] is True
          and legacy['total_actual_checks'] == len(legacy['checks']) == 4283
          and sum(r.get('passed') is True for r in legacy['checks']) == 4281
          and sum('passed' not in r for r in legacy['checks']) == 2)
    check('legacy complete52 requests and156 text', legacy['new_explicit_damage_button_requests090'] == 52
          and legacy['new_explicit_three_text_requests090'] == 156)
    check('legacy original source and additional closure', legacy['source_drift'] == legacy['source_additional_drift'] == []
          and legacy_closure['passed'] is True and legacy_closure['source_drift'] == legacy_closure['executed_tool_drift'] == []
          and legacy_closure['actual_current_native_windows_window_verified'] is True
          and legacy_closure['root_freeze_sha256'] == sha(FREEZE)
          and results['steps']['legacy']['actual_child_exit'] == results['steps']['legacy']['actual_supervisor_exit'] == 0)
    static = json.loads((BASE / 'legacy/static-preservation.json').read_bytes())
    window_tree = ast.parse((BASE / 'legacy/window.py').read_bytes())
    check('all862 current AST assertions and552 original body',
          sum(isinstance(n, ast.Assert) for n in ast.walk(window_tree)) == static['current_assertions'] == 862
          and static['original_functional_try_assertions'] == 552
          and static['functional_try_bytes_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922')
    metadata = legacy['new_state_archive090']
    compressed_path = legacy_folder / metadata['file']
    compressed = compressed_path.read_bytes()
    decoded = gzip.decompress(compressed)
    archive = json.loads(decoded)
    rows = archive['actual_new_window_states']
    check('actual typed archive hash and decompressed byte identity', len(compressed) == metadata['bytes']
          and hashlib.sha256(compressed).hexdigest() == metadata['sha256']
          and len(decoded) == metadata['decoded_bytes'] and hashlib.sha256(decoded).hexdigest() == metadata['decoded_sha256'])
    check('all52 unique typed actual states and44/8 split', len(rows) == metadata['records'] == archive['expected_UI_state_rows'] == 52
          and archive['actual_main_window_execution_only'] is True and archive['passed'] is True
          and Counter(r['section'] for r in rows) == {86: 44, 88: 8}
          and len({(r['section'], r['pair_id'], r['widget_checked']) for r in rows}) == 52)
    check('52 genuine same-call entries and3 report requests per state',
          all(r['passed'] is True and r['explicit_three_text_requests'] == 3
              and r['actual_entries']['calculate_damage'] == 1 and r['actual_entries']['RunState.__init__'] == 0
              and r['actual_entries']['format_estimate'] == 1 and set(r['reports']) == {'estimate', 'default', 'technical'}
              and r['scenario_native'].get('type') == r['result_native'].get('type') == 'dict' for r in rows))
    empty = sum(r['actual_same_call_readonly_trace'] == [] for r in rows)
    check('26 saved real empty traces retained', empty == 26)
    bridge = json.loads((legacy_folder / 'full125-113-bridge-ledger.json').read_bytes())
    admissions = sorted(bridge['actual_admissions'], key=lambda r: r['literal_index'])
    check('exact10 bridge identities and caller hashes', bridge['all10_admitted'] is True
          and len(admissions) == 10 and bridge['expected_literal_indices'] == [r['literal_index'] for r in admissions] == EXPECTED_INDICES
          and all(r['raw_result_and_caller_unchanged'] is True
                  and r['actual_caller_native090_sha256'] == r['Root_original_caller_native090_sha256'] for r in admissions))
    check('42 unchanged non-bridge state positions', len(rows) - len(admissions) == 42)
    bridge_closure = json.loads((legacy_folder / 'full125-bridge-closure.json').read_bytes())
    check('bridge closure true exact original byte hashes', bridge_closure['passed'] is True
          and bridge_closure['workflow_complete'] is True and bridge_closure['window_primary_code'] == 0
          and bridge_closure['source_drift'] == bridge_closure['source_additional_drift'] == []
          and bridge_closure['window_receipt_sha256'] == sha(legacy_path)
          and bridge_closure['ledger_sha256'] == sha(legacy_folder / 'full125-113-bridge-ledger.json'))
    results['legacy'] = {'runtime_records': 4283, 'passed_flag_records': 4281, 'metadata_records': 2,
                         'typed_states': len(rows), 'explicit_text_requests': 156, 'assertion_AST': 862,
                         'main_body_assertions': 552, 'exact_bridge_indices': EXPECTED_INDICES,
                         'unchanged_non_bridge_positions': len(rows) - len(admissions), 'real_empty_traces': empty,
                         'typed_archive_sha256': sha(compressed_path),
                         'full_codec_roundtrip_left_to_root_original_auditor': True}

    current = {}
    for name in ('current30', 'current29'):
        folder = source / name / 'actual'
        raw = json.loads((folder / 'window.json').read_bytes())
        closed = json.loads((folder / 'native275-launcher-closure.json').read_bytes())
        expected_count = 29 if name == 'current29' or raw['passed'] is False else 30
        check(name + ' original workflow count retained', len(raw['checks']) == expected_count)
        script_name = 'window29.py' if name == 'current29' else 'window.py'
        current_tree = ast.parse((BASE / 'current' / script_name).read_bytes())
        original_tree = ast.parse((ROOT / 'verification/full-275/current-window-attempt3/executed-tools' / script_name).read_bytes())
        assertions = [ast.dump(n, include_attributes=False) for n in ast.walk(current_tree) if isinstance(n, ast.Assert)]
        original_assertions = [ast.dump(n, include_attributes=False) for n in ast.walk(original_tree) if isinstance(n, ast.Assert)]
        check(name + ' complete original assertion AST retained', assertions == original_assertions
              and len(assertions) == (25 if name == 'current29' else 31))
        check(name + ' source map before/after exactly root freeze',
              raw['source_sha256_before'] == raw['source_sha256_after'] == frozen['source_sha256']
              and raw['source_drift'] == [] and raw['source_freeze_sha256'] == sha(FREEZE)
              and raw['frozen_source_binding_matches'] is True)
        check(name + ' actual window/Qt isolation', raw['native_windows_verified'] is True
              and raw['game_captures'] == raw['chat_requests'] == 0 and raw['private_state_isolated'] is True
              and raw['qt_cleanup']['application_destroyed'] is True and raw['qt_cleanup']['remaining_wrappers_valid'] == 0
              and closed['actual_current_native_windows_window_verified'] is True
              and closed['source_drift'] == closed['executed_tool_drift'] == [])
        current[name] = {'passed': raw['passed'], 'workflow_count': len(raw['checks']),
                         'receipt_sha256': sha(folder / 'window.json'),
                         'failure_type': raw.get('failure', {}).get('type'),
                         'symlink_unavailable': raw.get('maintenance261_symlink_specialization')}
        if name == 'current29':
            check('current29 genuine pass and0 child/supervisor', raw['passed'] is True and closed['passed'] is True
                  and results['steps'][name]['actual_child_exit'] == results['steps'][name]['actual_supervisor_exit'] == 0
                  and raw['original30_full_script_retained_and_required'] is True)
        else:
            failure = raw.get('failure', {})
            is1314 = (failure.get('type') == 'OSError' and '[WinError 1314]' in failure.get('message', '')
                      and '.symlink_to' in failure.get('traceback', '') and 'pathlib.py' in failure.get('traceback', ''))
            pass30 = (raw['passed'] is True and closed['passed'] is True
                      and results['steps'][name]['actual_child_exit'] == results['steps'][name]['actual_supervisor_exit'] == 0)
            unavailable30 = (raw['passed'] is False and closed['passed'] is False and is1314
                             and results['steps'][name]['actual_child_exit'] != 0 and results['steps'][name]['actual_supervisor_exit'] != 0)
            check('original30 actual pass or narrowly proved1314 unavailable', pass30 or unavailable30)
            current[name]['symlink_specialization_status'] = 'passed' if pass30 else 'unavailable1314' if unavailable30 else 'unresolved_failure'
    raw30 = json.loads((source / 'current30/actual/window.json').read_bytes())
    raw29 = json.loads((source / 'current29/actual/window.json').read_bytes())
    check('current29 complete unchanged workflow names equal full30 original prefix', raw30['checks'][:29] == raw29['checks'])
    results['current'] = current
    results['passed_reviewed_available_scope'] = not results['failures']
    results['complete_repository_validation'] = False
    results['formal_typed_auditor_and_PNG_review_still_required'] = True
    output = HERE / 'independent-actual-output-review.json'
    with output.open('x', encoding='utf8') as file:
        json.dump(results, file, ensure_ascii=False, indent=2)
        file.write('\n')
    print(json.dumps({key: value for key, value in results.items() if key not in ('checks',)}, ensure_ascii=False, indent=2))
    return 0 if not results['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
