"""Draft public account-cache validation and preservation regression.

Not executed by its author. Root must review, integrate and run this module.
No Qt, Wine, private fixtures, formatter calls or numerical API calls are used.
Genuine RunState priority and UI unknown labels remain root's window checks.
"""

import copy
import json
import tempfile
import time
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from rouge import account_cache as cache_module
from rouge.account_cache import AccountCache
from rouge.catalog import catalog, operator_profiles


MISSING = object()
OP = 'mechanist'
GOOD_OP = 'kaltsit'
UNKNOWN_OP = 'public_unknown_operator_093'
CONTAINERS = ('fields', 'skill_ranks', 'sources', 'field_times', 'skill_times')
NON_OBJECT_JSON = (None, False, 0, 'public text', [])
ISSUE_WORDS = {'fields': '字段', 'skill_ranks': '技能', 'sources': '来源',
               'field_times': '时间', 'skill_times': '时间',
               'elite': '精英', 'level': '等级', 'trust': '信赖',
               'potential': '潜能', 'invalid_fields': '字段',
               'invalid_skill_ranks': '技能', 'missing_fields': '字段'}


def observation(op=OP, **overrides):
    value = {
        'id': op, 'scope': 'operator_profile',
        'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1,
                   'selected_skill': 1},
        'skill_ranks': {'1': 7}, 'captured_at': 100.0,
        'sources': {'level': 'public fixture'},
        'field_times': {'level': 100.0}, 'skill_times': {'1': 100.0},
    }
    value.update(copy.deepcopy(overrides))
    return value


