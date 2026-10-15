"""Necessary public-source/qualification controls for current reward overlay."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge import moving_reward_reference as model

ROOT = Path(__file__).resolve().parents[1]


def ref(level=0, **changes):
    raw = {'id': 'enemy_2152_shezlc', 'useDb': True, 'level': level, 'overwrittenData': None}
    raw.update(changes)
    return {'source_selector': '$.enemyDbRefs[4]', 'raw': raw}


class MovingRewardReference287Tests(unittest.TestCase):
    def assert_unknown(self, result):
        self.assertFalse(result['all_fixed_level_candidates_documented'])
        self.assertFalse(result['action_level_binding_unique'])
        self.assertFalse(result['all_candidate_quantities_agree'])
        self.assertFalse(result['candidate_level_consensus'])
        self.assertEqual([row['quantity'] for row in result['outcomes']], [None, None])
        self.assertIsNone(result['actual_spawn_level'])
        self.assertIsNone(result['actual_reward_total'])

    def test_source_is_freshly_bound_to_archived_original_three_grades(self):
        data = model.source_data()
        self.assertIsNotNone(data)
        self.assertEqual(data['documented_levels'], [0, 1, 2])
        self.assertEqual(data['source']['revision'], '435751')
        self.assertTrue(data['source']['full_page_bytes_archived'])
        self.assertEqual(data['source']['archive_bytes'], 106062)
        self.assertFalse(data['source']['current_server_script_verified'])

    def test_every_documented_grade_has_independent_signed_conditions(self):
        for level in (0, 1, 2):
            with self.subTest(level=level):
                result = model.moving_reward_rule([ref(level)])
                self.assertEqual(result['referenced_levels'], [level])
                self.assertEqual([(r['condition'], r['quantity']) for r in result['outcomes']],
                                 [('defeated', 10), ('reached_route_end', -10)])
                self.assertTrue(result['all_fixed_level_candidates_documented'])
                self.assertTrue(result['action_level_binding_unique'])
                self.assertFalse(result['candidate_level_consensus'])

    def test_multiple_documented_grades_are_quantity_consensus_not_unique_instance(self):
        result = model.moving_reward_rule([ref(2), ref(0), ref(1)])
        self.assertEqual(result['referenced_levels'], [0, 1, 2])
        self.assertEqual([r['quantity'] for r in result['outcomes']], [10, -10])
        self.assertFalse(result['action_level_binding_unique'])
        self.assertTrue(result['candidate_level_consensus'])
        self.assertIn('不按引用数累加', result['quantity_scope_notice'])
        self.assertIsNone(result['actual_spawn_level'])
        self.assertIsNone(result['actual_reward_total'])

    def test_duplicate_grade_refs_never_multiply_the_per_enemy_quantity(self):
        result = model.moving_reward_rule([ref(1), ref(1), ref(1)])
        self.assertEqual([row['quantity'] for row in result['outcomes']], [10, -10])
        self.assertTrue(result['action_level_binding_unique'])
        self.assertFalse(result['candidate_level_consensus'])
        self.assertEqual(result['reference_qualification']['reference_count'], 3)

    def test_empty_or_wrong_reference_collection_retains_unknown(self):
        for value in (None, False, True, [], {}, (), 'grade1', 1):
            with self.subTest(value=value):
                self.assert_unknown(model.moving_reward_rule(value))

    def test_missing_or_wrong_raw_object_retains_unknown(self):
        for value in (None, [], False, 1, 'raw', {}, {'raw': None}, {'raw': []}, {'raw': False}):
            with self.subTest(value=value):
                self.assert_unknown(model.moving_reward_rule([value]))

    def test_exact_entity_is_required_even_for_same_named_device(self):
        for identity in ('trap_321_shnbox', 'trap_323_shsbox', '恶笼草',
                         'enemy_2152_shezlc ', 'ENEMY_2152_SHEZLC', None):
            with self.subTest(identity=identity):
                self.assert_unknown(model.moving_reward_rule([ref(1, id=identity)]))
        missing = ref(1)
        del missing['raw']['id']
        self.assert_unknown(model.moving_reward_rule([missing]))

    def test_use_db_is_strictly_explicit_true(self):
        for value in (False, 0, 1, None, 'true', [], {}):
            with self.subTest(value=value):
                self.assert_unknown(model.moving_reward_rule([ref(1, useDb=value)]))
        missing = ref(1)
        del missing['raw']['useDb']
        self.assert_unknown(model.moving_reward_rule([missing]))

    def test_level_is_exact_supported_int_without_zero_default(self):
        for value in (True, False, 0.0, 1.0, '0', '1', None, -1, 3, [], {}):
            with self.subTest(value=value):
                self.assert_unknown(model.moving_reward_rule([ref(value)]))
        missing = ref(1)
        del missing['raw']['level']
        self.assert_unknown(model.moving_reward_rule([missing]))

    def test_override_requires_an_explicit_null_not_falsy_or_missing(self):
        for value in ({}, [], False, 0, '', {'level': 1}, {'attributes': {}}):
            with self.subTest(value=value):
                self.assert_unknown(model.moving_reward_rule([ref(1, overwrittenData=value)]))
        missing = ref(1)
        del missing['raw']['overwrittenData']
        self.assert_unknown(model.moving_reward_rule([missing]))

    def test_one_bad_candidate_poisoning_is_not_silently_filtered(self):
        result = model.moving_reward_rule([ref(0), ref(True), ref(2)])
        self.assert_unknown(result)
        self.assertEqual(result['reference_qualification']['invalid_reference_indices'], [1])
        self.assertEqual(result['referenced_levels'], [0, 2])

    def test_input_remains_unchanged_and_extra_fields_are_not_reflected(self):
        values = [ref(1), ref(2)]
        values[0]['private_looking_unused_metadata'] = 'do-not-reflect-this'
        before = deepcopy(values)
        result = model.moving_reward_rule(values)
        self.assertEqual(values, before)
        self.assertNotIn('do-not-reflect-this', json.dumps(result))

    def test_no_actual_spawn_kill_route_end_grant_or_probability_is_claimed(self):
        result = model.moving_reward_rule([ref(2)])
        for key in ('actual_reward', 'actual_spawn_level', 'actual_reward_total',
                    'actual_defeated_count', 'actual_route_end_count', 'probability'):
            self.assertIsNone(result[key], key)
        self.assertFalse(result['current_rogue6_server_script_verified'])
        self.assertFalse(result['complete_effective_level_binding_known'])
        self.assertTrue(all(row['actual_quantity'] is None and row['quantity_is_total'] is False
                            for row in result['outcomes']))

    def test_returned_source_data_mutation_does_not_change_future_calls(self):
        data = model.source_data()
        data['documented_outcomes_by_level']['1']['defeated'] = 999
        self.assertEqual(model.moving_reward_rule([ref(1)])['outcomes'][0]['quantity'], 10)

    def test_every_source_pin_and_manifest_fail_closed_after_valid_warm_call(self):
        original = (ROOT / model.MANIFEST).read_bytes()
        manifest = json.loads(original)
        names = [model.MANIFEST, *manifest['files']]
        with tempfile.TemporaryDirectory(prefix='rouge-287-public-source-guard-') as temp:
            clone = Path(temp)
            for name in names:
                target = clone / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            with patch.object(model, 'ROOT', clone):
                for name in names:
                    target = clone / name
                    raw = target.read_bytes()
                    for mode in ('flip', 'missing'):
                        with self.subTest(name=name, mode=mode):
                            self.assertIsNotNone(model.source_data())
                            self.assertEqual(model.moving_reward_rule([ref(1)])['outcomes'][0]['quantity'], 10)
                            if mode == 'flip':
                                changed = bytearray(raw)
                                changed[len(changed) // 2] ^= 1
                                target.write_bytes(changed)
                            else:
                                target.unlink()
                            result = model.moving_reward_rule([ref(1), ref(2)])
                            self.assertFalse(result['source_valid'])
                            self.assertIsNone(result['quantity_source'])
                            self.assert_unknown(result)
                            target.write_bytes(raw)
                self.assertIsNotNone(model.source_data())
        self.assertEqual((ROOT / model.MANIFEST).read_bytes(), original)

    def test_public_function_rejects_source_or_data_injection(self):
        for keyword in ('source', 'data', 'source_data', 'evaluator'):
            with self.subTest(keyword=keyword), self.assertRaises(TypeError):
                model.moving_reward_rule([ref(1)], **{keyword: {}})

    def test_real_html_extraction_reproduces_three_independent_byte_spans(self):
        path = ROOT / 'scripts/build_moving_reward_current_reference.py'
        spec = importlib.util.spec_from_file_location('extract_moving_reward_287', path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        source = (ROOT / 'research/p3-moving-reward-current/moving-mobile-response.html').read_bytes()
        actual = builder.extract_document(source)
        expected = json.loads((ROOT / 'research/p3-moving-reward-current/extraction.json').read_text(encoding='utf8'))
        self.assertEqual(actual, expected)
        self.assertEqual([row['level'] for row in actual['grades']], [0, 1, 2])
        for row in actual['grades']:
            span = source[row['start_byte']:row['end_byte']]
            self.assertEqual(hashlib.sha256(span).hexdigest(), row['source_span_sha256'])
            self.assertEqual(span.count(builder.SENTENCE.encode('utf8')), 1)
            self.assertEqual((row['defeated_battle_settlement_gold'],
                              row['reached_route_end_battle_settlement_gold']), (10, -10))
        with self.assertRaises(ValueError):
            builder.extract_document(source + b' ')


if __name__ == '__main__':
    unittest.main()
