"""Author preparation controls for main caller capture, not independent math review."""
import argparse
import ast
import hashlib
from copy import deepcopy
import importlib
import importlib.machinery
import json
from pathlib import Path
import sys
import types
import unittest
import uuid

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
Q = 4294967296


def load(overlay=None):
    prefix = 'rouge'
    if overlay is not None:
        overlay = Path(overlay).resolve(strict=True)
        assert (overlay / 'rouge/operator_engine.py').is_file()
        assert (overlay / 'rouge/panel_native_bridge.py').is_file()
        prefix = 'skill284_author_' + uuid.uuid4().hex
        package = types.ModuleType(prefix)
        package.__package__ = prefix
        package.__path__ = [str(overlay / 'rouge'), str(ROOT / 'rouge')]
        package.__spec__ = importlib.machinery.ModuleSpec(prefix, loader=None, is_package=True)
        sys.modules[prefix] = package
    return importlib.import_module(prefix + '.damage'), importlib.import_module(prefix + '.panel_native_bridge')


def selected(result):
    return {key: deepcopy(result.get(key)) for key in ('attack', 'total_damage', 'total_healing',
        'attack_speed', 'attack_speed_reference', 'base_attack_speed', 'base_attack_speed_reference',
        'components', 'complete', 'warnings')} | {'estimate': {
        key: deepcopy(result['estimate'].get(key)) for key in ('base_stats', 'skill', 'training', 'complete', 'warnings')}}


def native_row(result, field):
    return next(row for row in result['panel_native_finalization']['fields']
                if row['phase'] == 'skill' and row['field'] == field)


