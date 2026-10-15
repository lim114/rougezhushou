"""Pure-file independent combined-scope review, never a single-run PASS claim."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / '.cache/full285-preparation'
FIRST = ROOT / 'verification/full-285/execution-attempt1'
FREEZE = ROOT / 'verification/full-285/source-freeze.json'
INDICES = [18, 19, 20, 21, 38, 39, 40, 41, 44, 45]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def ordered_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf8')).hexdigest()


def assertions(path):
    tree = ast.parse(path.read_bytes())
    nodes = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Assert)), key=lambda n: (n.lineno, n.col_offset))
    return [ast.dump(n, include_attributes=False) for n in nodes]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-container', required=True, type=Path)
    args = parser.parse_args()
    second = args.legacy_container.resolve()
    terminal_path = second / 'legacy-retry-terminal.json'
    if not terminal_path.is_file() or read(terminal_path).get('terminal') is not True:
        print(json.dumps({'review_started': False, 'reason': 'Unique real Legacy2 is not terminal'}))
        return 3
    frozen = read(FREEZE)
    frozen_sha = sha(FREEZE)
    own = read(second / 'owned-legacy-retry.json')
    terminal = read(terminal_path)
    first_manifest = read(FIRST / 'archive-manifest.json')
    ledger = read(HERE / 'additive-dependency-ledger-attempt2.json')
    record = {'kind': 'INDEPENDENT_FULL285_COMBINED_SAME_SOURCE_SCOPE_REVIEW',
              'checked_at': datetime.now(timezone.utc).isoformat(), 'reviewer_sha256': sha(Path(__file__)),
              'root_source_freeze_sha256': frozen_sha, 'parent_commit': frozen['parent_commit'],
              'single_execution_all_green': False, 'original_legacy_attempt1_remains_failed': True,
              'composition': {'offline': 'execution-attempt1/offline', 'current30': 'execution-attempt1/current30',
                              'current29': 'execution-attempt1/current29', 'legacy': str(second / 'legacy')},
              'source_count': len(frozen['source_sha256']), 'selector_count': len(frozen['selectors']),
              'checks': [], 'failures': [], 'actual_processes': {},
              'full_suite_window_game_chat_or_original_auditor_executed': False,
              'PNG_visual_inspection_claimed': False, 'complete_repository_validation': False,
              'Linux_Wine_original_private_game_chat_integration_verified': False}

    def check(name, condition, detail=None):
        row = {'name': name, 'passed': bool(condition)}
        if detail is not None:
            row['detail'] = detail
        record['checks'].append(row)
        if not condition:
            record['failures'].append(row)

    check('same original root declaration and parent, no new source freeze', frozen.get('section') == 285 and frozen.get('root_declared') is True
          and own['source_freeze_sha256'] == terminal['source_freeze_sha256'] == ledger['original_source_freeze_sha256'] == frozen_sha
          and own['parent_commit'] == terminal['parent_commit'] == ledger['original_parent_commit'] == frozen['parent_commit']
          and sha(FIRST / 'root-source-freeze.json') == frozen_sha)
    check('explicit reuse only first offline/current with separate second Legacy', own['other_scopes_reused_not_rerun'] == ['offline', 'current30', 'current29'])
    check('original first archive still sealed and byte-exact', first_manifest['status'] == 'sealed_exact_outputs_no_pass_claim'
          and all((FIRST / name).is_file() and sha(FIRST / name) == item['sha256']
                  and (FIRST / name).stat().st_size == item['bytes'] for name, item in first_manifest['files'].items()))
    drift = [p for p, digest in {**frozen['source_sha256'], **frozen['preparation_tools_sha256']}.items()
             if not (ROOT / p).is_file() or sha(ROOT / p) != digest]
    check('all original frozen1193 scope and six controllers fresh byte matches', not drift, drift)
    for label in ('legacy', 'current'):
        binding = read(BASE / label / 'activation275.json')
        bad = [p for p, digest in binding['execution_tools_sha256'].items() if sha(BASE / label / p) != digest]
        check(label + ' all original activation members unchanged', not bad and binding['root_freeze_sha256'] == frozen_sha, bad)
    mapping_path = BASE / 'legacy/expected-map125.json'
    mapping = read(mapping_path)
    check('exact seven additive original proof bytes and unchanged map', len(mapping['proof_files']) == len(ledger['copied']) == 7
          and ledger['all_seven_copied_byte_exact'] is True and ledger['original_protected_bytes_changed'] is False
          and ledger['original_expected_map_sha256'] == sha(mapping_path)
          and all(sha(BASE / 'legacy' / pin['path']) == pin['sha256']
                  and (BASE / 'legacy' / pin['path']).stat().st_size == pin['bytes'] for pin in mapping['proof_files'].values()))
    check('actual second controller fixed bytes', sha(ROOT / '.cache/full285-legacy2-run.py') == own['controller_sha256'])
    first_failure_path = FIRST / 'legacy/actual/native275-launcher-closure.json'
    first_failure = read(first_failure_path)
    check('original attempt1 failure preserved, never replaced by attempt2', first_failure['passed'] is False
          and first_failure['fixture_exception']['message'] == 'Escaped/nonregular artifact pin'
          and first_failure['actual_current_native_windows_window_verified'] is False
          and sha(first_failure_path) == ledger['original_attempt1_legacy_failure_sha256']
          and not (FIRST / 'legacy/actual/wine-ui-100.json').exists())

    def process(name, folder):
        supervisor, observed = read(folder / 'supervisor.json'), read(folder / 'controller-process.json')
        origin = read(folder / 'process-exit-origin.json')
        value = int((folder / 'process.exit').read_text(encoding='ascii').strip())
        check(name + ' true original Popen supervisor exit and closed owned job', observed['status'] == supervisor['status'] == 'completed'
              and type(supervisor['child_primary_exit']) is int and value == supervisor['supervisor_exit'] == observed['actual_observed_popen_exit']
              and supervisor['timed_out'] is False and supervisor['owned_handle_retained'] is True
              and supervisor['owned_job_assigned'] is True and supervisor['owned_job_no_live_execution_verified'] is True)
        check(name + ' original exit file not derived', origin['kind'] == 'ACTUAL_RETAINED_POPEN_OBSERVED_SUPERVISOR_EXIT'
              and origin['derived_from_supervisor_json'] is False and origin['actual_observed_popen_exit'] == value
              and origin['process_exit_sha256'] == sha(folder / 'process.exit'))
        for label in ('stdout', 'stderr'):
            log = supervisor[label]
            check(name + ' exact raw child ' + label, sha(folder / log['file']) == log['sha256']
                  and (folder / log['file']).stat().st_size == log['bytes'])
        record['actual_processes'][name] = {'child_exit': supervisor['child_primary_exit'], 'supervisor_exit': value,
                                           'elapsed_seconds': supervisor['elapsed_seconds'], 'owned_job_closed': True}
        return supervisor

    for name in ('offline', 'current30', 'current29', 'legacy_failed_first_attempt'):
        process(name, FIRST / ('legacy' if name == 'legacy_failed_first_attempt' else name))
    second_process = process('legacy_second_attempt', second / 'legacy')
    check('second independent legacy root terminal record', terminal['terminal'] is True
          and terminal['observed']['actual_observed_popen_exit'] == second_process['supervisor_exit'])
    offline_path = FIRST / 'offline/actual/windows-offline.json'
    offline = read(offline_path)
    offline_closure = read(FIRST / 'offline/actual/offline285-source-closure.json')
    check('offline complete maintained selector and source maps same frozen input', offline['selectors'] == frozen['selectors'] and offline['source_sha256'] == frozen['source_sha256'])
    check('offline available passed with no failure/error/drift and real zero exits', offline['available_checks_passed'] is True
          and offline['failures'] == offline['errors'] == 0 and offline['source_drift'] == []
          and record['actual_processes']['offline']['child_exit'] == record['actual_processes']['offline']['supervisor_exit'] == 0)
    check('offline raw closure binding and unknown not converted to passes', offline_closure['available_checks_passed'] is True
          and offline_closure['root_freeze_sha256'] == frozen_sha and offline_closure['actual_suite_receipt_sha256'] == sha(offline_path)
          and offline_closure['source_drift'] == [] and offline['complete_repository_validation'] is False
          and len(offline['unavailable']) == offline['unavailable_records']
          and all(row['counted_as_passed'] is False for row in offline['unavailable']))
    record['offline'] = {k: offline[k] for k in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                         'failures', 'errors', 'unavailable_records', 'unavailable_parent_count')}
    current_rows = {}
    for name in ('current30', 'current29'):
        raw, closure = read(FIRST / name / 'actual/window.json'), read(FIRST / name / 'actual/native275-launcher-closure.json')
        check(name + ' same freeze and intact actual windows source/isolation', raw['source_sha256_before'] == raw['source_sha256_after'] == frozen['source_sha256']
              and raw['source_drift'] == [] and raw['source_freeze_sha256'] == frozen_sha and raw['frozen_source_binding_matches'] is True
              and raw['native_windows_verified'] is True and raw['game_captures'] == raw['chat_requests'] == 0
              and raw['private_state_isolated'] is True and raw['qt_cleanup']['application_destroyed'] is True
              and raw['qt_cleanup']['remaining_wrappers_valid'] == 0 and closure['actual_current_native_windows_window_verified'] is True
              and closure['source_drift'] == closure['executed_tool_drift'] == [])
        script = 'window29.py' if name == 'current29' else 'window.py'
        tree = assertions(BASE / 'current' / script)
        check(name + ' original complete assertion AST retained', len(tree) == (25 if name == 'current29' else 31)
              and tree == assertions(ROOT / 'verification/full-275/current-window-attempt3/executed-tools' / script))
        current_rows[name] = raw
        if name == 'current29':
            check('current29 actual all29 pass and real zero exits', raw['passed'] is True and closure['passed'] is True
                  and len(raw['checks']) == 29 and raw['original30_full_script_retained_and_required'] is True
                  and record['actual_processes'][name]['child_exit'] == record['actual_processes'][name]['supervisor_exit'] == 0)
        else:
            failure = raw.get('failure', {})
            check('current30 true narrowly scoped WinError1314 unavailable, not passed', raw['passed'] is False and closure['passed'] is False
                  and len(raw['checks']) == 29 and failure.get('type') == 'OSError'
                  and '[WinError 1314]' in failure.get('message', '') and '.symlink_to' in failure.get('traceback', '')
                  and 'os.symlink' in failure.get('traceback', '') and 'pathlib.py' in failure.get('traceback', '')
                  and record['actual_processes'][name]['child_exit'] != 0 and record['actual_processes'][name]['supervisor_exit'] != 0)
    check('all29 original current workflow names match', current_rows['current30']['checks'] == current_rows['current29']['checks'])
    record['current'] = {'original30_attempt': 'failed solely at actual native symlink1314 prerequisite',
                         'available_original_workflows_passed': 29, 'symlink_specialization_passed': False}

    actual = second / 'legacy/actual'
    legacy_path = actual / 'wine-ui-100.json'
    legacy, closure = read(legacy_path), read(actual / 'native275-launcher-closure.json')
    check('legacy second attempt genuine zero exits and actual Windows closure', second_process['child_primary_exit'] == second_process['supervisor_exit'] == 0
          and legacy['passed'] is True and legacy['complete_ui_validation'] is True and closure['passed'] is True
          and closure['actual_current_native_windows_window_verified'] is True and closure['root_freeze_sha256'] == frozen_sha
          and closure['source_drift'] == closure['executed_tool_drift'] == legacy['source_drift'] == legacy['source_additional_drift'] == [])
    check('complete4283 records/4281 passed/2metadata and52/156 requests', legacy['total_actual_checks'] == len(legacy['checks']) == 4283
          and sum(row.get('passed') is True for row in legacy['checks']) == 4281
          and sum('passed' not in row for row in legacy['checks']) == 2
          and legacy['new_explicit_damage_button_requests090'] == 52 and legacy['new_explicit_three_text_requests090'] == 156)
    static = read(BASE / 'legacy/static-preservation.json')
    check('all862 AST original order and552 original body retained', len(assertions(BASE / 'legacy/window.py')) == 862
          and assertions(BASE / 'legacy/window.py') == assertions(ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools/window.py')
          and static['original_functional_try_assertions'] == 552
          and static['functional_try_bytes_sha256'] == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922')
    meta = legacy['new_state_archive090']
    compressed_path = actual / meta['file']
    compressed = compressed_path.read_bytes()
    decoded = gzip.decompress(compressed)
    typed = json.loads(decoded)
    rows = typed['actual_new_window_states']
    check('typed archive compressed/decompressed hashes and exact52 actual rows', len(compressed) == meta['bytes']
          and hashlib.sha256(compressed).hexdigest() == meta['sha256'] and len(decoded) == meta['decoded_bytes']
          and hashlib.sha256(decoded).hexdigest() == meta['decoded_sha256'] and len(rows) == meta['records'] == typed['expected_UI_state_rows'] == 52
          and typed['passed'] is True and typed['actual_main_window_execution_only'] is True
          and Counter(row['section'] for row in rows) == {86: 44, 88: 8}
          and len({(row['section'], row['pair_id'], row['widget_checked']) for row in rows}) == 52)
    check('all52 captured typed dicts/real same-call entries/3reports', all(row['passed'] is True
          and row['scenario_native'].get('type') == row['result_native'].get('type') == 'dict'
          and row['actual_entries']['calculate_damage'] == 1 and row['actual_entries']['RunState.__init__'] == 0
          and row['actual_entries']['format_estimate'] == 1 and row['explicit_three_text_requests'] == 3
          and set(row['reports']) == {'estimate', 'default', 'technical'} for row in rows))
    empty = sum(row['actual_same_call_readonly_trace'] == [] for row in rows)
    check('26 genuine saved empty traces retained', empty == 26)
    bridge = read(actual / 'full125-113-bridge-ledger.json')
    admissions = sorted(bridge['actual_admissions'], key=lambda row: row['literal_index'])
    by_identity = {(row['section'], row['pair_id'], row['widget_checked']): row for row in rows}
    check('exact10 admissions/caller identity and42 unchanged nonbridge positions', bridge['all10_admitted'] is True
          and len(admissions) == 10 and bridge['expected_literal_indices'] == [row['literal_index'] for row in admissions] == INDICES
          and len(rows) - len(admissions) == 42 and bridge['mapping_sha256'] == sha(mapping_path)
          and all(row['raw_result_and_caller_unchanged'] is True
                  and row['actual_caller_native090_sha256'] == row['Root_original_caller_native090_sha256']
                  == ordered_sha(by_identity[row['section'], row['pair_id'], row['widget_checked']]['scenario_native']) for row in admissions))
    bridge_closure = read(actual / 'full125-bridge-closure.json')
    check('bridge exact receipt/ledger closure and no source drift', bridge_closure['passed'] is True and bridge_closure['workflow_complete'] is True
          and bridge_closure['source_drift'] == bridge_closure['source_additional_drift'] == [] and bridge_closure['window_primary_code'] == 0
          and bridge_closure['window_receipt_sha256'] == sha(legacy_path)
          and bridge_closure['ledger_sha256'] == sha(actual / 'full125-113-bridge-ledger.json'))
    record['legacy_second'] = {'runtime_records': len(legacy['checks']), 'typed_states': len(rows),
                               'explicit_text_requests': legacy['new_explicit_three_text_requests090'],
                               'assertion_AST': 862, 'original_main_body_assertions': 552,
                               'exact_bridge_indices': INDICES, 'unchanged_nonbridge_positions': len(rows) - len(admissions),
                               'real_empty_traces': empty, 'typed_archive_sha256': sha(compressed_path)}
    formal_path = second / 'legacy/independent-saved-readback-audit.json'
    record['root_formal_typed_audit_present'] = formal_path.is_file()
    if formal_path.is_file():
        formal = read(formal_path)
        check('root original formal typed codec readback, historical label kept', formal['passed'] is True
              and formal['kind'] == 'INDEPENDENT_FULL261_COMPLETE_WINDOW_READBACK'
              and formal['complete_runtime_checks'] == 4283 and formal['saved_rows'] == 52
              and formal['codec_exact_typed_roundtrip'] is True and formal['codec_plain_JSON_order_and_values_match'] is True
              and formal['current_revised_assertions'] == 862 and formal['exact_ten_admission_indices'] == INDICES
              and formal['readonly_trace_empty_rows_not_invented'] == 26 and formal['source_and_additional_drift'] == [])
        record['root_formal_typed_audit_sha256'] = sha(formal_path)
    else:
        record['root_formal_typed_audit_remaining'] = 'Root must execute the original unchanged typed auditor; this independent structural/hash review does not substitute its full codec roundtrip.'
    record['same_source_combined_available_scope_reviewed'] = not record['failures']
    record['not_a_single_all_green_execution'] = True
    record['remaining_unavailable'] = ['Actual Windows symlink1314 prerequisites, not passed',
                                       'Current Linux/WSL/Wine environment',
                                       'Original historical Windows/private095/109/game/chat integration']
    output = HERE / 'combined-scope-review.json'
    with output.open('x', encoding='utf8') as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
        file.write('\n')
    print(json.dumps({key: value for key, value in record.items() if key != 'checks'}, ensure_ascii=False, indent=2))
    return 0 if not record['failures'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
