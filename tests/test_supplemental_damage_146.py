import unittest
from rouge.supplemental_skills import defaults,skill_reference
from rouge.supplemental_run import run_skill_reference,format_run_reference
from tests.test_supplemental_run_141 import environment


class SupplementalDamage146Tests(unittest.TestCase):
    def test_def_down_penetration_then_physical_damage_scale(self):
        p=defaults('char_124_kroos');p['enemy_defense']=400
        e=environment(['rogue_6_relic_legacy_84','rogue_6_relic_legacy_5'])
        e['operator_metadata'][p['operator']]={'char_buff_ids':['rogue_6_from_relic_5']}
        r=run_skill_reference(p,e);attack=r['attributes']['attack']
        self.assertEqual(r['damage_reference']['effective_target_defense'],180)
        self.assertAlmostEqual(r['rows'][0]['value'],max(attack-180,attack*.05)*1.15)
        self.assertAlmostEqual(r['rows'][4]['value'],max(attack*1.4-180,attack*1.4*.05)*2*1.15)
        self.assertIsNone(r['rows'][5]['value'])
        self.assertEqual(r['preview']['enemy_defense'],400)

    def test_def_down_combination_does_not_fall_back_as_complete_damage(self):
        p=defaults();p['enemy_defense']=500
        r=run_skill_reference(p,environment(['rogue_6_relic_legacy_84','rogue_6_relic_legacy_85']))
        self.assertIsNone(r['damage_reference']['effective_target_defense'])
        self.assertIsNone(r['rows'][2]['value']);self.assertIsNone(r['rows'][2]['delta'])
        self.assertEqual(r['rows'][1]['value'],skill_reference(p)['rows'][1]['value'])

    def test_magic_scale_after_resistance_and_physical_scale_is_separate(self):
        p=defaults('char_210_stward');p['enemy_resistance']=50
        base=skill_reference(p)
        r=run_skill_reference(p,environment(['rogue_6_relic_legacy_8','rogue_6_relic_legacy_5']))
        self.assertAlmostEqual(r['rows'][1]['value'],base['rows'][1]['value']*1.2)
        self.assertAlmostEqual(r['rows'][1]['delta'],base['rows'][1]['value']*.2)

    def test_multi_damage_scale_unknown_does_not_zero_all_types(self):
        p=defaults();r=run_skill_reference(p,environment(['rogue_6_relic_legacy_5','rogue_6_relic_legacy_6']))
        self.assertIsNone(r['rows'][2]['value']);self.assertIsNone(r['rows'][2]['declared_total'])
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('组合未知',format_run_reference(r))
        p=defaults('char_210_stward')
        r=run_skill_reference(p,environment(['rogue_6_relic_legacy_5','rogue_6_relic_legacy_6']))
        self.assertEqual(r['rows'][1]['value'],skill_reference(p)['rows'][1]['value'])

    def test_recipient_isolation_and_duplicate_damage_item(self):
        p=defaults('char_124_kroos');p['enemy_defense']=300
        e=environment(['rogue_6_relic_legacy_5','rogue_6_relic_legacy_5'])
        r=run_skill_reference(p,e)
        self.assertEqual(r['damage_reference']['penetration_ratio'],0)
        self.assertAlmostEqual(r['damage_reference']['damage_factors']['physical'],1.15)
        e['operator_metadata']['char_124_kroos']={'char_buff_ids':['rogue_6_from_relic_5']}
        other=run_skill_reference(defaults('char_208_melan'),e)
        self.assertEqual(other['damage_reference']['penetration_ratio'],0)

    def test_physical_floor_is_scaled_after_floor_not_added_to_attack(self):
        p=defaults();p['enemy_defense']=10000
        base=skill_reference(p)
        r=run_skill_reference(p,environment(['rogue_6_relic_legacy_5']))
        self.assertEqual(r['attributes'],base['attributes'])
        self.assertAlmostEqual(r['rows'][2]['value'],base['rows'][1]['value']*.05*1.15)
