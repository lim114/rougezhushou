"""Independent literal and control-flow vectors for the 13/19 FP getters.

Gold values come from the bound original instruction/parameter receipts. The
tests do not use production arithmetic as their oracle or infer live inventory.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import recovery_attributes as module

ROOT = Path(__file__).resolve().parents[1]
Q = 4294967296


def cached_modifier(identity='modifier', *, addition=0, multiplier=0, final_addition=0,
                    final_scaler=Q, registered=True, exists=True, normal=True, included=True):
    return {'id': identity, 'registered': registered, 'exists': exists,
            'get_value_normal': normal, 'included': included, 'basis': 'independent_cache',
            'cache_values': {'addition': addition, 'multiplier_delta': multiplier,
                             'final_addition': final_addition, 'final_scaler': final_scaler},
            'flower_load': None}


def flower(suffix=81, *, identity=None, **changes):
    result = {'id': identity or 'flower' + str(suffix), 'registered': True, 'exists': True,
              'get_value_normal': True, 'included': True, 'basis': 'flower_load',
              'cache_values': None, 'flower_load': {
                  'relic_id': 'rogue_6_relic_legacy_' + str(suffix), 'recipe_matches_bound': True,
                  'blackboard_exists': True, 'try_returns_normally': True, 'number_found': True,
                  'number_basis': 'nominal_bound_float', 'number_matches_bound_parameter': True,
                  'number_raw': None, 'stack_count': 1, 'cache_matches_completed_load': True,
                  'load_accesses_normal': True}}
    result['flower_load'].update(changes)
    return result


def reading(identity='read', *, attribute=13, raw=10 * Q, modifiers=(), dirty=True,
            cache_raw=None, cache_normal=None):
    return {'id': identity, 'attribute': attribute, 'ordinary_native_path': True,
            'attributes_exist': True, 'dirty': dirty,
            'decoded_cache': {'normal': cache_normal, 'raw': cache_raw},
            'calculation': {'inventory_complete': True, 'enumeration_normal': True,
                            'modifiers': list(modifiers), 'raw_read': {'normal': True, 'raw': raw},
                            'range_read': {'normal': True, 'override': False,
                                           'metadata_range_matches': True, 'lower_raw': None,
                                           'upper_raw': None}, 'cache_store_normal': True}}


def payload(*rows):
    return {'readings': list(rows) or [reading()], 'clock_bridge': None}


def result_of(row):
    return module.recovery_attribute_reference(payload(row))['rows'][0]


class RecoveryAttributeTests(unittest.TestCase):
    def test_three_flowers_add_fp_deltas_and_link_two_independent_rate_points(self):
        data = module.public_example(); before = deepcopy(data)
        result = module.recovery_attribute_reference(data)
        self.assertTrue(result['source_valid'])
        self.assertEqual([row['getter_raw_reference'] for row in result['rows']],
                         [81604379520, 510027372, 81604379520, 510027372])
        self.assertEqual([row['buckets_reference']['multiplier_delta'] for row in result['rows']],
                         [8160437952] * 4)
        self.assertEqual([step['flower_load']['loaded_multiplier_raw_reference']
                          for step in result['rows'][0]['steps']],
                         [858993472, 1288490240, 1717986944])
        self.assertEqual([link['snapshot_reference']['flat_raw'] for link in result['clock_links']],
                         [81604379520, 81604379520])
        clock = result['clock_reference']; self.assertTrue(clock['declared_chain_complete'])
        self.assertEqual(clock['rows'][0]['can_recover']['rate_raw_reference'], 132607116720)
        self.assertEqual(clock['rows'][0]['period_rate']['rate_raw_reference'], 132607116720)
        self.assertEqual(data, before)

    def test_same_flower_load_has_distinct_bound_13_and_19_channels(self):
        result = module.recovery_attribute_reference(payload(
            reading('flat', modifiers=[flower()]),
            reading('ratio', attribute=19, raw=Q // 16, modifiers=[flower()])))
        self.assertEqual([row['getter_raw_reference'] for row in result['rows']],
                         [51539607680, 322122548])
        self.assertEqual([row['steps'][0]['flower_load']['source_buff_index'] for row in result['rows']],
                         [1, 2])
        self.assertEqual([row['steps'][0]['flower_load']['attribute'] for row in result['rows']], [13, 19])

    def test_ratio_default_range_clamps_after_all_four_buckets(self):
        row = reading(attribute=19, raw=3 * Q // 4, modifiers=[flower(81), flower(82), flower(83)])
        result = result_of(row)
        self.assertEqual(result['pre_clamp_raw_reference'], 6120328464)
        self.assertEqual(result['computed_clamped_raw_reference'], Q)
        self.assertEqual(result['getter_raw_reference'], Q)
        self.assertEqual((result['lower_raw_reference'], result['upper_raw_reference']), (0, Q))

    def test_flat_default_fp_max_is_not_signed64_max_and_negative_values_clamp(self):
        for raw, expected in (((1 << 63) - 1, 9223372036854775806), (-Q, 0), (0, 0)):
            with self.subTest(raw=raw):
                result = result_of(reading(raw=raw))
                self.assertEqual(result['getter_raw_reference'], expected)
                self.assertEqual(result['upper_raw_reference'], 9223372036854775806)

    def test_clean_decoded_cache_bypasses_recompute_inventory_and_failing_stages(self):
        row = reading(dirty=False, cache_raw=-3 * Q, cache_normal=True)
        row['calculation']['inventory_complete'] = False
        row['calculation']['enumeration_normal'] = False
        row['calculation']['raw_read']['normal'] = False
        row['calculation']['range_read']['normal'] = False
        row['calculation']['cache_store_normal'] = False
        result = result_of(row)
        self.assertEqual(result['getter_raw_reference'], -3 * Q)
        self.assertTrue(result['normal_return_reference'])
        self.assertFalse(result['dirty_cleared_reference'])
        self.assertIsNone(result['cache_write_value_argument_raw_reference'])
        self.assertEqual(result['status'], 'independent_decoded_cache')
        self.assertNotIn('steps', result)

    def test_clean_cache_has_its_own_normal_qualification_and_needs_no_calculation(self):
        for normal, expected in ((True, 123), (False, None), (None, None)):
            row = reading(dirty=False, cache_raw=123, cache_normal=normal); row['calculation'] = None
            with self.subTest(normal=normal):
                result = result_of(row)
                self.assertIs(result['normal_return_reference'], normal)
                self.assertEqual(result['getter_raw_reference'], expected)
                self.assertFalse(result['dirty_cleared_reference'])

    def test_unknown_dirty_preserves_equal_branch_value_and_normal_but_not_dirty_state(self):
        row = reading(dirty=None, cache_raw=10 * Q, cache_normal=True)
        result = result_of(row)
        self.assertTrue(result['normal_return_reference'])
        self.assertEqual(result['getter_raw_reference'], 10 * Q)
        self.assertIsNone(result['dirty_cleared_reference'])
        self.assertFalse(result['clean_reference']['dirty_cleared_reference'])
        self.assertTrue(result['recompute_reference']['dirty_cleared_reference'])
        row['decoded_cache']['raw'] = 9 * Q
        self.assertIsNone(result_of(row)['getter_raw_reference'])

    def test_unknown_dirty_keeps_branch_failures_and_cannot_borrow_a_known_cache(self):
        row = reading(dirty=None, cache_raw=10 * Q, cache_normal=True)
        row['calculation']['raw_read']['normal'] = False
        result = result_of(row)
        self.assertIsNone(result['normal_return_reference']); self.assertIsNone(result['getter_raw_reference'])
        self.assertTrue(result['recompute_reference']['dirty_cleared_reference'])
        row['decoded_cache']['normal'] = False
        result = result_of(row)
        self.assertIs(result['normal_return_reference'], False)
        self.assertIsNone(result['getter_raw_reference'])

    def test_enumeration_failure_stops_before_clear_dirty_raw_and_range(self):
        for normal in (False, None):
            row = reading(); row['calculation']['enumeration_normal'] = normal
            with self.subTest(normal=normal):
                result = result_of(row)
                self.assertIs(result['normal_return_reference'], normal)
                self.assertIs(result['dirty_cleared_reference'], False if normal is False else None)
                self.assertFalse(result['raw_read_called_reference'])
                self.assertFalse(result['range_read_called_reference'])
                self.assertIsNone(result['getter_raw_reference'])

    def test_raw_read_failure_keeps_already_cleared_dirty_but_never_calls_range(self):
        for normal in (False, None):
            row = reading(); row['calculation']['raw_read']['normal'] = normal
            with self.subTest(normal=normal):
                result = result_of(row)
                self.assertTrue(result['dirty_cleared_reference'])
                self.assertTrue(result['raw_read_called_reference']); self.assertFalse(result['range_read_called_reference'])
                self.assertIs(result['normal_return_reference'], normal)
                self.assertIsNone(result['getter_raw_reference'])

    def test_range_read_failure_keeps_preclamp_but_blocks_cache_and_return(self):
        for normal in (False, None):
            row = reading(); row['calculation']['range_read']['normal'] = normal
            with self.subTest(normal=normal):
                result = result_of(row)
                self.assertTrue(result['dirty_cleared_reference']); self.assertTrue(result['range_read_called_reference'])
                self.assertEqual(result['pre_clamp_raw_reference'], 10 * Q)
                self.assertIs(result['normal_return_reference'], normal)
                self.assertIsNone(result['cache_write_value_argument_raw_reference'])
                self.assertIsNone(result['getter_raw_reference'])

    def test_cache_store_failure_retains_computed_argument_without_claiming_a_getter_return(self):
        for normal in (False, None):
            row = reading(); row['calculation']['cache_store_normal'] = normal
            with self.subTest(normal=normal):
                result = result_of(row)
                self.assertTrue(result['dirty_cleared_reference'])
                self.assertEqual(result['computed_clamped_raw_reference'], 10 * Q)
                self.assertEqual(result['cache_write_value_argument_raw_reference'], 10 * Q)
                self.assertIs(result['normal_return_reference'], normal)
                self.assertIsNone(result['getter_raw_reference'])

    def test_four_buckets_are_additive_except_ordered_final_scalers_then_formula(self):
        row = reading(modifiers=[
            cached_modifier('a', addition=2 * Q, multiplier=Q // 2, final_addition=3 * Q, final_scaler=2 * Q),
            cached_modifier('b', addition=Q, multiplier=Q // 4, final_addition=Q, final_scaler=Q // 2)])
        result = result_of(row)
        self.assertEqual(result['buckets_reference'], {'addition': 3 * Q, 'multiplier_delta': 7 * Q // 4,
                         'final_addition': 4 * Q, 'final_scaler': Q})
        self.assertEqual(result['getter_raw_reference'], 114890375168)  # 26.75 * Q
        wrapped = result_of(reading(raw=9223372036854775807,
                                   modifiers=[cached_modifier(addition=1)]))
        self.assertEqual(wrapped['pre_clamp_raw_reference'], -9223372036854775808)
        self.assertEqual(wrapped['getter_raw_reference'], 0)

    def test_final_scaler_order_preserves_each_intermediate_fp_truncation(self):
        half = cached_modifier('half', final_scaler=Q // 2)
        a = cached_modifier('a', final_scaler=Q + 1); b = cached_modifier('b', final_scaler=Q + 1)
        first = result_of(reading(modifiers=[half, a, b]))
        second = result_of(reading(modifiers=[a, b, half]))
        self.assertEqual(first['buckets_reference']['final_scaler'], 2147483648)
        self.assertEqual(second['buckets_reference']['final_scaler'], 2147483649)
        self.assertEqual(first['getter_raw_reference'], 21474836480)
        self.assertEqual(second['getter_raw_reference'], 21474836490)
        self.assertEqual([row['id'] for row in first['steps']], ['half', 'a', 'b'])

    def test_multiplier_clamps_zero_before_final_addition_and_scaler(self):
        row = reading(raw=10 * Q, modifiers=[cached_modifier(multiplier=-2 * Q,
                      final_addition=3 * Q, final_scaler=2 * Q)])
        result = result_of(row)
        self.assertEqual(result['buckets_reference']['multiplier_delta'], -Q)
        self.assertEqual(result['getter_raw_reference'], 6 * Q)

    def test_final_zero_annihilates_an_unknown_typed_raw_only_after_normal_reads(self):
        row = reading(raw=None, modifiers=[cached_modifier(final_scaler=0)])
        result = result_of(row)
        self.assertEqual(result['pre_clamp_raw_reference'], 0); self.assertEqual(result['getter_raw_reference'], 0)
        row['calculation']['raw_read']['normal'] = None
        result = result_of(row)
        self.assertIsNone(result['getter_raw_reference']); self.assertIsNone(result['normal_return_reference'])

    def test_explicit_unregistered_skips_nonexistent_and_failing_modifier(self):
        result = result_of(reading(modifiers=[cached_modifier(registered=False, exists=False, normal=False,
                                  multiplier=100 * Q)]))
        self.assertEqual(result['getter_raw_reference'], 10 * Q)
        self.assertTrue(result['normal_return_reference'])
        self.assertEqual(result['steps'][0]['status'], 'not_registered')
        self.assertFalse(result['steps'][0]['get_value_called_reference'])
        self.assertIsNone(result['steps'][0]['get_value_normal_reference'])
        self.assertTrue(result['steps'][0]['member_processing_normal_reference'])

    def test_included_false_does_not_skip_getvalue_exception_and_stops_later_modifier(self):
        row = reading(modifiers=[cached_modifier('bad', normal=False, included=False), cached_modifier('later')])
        result = result_of(row)
        self.assertIs(result['normal_return_reference'], False)
        self.assertFalse(result['raw_read_called_reference'])
        self.assertFalse(result['dirty_cleared_reference'])
        self.assertTrue(result['steps'][0]['get_value_called_reference'])
        self.assertIs(result['steps'][0]['get_value_normal_reference'], False)
        self.assertIs(result['steps'][0]['member_processing_normal_reference'], False)
        self.assertEqual(result['steps'][1]['status'], 'not_called_after_unqualified_enumeration')

    def test_unknown_registration_and_inclusion_close_only_agreeing_normal_branches(self):
        for registration, inclusion in ((None, True), (True, None), (None, None), (None, False)):
            row = reading(modifiers=[cached_modifier(registered=registration, included=inclusion)])
            with self.subTest(registration=registration, inclusion=inclusion):
                result = result_of(row)
                self.assertTrue(result['normal_return_reference']); self.assertEqual(result['getter_raw_reference'], 10 * Q)
        result = result_of(reading(modifiers=[cached_modifier(registered=None, normal=False)]))
        self.assertIsNone(result['normal_return_reference']); self.assertIsNone(result['getter_raw_reference'])
        result = result_of(reading(modifiers=[cached_modifier(included=None, multiplier=Q)]))
        self.assertTrue(result['normal_return_reference']); self.assertIsNone(result['getter_raw_reference'])

    def test_incomplete_inventory_does_not_publish_a_complete_attribute_value(self):
        for complete in (False, None):
            row = reading(); row['calculation']['inventory_complete'] = complete
            with self.subTest(complete=complete):
                result = result_of(row)
                self.assertTrue(result['normal_return_reference'])
                self.assertIsNone(result['buckets_reference'])
                self.assertIsNone(result['pre_clamp_raw_reference'])
                self.assertEqual(result['listed_buckets_reference'], {'addition': 0, 'multiplier_delta': Q,
                                                                     'final_addition': 0, 'final_scaler': Q})
                self.assertEqual(result['listed_pre_clamp_raw_reference'], 10 * Q)
                self.assertIsNone(result['getter_raw_reference'])
                self.assertIsNone(result['cache_write_value_argument_raw_reference'])

    def test_successful_zero_negative_and_absent_key_are_distinct_normal_flower_reads(self):
        vectors = [(True, 0, 10 * Q, False), (True, -Q // 2, 5 * Q, False),
                   (False, 99 * Q, 10 * Q, True)]
        for found, number, expected, used_zero in vectors:
            row = reading(modifiers=[flower(number_basis='independent_fp', number_raw=number, number_found=found)])
            with self.subTest(found=found, number=number):
                result = result_of(row)
                self.assertEqual(result['getter_raw_reference'], expected)
                self.assertIs(result['steps'][0]['flower_load']['default_zero_used_reference'], used_zero)
                self.assertTrue(result['steps'][0]['flower_load']['load_normal_reference'])

    def test_flower_fallback_zero_cannot_hide_a_failed_or_unknown_tryfp_return(self):
        for key in ('blackboard_exists', 'try_returns_normally', 'load_accesses_normal'):
            for normal in (False, None):
                row = reading(modifiers=[flower(number_found=False, **{key: normal})])
                with self.subTest(key=key, normal=normal):
                    result = result_of(row)
                    load = result['steps'][0]['flower_load']
                    self.assertIs(load['load_normal_reference'], normal)
                    self.assertIsNone(load['loaded_multiplier_raw_reference'])
                    self.assertIsNone(result['getter_raw_reference'])

    def test_signed_stack_count_zero_negative_and_unknown_have_literal_or_qualified_closure(self):
        for stack, expected in ((0, 42949672960), (-1, 34359738240), (2, 60129542400)):
            with self.subTest(stack=stack):
                result = result_of(reading(modifiers=[flower(stack_count=stack)]))
                self.assertEqual(result['getter_raw_reference'], expected)
        result = result_of(reading(modifiers=[flower(stack_count=None)]))
        self.assertIsNone(result['getter_raw_reference'])
        for changes in ({'number_found': False}, {'number_basis': 'independent_fp', 'number_raw': 0}):
            result = result_of(reading(modifiers=[flower(stack_count=None, **changes)]))
            self.assertEqual(result['steps'][0]['flower_load']['loaded_multiplier_raw_reference'], 0)
            self.assertEqual(result['getter_raw_reference'], 10 * Q)

    def test_loaded_flower_requires_independent_recipe_parameter_and_completed_cache_matches(self):
        for key in ('recipe_matches_bound', 'number_matches_bound_parameter', 'cache_matches_completed_load'):
            for value in (False, None):
                with self.subTest(key=key, value=value):
                    result = result_of(reading(modifiers=[flower(**{key: value})]))
                    self.assertIsNone(result['getter_raw_reference'])
        row = reading(modifiers=[flower(number_basis='independent_fp', number_raw=Q // 4,
                                       number_matches_bound_parameter=False)])
        self.assertEqual(result_of(row)['getter_raw_reference'], 53687091200)

    def test_dynamic_range_override_ignores_metadata_default_and_has_independent_normal_gate(self):
        row = reading(raw=10 * Q)
        row['calculation']['range_read'].update(override=True, metadata_range_matches=False,
                                               lower_raw=2 * Q, upper_raw=3 * Q)
        result = result_of(row)
        self.assertEqual(result['getter_raw_reference'], 3 * Q)
        self.assertEqual((result['lower_raw_reference'], result['upper_raw_reference']), (2 * Q, 3 * Q))
        row['calculation']['range_read']['normal'] = False
        self.assertIsNone(result_of(row)['getter_raw_reference'])
        row = reading(); row['calculation']['range_read']['metadata_range_matches'] = False
        self.assertIsNone(result_of(row)['getter_raw_reference'])

    def test_reversed_bounds_follow_native_min_upper_then_max_lower_even_with_unknown_value(self):
        # 0x1866ff330/333 chooses min(value, upper); 345/348 then max(..., lower).
        # For a reversed range the result is always lower, not upper.
        for raw in (-Q, 2 * Q, 4 * Q, None):
            row = reading(raw=raw)
            row['calculation']['range_read'].update(override=True, lower_raw=3 * Q, upper_raw=Q)
            with self.subTest(raw=raw):
                result = result_of(row)
                self.assertEqual(result['getter_raw_reference'], 3 * Q)
                self.assertTrue(result['normal_return_reference'])

    def test_unknown_override_can_close_identical_default_and_dynamic_ranges(self):
        row = reading(attribute=19, raw=2 * Q)
        row['calculation']['range_read'].update(override=None, lower_raw=0, upper_raw=Q)
        self.assertEqual(result_of(row)['getter_raw_reference'], Q)
        row['calculation']['range_read']['upper_raw'] = 3 * Q
        self.assertIsNone(result_of(row)['getter_raw_reference'])

    def test_ordinary_source_and_attribute_instance_gates_do_not_admit_otherwise_known_cache(self):
        for key in ('ordinary_native_path', 'attributes_exist'):
            for value in (False, None):
                row = reading(dirty=False, cache_raw=10 * Q, cache_normal=True); row[key] = value
                with self.subTest(key=key, value=value):
                    result = result_of(row)
                    self.assertIsNone(result['getter_raw_reference'])
                    expected = False if key == 'attributes_exist' and value is False else None
                    self.assertIs(result['normal_return_reference'], expected)

    def test_unknown_instance_with_definite_clean_cache_failure_closes_abnormal_return(self):
        # A missing instance and an existing instance with failed decoding both
        # fail. Their existence branches cannot create a normal return.
        for dirty in (False, True, None):
            row = reading(dirty=dirty, cache_raw=10 * Q, cache_normal=False)
            row['attributes_exist'] = None
            row['calculation']['raw_read']['normal'] = False
            with self.subTest(dirty=dirty):
                result = result_of(row)
                self.assertIs(result['normal_return_reference'], False)
                self.assertIsNone(result['getter_raw_reference'])
        row = reading(dirty=False, cache_raw=10 * Q, cache_normal=False)
        row['attributes_exist'] = None
        row['decoded_cache']['normal'] = True
        self.assertIsNone(result_of(row)['normal_return_reference'])

    def test_clock_links_keep_two_read_points_distinct_and_require_same_unchanged_entity(self):
        data = module.public_example()
        data['readings'][2]['calculation']['raw_read']['raw'] = 20 * Q
        result = module.recovery_attribute_reference(data)
        self.assertEqual(result['clock_reference']['rows'][0]['can_recover']['rate_raw_reference'], 132607116720)
        self.assertEqual(result['clock_reference']['rows'][0]['period_rate']['rate_raw_reference'], 214211496240)
        for key in ('same_entity', 'unchanged_to_point'):
            for value in (False, None):
                changed = module.public_example(); changed['clock_bridge']['links'][0][key] = value
                with self.subTest(key=key, value=value):
                    linked = module.recovery_attribute_reference(changed)
                    self.assertFalse(linked['clock_links'][0]['qualified'])
                    self.assertIsNone(linked['clock_links'][0]['snapshot_reference'])
                    self.assertIsNone(linked['clock_reference']['rows'][0]['can_recover']['rate_raw_reference'])

    def test_clock_link_failure_cannot_borrow_maxhp_or_other_reading_return(self):
        data = module.public_example(); data['clock_bridge']['links'][0]['max_hp_read_normal'] = False
        result = module.recovery_attribute_reference(data)
        self.assertTrue(result['clock_links'][0]['qualified'])
        self.assertIs(result['clock_reference']['rows'][0]['can_recover']['normal_return_reference'], False)
        self.assertIsNone(result['clock_reference']['rows'][0]['period_rate'])
        data = module.public_example(); data['readings'][0]['calculation']['cache_store_normal'] = False
        result = module.recovery_attribute_reference(data)
        self.assertIs(result['clock_links'][0]['snapshot_reference']['reads_return_normally'], False)
        self.assertIsNone(result['clock_links'][0]['snapshot_reference']['flat_raw'])

    def test_clock_link_schema_does_not_overwrite_snapshot_swap_attributes_or_reuse_point(self):
        mutations = [
            lambda p: p['clock_bridge']['input']['actions'][0].update(can_recover_snapshot={
                'attributes_exist': True, 'reads_return_normally': True, 'flat_raw': Q, 'ratio_raw': 0, 'max_hp_raw': 100 * Q}),
            lambda p: p['clock_bridge']['links'][0].update(flat_read_id='first19', ratio_read_id='first13'),
            lambda p: p['clock_bridge']['links'][0].update(flat_read_id='missing'),
            lambda p: p['clock_bridge']['links'][0].update(action_id='missing'),
            lambda p: p['clock_bridge']['links'][0].update(action_id=[]),
            lambda p: p['clock_bridge']['links'][0].update(flat_read_id=[]),
            lambda p: p['clock_bridge']['links'].append(deepcopy(p['clock_bridge']['links'][0])),
            lambda p: p['clock_bridge']['links'][1].update(flat_read_id='first13'),
            lambda p: p['clock_bridge']['links'][1].update(ratio_read_id='first19'),
            lambda p: p['clock_bridge']['links'][0].update(point='arbitrary'),
            lambda p: p['clock_bridge']['input'].update(extra=True)]
        for index, mutation in enumerate(mutations):
            data = module.public_example(); mutation(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.recovery_attribute_reference(data)
            self.assertEqual(data, before)

    def test_schema_rejects_unsafe_values_duplicates_mixed_basis_and_unsupported_attributes(self):
        mutations = [lambda p: p.update(extra=1), lambda p: p.update(readings=[]),
            lambda p: p['readings'][0].update(attribute=3), lambda p: p['readings'][0].update(attribute=True),
            lambda p: p['readings'][0].update(dirty=1), lambda p: p['readings'][0].update(id='\n'),
            lambda p: p['readings'][0].update(id='\ud800'),
            lambda p: p['readings'][0]['decoded_cache'].update(raw=True),
            lambda p: p['readings'][0]['calculation']['raw_read'].update(raw=1 << 63),
            lambda p: p['readings'][0]['calculation']['raw_read'].update(raw=.5),
            lambda p: p['readings'].append(deepcopy(p['readings'][0])),
            lambda p: p['readings'][0]['calculation']['range_read'].update(lower_raw=0),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[cached_modifier(), cached_modifier()]),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[flower(number_raw=1)]),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[flower(stack_count=True)]),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[flower(stack_count=1 << 31)]),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[flower(relic_id='other')]),
            lambda p: p['readings'][0]['calculation'].update(modifiers=[cached_modifier(final_scaler='1')])]
        for index, mutation in enumerate(mutations):
            data = payload(); mutation(data); before = deepcopy(data)
            with self.subTest(index=index), self.assertRaises(ValueError): module.recovery_attribute_reference(data)
            self.assertEqual(data, before)

    def test_source_manifest_bytes_native_cfg_and_metadata_spans_are_bound_and_copy_is_private(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(hashlib.sha256((ROOT / module.SOURCE).read_bytes()).hexdigest(), module.SOURCE_SHA256)
        for name, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        proof_path = next(name for name in source['source_artifacts_sha256'] if '273' in name and name.endswith('/source-proof.json'))
        native = json.loads((ROOT / proof_path).read_text(encoding='utf8'))
        self.assertEqual(len(native['methods']), 34); unique = {}
        for record in native['methods']:
            self.assertTrue(record['cfg_bounded_traversal_finished']); self.assertFalse(record['limits'])
            raw = b''.join(bytes.fromhex(row['bytes']) for row in record['instructions'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record['reachable_bytes_sha256'])
            unique.update({row['address']: row for row in record['instructions']})
        self.assertEqual(len(unique), 2945); self.assertEqual(len(native['byte_spans']), 4836)
        self.assertFalse(native['game_dll_executed']); self.assertFalse(native['process_memory_read'])
        source['source_artifacts_sha256'].clear(); source['flower_channels'][0]['parameter_fp_raw'] = 0
        self.assertTrue(module.source_data()['source_artifacts_sha256'])
        self.assertEqual(module.source_data()['flower_channels'][0]['parameter_fp_raw'], 858993472)

    def test_invalid_source_keeps_attributes_clock_and_actual_totals_unknown(self):
        with patch.object(module, '_source_data', return_value=None):
            result = module.recovery_attribute_reference(module.public_example())
        self.assertFalse(result['source_valid'])
        self.assertTrue(all(row['getter_raw_reference'] is None for row in result['rows']))
        self.assertTrue(all(link['snapshot_reference'] is None for link in result['clock_links']))
        self.assertIsNone(result['clock_reference']['final_period_raw_reference'])
        for field in ('actual_attribute_values', 'actual_cache_or_dirty_state', 'actual_clock', 'actual_hp_after', 'actual_complete_healing'):
            self.assertIsNone(result[field])
        self.assertFalse(result['events_scheduled']); self.assertFalse(result['hotfix_equivalence_proven'])


if __name__ == '__main__':
    unittest.main()
