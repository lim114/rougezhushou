"""Necessary independent controls for declared SP14/30 initialization/dirty flow.

No live cache, subscription, callback target, timer or SP is observed. Conditional
literal references and failed/unknown normality remain separate.
"""
import argparse
import copy
import hashlib
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
import uuid

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
MODULE_FILE = ROOT / 'rouge/sp_recovery_attribute_reference.py'
Q = 4294967296
UNKNOWNS = ('actual_attribute_values', 'actual_cache_or_dirty_state', 'actual_sp_after', 'actual_timer', 'complete_cycle')
INIT_STAGES = ('attributes_read', 'sp_data_access', 'increments_read', 'increments_guard', 'slot0_read',
    'single_conversion', 'attributes_guard', 'raw_array_capture', 'raw_encode', 'raw_array_guard',
    'raw_store', 'mark_dirty', 'refresh')
RATE_STAGES = ('first_attributes_getter', 'flat_read', 'second_attributes_getter', 'ratio_read', 'multiply')
NOTIFY_STAGES = ('entity_access', 'controller_capture', 'new_rate', 'controller_guard', 'controller_update')
RAW_PREFIX = {'field': 'rawData[14]', 'byte_count': 40, 'payload_identity': None, 'decoded_value': None}


def load_module(path):
    """Use an isolated package for relative imports, never a fallback module path."""
    path = Path(path).resolve(strict=True)
    package_name = 'sp282_independent_' + uuid.uuid4().hex
    package = types.ModuleType(package_name)
    package.__path__ = [str(path.parent)]
    package.__package__ = package_name
    package.__spec__ = importlib.machinery.ModuleSpec(package_name, loader=None, is_package=True)
    sys.modules[package_name] = package
    name = package_name + '.sp_recovery_attribute_reference'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module, package_name


def unload_package(name):
    for key in tuple(sys.modules):
        if key == name or key.startswith(name + '.'):
            sys.modules.pop(key, None)


def reading(label, attribute=14, raw=Q, *, dirty=False):
    return {'id': label, 'attribute': attribute, 'ordinary_native_path': True, 'attributes_exist': True,
        'dirty': dirty, 'decoded_cache': {'normal': True, 'raw': raw},
        'calculation': None if not dirty else {'inventory_complete': True, 'enumeration_normal': True,
            'modifiers': [], 'raw_read': {'normal': True, 'raw': raw},
            'range_read': {'normal': True, 'override': False, 'metadata_range_matches': True,
                           'lower_raw': None, 'upper_raw': None}, 'cache_store_normal': True}}


def modifier(label='mod', addition=0, mult_delta=0, final_addition=0, final_scaler=Q):
    return {'id': label, 'registered': True, 'exists': True, 'get_value_normal': True, 'included': True,
        'basis': 'independent_cache', 'flower_load': None, 'cache_values': {'addition': addition,
        'multiplier_delta': mult_delta, 'final_addition': final_addition, 'final_scaler': final_scaler}}


def ptr(label, identity=None, exists=True, normal=True, length=None):
    value = {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}
    if length is not None:
        value['length'] = length
    return value


def initialization(label='initial'):
    return {'id': label, 'ordinary_native_path': True,
        'attributes_read': ptr(label + '.attributes'), 'sp_data_read': ptr(label + '.spdata'),
        'increments_read': ptr(label + '.increments', length=1),
        'slot0_read': {'id': label + '.slot0', 'normal': True, 'bits': 0x3FC00000},
        'single_conversion_normally': True, 'raw_array_read': ptr(label + '.raw-array', length=15),
        'raw_encoder_normally': True, 'raw_store_normally': True, 'mark_dirty_returns_normally': True,
        'refresh_read_id': 'refresh14', 'refresh_same_attributes': True, 'refresh_unchanged_to_point': True}


def rate(label, flat, ratio):
    return {'id': label, 'ordinary_native_path': True, 'first_attributes_getter_normal': True,
        'second_attributes_getter_normal': True, 'flat_read_id': flat, 'ratio_read_id': ratio,
        'same_entity': True, 'unchanged_to_point': True, 'multiply_normally': True}


