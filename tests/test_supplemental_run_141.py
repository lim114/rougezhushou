import unittest
from copy import deepcopy
from rouge.catalog import operator_attributes
from rouge.supplemental_skills import defaults,skill_reference,supplemental_profiles
from rouge.supplemental_run import run_skill_reference,format_run_reference,selectors


def environment(ids=()):
    return {'relic_ids':list(ids),'run_config':{},'relic_context':{},
            'inventory_status':{'complete':True},'operator_metadata':{}}


class SupplementalRun141Tests(unittest.TestCase):
    def test_seven_unchanged_references_without_runes(self):
        for identity in supplemental_profiles()['operators']:
            with self.subTest(identity=identity):
                p=defaults(identity);before=deepcopy(p);e=environment()
                base=skill_reference(p);r=run_skill_reference(p,e)
                self.assertEqual(r['attributes'],base['attributes'])
                self.assertEqual([{k:v for k,v in row.items() if k not in ('base_value','delta')} for row in r['rows']],base['rows'])
                self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
                self.assertIsNone(r['cycle_output']);self.assertEqual(p,before)

    def test_additive_runes_then_talent_and_skill(self):
        p=defaults();e=environment(['rogue_6_relic_legacy_15','rogue_6_relic_legacy_27','rogue_6_relic_legacy_15'])
        e['run_config']={'squad':{'id':'rogue_6_band_6','effect_verified':True}}
        before=deepcopy(e);r=run_skill_reference(p,e)
        # Original cultivated ATK803; 15% melee +3% fruit +15% squad=33%,
        # rune writer1068, then qualified talent8% and skill50% share battle layer.
        self.assertEqual(r['run_attributes']['attack'],1068)
        self.assertAlmostEqual(r['rows'][1]['value'],1068*1.58)
        self.assertAlmostEqual(r['rows'][1]['delta'],(1068-803)*1.58)
        self.assertEqual(e,before)

    def test_selectors_preserve_profession_and_position(self):
        e=environment(['rogue_6_relic_legacy_64','rogue_6_relic_legacy_15'])
        fang=run_skill_reference(defaults('char_123_fang'),e)
        kroos=run_skill_reference(defaults('char_124_kroos'),e)
        a=operator_attributes('char_123_fang',1,55,100)['attack']
        self.assertEqual(fang['run_attributes']['attack'],round(a*1.65))
        self.assertEqual(kroos['run_attributes']['attack'],operator_attributes('char_124_kroos',1,55,100)['attack'])
        self.assertEqual(selectors()['operators']['char_124_kroos']['subprofession_id'],'fastshot')

    def test_unverified_squad_not_applied(self):
        e=environment();e['run_config']={'squad':{'id':'rogue_6_band_6','effect_verified':False}}
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['run_attributes']['attack'],803)
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('效果阶段尚未确认',format_run_reference(r))

    def test_defense_and_healing_keep_their_own_skill_layer(self):
        e=environment(['rogue_6_relic_legacy_27'])
        beagle=run_skill_reference(defaults('char_122_beagle'),e)
        a=operator_attributes('char_122_beagle',1,55,100)['defense']
        self.assertAlmostEqual(beagle['rows'][1]['value'],round(a*1.03)*1.6)
        hibisc=run_skill_reference(defaults('char_120_hibisc'),e)
        a=operator_attributes('char_120_hibisc',1,55,100)['attack']
        self.assertAlmostEqual(hibisc['rows'][1]['value'],round(a*1.03)*1.58)

    def test_combat_triggers_remain_reference_only(self):
        e=environment(['rogue_6_relic_legacy_53'])
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['attribute_resolution']['runes'],[])
        self.assertEqual(r['attribute_resolution']['unsupported'],[])
        self.assertTrue(r['attribute_resolution']['relics'][0]['reference_effects'])
        self.assertEqual(r['attributes'],skill_reference(defaults())['attributes'])

    def test_gold_missing_and_confirmed_count(self):
        e=environment(['rogue_6_relic_legacy_60'])
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['run_attributes']['attack_speed'],100)
        self.assertIn('gold',format_run_reference(r))
        e['relic_context']['gold']=26
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['run_attributes']['attack_speed'],135)
        self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIsNone(r['cycle_output'])

    def test_targeted_rune_does_not_follow_selection(self):
        e=environment();e['operator_metadata']={'char_208_melan':{
            'char_buff_ids':['rogue_6_from_relic_12'],'char_buffs_complete':True}}
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['run_attributes']['attack'],1767)
        self.assertEqual(r['run_attributes']['attack_speed'],50)
        other=run_skill_reference(defaults('char_124_kroos'),e)
        self.assertEqual(other['run_attributes']['attack_speed'],100)
        self.assertEqual(other['attribute_resolution']['runes'],[])

    def test_forbidden_skill_rejected(self):
        e=environment();e['operator_metadata']={'char_208_melan':{'char_buff_ids':['rogue_6_from_relic_10']}}
        with self.assertRaisesRegex(ValueError,'禁止.*技能'):run_skill_reference(defaults(),e)

    def test_unhandled_sp_and_incomplete_inventory_visible(self):
        e=environment(['rogue_6_relic_legacy_95']);e['inventory_status']['complete']=False
        r=run_skill_reference(defaults('char_123_fang'),e)
        self.assertEqual(r['rows'][0]['value'],6)
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertTrue(r['attribute_resolution']['unsupported'])
        self.assertIn('尚未纳入',format_run_reference(r));self.assertIn('清单尚未确认完整',format_run_reference(r))

    def test_self_heal_uses_rune_hp_then_talent_and_gap(self):
        p=defaults('char_209_ardign');p.update(missing_hp=2750,count=2)
        e=environment(['rogue_6_relic_legacy_27'])
        r=run_skill_reference(p,e)
        hp=operator_attributes(p['operator'],1,55,100)['hp']
        self.assertEqual(r['run_attributes']['hp'],round(hp*1.03))
        self.assertAlmostEqual(r['rows'][1]['value'],round(hp*1.03)*1.12*.4)
        self.assertEqual(r['rows'][2]['value'],min(2750,r['rows'][1]['value']*2))
        self.assertIsNotNone(r['attribute_resolution']['baseline_error'])
        self.assertTrue(all(row['delta'] is None for row in r['rows']))

    def test_no_double_preparation_allowed(self):
        for key,value in [('effects',[]),('_attribute_runes',[]),('base_attack',99999)]:
            e=environment();e[key]=value
            with self.assertRaisesRegex(ValueError,'已处理'):run_skill_reference(defaults(),e)

    def test_unknown_relic_and_invalid_inputs(self):
        r=run_skill_reference(defaults(),environment(['unknown']))
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        for key,value in [('relic_ids','bad'),('operator_metadata',[]),('inventory_status',{'complete':1}),('relic_context',[])]:
            e=environment();e[key]=value
            with self.assertRaises(ValueError):run_skill_reference(defaults(),e)
        for value in (True,float('nan'),-1):
            e=environment(['rogue_6_relic_legacy_60']);e['relic_context']['gold']=value
            with self.assertRaises(ValueError):run_skill_reference(defaults(),e)
