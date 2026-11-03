import unittest
from rouge.damage import calculate_damage
from rouge.reporting import format_report

NOTE='真实友方获取时钟未核验'

class FriendlyScopeReportTests(unittest.TestCase):
    def evaluate(self,mode,**extra):
        return calculate_damage({'operator':'char_298_susuro','skill':1,'timing_mode':mode,
                                 'window_seconds':10,'timing':{'target_disappears_seconds':0},**extra})

    def test_both_modes_keep_semantic_scope_warning(self):
        for mode in ('frames','continuous'):
            r=self.evaluate(mode)
            self.assertTrue(any(NOTE in note for note in r['estimate']['notes']))
            self.assertTrue(any(NOTE in note for note in r['timing']['target_scope_notes']))
            self.assertEqual(r['total_damage'],0)
            self.assertGreater(r['total_healing'],0)

    def test_actual_ui_scenario_shape_and_report_toggles_keep_warning(self):
        for mode in ('frames','continuous'):
            r=self.evaluate(mode,unconfirmed_training=['精英阶段','当前等级'],low_cost_healing_target=False)
            for technical in (False,True):
                self.assertEqual(format_report(r,technical=technical).count(NOTE),1)

    def test_continuous_does_not_gain_frame_claims(self):
        r=self.evaluate('continuous')
        self.assertNotIn('30Hz参考事件模型','\n'.join(r['estimate']['notes']))
        self.assertNotIn('战斗时序参考',format_report(r))
        self.assertNotIn('resource_and_damage_shared_clock',r['timing'])

    def test_empty_enemy_windows_preserve_same_scope_warning(self):
        for mode in ('frames','continuous'):
            r=self.evaluate(mode,timing={'target_windows':[]})
            self.assertIn(NOTE,format_report(r))
            self.assertEqual(r['total_damage'],0)
            self.assertGreater(r['total_healing'],0)

    def test_zero_recipient_warning_does_not_create_healing(self):
        for mode in ('frames','continuous'):
            r=self.evaluate(mode,healing_targets=0)
            self.assertEqual(r['total_healing'],0)
            self.assertIn(NOTE,format_report(r))

    def test_hostile_attack_triggered_healing_does_not_gain_friendly_scope(self):
        for mode in ('frames','continuous'):
            r=calculate_damage({'operator':'char_1037_amiya3','skill':1,'timing_mode':mode,
                'window_seconds':10,'timing':{'target_disappears_seconds':0}})
            self.assertEqual(r['timing']['target_scope_notes'],[])
            self.assertEqual(r['total_healing'],0)
            self.assertNotIn(NOTE,format_report(r))
