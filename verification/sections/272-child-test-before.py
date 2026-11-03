"""Source-bound recovery timer over public, independently declared reads.

Literal vectors and distinct branch counterexamples qualify the model. No
game clock, real attribute acquisition or final HP is used as an oracle.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import regeneration_clock as module

ROOT = Path(__file__).resolve().parents[1]
Q = 4294967296


def snapshot(flat, *, attributes=True, normal=True, max_hp=1000 * Q, ratio=0):
    return {'attributes_exist': attributes, 'reads_return_normally': normal,
            'flat_raw': flat, 'max_hp_raw': max_hp, 'ratio_raw': ratio}


def update(identity='update', *, delta=0, reads=(), normals=None):
    return {'id': identity, 'kind': 'update', 'delta_raw': delta,
            'hp_reads_raw': list(reads),
            'hp_access_returns_normally': [True] * len(reads) if normals is None else list(normals)}


def reconfigure(identity='reconfigure', *, first=None, second=None, dirty=13, reads=(), normals=None):
    return {'id': identity, 'kind': 'reconfigure', 'dirty_attribute': dirty,
            'can_recover_snapshot': first, 'period_snapshot': second,
            'hp_reads_raw': list(reads),
            'hp_access_returns_normally': [True] * len(reads) if normals is None else list(normals)}


def payload(*actions, period=Q, remaining=Q):
    return {'ordinary_native_path': True, 'precise_timer_identity': True,
            'no_intervening_timer_changes': True,
            'timer': {'exists': True, 'period_raw': period, 'remaining_raw': remaining},
            'actions': list(actions) or [update()]}


class RegenerationClockTests(unittest.TestCase):
    def test_public_gold_period_remaining_and_four_independent_setter_arguments(self):
        data = module.public_example(); before = deepcopy(data)
        result = module.regeneration_clock_reference(data)
        self.assertTrue(result['source_valid']); self.assertTrue(result['declared_chain_complete'])
        self.assertEqual(result['final_period_raw_reference'], Q // 4)
        self.assertEqual(result['final_remaining_raw_reference'], Q // 4)
        self.assertEqual(result['declared_complete_request_count'], 4)
        requests = result['rows'][2]['drain']['requests']
        self.assertEqual([row['setter_value_argument_raw_reference'] for row in requests],
                         [901 * Q, 902 * Q, 903 * Q, 904 * Q])
        self.assertEqual(data, before)

    def test_each_hp_read_is_independent_not_the_previous_setter_result(self):
        data = module.public_example(); data['actions'][2]['hp_reads_raw'] = [900 * Q, 400 * Q, None, 1500 * Q]
        result = module.regeneration_clock_reference(data)
        requests = result['rows'][2]['drain']['requests']
        self.assertEqual([row['setter_value_argument_raw_reference'] for row in requests],
                         [901 * Q, 401 * Q, None, 1501 * Q])
        self.assertEqual(result['declared_complete_request_count'], 4)
        self.assertTrue(result['normal_return_reference'])
        self.assertTrue(all(row['actual_hp_after'] is None for row in requests))

    def test_period_validity_and_remaining_ready_use_different_strict_epsilon_gates(self):
        for period in (-Q, 0, 42949, 42950):
            result = module.regeneration_clock_reference(payload(update(delta=Q), period=period, remaining=0))
            with self.subTest(period=period):
                drain = result['rows'][0]['drain']
                self.assertFalse(drain['valid_reference']); self.assertFalse(drain['delta_applied_reference'])
                self.assertEqual(drain['requests'], []); self.assertEqual(result['final_remaining_raw_reference'], 0)
        result = module.regeneration_clock_reference(payload(update(), period=42951, remaining=42950))
        self.assertTrue(result['rows'][0]['drain']['valid_reference'])
        self.assertEqual(result['declared_complete_request_count'], 0)
        result = module.regeneration_clock_reference(payload(update(reads=[10 * Q]), remaining=42949))
        self.assertEqual(result['declared_complete_request_count'], 1)
        self.assertEqual(result['final_remaining_raw_reference'], Q + 42949)

    def test_negative_delta_delays_without_creating_recovery_and_wrap_still_advances_next_first(self):
        result = module.regeneration_clock_reference(payload(update(delta=-Q // 2), remaining=Q // 4))
        self.assertEqual(result['final_remaining_raw_reference'], 3 * Q // 4)
        self.assertEqual(result['declared_complete_request_count'], 0)
        data = payload(update(delta=-1), remaining=(1 << 63) - 1)
        result = module.regeneration_clock_reference(data); drain = result['rows'][0]['drain']
        self.assertEqual(drain['status'], 'missing_independent_hp_access')
        self.assertEqual(result['final_remaining_raw_reference'], -9223372032559808512)
        self.assertTrue(drain['next_advanced_without_qualified_hp_access_reference'])
        self.assertIsNone(result['declared_complete_request_count'])

    def test_catch_up_emits_multiple_requests_with_one_next_per_independent_read(self):
        result = module.regeneration_clock_reference(payload(update(delta=3 * Q, reads=[10 * Q, 40 * Q, 5 * Q])))
        drain = result['rows'][0]['drain']
        self.assertEqual([row['setter_value_argument_raw_reference'] for row in drain['requests']], [11 * Q, 41 * Q, 6 * Q])
        self.assertEqual([row['remaining_after_next_raw_reference'] for row in drain['requests']], [-Q, 0, Q])
        self.assertEqual(result['declared_complete_request_count'], 3)
        self.assertEqual(result['final_remaining_raw_reference'], Q)

    def test_reset_keep_past_subtracts_elapsed_amount_instead_of_scaling_ratio(self):
        data = payload(reconfigure(first=snapshot(2 * Q), second=snapshot(2 * Q)), remaining=3 * Q // 4)
        result = module.regeneration_clock_reference(data); row = result['rows'][0]
        self.assertEqual(row['new_period_raw_reference'], Q // 2)
        self.assertEqual(row['reset_keep_past_reference']['past_raw_reference'], Q // 4)
        self.assertEqual(result['final_remaining_raw_reference'], Q // 4)
        self.assertNotEqual(result['final_remaining_raw_reference'], 3 * Q // 8)

    def test_reset_keep_past_clamps_to_zero_then_next_update_can_drain_the_ready_timer(self):
        data = payload(reconfigure(first=snapshot(2 * Q), second=snapshot(2 * Q)),
                       update('next-read', reads=[80 * Q]), remaining=Q // 4)
        result = module.regeneration_clock_reference(data); reset = result['rows'][0]
        self.assertEqual(reset['reset_keep_past_reference']['unclamped_remaining_raw_reference'], -Q // 4)
        self.assertEqual(reset['remaining_after_raw_reference'], 0)
        self.assertEqual(result['rows'][1]['drain']['requests'][0]['setter_value_argument_raw_reference'], 81 * Q)
        self.assertEqual(result['final_remaining_raw_reference'], Q // 2)

    def test_first_false_gate_does_not_read_second_snapshot_and_marks_timer_invalid(self):
        for rate in (0, -Q, 42950):
            data = payload(reconfigure(first=snapshot(rate), second=snapshot(4 * Q, attributes=False)))
            with self.subTest(rate=rate):
                result = module.regeneration_clock_reference(data); row = result['rows'][0]
                self.assertFalse(row['can_recover_hp_reference'])
                self.assertIsNone(row['period_rate']); self.assertTrue(row['normal_return_reference'])
                self.assertEqual(result['final_period_raw_reference'], -Q)
                self.assertEqual(result['final_remaining_raw_reference'], -Q)

    def test_two_attribute_snapshots_can_have_different_rates_and_dirty_13_19_are_exact(self):
        for dirty in (13, 19):
            data = payload(reconfigure(first=snapshot(4 * Q), second=snapshot(2 * Q), dirty=dirty))
            with self.subTest(dirty=dirty):
                result = module.regeneration_clock_reference(data); row = result['rows'][0]
                self.assertEqual(row['can_recover']['rate_raw_reference'], 4 * Q)
                self.assertEqual(row['period_rate']['rate_raw_reference'], 2 * Q)
                self.assertEqual(result['final_period_raw_reference'], Q // 2)
                self.assertEqual(result['final_remaining_raw_reference'], Q // 2)

    def test_reciprocal_qualified_epsilon_domain_has_independent_literal_vectors(self):
        literals = {42950: 429493459224902, 42951: 429483459610010,
                    -42950: -429493459224902, 6 * Q: 715827883, 3 * Q: 1431655765}
        for rate, period in literals.items():
            data = payload(reconfigure(first=snapshot(Q), second=snapshot(rate)))
            with self.subTest(rate=rate):
                result = module.regeneration_clock_reference(data)
                self.assertEqual(result['rows'][0]['new_period_raw_reference'], period)
                self.assertEqual(result['final_period_raw_reference'], period)
        for rate, period, valid in ((99998 * Q, 42951, True), (99999 * Q, 42950, False), (100000 * Q, 42950, False)):
            data = payload(reconfigure(first=snapshot(Q), second=snapshot(rate)), update('check-valid'))
            result = module.regeneration_clock_reference(data)
            with self.subTest(rate=rate):
                self.assertEqual(result['final_period_raw_reference'], period)
                self.assertEqual(result['rows'][1]['drain']['valid_reference'], valid)

    def test_second_zero_negative_and_tiny_rates_do_not_borrow_the_first_positive_rate(self):
        for rate, period in ((0, -Q), (-2 * Q, -Q // 2)):
            result = module.regeneration_clock_reference(payload(reconfigure(first=snapshot(4 * Q), second=snapshot(rate))))
            with self.subTest(rate=rate):
                self.assertEqual(result['final_period_raw_reference'], period)
                self.assertEqual(result['final_remaining_raw_reference'], 0)
        for rate in (1, -1, 42949, -42949):
            result = module.regeneration_clock_reference(payload(reconfigure(first=snapshot(4 * Q), second=snapshot(rate))))
            with self.subTest(rate=rate):
                self.assertIsNone(result['normal_return_reference'])
                self.assertIsNone(result['final_period_raw_reference'])

    def test_attribute_rate_keeps_flat_and_max_hp_ratio_contributions_independent(self):
        first = snapshot(Q, max_hp=100 * Q, ratio=Q // 2)
        second = snapshot(0, max_hp=100 * Q, ratio=Q // 4)
        result = module.regeneration_clock_reference(payload(reconfigure(first=first, second=second)))
        row = result['rows'][0]
        self.assertEqual(row['can_recover']['ratio_part_raw_reference'], 50 * Q)
        self.assertEqual(row['can_recover']['rate_raw_reference'], 51 * Q)
        self.assertEqual(row['period_rate']['rate_raw_reference'], 25 * Q)
        self.assertEqual(row['new_period_raw_reference'], 171798692)

    def test_explicit_second_attribute_failure_retains_false_normal_and_pre_reset_timer_state(self):
        for second in (snapshot(2 * Q, attributes=False), snapshot(2 * Q, normal=False)):
            data = payload(reconfigure(first=snapshot(4 * Q), second=second), update('must-not-run'), remaining=Q // 2)
            result = module.regeneration_clock_reference(data); row = result['rows'][0]
            with self.subTest(second=second):
                self.assertFalse(row['period_rate']['normal_return_reference'])
                self.assertIs(row['normal_return_reference'], False)
                self.assertIs(result['normal_return_reference'], False)
                self.assertEqual(row['period_after_raw_reference'], Q)
                self.assertEqual(row['remaining_after_raw_reference'], Q // 2)
                self.assertIsNone(row['reset_keep_past_reference'])
                self.assertFalse(result['rows'][1]['called_reference'])

    def test_first_attribute_failure_or_unknown_blocks_period_read_without_invented_timer(self):
        for first, normal in ((snapshot(Q, attributes=False), False), (snapshot(Q, normal=False), False),
                              (snapshot(Q, attributes=None), None), (None, None)):
            data = payload(reconfigure(first=first, second=snapshot(2 * Q)), update('must-not-run'))
            with self.subTest(first=first):
                result = module.regeneration_clock_reference(data)
                self.assertIs(result['rows'][0]['normal_return_reference'], normal)
                self.assertIsNone(result['rows'][0]['period_rate'])
                self.assertFalse(result['rows'][1]['called_reference'])

    def test_failed_or_unknown_hp_access_stops_chain_but_does_not_undo_next(self):
        for normal in (False, None):
            data = payload(update(delta=Q, reads=[10 * Q], normals=[normal]), update('must-not-run'))
            with self.subTest(normal=normal):
                result = module.regeneration_clock_reference(data); row = result['rows'][0]
                self.assertEqual(row['drain']['requests'][0]['remaining_after_next_raw_reference'], Q)
                self.assertEqual(row['remaining_after_raw_reference'], Q)
                self.assertIs(row['normal_return_reference'], normal)
                self.assertFalse(result['rows'][1]['called_reference'])
                self.assertIsNone(result['declared_complete_request_count'])

    def test_missing_hp_read_after_an_already_advanced_next_is_not_an_inferred_previous_plus_one(self):
        data = payload(update(delta=2 * Q, reads=[10 * Q]), update('must-not-run'))
        result = module.regeneration_clock_reference(data); drain = result['rows'][0]['drain']
        self.assertEqual(len(drain['requests']), 1)
        self.assertEqual(drain['requests'][0]['setter_value_argument_raw_reference'], 11 * Q)
        self.assertEqual(result['final_remaining_raw_reference'], Q)
        self.assertTrue(drain['next_advanced_without_qualified_hp_access_reference'])
        self.assertIsNone(result['declared_complete_request_count']); self.assertFalse(result['rows'][1]['called_reference'])

    def test_front_gates_null_timer_and_unknown_validity_do_not_admit_updates(self):
        for key in ('ordinary_native_path', 'precise_timer_identity', 'no_intervening_timer_changes'):
            for value in (False, None):
                data = payload(); data[key] = value
                with self.subTest(key=key, value=value):
                    result = module.regeneration_clock_reference(data)
                    self.assertFalse(result['rows'][0]['called_reference']); self.assertIsNone(result['normal_return_reference'])
        for exists, normal in ((False, False), (None, None)):
            data = payload(); data['timer']['exists'] = exists
            result = module.regeneration_clock_reference(data)
            self.assertFalse(result['rows'][0]['called_reference']); self.assertIs(result['normal_return_reference'], normal)
        data = payload(); data['timer']['period_raw'] = None
        result = module.regeneration_clock_reference(data)
        self.assertIsNone(result['rows'][0]['drain']['valid_reference'])
        self.assertIsNone(result['declared_complete_request_count'])

    def test_schema_rejects_cross_branch_fields_bad_identity_and_mismatched_independent_reads(self):
        mutations = [lambda p: p.update(extra=1), lambda p: p.update(precise_timer_identity=1),
            lambda p: p['timer'].update(period_raw=True), lambda p: p['timer'].update(remaining_raw=1 << 63),
            lambda p: p['actions'][0].update(delta_raw=.5), lambda p: p['actions'][0].update(dirty_attribute=13),
            lambda p: p['actions'][0].update(hp_reads_raw=[1]),
            lambda p: p['actions'][0].update(hp_reads_raw=[1], hp_access_returns_normally=[1]),
            lambda p: p['actions'][0].update(id='\n'), lambda p: p['actions'].append(deepcopy(p['actions'][0])),
            lambda p: p.update(actions=[])]
        for index, mutate in enumerate(mutations):
            data = payload(); mutate(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.regeneration_clock_reference(data)
            self.assertEqual(data, before)
        for dirty in (0, 3, 12, 14, True):
            data = payload(reconfigure(first=snapshot(Q), second=snapshot(Q), dirty=dirty))
            with self.subTest(dirty=dirty), self.assertRaises(ValueError): module.regeneration_clock_reference(data)

    def test_source_hashes_native_bytes_metadata_spans_and_returned_copy_are_bound(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(hashlib.sha256((ROOT / module.SOURCE).read_bytes()).hexdigest(), module.SOURCE_SHA256)
        for name, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        native_path = next(name for name in source['source_artifacts_sha256'] if '272' in name and name.endswith('/native-proof.json'))
        metadata_path = next(name for name in source['source_artifacts_sha256'] if '272' in name and name.endswith('/metadata-proof.json'))
        native = json.loads((ROOT / native_path).read_text(encoding='utf8'))
        metadata = json.loads((ROOT / metadata_path).read_text(encoding='utf8'))
        self.assertEqual(len(native['methods']), 26)
        unique = {}
        for record in native['methods']:
            self.assertTrue(record['cfg_bounded_traversal_finished']); self.assertFalse(record['limits'])
            raw = b''.join(bytes.fromhex(row['bytes']) for row in record['instructions'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['reachable_bytes_sha256'])
            unique.update({row['address']: row for row in record['instructions']})
        self.assertEqual(len(unique), 1589)
        self.assertEqual(len(metadata['byte_spans']), 277)
        self.assertFalse(native['game_dll_executed']); self.assertFalse(native['process_memory_read'])
        source['source_artifacts_sha256'].clear()
        self.assertTrue(module.source_data()['source_artifacts_sha256'])
        with patch.object(module, 'source_data', return_value=None):
            result = module.regeneration_clock_reference(module.public_example())
        self.assertFalse(result['source_valid']); self.assertFalse(result['declared_chain_complete'])
        self.assertIsNone(result['declared_complete_request_count'])

    def test_requests_do_not_claim_real_clock_actual_hp_or_complete_effective_healing(self):
        result = module.regeneration_clock_reference(module.public_example())
        for field in ('actual_attribute_values', 'actual_clock', 'actual_hp_after', 'actual_complete_healing'):
            self.assertIsNone(result[field])
        self.assertFalse(result['events_scheduled']); self.assertFalse(result['hotfix_equivalence_proven'])
        self.assertTrue(all(row['actual_hp_after'] is None for action in result['rows']
                            if action['drain'] for row in action['drain']['requests']))


if __name__ == '__main__':
    unittest.main()
