"""Independent SP-setter gate/clamp/opaque-copy and 274-link qualification.

Literal bounds and gate-order expectations come from the fixed native proof.
No encrypted bytes, decoded SP or game state are constructed as an oracle.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import sp_setter_reference as module
from rouge import sp_recovery_clock as clock_module

ROOT = Path(__file__).resolve().parents[1]
Q = 4294967296


def body(identity='write', *, mode='internal', value=5 * Q, force=False, alive=True,
         alive_normal=True, max_sp=10, max_normal=True, encoding_normal=True, copy_normal=True,
         target=True, native=True, virtual=True, value_source='independent'):
    return {'id': identity, 'mode': mode, 'ordinary_native_path': native,
            'bound_virtual_dispatch': virtual, 'target_exists': target, 'force': force,
            'value_source': value_source, 'value_raw': value,
            'alive_read': {'normal': alive_normal, 'value': alive},
            'max_sp_read': {'normal': max_normal, 'value': max_sp},
            'encoding_returns_normally': encoding_normal, 'copy_returns_normally': copy_normal}


def payload(*rows, bridge=None):
    return {'body_reads': list(rows) or [body()], 'clock_bridge': bridge}


def result_of(row):
    return module.sp_setter_reference(payload(row))['rows'][0]


def linked(*, phase='tick', body_row=None, action_index=0, same_target=True, unchanged=True):
    clock = clock_module.public_example()
    row = body('linked', mode='public', value=None, value_source='clock_request') if body_row is None else body_row
    return payload(row, bridge={'input': clock, 'links': [{
        'body_id': row['id'], 'action_id': clock['actions'][action_index]['id'], 'phase': phase,
        'same_target': same_target, 'no_intervening_value_change': unchanged}]})


class SpSetterReferenceTests(unittest.TestCase):
    def test_public_gold_caps9_to6_dead_public7_rejects_and_internal_force_negative_copies_zero(self):
        data = module.public_example(); before = deepcopy(data)
        result = module.sp_setter_reference(data)
        self.assertTrue(result['source_valid']); self.assertEqual(len(result['rows']), 3)
        first, second, third = result['rows']
        self.assertEqual(first['encoder_value_argument_raw_reference'], 25769803776)
        self.assertTrue(first['internal_bool_return_reference'])
        self.assertTrue(first['public_void_returns_normally_reference'])
        self.assertTrue(first['full_struct_copy_completed_reference'])
        self.assertEqual(first['struct_copy_bytes_reference'], 40)
        self.assertIs(second['internal_bool_return_reference'], False)
        self.assertTrue(second['public_void_returns_normally_reference'])
        self.assertFalse(second['encoder_called_reference']); self.assertFalse(second['copy_called_reference'])
        self.assertEqual(second['struct_copy_bytes_reference'], 0)
        self.assertEqual(third['encoder_value_argument_raw_reference'], 0)
        self.assertTrue(third['internal_bool_return_reference'])
        self.assertTrue(third['full_struct_copy_completed_reference'])
        self.assertEqual(result['known_full_struct_copies_count'], 2)
        self.assertEqual(result['declared_complete_struct_copy_count'], 2)
        clock_rows = result['clock_reference']['rows']
        self.assertEqual(clock_rows[0]['tick']['recovery']['setter_value_argument_raw_reference'], 38654705664)
        self.assertEqual(clock_rows[2]['recovery']['setter_value_argument_raw_reference'], 30064771072)
        self.assertEqual(data, before)

    def test_literal_low_equal_high_and_fractional_caps_use_no_epsilon(self):
        for value, expected in ((-Q, 0), (-1, 0), (0, 0), (1, 1), (42949, 42949),
                                (42950, 42950), (6 * Q - 1, 6 * Q - 1), (6 * Q, 6 * Q),
                                (6 * Q + 1, 6 * Q), (60 * Q, 6 * Q)):
            with self.subTest(value=value):
                row = result_of(body(value=value, max_sp=6))
                self.assertEqual(row['upper_raw_reference'], 25769803776)
                self.assertEqual(row['clamped_value_raw_reference'], expected)
                self.assertEqual(row['encoder_value_argument_raw_reference'], expected)
                self.assertTrue(row['normal_return_reference'])

    def test_int32_extremes_convert_exactly_and_reversed_nonpositive_upper_closes_zero(self):
        for max_sp, upper, expected in ((2147483647, 9223372032559808512, 9223372032559808512),
                                        (-2147483648, -9223372036854775808, 0), (-1, -Q, 0), (0, 0, 0)):
            with self.subTest(max_sp=max_sp):
                row = result_of(body(value=9223372036854775807, max_sp=max_sp))
                self.assertEqual(row['upper_raw_reference'], upper)
                self.assertEqual(row['encoder_value_argument_raw_reference'], expected)
                self.assertTrue(row['full_struct_copy_completed_reference'])

    def test_unknown_typed_value_with_nonpositive_max_and_unknown_upper_with_nonpositive_value_close_zero(self):
        for value, max_sp in ((None, 0), (None, -1), (None, -2147483648), (-Q, None),
                               (-9223372036854775808, None), (0, None)):
            with self.subTest(value=value, max_sp=max_sp):
                row = result_of(body(value=value, max_sp=max_sp))
                self.assertEqual(row['clamped_value_raw_reference'], 0)
                self.assertEqual(row['encoder_value_argument_raw_reference'], 0)
                self.assertTrue(row['normal_return_reference']); self.assertEqual(row['struct_copy_bytes_reference'], 40)

    def test_unknown_numeric_clamp_still_permits_qualified_normal_opaque_copy(self):
        for value, max_sp in ((None, 6), (1, None), (None, None)):
            with self.subTest(value=value, max_sp=max_sp):
                row = result_of(body(value=value, max_sp=max_sp))
                self.assertIsNone(row['clamped_value_raw_reference'])
                self.assertIsNone(row['encoder_value_argument_raw_reference'])
                self.assertTrue(row['encoder_called_reference']); self.assertTrue(row['copy_called_reference'])
                self.assertTrue(row['normal_return_reference']); self.assertTrue(row['internal_bool_return_reference'])
                self.assertTrue(row['full_struct_copy_completed_reference']); self.assertEqual(row['struct_copy_bytes_reference'], 40)

    def test_alive_false_returns_internal_false_but_public_void_returns_normally(self):
        for mode in ('public', 'internal', 'do_internal'):
            with self.subTest(mode=mode):
                row = result_of(body(mode=mode, alive=False, max_normal=False,
                                     encoding_normal=False, copy_normal=False))
                self.assertTrue(row['normal_return_reference'])
                self.assertIs(row['internal_bool_return_reference'], False)
                self.assertFalse(row['max_sp_called_reference']); self.assertFalse(row['encoder_called_reference'])
                self.assertFalse(row['copy_called_reference']); self.assertFalse(row['full_struct_copy_completed_reference'])
                self.assertEqual(row['struct_copy_bytes_reference'], 0)
                self.assertIs(row['public_void_returns_normally_reference'], True if mode == 'public' else None)

    def test_force_true_still_reads_alive_before_qualifying_max_and_copy(self):
        for mode in ('internal', 'do_internal'):
            row = result_of(body(mode=mode, alive=False, force=True, value=-Q))
            self.assertTrue(row['alive_called_reference']); self.assertTrue(row['alive_normal_reference'])
            self.assertTrue(row['max_sp_called_reference']); self.assertTrue(row['copy_called_reference'])
            self.assertEqual(row['encoder_value_argument_raw_reference'], 0)
            self.assertTrue(row['internal_bool_return_reference'])
            for normal in (False, None):
                with self.subTest(mode=mode, alive_normal=normal):
                    row = result_of(body(mode=mode, alive=False, force=True, alive_normal=normal))
                    self.assertIs(row['normal_return_reference'], normal)
                    self.assertIsNone(row['internal_bool_return_reference'])
                    self.assertIs(row['max_sp_called_reference'], False if normal is False else None)
                    self.assertIs(row['copy_called_reference'], False if normal is False else None)

    def test_alive_true_with_unknown_force_and_force_true_with_unknown_alive_have_same_write(self):
        for alive, force in ((True, None), (None, True)):
            with self.subTest(alive=alive, force=force):
                row = result_of(body(alive=alive, force=force, value=9 * Q, max_sp=6))
                self.assertTrue(row['alive_called_reference']); self.assertTrue(row['normal_return_reference'])
                self.assertTrue(row['internal_bool_return_reference'])
                self.assertEqual(row['encoder_value_argument_raw_reference'], 6 * Q)
                self.assertEqual(row['struct_copy_bytes_reference'], 40)

    def test_unknown_alive_or_force_preserves_normal_both_branches_but_copy_count_unknown(self):
        for alive, force, mode in ((None, False, 'public'), (False, None, 'internal')):
            with self.subTest(alive=alive, force=force):
                result = module.sp_setter_reference(payload(body(alive=alive, force=force, mode=mode)))
                row = result['rows'][0]
                self.assertTrue(row['normal_return_reference'])
                self.assertIsNone(row['internal_bool_return_reference'])
                self.assertIsNone(row['copy_called_reference']); self.assertIsNone(row['full_struct_copy_completed_reference'])
                self.assertIsNone(row['struct_copy_bytes_reference'])
                self.assertEqual(result['known_full_struct_copies_count'], 0)
                self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_unknown_alive_with_failed_active_branch_does_not_call_the_early_reject_a_failure(self):
        result = module.sp_setter_reference(payload(body(mode='public', alive=None, max_normal=False)))
        row = result['rows'][0]
        self.assertIsNone(row['normal_return_reference']); self.assertIsNone(row['public_void_returns_normally_reference'])
        self.assertIsNone(row['max_sp_called_reference'])
        self.assertFalse(row['encoder_called_reference']); self.assertFalse(row['copy_called_reference'])
        self.assertEqual(row['struct_copy_bytes_reference'], 0)

    def test_max_getter_abnormal_cannot_be_hidden_by_an_algebraically_zero_clamp(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                row = result_of(body(value=-Q, max_sp=0, max_normal=normal))
                self.assertTrue(row['max_sp_called_reference'])
                self.assertIs(row['max_sp_normal_reference'], normal)
                self.assertIs(row['normal_return_reference'], normal)
                self.assertIsNone(row['encoder_value_argument_raw_reference'])
                self.assertIs(row['encoder_called_reference'], False if normal is False else None)
                self.assertIs(row['copy_called_reference'], False if normal is False else None)

    def test_encoding_failure_leaves_a_known_argument_and_no_destination_copy(self):
        row = result_of(body(value=9 * Q, max_sp=6, encoding_normal=False))
        self.assertTrue(row['encoder_called_reference'])
        self.assertEqual(row['encoder_value_argument_raw_reference'], 6 * Q)
        self.assertIs(row['encoder_normal_reference'], False)
        self.assertIs(row['normal_return_reference'], False)
        self.assertIsNone(row['internal_bool_return_reference'])
        self.assertFalse(row['copy_called_reference']); self.assertFalse(row['full_struct_copy_completed_reference'])
        self.assertEqual(row['struct_copy_bytes_reference'], 0)

    def test_unknown_encoder_return_never_claims_copy_not_called_or_full40_complete(self):
        row = result_of(body(encoding_normal=None))
        self.assertTrue(row['encoder_called_reference']); self.assertIsNone(row['encoder_normal_reference'])
        self.assertIsNone(row['copy_called_reference']); self.assertIsNone(row['full_struct_copy_completed_reference'])
        self.assertIsNone(row['struct_copy_bytes_reference']); self.assertIsNone(row['normal_return_reference'])

    def test_copy_failure_does_not_report_complete40_or_zero_bytes_unmodified_state(self):
        for normal in (False, None):
            with self.subTest(normal=normal):
                result = module.sp_setter_reference(payload(body(copy_normal=normal))); row = result['rows'][0]
                self.assertTrue(row['encoder_called_reference']); self.assertTrue(row['copy_called_reference'])
                self.assertIs(row['normal_return_reference'], normal)
                self.assertIs(row['full_struct_copy_completed_reference'], False if normal is False else None)
                self.assertIsNone(row['struct_copy_bytes_reference'])
                self.assertIsNone(row['internal_bool_return_reference'])
                self.assertIsNone(row['actual_decoded_sp_after']); self.assertIsNone(row['actual_encoded_sp'])
                self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_rows_are_independent_and_one_failed_copy_does_not_erase_a_later_declared_write(self):
        result = module.sp_setter_reference(payload(body('bad', copy_normal=False), body('separate', value=Q)))
        self.assertIs(result['rows'][0]['normal_return_reference'], False)
        self.assertTrue(result['rows'][1]['normal_return_reference'])
        self.assertTrue(result['rows'][1]['full_struct_copy_completed_reference'])
        self.assertEqual(result['known_full_struct_copies_count'], 1)
        self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_explicit_null_target_distinguishes_public_forwarding_from_entered_internal_body(self):
        for mode in ('public', 'internal', 'do_internal'):
            with self.subTest(mode=mode):
                row = result_of(body(mode=mode, target=False))
                self.assertTrue(row['called_reference'])
                self.assertIs(row['internal_called_reference'], mode != 'public')
                self.assertIs(row['normal_return_reference'], False)
                self.assertFalse(row['alive_called_reference']); self.assertIsNone(row['alive_normal_reference'])
                self.assertIsNone(row['internal_bool_return_reference'])
                self.assertFalse(row['copy_called_reference']); self.assertEqual(row['struct_copy_bytes_reference'], 0)

    def test_unknown_target_does_not_lie_about_getter_call_and_failure_normal(self):
        for mode in ('public', 'internal', 'do_internal'):
            with self.subTest(mode=mode):
                row = result_of(body(mode=mode, target=None, alive_normal=False))
                self.assertIs(row['normal_return_reference'], False)
                self.assertIsNone(row['alive_called_reference']); self.assertIsNone(row['alive_normal_reference'])
                self.assertFalse(row['copy_called_reference']); self.assertEqual(row['struct_copy_bytes_reference'], 0)
        row = result_of(body(mode='public', target=None, alive=False))
        self.assertIsNone(row['internal_called_reference']); self.assertIsNone(row['normal_return_reference'])
        self.assertFalse(row['copy_called_reference'])

    def test_unbound_native_or_virtual_target_keeps_downstream_calls_and_complete_values_unknown(self):
        for key in ('ordinary_native_path', 'bound_virtual_dispatch'):
            for value in (False, None):
                row = body(); row[key] = value
                with self.subTest(key=key, value=value):
                    result = module.sp_setter_reference(payload(row)); out = result['rows'][0]
                    self.assertIsNone(out['normal_return_reference'])
                    self.assertIsNone(out['encoder_value_argument_raw_reference'])
                    self.assertIsNot(out['alive_called_reference'], False)
                    self.assertIsNot(out['copy_called_reference'], False)
                    self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_clock_link_uses_request9_but_never_rewrites_parent_or_claims_subsequent_sp6(self):
        data = linked(body_row=body('linked', mode='public', value=None, value_source='clock_request', max_sp=6))
        before = deepcopy(data); result = module.sp_setter_reference(data)
        self.assertEqual(result['rows'][0]['encoder_value_argument_raw_reference'], 6 * Q)
        self.assertEqual(result['clock_reference']['rows'][0]['tick']['recovery']['setter_value_argument_raw_reference'], 9 * Q)
        self.assertEqual(result['clock_reference']['rows'][2]['recovery']['sp_read_raw_reference'], 9 * Q)
        self.assertTrue(result['clock_links'][0]['normal_return_consistent_reference'])
        self.assertEqual(data, before)

    def test_recovery_force_true_does_not_promote_the_linked_public_setter_to_internal_force(self):
        data = linked(phase='recover', action_index=2,
                      body_row=body('linked', mode='public', value=None, value_source='clock_request', alive=False))
        result = module.sp_setter_reference(data); row = result['rows'][0]
        self.assertTrue(row['normal_return_reference']); self.assertTrue(row['public_void_returns_normally_reference'])
        self.assertIs(row['internal_bool_return_reference'], False)
        self.assertFalse(row['copy_called_reference']); self.assertEqual(row['struct_copy_bytes_reference'], 0)
        self.assertTrue(result['clock_links'][0]['normal_return_consistent_reference'])
        self.assertEqual(result['declared_complete_struct_copy_count'], 0)

    def test_parent_setter_normal_true_child_bool_false_is_consistent_but_child_exception_is_not(self):
        dead = linked(body_row=body('linked', mode='public', value=None, value_source='clock_request', alive=False))
        result = module.sp_setter_reference(dead)
        self.assertTrue(result['clock_links'][0]['normal_return_consistent_reference'])
        self.assertEqual(result['declared_complete_struct_copy_count'], 0)
        failed = linked(body_row=body('linked', mode='public', value=None, value_source='clock_request', copy_normal=False))
        result = module.sp_setter_reference(failed)
        self.assertIs(result['clock_links'][0]['normal_return_consistent_reference'], False)
        self.assertIsNone(result['declared_complete_struct_copy_count'])
        self.assertTrue(result['clock_reference']['rows'][0]['tick']['recovery']['setter_normal_reference'])

    def test_parent_setter_normal_false_child_normal_true_conflict_does_not_rewrite_clock_receipt(self):
        data = linked(); data['clock_bridge']['input']['actions'][0]['recovery']['setter_returns_normally'] = False
        before = deepcopy(data); result = module.sp_setter_reference(data)
        self.assertTrue(result['rows'][0]['normal_return_reference'])
        self.assertIs(result['clock_links'][0]['normal_return_consistent_reference'], False)
        self.assertIsNone(result['declared_complete_struct_copy_count'])
        self.assertIs(result['clock_reference']['rows'][0]['tick']['recovery']['setter_normal_reference'], False)
        self.assertEqual(result['clock_reference']['rows'][0]['tick']['known_prefix_remaining_raw_reference'], Q // 4)
        self.assertEqual(data, before)

    def test_linked_pause_without_setter_is_a_definite_unentered_zero_body_copy(self):
        data = linked(action_index=1); result = module.sp_setter_reference(data); row = result['rows'][0]
        self.assertFalse(row['called_reference']); self.assertFalse(row['internal_called_reference'])
        self.assertIsNone(row['normal_return_reference'])
        self.assertFalse(row['alive_called_reference']); self.assertFalse(row['encoder_called_reference'])
        self.assertFalse(row['copy_called_reference']); self.assertFalse(row['full_struct_copy_completed_reference'])
        self.assertEqual(row['struct_copy_bytes_reference'], 0)
        self.assertEqual(result['declared_complete_struct_copy_count'], 0)

    def test_unknown_parent_setter_call_cannot_publish_known_full_body_copy(self):
        data = linked(); data['clock_bridge']['input']['actions'][0]['recovery']['sp_read']['normal'] = None
        result = module.sp_setter_reference(data); row = result['rows'][0]
        self.assertIsNone(row['called_reference'])
        self.assertIsNot(row['full_struct_copy_completed_reference'], True)
        self.assertIsNone(row['struct_copy_bytes_reference'])
        self.assertEqual(result['known_full_struct_copies_count'], 0)
        self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_link_requires_same_target_and_no_value_change_without_inventing_source_values(self):
        for key in ('same_target', 'no_intervening_value_change'):
            for value in (False, None):
                data = linked(); data['clock_bridge']['links'][0][key] = value
                with self.subTest(key=key, value=value):
                    result = module.sp_setter_reference(data)
                    self.assertFalse(result['clock_links'][0]['qualified'])
                    self.assertIsNone(result['rows'][0]['encoder_value_argument_raw_reference'])
                    self.assertIsNone(result['declared_complete_struct_copy_count'])

    def test_drain_phase_binds_outer_reconfigure_id_and_cannot_alias_tick_or_recover(self):
        clock = clock_module.public_example()
        drain = deepcopy(clock['actions'][0]); drain['id'] = 'inner-drain'; drain['delta_raw'] = 0
        action = {'id': 'outer-reconfigure', 'kind': 'reconfigure', 'ordinary_native_path': True,
                  'rate_input_raw': 2 * Q, 'drain': drain, 'can_recover_rate': {
                      'ordinary_native_path': True, 'attributes_exist': True, 'reads_return_normally': True,
                      'attr14_raw': Q, 'attr30_raw': Q}}
        clock['actions'] = [action]; clock['timer']['remaining_raw'] = 0
        row = body('linked', mode='public', value=None, value_source='clock_request')
        data = payload(row, bridge={'input': clock, 'links': [{'body_id': 'linked', 'action_id': 'outer-reconfigure',
                    'phase': 'drain', 'same_target': True, 'no_intervening_value_change': True}]})
        result = module.sp_setter_reference(data)
        self.assertEqual(result['rows'][0]['encoder_value_argument_raw_reference'], 6 * Q)
        self.assertTrue(result['clock_links'][0]['normal_return_consistent_reference'])
        for phase in ('tick', 'recover'):
            changed = deepcopy(data); changed['clock_bridge']['links'][0]['phase'] = phase
            with self.subTest(phase=phase), self.assertRaises(ValueError): module.sp_setter_reference(changed)
        changed = deepcopy(data); changed['clock_bridge']['links'][0]['action_id'] = 'inner-drain'
        with self.assertRaises(ValueError): module.sp_setter_reference(changed)

    def test_clock_schema_rejects_duplicate_phase_body_bad_identity_mixed_values_and_internal_force_promotion(self):
        mutations = [lambda p: p['clock_bridge']['links'].append(deepcopy(p['clock_bridge']['links'][0])),
            lambda p: p['clock_bridge']['links'][0].update(action_id=[]),
            lambda p: p['clock_bridge']['links'][0].update(body_id=[]),
            lambda p: p['clock_bridge']['links'][0].update(action_id='missing'),
            lambda p: p['clock_bridge']['links'][0].update(body_id='missing'),
            lambda p: p['clock_bridge']['links'][0].update(phase='other'),
            lambda p: p['body_reads'][0].update(value_raw=Q),
            lambda p: p['body_reads'][0].update(value_source='independent', value_raw=Q),
            lambda p: p['body_reads'][0].update(mode='internal', force=True),
            lambda p: p['clock_bridge']['input'].update(extra=1)]
        for index, mutation in enumerate(mutations):
            data = linked(); mutation(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.sp_setter_reference(data)
            self.assertEqual(data, before)
        data = linked(); extra = deepcopy(data['body_reads'][0]); extra['id'] = 'second'
        data['body_reads'].append(extra); second_link = deepcopy(data['clock_bridge']['links'][0]); second_link['body_id'] = 'second'
        data['clock_bridge']['links'].append(second_link)
        with self.assertRaises(ValueError): module.sp_setter_reference(data)

    def test_standalone_schema_rejects_bad_raw_tri_mode_id_and_public_force_changes(self):
        mutations = [lambda p: p.update(extra=1), lambda p: p.update(body_reads=[]),
            lambda p: p['body_reads'][0].update(mode='other'), lambda p: p['body_reads'][0].update(value_raw=True),
            lambda p: p['body_reads'][0].update(value_raw=1 << 63), lambda p: p['body_reads'][0].update(value_raw=.5),
            lambda p: p['body_reads'][0].update(target_exists=1), lambda p: p['body_reads'][0].update(id='\n'),
            lambda p: p['body_reads'][0].update(id='\ud800'), lambda p: p['body_reads'][0]['alive_read'].update(value=1),
            lambda p: p['body_reads'][0]['max_sp_read'].update(value=True),
            lambda p: p['body_reads'][0]['max_sp_read'].update(value=1 << 31),
            lambda p: p['body_reads'][0]['max_sp_read'].update(value=-(1 << 31) - 1),
            lambda p: p['body_reads'][0].update(mode='public', force=True),
            lambda p: p['body_reads'][0].update(mode='public', force=None),
            lambda p: p['body_reads'][0].update(value_source='clock_request', value_raw=None),
            lambda p: p['body_reads'].append(deepcopy(p['body_reads'][0]))]
        for index, mutation in enumerate(mutations):
            data = payload(); mutation(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.sp_setter_reference(data)
            self.assertEqual(data, before)

    def test_source_binding_covers_native_bytes_metadata_dispatch_and_encoding_signature_only(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(hashlib.sha256((ROOT / module.SOURCE).read_bytes()).hexdigest(), module.SOURCE_SHA256)
        for name, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        proof_path = next(name for name in source['source_artifacts_sha256'] if '275' in name and name.endswith('/source-proof.json'))
        proof = json.loads((ROOT / proof_path).read_text(encoding='utf8')); unique = {}
        self.assertEqual(len(proof['methods']), 55)
        for record in proof['methods']:
            self.assertTrue(record['cfg_bounded_traversal_finished']); self.assertFalse(record['limits'])
            raw = b''.join(bytes.fromhex(row['bytes']) for row in record['instructions'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['reachable_bytes_sha256'])
            unique.update({row['address']: row for row in record['instructions']})
        self.assertEqual(len(unique), 2599)
        self.assertEqual(sum(len(bytes.fromhex(row['bytes'])) for row in unique.values()), 11190)
        self.assertEqual(len(proof['byte_spans']), 3971)
        self.assertFalse(proof['game_dll_executed']); self.assertFalse(proof['process_memory_read'])
        for target in ('Torappu.Battle.Entity', 'Torappu.Battle.Character'):
            self.assertEqual(proof['selected_dispatch'][target]['113']['method_index'], 66628)
        self.assertEqual(proof['selected_dispatch']['Torappu.Battle.Entity']['40']['method_index'], 66349)
        self.assertEqual(proof['selected_dispatch']['Torappu.Battle.Character']['40']['method_index'], 75822)
        encoding = proof['encoding_signature_and_mapping_only']
        self.assertFalse(encoding['encoding_body_evaluated']); self.assertFalse(encoding['later_decoding_equivalence_proven'])
        source['source_artifacts_sha256'].clear(); self.assertTrue(module.source_data()['source_artifacts_sha256'])

    def test_invalid_source_and_each_actual_effect_remain_unknown_even_with_public_gold(self):
        with patch.object(module, '_source_data', return_value=None):
            result = module.sp_setter_reference(module.public_example())
        self.assertFalse(result['source_valid']); self.assertIsNone(result['declared_complete_struct_copy_count'])
        self.assertTrue(all(row['normal_return_reference'] is None for row in result['rows']))
        result = module.sp_setter_reference(module.public_example())
        for field in ('actual_sp_after', 'actual_complete_recovery', 'actual_skill_cycle', 'actual_clock', 'actual_encoded_state'):
            self.assertIsNone(result[field])
        self.assertTrue(all(row['actual_decoded_sp_after'] is None and row['actual_encoded_sp'] is None for row in result['rows']))
        self.assertFalse(result['events_scheduled']); self.assertFalse(result['hotfix_equivalence_proven'])


if __name__ == '__main__':
    unittest.main()
