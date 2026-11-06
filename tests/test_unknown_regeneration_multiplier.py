import unittest
from unittest.mock import patch
from rouge.damage import calculate_damage


class UnknownRegenerationTests(unittest.TestCase):
    def test_unknown_multiplier_retains_subtotals_not_complete_rates(self):
        scenario={'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_91','rogue_6_relic_legacy_22']}
        known=calculate_damage(scenario)
        with patch('rouge.relic_healing_factors.regeneration_factor',return_value=None):
            result=calculate_damage(scenario)
        self.assertIsNone(result['relic_regeneration_multiplier'])
        self.assertIsNone(result['relic_regeneration_rate'])
        self.assertEqual(result['known_relic_regeneration_rate'],known['relic_regeneration_rate'])
        self.assertFalse(result['relic_resolution']['complete'])
        for token, baseline in zip(result['relic_token_stats'],known['relic_token_stats']):
            self.assertIsNone(token['regeneration_rate'])
            self.assertEqual(token['known_regeneration_rate'],baseline['regeneration_rate'])
        sections={s['id']:s for s in result['report']['sections']}
        rates={m['key']:m['value'] for m in sections['relic_regeneration']['metrics']}
        self.assertIsNone(rates['rate'])
        self.assertEqual(rates['known_rate'],known['relic_regeneration_rate'])
        rates={m['key']:m['value'] for m in sections['regeneration']['metrics']}
        self.assertIsNone(rates['per_token_rate'])
        self.assertIsNone(rates['all_tokens_rate'])
        self.assertEqual(result['total_damage'],known['total_damage'])
        self.assertEqual(result['estimate']['skill']['total_healing'],known['estimate']['skill']['total_healing'])

    def test_known_multiplier_keeps_normal_public_shape(self):
        result=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_91','rogue_6_relic_legacy_81']})
        self.assertEqual(result['relic_regeneration_multiplier'],1.2)
        self.assertNotIn('known_relic_regeneration_rate',result)
        self.assertTrue(all('known_regeneration_rate' not in t for t in result['relic_token_stats']))

    def test_regeneration_components_keep_labeled_subtotals(self):
        with patch('rouge.relic_healing_factors.regeneration_factor',return_value=None):
            result=calculate_damage({'operator':'char_1037_amiya3','skill':1})
        components=[c for c in result['components'] if c['damage_type']=='regeneration']
        self.assertTrue(components)
        for component in components:
            self.assertIsNone(component['actual_total'])
            self.assertEqual(component['known_regeneration_subtotal']['total'],component['total'])
        block=next(s for s in result['report']['sections'] if s['id']=='regeneration')
        values={m['key']:m['value'] for m in block['metrics']}
        self.assertIsNone(values['window_regeneration'])
        self.assertEqual(values['known_regeneration'],sum(c['total'] for c in components))
