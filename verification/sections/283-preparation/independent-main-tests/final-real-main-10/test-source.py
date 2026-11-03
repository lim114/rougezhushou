"""Independent main-caller contracts, not a re-audit of authored numeric code.

Public fixtures only. No application window, game process, private run/config or
chat is accessed. The old33 regression and parent38 suite are not repeated.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rouge import calibration, damage, panel_native_bridge as bridge, panel_native_finalization as native
from rouge import relic_attributes

Q = 4294967296
PHASES = ('cultivation', 'rune', 'normal', 'skill')
FIELDS = ('hp', 'attack', 'defense', 'resistance', 'attack_speed')


def row(result, phase, field):
    return next(r for r in result['panel_native_finalization']['fields']
                if r['phase'] == phase and r['field'] == field)


def legacy_projection(result):
    return {key: deepcopy(result.get(key)) for key in ('attack', 'total_damage', 'total_healing',
            'attack_speed', 'attack_speed_reference', 'base_attack_speed', 'base_attack_speed_reference',
            'components', 'complete', 'warnings')} | {
        'estimate': {key: deepcopy(result['estimate'].get(key)) for key in
                     ('base_stats', 'skill', 'training', 'complete', 'warnings')}}


class MainCaller283(unittest.TestCase):
    def test_main_uses_exact_same_prepared_rune_objects_and_collection(self):
        scenario = {'operator': 'mechanist', 'skill': 3, 'charge_count': 0,
                    'relic_ids': ['rogue_6_relic_legacy_16', 'rogue_6_relic_legacy_17'],
                    'effects': [{'kind': 'attack_pct', 'value': .25}]}
        before = deepcopy(scenario)
        applications, preparations = [], []
        original_apply, original_prepare = relic_attributes.apply_attribute_runes, bridge.prepare

        def apply(attributes, effects):
            applications.append(effects)
            return original_apply(attributes, effects)

        def prepare(s, cultivated, attributes, runes):
            self.assertIs(s['_attribute_runes'], runes)
            preparations.append((runes, deepcopy(runes)))
            return original_prepare(s, cultivated, attributes, runes)

        with patch.object(relic_attributes, 'apply_attribute_runes', side_effect=apply), \
             patch.object(bridge, 'prepare', side_effect=prepare):
            result = damage.calculate_damage(scenario)
        self.assertEqual(scenario, before)
        self.assertEqual(len(preparations), 1)
        shared, selected = preparations[0]
        self.assertGreaterEqual(len(applications), 2)
        self.assertIs(applications[0], shared)
        self.assertIs(applications[1], shared)
        self.assertTrue(selected)
        self.assertTrue(all(e['attribute_layer'] == 'relic_rune' for e in selected))
        self.assertFalse(any(e.get('token_only') for e in selected))
        self.assertEqual(result['panel_native_finalization']['input_provenance']['rune_sources'], selected)
        self.assertFalse(result['panel_native_finalization']['input_provenance']['normal_native_calls_inferred'])
        self.assertFalse(result['panel_native_finalization']['input_provenance']['protected_parent_result_propagated'])

    def test_calibration_four_layers_copy_main_reference_without_native_reevaluation(self):
        scenario = {'operator': 'kaltsit', 'skill': 2, 'relic_ids': ['rogue_6_relic_legacy_90']}
        main = damage.calculate_damage(scenario)
        before = deepcopy(main)
        with patch.object(calibration, 'calculate_damage', return_value=main) as calculate, \
             patch.object(native, 'panel_native_finalization', side_effect=AssertionError('calibration cannot recompute native')):
            panel = calibration.panel_layers(scenario)
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(main, before)
        self.assertEqual(panel['native_panel_reference'], main['panel_native_finalization'])
        self.assertIsNot(panel['native_panel_reference'], main['panel_native_finalization'])
        self.assertEqual(tuple(panel['panels']), tuple(bridge.PHASE_NAMES[p] for p in PHASES))
        self.assertEqual(panel['rune_sources'], main['panel_native_finalization']['input_provenance']['rune_sources'])
        self.assertFalse(panel['native_verified'])

    def test_nine_first_three_skills_attach_corresponding_normal_and_skill_model_snapshots(self):
        for operator in ('kaltsit', 'silverash', 'mechanist'):
            for skill in (1, 2, 3):
                with self.subTest(operator=operator, skill=skill):
                    scenario = {'operator': operator, 'skill': skill}
                    before = deepcopy(scenario)
                    with patch.object(native, 'panel_native_finalization', wraps=native.panel_native_finalization) as evaluate:
                        result = damage.calculate_damage(scenario)
                    self.assertEqual(evaluate.call_count, 1)
                    self.assertEqual(scenario, before)
                    data = result['panel_native_finalization']
                    self.assertEqual(len(data['fields']), 17)
                    self.assertEqual({p: len(v) for p, v in data['phase_ids'].items()},
                                     {'cultivation': 5, 'rune': 5, 'normal': 5, 'skill': 2})
                    for field in FIELDS:
                        stats = result['estimate']['base_stats']
                        expected = stats['attack_speed_reference'] if field == 'attack_speed' else stats[field]
                        self.assertEqual(row(result, 'normal', field)['model_value'], expected)
                    self.assertEqual(row(result, 'skill', 'attack')['model_value'], result['estimate']['skill']['skill_attack'])
                    self.assertEqual(row(result, 'skill', 'attack_speed')['model_value'],
                                     result['estimate']['skill']['skill_attack_speed_reference'])
                    self.assertNotIn('_panel_native_terms', result['estimate'])
                    self.assertEqual(result['estimate']['native_panel_reference_key'], 'panel_native_finalization')
                    self.assertTrue(any(section['id'] == 'panel_native_finalization' for section in result['report']['sections']))
                    self.assertFalse(data['complete_native_panel'])
                    self.assertIsNone(data['actual_panel'])
                    for reference in data['fields']:
                        self.assertIsNone(reference['actual_decoded_value'])
                        self.assertIsNone(reference['actual_getter_raw'])
                        self.assertFalse(reference['complete_native_value'])

    def test_combat_only_defense_relic_does_not_enter_offline_finisher(self):
        scenario = {'operator': 'silverash', 'skill': 1, 'deployment_elapsed_seconds': 80,
                    'relic_ids': ['rogue_6_relic_legacy_63'], 'relic_context': {'deployed_seconds': 80},
                    'effects': [{'kind': 'defense_pct', 'value': .5}]}
        with patch.object(bridge, 'add_final_term', wraps=bridge.add_final_term) as addition:
            result = damage.calculate_damage(scenario)
        defense = row(result, 'normal', 'defense')['references']
        calls = [call.args[1:] for call in addition.call_args_list]
        self.assertIn(('normal', 'defense', 'final_addition', 0), calls)
        self.assertEqual(defense['multiplier_raw'], 3 * Q // 2)
        # Pot1 SilverAsh's elapsed talent adds120. Combat-conditional legacy63
        # is reference-only in this product; it must not add defense400/MR30.
        self.assertEqual(defense['after_final_add_raw'] - defense['after_multiplier_raw'], 120 * Q)
        self.assertEqual(defense['getter_result_raw'] / Q, result['estimate']['base_stats']['defense'])
        self.assertEqual(row(result, 'normal', 'resistance')['references']['getter_result_raw'], 0)

    def test_synthetic_prepared_defense_finisher_hook_uses_final_addition_bucket(self):
        # Isolated internal propagation fixture, not a real/current relic or a
        # new supported combat condition. No public input or private state is
        # used to manufacture native call facts or an actual decoded panel.
        prepared = damage._prepare_damage({'operator': 'silverash', 'skill': 1,
                    'deployment_elapsed_seconds': 80, 'effects': [{'kind': 'defense_pct', 'value': .5}]})
        self.assertIs(prepared[0]['_relic_rules'], prepared[2]['rules'])
        prepared[2]['rules'].append({'kind': 'defense_flat', 'value': 400,
                                     'relic_id': 'synthetic-main-caller-fixture', '_verified_rule': True})
        with patch.object(bridge, 'add_final_term', wraps=bridge.add_final_term) as addition:
            result = damage._evaluate_damage(prepared)
        self.assertIn(('normal', 'defense', 'final_addition', 400),
                      [call.args[1:] for call in addition.call_args_list])
        defense = row(result, 'normal', 'defense')['references']
        self.assertEqual(defense['multiplier_raw'], 3 * Q // 2)
        self.assertEqual(defense['after_final_add_raw'] - defense['after_multiplier_raw'], 520 * Q)
        self.assertEqual(defense['getter_result_raw'] / Q, result['estimate']['base_stats']['defense'])
        self.assertIsNone(result['panel_native_finalization']['actual_panel'])
        self.assertFalse(result['panel_native_finalization']['complete_native_panel'])

    def test_finite_speed_updates_distinct_normal_age_and_skill_start_buckets(self):
        for age, normal_speed in ((0, 210), (10, 100)):
            with self.subTest(age=age):
                scenario = {'operator': 'mechanist', 'skill': 1, 'timing_mode': 'continuous',
                            'timing': {'windup_frames': 0, 'recovery_frames': 0},
                            'deployment_elapsed_seconds': age,
                            'relic_ids': ['rogue_6_relic_legacy_105', 'rogue_6_relic_legacy_106']}
                result = damage.calculate_damage(scenario)
                self.assertLess(result['deployment_buff_reference']['first_skill_start_seconds'], 10)
                normal = row(result, 'normal', 'attack_speed')['references']
                skill = row(result, 'skill', 'attack_speed')['references']
                self.assertEqual(normal['after_add_raw'], normal_speed * Q)
                self.assertEqual(skill['after_add_raw'], 210 * Q)
                self.assertEqual(normal['getter_result_raw'], normal_speed * Q)
                self.assertEqual(skill['getter_result_raw'], 210 * Q)
                self.assertEqual(result['estimate']['base_stats']['attack_speed_reference'], normal_speed)
                self.assertEqual(result['estimate']['skill']['skill_attack_speed_reference'], 210)

    def test_attribute_speed700_is_preserved_beside_effective_timing600(self):
        result = damage.calculate_damage({'operator': 'mechanist', 'skill': 1,
                                          'effects': [{'kind': 'attack_speed', 'value': 600}]})
        self.assertEqual(result['estimate']['base_stats']['attack_speed_reference'], 700)
        self.assertEqual(result['estimate']['base_stats']['attack_speed'], 600)
        self.assertEqual(result['base_attack_speed_reference'], 700)
        self.assertEqual(result['base_attack_speed'], 600)
        self.assertEqual(row(result, 'normal', 'attack_speed')['references']['getter_result_raw'], 700 * Q)
        self.assertEqual(row(result, 'skill', 'attack_speed')['references']['getter_result_raw'], 700 * Q)

    def test_private_snapshot_and_source_injection_cannot_forge_known_native_state(self):
        scenario = {'operator': 'mechanist', 'skill': 1}
        baseline = damage.calculate_damage(scenario)['panel_native_finalization']
        injected = {**scenario,
            '_panel_native_prepared': {'fields': [], 'rune_sources': [{'fake': True}], 'actual_panel': {'attack': 999}},
            '_panel_native_terms': {'normal': {'attack': {'basis': 999}}},
            '_attribute_runes': [{'fake': True}], '_relic_rules': [{'fake': True}],
            'panel_native_finalization': {'complete_native_panel': True, 'actual_panel': {'attack': 999}},
            'source': {'valid': True, 'actual_panel': {'attack': 999}}, 'evaluator': 'fake'}
        before = deepcopy(injected)
        result = damage.calculate_damage(injected)
        self.assertEqual(injected, before)
        self.assertEqual(result['panel_native_finalization'], baseline)
        for name in ('_panel_native_prepared', '_panel_native_terms', '_attribute_runes', '_relic_rules'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                calibration.panel_layers({**scenario, name: injected[name]})

    def test_extended_skill_native_basis_remains_unknown_while_model_estimate_survives(self):
        result = damage.calculate_damage({'operator': 'char_151_myrtle', 'skill': 2})
        self.assertIsInstance(result['estimate']['skill']['skill_attack'], (int, float))
        self.assertGreater(result['total_healing'], 0)
        for field in ('attack', 'attack_speed'):
            reference = row(result, 'skill', field)
            self.assertIsNotNone(reference['model_value'])
            self.assertIsNone(reference['references']['input_fp_raw'])
            self.assertIsNone(reference['references']['getter_result_raw'])
            self.assertFalse(reference['conditional_complete'])
            self.assertIsNone(reference['actual_decoded_value'])
        self.assertEqual(row(result, 'normal', 'attack')['model_value'], result['estimate']['base_stats']['attack'])

    def test_broken_mother_source_hides_conditional_result_but_preserves_legacy_model(self):
        source_path = ROOT / native.SOURCE
        before_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix='panel283-main-public-', dir=HERE) as folder:
            copy = Path(folder).resolve() / 'source-manifest.json'
            self.assertTrue(copy.is_relative_to(HERE.resolve()))
            copy.write_bytes(source_path.read_bytes())
            with patch.object(native, 'SOURCE', str(copy)):
                self.assertIsNotNone(native.source_data())
                scenario = {'operator': 'mechanist', 'skill': 3, 'charge_count': 0,
                            'relic_ids': ['rogue_6_relic_legacy_16']}
                valid = damage.calculate_damage(scenario)
                self.assertTrue(valid['panel_native_finalization']['source_valid'])
                raw = bytearray(copy.read_bytes()); raw[0] ^= 1; copy.write_bytes(raw)
                self.assertIsNone(native.source_data())
                invalid = damage.calculate_damage(scenario)
                self.assertEqual(legacy_projection(invalid), legacy_projection(valid))
                self.assertFalse(invalid['panel_native_finalization']['source_valid'])
                self.assertIsNone(invalid['panel_native_finalization']['actual_panel'])
                for reference in invalid['panel_native_finalization']['fields']:
                    self.assertFalse(reference['conditional_complete'])
                    self.assertTrue(all(value is None for value in reference['references'].values()))
                    self.assertIsNone(bridge.conditional_value(reference))
                section = next(s for s in invalid['report']['sections'] if s['id'] == 'panel_native_finalization')
                self.assertTrue(all(metric['value'] is None for metric in section['metrics']))
                panel = calibration.panel_layers(scenario)
                self.assertFalse(panel['native_panel_reference']['source_valid'])
                self.assertIsInstance(panel['panels']['已覆盖常态天赋与效果']['attack'], (int, float))
        self.assertEqual(hashlib.sha256(source_path.read_bytes()).hexdigest(), before_hash)
        self.assertIsNotNone(native.source_data())


if __name__ == '__main__':
    unittest.main(verbosity=2)
