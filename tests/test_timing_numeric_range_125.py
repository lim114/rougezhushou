"""Oversized integers are invalid previews, never uncaught float overflows."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.manual_scenario import parse_preview_object
from rouge.timing import finite,frame_time
from tests.test_unit_lifetime_123 import OP,TOKEN


class TimingNumericRange125Tests(unittest.TestCase):
    def test_oversized_JSON_integer_in_scalar_preview_is_a_labelled_input_error(self):
        for mode in ('frames','continuous'):
            for field in ('windup_frames','recovery_frames','start_delay_frames',
                          'post_skill_lock_frames','projectile_travel_seconds',
                          'sp_lockout_extra_seconds','target_disappears_seconds'):
                options=parse_preview_object('{"'+field+'":'+str(10**400)+'}','战斗时序情景')
                with self.subTest(mode=mode,field=field),self.assertRaisesRegex(ValueError,field):
                    calculate_damage({'operator':OP,'skill':1,'timing_mode':mode,'timing':options})

    def test_oversized_interval_endpoints_are_errors_in_each_window(self):
        for field in ('target_windows','movement_windows','interrupt_windows'):
            for pair in ((10**400,10**400+1),(0,10**400)):
                with self.subTest(field=field,pair=pair),self.assertRaisesRegex(ValueError,'时间'):
                    calculate_damage({'operator':OP,'skill':1,'timing':{field:[list(pair)]}})

    def test_oversized_initial_window_is_not_silently_ignored_when_used_for_charging(self):
        with self.assertRaisesRegex(ValueError,'时间'):
            calculate_damage({'operator':'mechanist','skill':1,
                'timing':{'initial_target_windows':[[0,10**400]]}})

    def test_unit_error_retains_caller_state(self):
        for mode in ('frames','continuous'):
            args={'operator':OP,'skill':1,'timing_mode':mode,
                  'timing':{'units':{TOKEN:{'target_disappears_seconds':10**400}}}}
            before=copy.deepcopy(args)
            with self.assertRaisesRegex(ValueError,'target_disappears_seconds'):
                calculate_damage(args)
            self.assertEqual(args,before)

    def test_finite_boundary_preserves_legal_values_and_rejects_out_of_range_values(self):
        self.assertEqual(finite(108000,'帧'),108000)
        self.assertEqual(frame_time(3600),108000)
        self.assertEqual(frame_time('0'),0)
        for invalid in (108001,10**400,-10**400,True,False,float('inf'),float('nan')):
            with self.subTest(value=invalid),self.assertRaisesRegex(ValueError,'帧'):
                finite(invalid,'帧')


if __name__=='__main__':unittest.main()
