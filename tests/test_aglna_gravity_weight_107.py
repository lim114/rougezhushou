"""The selected fixed weight used by the talent must agree with the report.

Use original calculation APIs and actual public records. Negative metadata is
not a displacement rule or a zero clamp. The author compiles Source only.
"""
from copy import deepcopy
import math
import unittest

from rouge.battle_preview import enemy_preview
from rouge.catalog import catalog, stage_previews
from rouge.damage import _prepare_damage, calculate_damage
from rouge.estimate import format_estimate
from rouge.operator_engine import Combat
from rouge.reporting import format_report

OP = 'char_1015_aglna2'
GRAVITY = 'rogue_6_relic_legacy_56'
TALENT = '飘浮大地之上'
TARGETS = (
    (0, 'ro6_n_1_1', 'enemy_2133_shdopl'),
    (1, 'ro6_n_1_2', 'enemy_1093_ccsbr'),
    (2, 'ro6_n_1_1', 'enemy_2034_sythef'),
    (3, 'ro6_n_1_1', 'enemy_2001_duckmi'),
    (4, 'ro6_n_1_1', 'enemy_2002_bearmi'),
    (5, 'ro6_n_1_1', 'enemy_2085_skzjxd'),
)
CONFIG = {'difficulty': {'value': 4, 'modeDifficulty': 'NORMAL', 'mode': 'NORMAL'},
          'zone': {'id': 'zone_1'}}


def identity(record):
    return {'stage_id': record[1], 'enemy_id': record[2], 'level': 0}


def reference(record):
    return next(item['reference_stats'] for item in stage_previews()[record[1]]['possible_enemies']
                if item['id'] == record[2] and item['level'] == 0)


def request(record=None, **extra):
    result = {'operator': OP, 'skill': 1, 'skill_rank': 10, 'elite': 2,
              'potential': 1, 'base_attack': 1000, 'window_seconds': 10}
    if record is not None:
        result.update(target_enemy=identity(record), run_config=deepcopy(CONFIG))
    result.update(extra)
    return result


def manual_reference(record, weight, **extra):
    stats = reference(record)
    return request(enemy_weight=weight, enemy_defense=stats['def'],
                   enemy_resistance=stats['magicResistance'], **extra)


def talent(result):
    return next(item for item in result['components'] if item['name'] == TALENT)


def normal_plan(caller):
    prepared = _prepare_damage(caller)
    return Combat(prepared[0], prepared[1]).plan(normal=True, window=10)


