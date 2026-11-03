"""Reviewed module parameters stay behind their real cultivation gates."""
import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.drone_traits import selected_drone_trait
from rouge.operator_engine import selected_talents


CAMMOU = 'char_328_cammou'
WHITW2 = 'char_1038_whitw2'
MODULES = {CAMMOU: 'uniequip_002_cammou', WHITW2: 'uniequip_002_whitw2'}
BASE = {'init_atk_scale': .2, 'delta_atk_scale': .15,
        'max_atk_scale': 1.1, 'max_stack_cnt': 6.0}


def selected(operator, **extra):
    scenario = {'operator': operator, 'module_id': MODULES[operator],
                'module_level': 1, **extra}
    profile = catalog()['operators'][operator]
    _, parts = selected_talents(profile, scenario)
    return selected_drone_trait(profile, scenario, parts)


class DroneTraitTests(unittest.TestCase):
    def test_all_cammou_stages_raise_the_reference_ceiling_to_120_percent(self):
        expected = {**BASE, 'max_atk_scale': 1.2, 'max_stack_cnt': 7.0}
        for stage in range(1, 4):
            with self.subTest(stage=stage):
                self.assertEqual(selected(CAMMOU, module_level=stage), expected)

    def test_all_whitw2_stages_start_at_35_percent_with_same_110_percent_ceiling(self):
        expected = {**BASE, 'init_atk_scale': .35, 'max_stack_cnt': 5.0}
        for stage in range(1, 4):
            with self.subTest(stage=stage):
                self.assertEqual(selected(WHITW2, module_level=stage), expected)

    def test_cammou_unlock_is_e2_level_40(self):
        self.assertEqual(selected(CAMMOU, elite=2, level=39), BASE)
        self.assertEqual(selected(CAMMOU, elite=2, level=40)['max_atk_scale'], 1.2)
        self.assertEqual(selected(CAMMOU, elite=1, level=60), BASE)

    def test_whitw2_unlock_is_e2_level_60(self):
        self.assertEqual(selected(WHITW2, elite=2, level=59), BASE)
        self.assertEqual(selected(WHITW2, elite=2, level=60)['init_atk_scale'], .35)
        self.assertEqual(selected(WHITW2, elite=1, level=80), BASE)

    def test_potential_does_not_change_the_reviewed_trait_override(self):
        for operator in MODULES:
            expected = selected(operator)
            for potential in range(1, 7):
                with self.subTest(operator=operator, potential=potential):
                    self.assertEqual(selected(operator, potential=potential), expected)

    def test_no_module_preserves_the_complete_base_bundle(self):
        for operator in MODULES:
            self.assertEqual(selected(operator, module_id=None, module_level=0), BASE)

    def test_parts_from_another_operator_cannot_supply_a_trait(self):
        profile = catalog()['operators'][CAMMOU]
        other = catalog()['operators'][WHITW2]
        scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU], 'module_level': 1}
        parts = other['modules'][0]['levels'][0]['parts']
        self.assertEqual(selected_drone_trait(profile, scenario, parts), BASE)

    def test_missing_or_unknown_module_parts_keep_base_parameters(self):
        profile = catalog()['operators'][CAMMOU]
        scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU], 'module_level': 1}
        self.assertEqual(selected_drone_trait(profile, scenario, []), BASE)
        self.assertEqual(selected_drone_trait(profile, scenario, [{'target': 'TRAIT_DATA_ONLY'}]), BASE)

    def test_unreviewed_operator_or_module_never_applies_drone_override(self):
        profile = catalog()['operators'][CAMMOU]
        parts = profile['modules'][0]['levels'][0]['parts']
        for extra in ({'operator': WHITW2}, {'module_id': MODULES[WHITW2]},
                      {'module_id': 'unreviewed_module'}):
            scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU], 'module_level': 1, **extra}
            self.assertEqual(selected_drone_trait(profile, scenario, parts), BASE)

    def test_invalid_stage_does_not_select_last_or_first_stage_by_accident(self):
        profile = catalog()['operators'][CAMMOU]
        parts = profile['modules'][0]['levels'][0]['parts']
        for stage in (0, -1, 4, True):
            scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU], 'module_level': stage}
            self.assertEqual(selected_drone_trait(profile, scenario, parts), BASE)

    def test_token_scripted_and_scoped_parts_are_not_direct_overrides(self):
        for field, value in (('isToken', True), ('target', 'TRAIT'), ('target', 'DISPLAY'),
                             ('validInGameTag', 'unverified'), ('validInMapTag', 'unverified')):
            with self.subTest(field=field, value=value):
                profile = copy.deepcopy(catalog()['operators'][CAMMOU])
                part = profile['modules'][0]['levels'][0]['parts'][0]
                part[field] = value
                scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU], 'module_level': 1}
                self.assertEqual(selected_drone_trait(profile, scenario, [part]), BASE)

    def test_raw_candidate_cultivation_and_potential_gates_are_independent(self):
        for change in ({'unlockCondition': {'phase': 'PHASE_2', 'level': 80}},
                       {'requiredPotentialRank': 5}):
            profile = copy.deepcopy(catalog()['operators'][CAMMOU])
            part = profile['modules'][0]['levels'][0]['parts'][0]
            part['overrideTraitDataBundle']['candidates'][0].update(change)
            scenario = {'operator': CAMMOU, 'module_id': MODULES[CAMMOU],
                        'module_level': 1, 'level': 70, 'potential': 1}
            self.assertEqual(selected_drone_trait(profile, scenario, [part]), BASE)

    def test_selecting_trait_does_not_mutate_catalog_scenario_or_module_talents(self):
        profile = catalog()['operators'][WHITW2]
        scenario = {'operator': WHITW2, 'module_id': MODULES[WHITW2], 'module_level': 3}
        talents, parts = selected_talents(profile, scenario)
        snapshots = copy.deepcopy((profile, scenario, talents, parts))
        values = selected_drone_trait(profile, scenario, parts)
        values['init_atk_scale'] = 999
        self.assertEqual((profile, scenario, talents, parts), snapshots)
        self.assertEqual(selected_talents(profile, scenario), (talents, parts))
        self.assertEqual(selected_drone_trait(profile, scenario, parts)['init_atk_scale'], .35)


