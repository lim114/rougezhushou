"""Public source boundaries for alternate Amiya opening and phase references."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

TACTICAL='char_1001_amiya2'
MEDICAL='char_1037_amiya3'

def evaluate(op, **extra):
    return calculate_damage({'operator':op,'skill':2,'base_attack':1000,**extra})

def components(result):
    return {c['name']:c for c in result['components']}

class AmiyaPhaseReferenceTests(unittest.TestCase):
    def test_explicit_zero_window_excludes_opening_and_linked_healing_in_both_modes(self):
        for op in (TACTICAL,MEDICAL):
            for mode in ('frames','continuous'):
                r=evaluate(op,timing_mode=mode,window_seconds=0)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['total_healing'],0)
                self.assertEqual(r['estimate']['skill']['window_seconds'],0)
                self.assertTrue(all(c['total']==0 for c in r['components']))

    def test_short_positive_window_does_not_promote_isolated_phase_to_actual(self):
        for op in (TACTICAL,MEDICAL):
            for mode in ('frames','continuous'):
                for window in (.1,1,10):
                    r=evaluate(op,timing_mode=mode,window_seconds=window)
                    self.assertIsNone(r['total_damage'])
                    self.assertEqual(r['estimate']['skill']['window_seconds'],window)
                    if op==MEDICAL:self.assertIsNone(r['total_healing'])

    def test_tactical_original_nine_magic_and_one_true_slash_parameters_survive(self):
        for mode in ('frames','continuous'):
            r=evaluate(TACTICAL,timing_mode=mode)
            refs={c['name']:c for c in r['unbound_cast_reference']['conditional_components']}
            self.assertEqual((refs['绝影前九击']['hits'],refs['绝影前九击']['per_hit'],refs['绝影前九击']['total']),(9,2508,22572))
            self.assertEqual((refs['绝影终击']['hits'],refs['绝影终击']['per_hit'],refs['绝影终击']['total']),(1,5016,5016))
            self.assertEqual(refs['绝影持续真伤']['total'],31920)
            self.assertEqual(r['total_healing'],0)
            for c in r['components']:
                self.assertNotIn('times_seconds',c)
                self.assertNotIn('instant_event',c)
                self.assertIsNone(c['actual_total'])

    def test_declared_kills_only_change_existing_followup_reference(self):
        refs=[]
        for count in range(4):
            r=evaluate(TACTICAL,amiya_slash_kills=count)
            refs.append(r['unbound_cast_reference']['conditional_components'])
            self.assertEqual(r['amiya_phase_reference']['strengthened_attack_reference'],1140+400*count)
            self.assertEqual(refs[-1][-1]['total'],28*(1140+400*count))
            self.assertIsNone(r['total_damage'])
        for ref in refs[1:]:self.assertEqual(ref[:2],refs[0][:2])
        for count in (-1,1.5,4):
            with self.assertRaises(ValueError):evaluate(TACTICAL,amiya_slash_kills=count)

    def test_attack_speed_changes_isolated_followup_but_never_slash_count(self):
        r=evaluate(TACTICAL,effects=[{'kind':'attack_speed','value':100}])
        refs=r['unbound_cast_reference']['conditional_components']
        self.assertEqual([(c['hits'],c['total']) for c in refs[:2]],[(9,22572),(1,5016)])
        self.assertGreater(refs[-1]['hits'],28)
        self.assertIsNone(r['total_damage'])

    def test_nominal_duration_never_extends_from_long_observation(self):
        for op,nominal in ((TACTICAL,35),(MEDICAL,32)):
            r=evaluate(op,window_seconds=100)
            phase=r['amiya_phase_reference']['window_reference']['isolated_attack_phase_reference']
            self.assertEqual(phase['phase_seconds'],nominal)
            self.assertEqual(r['estimate']['skill']['window_seconds'],100)
            self.assertIsNone(r['estimate']['skill']['duration_seconds'])
            self.assertIsNone(r['amiya_phase_reference']['actual_strengthening_start_seconds'])
            self.assertIsNone(r['amiya_phase_reference']['actual_skill_end_seconds'])
            self.assertEqual(r['timing']['streams'],[])

    def test_once_and_deployment_initial_sp_reference_remain(self):
        for op,first in ((TACTICAL,20),(MEDICAL,10)):
            r=evaluate(op)
            skill=r['estimate']['skill']
            self.assertEqual(skill['mode'],'once')
            self.assertEqual(skill['initial_seconds'],first)
            self.assertIsNone(skill['cycle_seconds'])
            self.assertIsNone(skill['recharge_seconds'])
            self.assertIsNone(skill['duration_seconds'])

    def test_zero_enemy_lifetime_excludes_attack_chain_but_not_regeneration_reference(self):
        for mode in ('frames','continuous'):
            for op in (TACTICAL,MEDICAL):
                r=evaluate(op,timing_mode=mode,timing={'target_disappears_seconds':0})
                self.assertEqual((r['total_damage'],r['total_healing']),(0,0))
                if op==MEDICAL:
                    c=components(r)['诚挚期许本体生命回复']
                    self.assertAlmostEqual(c['total'],1327.104)
                    self.assertEqual(c['nominal_duration_reference_seconds'],32)
                    self.assertIsNone(c['actual_total'])

    def test_medical_literal_opening_and_known_linked_subtotal_preserve_parameters(self):
        for mode in ('frames','continuous'):
            r=evaluate(MEDICAL,timing_mode=mode)
            c=components(r)
            self.assertEqual(c['慈悲愿景开启伤害']['total'],2000)
            self.assertTrue(c['慈悲愿景开启伤害']['instant_event'])
            self.assertEqual(c['技能攻击']['total'],26000)
            self.assertEqual(c['咒愈师伤害转治疗']['total'],14000)
            self.assertIsNone(c['咒愈师伤害转治疗']['actual_total'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],2000)
            self.assertEqual(r['known_healing_subtotals']['window_healing'],1000)
            self.assertIsNone(r['total_healing'])

    def test_medical_zero_recipients_remains_known_zero_while_damage_unknown(self):
        r=evaluate(MEDICAL,healing_targets=0)
        self.assertIsNone(r['total_damage'])
        self.assertEqual(r['total_healing'],0)
        self.assertNotIn('actual_total',components(r)['咒愈师伤害转治疗'])

    def test_conditional_healing_uses_after_modifier_damage_and_opening_subtotal(self):
        for factor in (1.3,1.7):
            r=evaluate(MEDICAL,effects=[{'kind':'damage_taken','damage_type':'magic','value':factor-1}])
            c=components(r)
            self.assertEqual(c['慈悲愿景开启伤害']['total'],2000*factor)
            self.assertEqual(c['咒愈师伤害转治疗']['total'],(26000+2000*factor)*.5)
            self.assertEqual(r['known_healing_subtotals']['window_healing'],1000*factor)
            self.assertIsNone(r['total_healing'])

    def test_accepted_healing_factor_scales_known_source_and_subtotal_consistently(self):
        for mode in ('frames','continuous'):
            r=evaluate(MEDICAL,timing_mode=mode,relic_ids=['rogue_6_relic_legacy_81'])
            c=components(r)['咒愈师伤害转治疗']
            self.assertEqual(c['total'],16800)
            self.assertEqual(sum(source['total'] for source in c['known_healing_sources']),1200)
            self.assertEqual(r['known_healing_subtotals']['window_healing'],1200)
            self.assertEqual(r['amiya_phase_reference']['opening_healing_reference'],1200)
            self.assertEqual(r['amiya_phase_reference']['window_reference']['opening_healing_reference'],1200)
            self.assertIsNone(r['total_healing'])
            self.assertIn('开启伤害派生治疗条件参考：1,200',format_estimate(r))
            zero=evaluate(MEDICAL,timing_mode=mode,window_seconds=0,relic_ids=['rogue_6_relic_legacy_81'])
            self.assertEqual(zero['known_healing_subtotals']['window_healing'],0)
            self.assertEqual(zero['total_healing'],0)

    def test_unverified_multiple_healing_factors_do_not_change_partial_reference(self):
        r=evaluate(MEDICAL,relic_ids=['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'])
        self.assertEqual(r['known_healing_subtotals']['window_healing'],1000)
        self.assertEqual(sum(c['total'] for c in components(r)['咒愈师伤害转治疗']['known_healing_sources']),1000)
        self.assertIsNone(r['total_healing'])

    def test_report_labels_nominal_reference_and_unknown_actual_phase(self):
        for op in (TACTICAL,MEDICAL):
            report=format_estimate(evaluate(op))
            self.assertIn('原表技能持续参数',report)
            self.assertIn('实际后续攻击阶段起点：未知',report)
            self.assertIn('实际技能结束时刻：未知',report)
            self.assertIn('单次技能总伤：未知',report)
        report=format_estimate(evaluate(MEDICAL))
        self.assertIn('开启伤害派生治疗条件参考：1,000',report)
        self.assertIn('单次技能已计治疗小计：1,000',report)
        self.assertIn('名义持续参数下生命回复条件参考',report)
        self.assertIn('实际情景生命回复总量：未知',report)
        self.assertIn('单次技能总治疗：未知',report)

    def test_finite_positive_lifetime_does_not_bind_empty_isolated_phase(self):
        for op in (TACTICAL,MEDICAL):
            for mode in ('frames','continuous'):
                r=evaluate(op,timing_mode=mode,window_seconds=1,
                    timing={'target_disappears_seconds':.1})
                self.assertIsNone(r['total_damage'])
                if op==MEDICAL:self.assertIsNone(r['total_healing'])
                phase=r['amiya_phase_reference']['window_reference']['isolated_attack_phase_reference']
                if mode=='frames':self.assertEqual(phase['conditional_hits'],0)
                body='绝影持续真伤' if op==TACTICAL else '技能攻击'
                self.assertIsNone(components(r)[body]['actual_total'])

    def test_public_input_and_returned_reference_are_independent(self):
        scenario={'operator':MEDICAL,'skill':2,'base_attack':1000,'timing':{'target_windows':[[5,10]]}}
        before=copy.deepcopy(scenario)
        expected=calculate_damage(scenario)
        altered=calculate_damage(scenario)
        altered['amiya_phase_reference']['isolated_attack_phase_reference']['conditional_damage']=999
        altered['components'][2].get('known_healing_sources',[]).clear()
        self.assertEqual(calculate_damage(scenario),expected)
        self.assertEqual(scenario,before)

if __name__=='__main__':unittest.main()
