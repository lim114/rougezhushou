"""Temporary editor ambiguity and unchanged ordinary JSON value boundaries."""
import json
import unittest

from rouge.manual_scenario import parse_preview_object


class ManualScenario120Tests(unittest.TestCase):
    def parse(self, text, label='战斗时序情景'):
        return parse_preview_object(text, label)

    def test_top_level_duplicate_cannot_silently_reverse_empty_target_choice(self):
        for text in ('{"target_windows": [], "target_windows": [[0, 5]]}',
                     '{"target_windows": [[0, 5]], "target_windows": []}'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, '不接受重复字段：target_windows'):
                self.parse(text)

    def test_nested_duplicate_cannot_silently_reverse_independent_unit_target_choice(self):
        text = '{"units":{"token_10001_deepcl_tentac":{"target_windows":[],"target_windows":[[0,5]]}}}'
        with self.assertRaisesRegex(ValueError, '不接受重复字段：target_windows'):
            self.parse(text)

    def test_relic_counter_duplicates_are_explicit_instead_of_last_value_wins(self):
        for text in ('{"parts_count":0,"parts_count":3}', '{"parts_count":3,"parts_count":0}'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, '藏品测试条件不接受重复字段：parts_count'):
                self.parse(text, '藏品测试条件')

    def test_equivalent_escaped_key_is_duplicate_after_JSON_unescaping(self):
        with self.assertRaisesRegex(ValueError, '不接受重复字段：gold'):
            self.parse(r'{"gold":0,"\u0067old":25}', '藏品测试条件')

    def test_same_key_on_separate_objects_preserves_independent_unit_choices(self):
        text = '{"units":{"one":{"target_windows":[]},"two":{"target_windows":[[0,5]]}}}'
        value = self.parse(text)
        self.assertEqual(value['units']['one']['target_windows'], [])
        self.assertEqual(value['units']['two']['target_windows'], [[0, 5]])
        self.assertIsNot(value['units']['one'], value['units']['two'])

    def test_bare_nonfinite_constants_reject_inside_arrays_and_objects(self):
        for literal in ('NaN', 'Infinity', '-Infinity'):
            for text in ('{"windup_frames":' + literal + '}',
                         '{"target_windows":[[0,' + literal + ']]}',
                         '{"units":{"one":{"projectile_travel_seconds":' + literal + '}}}'):
                with self.subTest(text=text), self.assertRaisesRegex(ValueError, '不接受非有限JSON数值'):
                    self.parse(text)

    def test_float_overflow_is_an_app_finite_input_policy(self):
        # 1e309 is grammatical JSON. The app cannot consume its float infinity.
        for token in ('1e309', '-1e309', '1.7976931348623159e308'):
            with self.subTest(token=token), self.assertRaisesRegex(ValueError, '不接受非有限JSON数值'):
                self.parse('{"projectile_travel_seconds":' + token + '}')

    def test_text_spelling_nan_or_infinity_is_not_a_numeric_constant(self):
        self.assertEqual(self.parse('{"unrelated":["NaN","Infinity","-Infinity"]}'),
                         {'unrelated': ['NaN', 'Infinity', '-Infinity']})

    def test_normal_numbers_keep_types_float_bits_order_and_zero(self):
        text = '{"integer":0,"float":0.0,"minus_zero":-0.0,"underflow":1e-324,"large":1e308,"flag":false,"unknown":null}'
        old = json.loads(text)
        fresh = self.parse(text)
        self.assertEqual(tuple(fresh), tuple(old))
        for name, value in old.items():
            self.assertIs(type(fresh[name]), type(value))
            if isinstance(value, float):
                self.assertEqual(fresh[name].hex(), value.hex())
            else:
                self.assertEqual(fresh[name], value)

    def test_valid_unicode_values_and_unknown_keys_remain_opaque(self):
        text = '{"备注":"尚待确认😀","extra":{"value":[null,false,0,"0"]}}'
        self.assertEqual(self.parse(text), json.loads(text))

    def test_old_malformed_document_message_is_preserved(self):
        for text in ('{', '{"target_windows":}', '{"target_windows":[]} trailing'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, '^战斗时序情景需要合法JSON对象。$'):
                self.parse(text)

    def test_old_non_object_message_is_preserved(self):
        for text in ('[]', 'null', 'false', '1', '"public"'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, '^藏品测试条件需要JSON对象。$'):
                self.parse(text, '藏品测试条件')


if __name__ == '__main__':
    unittest.main()