class AccountCache093Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Real public rules, including merged catalog aliases; no fake profiles.
        cls.profiles = operator_profiles()
        cls.implemented = tuple(catalog()['operators'])
        cls.module_id = cls.profiles[OP]['modules'][0]['id']

    def setUp(self):
        self.folder_context = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder_context.cleanup)
        self.folder = Path(self.folder_context.name)
        self.serial = 0

    def make_cache(self, payload=MISSING, *, path=None):
        self.serial += 1
        path = path or self.folder / ('account-%d.json' % self.serial)
        if payload is not MISSING:
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        return AccountCache(path, self.profiles, implemented_ids=self.implemented), path

    def assert_usable(self, cache, op=OP):
        self.assertNotIn(op, cache.issues)
        self.assertEqual(cache.view(op)['id'], op)

    def assert_quarantined(self, cache, op=OP):
        self.assertIn(op, cache.issues)
        self.assertTrue(cache.issues[op])
        self.assertEqual(cache.view(op), {})
        self.assertTrue(cache.preserve_original)

    def assert_save_skipped_completely(self, cache, fresh=None, *, at=200.0):
        # Patching the three actual filesystem side effects proves that the guard
        # sits before mkdir/write/replace, even when no changed data is persisted.
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            if fresh is not None:
                self.assertTrue(cache.observe(fresh, at))
            self.assertFalse(cache.save())
            for spy in spies:
                spy.assert_not_called()

    def test_missing_file_is_read_only_and_retains_normal_save(self):
        path = self.folder / 'public-missing.json'
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            cache, _ = self.make_cache(path=path)
            for spy in spies:
                spy.assert_not_called()
        self.assertFalse(cache.preserve_original)
        self.assertIsNone(cache.load_issue)
        self.assertFalse(path.exists())
        fresh = observation(fields={'level': 70}, skill_ranks={})
        before = copy.deepcopy(fresh)
        with patch.object(cache, 'save', wraps=cache.save) as save:
            self.assertTrue(cache.observe(fresh, 200.0))
            save.assert_called_once_with()
        self.assertEqual(fresh, before)
        disk = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(disk[OP]['id'], OP)
        self.assertEqual(disk[OP]['fields'], {'level': 70})
        self.assertTrue(cache.save())
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_each_legal_non_object_json_root_is_preserved(self):
        for root in NON_OBJECT_JSON:
            with self.subTest(root=repr(root)):
                cache, path = self.make_cache(root)
                original = path.read_bytes()
                self.assertTrue(cache.preserve_original)
                self.assertTrue(cache.load_issue)
                self.assertEqual(cache.view(OP), {})
                self.assert_save_skipped_completely(cache, observation())
                self.assertEqual(path.read_bytes(), original)
                self.assertFalse(path.with_suffix('.tmp').exists())

    def test_existing_clean_and_damaged_loads_have_no_write_side_effects(self):
        for payload in ({OP: observation()}, {OP: observation(fields={'elite': []})}):
            with self.subTest(damaged=payload[OP]['fields'].get('elite') == []):
                self.serial += 1
                path = self.folder / ('readonly-%d.json' % self.serial)
                path.write_text(json.dumps(payload), encoding='utf-8')
                original = path.read_bytes()
                with ExitStack() as stack:
                    spies = [stack.enter_context(patch.object(Path, name))
                             for name in ('mkdir', 'write_text', 'replace')]
                    self.make_cache(path=path)
                    for spy in spies:
                        spy.assert_not_called()
                self.assertEqual(path.read_bytes(), original)

    def test_invalid_json_original_and_normal_save_side_effects_stay_untouched(self):
        path = self.folder / 'malformed-public.json'
        original = b'{"public_bad_json":'
        path.write_bytes(original)
        cache, _ = self.make_cache(path=path)
        self.assertTrue(cache.preserve_original)
        self.assertTrue(cache.load_issue)
        self.assert_save_skipped_completely(cache, observation())
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_generic_oserror_is_not_missing_and_skips_every_save_side_effect(self):
        cache_path = self.folder / 'read-failure.json'
        original = b'{"public_unreadable":true}'
        cache_path.write_bytes(original)
        for failure in (OSError('public injected failure'), PermissionError('public denied')):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(Path, 'read_text', side_effect=failure):
                    cache, _ = self.make_cache(path=cache_path)
                self.assertTrue(cache.preserve_original)
                self.assertTrue(cache.load_issue)
                self.assert_save_skipped_completely(cache, observation())
                self.assertEqual(cache_path.read_bytes(), original)

    def test_existing_directory_is_not_missing(self):
        path = self.folder / 'public-directory.json'
        path.mkdir()
        cache, _ = self.make_cache(path=path)
        self.assertTrue(cache.preserve_original)
        self.assertTrue(cache.load_issue)
        self.assert_save_skipped_completely(cache, observation())
        self.assertTrue(path.is_dir())
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_file_not_found_with_unknown_lstat_status_is_not_safe_absence(self):
        path = self.folder / 'public-lstat-failure.json'
        original = b'{"public_opaque_original":true}'
        path.write_bytes(original)
        with patch.object(Path, 'read_text', side_effect=FileNotFoundError('public simulated read')):
            with patch.object(Path, 'lstat', side_effect=OSError('public unknown path state')):
                cache, _ = self.make_cache(path=path)
        self.assertTrue(cache.preserve_original)
        self.assertTrue(cache.load_issue)
        self.assert_save_skipped_completely(cache, observation())
        self.assertEqual(path.read_bytes(), original)

    def test_dangling_symlink_file_not_found_is_not_genuinely_absent(self):
        target = self.folder / 'missing-target.json'
        path = self.folder / 'public-link.json'
        try:
            path.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('This platform cannot create the public symlink control: ' + str(exc))
        self.assertTrue(path.is_symlink())
        self.assertFalse(path.exists())
        link_target = path.readlink()
        cache, _ = self.make_cache(path=path)
        self.assertTrue(cache.preserve_original)
        self.assertTrue(cache.load_issue)
        self.assert_save_skipped_completely(cache, observation())
        self.assertTrue(path.is_symlink())
        self.assertEqual(path.readlink(), link_target)
        self.assertFalse(target.exists())
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_symlink_to_damaged_file_retains_link_and_target_bytes(self):
        target = self.folder / 'damaged-public-target.json'
        original = b'{"public_bad_json":'
        target.write_bytes(original)
        path = self.folder / 'public-damaged-link.json'
        try:
            path.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest('This platform cannot create the public symlink control: ' + str(exc))
        link_target = path.readlink()
        cache, _ = self.make_cache(path=path)
        self.assertTrue(cache.preserve_original)
        self.assert_save_skipped_completely(cache, observation())
        self.assertTrue(path.is_symlink())
        self.assertEqual(path.readlink(), link_target)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_bad_record_and_bad_present_containers_are_quarantined(self):
        for value in NON_OBJECT_JSON:
            with self.subTest(record=repr(value)):
                cache, _ = self.make_cache({OP: value})
                self.assert_quarantined(cache)
        for field in CONTAINERS:
            for value in NON_OBJECT_JSON:
                with self.subTest(field=field, value=repr(value)):
                    bad = observation(**{field: value})
                    cache, _ = self.make_cache({OP: bad})
                    self.assert_quarantined(cache)
                    self.assertIn(ISSUE_WORDS[field], cache.issues[OP])
                    self.assertEqual(cache.records[OP], bad)

    def test_missing_or_wrong_observed_id_is_not_repaired_from_map_key(self):
        no_id = observation()
        del no_id['id']
        cases = [no_id] + [observation(id=value)
                            for value in (None, False, 1, '', GOOD_OP)]
        for bad in cases:
            with self.subTest(id=bad.get('id', 'absent')):
                cache, _ = self.make_cache({OP: bad})
                self.assert_quarantined(cache)
                self.assertEqual(cache.records[OP], bad)
                self.assertNotIn('id', cache.view(OP))

    def test_minimal_partial_records_and_omitted_defaults_stay_legal(self):
        for scope in (MISSING, 'operator_profile', 'account'):
            partial = {'id': OP}
            if scope is not MISSING:
                partial['scope'] = scope
            with self.subTest(scope=repr(scope)):
                cache, _ = self.make_cache({OP: partial})
                self.assert_usable(cache)
                self.assertFalse(cache.preserve_original)
                view = cache.view(OP)
                self.assertEqual(view, partial)
                for field in CONTAINERS + ('captured_at', 'invalid_fields',
                                           'invalid_skill_ranks', 'missing_fields'):
                    self.assertNotIn(field, view)
                self.assertEqual(view.get('fields', {}), {})
                self.assertEqual(view.get('skill_ranks', {}), {})
                self.assertEqual(view.get('captured_at', 0), 0)
                self.assertEqual(cache.records[OP], partial)

    def test_profile_alias_matches_account_key_not_profile_id(self):
        self.assertNotEqual(self.profiles[OP]['id'], OP)
        cache, _ = self.make_cache({OP: {'id': OP}})
        self.assert_usable(cache)
        bad_cache, _ = self.make_cache({OP: {'id': self.profiles[OP]['id']}})
        self.assert_quarantined(bad_cache)

    def test_all_ids_are_screened_before_good_id_can_save(self):
        good = observation(GOOD_OP)
        bad = observation(fields={'elite': []})
        payload = {GOOD_OP: good, OP: bad}
        snapshot = copy.deepcopy(payload)
        cache, path = self.make_cache(payload)
        original = path.read_bytes()
        self.assert_usable(cache, GOOD_OP)
        self.assert_quarantined(cache)
        self.assertEqual(cache.view(GOOD_OP), good)
        self.assert_save_skipped_completely(
            cache, observation(GOOD_OP, fields={'level': 70}, skill_ranks={}))
        self.assertEqual(cache.view(GOOD_OP)['fields']['level'], 70)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(payload, snapshot)

    def test_explicit_invalid_timestamps_are_quarantined_without_coercion(self):
        for stamp in (None, False, True, '100', float('nan'),
                      float('inf'), -float('inf')):
            with self.subTest(stamp=repr(stamp)):
                cache, _ = self.make_cache({OP: observation(captured_at=stamp)})
                self.assert_quarantined(cache)
                self.assertIn('时间', cache.issues[OP])

    def test_finite_timestamp_conversion_failures_are_isolated(self):
        for operation in ('localtime', 'strftime'):
            for failure in (OSError('public unsupported time'), OverflowError('public time overflow')):
                with self.subTest(operation=operation, failure=type(failure).__name__):
                    with patch.object(cache_module.time, operation, side_effect=failure):
                        cache, _ = self.make_cache({OP: observation(captured_at=100)})
                    self.assert_quarantined(cache)
                    self.assertIn('时间', cache.issues[OP])
                    self.assert_save_skipped_completely(cache)
                    self.assert_quarantined(cache)

    def test_quarantine_is_not_cleared_by_view_or_save_without_valid_observation(self):
        raw = observation()
        with patch.object(cache_module.time, 'localtime', side_effect=OSError('public transient failure')):
            cache, path = self.make_cache({OP: raw})
        original = path.read_bytes()
        self.assert_quarantined(cache)
        issue = cache.issues[OP]
        self.assert_save_skipped_completely(cache)
        self.assertEqual(cache.issues[OP], issue)
        self.assert_quarantined(cache)
        self.assert_save_skipped_completely(cache, observation(fields={'level': 60}, skill_ranks={}))
        self.assert_usable(cache)
        self.assertTrue(cache.preserve_original)
        self.assertEqual(path.read_bytes(), original)

    def test_supported_negative_timestamp_has_no_invented_positive_epoch_guard(self):
        # Inject a displayable platform conversion so this tests absence of an
        # invented positive-epoch rule, not Windows versus Linux time ranges.
        displayable = time.localtime(0)
        with patch.object(cache_module.time, 'localtime', return_value=displayable):
            cache, _ = self.make_cache({OP: observation(captured_at=-1)})
            self.assert_usable(cache)
            self.assertEqual(cache.view(OP)['captured_at'], -1)

    def test_active_cultivation_leaves_fail_at_account_boundary(self):
        maximum = self.profiles[OP]['phases'][-1]['max_level']
        values = {
            'elite': (None, False, True, 1.0, '2', -1, len(self.profiles[OP]['phases'])),
            'level': (None, False, True, 1.0, '80', 0, maximum + 1),
            'trust': (None, '100', [], {}, float('nan'), float('inf'), -1, 101),
            'potential': (None, False, True, 1.0, '1', 0, 7),
        }
        for field, invalid_values in values.items():
            for value in invalid_values:
                with self.subTest(field=field, value=repr(value)):
                    bad = observation()
                    bad['fields'][field] = value
                    cache, _ = self.make_cache({OP: bad})
                    self.assert_quarantined(cache)
                    self.assertIn(ISSUE_WORDS[field], cache.issues[OP])

    def test_valid_cultivation_boundaries_and_trust_boolean_are_preserved(self):
        for elite, phase in enumerate(self.profiles[OP]['phases']):
            for level in (1, phase['max_level']):
                for potential in (1, 6):
                    for trust in (False, True, 0, 100, 0.5):
                        with self.subTest(elite=elite, level=level, potential=potential, trust=trust):
                            fields = {'elite': elite, 'level': level, 'potential': potential,
                                      'trust': trust, 'selected_skill': 1}
                            cache, _ = self.make_cache({OP: observation(fields=fields)})
                            self.assert_usable(cache)
                            self.assertEqual(cache.view(OP)['fields'], fields)
                            self.assertIs(type(cache.view(OP)['fields']['trust']), type(trust))

    def test_falsy_module_identity_keeps_any_ignored_stage_exactly(self):
        for module_id in (None, False, 0, '', [], {}):
            for stage in (None, False, True, 0, 1, 1.0, '1', [], {'opaque': 'stage'}):
                with self.subTest(module_id=repr(module_id), stage=repr(stage)):
                    fields = {'module_id': module_id, 'module_level': stage}
                    cache, _ = self.make_cache({OP: observation(fields=fields, skill_ranks={})})
                    self.assert_usable(cache)
                    self.assertEqual(cache.view(OP)['fields'], fields)

    def test_truthy_module_stage_rules_preserve_locked_but_valid_module(self):
        module = self.profiles[OP]['modules'][0]
        for stage in (1, len(module['levels'])):
            for fields in ({'elite': 2, 'level': 80}, {'elite': 1, 'level': 1}):
                value = {**fields, 'module_id': self.module_id, 'module_level': stage}
                cache, _ = self.make_cache({OP: observation(fields=value, skill_ranks={})})
                self.assert_usable(cache)
                self.assertEqual(cache.view(OP)['fields'], value)
        for stage in (None, False, True, 0, len(module['levels']) + 1, 1.0, '1', [], {}):
            with self.subTest(stage=repr(stage)):
                cache, _ = self.make_cache({OP: observation(
                    fields={'module_id': self.module_id, 'module_level': stage}, skill_ranks={})})
                self.assert_quarantined(cache)
                self.assertIn('模组', cache.issues[OP])
        cache, _ = self.make_cache({OP: observation(
            fields={'module_id': 'public_unknown_module', 'module_level': 1}, skill_ranks={})})
        self.assert_quarantined(cache)

    def test_active_rank_bounds_and_non_boolean_integer_requirement(self):
        limit = min(10, len(self.profiles[OP]['skills'][0]['levels']))
        for rank in (None, False, True, 1.0, '7', [], {}, 0, limit + 1):
            with self.subTest(rank=repr(rank)):
                cache, _ = self.make_cache({OP: observation(skill_ranks={'1': rank})})
                self.assert_quarantined(cache)
                self.assertIn('技能', cache.issues[OP])
        for rank in (1, limit):
            cache, _ = self.make_cache({OP: observation(skill_ranks={'1': rank})})
            self.assert_usable(cache)
        cache, _ = self.make_cache({OP: observation(fields={'elite': 1}, skill_ranks={'1': 8})})
        self.assert_quarantined(cache)
        cache, _ = self.make_cache({OP: observation(fields={'elite': 1}, skill_ranks={'1': 7})})
        self.assert_usable(cache)

    def test_inactive_rank_is_formatter_safe_without_new_numeric_schema(self):
        # Mechanist S3 is not available at E0; formatter can still display it.
        for rank in (None, False, True, 0, -1, 1.0, 99):
            with self.subTest(rank=rank):
                cache, _ = self.make_cache({OP: observation(fields={'elite': 0}, skill_ranks={'3': rank})})
                self.assert_usable(cache)
                self.assertEqual(cache.view(OP)['skill_ranks']['3'], rank)
        for rank in ('7', [], {}):
            with self.subTest(rank=repr(rank)):
                cache, _ = self.make_cache({OP: observation(fields={'elite': 0}, skill_ranks={'3': rank})})
                self.assert_quarantined(cache)

    def test_masked_inactive_rank_is_ignored_but_active_rank_still_consumed_by_gui(self):
        for rank in ('bad rank', [], {'opaque': 'masked rank'}):
            with self.subTest(rank=repr(rank)):
                inactive = observation(fields={'elite': 0}, skill_ranks={'3': rank},
                                       invalid_skill_ranks=['3'])
                cache, _ = self.make_cache({OP: inactive})
                self.assert_usable(cache)
                self.assertEqual(cache.view(OP)['skill_ranks'], inactive['skill_ranks'])
                active = observation(fields={'elite': 2}, skill_ranks={'1': rank},
                                     invalid_skill_ranks=['1'])
                cache, _ = self.make_cache({OP: active})
                self.assert_quarantined(cache)

    def test_out_of_choice_selected_skill_and_no_skill_rank_are_inert(self):
        for selected in (None, False, 0, 99, '1', [], {'opaque': 'selected'}):
            with self.subTest(selected=repr(selected)):
                cache, _ = self.make_cache({OP: observation(
                    fields={'elite': 0, 'selected_skill': selected}, skill_ranks={'1': 7})})
                self.assert_usable(cache)
                self.assertEqual(cache.view(OP)['fields']['selected_skill'], selected)
        op = 'char_285_medic2'
        payload = observation(op, fields={'elite': 0, 'level': 30, 'selected_skill': {'ignored': True}},
                              skill_ranks={'1': {'unused': True}, 'future': [None]})
        cache, _ = self.make_cache({op: payload})
        self.assert_usable(cache, op)
        self.assertEqual(cache.view(op), payload)

    def test_formatter_consumed_bad_metadata_is_isolated(self):
        cases = [
            ('invalid_fields', None), ('invalid_fields', False), ('invalid_fields', 0),
            ('invalid_fields', [['elite']]), ('invalid_fields', [{'public': 'unhashable'}]),
            ('invalid_skill_ranks', None), ('invalid_skill_ranks', False), ('invalid_skill_ranks', 0),
            ('missing_fields', None), ('missing_fields', False), ('missing_fields', 0),
            ('missing_fields', [None]), ('missing_fields', [1]),
            ('missing_fields', [[]]), ('missing_fields', [{}]),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=repr(value)):
                # Nonempty ranks makes invalid_skill_ranks actual consumption.
                cache, _ = self.make_cache({OP: observation(**{field: value})})
                self.assert_quarantined(cache)
                self.assertIn(ISSUE_WORDS[field], cache.issues[OP])

    def test_safe_metadata_unknown_keys_and_nested_sources_stay_exact(self):
        raw = observation(
            invalid_fields=['public_ignored_field', 42, None],
            invalid_skill_ranks=[[], {}, 'future_rank'],
            missing_fields={'future_field': {'ignored_value': True}},
            extra_metadata={'opaque': [None, False, 0, {'exact': 'kept'}]})
        raw['fields']['public_ignored_leaf'] = {'opaque': [None, {'exact': True}]}
        raw['skill_ranks']['future_rank'] = {'opaque': [None, 'kept']}
        raw['sources']['nested'] = {'items': [None, False, {'raw': 'kept'}]}
        raw['field_times']['unconsumed'] = {'opaque': ['kept']}
        raw['skill_times']['unconsumed'] = [None, {'raw': 'kept'}]
        before = copy.deepcopy(raw)
        cache, _ = self.make_cache({OP: raw})
        self.assert_usable(cache)
        self.assertEqual(cache.records[OP], before)
        self.assertEqual(cache.view(OP), before)
        self.assertEqual(raw, before)
        view = cache.view(OP)
        view['fields']['public_ignored_leaf']['opaque'].append('changed only in view')
        view['extra_metadata']['opaque'].clear()
        self.assertEqual(cache.records[OP], before)
        self.assertEqual(cache.view(OP), before)

    def test_unknown_catalog_id_is_preserved_opaque_during_clean_save(self):
        unknown = {'id': UNKNOWN_OP, 'fields': [None, False],
                   'future_metadata': {'opaque': ['kept exactly']}}
        payload = {UNKNOWN_OP: unknown, GOOD_OP: observation(GOOD_OP)}
        snapshot = copy.deepcopy(payload)
        cache, path = self.make_cache(payload)
        self.assertFalse(cache.preserve_original)
        self.assertNotIn(UNKNOWN_OP, cache.issues)
        self.assertEqual(cache.records[UNKNOWN_OP], unknown)
        self.assertEqual(cache.view(UNKNOWN_OP), {})
        self.assertTrue(cache.observe(observation(GOOD_OP, fields={'level': 70}), 200))
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))[UNKNOWN_OP], unknown)
        self.assertEqual(payload, snapshot)
        self.assertFalse(cache.observe(observation(UNKNOWN_OP), 300))
        self.assertEqual(cache.records[UNKNOWN_OP], unknown)

    def test_account_scope_run_is_quarantined_and_other_run_effects_suppressed(self):
        foreign = observation(scope='run', recruitment_kind='emergency_hire', advanced=True)
        cache, _ = self.make_cache({OP: foreign})
        self.assert_quarantined(cache)
        self.assertEqual(cache.records[OP], foreign)
        for scope in ('operator_profile', 'account'):
            raw = observation(scope=scope, recruitment_kind='emergency_hire', advanced=True,
                              char_buff_ids=['public_buff'], char_buffs_complete=True,
                              char_buff_absent_ids=['public_absent'],
                              char_buff_pending_ids=['public_pending'],
                              run_confirmed_fields=['elite'],
                              extra_metadata={'run_history': [None, {'opaque': 'kept'}]})
            before = copy.deepcopy(raw)
            cache, _ = self.make_cache({OP: raw})
            self.assert_usable(cache)
            view = cache.view(OP)
            self.assertNotEqual(view.get('scope'), 'run')
            for key in ('recruitment_kind', 'advanced', 'char_buff_ids', 'char_buffs_complete',
                        'char_buff_absent_ids', 'char_buff_pending_ids', 'run_confirmed_fields'):
                self.assertNotIn(key, view)
            self.assertEqual(view['fields'], before['fields'])
            self.assertEqual(view['extra_metadata'], before['extra_metadata'])
            self.assertEqual(cache.records[OP], before)
            self.assertEqual(raw, before)

    def test_older_observation_is_rejected_equal_time_accepted_union_preserved(self):
        old = observation(fields={'elite': 2, 'level': 80, 'trust': 50},
                          skill_ranks={'1': 7, '2': 8},
                          sources={'level': {'source': 'old'}, 'trust': 'old'},
                          field_times={'level': 90, 'trust': 90},
                          skill_times={'1': 90, '2': 90},
                          old_extra={'producer_used_to_drop': True})
        cache, path = self.make_cache({OP: old})
        old_bytes = path.read_bytes()
        older = observation(fields={'level': 60}, skill_ranks={1: 9})
        older_before = copy.deepcopy(older)
        self.assertFalse(cache.observe(older, 99))
        self.assertEqual(cache.records[OP], old)
        self.assertEqual(path.read_bytes(), old_bytes)
        self.assertEqual(older, older_before)
        equal = {'id': OP, 'scope': 'operator_profile',
                 'fields': {'level': 70, 'potential': 2}, 'skill_ranks': {1: 9},
                 'sources': {'level': {'source': 'new'}, 'potential': 'new'},
                 'new_extra': {'producer': 'retains incoming'}}
        equal_before = copy.deepcopy(equal)
        self.assertTrue(cache.observe(equal, 100))
        merged = cache.records[OP]
        self.assertEqual(merged['fields'], {'elite': 2, 'level': 70, 'trust': 50, 'potential': 2})
        self.assertEqual(merged['skill_ranks'], {'1': 9, '2': 8})
        self.assertEqual(merged['sources'], {'level': {'source': 'new'}, 'trust': 'old', 'potential': 'new'})
        self.assertEqual(merged['field_times'], {'level': 100, 'trust': 90, 'potential': 100})
        self.assertEqual(merged['skill_times'], {'1': 100, '2': 90})
        self.assertEqual(merged['captured_at'], 100)
        self.assertIs(merged['merged_from_pages'], True)
        self.assertNotIn('old_extra', merged)
        self.assertEqual(merged['new_extra'], equal_before['new_extra'])
        self.assertEqual(equal, equal_before)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))[OP], merged)

    def test_timestamp_only_or_source_only_update_retains_original_changed_save_decision(self):
        old = observation()
        cache, path = self.make_cache({OP: old})
        original = path.read_bytes()
        fresh = observation(sources={'level': 'new source'}, extra_metadata={'new': True})
        before = copy.deepcopy(fresh)
        with patch.object(cache, 'save', wraps=cache.save) as save:
            self.assertTrue(cache.observe(fresh, 200))
            save.assert_not_called()
        self.assertEqual(cache.records[OP]['captured_at'], 200)
        self.assertEqual(cache.records[OP]['sources']['level'], 'new source')
        self.assertEqual(cache.records[OP]['extra_metadata'], {'new': True})
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(fresh, before)
        same = observation()
        cache, _ = self.make_cache({OP: same})
        with patch.object(cache, 'save', wraps=cache.save) as save:
            self.assertTrue(cache.observe(observation(), 100))
            save.assert_not_called()

    def test_absent_old_timestamp_keeps_implicit_zero_ordering(self):
        cache, path = self.make_cache({OP: {'id': OP, 'fields': {'trust': 10}}})
        original = path.read_bytes()
        displayable = time.localtime(0)
        with patch.object(cache_module.time, 'localtime', return_value=displayable):
            self.assertFalse(cache.observe(observation(fields={'level': 60}, skill_ranks={}), -1))
        self.assertEqual(path.read_bytes(), original)
        self.assertTrue(cache.observe(observation(fields={'level': 60}, skill_ranks={}), 0))
        self.assertEqual(cache.records[OP]['fields'], {'trust': 10, 'level': 60})
        self.assertEqual(cache.records[OP]['captured_at'], 0)

    def test_clean_missing_id_keeps_original_zero_ordering_and_is_not_damage(self):
        cache, path = self.make_cache()
        displayable = time.localtime(0)
        fresh = observation(fields={'level': 60}, skill_ranks={})
        with patch.object(cache_module.time, 'localtime', return_value=displayable):
            with patch.object(cache, 'save', wraps=cache.save) as save:
                self.assertFalse(cache.observe(fresh, -1))
                save.assert_not_called()
        self.assertFalse(path.exists())
        self.assertEqual(cache.records, {})
        self.assertEqual(cache.issues, {})
        self.assertFalse(cache.preserve_original)
        with patch.object(cache, 'save', wraps=cache.save) as save:
            self.assertTrue(cache.observe(fresh, 0))
            save.assert_called_once_with()
        self.assertTrue(path.exists())
        self.assertFalse(cache.preserve_original)

    def test_bad_old_record_accepts_displayable_negative_recovery_without_old_zero_guard(self):
        bad = observation(fields={'elite': []}, captured_at=999999)
        cache, path = self.make_cache({OP: bad})
        original = path.read_bytes()
        fresh = {'id': OP, 'scope': 'operator_profile', 'fields': {'level': 60},
                 'skill_ranks': {}, 'sources': {'level': 'fresh negative stamp'}}
        displayable = time.localtime(0)
        with patch.object(cache_module.time, 'localtime', return_value=displayable):
            self.assert_save_skipped_completely(cache, fresh, at=-1)
            self.assert_usable(cache)
            self.assertEqual(cache.view(OP)['fields'], {'level': 60})
            self.assertEqual(cache.view(OP)['captured_at'], -1)
        self.assertTrue(cache.preserve_original)
        self.assertEqual(path.read_bytes(), original)

    def test_bad_old_facts_never_join_recovery_and_original_protection_is_permanent(self):
        bad = observation(fields={'elite': [], 'level': 80, 'trust': 50},
                          skill_ranks={'1': 'bad'}, captured_at=999999,
                          sources={'trust': 'bad old'}, field_times={'trust': 'bad old'},
                          skill_times={'1': 'bad old'})
        cache, path = self.make_cache({OP: bad, GOOD_OP: observation(GOOD_OP)})
        original = path.read_bytes()
        self.assert_quarantined(cache)
        original_notice = cache.notice(OP)
        fresh = {'id': OP, 'scope': 'operator_profile', 'fields': {'level': 60},
                 'skill_ranks': {}, 'sources': {'level': 'fresh public'}}
        before = copy.deepcopy(fresh)
        self.assert_save_skipped_completely(cache, fresh, at=200)
        self.assert_usable(cache)
        self.assertEqual(cache.view(OP)['fields'], {'level': 60})
        self.assertEqual(cache.view(OP)['skill_ranks'], {})
        self.assertEqual(cache.view(OP)['sources'], {'level': 'fresh public'})
        self.assertEqual(cache.view(OP)['field_times'], {'level': 200})
        self.assertEqual(cache.view(OP)['skill_times'], {})
        self.assertEqual(cache.view(OP)['captured_at'], 200)
        self.assertTrue(cache.preserve_original)
        self.assertTrue(cache.notice(OP))
        self.assertNotEqual(cache.notice(OP), original_notice)
        self.assertEqual(cache.notice(OP), cache.notice(GOOD_OP))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(fresh, before)
        self.assert_save_skipped_completely(cache, observation(fields={'trust': 10}, skill_ranks={}), at=300)
        self.assertEqual(path.read_bytes(), original)

    def test_invalid_new_observations_cannot_rebuild_damaged_id_or_trigger_save(self):
        bad = observation(fields={'elite': []})
        cache, path = self.make_cache({OP: bad})
        original = path.read_bytes()
        invalids = [({}, 200), ({'id': GOOD_OP, 'fields': []}, 200),
                    (observation(fields={'level': None}), 200),
                    (observation(), None), (observation(), True),
                    (observation(), float('inf')), (observation(scope='run'), 200)]
        for fresh, captured_at in invalids:
            with self.subTest(fresh=repr(fresh), captured_at=repr(captured_at)):
                before = copy.deepcopy(fresh)
                with patch.object(cache, 'save', wraps=cache.save) as save:
                    self.assertFalse(cache.observe(fresh, captured_at))
                    save.assert_not_called()
                self.assertEqual(fresh, before)
                self.assert_quarantined(cache)
                self.assertEqual(cache.records[OP], bad)
                self.assertEqual(path.read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
