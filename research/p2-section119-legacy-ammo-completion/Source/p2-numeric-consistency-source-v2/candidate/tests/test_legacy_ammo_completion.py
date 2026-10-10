"""Public-path completion regression proposal; unexecuted Source only."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report


def scenario(op='mechanist', skill=1, **extra):
    value={'operator':op,'skill':skill,'elite':2,'level':1,'skill_rank':7,
           'trust':0,'potential':1,'base_attack':1000,'enemy_defense':0,
           'enemy_resistance':0,'timing_mode':'frames','window_seconds':10,
           'timing':{'windup_frames':0,'recovery_frames':0}}
    if op=='kaltsit':value['healing_targets']=2
    value.update(extra)
    return value


class LegacyAmmoCompletionTests(unittest.TestCase):
    def calculate(self,source):
        prior=copy.deepcopy(source)
        result=calculate_damage(source)
        self.assertEqual(source,prior)
        return result

    def test_partial_two_ammo_families_keep_window_but_do_not_publish_full_cast(self):
        for op,number,expected in (('mechanist',1,11000),('kaltsit',2,15750)):
            for gate in ({'target_windows':[[0,3]]},{'interrupt_windows':[[3,3600]]}):
                with self.subTest(op=op,gate=gate):
                    r=self.calculate(scenario(op,number,timing={'windup_frames':0,'recovery_frames':0,**gate}))
                    s=r['estimate']['skill']
                    self.assertEqual(r['total_damage'],expected)
                    self.assertEqual(s['window_damage'],expected)
                    self.assertEqual(s['window_seconds'],10)
                    self.assertIsNone(s['duration_seconds'])
                    self.assertIsNone(s['total_damage'])
                    self.assertIsNone(s['phase_damage'])
                    for key in ('cycle_seconds','cycle_damage','cycle_dps','cycle_healing','cycle_hps'):
                        self.assertIsNone(s[key])
                    if op=='kaltsit':
                        self.assertEqual(s['window_healing'],15300)
                        self.assertIsNone(s['total_healing'])
                        self.assertIsNone(s['phase_healing'])
                    else:self.assertEqual(s['total_healing'],0)

    def test_positive_lifetime_cancels_projectiles_without_claiming_ammo_exhaustion(self):
        for op,number,expected in (('mechanist',1,5500),('kaltsit',2,15750)):
            with self.subTest(op=op):
                r=self.calculate(scenario(op,number,timing={'windup_frames':0,'recovery_frames':0,
                    'target_disappears_seconds':3}))
                s=r['estimate']['skill']
                self.assertEqual(r['total_damage'],expected)
                self.assertIsNone(s['duration_seconds'])
                self.assertIsNone(s['total_damage'])
                self.assertIsNone(s['cycle_seconds'])
                self.assertEqual(len(r['timing']['streams'][0]['release_frames']),2)

    def test_complete_release_can_have_a_short_observation_and_late_impacts(self):
        for op,number,full,window in (('mechanist',1,16500,16500),('kaltsit',2,78750,31500)):
            with self.subTest(op=op):
                r=self.calculate(scenario(op,number))
                s=r['estimate']['skill']
                self.assertEqual(r['total_damage'],window)
                self.assertEqual(s['total_damage'],full)
                self.assertIsNotNone(s['duration_seconds'])
                self.assertEqual(s['window_seconds'],10)
                if op=='mechanist':self.assertEqual(s['duration_seconds'],175/30)
                else:self.assertEqual(s['duration_seconds'],775/30)

    def test_delayed_last_hit_does_not_prevent_a_genuinely_finished_cast(self):
        for op,number,full in (('mechanist',1,16500),('kaltsit',2,78750)):
            with self.subTest(op=op):
                r=self.calculate(scenario(op,number,timing={'windup_frames':0,'recovery_frames':0,
                    'projectile_travel_seconds':100}))
                s=r['estimate']['skill']
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(s['total_damage'],full)
                self.assertIsNotNone(s['duration_seconds'])
                self.assertEqual(s['phase_damage'],0)

    def test_empty_source_preserves_known_zero_and_existing_unknown_end(self):
        for op,number in (('mechanist',1),('kaltsit',2)):
            for mode in ('frames','continuous'):
                with self.subTest(op=op,mode=mode):
                    r=self.calculate(scenario(op,number,timing_mode=mode,healing_targets=0,
                        timing={'windup_frames':0,'recovery_frames':0,'target_windows':[]}))
                    s=r['estimate']['skill']
                    self.assertEqual(r['total_damage'],0)
                    self.assertEqual(s['total_damage'],0)
                    self.assertEqual(s['total_healing'],0)
                    self.assertIsNone(s['duration_seconds'])
                    self.assertIsNone(s['cycle_seconds'])

    def test_partial_medical_no_recipients_keeps_known_zero_healing(self):
        r=self.calculate(scenario('kaltsit',2,healing_targets=0,
            timing={'windup_frames':0,'recovery_frames':0,'target_windows':[[0,3]]}))
        s=r['estimate']['skill']
        self.assertIsNone(s['total_damage'])
        self.assertEqual(s['total_healing'],0)
        self.assertEqual(s['window_healing'],0)

    def test_continuous_and_complete_frame_controls_keep_existing_supported_totals(self):
        for mode in ('frames','continuous'):
            for op,number,full in (('mechanist',1,16500),('kaltsit',2,78750)):
                with self.subTest(op=op,mode=mode):
                    r=self.calculate(scenario(op,number,timing_mode=mode))
                    self.assertEqual(r['estimate']['skill']['total_damage'],full)
                    self.assertIsNotNone(r['estimate']['skill']['duration_seconds'])

    def test_three_public_formatters_preserve_window_and_unknown_full_cast(self):
        r=self.calculate(scenario(timing={'windup_frames':0,'recovery_frames':0,
            'target_windows':[[0,3]]}))
        prior=copy.deepcopy(r)
        texts=(format_estimate(r),format_report(r),format_report(r,technical=True))
        self.assertEqual(r,prior)
        self.assertEqual(texts[0],texts[1])
        for text in texts:
            self.assertIn('未知',text)
            self.assertIn('11,000',text)

    def test_empty_enemy_with_friends_can_really_finish_its_medical_ammo(self):
        for mode,window in (('frames',30600),('continuous',22950)):
            with self.subTest(mode=mode):
                r=self.calculate(scenario('kaltsit',2,timing_mode=mode,healing_targets=2,
                    timing={'windup_frames':0,'recovery_frames':0,'target_windows':[]}))
                s=r['estimate']['skill']
                self.assertEqual(r['total_damage'],0)
                self.assertEqual(s['total_damage'],0)
                self.assertEqual(s['total_healing'],76500)
                self.assertEqual(s['window_healing'],window)
                self.assertIsNotNone(s['duration_seconds'])