class DroneTraitIntegrationTests(unittest.TestCase):
    def evaluate(self, op, **extra):
        return calculate_damage({'operator': op, 'skill': 1, 'base_attack': 1000,
            'window_seconds': 2, 'module_id': MODULES[op], 'module_level': 1, **extra})

    def drone(self, result):
        return next(c for c in result['components'] if c['name'] == '浮游单元')

    def test_cammou_all_stages_apply_the_known_120_percent_cap(self):
        for stage in (1, 2, 3):
            r = self.evaluate(CAMMOU, module_level=stage, drone_warmup_hits=7)
            self.assertAlmostEqual(self.drone(r)['per_hit'], 2160)
            self.assertEqual(r['drone_trait_reference']['parameters']['max_atk_scale'], 1.2)
            self.assertFalse(r['estimate']['complete'])

    def test_whitw2_all_stages_apply_the_known_35_percent_start(self):
        for stage in (1, 2, 3):
            r = self.evaluate(WHITW2, module_level=stage)
            self.assertAlmostEqual(self.drone(r)['per_hit'], 472.5)
            self.assertAlmostEqual(self.drone(r)['total'], 945)
            self.assertFalse(r['drone_trait_reference']['independent_clock_verified'])

    def test_unlock_edges_do_not_apply_early(self):
        below = self.evaluate(CAMMOU, level=39, drone_warmup_hits=7)
        at = self.evaluate(CAMMOU, level=40, drone_warmup_hits=7)
        self.assertAlmostEqual(self.drone(below)['per_hit'], 1980)
        self.assertAlmostEqual(self.drone(at)['per_hit'], 2160)
        self.assertNotIn('drone_trait_reference', below)
        self.assertAlmostEqual(self.drone(self.evaluate(WHITW2, level=59))['per_hit'], 270)
        self.assertAlmostEqual(self.drone(self.evaluate(WHITW2, level=60))['per_hit'], 472.5)

    def test_no_module_preserves_existing_base_reference(self):
        r = self.evaluate(WHITW2, module_id=None, module_level=0)
        self.assertAlmostEqual(self.drone(r)['per_hit'], 270)
        self.assertNotIn('drone_trait_reference', r)

    def test_report_exposes_parameters_without_claiming_live_clock(self):
        text = format_estimate(self.evaluate(WHITW2))
        self.assertIn('浮游单元 · 模组特性参数', text)
        self.assertIn('初始攻击倍率参数：35 %', text)
        self.assertIn('实际独立单元时钟', text)


if __name__ == '__main__':
    unittest.main()
