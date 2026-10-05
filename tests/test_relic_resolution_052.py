"""Explicit completeness evidence and confirmed zero counters.

These public fixtures never read the active run. Counter facts are from the
already pinned topic table; tests do not invent hidden trigger/lifecycle rules.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.damage import calculate_damage
from rouge.run_state import RunState


def scenario(**values):
    return {'operator': 'mechanist', 'skill': 3, 'enemy_defense': 100,
            'timing': {'windup_frames': 6, 'recovery_frames': 9}, **values}


def relic_record(result, identity):
    return next(row for row in result['relic_resolution']['records']
                if row['id'] == identity)


class RelicResolution052Tests(unittest.TestCase):
    def test_completeness_flag_requires_an_explicit_recipient_list(self):
        # Same contract as RunState.apply: a flag alone does not establish
        # that a current operator's list was read, including an empty list.
        for value in (False, True):
            with self.subTest(value=value):
                args = scenario(relic_ids=['rogue_6_relic_assign_9'],
                                char_buffs_complete=value)
                before = copy.deepcopy(args)
                with self.assertRaisesRegex(ValueError, 'ID'):
                    calculate_damage(args)
                self.assertEqual(args, before)

    def test_explicit_empty_list_keeps_complete_and_partial_distinct(self):
        parent = 'rogue_6_relic_assign_9'
        partial = calculate_damage(scenario(relic_ids=[parent], char_buff_ids=[],
                                           char_buffs_complete=False))
        complete = calculate_damage(scenario(relic_ids=[parent], char_buff_ids=[],
                                            char_buffs_complete=True))
        self.assertEqual(relic_record(partial, parent)['recipient_binding']['state'], 'unknown')
        self.assertFalse(partial['relic_resolution']['complete'])
        self.assertEqual(relic_record(complete, parent)['recipient_binding']['state'], 'absent')
        self.assertTrue(complete['relic_resolution']['complete'])

    def test_zero_persistent_counts_are_confirmed_values_not_missing(self):
        # Explicit non-hound target settles Hunt Mark's separate enemy
        # selector; zero RES-layer evidence alone cannot settle that branch.
        args = scenario(target_enemy={'stage_id': 'ro6_n_1_2',
                                      'enemy_id': 'enemy_1093_ccsbr', 'level': 0})
        plain = calculate_damage(args)
        # Independent zero oracles: +7 per five gold, +8% per part,
        # +5% per altar layer, +10 RES per probe layer.
        cases = (('rogue_6_relic_legacy_60', 'gold'),
                 ('rogue_6_relic_cargo_2', 'parts_count'),
                 ('rogue_6_relic_legacy_103', 'altar_stacks'),
                 ('rogue_6_relic_cargo_12', 'probe_stacks'))
        for rid, counter in cases:
            with self.subTest(counter=counter):
                actual = calculate_damage({**args, 'relic_ids': [rid], 'relic_context': {counter: 0}})
                self.assertEqual(actual['estimate']['base_stats'], plain['estimate']['base_stats'])
                self.assertTrue(actual['relic_resolution']['complete'])
                self.assertEqual(relic_record(actual, rid)['missing_conditions'], [])
                self.assertEqual(actual['relic_resolution']['context'][counter], 0)
                missing = calculate_damage({**args, 'relic_ids': [rid]})
                self.assertFalse(missing['relic_resolution']['complete'])
                self.assertIn(counter, relic_record(missing, rid)['missing_conditions'])

    def test_zero_random_recipient_excludes_an_unknown_layer_count(self):
        plain = calculate_damage(scenario())
        actual = calculate_damage(scenario(relic_ids=['rogue_6_relic_legacy_136'],
                                          relic_context={'mercenary_recipient': 0}))
        self.assertEqual(actual['estimate']['base_stats'], plain['estimate']['base_stats'])
        self.assertTrue(actual['relic_resolution']['complete'])
        self.assertFalse(actual['relic_resolution']['records'][0]['applied'])
        self.assertFalse(actual['relic_resolution']['records'][0]['missing_conditions'])

    def test_slot_threshold_uses_capacity_minus_count_and_includes_zero(self):
        plain = calculate_damage(scenario())
        for empty in (0, 3, 4, 12):
            with self.subTest(empty=empty):
                actual = calculate_damage(scenario(relic_ids=['rogue_6_relic_cargo_3'],
                                                  relic_context={'empty_slots': empty}))
                expected = max(0, plain['deployment_cost'] - (6 if empty >= 4 else 0))
                self.assertEqual(actual['deployment_cost'], expected)
                self.assertTrue(actual['relic_resolution']['complete'])

    def test_resource_zero_survives_missing_pages_and_restart_in_same_run(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'run.json'
            run = RunState(file)
            start = run.state['started_at']
            run.apply({'resources': {'gold': {'value': 25, 'source': 'test'},
                                    'parts_count': {'value': 3, 'capacity': 12, 'source': 'test'}}}, start + 1)
            run.apply({'resources': {'gold': {'value': 0, 'source': 'test'},
                                    'parts_count': {'value': 0, 'capacity': 12, 'source': 'test'}}}, start + 2)
            run.apply({'resources': {}}, start + 3)
            restored = RunState(file)
            self.assertEqual(restored.state['id'], run.state['id'])
            self.assertEqual(restored.state['resources']['gold']['value'], 0)
            self.assertEqual(restored.state['resources']['parts_count']['value'], 0)
            self.assertEqual(restored.state['resources']['parts_count']['capacity'], 12)
            self.assertEqual(restored.state['resources']['gold']['captured_at'], start + 2)
            events = [row for row in restored.state['history'] if row['kind'] == 'resource_updated']
            self.assertEqual([(row['resource'], row['value']) for row in events],
                             [('gold', 25), ('parts_count', 3), ('gold', 0), ('parts_count', 0)])

    def test_absent_recipient_does_not_suppress_a_distinct_confirmed_buff(self):
        parent = 'rogue_6_relic_assign_9'
        buff = 'rogue_6_from_relic_12'
        expected = calculate_damage(scenario(char_buff_ids=[buff]))
        actual = calculate_damage(scenario(relic_ids=[parent], char_buff_ids=[buff],
                                          char_buffs_complete=True))
        self.assertEqual(actual['estimate']['base_stats'], expected['estimate']['base_stats'])
        self.assertEqual(actual['estimate']['skill'], expected['estimate']['skill'])
        self.assertEqual(relic_record(actual, parent)['status'], 'inapplicable')
        self.assertTrue(relic_record(actual, buff)['applied'])


if __name__ == '__main__':
    unittest.main()
