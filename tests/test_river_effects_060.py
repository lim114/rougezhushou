"""Evidence and condition-boundary tests for the offline river reference."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

from rouge.river_effects import RiverInstance, reference


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.cache/research/p1-native-runtime-054'


class RiverEffectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract_bytes = (EVIDENCE / 'river-contract-055.json').read_bytes()
        cls.contract = json.loads(cls.contract_bytes)
        cls.oracle = json.loads((EVIDENCE / 'river-reference-oracle-055.json').read_bytes())

    def test_original_contract_and_four_parameter_branches(self):
        info = reference()
        self.assertEqual(hashlib.sha256(self.contract_bytes).hexdigest(),
                         info['source']['contract_sha256'])
        self.assertEqual(set(info['branches']), {'dark', 'fire', 'sanity', 'water'})
        for element, branch in info['branches'].items():
            with self.subTest(element=element):
                expected = self.contract['contracts'][element]
                self.assertEqual(branch['burst_damage_scale'], expected['burst_damage_scale'])
                if element in ('water', 'sanity'):
                    self.assertEqual(branch['raw_pulse_damage'], expected['extra_damage'])
                    self.assertEqual(branch['period_seconds'], expected['period_seconds'])
                for key, value in branch['modifiers'].items():
                    self.assertEqual(value, expected[key if key != 'enemy_def_addition' else 'def_addition'])

    def test_wait_first_and_derived_flags_match_complete_templates(self):
        for element in ('dark', 'fire', 'sanity', 'water'):
            with self.subTest(element=element):
                template = self.contract['templates']['rogue_6_ep_' + element + '_fix']
                creation = template['eventToActions']['ON_EP_BREAK_START'][1]
                branch = reference(element)['branches'][element]
                self.assertEqual(branch['derived'], creation['_isDerivedBuff'])
                if element in ('sanity', 'water'):
                    self.assertEqual(branch['wait_first'], creation['_buff']['waitFirstTriggerInterval'])

    def test_water_missing_scale_is_not_invented_amplification(self):
        original = self.contract['relic']['buffs'][3]['blackboard']
        self.assertNotIn('damage_scale', {item['key'] for item in original})
        self.assertEqual(reference('侵蚀')['branches']['water']['burst_damage_scale'], 1.)
        self.assertIn('默认', reference('water')['branches']['water']['scale_reason'])

    def test_water_tenth_pulse_included_and_attribute_survives(self):
        child = RiverInstance('water')
        events = [child.tick(Fraction(1, 30)) for _ in range(10)]
        self.assertTrue(all(event['raw_damage'] == 1500 for event in events))
        self.assertIsNone(child.tick(Fraction(1, 30)))
        state = child.snapshot()
        self.assertEqual(state['conditional_raw_damage_total'], 15000)
        self.assertEqual(state['remaining_trigger_count'], 0)
        self.assertFalse(state['finished'])
        self.assertEqual(state['active_modifiers'], {'enemy_def_addition': -120})
        self.assertIsNone(state['actual_hp_loss'])

    def test_long_dt_does_not_catch_up(self):
        child = RiverInstance('water')
        for second in range(1, 4):
            event = child.tick(1)
            self.assertEqual(event['relative_time_exact'], str(second))
        state = child.snapshot()
        self.assertEqual(state['trigger_attempts'], 3)
        self.assertEqual(state['remaining_trigger_count'], 7)
        self.assertEqual(state['known_raw_damage_subtotal'], 4500)

    def test_elemental_break_cleans_only_derived_children(self):
        for element in ('dark', 'fire', 'sanity', 'water'):
            with self.subTest(element=element):
                child = RiverInstance(element)
                child.break_finished()
                state = child.snapshot()
                self.assertEqual(state['finished'], element != 'water')
                if element != 'water':
                    self.assertEqual(state['active_modifiers'], {})
                    self.assertIsNone(child.tick(1, palsy=True))
                else:
                    self.assertEqual(state['active_modifiers'], {'enemy_def_addition': -120})
                    self.assertEqual(child.tick(1)['raw_damage'], 1500)

    def test_water_child_instances_are_independent(self):
        old = RiverInstance('water')
        for _ in range(10):
            old.tick(1)
        new = RiverInstance('water')
        self.assertEqual(new.snapshot()['remaining_trigger_count'], 10)
        self.assertEqual(sum(item.snapshot()['active_modifiers']['enemy_def_addition']
                             for item in (old, new)), -240)
        self.assertIsNone(old.tick(1))
        self.assertEqual(new.tick(1)['raw_damage'], 1500)

    def test_sanity_full_first_period_and_per_trigger_condition(self):
        child = RiverInstance('sanity')
        self.assertIsNone(child.tick(Fraction(1, 2), palsy=True))
        self.assertEqual(child.tick(Fraction(1, 2), palsy=True)['raw_damage'], 1000)
        rejected = child.tick(1, palsy=False)
        self.assertFalse(rejected['condition_confirmed'])
        self.assertEqual(rejected['raw_damage'], 0)
        self.assertEqual(rejected['event_kind'], 'conditional_trigger_attempt')
        unknown = child.tick(1)
        self.assertIsNone(unknown['condition_confirmed'])
        self.assertIsNone(unknown['raw_damage'])
        state = child.snapshot()
        self.assertEqual(state['trigger_attempts'], 3)
        self.assertEqual(state['known_raw_damage_subtotal'], 1000)
        self.assertIsNone(state['conditional_raw_damage_total'])
        self.assertFalse(state['condition_complete'])
        self.assertEqual(state['condition_scope'], 'recorded_trigger_attempts_only')

    def test_break_end_order_is_explicit(self):
        before = RiverInstance('sanity')
        after = RiverInstance('sanity')
        before.break_finished()
        self.assertIsNone(before.tick(1, palsy=True))
        self.assertEqual(after.tick(1, palsy=True)['raw_damage'], 1000)
        after.break_finished()
        self.assertIsNone(after.tick(1, palsy=True))

    def test_no_fabricated_deadline_epsilon(self):
        child = RiverInstance('sanity')
        self.assertIsNone(child.tick(Fraction(999999, 1000000), palsy=True))
        self.assertEqual(child.tick(Fraction(1, 1000000), palsy=True)['raw_damage'], 1000)
        self.assertFalse(child.snapshot()['native_fp_equivalence_proven'])

    def test_no_damage_pulses_for_dark_and_fire(self):
        for element in ('dark', 'fire'):
            with self.subTest(element=element):
                child = RiverInstance(element)
                self.assertIsNone(child.tick(3))
                self.assertEqual(child.snapshot()['trigger_attempts'], 0)

    def test_reference_and_returned_state_are_copy_safe(self):
        info = reference('water')
        info['branches']['water']['modifiers']['enemy_def_addition'] = -999
        info['source']['scope'] = 'changed'
        info['limitations'].clear()
        self.assertEqual(reference('water')['branches']['water']['modifiers']['enemy_def_addition'], -120)
        self.assertNotEqual(reference()['source']['scope'], 'changed')
        self.assertTrue(reference()['limitations'])
        child = RiverInstance('water')
        event = child.tick(1)
        event['raw_damage'] = -99
        state = child.snapshot()
        state['events'][0]['raw_damage'] = -99
        state['active_modifiers']['enemy_def_addition'] = 0
        self.assertEqual(child.snapshot()['events'][0]['raw_damage'], 1500)
        self.assertEqual(child.snapshot()['active_modifiers'], {'enemy_def_addition': -120})

    def test_invalid_inputs_do_not_advance_clock(self):
        child = RiverInstance('water')
        for value in (True, 0, -1, float('nan'), float('inf'), '1', None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    child.tick(value)
        with self.assertRaises(ValueError):
            child.tick(1, palsy=1)
        self.assertEqual(child.snapshot()['elapsed_exact'], '0')
        for value in ([], None, 'other'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    RiverInstance(value)

    def test_no_live_or_permanent_prediction_claim(self):
        info = reference()
        self.assertFalse(info['permanent_panel_effect'])
        self.assertFalse(info['live_combat_inputs_added'])
        self.assertFalse(info['native_fp_equivalence_proven'])
        self.assertFalse(info['absolute_creation_phase_known'])
        self.assertFalse(info['source']['current_hotfix_equivalence_proven'])
        self.assertTrue(info['pulse_damage_is_before_target_mitigation'])
        self.assertEqual(info['maximum_triggers_per_owner_tick'], 1)
        self.assertFalse(info['catch_up_loop'])

    def test_six_prior_conditional_fixtures_without_epsilon_boundary(self):
        cases = [
            ('water_30fps_20_owner_ticks', 'water', Fraction(1, 30), 20, True, None),
            ('water_1fps_no_catch_up', 'water', 1, 3, True, None),
            ('water_break_end_frame3', 'water', Fraction(1, 30), 20, True, 3),
            ('sanity_30fps_61_owner_ticks', 'sanity', Fraction(1, 30), 61, True, None),
            ('sanity_break_ends_before_tick60', 'sanity', Fraction(1, 30), 61, True, 60),
            ('sanity_without_palsy', 'sanity', Fraction(1, 30), 61, False, None),
        ]
        for name, element, dt, count, palsy, finish in cases:
            with self.subTest(name=name):
                child = RiverInstance(element)
                events = []
                for frame in range(1, count + 1):
                    if frame == finish:
                        child.break_finished()
                    event = child.tick(dt, palsy=palsy)
                    if event is not None and event['raw_damage']:
                        events.append({'frame': frame, 'at': event['relative_time_exact'], 'kind': element})
                state = child.snapshot()
                actual = {'events': events, 'pulses': len(events),
                          'remaining_count': state['remaining_trigger_count'],
                          'finished': state['finished'],
                          'def_addition': state['active_modifiers'].get('enemy_def_addition', 0)}
                self.assertEqual(actual, self.oracle['examples'][name])


if __name__ == '__main__':
    unittest.main()
