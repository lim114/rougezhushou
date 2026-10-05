from tests.offline_scope_retirement import historical_combat_test
"""Public SP-event scenarios; no live combat input or private state mutation."""
import copy
import math
import unittest

from rouge.damage import calculate_damage
from rouge.reporting import format_report

TANK = 'rogue_6_from_relic_4'
TANK_RELIC = 'rogue_6_relic_assign_4'
BLOOM = 'rogue_6_relic_legacy_118'
COOKIE = 'rogue_6_from_relic_15'


def events(kind, times):
    return [{'at_seconds': t, 'type': kind} for t in times]


def scenario(op='mechanist', skill=3, initial=(), cycle=(), **extra):
    return {'operator': op, 'skill': skill, 'char_buff_ids': [TANK],
            'timing': {'sp_events': {'initial': list(initial), 'cycle': list(cycle)}}, **extra}


@historical_combat_test
class ReceivedSP026Tests(unittest.TestCase):
    def test_tank_training_merges_attack_events_with_natural_sp(self):
        args = scenario(initial=events('attack', [1, 2, 3]), cycle=events('attack', [41, 42, 43]))
        saved = copy.deepcopy(args)
        result = calculate_damage(args)
        skill = result['estimate']['skill']
        self.assertEqual(args, saved)
        self.assertEqual(skill['initial_seconds'], 4)
        self.assertEqual(skill['recharge_seconds'], 29)
        self.assertEqual(skill['cycle_seconds'], 69)
        self.assertEqual(skill['duration_seconds'], 40)
        self.assertTrue(result['relic_resolution']['complete'])
        self.assertEqual(result['estimate']['sp_events']['initial']['credited_received_events'], 3)
        self.assertEqual(result['total_damage'], calculate_damage({'operator': 'mechanist', 'skill': 3})['total_damage'])

    def test_possession_does_not_bind_and_duplicates_do_not_double_grant(self):
        plain = calculate_damage({'operator': 'mechanist', 'skill': 3})
        held = calculate_damage({'operator': 'mechanist', 'skill': 3, 'relic_ids': [TANK_RELIC]})
        self.assertEqual(held['estimate']['skill'], plain['estimate']['skill'])
        self.assertFalse(held['relic_resolution']['complete'])
        args = scenario(initial=events('attack', [1, 2, 3]))
        one = calculate_damage(args)
        two = calculate_damage({**args, 'char_buff_ids': [TANK, TANK]})
        self.assertEqual(one['estimate']['skill'], two['estimate']['skill'])
        with self.assertRaises(ValueError):
            calculate_damage({**args, 'operator': 'char_151_myrtle'})

    def test_missing_phase_is_unknown_and_empty_phase_is_confirmed_no_hits(self):
        missing = calculate_damage({'operator': 'mechanist', 'skill': 3, 'char_buff_ids': [TANK]})
        self.assertIsNone(missing['estimate']['skill']['initial_seconds'])
        self.assertIsNone(missing['estimate']['skill']['cycle_seconds'])
        record = missing['relic_resolution']['records'][0]
        self.assertIn('timing.sp_events.initial', record['missing_conditions'])
        self.assertIn('timing.sp_events.cycle', record['missing_conditions'])
        empty = calculate_damage(scenario())
        self.assertEqual(empty['estimate']['skill']['initial_seconds'], 10)
        self.assertEqual(empty['estimate']['skill']['recharge_seconds'], 35)
        self.assertTrue(empty['relic_resolution']['complete'])
        separate = calculate_damage({**scenario(), 'timing': {'sp_events': {'initial': events('attack', [1, 2, 3])}}})
        self.assertEqual(separate['estimate']['skill']['initial_seconds'], 4)
        self.assertIsNone(separate['estimate']['skill']['recharge_seconds'])

    def test_attack_damage_and_elemental_loss_are_separate_callback_types(self):
        tank = calculate_damage(scenario(initial=events('damage', [1] * 5)))
        self.assertEqual(tank['estimate']['skill']['initial_seconds'], 10)
        for kind, expected in (('attack', 10), ('damage', 5), ('elemental_loss', 5)):
            result = calculate_damage(scenario(initial=events(kind, [1] * 5), char_buff_ids=[], relic_ids=[BLOOM]))
            self.assertEqual(result['estimate']['skill']['initial_seconds'], expected)
        both = calculate_damage(scenario(initial=events('damage', [1] * 5) + events('elemental_loss', [1] * 5),
                                        char_buff_ids=[], relic_ids=[BLOOM, BLOOM]))
        self.assertEqual(both['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertEqual(both['estimate']['sp_events']['initial']['credited_received_events'], 9)

    def test_same_frame_separate_hits_are_not_deduplicated(self):
        one = calculate_damage(scenario(initial=events('attack', [1])))
        five = calculate_damage(scenario(initial=events('attack', [1] * 5)))
        self.assertEqual(one['estimate']['skill']['initial_seconds'], 8)
        self.assertEqual(five['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertLessEqual(five['estimate']['sp_events']['initial']['credited_received_sp'], 10)

    def test_skill_and_extra_lockout_discard_events_and_never_bank_sp(self):
        args = scenario(cycle=events('attack', [1, 39.9, 40, 41, 41.9]))
        args['timing']['sp_lockout_extra_seconds'] = 2
        result = calculate_damage(args)
        skill = result['estimate']['skill']
        self.assertEqual(skill['recharge_seconds'], 37)
        self.assertEqual(result['estimate']['sp_events']['cycle']['ignored_blocked'], 5)
        at_boundary = copy.deepcopy(args)
        at_boundary['timing']['sp_events']['cycle'] = events('attack', [42] * 20)
        skill = calculate_damage(at_boundary)['estimate']['skill']
        self.assertAlmostEqual(skill['recharge_seconds'], 61 / 30)
        self.assertAlmostEqual(skill['cycle_seconds'], 40 + 61 / 30)

    def test_attack_recovery_can_charge_from_incoming_events_without_outgoing_attacks(self):
        result = calculate_damage(scenario(skill=1, initial=events('attack', [1] * 4), continuous_attacks=False))
        self.assertEqual(result['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertIsNone(result['estimate']['skill']['sp_recovery_per_second'])

    def test_native_defensive_recovery_adds_once_and_does_not_require_unused_cycle(self):
        result = calculate_damage({'operator': 'char_1044_hsgma2', 'skill': 1, 'char_buff_ids': [TANK],
            'timing': {'sp_events': {'initial': events('attack', [1] * 5)}}})
        self.assertEqual(result['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
        self.assertNotIn('cycle', result['estimate']['sp_events'])
        self.assertTrue(result['relic_resolution']['complete'])
        with self.assertRaisesRegex(ValueError, 'incoming_attack_interval'):
            calculate_damage({'operator': 'char_1044_hsgma2', 'skill': 1, 'char_buff_ids': [TANK],
                'incoming_attack_interval': 2, 'timing': {'sp_events': {'initial': events('attack', [1] * 5)}}})

    def test_next_attack_waits_for_legal_slot_and_empty_targets_cannot_cast(self):
        args = scenario('char_133_mm', 1, initial=events('damage', [.1] * 20),
                        char_buff_ids=[], relic_ids=[BLOOM])
        args['timing'].update(windup_frames=6, recovery_frames=9)
        result = calculate_damage(args)
        self.assertGreater(result['estimate']['skill']['initial_seconds'], 4 / 30)
        args['timing']['initial_target_windows'] = []
        result = calculate_damage(args)
        self.assertIsNone(result['estimate']['skill']['initial_seconds'])

    def test_display_window_does_not_change_full_cycle_or_event_origin(self):
        args = scenario(initial=events('attack', [1, 2, 3]), cycle=events('attack', [41, 42, 43]))
        full = calculate_damage(args)
        short = calculate_damage({**args, 'window_seconds': 2})
        for key in ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps'):
            self.assertEqual(full['estimate']['skill'][key], short['estimate']['skill'][key])
        self.assertEqual(short['estimate']['sp_events']['cycle']['origin_seconds'], 40)

    def test_natural_sp_cookie_and_talent_attack_sp_are_not_lost(self):
        base = scenario('char_151_myrtle', 1, initial=events('damage', [1, 2]),
                        char_buff_ids=[COOKIE], relic_ids=[BLOOM])
        result = calculate_damage(base)
        self.assertAlmostEqual(result['estimate']['skill']['sp_recovery_per_second'], 1.8)
        self.assertLess(result['estimate']['skill']['initial_seconds'], 5)
        empty = scenario('char_002_amiya', 1, char_buff_ids=[], relic_ids=[BLOOM])
        reference = calculate_damage({'operator': 'char_002_amiya', 'skill': 1})
        actual = calculate_damage(empty)
        for key in ('initial_seconds', 'recharge_seconds', 'cycle_seconds'):
            self.assertEqual(reference['estimate']['skill'][key], actual['estimate']['skill'][key])

    def test_amiya_stun_stops_attack_sp_but_not_natural_recovery(self):
        for mode in ('frames','continuous'):
            args=scenario('char_002_amiya',2,char_buff_ids=[],relic_ids=[BLOOM],timing_mode=mode)
            reference=calculate_damage({'operator':'char_002_amiya','skill':2,'timing_mode':mode})
            result=calculate_damage(args)
            for key in ('initial_seconds','recharge_seconds','cycle_seconds'):
                self.assertAlmostEqual(result['estimate']['skill'][key],reference['estimate']['skill'][key])

    def test_already_full_initial_sp_needs_no_extra_event_table(self):
        result=calculate_damage({'operator':'char_1048_orchd2','skill':1,'relic_ids':[BLOOM]})
        self.assertEqual(result['estimate']['skill']['initial_seconds'],0)
        self.assertEqual(result['estimate']['sp_events']['initial']['status'],'not_needed')
        self.assertNotIn('timing.sp_events.initial',result['relic_resolution']['records'][0]['missing_conditions'])

    def test_end_sp_refund_and_extra_lockout_are_counted_once(self):
        from rouge.relics import mechanics
        end_id=next(rid for rid,data in mechanics()['relics'].items() if any(e['kind']=='end_sp' for e in data['effects']))
        args=scenario(initial=[],cycle=[],char_buff_ids=[TANK],relic_ids=[end_id])
        args['timing']['sp_lockout_extra_seconds']=2
        actual=calculate_damage(args)
        reference=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':[end_id],
            'timing':{'sp_lockout_extra_seconds':2}})
        for key in ('initial_seconds','recharge_seconds','cycle_seconds'):
            self.assertEqual(actual['estimate']['skill'][key],reference['estimate']['skill'][key])

    def test_no_natural_recovery_uses_finite_events_without_inventing_future_hits(self):
        args=scenario(skill=1,initial=events('attack',[1,2,3,4]),cycle=[],continuous_attacks=False)
        actual=calculate_damage(args)
        self.assertEqual(actual['estimate']['skill']['initial_seconds'],121/30)
        self.assertIsNone(actual['estimate']['skill']['recharge_seconds'])
        self.assertIsNone(actual['estimate']['skill']['cycle_seconds'])

    def test_received_callback_and_native_attack_sp_use_independent_axes(self):
        args=scenario(skill=1,initial=events('attack',[1,2,3]),cycle=[])
        args['timing'].update(initial_movement_windows=[[0,10]],windup_frames=6,recovery_frames=9)
        actual=calculate_damage(args)
        self.assertGreater(actual['estimate']['skill']['initial_seconds'],10)
        self.assertLess(actual['estimate']['skill']['initial_seconds'],12)
        self.assertEqual(actual['estimate']['sp_events']['initial']['credited_received_events'],3)

    def test_wine_phase_still_uses_discrete_envelope(self):
        args = scenario(skill=1, initial=events('attack', [.2]), continuous_attacks=False,
                        relic_ids=['rogue_6_relic_legacy_97'])
        result = calculate_damage(args)
        self.assertAlmostEqual(result['estimate']['skill']['initial_seconds'], 7 / 30)
        self.assertIn('recharge_seconds_range', result['estimate']['skill'])
        self.assertIn('相位范围', format_report(result))
        self.assertFalse(result['relic_resolution']['phase_estimate']['verified_phase'])

    def test_empty_event_wine_stays_on_existing_discrete_clock_in_both_modes(self):
        for mode in ('frames','continuous'):
            args={'operator':'mechanist','skill':1,'continuous_attacks':False,
                  'timing_mode':mode,'relic_ids':['rogue_6_relic_legacy_97']}
            before=calculate_damage(args)
            after=calculate_damage({**args,'char_buff_ids':[TANK],
                'timing':{'sp_events':{'initial':[],'cycle':[]}}})
            for key in ('initial_seconds_range','recharge_seconds_range','cycle_seconds_range'):
                self.assertEqual(before['estimate']['skill'][key],after['estimate']['skill'][key])

    def test_only_applicable_actors_get_the_incoming_sp_report(self):
        result = calculate_damage(scenario())
        self.assertIn('received_sp', [s['id'] for s in result['report']['sections']])
        plain = calculate_damage({'operator': 'mechanist', 'skill': 3})
        held = calculate_damage({'operator': 'mechanist', 'skill': 3, 'relic_ids': [TANK_RELIC]})
        for r in (plain, held):
            self.assertNotIn('received_sp', [s['id'] for s in r['report']['sections']])
        token = calculate_damage(scenario('char_110_deepcl', 1, char_buff_ids=[], relic_ids=[BLOOM]))
        self.assertFalse(token['relic_resolution']['token_effects'])
        self.assertFalse(any(r.get('token_only') for r in token['relic_resolution']['rules']))

    def test_passive_and_deployment_skills_have_no_event_fields_or_missing_conditions(self):
        for op,number in (('char_1029_yato2',1),('char_4087_ines',3),('char_4107_vrdant',1),('char_1015_aglna2',1)):
            result=calculate_damage({'operator':op,'skill':number,'relic_ids':[BLOOM]})
            self.assertNotIn('sp_events',result['estimate'])
            self.assertNotIn('received_sp',[s['id'] for s in result['report']['sections']])
            self.assertIn(BLOOM,result['relic_resolution']['inapplicable'])
            self.assertTrue(result['relic_resolution']['complete'])

    def test_invalid_tables_are_rejected_instead_of_ignored(self):
        for value in (None, [], {'init': []}, {'initial': None},
                      {'initial': [{'at_seconds': 1, 'type': 'heal'}]},
                      {'initial': [{'at_seconds': 1, 'type': 'attack', 'count': 5}]},
                      {'initial': events('attack', [True])}, {'initial': events('attack', [-1])},
                      {'initial': events('attack', ['1'])},
                      {'initial': events('attack', [math.nan])}, {'initial': events('attack', [math.inf])},
                      {'initial': events('attack', [3601])}, {'initial': events('attack', [1] * 1001)}):
            with self.subTest(value=str(value)[:70]), self.assertRaises(ValueError):
                calculate_damage({**scenario(), 'timing': {'sp_events': value}})


if __name__ == '__main__':
    unittest.main()
