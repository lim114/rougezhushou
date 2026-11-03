"""Source-bound low-HP output layer and receiver factors stay distinct."""
import copy,unittest
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.reporting import build_report
from rouge.susuro_healing import reference,FP_ONE,FP_LARGE_EPS_RAW,selected_trait

OP='char_298_susuro'
def evaluate(skill=1,**extra):
    return calculate_damage({'operator':OP,'skill':skill,'base_attack':1000,
        'module_id':'uniequip_002_susuro','module_level':3,**extra})

class SusuroModuleHealingTests(unittest.TestCase):
    def test_both_skills_and_recharge_receive_output_factor_once(self):
        for skill in (1,2):
            for mode in ('frames','continuous'):
                plain=evaluate(skill,timing_mode=mode,healing_target_hp_ratio=.8)
                low=evaluate(skill,timing_mode=mode,healing_target_hp_ratio=.4)
                for key in ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps'):
                    self.assertAlmostEqual(low['estimate']['skill'][key],plain['estimate']['skill'][key]*1.15)
                self.assertEqual(low['timing'],plain['timing'])
                self.assertEqual(low['total_damage'],plain['total_damage'])
                self.assertEqual(low['relic_regeneration_rate'],plain['relic_regeneration_rate'])
                self.assertAlmostEqual(next(c['per_hit'] for c in low['components'] if c['damage_type']=='healing'),1955 if skill==1 else 2300)

    def test_three_module_stages_and_low_cost_factor_compose_as_separate_layers(self):
        for stage,pot,factor in ((1,1,1.2),(1,5,1.23),(2,1,1.23),(2,5,1.26),(3,1,1.25),(3,5,1.28)):
            base=evaluate(module_level=stage,potential=pot,healing_target_hp_ratio=.8)
            low=evaluate(module_level=stage,potential=pot,healing_target_hp_ratio=.4,low_cost_healing_target=True)
            for key in ('total_healing','cycle_healing'):
                self.assertAlmostEqual(low['estimate']['skill'][key],base['estimate']['skill'][key]*factor*1.15)

    def test_flowers_multiply_healing_but_the_source_output_trait_does_not_scale_regen(self):
        ids=['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83','rogue_6_relic_legacy_22','rogue_6_relic_legacy_91']
        plain=evaluate(healing_target_hp_ratio=.8)
        ref=evaluate(healing_target_hp_ratio=.5,low_cost_healing_target=True,relic_ids=ids)
        self.assertAlmostEqual(ref['estimate']['skill']['total_healing'],plain['estimate']['skill']['total_healing']*1.15*1.25*2.184)
        self.assertAlmostEqual(ref['relic_regeneration_rate'],(3+ref['estimate']['base_stats']['hp']*.01)*1.9)
        self.assertFalse(ref['susuro_module_healing_reference']['natural_regeneration_affected'])
        low=evaluate(healing_target_hp_ratio=.5,relic_ids=ids)
        high=evaluate(healing_target_hp_ratio=.8,relic_ids=ids)
        self.assertEqual(low['relic_regeneration_rate'],high['relic_regeneration_rate'])

    def test_native_le_uses_exact_raw_tolerance_boundary(self):
        boundary=FP_ONE//2+FP_LARGE_EPS_RAW
        for raw,expected in ((FP_ONE//2,True),(boundary-1,True),(boundary,False),(boundary+1,False)):
            ref=evaluate(healing_target_hp_ratio=raw/FP_ONE)['susuro_module_healing_reference']
            self.assertEqual(ref['recipient_hp_ratio_raw_reference'],raw)
            self.assertIs(ref['qualified'],expected)
        self.assertIs(evaluate(healing_target_hp_ratio=.500005)['susuro_module_healing_reference']['qualified'],True)
        self.assertIs(evaluate(healing_target_hp_ratio=.50002)['susuro_module_healing_reference']['qualified'],False)

    def test_unspecified_recipient_keeps_subtotal_and_masks_affected_complete_healing(self):
        high=evaluate(healing_target_hp_ratio=.8,low_cost_healing_target=True)
        missing=evaluate(low_cost_healing_target=True)
        self.assertEqual(missing['components'],high['components'])
        for key,value in missing['known_healing_subtotals'].items():
            self.assertEqual(value,high['estimate']['skill'][key])
            self.assertIsNone(missing['estimate']['skill'][key])
        self.assertIsNone(missing['total_healing'])
        self.assertFalse(missing['complete'])
        self.assertIsNone(missing['susuro_module_healing_reference']['qualified'])
        self.assertEqual(missing['timing'],high['timing'])

    def test_zero_source_and_empty_window_are_known_zero_even_when_ratio_unknown(self):
        zero=evaluate(healing_targets=0)
        self.assertEqual(zero['total_healing'],0)
        self.assertEqual(zero['estimate']['skill']['cycle_healing'],0)
        self.assertEqual(zero['complete'],evaluate(healing_targets=0,healing_target_hp_ratio=.8)['complete'])
        empty=evaluate(window_seconds=0)
        self.assertEqual(empty['total_healing'],0)
        self.assertEqual(empty['estimate']['skill']['window_hps'],evaluate(window_seconds=0,healing_target_hp_ratio=.8)['estimate']['skill']['window_hps'])
        self.assertIsNone(empty['estimate']['skill']['total_healing'])

    def test_locked_module_and_other_operator_never_apply_stale_ratio(self):
        for extra in ({'level':39},{'elite':1,'skill_rank':7},{'module_id':None,'module_level':0}):
            plain=evaluate(**extra)
            stale=evaluate(**extra,healing_target_hp_ratio=.1)
            self.assertEqual(plain,stale)
            self.assertNotIn('susuro_module_healing_reference',stale)
        a=calculate_damage({'operator':'char_196_sunbr','skill':2})
        b=calculate_damage({'operator':'char_196_sunbr','skill':2,'healing_target_hp_ratio':.1})
        self.assertEqual(a,b)

    def test_recipient_condition_is_not_taken_from_self_or_enemy_hp(self):
        for extra in ({'current_hp_ratio':.1},{'enemy_current_hp':1},{'missing_hp':10000}):
            ref=evaluate(**extra)['susuro_module_healing_reference']
            self.assertIsNone(ref['recipient_hp_ratio'])
            self.assertIsNone(ref['qualified'])

    def test_ratio_validation_and_input_result_isolation(self):
        for value in (True,False,'0.4',-.1,1.1,10**1000,float('nan'),float('inf'),[],{}):
            with self.assertRaises(ValueError):evaluate(healing_target_hp_ratio=value)
        scenario={'operator':OP,'skill':1,'module_id':'uniequip_002_susuro','module_level':3,'healing_target_hp_ratio':.4}
        before=copy.deepcopy(scenario);a=calculate_damage(scenario);a['susuro_module_healing_reference']['factor']=99
        self.assertEqual(scenario,before)
        self.assertEqual(calculate_damage(scenario)['susuro_module_healing_reference']['factor'],1.15)

    def test_nonrepeat_cycle_is_not_invented_by_factor(self):
        result=evaluate(2,casts_used=1,healing_target_hp_ratio=.4)
        self.assertGreater(result['estimate']['skill']['total_healing'],0)
        self.assertIsNone(result['estimate']['skill']['cycle_healing'])
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])

    def test_structured_report_exposes_unknown_recipient_and_native_boundary(self):
        scenario={'operator':OP,'skill':1,'module_id':'uniequip_002_susuro','module_level':3}
        r=calculate_damage(scenario);block=next(s for s in build_report(scenario,r)['sections'] if s['id']=='susuro_module_healing')
        metrics={m['key']:m['value'] for m in block['metrics']}
        self.assertIsNone(metrics['recipient_ratio']);self.assertEqual(metrics['qualified'],'未知')
        self.assertIsNone(metrics['healing_factor']);self.assertEqual(metrics['regen_factor'],1)
        self.assertTrue(any('50%' in note and '42950' in note for note in block['notes']))

if __name__=='__main__':unittest.main()
