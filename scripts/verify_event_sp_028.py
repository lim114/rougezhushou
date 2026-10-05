"""Outgoing-SP public boundaries, selector matrix, and independent frame oracle."""
import copy
import hashlib
import json
import math
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from scripts.verify_received_sp_026 import oracle
from tests.test_event_sp_028 import HORN, WAVE, BOOK
from tests.test_received_sp_026 import BLOOM, TANK

DEST = ROOT / '.cache/relic-028'
TYPES = ('attack', 'damage', 'elemental_loss', 'dealt_damage', 'kill')


def events(times):
    return [{'at_seconds': t, 'type': kind} for t in times for kind in TYPES]


def main():
    DEST.mkdir(exist_ok=True)
    start = time.perf_counter()
    names = ['tests.test_event_sp_028', 'tests.test_deployment_relics_027', 'tests.test_received_sp_026',
        'tests.test_relic_candidates_025', 'tests.test_mantra_events_024', 'tests.test_relic_events_022',
        'tests.test_damage', 'tests.test_timing', 'tests.test_relics', 'tests.test_relic_extension',
        'tests.test_difficulty_rules', 'tests.test_wine_timing', 'tests.test_relic_conditions_022',
        'tests.test_report', 'tests.test_target_memory', 'tests.test_run_modifiers']
    names += ['tests.test_enemy_environment.EnemyEnvironmentTests.' + name for name in (
        'test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
        'test_portal_keeps_main_depth_and_missing_context_does_not_guess',
        'test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
        'test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense')]
    with (DEST / 'tests.log').open('w', encoding='utf-8') as log:
        tested = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tested.wasSuccessful(), 'See .cache/relic-028/tests.log'
    matrix = skills = 0
    samples = []
    for op, profile in catalog()['operators'].items():
        for number in range(1, len(profile['skills']) + 1):
            skills += 1
            for mode in ('frames', 'continuous'):
                args = {'operator': op, 'skill': number, 'timing_mode': mode}
                plain = calculate_damage(args)
                duration = plain['estimate']['skill']['duration_seconds'] or 0
                variants = [('missing', None), ('empty', {'initial': [], 'cycle': []}),
                    ('sparse', {'initial': events([1, 2, 3]), 'cycle': events([duration + 1, duration + 2, duration + 3])}),
                    ('burst', {'initial': events([1] * 20), 'cycle': events([duration + 1] * 20)}),
                    ('initial_only', {'initial': events([1, 2, 3])})]
                for rid in (HORN, WAVE):
                    empty = calculate_damage({**args, 'relic_ids': [rid], 'timing': {'sp_events': {'initial': [], 'cycle': []}}})
                    for name, table in variants:
                        scenario = {**args, 'relic_ids': [rid]}
                        if table is not None:
                            scenario['timing'] = {'sp_events': table}
                        before = copy.deepcopy(scenario)
                        result = calculate_damage(scenario)
                        assert scenario == before
                        assert result['estimate']['base_stats'] == plain['estimate']['base_stats']
                        assert not result['relic_resolution']['token_effects']
                        for key in ('total_damage', 'total_healing', 'interval_seconds', 'components'):
                            assert result.get(key) == plain.get(key), (op, number, rid, name, key)
                        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps', 'cycle_hps'):
                            value = result['estimate']['skill'][key]
                            assert value is None or math.isfinite(value) and value >= 0, (op, number, rid, name, key)
                        if name in ('sparse', 'burst'):
                            for key in ('initial_seconds', 'recharge_seconds'):
                                value = result['estimate']['skill'][key]
                                baseline = empty['estimate']['skill'][key]
                                if value is not None and baseline is not None:
                                    assert value <= baseline + 1e-8, (op, number, mode, rid, name, key)
                        for phase, ref in result['estimate'].get('sp_events', {}).items():
                            if ref['status'] == 'missing':
                                assert not result['relic_resolution']['complete']
                                field = 'initial_seconds' if phase == 'initial' else 'recharge_seconds'
                                assert result['estimate']['skill'][field] is None
                            if name == 'burst':
                                assert ref['events_supplied'] == 100
                        matrix += 1
                    samples.append({'operator': op, 'skill': number, 'mode': mode, 'relic': rid,
                        'event_rule_applies': bool(empty['estimate'].get('sp_events'))})
    assert skills == 87 and matrix == 1740, (skills, matrix)
    oracles = []
    variants = [
        ('horn', 'mechanist', 3, [HORN], [], {}, {'kill': 2}, 10, 35, 40),
        ('horn_incoming', 'mechanist', 3, [HORN, BLOOM], [TANK], {},
            {'kill': 2, 'attack': 2, 'damage': 1, 'elemental_loss': 1}, 10, 35, 40),
        ('wave', 'char_328_cammou', 2, [WAVE], [], {}, {'dealt_damage': 2}, 25, 45, 30),
        ('wave_horn', 'char_328_cammou', 2, [WAVE, HORN], [], {}, {'dealt_damage': 2, 'kill': 2}, 25, 45, 30),
        ('wave_horn_book', 'char_328_cammou', 2, [WAVE, HORN, BOOK], [], {'deployed_casters': 2},
            {'dealt_damage': 2, 'kill': 2}, 25, 39, 30)]
    for name, op, number, ids, bindings, context, amounts, deficit, cost, duration in variants:
        for block in (0, 2, 3.25):
            for times in ([], [1, 2, 3], [.001, 1.001, 2.001], [1] * 20):
                initial = events(times)
                cycle = events([1, duration - .1, duration] + [duration + block + t for t in times])
                result = calculate_damage({'operator': op, 'skill': number, 'relic_ids': ids,
                    'char_buff_ids': bindings, 'relic_context': context,
                    'timing': {'sp_lockout_extra_seconds': block, 'sp_events': {'initial': initial, 'cycle': cycle}}})
                expected_initial = oracle(deficit, 1, initial, amounts)
                expected_cycle = oracle(cost, 1, cycle, amounts, offset=duration, block=math.ceil(block * 30) / 30)
                skill = result['estimate']['skill']
                assert abs(skill['initial_seconds'] - expected_initial) < 1e-8, (name, block, times)
                assert abs(skill['recharge_seconds'] - expected_cycle) < 1e-8, (name, block, times)
                oracles.append({'rules': name, 'block': block, 'times': times,
                    'initial': expected_initial, 'recharge': expected_cycle})
    wine_args = {'operator': 'mechanist', 'skill': 1, 'continuous_attacks': False,
        'relic_ids': [HORN, 'rogue_6_relic_legacy_97']}
    duration = calculate_damage(wine_args)['estimate']['skill']['duration_seconds']
    table = {'initial': [{'at_seconds': .2, 'type': 'kill'}],
             'cycle': [{'at_seconds': duration + .2, 'type': 'kill'}]}
    wine = calculate_damage({**wine_args, 'timing': {'sp_events': table}})['estimate']['skill']
    for key, need, offset, phase_table in (('initial_seconds_range', 2, 0, table['initial']),
                                         ('recharge_seconds_range', 7, duration, table['cycle'])):
        values = [oracle(need, 0, phase_table, {'kill': 2}, offset=offset, wine_phase=p) for p in range(46)]
        assert all(v is not None for v in values)
        assert abs(wine[key]['lower'] - min(values)) < 1e-8
        assert abs(wine[key]['upper'] - max(values)) < 1e-8
    current = mechanics()
    old = json.loads((ROOT / '.cache/batch-028-before/rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))
    changed = [rid for rid, data in current['relics'].items() if data != old['relics'][rid]]
    assert set(changed) == {HORN, WAVE}, changed
    assert current['char_buffs'] == old['char_buffs']
    raw_path = ROOT / '.cache/game-data/roguelike_topic_table.json'
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert raw_sha == current['source_sha256']
    raw = json.loads(raw_path.read_text(encoding='utf-8'))['details']['rogue_6']
    evidence = {'source_commit': current['commit'], 'source_sha256': raw_sha, 'source_url': current['source_url'],
        'changed_relics': changed, 'changed_bindings': [],
        'raw_buffs': {rid: raw['relics'][rid]['buffs'] for rid in (HORN, WAVE, BOOK)},
        'rules': {rid: current['relics'][rid] for rid in (HORN, WAVE, BOOK)},
        'web_sources': ['https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目',
            'https://prts.wiki/w/游戏数据基础#异常效果（AbnormalFlag）'],
        'independent_oracles': oracles, 'wine_phases': 46, 'matrix': samples}
    (DEST / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    files = ('scripts/build_relic_mechanics.py', 'rouge/relics.py', 'rouge/sp_events.py', 'rouge/timing.py',
        'rouge/damage.py', 'rouge/estimate.py', 'rouge/operator_engine.py', 'rouge/reporting.py', 'rouge/app.py',
        'rouge/data/relic-mechanics.json', 'tests/test_event_sp_028.py', 'scripts/verify_event_sp_028.py')
    receipt = {'version': '0.28.0', 'passed': True, 'verified_at': time.time(), 'tests': tested.testsRun,
        'new_tests': unittest.TestLoader().loadTestsFromName('tests.test_event_sp_028').countTestCases(),
        'seconds': round(time.perf_counter() - start, 3), 'skill_matrix_skills': skills,
        'skill_matrix_cases': matrix, 'matrix_modes': ['frames', 'continuous'],
        'independent_oracle_cases': len(oracles), 'wine_oracle_phases': 46,
        'changed_relics': changed, 'changed_bindings': [], 'data_rule_counts': current['counts'],
        'source_commit': current['commit'], 'source_sha256': raw_sha,
        'source_sha256_files': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files},
        'evidence': '.cache/relic-028/evidence.json', 'chat_requests': 0, 'game_actions': 0,
        'limits': ['Only explicit own-unit successful-damage and kill callback scenarios; no live combat scan.',
            'Wave plus Book attack-stack refresh, ownership and per-hit values remain unknown.',
            'Non-forced SP blocking, next tick and simultaneous callback order remain reference assumptions.',
            'One initial and one cycle, not repeated steady state; no token callback inheritance.',
            'Wine phase remains a marginal envelope; hidden blocking and same-key wine stacking unknown.',
            'Recognition unchanged; no new speed or inventory-reading measurement.']}
    (ROOT / 'RELIC_0.28_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('version', 'passed', 'tests', 'new_tests', 'skill_matrix_cases',
        'independent_oracle_cases', 'wine_oracle_phases', 'seconds', 'data_rule_counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
