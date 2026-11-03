import unittest
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate


class WineTimingTests(unittest.TestCase):
    def test_verified_deployment_clock_is_discrete_not_average_sp_or_unknown_phase(self):
        result=calculate_damage({'operator':'mechanist','skill':1,
            'relic_ids':['rogue_6_relic_legacy_97'],
            'timing':{'initial_target_windows':[]}})
        skill=result['estimate']['skill']
        # Native waitFirst=true: two 1-SP pulses at deployment1.5 and3s.
        # Initial target_windows=[] explicitly excludes attack recovery.
        self.assertEqual(skill['initial_seconds'],3)
        for key in ('recharge_seconds','cycle_seconds','cycle_damage','cycle_dps'):
            self.assertGreater(skill[key],0)
            self.assertNotIn(key+'_range',skill)
        report=format_estimate(result)
        self.assertIn('预计回转：',report)
        self.assertNotIn('相位范围',report)
        cycle=next(m for s in result['report']['sections'] for m in s['metrics'] if m['key']=='cycle')
        self.assertEqual(cycle['value'],skill['cycle_seconds'])
        self.assertIsNone(cycle.get('range'))
        self.assertTrue(result['relic_resolution']['complete'])
        self.assertFalse(result['deployment_clock_reference']['live_state_verified'])

    def test_wine_charges_even_without_normal_attacks_and_respects_extra_lockout(self):
        scenario={'operator':'mechanist','skill':1,'continuous_attacks':False,
            'relic_ids':['rogue_6_relic_legacy_97']}
        base=calculate_damage(scenario)['estimate']['skill']
        blocked=calculate_damage({**scenario,'timing':{'sp_lockout_extra_seconds':2}})['estimate']['skill']
        # Initial3s + skill250/30s ends11+1/3s. Seven surviving pulses
        # at12..21s finish the cycle18s after its start. +2s lockout skips
        # the12s pulse and finishes at22.5s, a1.5s (not2s) cycle increase.
        self.assertAlmostEqual(base['recharge_seconds'],290/30)
        self.assertEqual(base['cycle_seconds'],18)
        self.assertEqual(base['cycle_damage'],base['total_damage'])
        self.assertAlmostEqual(blocked['cycle_seconds']-base['cycle_seconds'],1.5)
        self.assertEqual(blocked['cycle_damage'],blocked['total_damage'])

    def test_natural_recovery_has_no_wine_phase_range(self):
        result=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_97']})
        self.assertNotIn('cycle_seconds_range',result['estimate']['skill'])
        self.assertEqual(result['estimate']['skill']['recharge_seconds'],35)

    def test_defensive_recovery_can_charge_without_incoming_hits(self):
        result=calculate_damage({'operator':'char_1044_hsgma2','skill':1,
            'relic_ids':['rogue_6_relic_legacy_97']})
        skill=result['estimate']['skill']
        #15SP, +5 initial, ten pulses even without enemies attacking.
        self.assertEqual(skill['initial_seconds'],15)
        self.assertNotIn('initial_seconds_range',skill)
        self.assertIsNone(skill['cycle_seconds']) #infinite skill has no repeatable cycle
        self.assertNotIn('cycle_seconds_range',skill)

    def test_next_attack_waits_for_attack_slot_after_discrete_wine_credit(self):
        result=calculate_damage({'operator':'char_133_mm','skill':1,
            'relic_ids':['rogue_6_relic_legacy_97'],
            'timing':{'windup_frames':6,'recovery_frames':9}})
        skill=result['mei_s1_reference']['parameter_clock_reference']
        self.assertEqual(skill['initial_seconds'],0) #wine initialSP exceeds cost
        # Attack slots every28 frames, windup6. Normal credits on35/63,
        # wine on45; three SP are ready63 but next skill slot is84.
        self.assertAlmostEqual(skill['cycle_seconds'],84/30)
        self.assertAlmostEqual(skill['cycle_damage'],2324.04)
        self.assertAlmostEqual(skill['cycle_dps'],2324.04/(84/30))
        self.assertNotIn('cycle_seconds_range',skill)

    def test_wine_does_not_credit_attack_sp_from_movements_or_bank_blocked_ticks(self):
        s={'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_97'],
           'timing':{'initial_movement_windows':[[0,10]]}}
        skill=calculate_damage(s)['estimate']['skill']
        self.assertEqual(skill['initial_seconds'],3)
        full=calculate_damage({**s,'timing':{'sp_lockout_extra_seconds':10},'continuous_attacks':False})['estimate']['skill']
        # Block through21+1/3s discards intervening pulses. Seven fresh
        # pulses22.5..31.5s; original deployment phase never pauses/resets.
        self.assertAlmostEqual(full['recharge_seconds'],605/30)
        self.assertEqual(full['cycle_seconds'],28.5)