class AglnaGravityWeight107Tests(unittest.TestCase):
    def test_actual_crossing_cases_match_independent_original_manual_controls(self):
        # Root original105 real controls: 2714/2914. Buggy fixed gravity cases
        # were 2590/2790, despite reports already showing weights 2/3.
        for record, weight, expected in ((TARGETS[4], 2, 2714), (TARGETS[5], 3, 2914)):
            with self.subTest(target=record[2]):
                result = calculate_damage(request(record, window_seconds=3, relic_ids=[GRAVITY]))
                control = calculate_damage(manual_reference(record, weight, window_seconds=3))
                self.assertEqual(result['total_damage'], expected)
                self.assertEqual(result['components'], control['components'])
                self.assertEqual(result['estimate']['skill'], control['estimate']['skill'])
                self.assertEqual(result['run_resolution']['enemy']['stats']['massLevel'], weight)

    def test_fixed_zero_through_five_keep_signed_metadata_and_existing_light_damage(self):
        for record in TARGETS:
            for mode in ('frames', 'continuous'):
                for skill in (1, 2, 3):
                    with self.subTest(weight=record[0], mode=mode, skill=skill):
                        args = request(record, skill=skill, timing_mode=mode)
                        plain = calculate_damage(args)
                        result = calculate_damage({**args, 'relic_ids': [GRAVITY]})
                        self.assertEqual(result['run_resolution']['enemy']['reference_stats']['massLevel'], record[0])
                        self.assertEqual(result['run_resolution']['enemy']['stats']['massLevel'], record[0] - 2)
                        if record[0] <= 3:
                            # Already on the light branch. -2/-1 metadata is
                            # retained; no invalid manual negative control.
                            self.assertEqual(result['components'], plain['components'])
                            self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
                        else:
                            control = calculate_damage(manual_reference(
                                record, {4: 2, 5: 3}[record[0]], skill=skill, timing_mode=mode))
                            self.assertEqual(result['components'], control['components'])
                            self.assertEqual(result['estimate']['skill'], control['estimate']['skill'])
                            self.assertGreater(talent(result)['per_hit'], talent(plain)['per_hit'])

    def test_cultivation_potential_and_unlocked_skill_source_coefficients_survive(self):
        record = TARGETS[4]
        qualifications = ((1, 1, .20, .13), (1, 3, .30, .18),
                          (2, 1, .35, .25), (2, 3, .45, .30))
        for elite, potential, light, heavy in qualifications:
            for skill in range(1, elite + 2):
                for mode in ('frames', 'continuous'):
                    options = {'elite': elite, 'level': 1, 'potential': potential, 'skill': skill,
                               'skill_rank': 7 if elite == 1 else 10, 'timing_mode': mode}
                    with self.subTest(options=options):
                        plain = calculate_damage(request(record, **options))
                        result = calculate_damage(request(record, relic_ids=[GRAVITY], **options))
                        control = calculate_damage(manual_reference(record, 2, **options))
                        self.assertEqual(talent(result), talent(control))
                        self.assertAlmostEqual(talent(result)['per_hit'] / talent(plain)['per_hit'], light / heavy)
                        self.assertGreater(talent(result)['hits'], 0)

    def test_original_normal_plans_use_effective_branch_and_keep_base_scenario_weight(self):
        for record in TARGETS:
            for mode in ('frames', 'continuous'):
                for elite, rank in ((0, 1), (1, 7), (2, 10)):
                    args = request(record, elite=elite, level=1, skill_rank=rank,
                                   timing_mode=mode, relic_ids=[GRAVITY])
                    before = deepcopy(args)
                    with self.subTest(weight=record[0], mode=mode, elite=elite):
                        prepared = _prepare_damage(args)
                        self.assertEqual(prepared[0]['enemy_weight'], record[0])
                        plan = Combat(prepared[0], prepared[1]).plan(normal=True, window=10)
                        control_weight = {4: 2, 5: 3}.get(record[0], record[0])
                        control = normal_plan(manual_reference(
                            record, control_weight, elite=elite, level=1, skill_rank=rank, timing_mode=mode))
                        self.assertEqual(talent(plan), talent(control))
                        self.assertEqual(args, before)
                        if elite == 0:
                            self.assertEqual((talent(plan)['hits'], talent(plan)['total']), (0, 0))

    def test_manual_without_identity_never_supplies_gravity_qualification(self):
        for mode in ('frames', 'continuous'):
            for skill in (1, 2, 3):
                for weight in (0, 2, 3, 4, 100):
                    with self.subTest(mode=mode, skill=skill, weight=weight):
                        args = request(skill=skill, timing_mode=mode, enemy_weight=weight)
                        plain = calculate_damage(args)
                        result = calculate_damage({**args, 'relic_ids': [GRAVITY]})
                        record = result['relic_resolution']['records'][0]
                        self.assertEqual(record['applied'], [])
                        self.assertIn('target_enemy', record['missing_conditions'])
                        self.assertEqual(result['components'], plain['components'])
                        self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
        for weight in (False, True, '4', None, -1, 101, 3.5, math.nan, math.inf):
            with self.subTest(invalid_weight=weight), self.assertRaisesRegex(ValueError, '手动敌人重量'):
                calculate_damage(request(enemy_weight=weight, relic_ids=[GRAVITY]))

    def test_selected_identity_keeps_precedence_over_stale_manual_values(self):
        for record in (TARGETS[0], TARGETS[4], TARGETS[5]):
            for mode in ('frames', 'continuous'):
                args = request(record, timing_mode=mode, relic_ids=[GRAVITY])
                control = calculate_damage(args)
                for stale in (0, 100, False, True, -1, '4', None):
                    with self.subTest(weight=record[0], mode=mode, stale=stale):
                        self.assertEqual(calculate_damage({**args, 'enemy_weight': stale}), control)

    def test_duplicate_inventory_and_weight_independent_mechanical_output_stay_unchanged(self):
        for record in TARGETS:
            for mode in ('frames', 'continuous'):
                with self.subTest(weight=record[0], mode=mode):
                    args = request(record, timing_mode=mode, relic_ids=[GRAVITY])
                    one = calculate_damage(args)
                    self.assertEqual(calculate_damage({**args, 'relic_ids': [GRAVITY, GRAVITY]}), one)
                    mech = request(record, operator='mechanist', timing_mode=mode, window_seconds=30)
                    plain = calculate_damage(mech)
                    result = calculate_damage({**mech, 'relic_ids': [GRAVITY]})
                    # Original three-second probes had no mechanical hits;
                    # this actual longer-window regression must be nonvacuous.
                    self.assertGreater(plain['total_damage'], 0)
                    self.assertEqual(result['components'], plain['components'])
                    self.assertEqual(result['total_damage'], plain['total_damage'])
                    self.assertEqual(result['estimate']['skill'], plain['estimate']['skill'])
                    self.assertEqual(result['run_resolution']['enemy']['stats']['massLevel'], record[0] - 2)

    def test_locked_talent_empty_enemies_and_zero_windows_do_not_create_hits(self):
        for mode in ('frames', 'continuous'):
            locked = calculate_damage(request(TARGETS[4], timing_mode=mode, elite=0,
                                      level=1, skill_rank=1, relic_ids=[GRAVITY]))
            self.assertEqual((talent(locked)['hits'], talent(locked)['total']), (0, 0))
            self.assertEqual(talent(locked)['times_seconds'], [])
            empty_cases = [{'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}}]
            if mode == 'frames':
                empty_cases.append({'timing': {'target_windows': []}})
            for empty in empty_cases:
                with self.subTest(mode=mode, boundary=empty):
                    result = calculate_damage(request(TARGETS[4], timing_mode=mode,
                                                      relic_ids=[GRAVITY], **empty))
                    self.assertEqual((talent(result)['hits'], talent(result)['total']), (0, 0))
                    self.assertEqual(talent(result)['times_seconds'], [])

    def test_continuous_empty_ranges_remove_own_hits_without_changing_gravity_per_hit(self):
        # Section109 closes the ordinary continuous acquisition gap recorded
        # by the original twelve-call diagnosis. Empty owner supply cancels
        # hits; the already qualified gravity per-hit amount stays unchanged.
        baselines = []
        references = []
        for relic_ids in ([], [GRAVITY]):
            with self.subTest(mode='continuous', relic_ids=relic_ids):
                caller = request(TARGETS[4], timing_mode='continuous', relic_ids=relic_ids)
                caller_before = deepcopy(caller)
                baseline = calculate_damage(caller)
                self.assertEqual(caller, caller_before)
                empty_caller = {**caller, 'timing': {'target_windows': []}}
                empty_caller_before = deepcopy(empty_caller)
                empty = calculate_damage(empty_caller)
                self.assertEqual(empty_caller, empty_caller_before)
                self.assertGreater(talent(baseline)['hits'], 0)
                self.assertEqual((talent(empty)['hits'], talent(empty)['total']), (0, 0))
                self.assertEqual(talent(empty)['times_seconds'], [])
                self.assertEqual(talent(empty)['per_hit'], talent(baseline)['per_hit'])
                self.assertEqual(empty['total_damage'], 0)
                self.assertEqual(empty['estimate']['skill']['total_damage'], 0)
                self.assertIs(baseline['timing']['scenario_provided'], False)
                self.assertIs(empty['timing']['scenario_provided'], True)
                baselines.append(talent(baseline))
                references.append(talent(empty))
        self.assertEqual(baselines[0]['hits'], baselines[1]['hits'])
        self.assertEqual(baselines[0]['times_seconds'], baselines[1]['times_seconds'])
        self.assertGreater(baselines[1]['per_hit'], baselines[0]['per_hit'])
        self.assertEqual(references[0]['hits'], references[1]['hits'])
        self.assertEqual(references[0]['times_seconds'], references[1]['times_seconds'])

    def test_original_training_and_target_identity_errors_still_precede_consumer(self):
        for options in ({'skill': 0}, {'skill': 4}, {'skill_rank': 11}, {'level': 0},
                        {'elite': 1, 'skill': 3, 'skill_rank': 7},
                        {'elite': 0, 'skill_rank': 10}, {'potential': False}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                calculate_damage(request(TARGETS[4], relic_ids=[GRAVITY], **options))
        for level in (False, True):
            target = {**identity(TARGETS[4]), 'level': level}
            with self.subTest(level=level), self.assertRaises(ValueError):
                calculate_damage(request(TARGETS[4], target_enemy=target, relic_ids=[GRAVITY]))

    def test_report_and_estimate_preserve_signed_weight_and_preview_excludes_relics(self):
        for record in TARGETS:
            with self.subTest(weight=record[0]):
                result = calculate_damage(request(record, relic_ids=[GRAVITY]))
                section = next(s for s in result['report']['sections'] if s['id'] == 'enemy_environment')
                metric = next(m for m in section['metrics'] if m['key'] == 'massLevel')
                self.assertEqual(metric['value'], record[0] - 2)
                text = format_report(result)
                self.assertEqual(format_estimate(result), text)
                self.assertIn('预计重量', text)
                self.assertIn('不据此计算位移', text)
                self.assertIn('预计重量', format_report(result, technical=True))
                preview = enemy_preview(record[1], record[2], 0, deepcopy(CONFIG))
                self.assertEqual(preview['environment']['stats']['massLevel'], record[0])
                self.assertTrue(any('本预览不套用藏品' in note for note in preview['limits']))

    def test_caller_and_public_sources_survive_calculation_and_mutated_result(self):
        catalog_before, previews_before = deepcopy(catalog()), deepcopy(stage_previews())
        args = request(TARGETS[4], enemy_weight=False, relic_ids=[GRAVITY, GRAVITY])
        before = deepcopy(args)
        result = calculate_damage(args)
        expected = deepcopy(result)
        talent(result)['per_hit'] = -999
        talent(result)['times_seconds'].append(99)
        result['run_resolution']['enemy']['stats']['massLevel'] = 999
        self.assertEqual(calculate_damage(args), expected)
        self.assertEqual(args, before)
        self.assertIs(args['enemy_weight'], False)
        self.assertEqual(catalog(), catalog_before)
        self.assertEqual(stage_previews(), previews_before)


if __name__ == '__main__':
    unittest.main()
