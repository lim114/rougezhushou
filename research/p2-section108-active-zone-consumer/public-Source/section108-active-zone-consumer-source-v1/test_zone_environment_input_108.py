"""Active zone input qualification preserves existing public environment facts.

These Source-only tests use original APIs and pinned public records. They add no
zone names, hidden depth, difficulty modes, growth values or game timing. Root
owns all actual execution and independent full native evidence.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from rouge.battle_preview import enemy_preview
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.run_modifiers import prepare_run
from rouge.run_state import RunState


BASE = {'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 90,
        'skill_rank': 10, 'trust': 100, 'potential': 1, 'module_id': None,
        'module_level': 0, 'timing_mode': 'frames', 'window_seconds': 10,
        'relic_ids': [], 'enemy_defense': 99999, 'enemy_resistance': 99}
TARGET = {'stage_id': 'ro6_n_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0}
ABSENT = object()
CONTAINER_ERROR = '本局区域配置需要对象。'
IDENTITY_ERROR = '本局区域ID不能用于固定区域查询。'
BAD_CONTAINERS = ('zone_2', True, 1, 1.5, ['zone_2'])
BAD_IDENTITIES = ([], {}, ['zone_2'])
FALSEY = (None, {}, False, 0, '', [])


def request(zone=ABSENT, grade=10, *, target=True):
    caller = deepcopy(BASE)
    if target:caller['target_enemy'] = deepcopy(TARGET)
    config = {}
    if grade is not None:
        config['difficulty'] = {'value': grade, 'mode': 'NORMAL', 'modeDifficulty': 'NORMAL',
                                'source': 'public108-zone-consumer-regression'}
    if zone is not ABSENT:config['zone'] = deepcopy(zone)
    caller['run_config'] = config
    return caller


def checked(test, caller, api=calculate_damage):
    before = deepcopy(caller)
    try:return api(caller)
    finally:test.assertEqual(caller, before)


def preview(test, config):
    before = deepcopy(config)
    try:return enemy_preview(TARGET['stage_id'], TARGET['enemy_id'], TARGET['level'], config)
    finally:test.assertEqual(config, before)


def portal(**extra):
    data = config_data()['zones']
    return {'id': None, 'hidden': True, 'name': data['zone_portal_normal_1_1']['name'],
            'candidates': ['zone_portal_normal_1_1', 'zone_portal_normal_1_2'], **extra}


def fixture(zone):
    return {'id': 'public108-zone-cache-regression', 'started_at': 1000,
            'last_capture_at': 1001, 'operators': {}, 'relics': {},
            'config': {'difficulty': {'value': 10, 'captured_at': 1001}, 'zone': zone}}


class ZoneEnvironmentInput108Tests(unittest.TestCase):
    def test_active_truthy_nonmapping_zone_has_value_error_and_pure_caller(self):
        for grade in (0, 4, 10):
            for zone in BAD_CONTAINERS:
                for api in (prepare_run, calculate_damage):
                    with self.subTest(grade=grade, zone=zone, api=api.__name__):
                        with self.assertRaisesRegex(ValueError, CONTAINER_ERROR):
                            checked(self, request(zone, grade), api)

    def test_active_unhashable_identity_has_value_error_even_without_growth(self):
        for grade in (0, 4, 10):
            for identity in BAD_IDENTITIES:
                for api in (prepare_run, calculate_damage):
                    with self.subTest(grade=grade, identity=identity, api=api.__name__):
                        with self.assertRaisesRegex(ValueError, IDENTITY_ERROR):
                            checked(self, request({'id': identity, 'main_zone_index': 2}, grade), api)

    def test_preview_uses_existing_pending_contract_for_invalid_active_zone(self):
        invalid = [(zone, CONTAINER_ERROR) for zone in BAD_CONTAINERS]
        invalid += [({'id': identity, 'main_zone_index': 2}, IDENTITY_ERROR)
                    for identity in BAD_IDENTITIES]
        for grade in (4, 10):
            control = preview(self, request(grade=grade)['run_config'])
            for zone, message in invalid:
                with self.subTest(grade=grade, zone=zone):
                    result = preview(self, request(zone, grade)['run_config'])
                    self.assertIsNone(result['environment'])
                    self.assertEqual(result['context_pending'], ['本局环境无法确认：' + message])
                    expected = deepcopy(control)
                    expected['environment'] = None
                    expected['context_pending'] = ['本局环境无法确认：' + message]
                    self.assertEqual(result, expected)

    def test_falsey_zone_keeps_absent_result_in_low_and_growth_grades(self):
        for grade in (0, 4, 10):
            control = checked(self, request(grade=grade))
            for zone in FALSEY:
                with self.subTest(grade=grade, zone=zone):
                    self.assertEqual(checked(self, request(zone, grade)), control)

    def test_bad_zone_is_not_consumed_without_target_or_difficulty(self):
        zones = list(BAD_CONTAINERS) + [{'id': value} for value in BAD_IDENTITIES]
        for grade, target in ((10, False), (None, True)):
            control = checked(self, request(grade=grade, target=target))
            for zone in zones:
                with self.subTest(grade=grade, target=target, zone=zone):
                    self.assertEqual(checked(self, request(zone, grade, target=target)), control)
                    prepared, resolution = checked(self, request(zone, grade, target=target), prepare_run)
                    self.assertEqual(prepared['run_config']['zone'], zone)
                    self.assertEqual(resolution, checked(self, request(grade=grade, target=target), prepare_run)[1])

    def test_known_main_id_only_matches_explicit_declared_depth(self):
        for identity, depth in (('zone_1', 1), ('zone_2', 2), ('zone_3', 3),
                                ('zone_4', 4), ('zone_4_1', 4), ('zone_5', 5), ('zone_6', 6)):
            with self.subTest(identity=identity):
                self.assertIn(identity, config_data()['zones'])
                self.assertEqual(checked(self, request({'id': identity})),
                                 checked(self, request({'main_zone_index': depth})))

    def test_zone4_variants_keep_same_main_depth_for_all_original_normal_grades(self):
        for grade in range(16):
            control = checked(self, request({'main_zone_index': 4}, grade))
            for identity in ('zone_4', 'zone_4_1'):
                with self.subTest(grade=grade, identity=identity):
                    self.assertEqual(checked(self, request({'id': identity}, grade)), control)

    def test_known_id_overrides_stale_typed_depth_without_rewriting_it(self):
        for identity in ('zone_4', 'zone_4_1'):
            control = checked(self, request({'id': identity}))
            for main in (None, True, False, -1, 0, 7, 2.0, '2', [], {}):
                with self.subTest(identity=identity, main=main):
                    caller = request({'id': identity, 'main_zone_index': main})
                    self.assertEqual(checked(self, caller), control)
                    self.assertIs(type(caller['run_config']['zone']['main_zone_index']), type(main))

    def test_safe_hashable_raw_ids_keep_original_explicit_depth_fallback(self):
        control = checked(self, request({'main_zone_index': 2}))
        for identity in (None, '', False, True, 1, 1.5, 'public-unknown-zone'):
            with self.subTest(identity=identity):
                caller = request({'id': identity, 'main_zone_index': 2})
                self.assertEqual(checked(self, caller), control)
                self.assertIs(type(caller['run_config']['zone']['id']), type(identity))

    def test_unknown_invalid_depth_remains_pending_without_normalization(self):
        control = checked(self, request())
        for main in (None, True, False, -1, 0, 7, 2.0, '2', [], {}):
            with self.subTest(main=main):
                caller = request({'id': 'public-unknown-zone', 'main_zone_index': main})
                result = checked(self, caller)
                self.assertEqual(result, control)
                self.assertTrue(any('主区域深度尚未确认' in note for note in result['run_resolution']['pending']))
                self.assertIs(type(caller['run_config']['zone']['main_zone_index']), type(main))

    def test_portal_identity_digits_do_not_infer_a_main_region(self):
        control = checked(self, request())
        identities = [key for key in config_data()['zones'] if key.startswith('zone_portal_')]
        self.assertEqual(len(identities), 19)
        for identity in identities:
            with self.subTest(identity=identity):
                self.assertEqual(checked(self, request({'id': identity})), control)
        self.assertEqual(checked(self, request(portal())), control)

    def test_portal_uses_only_explicit_existing_integer_main_depth(self):
        for depth in (1, 2, 6):
            control = checked(self, request({'main_zone_index': depth}))
            for zone in (portal(main_zone_index=depth),
                         {'id': 'zone_portal_normal_1_1', 'main_zone_index': depth}):
                with self.subTest(depth=depth, zone=zone):
                    self.assertEqual(checked(self, request(zone)), control)

    def test_healthy_preview_and_calculation_share_fixed_environment_without_relics(self):
        for zone in ({'id': 'zone_4'}, {'id': 'zone_4_1', 'main_zone_index': True},
                     portal(), portal(main_zone_index=2)):
            with self.subTest(zone=zone):
                caller = request(zone)
                numeric = checked(self, caller)
                result = preview(self, caller['run_config'])
                self.assertEqual(result['environment'], numeric['run_resolution']['enemy'])
                self.assertEqual(result['context_pending'], numeric['run_resolution']['pending'])

    def test_safe_cached_raw_depth_is_consumed_without_memory_or_disk_normalization(self):
        for raw_main in (True, '2', [6]):
            with self.subTest(raw_main=raw_main), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'run.json'
                zone = {'id': 'zone_4_1', 'name': config_data()['zones']['zone_4_1']['name'],
                        'captured_at': 1001, 'source': 'public108-old-zone', 'main_zone_index': raw_main}
                raw = json.dumps(fixture(zone), ensure_ascii=False).encode()
                path.write_bytes(raw)
                run = RunState(path)
                self.assertFalse(run.preserve_unreadable)
                before = deepcopy(run.state)
                self.assertEqual(checked(self, request(run.state['config']['zone'])),
                                 checked(self, request({'id': 'zone_4_1'})))
                self.assertEqual(run.state, before)
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(RunState(path).state['config']['zone'], zone)

    def test_fresh_confirmed_main_then_portal_preserves_original_depth_on_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'run.json'
            path.write_text(json.dumps(fixture({}), ensure_ascii=False), encoding='utf-8')
            run = RunState(path)
            known = {'id': 'zone_4_1', 'name': config_data()['zones']['zone_4_1']['name'],
                     'source': 'public108-fresh-confirmed-zone'}
            incoming = {'operators': [], 'config': {'zone': known}}
            before = deepcopy(incoming)
            self.assertTrue(run.apply(incoming, 1002))
            self.assertEqual(incoming, before)
            self.assertEqual(run.state['config']['zone']['main_zone_index'], 4)
            hidden = {'operators': [], 'config': {'zone': portal(main_zone_index=6)}}
            hidden_before = deepcopy(hidden)
            self.assertTrue(run.apply(hidden, 1003))
            self.assertEqual(hidden, hidden_before)
            self.assertEqual(run.state['config']['zone']['main_zone_index'], 4)
            restarted = RunState(path)
            self.assertEqual(restarted.state['config']['zone'], run.state['config']['zone'])
            self.assertEqual(checked(self, request(restarted.state['config']['zone'])),
                             checked(self, request({'id': 'zone_4'})))

    def test_existing_invalid_difficulty_and_target_errors_still_precede_zone(self):
        for zone in BAD_CONTAINERS:
            caller = request(zone)
            caller['run_config']['difficulty']['value'] = True
            with self.subTest(zone=zone, boundary='grade'), self.assertRaisesRegex(ValueError, '0–15的整数'):
                checked(self, caller)
            caller = request(zone)
            caller['target_enemy']['stage_id'] = 'public-invalid-stage'
            with self.subTest(zone=zone, boundary='target'), self.assertRaisesRegex(ValueError, '目标关卡没有固定敌人档案'):
                checked(self, caller)
