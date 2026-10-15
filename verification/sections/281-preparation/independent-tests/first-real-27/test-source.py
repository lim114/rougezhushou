"""Independent workflow controls for the fixed 281 five-kind composition.

Numerical goldens are literals; old public278 is a comparison contract only for
unchanged behavior. No caller evaluator, live state, game execution or RC choice.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
MODULE_FILE = ROOT / 'rouge/skill_data_cost_consensus_reference.py'
LEGACY_SHA = '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a'
CONSENSUS_SHA = '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77'
ACTUAL = ('actual_cost_after', 'actual_sp_after', 'complete_cycle')
SINGLE_STAGES = ('owner_read', 'character_data_read', 'skill_data_read', 'blackboard_read',
    'modifier_read', 'sp_data_read', 'cost_copy', 'cost_decode', 'single_conversion',
    'single_arithmetic', 'round', 'encode', 'store')


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ptr(label, identity='public-instance', exists=True, normal=True):
    return {'id': label, 'normal': normal, 'exists': exists, 'identity': identity}


def integer(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def boolean(label, value, normal=True):
    return {'id': label, 'normal': normal, 'value': value}


def single_action(kind='rune_mul', label='single', cost=10, bits=0x3E4CCCCD):
    item = {'id': label, 'kind': kind, 'ordinary_native_path': True,
        'owner_read': ptr(label + '.owner', 'single-owner'),
        'character_data_read': ptr(label + '.character', 'character-data'),
        'skill_data_read': ptr(label + '.skill', 'skill-data'),
        'blackboard_read': ptr(label + '.blackboard', 'blackboard'),
        'sp_data_read': ptr(label + '.spdata', 'first-sp-data'),
        'modifier_read': {'id': label + '.modifier', 'normal': True, 'bits': bits},
        'cost_decode': integer(label + '.decoded', cost), 'cost_copy_normally': True,
        'single_conversion_normally': True, 'single_arithmetic_normally': True,
        'round_normally': True, 'encode_normally': True, 'store_normally': True,
        'encoded_payload_identity': 'opaque-single-payload'}
    if kind != 'relic_mul':
        item['modifier_read']['found'] = True
    return item


def scale_action(label='scale'):
    return {'id': label, 'kind': 'scale_cost', 'ordinary_native_path': True,
        'first_data_read': ptr(label + '.data1', 'data-one'),
        'first_sp_data_read': ptr(label + '.spdata1', 'spdata-one'),
        'owner_read': ptr(label + '.owner', 'later-owner'),
        'second_data_read': ptr(label + '.data2', 'data-two'),
        'cost_decode': integer(label + '.decoded', 2147483647),
        'scale_read': integer(label + '.scale', 2), 'cost_copy_normally': True,
        'encode_normally': True, 'store_normally': True, 'update_normally': True,
        'encoded_payload_identity': 'opaque-scale', 'update_sp_data_identity': 'spdata-two'}


def replace_action(label='replace'):
    return {'id': label, 'kind': 'replace_cost', 'ordinary_native_path': True, 'new_cost': -7,
        'first_data_read': ptr(label + '.data1', 'data-one'),
        'first_sp_data_read': ptr(label + '.spdata1', 'spdata-one'),
        'second_data_read': ptr(label + '.data2', 'data-two'),
        'second_sp_data_read': ptr(label + '.spdata2', 'spdata-two'),
        'first_owner_read': ptr(label + '.owner1', 'truth-owner'),
        'second_owner_read': ptr(label + '.owner2', 'update-owner'),
        'third_data_read': ptr(label + '.data3', 'data-three'),
        'modify_type_read': boolean(label + '.modify', True),
        'type_value_read': integer(label + '.type', 6),
        'unity_truth_read': boolean(label + '.truth', True),
        'encode_normally': True, 'store_normally': True, 'type_store_normally': True,
        'update_normally': True, 'encoded_payload_identity': 'opaque-replace',
        'update_sp_data_identity': 'spdata-three'}


def payload(*items):
    return {'receiver_exists': True, 'actions': list(items)}


def prefix(identity='opaque-single-payload'):
    return {'field': 'spCost', 'byte_count': 20, 'payload_identity': identity, 'decoded_value': None}


class IndependentWorkflowConsensusTests(unittest.TestCase):
    subject = None
    legacy = None

    @classmethod
    def setUpClass(cls):
        if cls.subject is None:
            cls.subject = load_module(MODULE_FILE, 'independent_281_subject')
        if cls.legacy is None:
            path = Path(cls.subject.__file__).resolve().parent / 'skill_data_cost_reference.py'
            assert hashlib.sha256(path.read_bytes()).hexdigest() == LEGACY_SHA
            cls.legacy = load_module(path, 'independent_281_legacy_comparison')

    def run_action(self, item):
        value = self.subject.skill_data_cost_consensus_reference(payload(item))
        self.assertEqual(set(value), {'kind', 'source', 'payload', 'rows', *ACTUAL})
        self.assertEqual(value['kind'], 'skill_data_cost_consensus_reference')
        self.assertTrue(value['source']['valid'])
        row = value['rows'][0]
        for key in ACTUAL:
            self.assertIsNone(value[key])
            self.assertIsNone(row[key])
        stages = {stage['name']: stage for stage in row['stages']}
        if item['kind'] in ('rune_add', 'rune_mul', 'relic_mul'):
            self.assertEqual(tuple(stages), SINGLE_STAGES)
            self.assertIsNone(row['update_arguments'])
        for stage in row['stages']:
            self.assertEqual(set(stage), {'name', 'called', 'normal', 'reference'})
        return row, stages

    def test_bound_source_counts_are_reuse32_not_sum41_or_new_fresh(self):
        source = self.subject.source_data()
        self.assertTrue(source['valid'])
        self.assertEqual(source['method_count'], 32)
        self.assertEqual(source['byte_span_count'], 4034)
        self.assertEqual(set(source['components']), {'legacy', 'consensus'})
        self.assertTrue(all(component['valid'] for component in source['components'].values()))

    def test_three_single_routes_reach_consensus_encoder_and_opaque_store(self):
        for kind, expected in [('rune_mul', 2), ('relic_mul', 2), ('rune_add', 10)]:
            with self.subTest(kind=kind):
                row, stages = self.run_action(single_action(kind))
                self.assertEqual(row['calculation_route'], 'single_consensus_numeric_tail')
                self.assertEqual(row['encoder_argument_reference'], expected)
                self.assertEqual(row['stored_prefixes'], [prefix()])
                self.assertTrue(row['normal'])
                self.assertEqual(stages['encode']['reference'], {'argument': expected,
                    'argument_known': True, 'argument_candidates': [expected], 'returned_payload': None})

    def test_20_and30_true_Single_one_point_zero_five_qualification(self):
        for cost, expected, candidates in [(20, 21, [21]), (30, None, [31, 32])]:
            with self.subTest(cost=cost):
                row, stages = self.run_action(single_action(cost=cost, bits=0x3F866666))
                self.assertEqual(row['encoder_argument_reference'], expected)
                self.assertEqual(row['consensus_reference']['integer_candidates'], candidates)
                self.assertEqual(row['stored_prefixes'], [prefix()])

    def test_divergent_zero_or_one_still_can_encode_and_store_opaque(self):
        row, stages = self.run_action(single_action(bits=0x3D4CCCCD))
        self.assertTrue(row['normal'])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertEqual(stages['encode']['reference'], {'argument': None, 'argument_known': False,
            'argument_candidates': [0, 1], 'returned_payload': None})
        self.assertEqual(row['stored_prefixes'], [prefix()])
        self.assertTrue(stages['store']['normal'])

    def test_all16_superset_counterexample_not_diagonal_or_physical_RC_claim(self):
        row, stages = self.run_action(single_action(cost=16777217, bits=0xB2FFFFFF))
        self.assertEqual(row['consensus_reference']['same_rc_integer_candidates'], [0])
        self.assertEqual(row['consensus_reference']['integer_candidates'], [-1, 0])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertEqual(row['stored_prefixes'], [prefix()])

    def test_negative_consensus_is_not_clamped(self):
        row, stages = self.run_action(single_action(cost=-10))
        self.assertEqual(row['encoder_argument_reference'], -2)
        self.assertEqual(row['stored_prefixes'], [prefix()])

    def test_unknown_and_unsupported_values_keep_normal_opaque_chain(self):
        for cost, bits in [(None, 0x3F800000), (3, None), (3, 0x7FC00000), (1, 0x00000001)]:
            with self.subTest(cost=cost, bits=bits):
                row, stages = self.run_action(single_action(cost=cost, bits=bits))
                self.assertTrue(row['normal'])
                self.assertIsNone(row['encoder_argument_reference'])
                self.assertEqual(row['stored_prefixes'], [prefix()])
                self.assertFalse(stages['encode']['reference']['argument_known'])
                for name in SINGLE_STAGES[8:]:
                    self.assertTrue(stages[name]['called'])
                    self.assertTrue(stages[name]['normal'])

    def test_partial_valid_integer_candidates_do_not_become_known_argument(self):
        row, stages = self.run_action(single_action(cost=2147483647, bits=0x3F800000))
        self.assertEqual(row['consensus_reference']['integer_candidates'], [2147483520])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertFalse(stages['encode']['reference']['argument_known'])
        self.assertEqual(row['stored_prefixes'], [prefix()])

    def test_no_qualified_integer_before_normal_round(self):
        item = single_action()
        item['round_normally'] = None
        row, stages = self.run_action(item)
        self.assertIsNone(row['consensus_reference'])
        self.assertIsNone(row['encoder_argument_reference'])
        self.assertNotIn('integer_consensus_reference', stages['single_arithmetic']['reference'])
        self.assertIsNone(stages['encode']['called'])

    def test_numeric_failure_false_and_unknown_keep_distinct_future(self):
        for flag, expected in [(False, False), (None, None)]:
            for field, name in [('single_conversion_normally', 'single_conversion'),
                                ('single_arithmetic_normally', 'single_arithmetic'), ('round_normally', 'round')]:
                with self.subTest(flag=flag, field=field):
                    item = single_action()
                    item[field] = flag
                    row, stages = self.run_action(item)
                    self.assertIs(row['normal'], flag)
                    self.assertIsNone(row['encoder_argument_reference'])
                    self.assertEqual(row['stored_prefixes'], [])
                    for later in SINGLE_STAGES[SINGLE_STAGES.index(name) + 1:]:
                        self.assertIs(stages[later]['called'], expected)

    def test_encoder_failure_or_unknown_does_not_claim_store(self):
        for flag, expected in [(False, False), (None, None)]:
            with self.subTest(flag=flag):
                item = single_action()
                item['encode_normally'] = flag
                row, stages = self.run_action(item)
                self.assertEqual(row['encoder_argument_reference'], 2)
                self.assertEqual(row['stored_prefixes'], [])
                self.assertIs(stages['store']['called'], expected)

    def test_store_failed_or_unknown_does_not_record_completed_write(self):
        for flag in [False, None]:
            with self.subTest(flag=flag):
                item = single_action()
                item['store_normally'] = flag
                row, stages = self.run_action(item)
                self.assertEqual(row['encoder_argument_reference'], 2)
                self.assertEqual(row['stored_prefixes'], [])
                self.assertIs(stages['store']['normal'], flag)

    def test_no_skill_normal_return_does_not_rebuild_tail(self):
        item = single_action()
        item['skill_data_read']['exists'] = False
        row, stages = self.run_action(item)
        self.assertTrue(row['normal'])
        self.assertIsNone(row['consensus_reference'])
        self.assertEqual(row['stored_prefixes'], [])
        for name in SINGLE_STAGES[3:]:
            self.assertFalse(stages[name]['called'])

    def test_Rune_found_false_or_unknown_are_not_numerical_unknown(self):
        for found, expected in [(False, False), (None, None)]:
            with self.subTest(found=found):
                item = single_action()
                item['modifier_read']['found'] = found
                row, stages = self.run_action(item)
                self.assertIs(stages['cost_decode']['called'], expected)
                self.assertIsNone(row['consensus_reference'])
                self.assertEqual(row['stored_prefixes'], [])

    def test_prelude_read_failure_or_unknown_prevents_new_tail(self):
        for flag, expected in [(False, False), (None, None)]:
            with self.subTest(flag=flag):
                item = single_action()
                item['cost_decode']['normal'] = flag
                row, stages = self.run_action(item)
                self.assertIs(stages['single_conversion']['called'], expected)
                self.assertIsNone(row['consensus_reference'])
                self.assertEqual(row['stored_prefixes'], [])

    def test_unknown_pointer_existence_not_unknown_identity_controls_prelude(self):
        item = single_action()
        item['owner_read']['identity'] = None
        row, stages = self.run_action(item)
        self.assertEqual(row['encoder_argument_reference'], 2)
        item['owner_read']['exists'] = None
        row, stages = self.run_action(item)
        self.assertIsNone(stages['character_data_read']['called'])
        self.assertIsNone(row['consensus_reference'])

    def test_missing_sp_data_fails_before_decode_not_store_only(self):
        item = single_action()
        item['sp_data_read']['exists'] = False
        row, stages = self.run_action(item)
        self.assertFalse(row['normal'])
        self.assertFalse(stages['cost_decode']['called'])
        self.assertFalse(stages['encode']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_scale_and_replace_original_public_fields_are_bytewise_equal_values(self):
        for item in [scale_action(), replace_action()]:
            with self.subTest(kind=item['kind']):
                old = self.legacy.skill_data_cost_reference(payload(item))['rows'][0]
                row, stages = self.run_action(item)
                self.assertEqual(row['calculation_route'], 'legacy_non_single_reference')
                self.assertIsNone(row['consensus_reference'])
                stripped = {k: v for k, v in row.items() if k not in ('calculation_route', 'consensus_reference')}
                self.assertEqual(stripped, old)

    def test_nonSingle_fail_unknown_and_prefix_cases_match_original_full_result(self):
        variants = []
        one = scale_action(); one['owner_read']['exists'] = False; variants.append(one)
        one = scale_action(); one['second_data_read']['normal'] = None; variants.append(one)
        one = scale_action(); one['store_normally'] = False; variants.append(one)
        one = replace_action(); one['first_sp_data_read']['exists'] = False; variants.append(one)
        one = replace_action(); one['unity_truth_read']['value'] = False; variants.append(one)
        one = replace_action(); one['second_owner_read']['exists'] = False; variants.append(one)
        one = replace_action(); one['type_value_read']['value'] = None; variants.append(one)
        one = replace_action(); one['type_store_normally'] = False; variants.append(one)
        for item in variants:
            with self.subTest(item=item):
                old = self.legacy.skill_data_cost_reference(payload(item))['rows'][0]
                row, stages = self.run_action(item)
                stripped = {k: v for k, v in row.items() if k not in ('calculation_route', 'consensus_reference')}
                self.assertEqual(stripped, old)

    def test_scale_owner_null_keeps_second_data_read_and_cost_prefix(self):
        item = scale_action()
        item['owner_read']['exists'] = False
        row, stages = self.run_action(item)
        self.assertTrue(stages['second_data_read']['called'])
        self.assertFalse(stages['update']['called'])
        self.assertEqual(row['stored_prefixes'], [prefix('opaque-scale')])

    def test_replace_encoder_precedes_spdata_null_and_keeps_no_write(self):
        item = replace_action()
        item['first_sp_data_read']['exists'] = False
        row, stages = self.run_action(item)
        self.assertTrue(stages['encode']['called'])
        self.assertTrue(stages['first_sp_data_check']['normal'])
        self.assertFalse(stages['store']['called'])
        self.assertEqual(row['stored_prefixes'], [])

    def test_current_inputs_and_previous_decoded_values_are_not_mutated(self):
        one = single_action(label='one')
        two = single_action(label='two', cost=101, bits=0x3F000000)
        value = payload(one, two)
        before = copy.deepcopy(value)
        out = self.subject.skill_data_cost_consensus_reference(value)
        self.assertEqual(value, before)
        self.assertEqual([r['encoder_argument_reference'] for r in out['rows']], [2, 50])

    def test_original278_default_public_result_and_core_bytes_unchanged(self):
        path = Path(self.subject.__file__).resolve().parent / 'skill_data_cost_reference.py'
        before_bytes = path.read_bytes()
        original_input = self.legacy.public_example()
        before = json.dumps(self.legacy.skill_data_cost_reference(original_input), sort_keys=True)
        self.subject.skill_data_cost_consensus_reference(self.subject.public_example())
        self.subject.skill_data_cost_consensus_reference(payload(single_action()))
        after = json.dumps(self.legacy.skill_data_cost_reference(original_input), sort_keys=True)
        self.assertEqual(before, after)
        self.assertEqual(path.read_bytes(), before_bytes)
        self.assertEqual(hashlib.sha256(before_bytes).hexdigest(), LEGACY_SHA)

    def test_unqualified_native_and_receiver_do_not_invent_tail(self):
        for normal in [False, None]:
            with self.subTest(normal=normal):
                item = single_action()
                item['ordinary_native_path'] = normal
                row, stages = self.run_action(item)
                self.assertIsNone(row['encoder_argument_reference'])
                self.assertEqual(row['stored_prefixes'], [])
        for exists in [False, None]:
            value = payload(single_action())
            value['receiver_exists'] = exists
            out = self.subject.skill_data_cost_consensus_reference(value)
            self.assertIsNone(out['rows'][0]['encoder_argument_reference'])

    def test_strict_keys_IDs_and_no_public_evaluator_source_or_mode(self):
        bomb_calls = []
        def bomb(*args, **kwargs):
            bomb_calls.append(True)
            raise AssertionError('must not be called')
        for key, value in [('evaluator', bomb), ('source', {'valid': True}), ('mode', 'nearest'), ('rc', 0)]:
            item = single_action()
            item[key] = value
            with self.assertRaises((ValueError, TypeError)):
                self.subject.skill_data_cost_consensus_reference(payload(item))
        with self.assertRaises(TypeError):
            self.subject.skill_data_cost_consensus_reference(payload(single_action()), evaluator=bomb)
        with self.assertRaises(TypeError):
            self.subject.skill_data_cost_consensus_reference(payload(single_action()), data={})
        self.assertEqual(bomb_calls, [])
        one, two = single_action(label='one'), single_action(label='two')
        two['cost_decode']['id'] = one['modifier_read']['id']
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_data_cost_consensus_reference(payload(one, two))
        item = single_action(); item['cost_decode']['value'] = True
        with self.assertRaises((ValueError, TypeError)):
            self.subject.skill_data_cost_consensus_reference(payload(item))

    def pinned_relative_files(self):
        root = Path(self.subject.__file__).resolve().parents[1]
        packet = root / 'research/p2-skill-data-cost-consensus-281'
        manifest = json.loads((packet / 'source_manifest.json').read_bytes())
        links = json.loads((packet / 'source-links.json').read_bytes())
        names = [Path('rouge/skill_data_cost_reference.py'), Path('rouge/skill_cost_rounding_consensus.py'),
            Path('research/p2-skill-data-cost-consensus-281/source_manifest.json'),
            Path('research/p2-skill-data-cost-consensus-281/source-links.json')]
        names += [Path('research/p2-skill-data-cost-consensus-281') / name for name in manifest['support_files_sha256']]
        for component in links['components'].values():
            names += [Path('research') / component['source_directory'] / name for name in component['source_files_sha256']]
        self.assertEqual(len(names), 25)
        self.assertEqual(len(set(names)), 25)
        return root, names

    def clone_public_dependency_tree(self, original, target):
        (target / 'rouge').mkdir()
        for filename in ['skill_data_cost_consensus_reference.py', 'skill_data_cost_reference.py', 'skill_cost_rounding_consensus.py']:
            shutil.copyfile(original / 'rouge' / filename, target / 'rouge' / filename)
        for name in ['p2-skill-data-cost-278', 'p2-cost-rounding-consensus-280', 'p2-skill-data-cost-consensus-281']:
            source = original / 'research' / name
            destination = target / 'research' / name
            destination.mkdir(parents=True)
            for item in source.iterdir():
                self.assertTrue(item.is_file())
                shutil.copyfile(item, destination / item.name)
        return load_module(target / 'rouge/skill_data_cost_consensus_reference.py', 'independent_281_isolated_source')

    def assert_invalid_source_blocks_all_five_kinds(self, subject):
        self.assertFalse(subject.source_data()['valid'])
        value = subject.skill_data_cost_consensus_reference(payload(single_action('rune_add', 'add'),
            single_action('rune_mul', 'mul'), single_action('relic_mul', 'relic'), scale_action(), replace_action()))
        self.assertFalse(value['source']['valid'])
        for row in value['rows']:
            self.assertEqual(row['calculation_route'], 'source_unqualified')
            for key in ['arithmetic_reference', 'encoder_argument_reference', 'consensus_reference', 'update_arguments', *ACTUAL]:
                self.assertIsNone(row[key])
            self.assertEqual(row['stored_prefixes'], [])
            for stage in row['stages']:
                self.assertIsNone(stage['reference'])
        with self.assertRaises(TypeError):
            subject.skill_data_cost_consensus_reference(payload(single_action()), source={'valid': True})

    def test_each_of25_dependency_and_source_pins_one_byte_change_blocks_results(self):
        original, names = self.pinned_relative_files()
        before = {str(name): hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for changed in names:
            with self.subTest(changed=str(changed)), tempfile.TemporaryDirectory(prefix='rouge281-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject = self.clone_public_dependency_tree(original, target)
                self.assertTrue(subject.source_data()['valid'])
                path = (target / changed).resolve()
                self.assertTrue(path.is_relative_to(target))
                raw = bytearray(path.read_bytes()); raw[0] ^= 1; path.write_bytes(raw)
                self.assert_invalid_source_blocks_all_five_kinds(subject)
        self.assertEqual(before, {str(name): hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})

    def test_each_of25_missing_dependency_and_source_pins_blocks_results(self):
        original, names = self.pinned_relative_files()
        before = {str(name): hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names}
        for missing in names:
            with self.subTest(missing=str(missing)), tempfile.TemporaryDirectory(prefix='rouge281-source-', dir=HERE) as folder:
                target = Path(folder).resolve()
                self.assertTrue(target.is_relative_to(HERE.resolve()))
                subject = self.clone_public_dependency_tree(original, target)
                self.assertTrue(subject.source_data()['valid'])
                removed = (target / missing).resolve()
                self.assertTrue(removed.is_relative_to(target))
                removed.unlink()
                self.assert_invalid_source_blocks_all_five_kinds(subject)
        self.assertEqual(before, {str(name): hashlib.sha256((original / name).read_bytes()).hexdigest() for name in names})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--module-file', type=Path, default=MODULE_FILE)
    args, remaining = parser.parse_known_args()
    IndependentWorkflowConsensusTests.subject = load_module(args.module_file, 'independent_281_subject')
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == '__main__':
    main()