class ExtendedSkillCapture284(unittest.TestCase):
    damage = None
    bridge = None

    @classmethod
    def setUpClass(cls):
        if cls.damage is None:
            cls.damage, cls.bridge = load()

    def test_generic_myrtle_field_primitives_are_now_known_not_actual_state(self):
        scenario = {'operator': 'char_151_myrtle', 'skill': 2,
                    'effects': [{'kind': 'attack_pct', 'value': .25}, {'kind': 'attack_speed', 'value': 600}]}
        before = deepcopy(scenario)
        result = self.damage.calculate_damage(scenario)
        self.assertEqual(scenario, before)
        scope = result['panel_native_finalization']['skill_primitive_qualification']
        for field, key in [('attack', 'skill_attack'), ('attack_speed', 'skill_attack_speed_reference')]:
            row = native_row(result, field)
            self.assertTrue(scope[field]['common_model_primitives_captured'])
            self.assertIsNone(scope[field]['reason'])
            self.assertTrue(row['conditional_complete'])
            self.assertIsNotNone(row['references']['input_fp_raw'])
            self.assertEqual(row['model_value'], result['estimate']['skill'][key])
            self.assertIsNone(row['actual_decoded_value'])
        self.assertEqual(native_row(result, 'attack_speed')['references']['getter_result_raw'], 700 * Q)
        self.assertEqual(result['estimate']['skill']['skill_attack_speed'], 600)
        self.assertIsNone(result['panel_native_finalization']['actual_panel'])
        self.assertFalse(result['panel_native_finalization']['complete_native_panel'])
        self.assertNotIn('_panel_native_skill_qualification', result['estimate'])

    def test_special_actor_rewrites_exclude_only_affected_fields(self):
        cases = [
            ('char_110_deepcl', 1, {}, False, True),
            ('char_4228_closur', 2, {}, False, True),
            ('char_1001_amiya2', 1, {}, False, True),
            ('char_1029_yato2', 3, {}, False, True),
            ('char_1015_aglna2', 2, {}, False, True),
            ('char_1050_chen3', 2, {}, False, True),
            ('char_1037_amiya3', 2, {}, False, True),
            ('char_4202_haruka', 2, {}, False, True),
            ('char_2025_shu', 3, {'enemy_on_sown_tile': True}, False, False),
            ('char_2025_shu', 3, {'enemy_on_sown_tile': False}, True, True),
            ('char_4182_oblvns', 2, {'organ_mode': False}, False, True),
            ('char_4182_oblvns', 2, {'organ_mode': True}, True, False),
            ('char_1041_angel2', 2, {'steal_success': True}, True, False),
            ('char_1041_angel2', 2, {'steal_success': False}, True, True),
        ]
        for op, number, extra, attack, speed in cases:
            with self.subTest(operator=op, skill=number, extra=extra):
                result = self.damage.calculate_damage({'operator': op, 'skill': number, **extra})
                for field, expected in [('attack', attack), ('attack_speed', speed)]:
                    row = native_row(result, field)
                    self.assertIs(row['primitive_qualification']['common_model_primitives_captured'], expected)
                    self.assertIs(row['conditional_complete'], expected)
                    if not expected:
                        self.assertTrue(row['primitive_qualification']['reason'])
                        self.assertIsNone(row['references']['input_fp_raw'])
                        self.assertIsNone(row['references']['getter_result_raw'])
                    self.assertIsNone(row['actual_decoded_value'])

    def test_catalog_coverage_is_explicit_and_unknown_future_actor_cannot_claim_qualification(self):
        data = json.loads((ROOT / 'rouge/data/catalog.json').read_bytes())
        extended = {key: op for key, op in data['operators'].items() if key not in ('kaltsit', 'silverash', 'mechanist')}
        self.assertEqual(len(extended), 29)
        self.assertEqual(self.bridge.EXTENDED_CAPTURE_OPERATORS, set(extended))
        captured = {'attack': 0, 'attack_speed': 0}
        total = 0
        for key, op in extended.items():
            for number, skill in enumerate(op['skills'], 1):
                _, scopes = self.bridge.capture_extended_skill_primitives({'operator': key}, number,
                    {'attack_speed': 100}, 100, 0, 0, 0, skill['levels'][-1]['values'])
                total += 1
                for field in captured:
                    captured[field] += int(scopes[field]['common_model_primitives_captured'])
        self.assertEqual(total, 78)
        self.assertEqual(captured, {'attack': 61, 'attack_speed': 77})
        terms, scopes = self.bridge.capture_extended_skill_primitives({'operator': 'future-unknown'}, 1,
            {'attack_speed': 100}, 100, 0, 0, 0, {'atk': .5, 'attack_speed': 50})
        for field in scopes:
            self.assertFalse(scopes[field]['common_model_primitives_captured'])
            self.assertIsNone(terms[field]['basis'])

    def test_public_internal_injection_does_not_forge_qualification(self):
        result = self.damage.calculate_damage({'operator': 'char_1029_yato2', 'skill': 3,
            '_panel_native_skill_qualification': {'attack': {'common_model_primitives_captured': True}},
            '_panel_native_terms': {'skill': {'attack': {'basis': 999}}}})
        self.assertFalse(native_row(result, 'attack')['primitive_qualification']['common_model_primitives_captured'])
        self.assertIsNone(native_row(result, 'attack')['references']['input_fp_raw'])
        self.assertIsNone(result['panel_native_finalization']['actual_panel'])

    def test_existing_actor_arithmetic_assignment_expressions_are_preserved(self):
        engine = importlib.import_module(self.damage.__package__ + '.operator_engine')
        current = ast.parse(Path(engine.__file__).read_text(encoding='utf8'))
        def assignments(tree):
            plan = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'plan')
            return [ast.dump(node, include_attributes=False) for node in ast.walk(plan)
                    if isinstance(node, (ast.Assign, ast.AugAssign)) and
                    any(isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id in ('attack', 'speed_reference')
                        for n in ast.walk(node))]
        values = assignments(current)
        self.assertEqual(len(values), 18)
        digest = hashlib.sha256(json.dumps(values, separators=(',', ':')).encode()).hexdigest()
        # Exact pre284 source ab607af9... held this actor-expression inventory.
        # No cache file or current source is used as the expected oracle.
        self.assertEqual(digest, '8c61639981df9a4e49f7fe8e52f4e1d82702f3f8d8fcbdd0267f71ed8b2e6a24')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--overlay-root', type=Path)
    args, remaining = parser.parse_known_args()
    ExtendedSkillCapture284.damage, ExtendedSkillCapture284.bridge = load(args.overlay_root)
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
