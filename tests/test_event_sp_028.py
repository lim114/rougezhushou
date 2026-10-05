from tests.offline_scope_retirement import historical_combat_test
"""Own-unit outgoing callbacks, shared SP clock, and scoped hand synergy."""
import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from tests.test_received_sp_026 import BLOOM, TANK, events

HORN = 'rogue_6_relic_fight_5'
WAVE = 'rogue_6_relic_hand_5'
BOOK = 'rogue_6_relic_book_5'


def scenario(op='mechanist', skill=3, *, initial=(), cycle=(), ids=(HORN,), **extra):
    return {'operator': op, 'skill': skill, 'relic_ids': list(ids),
            'timing': {'sp_events': {'initial': list(initial), 'cycle': list(cycle)}}, **extra}


@historical_combat_test
class EventSP028Tests(unittest.TestCase):
    def test_horn_kill_updates_initial_recharge_and_cycle_not_per_cast_damage(self):
        args = scenario(initial=events('kill', [1, 2, 3]), cycle=events('kill', [41, 42, 43]))
        saved = copy.deepcopy(args)
        result = calculate_damage(args)
        plain = calculate_damage({'operator': 'mechanist', 'skill': 3})
        skill = result['estimate']['skill']
        self.assertEqual(args, saved)
        self.assertEqual((skill['initial_seconds'], skill['recharge_seconds'], skill['cycle_seconds']), (4, 29, 69))
        self.assertEqual(skill['total_damage'], plain['estimate']['skill']['total_damage'])
        self.assertNotEqual(skill['cycle_dps'], plain['estimate']['skill']['cycle_dps'])
        ref = result['estimate']['sp_events']['initial']
        self.assertEqual(ref['credited_by_type'], {'kill': {'events': 3, 'sp': 6}})
        self.assertEqual(ref['credited_received_events'], 0)
        self.assertEqual(ref['credited_received_sp'], 0)
        self.assertTrue(result['relic_resolution']['complete'])

    def test_kill_is_not_attack_dealt_damage_or_received_damage(self):
        for kind in ('attack', 'damage', 'elemental_loss', 'dealt_damage'):
            result = calculate_damage(scenario(initial=events(kind, [1] * 20)))
            self.assertEqual(result['estimate']['skill']['initial_seconds'], 10, kind)
            self.assertEqual(result['estimate']['sp_events']['initial']['credited_callback_sp'], 0)

    def test_wave_damage_callback_applies_to_both_supported_funnel_operators_all_skills(self):
        for op in ('char_328_cammou', 'char_1038_whitw2'):
            for number in range(1, len(catalog()['operators'][op]['skills']) + 1):
                args = scenario(op, number, ids=(WAVE,), initial=events('dealt_damage', [.1] * 30))
                result = calculate_damage(args)
                reference = calculate_damage(scenario(op, number, ids=(WAVE,)))
                self.assertLess(result['estimate']['skill']['initial_seconds'], reference['estimate']['skill']['initial_seconds'])
                self.assertEqual(result['estimate']['skill']['initial_seconds'], 4 / 30)
                self.assertTrue(result['relic_resolution']['complete'], (op, number))
                self.assertEqual(result['relic_resolution']['records'][0]['pending'], [])

    def test_wave_selector_does_not_apply_to_other_casters_or_other_professions(self):
        for op in ('char_002_amiya', 'mechanist', 'kaltsit', 'char_110_deepcl'):
            result = calculate_damage({'operator': op, 'skill': 1, 'relic_ids': [WAVE]})
            self.assertIn(WAVE, result['relic_resolution']['inapplicable'])
            self.assertTrue(result['relic_resolution']['complete'])
            self.assertNotIn('sp_events', result['estimate'])
            self.assertNotIn('event_sp', [s['id'] for s in result['report']['sections']])

    def test_wave_received_damage_and_kills_do_not_trigger_outgoing_damage_sp(self):
        for kind in ('attack', 'damage', 'elemental_loss', 'kill'):
            result = calculate_damage(scenario('char_328_cammou', 2, ids=(WAVE,), initial=events(kind, [1] * 30)))
            self.assertEqual(result['estimate']['skill']['initial_seconds'], 25)
            self.assertEqual(result['estimate']['sp_events']['initial']['credited_callback_sp'], 0)

    def test_wave_and_horn_distinct_callbacks_on_same_timestamp_share_one_clock(self):
        args = scenario('char_328_cammou', 2, ids=(WAVE, HORN),
            initial=events('dealt_damage', [1, 2, 3]) + events('kill', [1, 2, 3]))
        result = calculate_damage(args)
        self.assertEqual(result['estimate']['skill']['initial_seconds'], 13)
        ref = result['estimate']['sp_events']['initial']
        self.assertEqual(ref['credited_by_type']['kill'], {'events': 3, 'sp': 6})
        self.assertEqual(ref['credited_by_type']['dealt_damage'], {'events': 3, 'sp': 6})
        self.assertEqual(ref['credited_callback_sp'], 12)
        self.assertEqual(ref['credited_received_events'], 0)

    def test_same_frame_events_preserve_multiplicity_and_cap_usable_sp(self):
        one = calculate_damage(scenario(initial=events('kill', [1])))
        many = calculate_damage(scenario(initial=events('kill', [1] * 20)))
        self.assertEqual(one['estimate']['skill']['initial_seconds'], 8)
        self.assertEqual(many['estimate']['skill']['initial_seconds'], 31 / 30)
        ref = many['estimate']['sp_events']['initial']
        self.assertEqual(ref['credited_callback_events'], 5)
        self.assertLessEqual(ref['credited_callback_sp'], 10)

    def test_duplicate_relic_ids_do_not_grant_extra_callback_sp(self):
        args = scenario('char_328_cammou', 2, ids=(WAVE, HORN), initial=events('dealt_damage', [1, 2, 3]))
        one = calculate_damage(args)
        doubled = calculate_damage({**args, 'relic_ids': [WAVE, HORN, WAVE, HORN]})
        self.assertEqual(one['estimate']['skill'], doubled['estimate']['skill'])
        self.assertEqual(one['estimate']['sp_events'], doubled['estimate']['sp_events'])

    def test_missing_phase_unknown_and_explicit_empty_table_preserves_native_clock(self):
        for op, number, rid in (('mechanist', 3, HORN), ('char_328_cammou', 2, WAVE)):
            missing = calculate_damage({'operator': op, 'skill': number, 'relic_ids': [rid]})
            self.assertIsNone(missing['estimate']['skill']['initial_seconds'])
            self.assertIsNone(missing['estimate']['skill']['recharge_seconds'])
            self.assertIn('timing.sp_events.cycle', missing['relic_resolution']['records'][0]['missing_conditions'])
            empty = calculate_damage(scenario(op, number, ids=(rid,)))
            plain = calculate_damage({'operator': op, 'skill': number})
            for field in ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps'):
                self.assertEqual(empty['estimate']['skill'][field], plain['estimate']['skill'][field])
            self.assertTrue(empty['relic_resolution']['complete'])

    def test_skills_without_repeat_do_not_require_unused_cycle_phase(self):
        result = calculate_damage({'operator': 'char_1044_hsgma2', 'skill': 1, 'relic_ids': [HORN],
            'timing': {'sp_events': {'initial': events('kill', [1] * 8)}}})
        self.assertEqual(result['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertNotIn('cycle', result['estimate']['sp_events'])
        self.assertTrue(result['relic_resolution']['complete'])

    def test_skill_and_extra_lockout_drop_kills_without_banking(self):
        args = scenario(cycle=events('kill', [1, 39.9, 40, 41, 41.9]))
        args['timing']['sp_lockout_extra_seconds'] = 2
        result = calculate_damage(args)
        self.assertEqual(result['estimate']['skill']['recharge_seconds'], 37)
        self.assertEqual(result['estimate']['sp_events']['cycle']['ignored_blocked'], 5)
        args['timing']['sp_events']['cycle'] = events('kill', [42] * 20)
        result = calculate_damage(args)
        self.assertAlmostEqual(result['estimate']['skill']['recharge_seconds'], 61 / 30)

    def test_native_attack_recovery_uses_own_attack_clock_beside_kill_callbacks(self):
        args = scenario(skill=1, initial=events('kill', [1]), cycle=[])
        result = calculate_damage(args)
        plain = calculate_damage(scenario(skill=1))
        self.assertLess(result['estimate']['skill']['initial_seconds'], plain['estimate']['skill']['initial_seconds'])
        args['continuous_attacks'] = False
        finite = calculate_damage(args)
        self.assertIsNone(finite['estimate']['skill']['initial_seconds'])
        self.assertIsNone(finite['estimate']['skill']['recharge_seconds'])
        args['timing']['sp_events']['initial'] = events('kill', [1] * 4)
        self.assertEqual(calculate_damage(args)['estimate']['skill']['initial_seconds'], 31 / 30)

    def test_native_defensive_attack_and_kill_are_each_counted_once(self):
        args = scenario('char_1044_hsgma2', 1, initial=events('kill', [1] * 5) + events('attack', [1] * 5))
        result = calculate_damage(args)
        self.assertEqual(result['estimate']['skill']['initial_seconds'], 31 / 30)
        self.assertEqual(result['estimate']['sp_events']['initial']['credited_by_type'], {'kill': {'events': 5, 'sp': 10}})
        with self.assertRaisesRegex(ValueError, 'incoming_attack_interval'):
            calculate_damage({**args, 'incoming_attack_interval': 2})

    def test_incoming_and_outgoing_receipts_remain_separate(self):
        args = scenario(initial=events('kill', [1, 2]) + events('damage', [1, 2]) + events('attack', [1, 2]),
            ids=(HORN, BLOOM), char_buff_ids=[TANK])
        result = calculate_damage(args)
        ref = result['estimate']['sp_events']['initial']
        self.assertGreater(ref['credited_callback_events'], ref['credited_received_events'])
        self.assertEqual(set(ref['credited_by_type']), {'kill', 'attack', 'damage'})
        self.assertEqual(ref['credited_received_events'], 4)
        self.assertLessEqual(ref['credited_callback_sp'], 10)

    def test_caster_end_refund_remains_independent_and_wave_attack_stack_is_unknown(self):
        args = scenario('char_328_cammou', 2, ids=(WAVE, BOOK),
            cycle=events('dealt_damage', [31, 32, 33]), relic_context={'deployed_casters': 2})
        result = calculate_damage(args)
        skill = result['estimate']['skill']
        self.assertEqual(skill['recharge_seconds'], 33)
        self.assertEqual(skill['cycle_seconds'], 63)
        plain = calculate_damage({'operator': 'char_328_cammou', 'skill': 2})
        self.assertEqual(skill['skill_attack'], plain['estimate']['skill']['skill_attack'])
        self.assertEqual(skill['total_damage'], plain['estimate']['skill']['total_damage'])
        wave = next(r for r in result['relic_resolution']['records'] if r['id'] == WAVE)
        self.assertEqual(wave['status'], 'incomplete')
        self.assertTrue(any('攻击叠层' in p for p in wave['pending']))
        self.assertFalse(result['relic_resolution']['complete'])

    def test_wave_synergy_warning_hidden_for_other_subclasses_even_when_book_held(self):
        result = calculate_damage({'operator': 'char_002_amiya', 'skill': 1, 'relic_ids': [WAVE, BOOK],
            'relic_context': {'deployed_casters': 2}})
        wave = next(r for r in result['relic_resolution']['records'] if r['id'] == WAVE)
        self.assertEqual(wave['status'], 'inapplicable')
        self.assertEqual(wave['pending'], [])
        self.assertNotIn('sp_events', result['estimate'])

    def test_passive_deployment_skills_have_no_event_panel_or_requirements(self):
        for op, number in (('char_1029_yato2', 1), ('char_4087_ines', 3), ('char_4107_vrdant', 1), ('char_1015_aglna2', 1)):
            result = calculate_damage({'operator': op, 'skill': number, 'relic_ids': [HORN, WAVE]})
            self.assertNotIn('sp_events', result['estimate'])
            self.assertNotIn('event_sp', [s['id'] for s in result['report']['sections']])
            self.assertTrue(result['relic_resolution']['complete'])

    def test_no_token_callback_inheritance_and_report_only_applicable_types(self):
        result = calculate_damage(scenario('char_110_deepcl', 1))
        self.assertFalse(result['relic_resolution']['token_effects'])
        self.assertFalse(any(r.get('token_only') for r in result['relic_resolution']['rules']))
        section = next(s for s in result['report']['sections'] if s['id'] == 'event_sp')
        labels = ' '.join(m['label'] for m in section['metrics'])
        self.assertIn('本体击倒敌人', labels)
        self.assertNotIn('成功造成伤害', labels)
        wave = calculate_damage(scenario('char_328_cammou', 2, ids=(WAVE,)))
        labels = ' '.join(m['label'] for s in wave['report']['sections'] if s['id'] == 'event_sp' for m in s['metrics'])
        self.assertNotIn('击倒', labels)

    def test_display_window_preserves_full_cycle_and_origin(self):
        args = scenario('char_328_cammou', 2, ids=(WAVE,),
            initial=events('dealt_damage', [1, 2, 3]), cycle=events('dealt_damage', [31, 32, 33]))
        full = calculate_damage(args)
        short = calculate_damage({**args, 'window_seconds': 1})
        for field in ('initial_seconds', 'duration_seconds', 'recharge_seconds', 'cycle_seconds', 'cycle_dps'):
            self.assertEqual(full['estimate']['skill'][field], short['estimate']['skill'][field])
        self.assertEqual(short['estimate']['sp_events']['cycle']['origin_seconds'], 30)

    def test_continuous_mode_keeps_exact_callback_time_and_frame_mode_next_tick(self):
        args = scenario(initial=events('kill', [.01] * 5))
        frame = calculate_damage(args)
        continuous = calculate_damage({**args, 'timing_mode': 'continuous'})
        self.assertEqual(frame['estimate']['skill']['initial_seconds'], 2 / 30)
        self.assertEqual(continuous['estimate']['skill']['initial_seconds'], .01)

    def test_invalid_outgoing_table_not_silently_converted_to_success(self):
        for event in ({'at_seconds': 1, 'type': 'damage_dealt'},
                      {'at_seconds': 1, 'type': 'kill', 'owner': 'drone'},
                      {'at_seconds': True, 'type': 'dealt_damage'}):
            with self.assertRaises(ValueError):
                calculate_damage(scenario(initial=[event]))

    def test_horn_callbacks_can_share_existing_wine_phase_envelope(self):
        args = scenario(skill=1, ids=(HORN, 'rogue_6_relic_legacy_97'), continuous_attacks=False,
            initial=events('kill', [.2]), cycle=[])
        result = calculate_damage(args)
        self.assertAlmostEqual(result['estimate']['skill']['initial_seconds'], 7 / 30)
        self.assertIn('recharge_seconds_range', result['estimate']['skill'])
        self.assertFalse(result['relic_resolution']['phase_estimate']['verified_phase'])

    def test_raw_selectors_and_partial_status_preserved(self):
        horn = mechanics()['relics'][HORN]
        wave = mechanics()['relics'][WAVE]
        self.assertEqual(horn['status'], 'conditional')
        self.assertEqual(wave['status'], 'partial')
        self.assertEqual(horn['effects'][0]['value'], 2)
        self.assertEqual(wave['effects'][0]['value'], 2)
        self.assertEqual(set(wave['effects'][0]['subprofession'].split('|')), {'blastcaster', 'funnel', 'chain'})
        self.assertEqual(len(horn['effects'][0]['profession'].split('|')), 8)
        self.assertEqual(wave['pending_scopes'][0]['requires_relic_ids'], [BOOK])


if __name__ == '__main__':
    unittest.main()
