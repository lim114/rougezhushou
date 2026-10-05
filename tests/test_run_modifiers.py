"""Independent worked values through the public calculation seam."""
import unittest
from rouge.damage import calculate_damage

class RunModifierTests(unittest.TestCase):
    def test_squad_buff_applies_to_independent_token_stats_and_output(self):
        base={'operator':'char_110_deepcl','skill':1,'elite':2,'level':70,'skill_rank':10}
        plain=calculate_damage(base)
        result=calculate_damage({**base,'run_config':{'squad':{'id':'rogue_6_band_6','effect_verified':True}}})
        token=next(t for t in result['relic_token_stats'] if t['id']=='token_10001_deepcl_tentac')
        self.assertIn('分队',token['modifier_sources'])
        self.assertEqual(token['attack'],531) # round-even(462*1.15)
        self.assertEqual(token['hp'],2318) # round-even(2016*1.15)
        self.assertEqual(token['defense'],385) # round-even(335*1.15)
        before=next(c['total'] for c in plain['components'] if c['name']=='触手')
        after=next(c['total'] for c in result['components'] if c['name']=='触手')
        self.assertGreater(after,before)

    def test_spear_squad_and_attack_relic_share_the_additive_attribute_bucket(self):
        base={'operator':'mechanist','skill':1,'elite':2,'level':90,'trust':100,'potential':1,
              'skill_rank':10,'module_id':None,'module_level':0,'timing_mode':'frames'}
        plain=calculate_damage(base)
        # Raw game BAND record: all friendly units ATK/HP/DEF +15%.
        run={'squad':{'id':'rogue_6_band_6','name':'矛头分队','level':0,'effect_verified':True}}
        result=calculate_damage({**base,'run_config':run})
        self.assertEqual(result['estimate']['base_stats']['attack'],659) # round-even(573*1.15)
        self.assertEqual(result['estimate']['base_stats']['hp'],4176) # round-even(3631*1.15)
        self.assertEqual(result['estimate']['base_stats']['defense'],880) # round-even(765*1.15)
        mixed=calculate_damage({**base,'run_config':run,'effects':[{'kind':'attack_pct','value':.2}]})
        self.assertAlmostEqual(mixed['estimate']['base_stats']['attack'],659*1.2) # battle multiplier after rune
        relic=calculate_damage({**base,'run_config':run,'relic_ids':['rogue_6_relic_legacy_15']})
        self.assertEqual(relic['estimate']['base_stats']['attack'],745) # round-even(573*1.30); same rune bucket
        self.assertIn('矛头分队',mixed['run_resolution']['squad']['name'])

    def test_unverified_squad_cannot_change_stats_or_create_its_initial_gift(self):
        base={'operator':'mechanist','skill':1,'level':90,'skill_rank':10,'relic_ids':[]}
        plain=calculate_damage(base)
        unknown=calculate_damage({**base,'run_config':{'squad':{'id':'rogue_6_band_6','effect_verified':False}}})
        self.assertEqual(unknown['estimate']['base_stats'],plain['estimate']['base_stats'])
        self.assertTrue(unknown['run_resolution']['pending'])
        known=calculate_damage({**base,'run_config':{'squad':{'id':'rogue_6_band_7','effect_verified':True}}})
        self.assertEqual(known['relic_resolution']['records'],[])
        self.assertEqual(known['relic_resolution']['rules'],[])

    def test_normal_difficulty_zero_is_not_overwritten_by_monthly_mode(self):
        result=calculate_damage({'operator':'mechanist','skill':1,'run_config':{'difficulty':{'value':0}}})
        self.assertEqual(result['run_resolution']['difficulty']['mode'],'NORMAL')
        self.assertNotIn('每月1日',result['run_resolution']['difficulty']['rule'])
        self.assertTrue(result['run_resolution']['pending'])
        self.assertFalse(result['estimate']['complete'])
