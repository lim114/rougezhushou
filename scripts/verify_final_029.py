"""Assemble observed 0.29 evidence; private state is read-only, tasks stay ended."""
import compileall
import hashlib
import json
import statistics
import sys
import time
import tomllib
from pathlib import Path

import win32gui
import win32process

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.relic_recognition import ProjectionScreen


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    tests = read('TEST_0.29_VERIFICATION.json')
    recognition = read('RECOGNITION_0.29_VERIFICATION.json')
    paired = read(recognition['evidence'])
    ui = read('UI_0.29_VERIFICATION.json')
    launch = read('APP_0.29_LAUNCH_VERIFICATION.json')
    audit = read('RELIC_VERIFICATION.json')
    previous_calculation = read('RELIC_0.28_VERIFICATION.json')
    for proof in (tests, recognition, ui, launch, audit):
        assert proof['version'] == '0.29.0'
    assert tests['passed'] and tests['tests'] == 285 and tests['new_tests'] == 12
    assert tests['failures'] == 0 and tests['errors'] == 0
    assert recognition['passed'] and recognition['paired_visual_cases'] == 14
    assert recognition['public_reader_cases'] == 5
    assert recognition['exact_records_scores_centers_preserved']
    assert recognition['warm_comparison_repeats_per_version'] == 3
    assert len(paired['rows']) == 14 and len(paired['public']) == 5
    assert all(row['identical_records_scores_centers'] for row in paired['rows'])
    assert all(row['identical_public_run_and_page'] for row in paired['public'])
    assert ProjectionScreen.max_cache_bytes == 8 * 1024 * 1024
    assert ProjectionScreen.max_cache_entries == 32
    assert recognition['max_projection_cache_bytes'] <= ProjectionScreen.max_cache_bytes
    assert recognition['max_projection_cache_entries'] <= ProjectionScreen.max_cache_entries
    assert recognition['source_sha256'] == paired['source_sha256'] == digest(ROOT / 'rouge/relic_recognition.py')
    assert recognition['baseline_source_sha256'] == paired['baseline_source_sha256'] == digest(
        ROOT / '.cache/batch-029-before/rouge/relic_recognition.py')
    timings = []
    for row in paired['rows']:
        stats = row['after_counts']
        assert stats.get('peak_window_cache_bytes', 0) <= ProjectionScreen.max_cache_bytes
        assert stats.get('peak_window_cache_entries', 0) <= ProjectionScreen.max_cache_entries
        if 'before_warm_ms' not in row:
            continue
        assert len(row['before_warm_ms']) == len(row['after_warm_ms']) == 3
        before = statistics.median(row['before_warm_ms'])
        after = statistics.median(row['after_warm_ms'])
        assert before == row['before_median_ms'] and after == row['after_median_ms']
        assert before / after == row['speedup'] and after < before
        timings.append({'case': row['case'], 'before_median_ms': before, 'after_median_ms': after,
            'time_reduction_percent': 100 * (1 - after / before),
            'rgb_screen_calls_before': row['before_counts']['rgb_screen_calls'],
            'rgb_screen_calls_after': row['after_counts']['rgb_screen_calls']})
    assert len(timings) == 2
    assert ui['passed'] and ui['skill_option_visibility_cases'] == 87
    assert ui['private_state_isolated'] and ui['no_irrelevant_special_fields']
    assert ui['game_captures'] == 0 and ui['chat_requests'] == 0
    assert launch['only_one_project_window'] and launch['same_run_preserved'] and launch['history_preserved']
    assert launch['settings_and_bindings_unchanged'] and launch['run_cmd_startup_verified']
    assert launch['launcher_sha256'] == digest(ROOT / 'run.cmd')
    assert audit['audit_count'] == 272 and audit['public_entry_cases'] == 8704
    assert audit['bound_recipient_cases'] == 609 and audit['forbidden_skill_cases'] == 87
    assert read('TARGET_ICON_VERIFICATION.json')['count'] == 15
    for proof, field in ((tests, 'source_sha256'), (ui, 'source_sha256'), (audit, 'source_hashes')):
        for name, checksum in proof[field].items():
            assert digest(ROOT / name) == checksum, name
    # The batch changes recognition only, plus the displayed/project version.
    for name, checksum in previous_calculation['source_sha256_files'].items():
        if name != 'rouge/app.py':
            assert digest(ROOT / name) == checksum, name
    old_app = (ROOT / '.cache/batch-029-before/rouge/app.py').read_text(encoding='utf-8')
    assert old_app.replace('0.28', '0.29') == (ROOT / 'rouge/app.py').read_text(encoding='utf-8')
    new = read('rouge/data/relic-mechanics.json')
    assert new['counts'] == {'numeric': 118, 'conditional': 27, 'partial': 12, 'pending': 63, 'non_output': 52}
    assert new['counts'] == audit['data_rule_counts'] == previous_calculation['data_rule_counts']
    checkpoint = read('.cache/upgrade-0.29-checkpoint.json')
    run = read('.local/run-state.json')
    assert hashlib.sha256(str(run.get('id')).encode()).hexdigest() == checkpoint['run_id_hash']
    assert checkpoint['history_count'] > 0
    prefix = run['history'][:checkpoint['history_count']]
    assert hashlib.sha256(json.dumps(prefix, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == checkpoint['history_prefix_hash']
    for name, checksum in checkpoint['config_hashes'].items():
        assert digest(ROOT / name) == checksum, name
    live = []

    def visit(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title.startswith('黑流树海助手'):
            live.append({'title': title, 'pid': win32process.GetWindowThreadProcessId(hwnd)[1]})

    win32gui.EnumWindows(visit, None)
    assert len(live) == 1 and '0.29' in live[0]['title']
    assert live[0]['pid'] == launch['process_id']
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    assert version == '0.29.0'
    ended = read('.cache/automation-ended-028.json')
    assert ended['automation_id'] == '1-3' and ended['app_delete_result'] == 'deleted'
    assert not Path(r'C:\Users\李娜\.codex\automations\1-3\automation.toml').exists()
    assert all(compileall.compile_dir(str(ROOT / folder), quiet=2) for folder in ('rouge', 'scripts', 'tests'))
    files = ('BATCH_0.29.md', 'PROJECT_PROGRESS.md', 'WORK_IN_PROGRESS.md', 'README.md',
        'RELIC_MECHANICS.md', 'RELIC_COVERAGE.md', '.cache/recognition-029/paired-replay.json',
        '.cache/recognition-029/probe.json', '.cache/recognition-029/projection-probe.json',
        '.cache/automation-ended-028.json', 'scripts/verify_projection_recognition_029.py',
        'scripts/verify_projection_batch_029.py', 'scripts/verify_projection_ui_029.py',
        'scripts/verify_final_029.py', 'tests/test_projection_screen_029.py', '.cache/verify-launch-0.29.py',
        'TEST_0.29_VERIFICATION.json', 'RECOGNITION_0.29_VERIFICATION.json', 'UI_0.29_VERIFICATION.json',
        'APP_0.29_LAUNCH_VERIFICATION.json', 'RELIC_VERIFICATION.json', 'TARGET_ICON_VERIFICATION.json')
    receipt = {'version': version, 'passed': True, 'verified_at': time.time(),
        'checks': ['285 relevant regressions, including 12 new projection tests',
            '14 exact paired identities/candidates/scores/centers and 5 public structured reads',
            'Two alternating warm benchmarks, three reads per version, no image-result cache',
            'Per-current-bar projection window cache <= 8 MiB and <= 32 entries',
            '87 skills isolated UI options; no irrelevant special fields',
            '8704 relic public entries; 609 bindings; 87 forbidden skills',
            '15 bound icon hashes; compileall', 'Actual run.cmd launch and one 0.29 window',
            'Same run, nonempty history prefix and existing private config hashes preserved',
            'Calculation data/engine hashes unchanged from 0.28',
            'Recurring task deletion receipt and absent manifest'],
        'tests': tests['tests'], 'new_tests': tests['new_tests'],
        'paired_visual_cases': len(paired['rows']), 'public_reader_cases': len(paired['public']),
        'held_icon_timings': timings, 'changed_relic_ids': [], 'changed_char_buff_ids': [],
        'data_rule_counts': new['counts'], 'history_count_before': checkpoint['history_count'],
        'history_count_after': len(run['history']), 'configuration_files_verified': list(checkpoint['config_hashes']),
        'process_id': live[0]['pid'], 'automation_id': '1-3', 'automation_status': 'DELETED',
        'automatic_development_will_resume': False, 'all_priorities_1_to_3_completed': False,
        'new_game_actions': 0, 'chat_requests': 0, 'new_live_validation_captures': 0,
        'new_live_combat_measurements': 0, 'evidence_sha256': {name: digest(ROOT / name) for name in files},
        'limits': ['Development fixtures and controlled transforms, not independent whole-inventory accuracy.',
            'Only held-icon matching timed in alternating comparisons; full-reader OCR timings are not attribution.',
            'Transformed matcher tests carry recorded label geometry; public reads rediscover current anchors.',
            'The additional 8 MiB limit bounds the projection window cache, not the application total.',
            'No new relic mechanism, targeted-recipient positive sample, or actual stacking validation.',
            'P1-3 still have documented remaining work.']}
    (ROOT / 'FINAL_0.29_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'version': version, 'passed': True, 'tests': tests['tests'],
        'history_count': len(run['history']), 'process_id': live[0]['pid'],
        'automation_status': 'DELETED'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
