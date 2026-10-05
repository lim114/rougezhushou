"""Bounded collectible acceptance through the public calculation interface."""
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.catalog import catalog, stage_previews
from rouge.damage import calculate_damage
from rouge.relics import mechanics

DEST = ROOT / '.cache/relic-025'
FIRE = 'rogue_6_relic_cargo_11'
COOKIE = 'rogue_6_from_relic_15'
GRAVITY = 'rogue_6_relic_legacy_56'
TARGET = {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_2137_shsdgo', 'level': 0}


def numeric_output(result):
    return {key: result.get(key) for key in ('total_damage', 'total_healing', 'interval_seconds', 'components')} | {
        'base_stats': result['estimate']['base_stats'], 'skill': result['estimate']['skill']}


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    names = ['tests.test_relic_candidates_025', 'tests.test_mantra_events_024',
             'tests.test_relic_events_022', 'tests.test_damage', 'tests.test_timing',
             'tests.test_relics', 'tests.test_relic_extension', 'tests.test_difficulty_rules',
             'tests.test_wine_timing', 'tests.test_relic_conditions_022']
    # Enemy-environment calculation tests; the expensive OCR replay was unchanged.
    names += ['tests.test_enemy_environment.EnemyEnvironmentTests.' + name for name in (
        'test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
        'test_portal_keeps_main_depth_and_missing_context_does_not_guess',
        'test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
        'test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense')]
    with (DEST / 'tests.log').open('w', encoding='utf-8') as stream:
        tested = unittest.TextTestRunner(stream=stream, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromNames(names))
    cases = 0
    skill_count = 0
    for op, profile in catalog()['operators'].items():
        for number, skill in enumerate(profile['skills'], 1):
            skill_count += 1
            for mode in ('frames', 'continuous'):
                args = {'operator': op, 'skill': number, 'timing_mode': mode}
                plain = calculate_damage(args)
                for count in (0, 3, 99):
                    actual = calculate_damage({**args, 'relic_ids': [FIRE],
                                               'relic_context': {'fire_rod_stacks': count}})
                    expected = calculate_damage({**args, 'effects': [{'kind': 'attack_speed', 'value': 10 * count}]})
                    assert numeric_output(actual) == numeric_output(expected), (op, number, mode, count)
                    assert actual['estimate']['base_stats']['attack_speed'] <= 600
                    assert not actual['relic_resolution']['token_effects']
                    cases += 1
                bound = calculate_damage({**args, 'char_buff_ids': [COOKIE]})
                natural = skill['levels'][9]['sp_type'] == 'INCREASE_WITH_TIME'
                expected = calculate_damage({**args, 'effects': [{'kind': 'sp_recovery', 'value': .8}]}) if natural else plain
                assert numeric_output(bound) == numeric_output(expected), (op, number, mode, 'cookie')
                assert not bound['relic_resolution']['token_effects']
                cases += 1
                mixed = calculate_damage({**args, 'relic_ids': [FIRE], 'char_buff_ids': [COOKIE],
                                          'relic_context': {'fire_rod_stacks': 3}})
                effects = [{'kind': 'attack_speed', 'value': 30}] + ([{'kind': 'sp_recovery', 'value': .8}] if natural else [])
                expected = calculate_damage({**args, 'effects': effects})
                assert numeric_output(mixed) == numeric_output(expected), (op, number, mode, 'mixed')
                cases += 1
                target_args = {**args, 'target_enemy': TARGET}
                actual = calculate_damage({**target_args, 'relic_ids': [GRAVITY]})
                expected = calculate_damage(target_args)
                assert numeric_output(actual) == numeric_output(expected), (op, number, mode, 'weight')
                assert actual['run_resolution']['enemy']['stats']['massLevel'] == 1
                cases += 1
    assert skill_count == 87, skill_count
    raw_path = ROOT / '.cache/game-data/roguelike_topic_table.json'
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert raw_hash == mechanics()['source_sha256']
    raw = json.loads(raw_path.read_text(encoding='utf-8'))['details']['rogue_6']
    evidence = {rid: {'raw_buffs': raw['relics'][rid]['buffs'],
                      'implemented': mechanics()['relics'][rid]['effects'],
                      'status': mechanics()['relics'][rid]['status'],
                      'pending': mechanics()['relics'][rid]['pending']}
                for rid in (FIRE, 'rogue_6_relic_assign_15', GRAVITY)}
    evidence['cookie_binding'] = mechanics()['char_buffs'][COOKIE]
    level_receipt = json.loads((ROOT / '.cache/game-data/level-receipt.json').read_text(encoding='utf-8'))
    weights = []
    for sid, eid, initial, final in (
            ('ro6_n_1_2', 'enemy_2137_shsdgo', 3, 1),
            ('ro6_n_1_2', 'enemy_1093_ccsbr', 1, -1),
            ('ro6_n_1_1', 'enemy_2133_shdopl', 0, -2)):
        enemy = next(e for e in stage_previews()[sid]['possible_enemies'] if e['id'] == eid)
        assert enemy['reference_stats']['massLevel'] == initial
        result = calculate_damage({'operator': 'mechanist', 'skill': 3, 'relic_ids': [GRAVITY],
                                   'target_enemy': {'stage_id': sid, 'enemy_id': eid, 'level': 0}})
        assert result['run_resolution']['enemy']['stats']['massLevel'] == final
        weights.append({'stage_id': sid, 'enemy_id': eid, 'reference_weight': initial, 'result_weight': final})
    evidence['weight_examples'] = weights
    (DEST / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    receipt = {'version': '0.25.0', 'verified_at': time.time(), 'tests': tested.testsRun,
        'failures': len(tested.failures), 'errors': len(tested.errors), 'matrix_cases': cases,
        'matrix_skills': skill_count, 'matrix_modes': ['frames', 'continuous'],
        'passed': tested.wasSuccessful(), 'seconds': round(time.perf_counter() - start, 3),
        'data_rule_counts': mechanics()['counts'], 'source_commit': mechanics()['commit'],
        'source_sha256': raw_hash, 'enemy_data_commit': level_receipt['commit'],
        'source_sha256_files': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
            'scripts/build_relic_mechanics.py', 'scripts/build_previews.py', 'rouge/relics.py',
            'rouge/enemy_environment.py', 'rouge/run_modifiers.py', 'rouge/damage.py',
            'rouge/estimate.py', 'rouge/operator_engine.py', 'rouge/reporting.py',
            'rouge/app.py', 'rouge/data/relic-mechanics.json', 'rouge/data/previews.json',
            'tests/test_relic_candidates_025.py')},
        'evidence': '.cache/relic-025/evidence.json', 'chat_requests': 0, 'game_actions': 0,
        'limits': ['Only explicit stack counts and recipient bindings are accepted.',
                  'Resident-stage HP script and repeat binding stacking remain unverified.',
                  'Weight correction is a parameter reference, not displacement or damage prediction.',
                  'No new live candidate relic capture or animation calibration was available.',
                  'Focused calculation regressions were run; unchanged full OCR suite was not repeated.']}
    (ROOT / 'RELIC_0.25_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('version', 'tests', 'matrix_cases', 'matrix_skills', 'passed', 'seconds', 'data_rule_counts')}, ensure_ascii=False))
    raise SystemExit(0 if tested.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
