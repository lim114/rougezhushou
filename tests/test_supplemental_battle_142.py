import unittest
from copy import deepcopy
from rouge.supplemental_skills import defaults,skill_reference,supplemental_profiles
from rouge.supplemental_run import run_skill_reference,format_run_reference
from tests.test_supplemental_run_141 import environment


PARTS='rogue_6_relic_cargo_2'
EMERGENCY='rogue_6_relic_cargo_10'
GRUDGE='rogue_6_relic_artifact_7'
FRUIT='rogue_6_relic_legacy_27'


def emergency_environment(identity):
    e=environment([EMERGENCY])
    e['operator_metadata'][identity]={'recruitment_kind':'emergency_hire'}
    return e


class SupplementalBattle142Tests(unittest.TestCase):
    def test_rune_and_squad_writeback_then_ordinary_talent_skill_sum(self):
        e=emergency_environment('char_208_melan')
        e['relic_ids'] += [PARTS,GRUDGE,FRUIT,EMERGENCY]
        e['relic_context']={'parts_count':2,'grudge_stacks':100}
        e['run_config']={'squad':{'id':'rogue_6_band_6','effect_verified':True}}
        p=defaults();before=deepcopy(e)
        r=run_skill_reference(p,e)
        # ATK803 -> rune3%+2%+15%, integer964. Ordinary40%+16%+20%,
        # talent8%+skill50% in one subsequent additive multiplier.
        self.assertEqual(r['run_attributes']['attack'],964)
        self.assertAlmostEqual(r['attributes']['attack'],964*1.84)
        self.assertAlmostEqual(r['rows'][1]['value'],964*2.34)
        self.assertAlmostEqual(r['rows'][1]['delta'],964*2.34-803*1.58)
        self.assertEqual(len(r['attribute_resolution']['ordinary']),6)
        self.assertEqual(r['attribute_resolution']['unsupported'],[])
        self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertEqual(r['talents'],skill_reference(p)['talents'])
        self.assertEqual(e,before)

    def test_seven_operators_use_emergency_attributes_without_changing_clocks(self):
        for identity in supplemental_profiles()['operators']:
            with self.subTest(identity=identity):
                p=defaults(identity);r=run_skill_reference(p,emergency_environment(identity))
                base=skill_reference(p)
                for stat in ('attack','hp','defense'):
                    self.assertAlmostEqual(r['attributes'][stat]-base['attributes'][stat],
                                           r['run_attributes'][stat]*.4)
                self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
                self.assertIsNone(r['cycle_output'])
                self.assertIsNone(r['actual_activation_verified'])
                self.assertEqual(r['skill_parameter'],base['skill_parameter'])

    def test_defense_skill_and_heal_skill_keep_additive_layer(self):
        for identity,row,factor in [('char_122_beagle',1,2.0),('char_120_hibisc',1,1.98)]:
            p=defaults(identity)
            r=run_skill_reference(p,emergency_environment(identity))
            basis=r['run_attributes']['defense' if identity=='char_122_beagle' else 'attack']
            self.assertAlmostEqual(r['rows'][row]['value'],basis*factor)

    def test_parts_and_hp_talent_determine_legal_heal_budget(self):
        p=defaults('char_209_ardign');p.update(missing_hp=3200,count=2)
        e=environment([PARTS]);e['relic_context']['parts_count']=4
        r=run_skill_reference(p,e)
        # Original HP2430, talent12% and ordinary32% share one layer.
        self.assertAlmostEqual(r['attributes']['hp'],2430*1.44)
        self.assertAlmostEqual(r['rows'][1]['value'],2430*1.44*.4)
        potential=2430*1.44*.4*2
        self.assertAlmostEqual(r['rows'][2]['value'],potential)
        self.assertEqual(r['rows'][3]['value'],0)
        self.assertIsNotNone(r['attribute_resolution']['baseline_error'])
        self.assertTrue(all(row['delta'] is None for row in r['rows']))
        p['missing_hp']=3500
        with self.assertRaisesRegex(ValueError,'最大生命'):run_skill_reference(p,e)

    def test_parts_caps_and_missing_count_are_not_zero(self):
        e=environment([PARTS])
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['attribute_resolution']['ordinary'],[])
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('parts_count',format_run_reference(r))
        for count in (0,1,99,10000):
            e['relic_context']['parts_count']=count
            r=run_skill_reference(defaults(),e)
            self.assertAlmostEqual(r['attributes']['attack'],803*(1.08+.08*min(count,99)))
            self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
        for count in (True,float('nan'),-1,1.5,10001):
            e['relic_context']['parts_count']=count
            with self.assertRaises(ValueError):run_skill_reference(defaults(),e)

    def test_grudge_initial_rune_and_confirmed_retained_counter(self):
        e=environment([GRUDGE])
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['run_attributes']['attack'],819)
        self.assertEqual(r['attribute_resolution']['ordinary'],[])
        self.assertIn('grudge_stacks',format_run_reference(r))
        for count in (0,100,999,1000):
            e['relic_context']['grudge_stacks']=count
            r=run_skill_reference(defaults(),e)
            self.assertEqual(r['run_attributes']['attack'],819)
            self.assertAlmostEqual(r['rows'][1]['value'],819*(1.58+.002*min(count,999)))
            self.assertEqual(len(r['attribute_resolution']['ordinary']),1)
        text=format_run_reference(r)
        self.assertIn('持久层数999',text)
        self.assertIn('不模拟击倒事件',text)

    def test_emergency_identity_unknown_normal_and_other_operator(self):
        e=environment([EMERGENCY]);e['relic_context']['emergency_hire']=1
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['attributes'],skill_reference(defaults())['attributes'])
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        e['operator_metadata']['char_208_melan']={'recruitment_kind':'non_emergency'}
        r=run_skill_reference(defaults(),e)
        self.assertEqual(r['attribute_resolution']['battle_attributes']['attack_pct'],0)
        self.assertTrue(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('本项增益为0',format_run_reference(r))
        e['operator_metadata']['char_208_melan']['recruitment_kind']='emergency_hire'
        other=run_skill_reference(defaults('char_124_kroos'),e)
        self.assertEqual(other['attributes'],skill_reference(defaults('char_124_kroos'))['attributes'])
        self.assertFalse(other['attribute_resolution']['complete_for_attribute_scope'])

    def test_critical_and_magic_hit_mitigation_after_ordinary_multiplier(self):
        p=defaults('char_124_kroos');p['enemy_defense']=200
        r=run_skill_reference(p,emergency_environment(p['operator']))
        attack=r['run_attributes']['attack']*1.4
        normal=max(attack-200,attack*.05);critical=max(attack*1.5-200,attack*1.5*.05)
        self.assertAlmostEqual(r['rows'][0]['value'],normal)
        self.assertAlmostEqual(r['rows'][1]['value'],critical)
        self.assertAlmostEqual(r['rows'][2]['value'],normal*.8+critical*.2)
        self.assertAlmostEqual(r['rows'][4]['value'],max(attack*1.4-200,attack*1.4*.05)*2)
        self.assertIsNone(r['rows'][5]['value'])
        p=defaults('char_210_stward');p['enemy_resistance']=50
        r=run_skill_reference(p,emergency_environment(p['operator']))
        self.assertAlmostEqual(r['rows'][1]['value'],r['run_attributes']['attack']*1.46*1.9*.5)

    def test_dp_cost_and_combat_only_rules_not_silently_consumed(self):
        p=defaults('char_123_fang');e=emergency_environment(p['operator'])
        e['relic_ids']+=['rogue_6_relic_legacy_141','rogue_6_relic_fight_14','rogue_6_relic_legacy_57']
        e['relic_context']['current_hp_ratio']=.3
        e['relic_context']['battle_start_shields']=2
        r=run_skill_reference(p,e)
        self.assertEqual(r['rows'][0]['value'],6)
        self.assertEqual(r['rows'][1]['value'],skill_reference(p)['rows'][1]['value'])
        self.assertAlmostEqual(r['attributes']['attack'],r['run_attributes']['attack']*1.4)
        self.assertAlmostEqual(r['attributes']['hp'],r['run_attributes']['hp']*1.4)
        self.assertTrue(r['attribute_resolution']['unsupported'])
        self.assertTrue(any(effect['kind']=='hp_pct' and effect['relic_id']=='rogue_6_relic_legacy_57'
                            for effect in r['attribute_resolution']['unsupported']))
        cocoa=next(record for record in r['attribute_resolution']['relics'] if record['id']=='rogue_6_relic_fight_14')
        self.assertTrue(cocoa['reference_effects'])
        self.assertIn('尚未纳入',format_run_reference(r))
