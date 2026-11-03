"""Root actual Linux/Wine regressions with the original availability classifier."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import unittest


def source_map(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ('rouge', 'tests', 'scripts')
            for p in sorted((root / folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser()
    for key in ('root', 'guard', 'output'):
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--wine', action='store_true')
    args = parser.parse_args()
    root, output = Path(args.root).resolve(), Path(args.output).resolve()
    assert not output.exists() and not output.with_suffix('.log').exists()
    guard = json.loads(Path(args.guard).read_bytes())
    before = source_map(root)
    assert guard['section'] == 108 and before == guard['source_sha256'] and len(before) == 751
    extra = {p: hashlib.sha256((root / p).read_bytes()).hexdigest()
             for p in guard['source_additional_sha256']}
    assert extra == guard['source_additional_sha256']
    selectors = ['tests.test_zone_environment_input_108', 'tests.test_environment_input_106', 'tests.test_run_config_validation', 'tests.test_run_config', 'tests.test_run_modifiers', 'tests.test_run_state_reliability', 'tests.test_enemy_environment', 'tests.test_enemy_rune_selectors', 'tests.test_battle_preview_039', 'tests.test_enemy_skills_042', 'tests.test_aglna_gravity_weight_107', 'tests.test_training_input_types', 'tests.test_training_view_100', 'tests.test_relics', 'tests.test_relic_resolution_052', 'tests.test_relic_scope_052']
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / 'scripts'))
    from verify_full_available import AvailableResult
    started = time.perf_counter()
    with output.with_suffix('.log').open('x', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=1, resultclass=AvailableResult).run(
            unittest.defaultTestLoader.loadTestsFromNames(selectors))
    after = source_map(root)
    extra_after = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in extra}
    drift = [p for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    receipt = {
        'section': 108, 'platform': platform.system(), 'wine_compatibility': args.wine,
        'available_checks_passed': result.wasSuccessful() and not drift and extra_after == extra,
        'tests_run': result.testsRun, 'tests_passed': result.passed_count,
        'unavailable': result.unavailable, 'unavailable_parent_count': len(result.unavailable_parents),
        'skipped': len(result.skipped),
        'skips': [{'test': t.id(), 'reason': why} for t, why in result.skipped],
        'failures': len(result.failures), 'errors': len(result.errors),
        'failed_cases': [{'test': t.id(), 'reason': reason} for t, reason in result.failures + result.errors],
        'selectors': selectors, 'source_sha256': before, 'source_after': after,
        'source_additional_sha256': extra, 'source_additional_after': extra_after,
        'source_drift': drift, 'elapsed_seconds': time.perf_counter() - started,
        'original_assertions_and_classifier_unchanged': True,
        'native_windows_game_chat_verified': False,
        'scope': 'Related original maintained assertions plus new active-zone qualification tests; no full-suite claim',
    }
    with output.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({k: receipt[k] for k in (
        'available_checks_passed', 'tests_run', 'tests_passed', 'skipped',
        'unavailable_parent_count', 'failures', 'errors', 'elapsed_seconds')}))
    return 0 if receipt['available_checks_passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
