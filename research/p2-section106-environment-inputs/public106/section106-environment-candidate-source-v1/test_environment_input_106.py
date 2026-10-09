"""Combined public environment qualification and genuine cache recovery contracts.

Source-only candidate: the author has not imported this module or run its tests.
Root validates against the actual original observations before transportation.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from rouge.battle_preview import enemy_preview
from rouge.damage import calculate_damage
from rouge.run_config import confirmed_config, difficulty_value
from rouge.run_state import RunState


BASE = {'operator': 'mechanist', 'skill': 3, 'elite': 2, 'level': 90,
        'skill_rank': 10, 'trust': 100, 'potential': 1, 'module_id': None,
        'module_level': 0, 'timing_mode': 'frames', 'charge_count': 0,
        'window_seconds': 10}
ZERO = {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0}
ONE = {'stage_id': 'ro6_n_3_1', 'enemy_id': 'enemy_2001_duckmi', 'level': 1}


def fixture(record):
    return {'id': 'public-environment106-test', 'started_at': 1000,
            'last_capture_at': 1001, 'operators': {}, 'relics': {},
            'config': {'difficulty': deepcopy(record)}}


def calculation(record, **extra):
    return {**BASE, 'run_config': {'difficulty': deepcopy(record)}, **extra}


def environment_note(result):
    return next(section for section in result['report']['sections']
                if section['id'] == 'run_environment')['notes'][0]


def without_exact_source_presentation(result):
    """Ignore only the two explicitly changed provenance presentation leaves."""
    result = deepcopy(result)
    result['run_resolution']['difficulty'].pop('source', None)
    section = next(item for item in result['report']['sections']
                   if item['id'] == 'run_environment')
    section['notes'][0] = 'SOURCE_NOTE_QUALIFIED_COMPARISON'
    return result


class DifficultyQualification106Tests(unittest.TestCase):
    def test_all_normal_grades_and_alias_defaults_remain_available(self):
        for value in range(16):
            for aliases in ({}, {'mode': 'NORMAL'}, {'modeDifficulty': 'NORMAL'},
                            {'mode': 'NORMAL', 'modeDifficulty': 'NORMAL'}):
                with self.subTest(value=value, aliases=aliases):
                    self.assertEqual(difficulty_value({'value': value, **aliases}), value)

    def test_either_unsupported_mode_alias_is_unavailable(self):
        for field in ('mode', 'modeDifficulty'):
            for mode in ('MONTH_TEAM', None, False, 1, ['NORMAL'], {'mode': 'NORMAL'}):
                with self.subTest(field=field, mode=mode):
                    self.assertIsNone(difficulty_value({'value': 2, field: mode}))

    def test_conflicting_aliases_do_not_let_normal_override_monthly(self):
        for record in ({'value': 2, 'mode': 'MONTH_TEAM', 'modeDifficulty': 'NORMAL'},
                       {'value': 2, 'mode': 'NORMAL', 'modeDifficulty': 'MONTH_TEAM'}):
            self.assertIsNone(difficulty_value(record))

    def test_grade_type_and_range_contract_is_not_broadened(self):
        for grade in (True, False, 2.0, '2', None, [2], {}, -1, 16):
            with self.subTest(grade=grade):
                self.assertIsNone(difficulty_value({'value': grade}))

    def test_unsupported_mode_is_not_reused_but_other_safe_config_survives(self):
        squad = {'id': 'rogue_6_band_6', 'name': '矛头分队',
                 'captured_at': 1001, 'effect_verified': ['opaque-legacy-flag']}
        context = {'run_id': 'public106', 'config': {
            'difficulty': {'value': 2, 'mode': 'MONTH_TEAM', 'captured_at': 1001},
            'squad': squad}}
        before = deepcopy(context)
        result = confirmed_config(context)
        self.assertNotIn('difficulty', result)
        self.assertEqual(result['squad']['effect_verified'], squad['effect_verified'])
        self.assertEqual(context, before)

    def test_normal_reuse_and_unused_time_shortcut_are_preserved(self):
        valid = {'value': 0, 'mode': 'NORMAL', 'captured_at': 0, 'source': ''}
        result = confirmed_config({'run_id': 'public106', 'config': {'difficulty': valid}})
        self.assertEqual(result['difficulty']['value'], 0)
        self.assertEqual(result['difficulty']['source'], '')
        for context in ({'run_id': 'public106', 'config': {'difficulty': {**valid, 'captured_at': None}}},
                        {'run_id': '', 'config': {'difficulty': valid}}):
            self.assertEqual(confirmed_config(context), {})

    def test_numeric_entry_retains_existing_mode_value_error(self):
        for field in ('mode', 'modeDifficulty'):
            with self.subTest(field=field):
                caller = calculation({'value': 2, field: 'MONTH_TEAM', 'source': None})
                before = deepcopy(caller)
                with self.assertRaisesRegex(ValueError, '仅支持NORMAL模式'):
                    calculate_damage(caller)
                self.assertEqual(caller, before)

    def test_invalid_incoming_mode_does_not_replace_valid_saved_difficulty(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.json'
            run = RunState(path)
            valid = {'operators': [], 'config': {'difficulty': {'value': 0, 'source': 'public-normal'}}}
            self.assertTrue(run.apply(valid, 1001))
            original = deepcopy(run.state['config']['difficulty'])
            bad = {'operators': [], 'config': {'difficulty': {'value': 15, 'mode': 'MONTH_TEAM'}}}
            before = deepcopy(bad)
            self.assertTrue(run.apply(bad, 1002))
            self.assertEqual(run.state['config']['difficulty'], original)
            self.assertEqual(bad, before)
            self.assertEqual(RunState(path).state['config']['difficulty'], original)

    def test_unknown_cached_mode_is_purely_visible_and_then_legally_recoverable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.json'
            raw = json.dumps(fixture({'value': 2, 'mode': 'MONTH_TEAM',
                                     'source': None, 'captured_at': 1001})).encode()
            path.write_bytes(raw)
            temporary = path.with_suffix('.tmp')
            temporary.write_bytes(b'public106-protected-temp\n')
            run = RunState(path)
            self.assertFalse(run.preserve_unreadable)
            before = deepcopy(run.state)
            self.assertIn('保密等级未确认', run.summary())
            self.assertNotIn('保密等级 2', run.summary())
            self.assertNotIn('difficulty', confirmed_config(run.recognition_context()))
            self.assertEqual(run.state, before)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(temporary.read_bytes(), b'public106-protected-temp\n')
            fresh = {'operators': [], 'config': {'difficulty': {'value': 2, 'source': 'public-fresh-normal'}}}
            fresh_before = deepcopy(fresh)
            self.assertTrue(run.apply(fresh, 1002))
            self.assertEqual(fresh, fresh_before)
            self.assertNotIn('mode', run.state['config']['difficulty'])
            self.assertIn('保密等级 2', run.summary())
            restarted = RunState(path)
            self.assertEqual(restarted.state, json.loads(path.read_text()))
            self.assertIn('difficulty', confirmed_config(restarted.recognition_context()))
            result = calculate_damage(calculation(restarted.state['config']['difficulty']))
            self.assertIn('public-fresh-normal', environment_note(result))

    def test_bad_cached_grade_is_not_named_confirmed_and_raw_is_not_normalized(self):
        for grade in (True, 2.0, '2', [2], None):
            with self.subTest(grade=grade), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'run.json'
                raw = json.dumps(fixture({'value': grade, 'captured_at': 1001})).encode()
                path.write_bytes(raw)
                run = RunState(path)
                self.assertFalse(run.preserve_unreadable)
                self.assertIn('保密等级未确认', run.summary())
                self.assertEqual(run.state['config']['difficulty']['value'], grade)
                self.assertIs(type(run.state['config']['difficulty']['value']), type(grade))
                self.assertEqual(path.read_bytes(), raw)


class EnemyReferenceIdentity106Tests(unittest.TestCase):
    def test_active_boolean_zero_and_one_do_not_select_integer_enemy_profiles(self):
        for target, value in ((ZERO, False), (ONE, True)):
            with self.subTest(value=value):
                caller = calculation({'value': 2}, target_enemy={**target, 'level': value})
                before = deepcopy(caller)
                with self.assertRaisesRegex(ValueError, '身份/等级必须与关卡引用唯一匹配'):
                    calculate_damage(caller)
                self.assertEqual(caller, before)

    def test_historical_integer_and_float_target_calls_keep_their_own_raw_types(self):
        for target in (ZERO, ONE):
            for level in (target['level'], float(target['level'])):
                with self.subTest(target=target, level=level):
                    caller = calculation({'value': 2}, target_enemy={**target, 'level': level})
                    before = deepcopy(caller)
                    result = calculate_damage(caller)
                    self.assertEqual(caller, before)
                    self.assertIs(type(result['run_resolution']['enemy']['level']), type(level))
                    self.assertEqual(result['run_resolution']['enemy']['reference_stats'],
                                     calculate_damage(calculation({'value': 2}, target_enemy=target))[
                                         'run_resolution']['enemy']['reference_stats'])

    def test_inactive_false_or_empty_target_keeps_original_no_target_calculation(self):
        plain = calculate_damage(calculation({'value': 2}))
        for target in (False, {}):
            self.assertEqual(calculate_damage(calculation({'value': 2}, target_enemy=target)), plain)

    def test_other_invalid_identity_errors_remain_separate(self):
        caller = calculation({'value': 2}, target_enemy={**ONE, 'level': '1'})
        with self.assertRaisesRegex(ValueError, '身份/等级必须与关卡引用唯一匹配'):
            calculate_damage(caller)
        caller = calculation({'value': 2}, target_enemy={**ONE, 'stage_id': 'public-invalid-stage', 'level': True})
        with self.assertRaisesRegex(ValueError, '目标关卡没有固定敌人档案'):
            calculate_damage(caller)

    def test_preview_keeps_its_existing_stricter_boolean_and_float_errors(self):
        for level in (False, True, 0.0, 1.0):
            target = ZERO if level == 0 else ONE
            with self.subTest(level=level):
                with self.assertRaisesRegex(ValueError, '敌人引用等级需要非负整数'):
                    enemy_preview(target['stage_id'], target['enemy_id'], level)

    def test_preview_valid_integer_binding_is_unchanged(self):
        for target in (ZERO, ONE):
            result = enemy_preview(target['stage_id'], target['enemy_id'], target['level'])
            self.assertEqual(result['skill_reference']['requested_level'], target['level'])
            self.assertIs(type(result['skill_reference']['requested_level']), int)


class DifficultySourcePresentation106Tests(unittest.TestCase):
    def test_non_text_metadata_uses_explicit_unconfirmed_source_and_keeps_raw_input(self):
        for source in (None, [], ['public'], 1, 2.5, {'text': 'public'}, False):
            with self.subTest(source=source):
                caller = calculation({'value': 2, 'source': source})
                before = deepcopy(caller)
                result = calculate_damage(caller)
                self.assertEqual(caller, before)
                self.assertEqual(result['run_resolution']['difficulty']['source'], source)
                self.assertIs(type(result['run_resolution']['difficulty']['source']), type(source))
                self.assertIn('来源：未确认（来源字段不是文本）', environment_note(result))

    def test_source_fallback_only_changes_two_declared_presentation_leaves(self):
        control = calculate_damage(calculation({'value': 2}))
        expected = without_exact_source_presentation(control)
        for source in (None, [], 1, {}, False):
            with self.subTest(source=source):
                result = calculate_damage(calculation({'value': 2, 'source': source}))
                self.assertEqual(without_exact_source_presentation(result), expected)

    def test_missing_source_retains_existing_explicit_scenario_default(self):
        result = calculate_damage(calculation({'value': 2}))
        self.assertIn('来源：明确提供的计算情景', environment_note(result))
        self.assertNotIn('source', result['run_resolution']['difficulty'])

    def test_empty_and_text_sources_are_neither_replaced_nor_stripped(self):
        for source in ('', 'public-confirmed', '  public-reference  '):
            result = calculate_damage(calculation({'value': 2, 'source': source}))
            self.assertEqual(environment_note(result), '本局保密等级：2；来源：' + source)
            self.assertEqual(result['run_resolution']['difficulty']['source'], source)

    def test_non_text_saved_source_can_calculate_without_overwriting_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.json'
            raw = json.dumps(fixture({'value': 2, 'source': None, 'captured_at': 1001})).encode()
            path.write_bytes(raw)
            run = RunState(path)
            self.assertFalse(run.preserve_unreadable)
            before = deepcopy(run.state)
            result = calculate_damage(calculation(run.state['config']['difficulty']))
            self.assertIn('来源：未确认', environment_note(result))
            self.assertEqual(run.state, before)
            self.assertEqual(path.read_bytes(), raw)

    def test_unusable_grade_precedes_provenance_formatting(self):
        for grade in (True, 2.0, '2', None):
            with self.subTest(grade=grade):
                with self.assertRaisesRegex(ValueError, '保密等级需要0–15的整数'):
                    calculate_damage(calculation({'value': grade, 'source': []}))

    def test_normal_zero_remains_distinct_from_unsupported_monthly_zero(self):
        normal = calculate_damage(calculation({'value': 0, 'source': None}))
        self.assertEqual(normal['run_resolution']['difficulty']['mode'], 'NORMAL')
        self.assertIn('来源：未确认', environment_note(normal))
        with self.assertRaisesRegex(ValueError, '仅支持NORMAL模式'):
            calculate_damage(calculation({'value': 0, 'mode': 'MONTH_TEAM', 'source': None}))
