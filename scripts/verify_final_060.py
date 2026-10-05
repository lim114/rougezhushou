"""Close this batch's direct evidence without reinterpreting historical receipts."""
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def check_hashes(mapping):
    for name, digest in mapping.items():
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and '.local' not in path.relative_to(ROOT).parts, name
        assert sha(path) == digest, name


def main():
    core = read('CORE_0.60_VERIFICATION.json')
    numeric = read('NUMERIC_REPLAY_0.60_VERIFICATION.json')
    ui = read('NATIVE_UI_0.60_VERIFICATION.json')
    package = read('PACKAGE_0.60_VERIFICATION.json')
    counter = read('COUNTER_0.60_VERIFICATION.json')
    app = read('APP_0.60_LAUNCH_VERIFICATION.json')
    for result in (core, numeric, ui, package, counter):
        assert result['passed'] and result['version'] == '0.60.0'
    assert core['failures'] == core['errors'] == 0 and not core['source_drift_during_tests']
    assert numeric['cases'] == numeric['exact_structured_unchanged'] == 732
    assert numeric['allowances'] == []
    for key in ('only_one_project_window', 'window_visible_and_restored', 'within_monitor_work_area',
                'same_run_preserved', 'history_preserved', 'settings_and_bindings_unchanged',
                'run_cmd_startup_verified'):
        assert app[key], key
    assert app['chat_requests'] == app['game_actions'] == app['run_state_writes_by_upgrade_script'] == 0
    # Recheck only explicitly current source maps. Archived source metadata is
    # evidence of its own version, never asserted against today's files.
    for mapping in (core['source_sha256_after'], numeric['full_formal_source_sha256_after'],
                    counter['sha256'], ui['source_sha256_after'], package['source_sha256_after']):
        check_hashes(mapping)
    evidence = {
        name: sha(ROOT / name) for name in (
            'CORE_0.60_VERIFICATION.json', 'NUMERIC_REPLAY_0.60_VERIFICATION.json',
            'NATIVE_UI_0.60_VERIFICATION.json', 'PACKAGE_0.60_VERIFICATION.json',
            'COUNTER_0.60_VERIFICATION.json', 'APP_0.60_LAUNCH_VERIFICATION.json',
            '.cache/research/river-effects-060/player-integration-verification.json',
            '.cache/research/river-effects-060/verification.json',
            '.cache/research/counter-samples-060/manifest.json',
            '.cache/research/recipient-lifecycle-060/receipt.json',
            '.cache/research/counter-reading-060/actual-current-1791197167969609900/receipt.json')}
    river = read('.cache/research/river-effects-060/player-integration-verification.json')
    check_hashes(river['source_sha256_at_fast_tests'])
    check_hashes(river['unchanged_numerical_source_sha256'])
    check_hashes(river['evidence_sha256'])
    evidence.update(river['evidence_sha256'])
    direct = read('.cache/research/river-effects-060/verification.json')
    direct_hashes = {item['path']: item['sha256'] for item in direct['evidence_direct_sha_checks']}
    check_hashes(direct_hashes)
    evidence.update(direct_hashes)
    samples = read('.cache/research/counter-samples-060/manifest.json')
    assert samples['positive_gray_held_counter_count'] == 0 and samples['p1_gap_closed'] is False
    sample_hashes = {'.cache/research/counter-samples-060/' + name: item['sha256']
                     for name, item in samples['files'].items()}
    check_hashes(sample_hashes)
    evidence.update(sample_hashes)
    review = '.cache/research/counter-samples-060-audit-1791199482306510100.json'
    evidence[review] = sha(ROOT / review)
    hydra_name = '.cache/research/hydra-060/freeze.json'
    hydra = read(hydra_name)
    assert hydra['passed']
    check_hashes(hydra['source_sha256'])
    check_hashes(hydra['owned_files_and_receipts_sha256'])
    evidence.update(hydra['owned_files_and_receipts_sha256'])
    evidence[hydra_name] = sha(ROOT / hydra_name)
    contract = read('.cache/research/hydra-060/mechanism-contract.json')
    check_hashes(contract['references'])
    evidence.update(contract['references'])
    assert sha(ROOT / package['wheel']) == package['wheel_sha256']
    evidence[package['wheel']] = package['wheel_sha256']
    for name in (core['test_log'], numeric['current_output'], numeric['worker_receipt']):
        evidence[name] = sha(ROOT / name)
    actual = read('.cache/research/counter-reading-060/actual-current-1791197167969609900/receipt.json')
    assert actual['passed'] and actual['whole_source_half_remains_unknown']
    check_hashes(actual['source_sha256_after'])
    for case in actual['cases']:
        assert sha(ROOT / case['path']) == case['sha256']
        evidence[case['path']] = case['sha256']
    # All current code/data covered by CORE plus changed batch tools and docs.
    files = {ROOT / name for name in core['source_sha256_after'] if not name.startswith('.cache/')}
    files.update((ROOT / 'scripts').glob('*_060.py'))
    files.update((ROOT / 'tests').glob('*_060.py'))
    files.update(ROOT / name for name in ('pyproject.toml', 'run.cmd', 'WORK_IN_PROGRESS.md',
                 'PROJECT_PROGRESS.md', 'PROJECT_COMPLETED.md', 'BATCH_0.60.md'))
    current = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}
    check_hashes(evidence)
    result = {'version': '0.60.0', 'passed': True, 'verified_at': time.time(),
              'source_sha256': current, 'receipt_sha256': evidence,
              'core_tests_run': core['tests_run'], 'current_tests_passed': core['current_tests_passed'],
              'historical_skipped': core['historical_tests_skipped'], 'numeric_exact_cases': 732,
              'all_priority_1_completed': False, 'private_state_copied': False,
              'game_actions': 0, 'chat_requests': 0, 'automation_recreated': False,
              'scope': 'Direct current batch code/tests/reports; historical receipts retained without recursive rewriting.'}
    with (ROOT / 'FINAL_0.60_VERIFICATION.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps({'passed': True, 'source_files': len(current), 'evidence_files': len(evidence),
                      'current_tests_passed': core['current_tests_passed']}))


if __name__ == '__main__':
    main()
