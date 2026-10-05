import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


class AdaptiveReportTests(unittest.TestCase):
    def test_kaltsit_window_healing_stays_distinct_from_full_skill_healing(self):
        result=calculate_damage({'operator':'kaltsit','skill':2,'base_attack':1000,
            'healing_targets':3,'window_seconds':6})
        panel=next(s for s in result['report']['sections'] if s['id']=='healing')
        values={m['key']:m['value'] for m in panel['metrics']}
        # Ten full rounds heal150000; only two firing events occur in6seconds.
        self.assertEqual(values['per_cast'],150000)
        self.assertEqual(values['window_healing'],30000)

    def test_protection_elements_and_summons_only_appear_where_they_exist(self):
        shield=calculate_damage({'operator':'mechanist','skill':2})
        text=format_estimate(shield)
        self.assertIn('屏障与防护',text)
        self.assertNotIn('治疗输出',text)
        self.assertNotIn('费用收益',text)
        tentacle=format_estimate(calculate_damage({'operator':'char_110_deepcl','skill':1}))
        self.assertIn('召唤与协同',tentacle)
        self.assertIn('生命回复',tentacle)
        self.assertNotIn('治疗输出',tentacle)
        neural=format_estimate(calculate_damage({'operator':'char_1042_phatm2','skill':1}))
        self.assertIn('元素机制',neural)
        medic=format_estimate(calculate_damage({'operator':'char_298_susuro','skill':1}))
        for title in ('费用收益','屏障与防护','召唤与协同','元素机制','控制与状态','伤害输出'):
            self.assertNotIn('【'+title+'】',medic)
        self.assertIn('【治疗输出】',medic)
        other=format_estimate(calculate_damage({'operator':'mechanist','skill':1}))
        self.assertNotIn('【屏障与防护】',other)

    def test_ines_fee_counts_attack_events_not_each_damage_type_or_short_window(self):
        result=calculate_damage({'operator':'char_4087_ines','skill':1})
        fee=next(s for s in result['report']['sections'] if s['id']=='dp')
        self.assertEqual(next(m['value'] for m in fee['metrics'] if m['key']=='per_cast'),2)
        # Three DOT ticks are not three additional DP-generating attacks.
        full=calculate_damage({'operator':'char_4087_ines','skill':2})
        short=calculate_damage({'operator':'char_4087_ines','skill':2,'window_seconds':1})
        def amount(r):
            s=next(s for s in r['report']['sections'] if s['id']=='dp')
            return next(m['value'] for m in s['metrics'] if m['key']=='per_cast')
        self.assertEqual(amount(full),amount(short))
        self.assertGreater(amount(full),1)
        first=calculate_damage({'operator':'char_4087_ines','skill':3,'ines_first_deployment':True})
        self.assertEqual(amount(first),0)

    def test_closure_first_skill_growth_is_capped_and_deployment_rebate_is_separate(self):
        result=calculate_damage({'operator':'char_4228_closur','skill':1,'closure_prior_casts':100})
        fee=next(s for s in result['report']['sections'] if s['id']=='dp')
        values={m['key']:m['value'] for m in fee['metrics']}
        self.assertEqual(values['per_cast'],7)
        self.assertAlmostEqual(values['active_rate'],7/8)
        second=calculate_damage({'operator':'char_4228_closur','skill':2})
        fee=next(s for s in second['report']['sections'] if s['id']=='dp')
        self.assertEqual(next(m['value'] for m in fee['metrics'] if m['key']=='per_cast'),25)
        rebate=next(s for s in second['report']['sections'] if s['id']=='deployment_cost')
        self.assertEqual(rebate['metrics'][0]['value'],40)
        self.assertIsNone(rebate['metrics'][1]['value'])

    def test_silverash_fee_generation_and_deployment_discount_are_different_mechanisms(self):
        third=calculate_damage({'operator':'silverash','skill':3})
        fee=next(s for s in third['report']['sections'] if s['id']=='dp')
        values={m['key']:m['value'] for m in fee['metrics']}
        self.assertEqual(values['immediate'],9)
        self.assertEqual(values['gradual'],24)
        self.assertEqual(values['per_cast'],33)
        second=calculate_damage({'operator':'silverash','skill':2})
        self.assertNotIn('dp',[s['id'] for s in second['report']['sections']])
        discount=next(s for s in second['report']['sections'] if s['id']=='deployment_cost')
        self.assertEqual(discount['metrics'][0]['value'],11)
        other=format_estimate(calculate_damage({'operator':'char_133_mm','skill':2}))
        self.assertNotIn('费用收益',other)
        self.assertNotIn('部署费用调整',other)

    def test_myrtle_skill_one_reports_fee_efficiency_without_a_healing_panel(self):
        result=calculate_damage({'operator':'char_151_myrtle','skill':1,'skill_rank':10})
        fee=next(s for s in result['report']['sections'] if s['id']=='dp')
        values={m['key']:m['value'] for m in fee['metrics']}
        # S1M3 returns14 over8s; recharge22, full cycle30, initial9.
        self.assertEqual(values['per_cast'],14)
        self.assertAlmostEqual(values['active_rate'],1.75)
        self.assertAlmostEqual(values['cycle_rate'],14/30)
        text=format_estimate(result)
        self.assertIn('费用收益',text)
        self.assertNotIn('治疗输出',text)
        self.assertNotIn('总治疗',text)


if __name__=='__main__':unittest.main()
