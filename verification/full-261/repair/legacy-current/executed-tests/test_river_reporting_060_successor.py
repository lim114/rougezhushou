"""Current equivalents of the ten river presentation integration case classes.

These are explicitly declared new public controls.  The missing sealed
pre060 scenario/result JSON and the original historical tests stay intact.
No calculation result is stored as an expected historical output.
"""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import river_reference_sections
from rouge.river_effects import RELIC_ID, reference


ROOT = Path(__file__).resolve().parents[1]
OTHER = 'rogue_6_relic_fight_21'
BLOCKS = {'river_dark', 'river_fire', 'river_sanity', 'river_water', 'river_limits'}
ORIGINAL_OUTPUT_SHA = '66e5babd5d88eeef681472958780822e6717617c1b403dbe1bdf75e1fc6e0326'
POST060_REFERENCE_SHA = '054acea609cd3554fff80684df5559c69e842efc485e9f7ab2c197095acff43a'

# Names identify the original ten case classes, not recovered original inputs.
# Common neural controls follow the public tests.test_neural_relic_034 scenario;
# base_attack=1000 is an explicit new arithmetic control, not a frozen old input.
NEURAL = {'operator': 'char_4204_mantra', 'skill': 2, 'base_attack': 1000,
    'enemy_resistance': 0, 'enemy_elemental_resistance': 20,
    'initial_neural_buildup': 999, 'window_seconds': 1}
MECHANIST = {'operator': 'mechanist', 'skill': 3, 'base_attack': 1000, 'window_seconds': 1}
MYRTLE = {'operator': 'char_151_myrtle', 'skill': 1, 'base_attack': 1000, 'window_seconds': 1}
CONTROLS = {
    'mechanist_default': MECHANIST,
    'myrtle_default': MYRTLE,
    'mantra_default': NEURAL,
    'mantra_other_relic': {**NEURAL, 'relic_ids': [OTHER]},
    'mechanist_river': {**MECHANIST, 'relic_ids': [RELIC_ID]},
    'myrtle_river': {**MYRTLE, 'relic_ids': [RELIC_ID]},
    'mantra_river': {**NEURAL, 'relic_ids': [RELIC_ID]},
    'mantra_river_no_supply': {**NEURAL, 'relic_ids': [RELIC_ID],
        'initial_neural_buildup': 0,
        'timing': {'target_windows': [], 'initial_target_windows': []}},
    'phantom_river': {**NEURAL, 'operator': 'char_1042_phatm2', 'skill': 1,
        'initial_neural_buildup': 400, 'relic_ids': [RELIC_ID]},
    'mantra_river_and_other': {**NEURAL, 'relic_ids': [RELIC_ID, OTHER]},
}


