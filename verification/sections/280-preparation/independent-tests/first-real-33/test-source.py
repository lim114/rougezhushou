"""Independent literal controls for all16 source-bound RC pair consensus.

Golden values are explicit binary32 neighbors/ties, not a call to the candidate
core as an oracle. RC pairs are conditional alternatives, never probabilities.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
MODULE_FILE = ROOT / 'rouge/skill_cost_rounding_consensus.py'
STAGES = ('modifier_read', 'cost_decode', 'int32_to_single', 'single_operation', 'round')
UNKNOWNS = ('actual_cost_after', 'actual_sp_after', 'complete_cycle')
SCALAR_KEYS = {'operation', 'cost_int32', 'modifier_bits', 'status', 'rc_pair_scope',
    'cost_conversion_candidates', 'cases', 'possible_operation_bits', 'integer_candidates',
    'same_rc_integer_candidates', 'int32_to_single_exact', 'all_operations_exact',
    'integer_consensus_reference', 'expanded_beyond_exact_only'}
CASE_KEYS = {'conversion_rc', 'operation_rc', 'cost_single_bits', 'operation_exact',
    'mathematical_numerator', 'mathematical_denominator', 'result_bits_candidates',
    'status', 'rounded_int32_reference'}


def action(kind='rune_mul', label='case', cost=10, bits=0x3E4CCCCD):
    return {'id': label, 'kind': kind, 'ordinary_native_path': True,
        'modifier_read': {'id': label + '.modifier', 'normal': True, 'bits': bits},
        'cost_decode': {'id': label + '.decoded-cost', 'normal': True, 'value': cost},
        'conversion_normally': True, 'operation_normally': True, 'round_normally': True}


def payload(*actions):
    return {'receiver_exists': True, 'actions': list(actions)}


class IndependentConsensusTests(unittest.TestCase):
    subject = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:
            spec = importlib.util.spec_from_file_location('independent_consensus_subject_280', MODULE_FILE)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.subject = module

    def scalar(self, operation, cost, bits):
        value = self.subject.single_cost_consensus_reference(operation, cost, bits)
        self.assertEqual(set(value), SCALAR_KEYS)
        self.assertEqual(value['rc_pair_scope'], 'all16_independent_RC_pairs_conservative_superset')
        for item in value['cost_conversion_candidates']:
            self.assertEqual(set(item), {'rc', 'cost_single_bits', 'exact'})
        for case in value['cases']:
            self.assertEqual(set(case), CASE_KEYS)
        return value

    def assert_golden_matrix(self, value, converted_bits, rows_bits, rows_integers):
        self.assertEqual([r['rc'] for r in value['cost_conversion_candidates']], [0, 1, 2, 3])
        self.assertEqual([r['cost_single_bits'] for r in value['cost_conversion_candidates']], converted_bits)
        self.assertEqual(len(value['cases']), 16)
        for index, item in enumerate(value['cases']):
            conversion, operation = divmod(index, 4)
            self.assertEqual((item['conversion_rc'], item['operation_rc']), (conversion, operation))
            self.assertEqual(item['cost_single_bits'], converted_bits[conversion])
            self.assertEqual(item['result_bits_candidates'], rows_bits[conversion][operation])
            self.assertEqual(item['rounded_int32_reference'], rows_integers[conversion][operation])

    def run_action(self, item):
        out = self.subject.skill_cost_rounding_consensus(payload(item))
        self.assertEqual(set(out), {'kind', 'source', 'payload', 'rows', *UNKNOWNS})
        self.assertEqual(out['kind'], 'skill_cost_rounding_consensus')
        self.assertTrue(out['source']['valid'])
        row = out['rows'][0]
        self.assertEqual(set(row), {'id', 'kind', 'called', 'normal', 'status', 'stages',
            'consensus_reference', 'encoder_argument_reference', *UNKNOWNS})
        for key in UNKNOWNS:
            self.assertIsNone(out[key])
            self.assertIsNone(row[key])
        stages = {stage['name']: stage for stage in row['stages']}
        self.assertEqual(tuple(stages), STAGES)
        for stage in row['stages']:
            self.assertEqual(set(stage), {'name', 'called', 'normal', 'reference'})
        return row, stages

    def test_tenth_times_point_two_closes_all16_integer_two(self):
        value = self.scalar('mul', 10, 0x3E4CCCCD)
        row_bits = [[0x40000000], [0x40000000], [0x40000001], [0x40000000]]
        self.assert_golden_matrix(value, [0x41200000] * 4, [row_bits] * 4, [[2, 2, 2, 2]] * 4)
        self.assertEqual(value['integer_candidates'], [2])
        self.assertEqual(value['integer_consensus_reference'], 2)
        self.assertTrue(value['expanded_beyond_exact_only'])
        self.assertTrue(value['int32_to_single_exact'])
        self.assertFalse(value['all_operations_exact'])
        for case in value['cases']:
            self.assertEqual((case['mathematical_numerator'], case['mathematical_denominator']), (67108865, 33554432))

    def test_point_zero_five_is_zero_or_one_not_complete_value(self):
        value = self.scalar('mul', 10, 0x3D4CCCCD)
        row_bits = [[0x3F000000], [0x3F000000], [0x3F000001], [0x3F000000]]
        self.assert_golden_matrix(value, [0x41200000] * 4, [row_bits] * 4, [[0, 0, 1, 0]] * 4)
        self.assertEqual(value['integer_candidates'], [0, 1])
        self.assertIsNone(value['integer_consensus_reference'])
        self.assertFalse(value['expanded_beyond_exact_only'])

    def test_real_Single_one_point_zero_five_cost20_all21(self):
        value = self.scalar('mul', 20, 0x3F866666)
        row_bits = [[0x41A80000], [0x41A7FFFF], [0x41A80000], [0x41A7FFFF]]
        self.assert_golden_matrix(value, [0x41A00000] * 4, [row_bits] * 4, [[21, 21, 21, 21]] * 4)
        self.assertEqual(value['integer_consensus_reference'], 21)
        self.assertTrue(value['expanded_beyond_exact_only'])
        for case in value['cases']:
            self.assertEqual((case['mathematical_numerator'], case['mathematical_denominator']), (22020095, 1048576))

    def test_same_Single_one_point_zero_five_cost30_is31_or32(self):
        value = self.scalar('mul', 30, 0x3F866666)
        row_bits = [[0x41FBFFFF], [0x41FBFFFF], [0x41FC0000], [0x41FBFFFF]]
        self.assert_golden_matrix(value, [0x41F00000] * 4, [row_bits] * 4, [[31, 31, 32, 31]] * 4)
        self.assertEqual(value['integer_candidates'], [31, 32])
        self.assertIsNone(value['integer_consensus_reference'])

    def test_negative_operation_has_opposite_directed_neighbors_and_no_clamp(self):
        value = self.scalar('mul', -10, 0x3E4CCCCD)
        row_bits = [[0xC0000000], [0xC0000001], [0xC0000000], [0xC0000000]]
        self.assert_golden_matrix(value, [0xC1200000] * 4, [row_bits] * 4, [[-2, -2, -2, -2]] * 4)
        self.assertEqual(value['integer_consensus_reference'], -2)
        self.assertTrue(value['expanded_beyond_exact_only'])

    def test_negative_point_zero_five_has_minus_one_or_zero(self):
        value = self.scalar('mul', -10, 0x3D4CCCCD)
        row_bits = [[0xBF000000], [0xBF000001], [0xBF000000], [0xBF000000]]
        self.assert_golden_matrix(value, [0xC1200000] * 4, [row_bits] * 4, [[0, -1, 0, 0]] * 4)
        self.assertEqual(value['integer_candidates'], [-1, 0])
        self.assertIsNone(value['integer_consensus_reference'])

    def test_inexact_positive_integer_conversion_keeps_four_results(self):
        value = self.scalar('mul', 16777217, 0x3F800000)
        converted = [0x4B800000, 0x4B800000, 0x4B800001, 0x4B800000]
        bits = [[[x]] * 4 for x in converted]
        integers = [[16777216] * 4, [16777216] * 4, [16777218] * 4, [16777216] * 4]
        self.assert_golden_matrix(value, converted, bits, integers)
        self.assertFalse(value['int32_to_single_exact'])
        self.assertTrue(value['all_operations_exact'])
        self.assertEqual(value['integer_candidates'], [16777216, 16777218])
        self.assertIsNone(value['integer_consensus_reference'])
        self.assertEqual(value['cases'][8]['mathematical_numerator'], 16777218)

    def test_inexact_negative_integer_conversion_direction_is_signed(self):
        value = self.scalar('mul', -16777217, 0x3F800000)
        converted = [0xCB800000, 0xCB800001, 0xCB800000, 0xCB800000]
        self.assert_golden_matrix(value, converted, [[[x]] * 4 for x in converted],
            [[-16777216] * 4, [-16777218] * 4, [-16777216] * 4, [-16777216] * 4])
        self.assertEqual(value['integer_candidates'], [-16777218, -16777216])
        self.assertIsNone(value['integer_consensus_reference'])

    def test_inexact_integer_times_zero_can_close_without_signzero_guess(self):
        value = self.scalar('mul', 16777217, 0)
        converted = [0x4B800000, 0x4B800000, 0x4B800001, 0x4B800000]
        self.assert_golden_matrix(value, converted, [[[0, 2147483648]] * 4] * 4, [[0] * 4] * 4)
        self.assertEqual(value['possible_operation_bits'], [0, 2147483648])
        self.assertEqual(value['integer_consensus_reference'], 0)
        self.assertTrue(value['expanded_beyond_exact_only'])

    def test_integer_zero_conversion_is_canonical_pluszero_operation_zero_is_conservative(self):
        value = self.scalar('mul', 0, 0x80000000)
        self.assertEqual([r['cost_single_bits'] for r in value['cost_conversion_candidates']], [0, 0, 0, 0])
        for case in value['cases']:
            self.assertEqual(case['result_bits_candidates'], [0, 2147483648])
            self.assertEqual(case['rounded_int32_reference'], 0)
        self.assertEqual(value['integer_consensus_reference'], 0)
        self.assertFalse(value['expanded_beyond_exact_only'])

    def test_same_RC_diagonal_consensus_does_not_replace_independent_all16(self):
        # Conditional all16-superset contract counterexample, not proof of live cross-RC behavior.
        # The neighboring source instructions contain no explicit MXCSR change.
        value = self.scalar('mul', 16777217, 0xB2FFFFFF)
        converted = [0x4B800000, 0x4B800000, 0x4B800001, 0x4B800000]
        stable = [[0xBEFFFFFF]] * 4
        changed = [[0xBF000000], [0xBF000001], [0xBF000000], [0xBF000000]]
        self.assert_golden_matrix(value, converted, [stable, stable, changed, stable],
                                  [[0] * 4, [0] * 4, [0, -1, 0, 0], [0] * 4])
        self.assertEqual(value['same_rc_integer_candidates'], [0])
        self.assertEqual(value['integer_candidates'], [-1, 0])
        self.assertIsNone(value['integer_consensus_reference'])

    def test_partial_valid_int32_results_are_not_complete_consensus(self):
        value = self.scalar('mul', 2147483647, 0x3F800000)
        self.assertEqual(value['integer_candidates'], [2147483520])
        self.assertEqual(sum(case['rounded_int32_reference'] is None for case in value['cases']), 8)
        self.assertEqual(len(value['cases']), 16)
        self.assertIsNone(value['integer_consensus_reference'])

    def test_signed_MIN32_exact_value_not_confused_with_invalid_indefinite(self):
        value = self.scalar('mul', -2147483648, 0x3F800000)
        self.assertEqual(value['integer_consensus_reference'], -2147483648)
        self.assertTrue(value['int32_to_single_exact'])
        self.assertTrue(value['all_operations_exact'])
        self.assertFalse(value['expanded_beyond_exact_only'])

    def test_MIN32_times_minus_one_cannot_create_valid_positive_int32(self):
        value = self.scalar('mul', -2147483648, 0xBF800000)
        self.assertEqual(len(value['cases']), 16)
        self.assertEqual(value['integer_candidates'], [])
        self.assertTrue(all(case['rounded_int32_reference'] is None for case in value['cases']))
        self.assertIsNone(value['integer_consensus_reference'])

    def test_finite_operation_overflow_candidates_are_not_dropped(self):
        value = self.scalar('mul', 3, 0x7F7FFFFF)
        self.assertEqual(len(value['cases']), 16)
        self.assertEqual(value['integer_candidates'], [])
        self.assertTrue(all(case['rounded_int32_reference'] is None for case in value['cases']))
        self.assertIsNone(value['integer_consensus_reference'])

    def test_nonfinite_and_subnormal_modifiers_keep_known_conversion_but_no_cases(self):
        for bits in [0x7FC00000, 0x7F800000, 0xFF800000, 0x00000001, 0x807FFFFF, None]:
            with self.subTest(bits=bits):
                value = self.scalar('mul', 3, bits)
                self.assertEqual(len(value['cost_conversion_candidates']), 4)
                self.assertEqual(value['cases'], [])
                self.assertIsNone(value['integer_consensus_reference'])

    def test_unknown_cost_does_not_invent_conversion_or_full_candidates(self):
        value = self.scalar('mul', None, 0x3F800000)
        self.assertEqual(value['cost_conversion_candidates'], [])
        self.assertEqual(value['cases'], [])
        self.assertIsNone(value['integer_consensus_reference'])

    def test_exact_half_even_parity_on_both_signs_remains_old_exact_domain(self):
        for operation, cost, bits, expected in [('mul', 3, 0x3FC00000, 4), ('mul', 5, 0x3FC00000, 8),
                ('mul', -3, 0x3FC00000, -4), ('mul', -5, 0x3FC00000, -8),
                ('add', 4, 0x3F000000, 4), ('add', 5, 0x3F000000, 6),
                ('add', -4, 0xBF000000, -4), ('add', -5, 0xBF000000, -6)]:
            with self.subTest(operation=operation, cost=cost):
                value = self.scalar(operation, cost, bits)
                self.assertEqual(value['integer_consensus_reference'], expected)
                self.assertFalse(value['expanded_beyond_exact_only'])

    def test_small_normal_values_round_to_zero_without_Double_RC_assumption(self):
        for bits in [0x00800000, 0x80800000]:
            with self.subTest(bits=bits):
                value = self.scalar('mul', 1, bits)
                self.assertEqual(value['integer_consensus_reference'], 0)
                self.assertEqual(len(value['cases']), 16)

    def test_exact_large_integer_outside_two_power24_is_supported(self):
        value = self.scalar('mul', 1073741824, 0x3F000000)
        self.assertEqual(value['integer_consensus_reference'], 536870912)
        self.assertTrue(value['int32_to_single_exact'])
        self.assertFalse(value['expanded_beyond_exact_only'])

    def test_scalar_typed_values_and_operation_rejected(self):
        for bad in [True, False, 1.0, 2147483648, -2147483649]:
            with self.assertRaises((ValueError, TypeError)):
                self.subject.single_cost_consensus_reference('mul', bad, 0)
        for bits in [True, -1, 4294967296, 1.0]:
            with self.assertRaises((ValueError, TypeError)):
                self.subject.single_cost_consensus_reference('mul', 1, bits)
        with self.assertRaises((ValueError, TypeError)):
            self.subject.single_cost_consensus_reference('nearest_only', 1, 0)

    def test_three_source_kinds_have_only_numeric_prefix_stages(self):
        for kind in ['rune_add', 'rune_mul', 'relic_mul']:
            with self.subTest(kind=kind):
                row, stages = self.run_action(action(kind))
                self.assertTrue(row['normal'])
                self.assertTrue(all(stage['normal'] is True for stage in stages.values()))
                self.assertNotIn('encode', stages)
                self.assertNotIn('store', stages)

    def test_closed_number_is_conditional_encoder_argument_only(self):
        row, stages = self.run_action(action())
        self.assertEqual(row['encoder_argument_reference'], 2)
        self.assertEqual(row['consensus_reference']['integer_consensus_reference'], 2)
        self.assertTrue(stages['round']['normal'])

    def test_divergent_reference_still_has_normal_independent_operation_facts(self):
        row, stages = self.run_action(action(bits=0x3D4CCCCD))
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertEqual(row['consensus_reference']['integer_candidates'], [0, 1])
        self.assertTrue(row['normal'])
        for stage in stages.values():
            self.assertTrue(stage['called'])

    def test_unknown_values_do_not_invent_failure_or_skip_normal_numeric_prefix(self):
        for cost, bits in [(None, 0x3F800000), (3, None), (3, 0x7FC00000)]:
            with self.subTest(cost=cost, bits=bits):
                row, stages = self.run_action(action(cost=cost, bits=bits))
                self.assertIsNone(row['encoder_argument_reference'])
                self.assertTrue(row['normal'])
                for stage in stages.values():
                    self.assertTrue(stage['called'])
                    self.assertTrue(stage['normal'])

    def test_failed_normality_skips_only_later_stages(self):
        for field, stage in [('conversion_normally', 'int32_to_single'),
                             ('operation_normally', 'single_operation'), ('round_normally', 'round')]:
            with self.subTest(field=field):
                item = action()
                item[field] = False
                row, stages = self.run_action(item)
                self.assertFalse(row['normal'])
                self.assertTrue(stages[stage]['called'])
                self.assertFalse(stages[stage]['normal'])
                for later in STAGES[STAGES.index(stage) + 1:]:
                    self.assertFalse(stages[later]['called'])
                self.assertIsNone(row['encoder_argument_reference'])

    def test_unknown_normality_keeps_later_calls_unknown(self):
        for field, stage in [('conversion_normally', 'int32_to_single'),
                             ('operation_normally', 'single_operation'), ('round_normally', 'round')]:
            with self.subTest(field=field):
                item = action()
                item[field] = None
                row, stages = self.run_action(item)
                self.assertIsNone(row['normal'])
                for later in STAGES[STAGES.index(stage) + 1:]:
                    self.assertIsNone(stages[later]['called'])
                self.assertIsNone(row['encoder_argument_reference'])

    def test_failed_or_unknown_operand_read_controls_only_reached_prefix(self):
        for flag, expected in [(False, False), (None, None)]:
            with self.subTest(flag=flag):
                item = action()
                item['modifier_read']['normal'] = flag
                row, stages = self.run_action(item)
                self.assertIs(stages['cost_decode']['called'], expected)
                self.assertIsNone(row['encoder_argument_reference'])

    def test_no_previous_action_cost_propagation_or_combined_round(self):
        out = self.subject.skill_cost_rounding_consensus(payload(action(label='one', cost=10),
            action(label='two', cost=101, bits=0x3F000000)))
        self.assertEqual([row['encoder_argument_reference'] for row in out['rows']], [2, 50])
        self.assertIsNone(out['actual_cost_after'])

    def test_unqualified_native_or_receiver_does_not_claim_conditional_number(self):
        for route in [False, None]:
            with self.subTest(route=route):
                item = action()
                item['ordinary_native_path'] = route
                row, stages = self.run_action(item)
                self.assertIsNone(row['encoder_argument_reference'])
        for exists in [False, None]:
            value = payload(action())
            value['receiver_exists'] = exists
            out = self.subject.skill_cost_rounding_consensus(value)
            self.assertIsNone(out['rows'][0]['encoder_argument_reference'])

    def test_no_RC_selection_or_public_source_injection_and_duplicate_ids(self):
        item = action()
        item['rc'] = 0
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_cost_rounding_consensus(payload(item))
        with self.assertRaises(TypeError):
            self.subject.skill_cost_rounding_consensus(payload(action()), data={})
        one, two = action(label='one'), action(label='two')
        two['cost_decode']['id'] = one['modifier_read']['id']
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_cost_rounding_consensus(payload(one, two))

    def assert_invalid_source_has_no_references(self):
        self.assertFalse(self.subject.source_data()['valid'])
        self.assertIsNone(self.subject.single_cost_consensus_reference('mul', 10, 0x3E4CCCCD))
        out = self.subject.skill_cost_rounding_consensus(payload(action('rune_add', 'add'),
            action('rune_mul', 'mul'), action('relic_mul', 'relic')))
        self.assertFalse(out['source']['valid'])
        for row in out['rows']:
            self.assertIsNone(row['consensus_reference'])
            self.assertIsNone(row['encoder_argument_reference'])
            for stage in row['stages']:
                self.assertIsNone(stage['reference'])
            for key in UNKNOWNS:
                self.assertIsNone(row[key])
        attempted = payload(action())
        attempted['source'] = {'valid': True}
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_cost_rounding_consensus(attempted)

    def test_source_byte_mutation_blocks_all_numeric_references(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json', *json.loads((original / 'source_manifest.json').read_bytes())['support_files_sha256'])
        files = tuple(p for p in original.iterdir() if p.is_file())
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for changed in names:
            with self.subTest(changed=changed), tempfile.TemporaryDirectory(prefix='rouge280-public-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                for item in files:
                    shutil.copyfile(item, target / item.name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assertTrue(self.subject.source_data()['valid'])
                    raw = bytearray((target / changed).read_bytes())
                    raw[0] ^= 1
                    (target / changed).write_bytes(raw)
                    self.assert_invalid_source_has_no_references()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})

    def test_missing_source_files_block_all_numeric_references(self):
        original = Path(self.subject.SOURCE_DIRECTORY)
        names = ('source-proof.json', 'source_manifest.json', *json.loads((original / 'source_manifest.json').read_bytes())['support_files_sha256'])
        files = tuple(p for p in original.iterdir() if p.is_file())
        before = {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for missing in names:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory(prefix='rouge280-public-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                for item in files:
                    shutil.copyfile(item, target / item.name)
                with patch.object(self.subject, 'SOURCE_DIRECTORY', target):
                    self.assertTrue(self.subject.source_data()['valid'])
                    removed = (target / missing).resolve()
                    self.assertTrue(removed.is_relative_to(target))
                    removed.unlink()
                    self.assert_invalid_source_has_no_references()
        self.assertEqual(before, {name: hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    spec = importlib.util.spec_from_file_location('independent_consensus_subject_280', args.module_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    IndependentConsensusTests.subject = module
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__':
    main()
