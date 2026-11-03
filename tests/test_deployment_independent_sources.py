import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


INES='char_4087_ines'
ANGEL='char_1041_angel2'


def evaluate(operator, **extra):
    return calculate_damage({'operator':operator,'skill':3,'base_attack':1000,
                             'enemy_defense':0,'enemy_resistance':0,**extra})


def independent(result):
    return result['external_event_reference']['conditional_components'][0]


class DeploymentIndependentSourcesTests(unittest.TestCase):
    def test_empty_observation_has_no_opening_damage_in_either_mode(self):
        for op in (INES,ANGEL):
            for mode in ('frames','continuous'):
                r=evaluate(op,timing_mode=mode,window_seconds=0)
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(r['estimate']['skill']['window_seconds'],0)
                self.assertFalse(r['external_event_reference']['window_reference']['source_possible'])
                self.assertTrue(all(c['total']==0 for c in r['components']))
                self.assertGreater(independent(r)['total'],0)

    def test_zero_current_target_lifetime_excludes_actual_damage(self):
        for op in (INES,ANGEL):
            for mode in ('frames','continuous'):
                for extra in ({},{'window_seconds':10}):
                    r=evaluate(op,timing_mode=mode,timing={'target_disappears_seconds':0},**extra)
                    self.assertEqual(r['total_damage'],0)
                    self.assertTrue(all(c['hits']==0 and c['total']==0 for c in r['components']))
                    self.assertFalse(r['external_event_reference']['source_possible'])
                    self.assertGreater(independent(r)['total'],0)

    def test_independent_collision_reference_is_not_assigned_time_zero(self):
        for op,name,amount in ((INES,'收回影哨',5380),(ANGEL,'投递坐标轰炸',3700)):
            r=evaluate(op,window_seconds=1)
            c=next(c for c in r['components'] if c['name']==name)
            self.assertEqual(independent(r)['total'],amount)
            self.assertEqual(independent(r)['hits'],1)
            self.assertIsNone(c['actual_total'])
            self.assertNotIn('times_seconds',c)
            self.assertNotIn('instant_event',c)
            self.assertIsNone(r['external_event_reference']['actual_event_times_seconds'])
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['estimate']['skill']['hit_counts'][name])

    def test_owner_range_does_not_cancel_independent_path_or_coordinate(self):
        for op,amount in ((INES,5380),(ANGEL,3700)):
            r=evaluate(op,window_seconds=10,timing={'target_windows':[]})
            self.assertEqual(independent(r)['total'],amount)
            self.assertIsNone(r['total_damage'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
            self.assertTrue(r['external_event_reference']['window_reference']['source_possible'])

    def test_owner_interruption_does_not_prove_independent_projectile_absence(self):
        for op in (INES,ANGEL):
            r=evaluate(op,window_seconds=10,timing={'interrupt_windows':[[0,3600]]})
            self.assertIsNone(r['total_damage'])
            self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
            self.assertTrue(r['external_event_reference']['source_possible'])

    def test_body_reference_is_preserved_but_not_published_as_whole_cast(self):
        for op,body in ((INES,43040),(ANGEL,146150)):
            r=evaluate(op)
            self.assertEqual(r['known_damage_subtotals']['total_damage'],body)
            self.assertEqual(r['known_damage_subtotals']['window_damage'],body)
            self.assertIsNone(r['total_damage'])
            self.assertIsNone(r['estimate']['skill']['total_damage'])
            self.assertIsNone(r['estimate']['skill']['phase_damage'])
            self.assertFalse(r['estimate']['complete'])

    def test_shadow_keeps_deployment_initial_and_nonrepeat_reference(self):
        r=evaluate(INES)
        skill=r['estimate']['skill']
        self.assertEqual(skill['mode'],'deployment')
        self.assertEqual(skill['initial_seconds'],0)
        self.assertEqual(skill['duration_seconds'],16)
        self.assertIsNone(skill['recharge_seconds'])
        self.assertIsNone(skill['cycle_seconds'])
        self.assertEqual(independent(r)['per_hit'],5380)
        self.assertEqual(independent(evaluate(INES,stolen_enemy_count=0))['per_hit'],5200)

    def test_ines_first_deployment_remains_only_shadow_placement(self):
        for mode in ('frames','continuous'):
            r=evaluate(INES,timing_mode=mode,ines_first_deployment=True)
            self.assertEqual(r['total_damage'],0)
            self.assertEqual(r['components'],[])
            self.assertNotIn('external_event_reference',r)
            self.assertEqual(r['estimate']['skill']['initial_seconds'],0)

    def test_coordinate_off_keeps_known_ammo_output_and_same_ammo_timeline(self):
        for mode in ('frames','continuous'):
            on=evaluate(ANGEL,timing_mode=mode)
            off=evaluate(ANGEL,timing_mode=mode,delivery_coordinate=False)
            self.assertNotIn('external_event_reference',off)
            self.assertEqual(off['total_damage'],146150)
            for key in ('duration_seconds','initial_seconds','recharge_seconds','cycle_seconds'):
                self.assertEqual(on['estimate']['skill'][key],off['estimate']['skill'][key])
            for name in ('技能攻击','火力电台期望轰炸','火力电台本体生命回复'):
                self.assertEqual(next(c for c in on['components'] if c['name']==name),
                                 next(c for c in off['components'] if c['name']==name))
            self.assertEqual(on['estimate']['skill']['hit_counts']['技能攻击'],50)

    def test_independent_damage_preserves_per_collision_mitigation(self):
        for op,amount in ((INES,5180),(ANGEL,3500)):
            r=evaluate(op,enemy_defense=200)
            self.assertEqual(independent(r)['total'],amount)
            self.assertIsNone(r['total_damage'])

    def test_positive_observation_is_kept_and_late_body_is_separate(self):
        for op in (INES,ANGEL):
            r=evaluate(op,window_seconds=1,timing={'target_windows':[[5,100]]})
            self.assertEqual(r['estimate']['skill']['window_seconds'],1)
            self.assertEqual(r['known_damage_subtotals']['window_damage'],0)
            self.assertIsNone(r['total_damage'])
            self.assertEqual(r['external_event_reference']['window_reference']['observation_seconds'],1)

    def test_shadow_fee_depends_on_unplaced_path_damage_and_is_not_opening_fee(self):
        r=evaluate(INES)
        fee=next(s for s in r['report']['sections'] if s['id']=='dp')
        values={m['key']:m['value'] for m in fee['metrics']}
        self.assertIsNone(values['per_cast'])
        self.assertIsNone(values['active_rate'])
        self.assertEqual(values['known_subtotal'],16)
        self.assertEqual(values['shadow_per_hit'],1)
        self.assertNotIn('immediate',values)
        text=format_estimate(r)
        self.assertIn('影哨每个路径伤害事件回费参数：1',text)
        self.assertNotIn('开启时立即回费：1',text)

    def test_report_explains_actual_unknown_and_retained_source_reference(self):
        for op,label,value in ((INES,'收回影哨条件总量','5,380'),(ANGEL,'投递坐标轰炸条件总量','3,700')):
            text=format_estimate(evaluate(op,window_seconds=1))
            self.assertIn('独立条件来源 · 事件时钟待核验',text)
            self.assertIn(label+'：'+value,text)
            self.assertIn('实际事件时刻：未知',text)
            self.assertIn('观察窗口总伤：未知',text)


if __name__=='__main__':unittest.main()
