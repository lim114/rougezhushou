"""Literal packet vectors, source bindings and independent qualification cases.

These tests do not reproduce the multiplier algorithm as an expected-value
oracle. Native/metadata receipts and previously verified FP vectors provide
the constants; all conditions are public declarations, never game observations.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge import modifier_packet_reference as module
from rouge.mechanist_explosion_math import public_example as explosion_example

ROOT = Path(__file__).resolve().parents[1]
Q = 4294967296
HEALING_GOLD = [9380208443390, 9380208443391]
MAGIC_GOLD = [8160437248000, 8160438272000]
EXPLOSION_GOLD = [11424611891840, 11424613325439]


def one_source(family='healing'):
    payload = module.public_example(family)
    payload['relic_ids'] = payload['relic_ids'][:1]
    payload['modules'] = payload['modules'][:1]
    payload['acquisition_order'] = list(payload['relic_ids'])
    payload['application_order'] = [payload['modules'][0]['id']]
    return payload


def first_case(payload):
    return module.modifier_packet_reference(payload)['cases'][0]


def first_step(payload):
    return first_case(payload)['steps'][0]


class ModifierPacketReferenceTests(unittest.TestCase):
    def test_three_independent_healing_modules_have_two_literal_fp_results(self):
        payload = module.public_example(); before = deepcopy(payload)
        result = module.modifier_packet_reference(payload)
        self.assertTrue(result['source_valid'])
        self.assertEqual(result['known_discrete_raw_references'], HEALING_GOLD)
        self.assertEqual(result['declared_order_combination_count'], 36)
        self.assertTrue(result['all_declared_cases_numeric'])
        self.assertIsNone(result['single_declared_chain_raw_reference'])
        self.assertEqual(len(result['module_definitions']), 3)
        self.assertTrue(all(len(case['steps']) == 3 for case in result['cases']))
        self.assertEqual(payload, before)

    def test_magic_base_one_merges_three_sources_into_one_not_three_multiplications(self):
        result = module.modifier_packet_reference(module.public_example('magic'))
        self.assertEqual(result['known_discrete_raw_references'], MAGIC_GOLD)
        self.assertEqual(result['declared_order_combination_count'], 6)
        self.assertEqual(set(result['module_definitions']), {'damage:magic'})
        self.assertTrue(all(len(case['steps']) == 1 for case in result['cases']))
        self.assertEqual({case['steps'][0]['factor_raw_reference'] for case in result['cases']},
                         {8160437248, 8160438272})
        for family in ('physical', 'true'):
            with self.subTest(family=family):
                row = module.modifier_packet_reference(module.public_example(family))
                self.assertEqual(len(row['module_definitions']), 1)
        elemental = module.modifier_packet_reference(module.public_example('elemental'))
        self.assertEqual(len(elemental['module_definitions']), 2)
        self.assertEqual(elemental['known_discrete_raw_references'], [15032385536000])
        self.assertEqual(elemental['declared_order_combination_count'], 4)

    def test_source_269_explosion_return_has_distinct_created_and_entry_unchanged_gates(self):
        payload = module.public_example('magic'); explosion = explosion_example()
        payload['packet']['input'] = {'kind': 'explosion_return', 'explosion': explosion,
            'call_id': explosion['calls'][0]['id'], 'branch': 'scaled', 'value_unchanged_at_entry': True}
        result = module.modifier_packet_reference(payload)
        self.assertEqual(result['declared_entry_raw'], 6012954080000)
        self.assertEqual(result['known_discrete_raw_references'], EXPLOSION_GOLD)
        self.assertIsNone(result['explosion_base_reference']['actual_total_damage'])
        for field, value in (('modifier_exists', None), ('modifier_exists', False)):
            changed = deepcopy(payload); changed['packet'][field] = value
            self.assertEqual(module.modifier_packet_reference(changed)['known_discrete_raw_references'], [])
        for value in (False, None):
            changed = deepcopy(payload); changed['packet']['input']['value_unchanged_at_entry'] = value
            row = module.modifier_packet_reference(changed)
            self.assertIsNone(row['declared_entry_raw']); self.assertEqual(row['known_discrete_raw_references'], [])

    def test_damage_types_are_metadata_enum_values_and_masks_are_separate(self):
        proof = json.loads((ROOT / 'research/p2-modifier-packets-271/metadata-proof.json').read_text(encoding='utf8'))
        def values(name):
            record = next(row for row in proof['layouts'] if row['name'] == name)
            return {row['name']: row['default']['value'] for row in record['fields'] if row.get('default')}
        damage = values('Torappu.Battle.DamageType'); masks = values('Torappu.Battle.DamageTypeMask')
        self.assertEqual({key: damage[key] for key in ('PURE', 'HEAL', 'ELEMENT')}, {'PURE': 3, 'HEAL': 4, 'ELEMENT': 5})
        self.assertEqual({key: masks[key] for key in ('PURE', 'HEAL', 'ELEMENT')}, {'PURE': 8, 'HEAL': 16, 'ELEMENT': 32})
        self.assertEqual(values('Torappu.Battle.Modifier+DeltaType')['ADD'], 1)
        for value in (3, 4, 5, 8, 16, 32, 'TRUE'):
            payload = one_source('true'); payload['packet']['damage_type'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): module.modifier_packet_reference(payload)

    def test_add_direction_does_not_convert_a_damage_type_into_healing(self):
        payload = one_source('true'); payload['packet']['delta_type'] = 'ADD'
        row = first_step(payload)
        self.assertTrue(row['is_damage_reference']); self.assertTrue(row['type_pass_reference'])
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 10737418240000)
        payload = one_source('healing'); payload['packet']['damage_type'] = 'PHYSICAL'
        row = first_step(payload)
        self.assertFalse(row['type_pass_reference']); self.assertFalse(row['setter_called_reference'])
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 1000 * Q)

    def test_cancelled_abs_threshold_is_strict_symmetric_and_min64_is_nonzero(self):
        expected = {0: True, 42949: True, -42949: True, 42950: False, -42950: False, -(1 << 63): False}
        for raw, cancelled in expected.items():
            payload = one_source('true'); payload['packet']['input']['raw'] = raw
            payload['packet']['value_immutable'] = True
            with self.subTest(raw=raw):
                step = first_step(payload)
                self.assertEqual(step['cancelled_reference'], cancelled)
                self.assertEqual(step['setter_called_reference'], not cancelled)
                self.assertEqual(first_case(payload)['declared_chain_raw_reference'], raw)
        payload = one_source('true'); payload['packet']['delta_type'] = 'CANCELLED'
        self.assertTrue(first_step(payload)['cancelled_reference'])

    def test_cancelled_damage_early_gate_requires_hp_damage_but_cancelled_element_ep_can_run(self):
        payload = one_source('elemental'); payload['packet']['delta_type'] = 'CANCELLED'
        row = first_step(payload)
        self.assertTrue(row['is_damage_reference']); self.assertTrue(row['early_stop_reference'])
        self.assertFalse(row['setter_called_reference'])
        for target in ('EP', 'SP'):
            payload['packet']['target_type'] = target
            with self.subTest(target=target):
                row = first_step(payload)
                self.assertTrue(row['cancelled_reference']); self.assertFalse(row['is_damage_reference'])
                self.assertFalse(row['early_stop_reference']); self.assertTrue(row['setter_called_reference'])
                self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 2000 * Q)

    def test_cancelled_healing_stops_even_for_non_hp_target_and_missing_blackboard(self):
        payload = one_source('healing'); payload['packet']['delta_type'] = 'CANCELLED'
        payload['packet']['target_type'] = 'SP'; payload['modules'][0]['blackboard_available'] = False
        row = first_step(payload)
        self.assertTrue(row['early_stop_reference']); self.assertFalse(row['setter_called_reference'])
        self.assertTrue(row['normal_return_reference']); self.assertEqual(row['status'], 'skipped')
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 1000 * Q)

    def test_successful_zero_and_negative_numbers_are_not_default_one(self):
        for bits, raw in ((0x00000000, 0), (0x80000000, 0), (0xbf800000, -1000 * Q)):
            payload = one_source('healing'); state = payload['modules'][0]
            state.update(factor_basis='independent_number', float32_bits=bits)
            with self.subTest(bits=bits):
                step = first_step(payload)
                self.assertFalse(step['default_one_used_reference'])
                self.assertEqual(step['attempted_raw_reference'], raw)
                self.assertEqual(first_case(payload)['declared_chain_raw_reference'], raw)

    def test_failed_numeric_lookup_defaults_one_but_missing_object_is_exception(self):
        payload = one_source('healing'); payload['modules'][0]['number_readable'] = False
        row = first_step(payload)
        self.assertTrue(row['default_one_used_reference']); self.assertEqual(row['factor_raw_reference'], Q)
        self.assertEqual(row['attempted_raw_reference'], 1000 * Q)
        payload['modules'][0]['blackboard_available'] = False
        row = first_step(payload)
        self.assertEqual(row['status'], 'missing_blackboard_exception')
        self.assertFalse(row['normal_return_reference']); self.assertFalse(row['setter_called_reference'])
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])

    def test_immutable_value_preserves_stored_value_but_does_not_skip_read_or_multiply(self):
        payload = one_source('healing'); payload['packet']['value_immutable'] = True
        row = first_step(payload)
        self.assertTrue(row['setter_called_reference'])
        self.assertEqual(row['attempted_raw_reference'], 5153960960000)
        self.assertEqual(row['stored_raw_reference'], 1000 * Q)
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 1000 * Q)
        payload['modules'][0]['blackboard_available'] = False
        row = first_step(payload)
        self.assertFalse(row['normal_return_reference'])
        self.assertEqual(row['stored_raw_reference'], 1000 * Q)
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])

    def test_unknown_execution_and_normal_return_are_not_confused_with_retained_storage(self):
        payload = one_source('healing'); payload['packet']['value_immutable'] = True
        payload['modules'][0].update(enabled=None, blackboard_available=False)
        row = first_step(payload)
        self.assertIsNone(row['normal_return_reference'])
        self.assertEqual(row['stored_raw_reference'], 1000 * Q)
        self.assertEqual(first_case(payload)['last_stored_raw_reference'], 1000 * Q)
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])
        payload['modules'][0]['enabled'] = False
        self.assertTrue(first_step(payload)['normal_return_reference'])
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 1000 * Q)
        payload = one_source('healing'); payload['packet']['value_immutable'] = None
        self.assertEqual(first_step(payload)['attempted_raw_reference'], 5153960960000)
        self.assertIsNone(first_step(payload)['stored_raw_reference'])
        for field in ('damage_type', 'delta_type'):
            payload = one_source(); payload['packet'][field] = None
            with self.subTest(unknown_flag=field):
                self.assertIsNone(first_step(payload)['body_active_reference'])
                self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])
        # Unknown HP/SP/EP classification does not matter once cancellation is
        # explicitly false. Do not erase a source-qualified numeric subtree.
        payload = one_source('magic'); payload['packet']['target_type'] = None
        self.assertIsNone(first_step(payload)['is_damage_reference'])
        self.assertFalse(first_step(payload)['early_stop_reference'])
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 5153960960000)

    def test_exception_stops_remaining_modules_instead_of_claiming_complete_total(self):
        payload = module.public_example(); payload['acquisition_order'] = list(payload['relic_ids'])
        payload['application_order'] = [state['id'] for state in payload['modules']]
        payload['modules'][0]['blackboard_available'] = False
        case = first_case(payload)
        self.assertFalse(case['normal_return_reference'])
        self.assertTrue(all(row['status'] == 'not_called_after_unqualified_chain' for row in case['steps'][1:]))
        self.assertIsNone(case['declared_chain_raw_reference'])

    def test_ordinary_no_intervening_and_modifier_existence_are_independent_required_gates(self):
        for field in ('ordinary_native_path', 'no_intervening_changes'):
            for value in (False, None):
                payload = one_source(); payload[field] = value
                with self.subTest(field=field, value=value):
                    row = module.modifier_packet_reference(payload)
                    self.assertEqual(row['known_discrete_raw_references'], [])
                    self.assertIsNone(row['single_declared_chain_raw_reference'])
        for value in (False, None):
            payload = one_source(); payload['packet']['modifier_exists'] = value
            self.assertIsNone(first_case(payload)['normal_return_reference'])

    def test_nonempty_background_or_unknown_rounding_cannot_supply_nominal_merged_factor(self):
        for field, value in (('groups_start_empty', False), ('groups_start_empty', None), ('float_rounding', None)):
            payload = module.public_example('magic'); payload[field] = value
            with self.subTest(field=field, value=value):
                result = module.modifier_packet_reference(payload)
                self.assertEqual(result['known_discrete_raw_references'], [])
                self.assertTrue(all(case['steps'][0]['factor_raw_reference'] is None for case in result['cases']))
        payload = one_source('magic'); payload['groups_start_empty'] = False; payload['float_rounding'] = None
        payload['modules'][0].update(factor_basis='independent_number', float32_bits=0x3fc00000)
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 1500 * Q)

    def test_independent_bits_nonfinite_and_unknown_read_remain_unknown_without_invented_defaults(self):
        for bits in (None, 0x7fc00000, 0x7f800000, 0xff800000, 0x5f000000):
            payload = one_source(); payload['modules'][0].update(factor_basis='independent_number', float32_bits=bits)
            with self.subTest(bits=bits):
                step = first_step(payload)
                self.assertIsNone(step['factor_raw_reference'])
                self.assertFalse(step['default_one_used_reference'])
                self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])
        payload = one_source(); payload['modules'][0]['number_readable'] = None
        self.assertIsNone(first_step(payload)['default_one_used_reference'])
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])

    def test_schema_rejects_mixed_families_bad_orders_overrides_and_nonintegral_fp(self):
        mutations = [
            lambda p: p.update(unknown=True), lambda p: p.update(relic_ids=[]),
            lambda p: p['relic_ids'].append(p['relic_ids'][0]),
            lambda p: p.update(relic_ids=['rogue_6_relic_legacy_8']),
            lambda p: p.update(acquisition_order=[]), lambda p: p.update(application_order=['damage:magic']),
            lambda p: p.update(float_rounding='nearest'), lambda p: p.update(no_intervening_changes=1),
            lambda p: p['packet']['input'].update(raw=True), lambda p: p['packet']['input'].update(raw=1.5),
            lambda p: p['packet']['input'].update(raw=1 << 63), lambda p: p['packet'].update(delta_type='HEAL'),
            lambda p: p['packet'].update(value_immutable=1), lambda p: p['modules'][0].update(float32_bits=0x3f800000),
            lambda p: p['modules'][0].update(factor_basis='independent_number', float32_bits=True),
            lambda p: p['modules'][0].update(id='healing:missing'), lambda p: p.update(modules=[]),
        ]
        for index, mutation in enumerate(mutations):
            payload = one_source(); mutation(payload); before = deepcopy(payload)
            with self.subTest(index=index), self.assertRaises(ValueError): module.modifier_packet_reference(payload)
            self.assertEqual(payload, before)

    def test_source_binding_deep_copy_and_invalid_source_cannot_close_numeric_results(self):
        source = module.source_data(); self.assertIsNotNone(source)
        self.assertEqual(hashlib.sha256((ROOT / module.SOURCE).read_bytes()).hexdigest(), module.SOURCE_SHA256)
        for path, digest in source['source_artifacts_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)
        source['sources'][0]['name'] = 'mutated'; source['sources'].clear()
        self.assertEqual(len(module.source_data()['sources']), 12)
        with patch.object(module, '_source_data', return_value=None):
            result = module.modifier_packet_reference(module.public_example())
        self.assertFalse(result['source_valid']); self.assertEqual(result['known_discrete_raw_references'], [])
        self.assertIsNone(result['single_declared_chain_raw_reference'])

    def test_native_bytes_and_exact_buff_indices_bind_twelve_sources_without_regen_or_buildup(self):
        proof = json.loads((ROOT / 'research/p2-modifier-packets-271/native-proof.json').read_text(encoding='utf8'))
        self.assertTrue(proof['all_instruction_bytes_rechecked'])
        self.assertFalse(proof['game_dll_executed']); self.assertFalse(proof['process_memory_read'])
        self.assertEqual(len(proof['methods']), 21)
        unique = {}
        for row in proof['methods']:
            self.assertTrue(row['cfg_bounded_traversal_finished']); self.assertFalse(row['limits'])
            raw = b''.join(bytes.fromhex(i['bytes']) for i in row['instructions'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['reachable_bytes_sha256'])
            self.assertEqual(len(raw), row['reachable_instruction_bytes'])
            unique.update({i['address']: i for i in row['instructions']})
        self.assertEqual(len(unique), 1630)
        source = module.source_data(); self.assertEqual(len(source['sources']), 12)
        damage = json.loads((ROOT / 'research/p2-relic-damage-composition-current/fixed-raw-sources.json').read_text(encoding='utf8'))['selected']
        flowers = json.loads((ROOT / 'research/p2-flower-healing-composition-current/fixed-raw-sources.json').read_text(encoding='utf8'))['relics']
        for row in source['sources']:
            original = flowers[row['relic_id']]['raw_buffs'] if row['family'] == 'healing' else damage[row['relic_id']]['buffs']
            buff = original[row['source_buff_index']]
            self.assertEqual(buff['key'], row['source_buff_type'])
            self.assertEqual(next(v['valueStr'] for v in buff['blackboard'] if v['key'] == 'key'), row['prefab_key'])
            self.assertEqual(next(v['value'] for v in buff['blackboard'] if v['key'] == row['number_key']), row['parameter'])
        ice = next(row for row in source['sources'] if row['relic_id'] == 'rogue_6_relic_fight_21')
        self.assertEqual(ice['source_buff_index'], 1)
        self.assertNotEqual(ice['prefab_key'], damage[ice['relic_id']]['buffs'][0]['blackboard'][0]['valueStr'])
        self.assertTrue(all(row['number_key'] in ('heal_scale', 'damage_scale') for row in source['sources']))

    def test_literal_order_results_are_not_probabilities_actual_modifier_or_complete_hp(self):
        for family in ('physical', 'magic', 'true', 'healing', 'elemental'):
            with self.subTest(family=family):
                result = module.modifier_packet_reference(module.public_example(family))
                self.assertFalse(result['order_counts_are_probabilities']); self.assertFalse(result['events_scheduled'])
                for field in ('actual_modifier_value', 'actual_hp_loss', 'actual_healing', 'actual_complete_total',
                              'actual_order', 'actual_probability_by_order'):
                    self.assertIsNone(result[field], field)

    def test_zero_factor_closes_unknown_signed_fp_only_after_active_normal_conversion(self):
        payload = one_source('magic')
        payload['packet']['input']['raw'] = None
        payload['packet']['target_type'] = 'SP'
        payload['modules'][0].update(factor_basis='independent_number', float32_bits=0)
        self.assertEqual(first_case(payload)['declared_chain_raw_reference'], 0)
        for field, value in (('enabled', None), ('blackboard_available', None), ('blackboard_available', False)):
            changed = deepcopy(payload); changed['modules'][0][field] = value
            with self.subTest(field=field, value=value):
                self.assertIsNone(first_case(changed)['declared_chain_raw_reference'])
        payload['packet']['value_immutable'] = True
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])
        payload['packet']['input']['raw'] = 0
        payload['modules'][0]['float32_bits'] = 0x7fc00000
        self.assertIsNone(first_case(payload)['normal_return_reference'])
        self.assertIsNone(first_case(payload)['declared_chain_raw_reference'])

    def test_unknown_enabled_default_one_closes_the_same_storage_and_normal_return(self):
        payload = one_source('healing')
        payload['modules'][0].update(enabled=None, blackboard_available=True, number_readable=False)
        payload['packet']['value_immutable'] = False
        result = module.modifier_packet_reference(payload); case = result['cases'][0]; step = case['steps'][0]
        # The skip branch and the executed default-ONE branch both retain this
        # literal value normally. Unknown execution must not erase that fact.
        self.assertIsNone(step['body_active_reference'])
        self.assertEqual(step['stored_raw_reference'], 1000 * Q)
        self.assertTrue(step['normal_return_reference'])
        self.assertEqual(case['declared_chain_raw_reference'], 1000 * Q)
        self.assertEqual(result['known_discrete_raw_references'], [1000 * Q])

    def test_immutable_storage_cannot_prove_normal_conversion_or_admit_following_modules(self):
        # NaN, finite out-of-range and a half-raw-unit conversion are separate
        # counterexamples. A retained setter value does not qualify CVTT normal
        # return when the native exception-mask state is independently unknown.
        for bits in (0x7fc00000, 0x7f7fffff, 0x2f000000):
            payload = one_source('healing'); payload['packet']['value_immutable'] = True
            payload['modules'][0].update(factor_basis='independent_number', float32_bits=bits)
            with self.subTest(bits=bits):
                result = module.modifier_packet_reference(payload); case = result['cases'][0]; step = case['steps'][0]
                self.assertEqual(step['stored_raw_reference'], 1000 * Q)
                self.assertEqual(case['last_stored_raw_reference'], 1000 * Q)
                self.assertIsNone(step['normal_return_reference'])
                self.assertIsNone(step['setter_called_reference'])
                self.assertIsNone(step['node_return_reference'])
                self.assertIsNone(case['normal_return_reference'])
                self.assertIsNone(case['declared_chain_raw_reference'])
                self.assertEqual(result['known_discrete_raw_references'], [])
        payload = module.public_example('healing')
        payload['acquisition_order'] = list(payload['relic_ids'])
        payload['application_order'] = [state['id'] for state in payload['modules']]
        payload['packet']['value_immutable'] = True
        payload['modules'][0].update(factor_basis='independent_number', float32_bits=0x7fc00000)
        case = first_case(payload)
        self.assertTrue(all(row['status'] == 'not_called_after_unqualified_chain' for row in case['steps'][1:]))
        self.assertIsNone(case['declared_chain_raw_reference'])

    def test_cancelled_hp_unknown_damage_type_keeps_correlated_type_and_early_gate_skip(self):
        payload = one_source('magic')
        payload['packet'].update(delta_type='CANCELLED', target_type='HP')
        payload['modules'][0]['blackboard_available'] = False
        # Every legal concrete type skips: MAGIC has the cancellation early
        # gate; all other types fail its type filter. They are the same unknown
        # damageType, rather than two independently chosen unknown properties.
        for damage_type in ('NONE', 'PHYSICAL', 'MAGICAL', 'PURE', 'HEAL', 'ELEMENT', None):
            payload['packet']['damage_type'] = damage_type
            with self.subTest(damage_type=damage_type):
                result = module.modifier_packet_reference(payload); case = result['cases'][0]; step = case['steps'][0]
                self.assertFalse(step['body_active_reference'])
                self.assertFalse(step['setter_called_reference'])
                self.assertTrue(step['normal_return_reference'])
                self.assertEqual(step['stored_raw_reference'], 1000 * Q)
                self.assertEqual(case['declared_chain_raw_reference'], 1000 * Q)
                self.assertEqual(result['known_discrete_raw_references'], [1000 * Q])


if __name__ == '__main__':
    unittest.main()
