"""Append-only pure-file evidence of the genuine285 attempt1 preparation failure."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ACTUAL = Path('C:/Users/李娜/AppData/Local/Temp/rouge-full285-ec254bf0c8a64493986a510420c37811')
BASE = ROOT / '.cache/full285-preparation'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze_path = ROOT / 'verification/full-285/source-freeze.json'
    freeze = json.loads(freeze_path.read_bytes())
    control = json.loads((ACTUAL / 'orchestration.json').read_bytes())
    record = {'kind': 'FULL285_ATTEMPT1_REAL_LEGACY_PREPARATION_FAILURE',
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'recorder_sha256': sha(Path(__file__)),
              'source_container': str(ACTUAL), 'source_freeze_sha256': sha(freeze_path),
              'parent_commit': freeze['parent_commit'],
              'root_source_files': len(freeze['source_sha256']), 'selectors': len(freeze['selectors']),
              'orchestration_status': control['status'], 'whole_full285_validation_passed': False,
              'failure_classification': 'PREPARATION_TRANSITIVE_PROOF_DEPENDENCY_OMISSION',
              'legacy_52_typed_or_4283_checks_executed': False,
              'prior275_receipts_substituted': False,
              'fixture_tests_or_GUI_reexecuted_by_this_recorder': False,
              'frozen_source_tools_actual_outputs_changed': False,
              'steps': {}, 'evidence_files': {}, 'missing_bridge_proofs': []}
    for name in ('offline', 'legacy', 'current30', 'current29'):
        folder = ACTUAL / name
        supervisor = json.loads((folder / 'supervisor.json').read_bytes())
        observed = json.loads((folder / 'controller-process.json').read_bytes())
        origin = json.loads((folder / 'process-exit-origin.json').read_bytes())
        raw_exit = int((folder / 'process.exit').read_text(encoding='ascii'))
        assert observed['actual_observed_popen_exit'] == supervisor['supervisor_exit'] == raw_exit
        assert origin['derived_from_supervisor_json'] is False and origin['process_exit_sha256'] == sha(folder / 'process.exit')
        assert supervisor['status'] == 'completed' and supervisor['timed_out'] is False
        assert supervisor['owned_job_no_live_execution_verified'] is True
        record['steps'][name] = {'actual_child_exit': supervisor['child_primary_exit'],
                                 'actual_supervisor_exit': raw_exit,
                                 'elapsed_seconds': supervisor['elapsed_seconds'],
                                 'timed_out': False, 'owned_job_closed': True,
                                 'original_Popen_exit_not_derived': True}
        for filename in ('supervisor.json', 'controller-process.json', 'process.exit', 'process-exit-origin.json'):
            path = folder / filename
            record['evidence_files'][name + '/' + filename] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    for relative in ('orchestration.json', 'legacy/actual/native275-launcher-closure.json',
                     'offline/actual/windows-offline.json', 'offline/actual/offline285-source-closure.json',
                     'current30/actual/window.json', 'current29/actual/window.json'):
        path = ACTUAL / relative
        record['evidence_files'][relative] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    offline = json.loads((ACTUAL / 'offline/actual/windows-offline.json').read_bytes())
    assert offline['source_sha256'] == freeze['source_sha256'] and offline['selectors'] == freeze['selectors']
    assert offline['available_checks_passed'] is True and offline['failures'] == offline['errors'] == 0
    record['offline'] = {key: offline[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips',
                         'failures', 'errors', 'unavailable_records', 'unavailable_parent_count', 'complete_repository_validation')}
    record['offline']['source_and_selector_map_match_freeze'] = True
    closure = json.loads((ACTUAL / 'legacy/actual/native275-launcher-closure.json').read_bytes())
    assert closure['fixture_exception']['message'] == 'Escaped/nonregular artifact pin'
    assert closure['passed'] is False and closure['source_drift'] == closure['executed_tool_drift'] == []
    assert closure['actual_current_native_windows_window_verified'] is False
    assert not (ACTUAL / 'legacy/actual/wine-ui-100.json').exists()
    record['legacy_failure'] = {'exception': closure['fixture_exception'],
                                'source_and_tool_drift': [], 'Qt_created': False,
                                'actual_files': [p.name for p in (ACTUAL / 'legacy/actual').iterdir()],
                                'full_receipt_missing': True}
    for name in ('current30', 'current29'):
        row = json.loads((ACTUAL / name / 'actual/window.json').read_bytes())
        record[name] = {'passed': row['passed'], 'workflow_count': len(row['checks']),
                        'source_drift': row['source_drift'],
                        'failure_type': row.get('failure', {}).get('type'),
                        'actual_1314': '[WinError 1314]' in row.get('failure', {}).get('message', ''),
                        'unavailable_specialization': row.get('maintenance261_symlink_specialization')}
    mapping_path = BASE / 'legacy/expected-map125.json'
    mapping = json.loads(mapping_path.read_bytes())
    old = ROOT / 'verification/full-275/legacy-window-attempt3/executed-tools'
    for key, pin in mapping['proof_files'].items():
        new_path, old_path = BASE / 'legacy' / pin['path'], old / pin['path']
        assert not new_path.exists()
        assert old_path.is_file() and old_path.stat().st_size == pin['bytes'] and sha(old_path) == pin['sha256']
        record['missing_bridge_proofs'].append({'key': key, **pin, 'attempt1_present': False,
                                               'original_275_executed_exact_bytes_available': True,
                                               'original_public_path': old_path.relative_to(ROOT).as_posix()})
    assert len(record['missing_bridge_proofs']) == 7
    record['expected_map_sha256'] = sha(mapping_path)
    record['required_next_action'] = 'Root-reviewed independent new bundle/binding with all seven original proof bytes; do not overwrite attempt1 or relax original checks.'
    record['preparation_static_green_limitation'] = 'Original76/17 pin-list and compile/argv checks passed only their listed scope; they did not establish transitive expected-map proof existence.'
    record['first_review_reader_exit1_classification'] = 'Real missing legacy receipt, consistent with actual bridge admission failure; not a product PASS or an executed original typed audit.'
    output = HERE / 'attempt1-failure-summary.json'
    with output.open('x', encoding='utf8') as file:
        json.dump(record, file, ensure_ascii=False, indent=2)
        file.write('\n')
    print(json.dumps({'evidence_recorded': True, 'whole_full285_validation_passed': False,
                      'missing_proof_count': 7, 'record_sha256': sha(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