class RiverReporting060CurrentSuccessorTests(unittest.TestCase):
    def paired_full_structure(self, name):
        scenario = deepcopy(CONTROLS[name])
        original_input = deepcopy(scenario)
        with patch('rouge.river_effects.RiverInstance',
                   side_effect=AssertionError('presentation entered a combat simulator')):
            with patch('rouge.reporting.river_reference_sections',
                       wraps=river_reference_sections) as rendered:
                current = calculate_damage(scenario)
            # This switch exists only at the test boundary.  It suppresses the
            # five reference blocks while running the same complete calculator.
            # Timing, warnings, source fields and numeric results remain present.
            with patch('rouge.reporting.river_reference_sections', return_value=[]) as suppressed:
                control = calculate_damage(scenario)
        held = RELIC_ID in scenario.get('relic_ids', [])
        self.assertEqual(rendered.call_count, int(held))
        self.assertEqual(suppressed.call_count, int(held))
        expected = BLOCKS if held else set()
        actual = [b for b in current['report']['sections'] if b['id'] in BLOCKS]
        self.assertEqual({b['id'] for b in actual}, expected)
        self.assertEqual(len(actual), len(expected))
        self.assertFalse(any(b['id'] in BLOCKS for b in control['report']['sections']))
        without_reference = deepcopy(current)
        without_reference['report']['sections'] = [b for b in without_reference['report']['sections']
            if b['id'] not in BLOCKS]
        # The only exclusion is exactly the five asserted presentation blocks.
        # Compare the whole nested result, including every numeric and clock leaf.
        self.assertEqual(without_reference, control)
        self.assertEqual(scenario, original_input)
        return current

    def test_mechanist_default_current_equivalence(self):
        self.paired_full_structure('mechanist_default')

    def test_myrtle_default_current_equivalence(self):
        self.paired_full_structure('myrtle_default')

    def test_mantra_default_current_equivalence(self):
        self.paired_full_structure('mantra_default')

    def test_mantra_other_relic_current_equivalence(self):
        self.paired_full_structure('mantra_other_relic')

    def test_mechanist_river_current_equivalence(self):
        result = self.paired_full_structure('mechanist_river')
        self.assertNotIn('neural_relic_reference', result)
        self.assertNotIn('已建模伤害小计', format_estimate(result))

    def test_myrtle_river_current_equivalence(self):
        result = self.paired_full_structure('myrtle_river')
        self.assertNotIn('neural_relic_reference', result)

    def test_mantra_river_current_equivalence_and_independent_subtotal(self):
        result = self.paired_full_structure('mantra_river')
        # Fixed original skill/talent parameters: 1000*2.4 arts,
        # 6000*2*.8 burst, 1000*.25*.8 attached element =12200.
        self.assertEqual(result['known_damage_subtotals']['window_damage'], 12200)
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['estimate']['skill']['window_dps'])
        self.assertIsNone(result['estimate']['skill']['cycle_dps'])
        self.assertFalse(result['neural_relic_reference']['periodic_damage_scheduled'])
        self.assertFalse(result['complete'])

    def test_mantra_river_no_supply_current_equivalence_and_known_zero(self):
        result = self.paired_full_structure('mantra_river_no_supply')
        self.assertEqual(result['total_damage'], 0)
        self.assertEqual(result['estimate']['skill']['total_damage'], 0)
        self.assertFalse(result['neural_relic_reference']['periodic_damage_possible'])
        self.assertEqual(result['neural_relic_reference']['lifecycle_reference'], reference())
        self.assertNotIn('lifecycle_reference', result)

    def test_phantom_river_current_equivalence_keeps_arts_and_unknown_total(self):
        result = self.paired_full_structure('phantom_river')
        # Source-backed S1 control: two arts hits, 1000*1.5*2=3000.
        self.assertEqual(result['known_damage_subtotals']['window_damage'], 3000)
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        self.assertEqual(result['components'][0]['times_seconds'], [.5, .9])
        self.assertFalse(result['neural_s1_reference']['binding_multiplier_applied'])
        self.assertFalse(result['neural_s1_reference']['first_attachment_verified'])
        self.assertFalse(result['neural_s1_reference']['refresh_order_verified'])
        self.assertFalse(result['neural_relic_reference']['periodic_damage_scheduled'])

    def test_mantra_river_and_other_current_equivalence_and_separate_sources(self):
        result = self.paired_full_structure('mantra_river_and_other')
        # Other-source factor1.75 applies separately to elemental damage:
        # 1000*2.4 +6000*2*1.75*.8 +1000*.25*1.75*.8=19550.
        self.assertEqual(result['known_damage_subtotals']['window_damage'], 19550)
        self.assertIsNone(result['total_damage'])
        self.assertFalse(result['neural_relic_reference']['periodic_damage_scheduled'])

    def test_reference_parameters_match_exact_sealed_post060_public_source(self):
        raw = (ROOT / 'rouge/river_effects.py').read_bytes()
        sealed = json.loads((ROOT / 'FINAL_0.60_VERIFICATION.json').read_text(encoding='utf-8'))
        self.assertEqual(sealed['source_sha256']['rouge/river_effects.py'], POST060_REFERENCE_SHA)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), POST060_REFERENCE_SHA)
        # This source really has original sealed0.60 bytes.  Read its literal
        # contract independently; do not invoke reference() to make an expected.
        assignment = next(n for n in ast.parse(raw).body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == '_BRANCHES' for t in n.targets))
        branches = ast.literal_eval(assignment.value)
        current = reference()
        self.assertEqual(current['branches'], branches)
        self.assertFalse(current['permanent_panel_effect'])
        self.assertFalse(current['live_combat_inputs_added'])
        self.assertFalse(current['native_fp_equivalence_proven'])
        self.assertFalse(current['absolute_creation_phase_known'])
        self.assertFalse(current['source']['current_hotfix_equivalence_proven'])
        self.assertEqual(current['maximum_triggers_per_owner_tick'], 1)
        self.assertFalse(current['catch_up_loop'])

    def test_exact_four_metric_contracts_and_player_boundaries(self):
        result = calculate_damage(deepcopy(CONTROLS['mantra_river']))
        blocks = {b['id']: b for b in result['report']['sections'] if b['id'] in BLOCKS}
        metric_values = {key: {r['key']: r['value'] for r in blocks['river_' + key]['metrics']}
            for key in ('dark', 'fire', 'sanity', 'water')}
        self.assertEqual(metric_values, {
            'dark': {'burst_factor': 2.5, 'enemy_attack_factor': .7},
            'fire': {'burst_factor': 3.8, 'enemy_mr_addition': -20},
            'sanity': {'burst_factor': 2., 'pulse_raw': 1000., 'period': 1., 'first_wait': 1.},
            'water': {'burst_factor': 1., 'pulse_raw': 1500., 'period': .03,
                'maximum_pulses': 10, 'enemy_def_addition': -120},
        })
        text = '\n'.join(b['title'] + '\n' + '\n'.join(b['notes']) for b in blocks.values())
        for forbidden in ('有理时间', '原生定点时钟', '六个完整模板', '同键', '属性组', '派生', 'Q32', 'palsy'):
            self.assertNotIn(forbidden, text)
        for boundary in ('没有默认目标处于麻痹', '不另加冷却加速', '热更新版本是否改变',
                         '十次伤害结束后防御减算继续', '实际追加跳数与完整总伤仍未知'):
            self.assertIn(boundary, text)

    def test_returned_lifecycle_is_copy_safe(self):
        scenario = deepcopy(CONTROLS['mantra_river_no_supply'])
        original = deepcopy(scenario)
        first = calculate_damage(scenario)
        first['neural_relic_reference']['lifecycle_reference']['branches']['water']['raw_pulse_damage'] = 99
        again = calculate_damage(scenario)
        self.assertEqual(again['neural_relic_reference']['lifecycle_reference']['branches']['water']['raw_pulse_damage'], 1500)
        self.assertEqual(scenario, original)


if __name__ == '__main__':
    unittest.main()
