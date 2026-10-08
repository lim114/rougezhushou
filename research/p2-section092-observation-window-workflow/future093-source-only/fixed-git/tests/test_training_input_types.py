import copy
import json
import re
import unittest

from rouge.catalog import catalog, operator_attributes, operator_profiles
from rouge.damage import calculate_damage


class TrainingInputTypesTests(unittest.TestCase):
    operators = ('kaltsit', 'silverash', 'mechanist', 'char_298_susuro', 'char_1037_amiya3')
    errors = {
        'elite': '精英阶段需要为 0、1 或 2。',
        'level': '等级或信赖超出范围（信赖按加成进度 0–100%）。',
        'potential': '潜能需要为 1–6。',
        'module_level': '模组身份或等级尚无可用规则。',
    }

    def arguments(self, op, field=None, value=None):
        args = {'operator': op, 'elite': 2, 'level': None, 'potential': 1}
        if field is not None:
            args[field] = value
        if field == 'module_level':
            args['module_id'] = operator_profiles()[op]['modules'][0]['id']
        return args

    def test_attributes_reject_boolean_cultivation(self):
        for op in self.operators:
            for field, error in self.errors.items():
                if field == 'module_level' and not operator_profiles()[op]['modules']:
                    continue
                for value in (False, True):
                    with self.subTest(operator=op, field=field, value=value):
                        args = self.arguments(op, field, value)
                        with self.assertRaisesRegex(ValueError, '^' + re.escape(error) + '$'):
                            operator_attributes(**args)

    def test_calculation_rejects_booleans_before_both_engines(self):
        for op in self.operators:
            for mode in ('frames', 'continuous'):
                for field, error in self.errors.items():
                    if field == 'module_level' and not operator_profiles()[op]['modules']:
                        continue
                    for value in (False, True):
                        with self.subTest(operator=op, mode=mode, field=field, value=value):
                            args = {**self.arguments(op, field, value), 'skill': 1, 'skill_rank': 1, 'timing_mode': mode}
                            snapshot = copy.deepcopy(args)
                            with self.assertRaisesRegex(ValueError, '^' + re.escape(error) + '$'):
                                calculate_damage(args)
                            self.assertEqual(args, snapshot)

    def test_valid_integer_boundaries_and_level_default(self):
        for op in self.operators:
            profile = operator_profiles()[op]
            for elite, phase in enumerate(profile['phases']):
                for potential in (1, 6):
                    default = operator_attributes(op, elite, None, potential=potential)
                    self.assertEqual(default, operator_attributes(op, elite, phase['max_level'], potential=potential))
                    minimum = operator_attributes(op, elite, 1, potential=potential)
                    self.assertGreater(minimum['hp'], 0)
                    for mode in ('frames', 'continuous'):
                        args = {'operator': op, 'elite': elite, 'potential': potential, 'level': 1,
                                'skill': 1, 'skill_rank': 1, 'timing_mode': mode}
                        result = calculate_damage(args)
                        self.assertEqual(result['estimate']['training']['elite'], elite)
                        self.assertEqual(result['estimate']['training']['level'], 1)
                        self.assertEqual(result['estimate']['training']['potential'], potential)
            for module in profile['modules']:
                for stage in (1, 2, 3):
                    with self.subTest(operator=op, module=module['id'], stage=stage):
                        args = {'operator': op, 'elite': module['unlock_elite'], 'level': module['unlock_level'],
                                'module_id': module['id'], 'module_level': stage}
                        self.assertGreater(operator_attributes(**args)['hp'], 0)
                        result = calculate_damage({**args, 'skill': 1, 'skill_rank': 7})
                        self.assertEqual(result['estimate']['training']['module_level'], stage)

    def test_non_boolean_types_keep_existing_errors(self):
        for field, error in self.errors.items():
            for value in (1.0, '1'):
                args = self.arguments('char_298_susuro', field, value)
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, '^' + re.escape(error) + '$'):
                        operator_attributes(**args)

    def test_module_stage_remains_ignored_without_module_identity(self):
        for op in self.operators:
            attrs = operator_attributes(op)
            for ignored in (False, True, 0, 1, 1.0, '1', None):
                with self.subTest(operator=op, stage=ignored):
                    self.assertEqual(attrs, operator_attributes(op, module_id=None, module_level=ignored))
                    result = calculate_damage({'operator': op, 'skill': 1, 'skill_rank': 7,
                                               'module_id': None, 'module_level': ignored})
                    self.assertEqual(result['estimate']['training']['module_id'], None)

    def test_existing_skill_boolean_rejection_and_catalog_isolation(self):
        before = json.dumps(catalog(), sort_keys=True)
        for field, error in (('skill', '请选择该干员的有效技能。'),
                             ('skill_rank', '技能等级需要为1–10的整数。')):
            for value in (False, True):
                args = {'operator': 'mechanist', 'skill': 1, 'skill_rank': 7, field: value}
                with self.assertRaisesRegex(ValueError, '^' + re.escape(error) + '$'):
                    calculate_damage(args)
        self.assertEqual(before, json.dumps(catalog(), sort_keys=True))


if __name__ == '__main__':
    unittest.main()
