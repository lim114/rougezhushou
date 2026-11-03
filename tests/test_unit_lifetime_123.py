"""Independent previews obey the existing numeric-zero target boundary."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.timing import AttackTimeline

OP='char_110_deepcl'
TOKEN='token_10001_deepcl_tentac'


def scenario(mode,lifetime,**options):
    return {'operator':OP,'skill':1,'window_seconds':10,'timing_mode':mode,
            'timing':{**options,'units':{TOKEN:{'target_disappears_seconds':lifetime}}}}


def tentacle(result):
    return next(c for c in result['components'] if c['name']=='触手')


class UnitLifetime123Tests(unittest.TestCase):
    def test_public_unit_zero_spellings_cancel_the_same_attacks_in_both_modes(self):
        for mode in ('frames','continuous'):
            expected=tentacle(calculate_damage(scenario(mode,0)))
            self.assertEqual(expected['total'],0)
            for lifetime in ('0','0.0','-0',' +0 ','0e10'):
                with self.subTest(mode=mode,lifetime=lifetime):
                    actual=calculate_damage(scenario(mode,lifetime))
                    self.assertEqual(tentacle(actual),expected)

    def test_explicit_unit_lifetime_overrides_owner_and_absence_inherits(self):
        for mode in ('frames','continuous'):
            cancelled=calculate_damage(scenario(mode,'0',target_disappears_seconds=10))
            self.assertEqual(tentacle(cancelled)['total'],0)
            alive=calculate_damage(scenario(mode,10,target_disappears_seconds=0))
            self.assertGreater(tentacle(alive)['total'],0)
            inherited=scenario(mode,10,target_disappears_seconds='0')
            inherited['timing']['units'][TOKEN].clear()
            self.assertEqual(tentacle(calculate_damage(inherited))['total'],0)

    def test_invalid_raw_unit_lifetimes_remain_errors(self):
        for mode in ('frames','continuous'):
            for lifetime in (True,False,None,-1,'-1','unknown','nan',float('inf')):
                with self.subTest(mode=mode,lifetime=lifetime):
                    with self.assertRaisesRegex(ValueError,'target_disappears_seconds'):
                        calculate_damage(scenario(mode,lifetime))

    def test_caller_preview_and_other_unit_remain_unchanged(self):
        value=scenario('continuous','-0',target_disappears_seconds=10)
        value['timing']['units']['unrelated']={'target_disappears_seconds':'unknown'}
        before=copy.deepcopy(value)
        calculate_damage(value)
        self.assertEqual(value,before)
        self.assertIsInstance(value['timing']['units'][TOKEN]['target_disappears_seconds'],str)

    def test_empty_enemy_declaration_does_not_cancel_friendly_stream(self):
        for mode in ('frames','continuous'):
            for lifetime in (0,'0'):
                timeline=AttackTimeline({'operator':OP,'skill':1,'timing_mode':mode,
                    'timing':{'target_disappears_seconds':lifetime}},target_scope='friendly')
                self.assertTrue(timeline.attacks(3,1)['times_seconds'])


if __name__=='__main__':unittest.main()
