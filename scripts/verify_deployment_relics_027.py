"""Deployment and resident-stage public acceptance, with bounded receipts."""
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
from rouge.catalog import catalog, stage_previews
from rouge.damage import calculate_damage
from rouge.deployment import finish_deployment
from rouge.relics import mechanics, prepare
from tests.test_deployment_relics_027 import BIND, FIRE, STAGES, scenario, target

DEST = ROOT / '.cache/relic-027'


def main():
    DEST.mkdir(exist_ok=True)
    start = time.perf_counter()
    names = ['tests.test_deployment_relics_027', 'tests.test_received_sp_026',
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
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)
        tested = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    assert tested.wasSuccessful(), 'See .cache/relic-027/tests.log'
    matrix = 0
    for op, profile in catalog()['operators'].items():
        for skill in range(1, len(profile['skills']) + 1):
            for mode in ('frames', 'continuous'):
                args = {'operator': op, 'skill': skill, 'timing_mode': mode}
                base = calculate_damage(args)
                contexts = [{}] + [{'deployment_hp_ratio': ratio, 'deployment_loss_unused': unused}
                                  for ratio in (0, .65, 1) for unused in (0, 1)]
                for context in contexts:
                    inputs = {**args, 'relic_ids': [BIND], 'relic_context': context}
                    before = copy.deepcopy(inputs)
                    result = calculate_damage(inputs)
                    assert inputs == before
                    assert result['estimate']['base_stats'] == base['estimate']['base_stats'], (op, skill)
                    for field in ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'total_damage',
                                  'total_healing', 'cycle_dps', 'cycle_hps'):
                        assert result['estimate']['skill'][field] == base['estimate']['skill'][field], (op, skill, field)
                    ref = result['deployment_reference']
                    assert result['deployment_cost'] is None and ref['cost']['actual_cost'] is None
                    loss = ref['hp_loss'][0]
                    if context:
                        hp = base['estimate']['base_stats']['hp'] * context['deployment_hp_ratio']
                        expected = hp * (.3 if context['deployment_loss_unused'] else 1)
                        assert math.isclose(loss['hp_after_loss'], expected, abs_tol=1e-9)
                    else:
                        assert loss['hp_after_loss'] is None
                    matrix += 1
    resident_cases = 0
    for sid in STAGES:
        for enemy in stage_previews()[sid]['possible_enemies']:
            for grade in (None, 0, 5, 10, 15):
                args = scenario(target_enemy={'stage_id': sid, 'enemy_id': enemy['id'], 'level': enemy['level']})
                if grade is not None:
                    args['run_config'] = {'difficulty': {'value': grade}, 'zone': {'id': 'zone_3'}}
                base = calculate_damage(args)
                result = calculate_damage({**args, 'relic_ids': [FIRE], 'relic_context': {'fire_rod_stacks': 0}})
                hp = base['run_resolution']['enemy']['stats']['maxHp']
                assert math.isclose(result['run_resolution']['enemy']['stats']['maxHp'], hp * .6, abs_tol=1e-8)
                assert result['total_damage'] == base['total_damage']
                assert result['estimate']['skill']['cycle_seconds'] == base['estimate']['skill']['cycle_seconds']
                resident_cases += 1
    combination_cases = 0
    guarded_cases = 0
    others = [rid for rid, record in mechanics()['relics'].items() if rid != FIRE and any(
        e['kind'] == 'enemy_hp_factor' for e in record['effects'])]
    for sid in STAGES:
        for rid in others:
            args = scenario(target_enemy=target(sid), relic_ids=[rid],
                relic_context={'fire_rod_stacks': 0, 'entered_zone_count': 2})
            base = calculate_damage(args)
            result = calculate_damage({**args, 'relic_ids': [rid, FIRE]})
            effects = result['relic_resolution']['enemy_effects']
            before = base['run_resolution']['enemy']['stats']['maxHp']
            if effects['hp_composition_pending']:
                assert result['run_resolution']['enemy']['stats']['maxHp'] == before
                assert not result['relic_resolution']['complete']
                guarded_cases += 1
            else:
                assert math.isclose(result['run_resolution']['enemy']['stats']['maxHp'], before * .6, abs_tol=1e-8)
            combination_cases += 1
    # Synthetic canonical source examples, deliberately separate from the
    # public cultivation matrix. No claim of game acquisition or real HP.
    canonical = []
    for ratio, unused, lost, remaining in ((2/3, 1, 1400, 600),
            (2/3, 0, 0, 2000), (1, 1, 2100, 900)):
        _, resolution = prepare(scenario(relic_ids=[BIND], base_attack=1,
            relic_context={'deployment_hp_ratio': ratio, 'deployment_loss_unused': unused}),
            catalog()['operators']['mechanist'])
        result = {'estimate': {'base_stats': {'hp': 3000}}}
        finish_deployment(result, resolution, {'deployment_cost': 20})
        actual = result['deployment_reference']['hp_loss'][0]
        assert math.isclose(actual['lost_hp'], lost, abs_tol=1e-9)
        assert math.isclose(actual['hp_after_loss'], remaining, abs_tol=1e-9)
        assert result['deployment_reference']['cost']['unrounded_rune_reference'] == 10
        canonical.append({'max_hp': 3000, 'ratio': ratio, 'loss_unused': unused,
                          'expected_loss': lost, 'expected_remaining': remaining, 'passed': True})
    old = json.loads((ROOT / '.cache/batch-027-before/rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))
    new = mechanics()
    changed = [rid for rid, record in new['relics'].items() if record != old['relics'][rid]]
    assert set(changed) == {BIND, FIRE}
    assert new['char_buffs'] == old['char_buffs']
    receipt = {'version': '0.27.0', 'passed': True, 'verified_at': time.time(),
        'seconds': round(time.perf_counter() - start, 3), 'tests': tested.testsRun,
        'new_tests': unittest.defaultTestLoader.loadTestsFromName('tests.test_deployment_relics_027').countTestCases(),
        'skill_matrix_cases': matrix, 'matrix_modes': ['frames', 'continuous'],
        'resident_stage_ids': list(STAGES), 'resident_enemy_difficulty_cases': resident_cases,
        'hp_combination_cases': combination_cases, 'hp_combinations_guarded': guarded_cases,
        'synthetic_canonical_examples': canonical, 'changed_relic_ids': changed,
        'changed_char_buff_ids': [], 'data_rule_counts': new['counts'],
        'source_sha256_files': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
            'rouge/relics.py', 'rouge/deployment.py', 'rouge/run_modifiers.py', 'rouge/reporting.py',
            'rouge/app.py', 'rouge/data/relic-mechanics.json', 'scripts/build_relic_mechanics.py',
            'tests/test_deployment_relics_027.py', 'tests/test_relic_candidates_025.py')},
        'game_actions': 0, 'chat_requests': 0, 'new_live_combat_measurements': 0,
        'limits': ['Deployment HP is an explicit offline event reference, not live lifecycle tracking.',
            'Cost rune values stay unrounded; actual deductions and skill/trait discounts are unknown.',
            'Resident HP applies only to eight pinned stages; mixed HP relic scripts remain unverified.',
            'These public matrices are regression coverage, not combat accuracy or new recognition measurements.']}
    (ROOT / 'RELIC_0.27_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('passed', 'tests', 'new_tests', 'skill_matrix_cases',
        'resident_enemy_difficulty_cases', 'hp_combination_cases', 'hp_combinations_guarded', 'seconds')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