def drain(label='drain-zero', enabled=False):
    return {'id': label, 'kind': 'tick', 'ordinary_native_path': True, 'delta_raw': 0, 'enabled': enabled,
        'gate_stop': {'exists': True, 'normal': True, 'value': False},
        'full_read': {'normal': True, 'value': False},
        'recovery': {'ordinary_native_path': True, 'force': False,
            'stop_read': {'exists': True, 'normal': True, 'value': False},
            'sp_read': {'exists': True, 'normal': True, 'raw': 0}, 'setter_returns_normally': True}}


def notification(label='dirty', attribute=30):
    return {'id': label, 'attribute': attribute, 'old_value_raw': 99 * Q, 'ordinary_native_path': True,
        'entity_exists': True, 'controller_read': ptr(label + '.controller'),
        'new_rate_id': 'new-rate', 'can_recover_rate_id': 'can-rate',
        'ordinary_controller_update_path': True, 'controller_matches_clock': True,
        'precise_timer_identity': True, 'no_intervening_timer_changes': True,
        'timer': {'exists': True, 'period_raw': Q, 'remaining_raw': 3 * Q // 4}, 'drain': drain()}


def payload(readings=(), rates=(), initializations=(), notifications=()):
    return {'readings': list(readings), 'rate_reads': list(rates),
            'initializations': list(initializations), 'notifications': list(notifications)}


def init_payload():
    return payload([reading('refresh14', raw=7 * Q)], initializations=[initialization()])


def notify_payload():
    return payload([reading('new14', raw=4 * Q), reading('new30', 30, Q // 2),
                    reading('can14', raw=Q), reading('can30', 30, Q)],
        [rate('new-rate', 'new14', 'new30'), rate('can-rate', 'can14', 'can30')], notifications=[notification()])


def all_groups_payload():
    value = notify_payload()
    value['readings'].append(reading('refresh14', raw=7 * Q))
    value['initializations'].append(initialization())
    return value


class IndependentSpAttributeTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:
            cls.subject, cls.package_name = load_module(MODULE_FILE)

    def evaluate(self, value, subject=None):
        out = (subject or self.subject).sp_recovery_attribute_reference(value)
        for key in UNKNOWNS:
            self.assertIsNone(out[key])
        self.assertFalse(out['events_scheduled'])
        self.assertFalse(out['hotfix_equivalence_proven'])
        for row in out['rows']:
            for key in UNKNOWNS:
                self.assertIsNone(row[key])
            expected = INIT_STAGES if row['kind'] == 'initial_slot0' else NOTIFY_STAGES
            self.assertEqual(tuple(stage['name'] for stage in row['stages']), expected)
            for stage in row['stages']:
                self.assertEqual(set(stage), {'name', 'called', 'normal', 'reference'})
        return out

    def init_result(self, value=None):
        out = self.evaluate(value or init_payload())
        self.assertTrue(out['source_valid'])
        row = next(row for row in out['rows'] if row['kind'] == 'initial_slot0')
        return row, {stage['name']: stage for stage in row['stages']}

    def notify_result(self, value=None):
        out = self.evaluate(value or notify_payload())
        self.assertTrue(out['source_valid'])
        row = next(row for row in out['rows'] if row['kind'] == 'dirty_notification')
        return row, {stage['name']: stage for stage in row['stages']}

    def test_default_ranges_are_MAXFP_and_ratio30_can_exceed_one(self):
        out = self.evaluate(payload([reading('ratio', 30, 3 * Q, dirty=True),
                                     reading('max', 14, 9223372036854775806, dirty=True)]))
        self.assertEqual([r['getter_raw_reference'] for r in out['readings']], [3 * Q, 9223372036854775806])
        self.assertEqual(out['readings'][0]['upper_raw_reference'], 9223372036854775806)

    def test_full_four_bucket_literal_ten_ONE(self):
        r = reading('combined', raw=2 * Q, dirty=True)
        r['calculation']['modifiers'] = [modifier(addition=Q, mult_delta=Q // 2, final_addition=Q // 2, final_scaler=2 * Q)]
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['getter_raw_reference'], 10 * Q)

    def test_MULT_deltas_add_but_FINALSCALER_multiplies(self):
        r = reading('two', dirty=True)
        r['calculation']['modifiers'] = [modifier('a', mult_delta=Q // 2, final_scaler=2 * Q),
                                        modifier('b', mult_delta=Q // 2, final_scaler=2 * Q)]
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['getter_raw_reference'], 8 * Q)

    def test_negative_MULT_clamps_before_final_addition_and_scaler(self):
        r = reading('negative-mult', raw=2 * Q, dirty=True)
        r['calculation']['modifiers'] = [modifier(mult_delta=-2 * Q, final_addition=Q // 2, final_scaler=2 * Q)]
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['getter_raw_reference'], Q)

    def test_negative_final_scaler_is_not_replaced_with_default(self):
        r = reading('negative-scale', dirty=True)
        r['calculation']['modifiers'] = [modifier(final_scaler=-Q)]
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['pre_clamp_raw_reference'], -Q)
        self.assertEqual(row['getter_raw_reference'], 0)

    def test_clean_independent_negative_cache_is_not_recomputed_or_clamped(self):
        r = reading('clean', raw=-Q)
        dirty = reading('unused', raw=7 * Q, dirty=True)['calculation']
        dirty['raw_read']['normal'] = False
        r['calculation'] = dirty
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['getter_raw_reference'], -Q)
        self.assertFalse(row['dirty_cleared_reference'])
        self.assertIsNone(row['cache_write_value_argument_raw_reference'])

    def test_reversed_dynamic_range_closes_lower_without_sorting(self):
        r = reading('reversed', raw=None, dirty=True)
        r['calculation']['inventory_complete'] = False
        r['calculation']['range_read'].update(override=True, lower_raw=5 * Q, upper_raw=2 * Q)
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['getter_raw_reference'], 5 * Q)

    def test_signed64_wrap_precedes_default_range_clamp(self):
        r = reading('wrap', raw=9223372036854775806, dirty=True)
        r['calculation']['modifiers'] = [modifier(addition=4)]
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['pre_clamp_raw_reference'], -9223372036854775806)
        self.assertEqual(row['getter_raw_reference'], 0)

    def test_dirty_clear_survives_later_raw_range_or_store_failure(self):
        for field in ['raw_read', 'range_read', 'cache_store_normal']:
            with self.subTest(field=field):
                r = reading('failure', dirty=True)
                if field == 'cache_store_normal': r['calculation'][field] = False
                else: r['calculation'][field]['normal'] = False
                row = self.evaluate(payload([r]))['readings'][0]
                self.assertTrue(row['dirty_cleared_reference'])
                self.assertFalse(row['normal_return_reference'])
                self.assertIsNone(row['getter_raw_reference'])

    def test_failed_enumeration_does_not_claim_dirty_cleared(self):
        r = reading('enumeration', dirty=True)
        r['calculation']['enumeration_normal'] = False
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertFalse(row['dirty_cleared_reference'])

    def test_incomplete_inventory_does_not_promote_listed_value_to_total(self):
        r = reading('incomplete', raw=2 * Q, dirty=True)
        r['calculation']['inventory_complete'] = False
        row = self.evaluate(payload([r]))['readings'][0]
        self.assertEqual(row['listed_pre_clamp_raw_reference'], 2 * Q)
        self.assertIsNone(row['getter_raw_reference'])

    def test_rate_has_independent_getter_order_and_literal_product(self):
        out = self.evaluate(notify_payload())
        row = out['rate_reads'][0]
        self.assertEqual(tuple(s['name'] for s in row['stages']), RATE_STAGES)
        self.assertEqual(row['rate_raw_reference'], 2 * Q)
        self.assertTrue(row['normal'])

    def test_zero_times_unknown_can_close_but_nonzero_unknown_cannot(self):
        for flat, expected in [(0, 0), (Q, None)]:
            with self.subTest(flat=flat):
                value = payload([reading('flat', raw=flat), reading('ratio', 30, None)], [rate('rate', 'flat', 'ratio')])
                row = self.evaluate(value)['rate_reads'][0]
                self.assertEqual(row['rate_raw_reference'], expected)
                self.assertTrue(row['normal'])

    def test_rate_second_getter_failed_or_unknown_retains_first_but_not_ratio(self):
        for flag in [False, None]:
            with self.subTest(flag=flag):
                value = notify_payload(); value['rate_reads'][0]['second_attributes_getter_normal'] = flag
                row = self.evaluate(value)['rate_reads'][0]
                stages = {s['name']: s for s in row['stages']}
                self.assertTrue(stages['flat_read']['called'])
                self.assertIs(stages['ratio_read']['called'], flag)
                self.assertIsNone(row['rate_raw_reference'])

    def test_rate_identity_or_change_link_does_not_borrow_equal_values(self):
        for field in ['same_entity', 'unchanged_to_point']:
            value = notify_payload(); value['rate_reads'][0][field] = False
            row = self.evaluate(value)['rate_reads'][0]
            self.assertIsNone(row['rate_raw_reference'])
            self.assertFalse(row['binding_qualified'])

    def test_slot_conversion_and_refresh_are_independent_values(self):
        row, stages = self.init_result()
        self.assertEqual(row['slot0_fp_argument_raw_reference'], 6442450944)
        self.assertEqual(row['refresh_reference']['getter_raw_reference'], 7 * Q)
        self.assertEqual(row['stored_prefix'], [RAW_PREFIX])
        self.assertIsNone(row['raw_value_after']); self.assertIsNone(row['cache_value_after'])
        self.assertEqual(stages['raw_encode']['reference']['argument_raw'], 6442450944)

    def test_null_attributes_guard_is_after_normal_slot_conversion(self):
        value = init_payload(); value['initializations'][0]['attributes_read']['exists'] = False
        row, stages = self.init_result(value)
        self.assertTrue(stages['single_conversion']['called'])
        self.assertTrue(stages['single_conversion']['normal'])
        self.assertEqual(row['slot0_fp_argument_raw_reference'], 6442450944)
        self.assertFalse(stages['raw_array_capture']['called'])
        self.assertEqual(row['stored_prefix'], [])

    def test_raw_array_null_or_short_still_encodes_before_guard(self):
        for exists, length in [(False, 15), (True, 14)]:
            value = init_payload(); value['initializations'][0]['raw_array_read'].update(exists=exists, length=length)
            row, stages = self.init_result(value)
            self.assertTrue(stages['raw_array_capture']['normal'])
            self.assertTrue(stages['raw_encode']['called'])
            self.assertTrue(stages['raw_encode']['normal'])
            self.assertFalse(stages['raw_store']['called'])
            self.assertEqual(row['stored_prefix'], [])

    def test_null_or_empty_increment_array_fails_before_slot(self):
        for exists, length in [(False, 1), (True, 0)]:
            value = init_payload(); value['initializations'][0]['increments_read'].update(exists=exists, length=length)
            row, stages = self.init_result(value)
            self.assertFalse(stages['slot0_read']['called'])
            self.assertIsNone(row['slot0_fp_argument_raw_reference'])

    def test_slot_negative_and_signedzero_do_not_get_clamped_before_encoder(self):
        for bits, expected in [(0xBF800000, -Q), (0x80000000, 0)]:
            value = init_payload(); value['initializations'][0]['slot0_read']['bits'] = bits
            row, stages = self.init_result(value)
            self.assertEqual(row['slot0_fp_argument_raw_reference'], expected)
            self.assertEqual(stages['raw_encode']['reference']['argument_raw'], expected)
            self.assertEqual(row['stored_prefix'], [RAW_PREFIX])

    def test_unknown_numeric_slot_can_have_normal_opaque_store_and_refresh(self):
        for bits in [None, 0x7FC00000, 0x00000001]:
            value = init_payload(); value['initializations'][0]['slot0_read']['bits'] = bits
            row, stages = self.init_result(value)
            self.assertIsNone(row['slot0_fp_argument_raw_reference'])
            self.assertTrue(stages['raw_encode']['normal'])
            self.assertEqual(row['stored_prefix'], [RAW_PREFIX])
            self.assertTrue(stages['refresh']['called'])

    def test_conversion_failure_or_unknown_stops_later_guard_and_store(self):
        for flag in [False, None]:
            value = init_payload(); value['initializations'][0]['single_conversion_normally'] = flag
            row, stages = self.init_result(value)
            self.assertIs(stages['attributes_guard']['called'], flag)
            self.assertEqual(row['stored_prefix'], [])

    def test_completed_raw_store_survives_opaque_MarkDirty_failure_or_unknown(self):
        for flag in [False, None]:
            value = init_payload(); value['initializations'][0]['mark_dirty_returns_normally'] = flag
            row, stages = self.init_result(value)
            self.assertEqual(row['stored_prefix'], [RAW_PREFIX])
            self.assertIs(stages['refresh']['called'], flag)
            self.assertIsNone(stages['mark_dirty']['reference']['partial_mask_state'])
            self.assertIsNone(stages['mark_dirty']['reference']['callback_target'])

    def test_failed_raw_store_is_not_recorded_as_completed(self):
        value = init_payload(); value['initializations'][0]['raw_store_normally'] = False
        row, stages = self.init_result(value)
        self.assertEqual(row['stored_prefix'], [])
        self.assertFalse(stages['mark_dirty']['called'])

    def test_unqualified_refresh_identity_keeps_raw_prefix_but_not_value(self):
        for flag in [False, None]:
            value = init_payload(); value['initializations'][0]['refresh_same_attributes'] = flag
            row, stages = self.init_result(value)
            self.assertEqual(row['stored_prefix'], [RAW_PREFIX])
            self.assertIsNone(row['refresh_reference'])

    def test_unknown_labels_do_not_mean_null_and_no_subscription_state_is_created(self):
        row, stages = self.init_result()
        self.assertTrue(row['normal'])
        self.assertEqual(tuple(stages), INIT_STAGES)
        self.assertNotIn('subscription', row)
        self.assertNotIn('callback_count', row)

    def test_notification_new_rate_and_canRecover_have_different_snapshots(self):
        row, stages = self.notify_result()
        request = row['clock_request']; action = request['actions'][0]
        self.assertEqual(len(request['actions']), 1)
        self.assertEqual(action['id'], 'sp282.reconfigure')
        self.assertEqual(action['rate_input_raw'], 2 * Q)
        self.assertEqual(action['can_recover_rate']['attr14_raw'], Q)
        self.assertEqual(action['can_recover_rate']['attr30_raw'], Q)
        self.assertEqual(row['clock_reference']['final_period_raw_reference'], Q // 2)
        self.assertEqual(row['clock_reference']['final_remaining_raw_reference'], Q // 4)

    def test_controller_null_is_guarded_after_new_rate_getter(self):
        value = notify_payload(); value['notifications'][0]['controller_read']['exists'] = False
        row, stages = self.notify_result(value)
        self.assertTrue(stages['new_rate']['called'])
        self.assertEqual(row['new_rate_reference']['rate_raw_reference'], 2 * Q)
        self.assertFalse(stages['controller_update']['called'])
        self.assertIsNone(row['clock_request'])

    def test_old_value_is_not_used_by_supported14_or30_body(self):
        requests = []
        for attribute, old in [(14, None), (30, -99 * Q)]:
            value = notify_payload(); value['notifications'][0].update(attribute=attribute, old_value_raw=old)
            row, stages = self.notify_result(value); requests.append(row['clock_request'])
            self.assertFalse(stages['controller_update']['reference']['old_value_used_by_ordinary_body'])
        self.assertEqual(requests[0], requests[1])

    def test_valid_timer_drains_then_independent_zero_eligibility_marks_invalid(self):
        value = notify_payload(); value['readings'][2]['decoded_cache']['raw'] = 0
        row, stages = self.notify_result(value)
        clock = row['clock_reference']; child = clock['rows'][0]
        self.assertIsNotNone(child['drain'])
        self.assertFalse(child['can_recover']['can_recover_reference'])
        self.assertEqual(clock['final_period_raw_reference'], -Q)
        self.assertEqual(clock['final_remaining_raw_reference'], -Q)

    def test_invalid_timer_ignores_prefilled_can_snapshot_and_restarts(self):
        value = notify_payload(); value['notifications'][0]['timer'].update(period_raw=-Q, remaining_raw=-Q)
        row, stages = self.notify_result(value)
        self.assertIsNotNone(row['can_recover_snapshot_reference'])
        child = row['clock_reference']['rows'][0]
        self.assertIsNone(child['drain']); self.assertIsNone(child['can_recover'])
        self.assertEqual(child['period_reset']['kind'], 'restart')
        self.assertEqual(row['clock_reference']['final_period_raw_reference'], Q // 2)
        self.assertEqual(row['clock_reference']['final_remaining_raw_reference'], Q // 2)

    def test_invalid_timer_does_not_require_eligibility_rate_ID(self):
        value = notify_payload(); value['notifications'][0].update(can_recover_rate_id=None, drain=None)
        value['notifications'][0]['timer'].update(period_raw=-Q, remaining_raw=-Q)
        row, stages = self.notify_result(value)
        self.assertIsNone(row['can_recover_snapshot_reference'])
        self.assertEqual(row['clock_reference']['final_period_raw_reference'], Q // 2)

    def test_canRecover_strict_EPS_boundary_is_not_new_rate_substitution(self):
        for raw, expected in [(42950, False), (42951, True)]:
            value = notify_payload(); value['readings'][2]['decoded_cache']['raw'] = raw
            row, stages = self.notify_result(value)
            self.assertIs(row['clock_reference']['rows'][0]['can_recover']['can_recover_reference'], expected)
            self.assertEqual(row['clock_request']['actions'][0]['rate_input_raw'], 2 * Q)

    def test_inline_ordinary_path_and_controller_identity_are_independent_qualifiers(self):
        for field, flag in [('ordinary_controller_update_path', False), ('ordinary_controller_update_path', None),
                            ('controller_matches_clock', False)]:
            value = notify_payload(); value['notifications'][0][field] = flag
            row, stages = self.notify_result(value)
            self.assertIsNone(row['clock_request'])
            self.assertIsNone(row['normal'])

    def test_timer_identity_and_no_change_flags_do_not_prove_clock_values(self):
        for field in ['precise_timer_identity', 'no_intervening_timer_changes']:
            value = notify_payload(); value['notifications'][0][field] = False
            row, stages = self.notify_result(value)
            self.assertIsNone(row['clock_reference']['final_period_raw_reference'])

    def test_independent_reads_cannot_serve_two_access_points(self):
        value = notify_payload(); value['rate_reads'][1]['flat_read_id'] = 'new14'
        with self.assertRaises((ValueError, TypeError)): self.evaluate(value)
        value = all_groups_payload(); value['initializations'][0]['refresh_read_id'] = 'new14'
        with self.assertRaises((ValueError, TypeError)): self.evaluate(value)
        value = notify_payload(); value['notifications'][0]['can_recover_rate_id'] = 'new-rate'
        with self.assertRaises((ValueError, TypeError)): self.evaluate(value)

    def test_strict_scope_rejects_HP_recipes_caller_clock_overrides_and_bad_drain(self):
        value = payload([reading('bad', 13)])
        with self.assertRaises((ValueError, TypeError)): self.evaluate(value)
        r = reading('flower', dirty=True); r['calculation']['modifiers'] = [modifier()]
        r['calculation']['modifiers'][0]['basis'] = 'flower_load'
        with self.assertRaises((ValueError, TypeError)): self.evaluate(payload([r]))
        for key in ['actions', 'rate_input_raw', 'can_recover_rate']:
            value = notify_payload(); value['notifications'][0][key] = None
            with self.assertRaises((ValueError, TypeError)): self.evaluate(value)
        for key, new in [('delta_raw', 1), ('id', 'sp282.reconfigure')]:
            value = notify_payload(); value['notifications'][0]['drain'][key] = new
            with self.assertRaises((ValueError, TypeError)): self.evaluate(value)
        value = notify_payload(); value['notifications'][0]['drain']['full_read']['exists'] = True
        with self.assertRaises((ValueError, TypeError)): self.evaluate(value)

    def test_payload_is_not_mutated_and_public_injection_is_rejected(self):
        value = all_groups_payload(); before = copy.deepcopy(value)
        self.evaluate(value); self.assertEqual(value, before)
        for key in ['source', 'data', 'evaluator']:
            with self.assertRaises(TypeError):
                self.subject.sp_recovery_attribute_reference(value, **{key: {}})

    def public_pin_paths(self):
        root = Path(self.subject.__file__).resolve().parents[1]
        packet = Path('research/p2-sp-recovery-attributes-282')
        manifest = json.loads((root / packet / 'source_manifest.json').read_bytes())
        paths = [Path(p) for p in manifest['files_sha256']]
        paths += [packet / 'source_manifest.json', packet / 'source-proof.json']
        self.assertEqual(len(paths), 31); self.assertEqual(len(set(paths)), 31)
        return root, paths

    def clone_public(self, original, paths, target):
        for rel in [*paths, Path('rouge/sp_recovery_attribute_reference.py')]:
            destination = (target / rel).resolve()
            self.assertTrue(destination.is_relative_to(target))
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original / rel, destination)
        return load_module(target / 'rouge/sp_recovery_attribute_reference.py')

    def assert_invalid_source_suppresses_all_groups(self, subject):
        self.assertFalse(subject.source_data()['valid'])
        value = self.evaluate(all_groups_payload(), subject)
        self.assertFalse(value['source_valid'])
        for row in value['readings']:
            self.assertIsNone(row['getter_raw_reference'])
            self.assertIsNone(row['cache_write_value_argument_raw_reference'])
            self.assertIsNone(row['dirty_cleared_reference'])
        for row in value['rate_reads']:
            self.assertIsNone(row['rate_raw_reference'])
        for row in value['rows']:
            self.assertEqual(row['stored_prefix'], [])
            self.assertIsNone(row['clock_request']); self.assertIsNone(row['clock_reference'])
            if row['kind'] == 'initial_slot0':
                self.assertIsNone(row['slot0_fp_argument_raw_reference'])
                self.assertIsNone(row['refresh_reference'])
            else:
                self.assertIsNone(row['new_rate_reference']); self.assertIsNone(row['can_recover_snapshot_reference'])
            for stage in row['stages']:
                self.assertIsNone(stage['reference'])

    def assert_valid_clone_executes_all_groups(self, subject):
        self.assertTrue(subject.source_data()['valid'])
        value = self.evaluate(all_groups_payload(), subject)
        self.assertTrue(value['source_valid'])
        self.assertEqual([row['normal'] for row in value['rows']], [True, True])
        self.assertEqual(value['rate_reads'][0]['rate_raw_reference'], 2 * Q)
        self.assertTrue(value['rows'][1]['clock_reference']['source_valid'])

    def test_every31_pin_byte_change_is_rechecked_after_valid_cached_execution(self):
        original, paths = self.public_pin_paths()
        before = {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths}
        for changed in paths:
            with self.subTest(changed=str(changed)), tempfile.TemporaryDirectory(prefix='sp282-public-', dir=HERE) as folder:
                target = Path(folder).resolve(); self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject, package_name = self.clone_public(original, paths, target)
                try:
                    self.assert_valid_clone_executes_all_groups(subject)
                    path = (target / changed).resolve(); self.assertTrue(path.is_relative_to(target))
                    raw = bytearray(path.read_bytes()); raw[0] ^= 1; path.write_bytes(raw)
                    self.assert_invalid_source_suppresses_all_groups(subject)
                finally: unload_package(package_name)
        self.assertEqual(before, {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths})

    def test_every31_missing_pin_is_rechecked_after_valid_cached_execution(self):
        original, paths = self.public_pin_paths()
        before = {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths}
        for missing in paths:
            with self.subTest(missing=str(missing)), tempfile.TemporaryDirectory(prefix='sp282-public-', dir=HERE) as folder:
                target = Path(folder).resolve(); self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject, package_name = self.clone_public(original, paths, target)
                try:
                    self.assert_valid_clone_executes_all_groups(subject)
                    removed = (target / missing).resolve(); self.assertTrue(removed.is_relative_to(target)); removed.unlink()
                    self.assert_invalid_source_suppresses_all_groups(subject)
                finally: unload_package(package_name)
        self.assertEqual(before, {str(p): hashlib.sha256((original / p).read_bytes()).hexdigest() for p in paths})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    IndependentSpAttributeTests.subject, IndependentSpAttributeTests.package_name = load_module(args.module_file)
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__': main()
