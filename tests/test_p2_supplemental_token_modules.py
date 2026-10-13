import unittest
from copy import deepcopy

from rouge.p2_supplemental_token_modules import (compare_supplemental_token_modules,
    format_supplemental_token_modules, source_data)


L = 'char_2023_ling'
M = 'char_248_mgllan'
END = {'token_elite': 2, 'endpoint': 'last'}


class SupplementalTokenModuleTests(unittest.TestCase):
    def test_ling_three_primary_variants_receive_their_own_direct_stats(self):
        r = compare_supplemental_token_modules(L, {'elite': 2, 'level': 90}, END)
        expected = [('token_10020_ling_soul1', 2500, 549, 12, 2650, 594, 9),
                    ('token_10020_ling_soul2', 1217, 406, 9, 1317, 441, 6),
                    ('token_10020_ling_soul3', 3607, 823, 23, 3857, 883, 18)]
        for variant, values in zip(r['variants'], expected):
            identity, hp, attack, cost, added_hp, added_attack, reduced_cost = values
            with self.subTest(token=identity):
                self.assertEqual(variant['token_id'], identity)
                base = variant['stages'][0]['values']; equipped = variant['stages'][3]['values']
                self.assertEqual((base['hp'], base['attack'], base['deployment_cost']), (hp, attack, cost))
                self.assertEqual((equipped['hp'], equipped['attack'], equipped['deployment_cost']),
                                 (added_hp, added_attack, reduced_cost))
                self.assertIn(identity, variant['stages'][3]['source_selector'])
        self.assertEqual([v['skill'] for v in r['variants']], [1, 2, 3])
        self.assertEqual((r['module_unlock_elite'], r['module_unlock_level']), (2, 60))

    def test_magallan_zero_attack_and_defense_variant_are_not_an_attack_drone(self):
        r = compare_supplemental_token_modules(M, {'elite': 2, 'level': 90}, END)
        f, laser, artillery = [variant['stages'][3]['values'] for variant in r['variants']]
        self.assertEqual((f['hp'], f['attack'], f['defense'], f['attack_speed'], f['deployment_cost']),
                         (2100, 0, 250, 100, 2))
        self.assertEqual((laser['attack'], laser['attack_speed'], laser['deployment_cost']), (549, 103, 4))
        self.assertEqual((artillery['attack'], artillery['attack_speed'], artillery['deployment_cost']), (803, 103, 5))
        self.assertEqual(artillery['base_interval'], 2.3)
        self.assertIn('当前完整实体面板', format_supplemental_token_modules(r))

    def test_cost_reductions_are_present_at_all_three_stages_and_stats_only_at_third(self):
        for operator, costs in [(L, [9, 6, 18]), (M, [2, 4, 5])]:
            r = compare_supplemental_token_modules(operator, {}, END)
            for variant, cost in zip(r['variants'], costs):
                for stage in variant['stages'][1:]:
                    self.assertEqual(stage['values']['deployment_cost'], cost)
                    self.assertEqual(stage['stock_add_parameter'], 3)
                    self.assertGreaterEqual(stage['values']['deployment_cost'], 0)
                self.assertEqual(variant['stages'][1]['values']['hp'], variant['stages'][0]['values']['hp'])
                self.assertEqual(variant['stages'][2]['values']['attack'], variant['stages'][0]['values']['attack'])
                self.assertIsNone(variant['held_limit']); self.assertIsNone(variant['concurrent_limit'])

    def test_original_module_gate_keeps_lock_and_parameter_reference_distinct(self):
        for operator in (L, M):
            for elite, level, qualified in [(1, 60, False), (2, 59, False), (2, 60, True)]:
                with self.subTest(operator=operator, elite=elite, level=level):
                    r = compare_supplemental_token_modules(operator, {'elite': elite, 'level': level}, END)
                    self.assertEqual(r['module_qualified'], qualified)
                    for variant in r['variants']:
                        self.assertIsNotNone(variant['stages'][0]['values']['hp'])
                        stage = variant['stages'][3]
                        self.assertLess(stage['direct_additions']['deployment_cost'], 0)
                        if qualified: self.assertIsNotNone(stage['values']['hp'])
                        else:
                            self.assertIsNone(stage['values']['hp']); self.assertIsNone(stage['differences']['hp'])

    def test_independent_endpoints_do_not_follow_the_host_level_or_phase(self):
        training = {'elite': 2, 'level': 65}
        first = compare_supplemental_token_modules(L, training, {'token_elite': 1, 'endpoint': 'first'})
        last = compare_supplemental_token_modules(L, training, {'token_elite': 1, 'endpoint': 'last'})
        self.assertEqual([v['token_level_endpoint'] for v in first['variants']], [1, 1, 1])
        self.assertEqual([v['token_level_endpoint'] for v in last['variants']], [80, 80, 80])
        self.assertEqual(first['variants'][0]['base_parameter_values']['hp'], 1936)
        self.assertEqual(last['variants'][0]['base_parameter_values']['hp'], 2225)
        self.assertEqual(last['host_training']['level'], 65)
        self.assertTrue(all(v['actual_token_cultivation'] is None for v in last['variants']))

    def test_host_trust_potential_and_equipment_stats_never_enter_the_tokens(self):
        for operator, equipment in [(L, 'uniequip_002_ling'), (M, 'uniequip_002_mgllan')]:
            base = compare_supplemental_token_modules(operator, {'elite': 2, 'level': 90, 'trust': 0, 'potential': 1}, END)
            boosted = compare_supplemental_token_modules(operator, {'elite': 2, 'level': 90, 'trust': 100,
                                'potential': 6, 'module_id': equipment, 'module_level': 3}, END)
            self.assertEqual([v['stages'] for v in base['variants']], [v['stages'] for v in boosted['variants']])
        self.assertEqual(boosted['variants'][0]['stages'][3]['values']['attack'], 0)

    def test_all_declared_source_phases_have_exact_endpoints_but_no_live_or_merged_totals(self):
        for operator in (L, M):
            for elite in range(3):
                for endpoint, level in [('first', 1), ('last', [50, 80, 90][elite])]:
                    r = compare_supplemental_token_modules(operator, {}, {'token_elite': elite, 'endpoint': endpoint})
                    for variant in r['variants']:
                        self.assertEqual(variant['token_level_endpoint'], level)
                        self.assertIsNone(variant['actual_presence']); self.assertIsNone(variant['full_damage'])
                        self.assertIsNone(variant['merged_token_values']); self.assertIsNone(variant['full_healing'])
                        self.assertTrue(all(value is None for value in variant['stages'][3]['actual_values'].values()))

    def test_skill_qualification_is_independent_of_existing_low_phase_source_frames(self):
        r = compare_supplemental_token_modules(M, {'elite': 0, 'level': 50}, {'token_elite': 2, 'endpoint': 'last'})
        self.assertEqual([v['skill_qualified'] for v in r['variants']], [True, False, False])
        self.assertEqual(r['variants'][2]['stages'][0]['values']['attack'], 753)
        self.assertIsNone(r['variants'][2]['stages'][3]['values']['attack'])

    def test_explicit_endpoint_required_and_invalid_input_never_becomes_interpolation(self):
        for selection in ({}, {'token_elite': 2}, {'token_elite': True, 'endpoint': 'last'},
                          {'token_elite': 3, 'endpoint': 'first'}, {'token_elite': 2, 'endpoint': 'middle'},
                          {'token_elite': 2, 'endpoint': 'last', 'level': 65}, {'token_elite': 2, 'endpoint': None}):
            with self.subTest(selection=selection), self.assertRaises(ValueError):
                compare_supplemental_token_modules(L, {}, selection)
        for training in ({'level': 0}, {'level': 91}, {'elite': True}, {'potential': True}, {'trust': True},
                         {'module_id': None, 'module_level': 1}, {'module_id': ''}, {'token_trust': 100}):
            with self.subTest(training=training), self.assertRaises(ValueError):
                compare_supplemental_token_modules(L, training, END)
        with self.assertRaises(ValueError): compare_supplemental_token_modules('mechanist', {}, END)

    def test_source_and_caller_values_are_immutable_across_independent_results(self):
        training = {'elite': 2, 'level': 90}; selection = deepcopy(END)
        before = deepcopy((training, selection, source_data()))
        r = compare_supplemental_token_modules(L, training, selection)
        r['variants'][0]['stages'][3]['values']['hp'] = 1
        r['public_documents'][0]['quotes'][0] = 'changed'
        self.assertEqual((training, selection, source_data()), before)
        self.assertEqual(compare_supplemental_token_modules(L, training, selection)['variants'][0]['stages'][3]['values']['hp'], 2650)


if __name__ == '__main__':
    unittest.main()
