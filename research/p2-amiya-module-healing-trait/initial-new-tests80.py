"""Medical Amiya's reviewed same-trait INC-X ratio in offline references."""
import copy
import unittest
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP='char_1037_amiya3'
MODULE='uniequip_002_amiya3'


def evaluate(skill=1,**extra):
    return calculate_damage({'operator':OP,'skill':skill,'base_attack':1000,
                             'elite':2,'level':50,'module_id':MODULE,'module_level':1,**extra})


def components(result):
    return {component['name']:component for component in result['components']}


class AmiyaModuleHealingTraitTests(unittest.TestCase):
    def test_all_three_stages_replace_the_same_ratio_at_exact_unlock(self):
        for stage in (1,2,3):
            for skill in (1,2):
                for mode in ('frames','continuous'):
                    r=evaluate(skill,module_level=stage,timing_mode=mode)
                    self.assertEqual(components(r)['咒愈师伤害转治疗']['damage_healing']['ratio'],.6)
                    self.assertEqual(r['estimate']['training']['module_level'],stage)
                    if skill==2:
                        self.assertIsNone(r['total_healing'])
                        self.assertFalse(r['amiya_phase_reference']['phase_clock_verified'])
                        self.assertIsNone(components(r)['诚挚期许本体生命回复']['actual_total'])

    def test_inactive_cultivation_retains_half_ratio_and_absent_module_components(self):
        for elite,level in ((0,1),(1,1),(2,49)):
            for stage in (1,2,3):
                for mode in ('frames','continuous'):
                    args={'operator':OP,'skill':1,'base_attack':1000,'elite':elite,'level':level,
                          'skill_rank':7,'timing_mode':mode}
                    base=calculate_damage(args)
                    r=calculate_damage({**args,'module_id':MODULE,'module_level':stage})
                    self.assertEqual(components(r)['咒愈师伤害转治疗']['damage_healing']['ratio'],.5)
                    self.assertEqual(r['components'],base['components'])
                    self.assertEqual(r['total_healing'],base['total_healing'])

    def test_invalid_module_and_level_zero_contracts_remain(self):
        for extra in ({'module_level':0},{'module_level':4},{'module_level':True},
                      {'module_id':'uniequip_002_amiya2'}):
            with self.assertRaisesRegex(ValueError,'模组身份或等级尚无可用规则'):
                evaluate(**extra)
        plain={'operator':OP,'skill':1,'base_attack':1000}
        self.assertEqual(calculate_damage(plain),calculate_damage({**plain,'module_level':0}))

    def test_recharge_normal_attacks_use_the_same_sixty_percent_trait(self):
        for mode in ('frames','continuous'):
            r=evaluate(timing_mode=mode)
            s=r['estimate']['skill']
            recharge_damage=s['cycle_damage']-s['phase_damage']
            recharge_healing=s['cycle_healing']-s['phase_healing']
            self.assertGreater(recharge_damage,0)
            self.assertAlmostEqual(recharge_healing,recharge_damage*.6)

    def test_s2_opening_reference_and_known_sources_use_ratio_without_closing_unknown(self):
        for mode in ('frames','continuous'):
            r=evaluate(2,timing_mode=mode)
            c=components(r)['咒愈师伤害转治疗']
            self.assertEqual(c['total'],16800)
            self.assertIsNone(c['actual_total'])
            self.assertEqual(r['known_healing_subtotals']['window_healing'],1200)
            self.assertEqual(sum(v['total'] for v in c['known_healing_sources']),1200)
            self.assertEqual(r['amiya_phase_reference']['opening_healing_reference'],1200)
            self.assertEqual(r['amiya_phase_reference']['window_reference']['opening_healing_reference'],1200)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['total_healing'])
            self.assertIsNone(r['estimate']['skill']['duration_seconds'])
            self.assertIn('开启伤害派生治疗条件参考：1,200',format_estimate(r))

    def test_resistance_and_damage_modifier_settle_before_linked_healing(self):
        r=evaluate(2,enemy_resistance=40,
                   effects=[{'kind':'damage_taken','damage_type':'magic','value':.3}])
        c=components(r)
        self.assertAlmostEqual(c['慈悲愿景开启伤害']['total'],2000*.6*1.3)
        self.assertAlmostEqual(r['known_healing_subtotals']['window_healing'],2000*.6*1.3*.6)
        self.assertAlmostEqual(c['咒愈师伤害转治疗']['total'],
                               (c['慈悲愿景开启伤害']['total']+c['技能攻击']['total'])*.6)
        self.assertIsNone(r['total_healing'])

    def test_accepted_healing_factor_keeps_known_sources_and_opening_reference_synchronized(self):
        for mode in ('frames','continuous'):
            r=evaluate(2,timing_mode=mode,relic_ids=['rogue_6_relic_legacy_81'])
            c=components(r)
            self.assertEqual(c['咒愈师伤害转治疗']['total'],20160)
            self.assertEqual(r['known_healing_subtotals']['window_healing'],1440)
            self.assertEqual(sum(v['total'] for v in c['咒愈师伤害转治疗']['known_healing_sources']),1440)
            self.assertEqual(r['amiya_phase_reference']['opening_healing_reference'],1440)
            self.assertIsNone(r['total_healing'])
            baseline=evaluate(2,timing_mode=mode)
            self.assertEqual(c['诚挚期许本体生命回复'],components(baseline)['诚挚期许本体生命回复'])

    def test_mathematical_exclusions_and_finite_positive_unknowns_survive(self):
        for mode in ('frames','continuous'):
            for extra in ({'window_seconds':0},{'healing_targets':0},
                          {'timing':{'target_disappears_seconds':0}}):
                r=evaluate(2,timing_mode=mode,**extra)
                self.assertEqual(r['total_healing'],0)
                self.assertEqual(r['known_healing_subtotals']['window_healing'],0)
            r=evaluate(2,timing_mode=mode,window_seconds=.1,
                       timing={'target_disappears_seconds':.1})
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['total_healing'])

    def test_s1_extra_skill_heal_is_separate_and_public_data_is_immutable(self):
        original=copy.deepcopy(catalog())
        plain={'operator':OP,'skill':1,'base_attack':1000,'elite':2,'level':50,'window_seconds':10}
        args={**plain,'module_id':MODULE,'module_level':3,'healing_targets':100}
        untouched=copy.deepcopy(args)
        r=calculate_damage(args)
        baseline=calculate_damage({**plain,'healing_targets':100})
        c=components(r);old=components(baseline)
        self.assertEqual(c['哀恸共情范围治疗'],old['哀恸共情范围治疗'])
        self.assertEqual(c['咒愈师伤害转治疗']['damage_healing']['ratio'],.6)
        self.assertEqual(args,untouched)
        self.assertEqual(catalog(),original)


if __name__=='__main__':unittest.main()
