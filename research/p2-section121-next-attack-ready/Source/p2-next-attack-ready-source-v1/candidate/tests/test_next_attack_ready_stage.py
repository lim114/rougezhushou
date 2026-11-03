"""Already-ready next-attack SP stage proposals; Root runtime still required."""
import copy
import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.timing import charge_seconds, periodic_charge_seconds
from rouge.sp_events import charge as event_charge


def scenario(**extra):
    s={'operator':'char_4204_mantra','skill':1,'elite':2,'level':1,'skill_rank':7,
       'trust':0,'potential':1,'base_attack':1000,'enemy_defense':0,'enemy_resistance':0,
       'timing_mode':'continuous','window_seconds':3,
       'timing':{'windup_frames':0,'recovery_frames':0},
       'relic_ids':['rogue_6_relic_legacy_98']}
    s.update(extra)
    return s


def direct(mode='continuous',**extra):
    s={'operator':'char_4204_mantra','skill':1,'timing_mode':mode,
       'timing':{'windup_frames':0,'recovery_frames':0},'_relic_rules':[]}
    s.update(extra)
    return s


class NextAttackReadyStageTests(unittest.TestCase):
    def test_two_initial_sp_items_do_not_invent_an_extra_continuous_attack_charge(self):
        for rid in ('rogue_6_relic_legacy_98','rogue_6_relic_legacy_99'):
            for mode in ('continuous','frames'):
                with self.subTest(rid=rid,mode=mode):
                    source=scenario(relic_ids=[rid],timing_mode=mode)
                    before=copy.deepcopy(source)
                    r=calculate_damage(source)
                    self.assertEqual(source,before)
                    self.assertEqual(r['estimate']['skill']['initial_seconds'],0)
                    self.assertEqual(r['estimate']['skill']['mode'],'next_attack')

    def test_public_initial_sp_changes_initial_readiness_without_changing_cast_or_recharge(self):
        keys=('duration_seconds','total_damage','phase_damage','recharge_seconds',
              'cycle_seconds','cycle_damage','cycle_dps','total_healing','cycle_healing','cycle_hps')
        for mode in ('continuous','frames'):
            base=calculate_damage(scenario(relic_ids=[],timing_mode=mode))
            ready=calculate_damage(scenario(timing_mode=mode))
            for key in keys:
                with self.subTest(mode=mode,key=key):
                    self.assertEqual(ready['estimate']['skill'][key],base['estimate']['skill'][key])
            self.assertEqual(ready['components'],base['components'])
            self.assertGreater(base['estimate']['skill']['initial_seconds'],0)

    def test_public_three_formatters_are_pure_and_show_zero_initial_time(self):
        r=calculate_damage(scenario())
        before=copy.deepcopy(r)
        texts=(format_estimate(r),format_report(r),format_report(r,technical=True))
        self.assertEqual(r,before)
        self.assertEqual(texts[0],texts[1])
        self.assertEqual(r['estimate']['skill']['initial_seconds'],0)
        for text in texts:self.assertIn('初动',text)

    def test_zero_required_sp_does_not_require_a_positive_future_increment(self):
        for mode in ('frames','continuous'):
            for initial in (False,True):
                with self.subTest(mode=mode,initial=initial):
                    s=direct(mode)
                    before=copy.deepcopy(s)
                    value=charge_seconds(s,0,0,1.6,100,initial=initial,wait_next_attack=True)
                    self.assertEqual(s,before)
                    self.assertEqual(value,0)
                    self.assertEqual(charge_seconds(s,1,0,1.6,100,initial=initial,wait_next_attack=True),None)

    def test_ready_sp_still_requires_a_legal_attack_slot_and_empty_source_stays_unknown(self):
        for mode in ('frames','continuous'):
            for initial in (False,True):
                for increment in (0,1):
                    with self.subTest(mode=mode,initial=initial,increment=increment):
                        s=direct(mode,timing={'windup_frames':0,'recovery_frames':0,
                            'target_windows':[],'initial_target_windows':[]})
                        self.assertIsNone(charge_seconds(s,0,increment,1.6,100,
                            initial=initial,wait_next_attack=True))

    def test_frame_ready_stage_uses_first_legal_start_without_sp_credit_or_windup(self):
        for increment in (0,1):
            s=direct('frames',timing={'windup_frames':6,'recovery_frames':0,
                'target_windows':[[5,6]],'initial_target_windows':[[5,6]]})
            self.assertEqual(charge_seconds(s,0,increment,1.6,100,
                initial=True,wait_next_attack=True),5)
            self.assertEqual(charge_seconds(s,0,increment,1.6,100,
                initial=False,offset=2,wait_next_attack=True),3)

    def test_zero_ready_stage_matches_existing_periodic_and_classified_charge_contract(self):
        skill={'sp_type':'INCREASE_WHEN_ATTACK','sp_increment':0}
        wine={'kind':'periodic_sp','value':1,'interval':3,'clock':'deployment'}
        for mode in ('frames','continuous'):
            for initial in (False,True):
                with self.subTest(mode=mode,initial=initial):
                    ordinary=direct(mode)
                    periodic=direct(mode,_relic_rules=[wine])
                    callback=direct(mode,timing={'windup_frames':0,'recovery_frames':0,
                        'sp_events':{'initial':[],'cycle':[]}})
                    a=charge_seconds(ordinary,0,0,1.6,100,initial=initial,wait_next_attack=True)
                    b=periodic_charge_seconds(periodic,0,0,1.6,100,
                        initial=initial,wait_next_attack=True)
                    c=event_charge(callback,skill,0,0,1.6,100,
                        initial=initial,wait_next_attack=True)['seconds']
                    self.assertEqual((a,b,c),(0,0,0))

    def test_positive_requirement_keeps_existing_continuous_charge_float_bits(self):
        for required,increment,interval in ((3,1,1.6),(13,2,.73),(5,3,1.41)):
            s=direct()
            count=__import__('math').ceil(required/increment)
            expected=count*interval
            actual=charge_seconds(s,required,increment,interval,100,initial=True,wait_next_attack=True)
            self.assertEqual(actual.hex(),expected.hex())

    def test_ready_next_attack_stage_does_not_change_non_next_attack_zero_charge(self):
        for mode in ('frames','continuous'):
            s=direct(mode,timing={'target_windows':[],'initial_target_windows':[]})
            self.assertEqual(charge_seconds(s,0,0,1.6,100,initial=True,wait_next_attack=False),0)
            self.assertEqual(charge_seconds(s,0,1,1.6,100,initial=False,wait_next_attack=False),0)
