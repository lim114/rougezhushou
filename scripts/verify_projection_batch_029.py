"""Relevant calculation, recognition and queued-sampling regressions."""
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    folder = ROOT / '.cache/recognition-029'
    folder.mkdir(exist_ok=True)
    names = ['tests.test_projection_screen_029', 'tests.test_relic_screening_024',
        'tests.test_relic_recognition_022', 'tests.test_numeric_recognition_024',
        'tests.test_recognition', 'tests.test_recognition_reuse', 'tests.test_adaptive_recognition',
        'tests.test_visual_recognition', 'tests.test_difficulty_relics',
        'tests.test_capture_queue', 'tests.test_sampling_flow',
        'tests.test_event_sp_028', 'tests.test_deployment_relics_027', 'tests.test_received_sp_026',
        'tests.test_relic_candidates_025', 'tests.test_mantra_events_024', 'tests.test_relic_events_022',
        'tests.test_damage', 'tests.test_timing', 'tests.test_relics', 'tests.test_relic_extension',
        'tests.test_difficulty_rules', 'tests.test_wine_timing', 'tests.test_relic_conditions_022',
        'tests.test_report', 'tests.test_target_memory', 'tests.test_run_modifiers']
    names += ['tests.test_enemy_environment.EnemyEnvironmentTests.' + name for name in (
        'test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
        'test_portal_keeps_main_depth_and_missing_context_does_not_guess',
        'test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
        'test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense')]
    files = ('rouge/relic_recognition.py', 'rouge/recognition.py', 'rouge/recognition_cache.py',
        'rouge/run_recognition.py', 'rouge/capture.py', 'rouge/app.py', 'rouge/relics.py', 'rouge/sp_events.py',
        'rouge/estimate.py', 'rouge/operator_engine.py', 'rouge/reporting.py', 'rouge/data/relic-mechanics.json',
        'tests/test_projection_screen_029.py', 'scripts/verify_projection_batch_029.py')
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    start = time.perf_counter()
    with (folder / 'tests.log').open('w', encoding='utf-8') as log:
        tested = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tested.wasSuccessful(), '.cache/recognition-029/tests.log'
    assert before == {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    receipt = {'version': '0.29.0', 'passed': True, 'verified_at': time.time(), 'tests': tested.testsRun,
        'new_tests': unittest.TestLoader().loadTestsFromName('tests.test_projection_screen_029').countTestCases(),
        'seconds': round(time.perf_counter() - start, 3), 'failures': len(tested.failures), 'errors': len(tested.errors),
        'source_sha256': before, 'test_modules': names, 'game_actions': 0, 'chat_requests': 0,
        'limits': ['Development fixtures and synthetic inputs; no new live WGC or full-inventory accuracy claim.',
            'Native UI/capture and chat boundaries are mocked or isolated in flow tests.',
            'Changed recognition projection preserves original RGB confirmation thresholds.']}
    (ROOT / 'TEST_0.29_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('passed', 'tests', 'new_tests', 'seconds')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
