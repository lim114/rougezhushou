"""SOURCE draft for exact account persistence and failed-save boundaries.

Author has not imported or run this module, AccountCache, or any project API.
Root must integrate against the actually completed096 tree and run it fresh.
All fixtures are public, temporary and independent of the user's state.
"""
import json
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from rouge.account_cache import AccountCache
from rouge.catalog import catalog, operator_profiles


OP = 'mechanist'
OTHER = 'kaltsit'
UNKNOWN = 'public_unknown_persistence'
MISSING = object()


def observation(level=2, **extra):
    value = {'id': OP, 'scope': 'operator_profile',
             'fields': {'level': level}, 'skill_ranks': {}}
    value.update(extra)
    return value


class AccountPersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = operator_profiles()
        cls.implemented = tuple(catalog()['operators'])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.serial = 0

    def cache(self, payload=MISSING, *, path=None):
        self.serial += 1
        path = path or self.folder / ('public-%d.json' % self.serial)
        if payload is not MISSING:
            # ASCII transport is necessary: the default093 fixture helper
            # cannot initially write a lone surrogate with strict UTF-8.
            path.write_bytes(json.dumps(payload, ensure_ascii=True).encode('ascii'))
        return AccountCache(path, self.profiles, self.implemented), path

    def original(self, **extra):
        return {OP: {'id': OP, 'scope': 'operator_profile',
                     'fields': {'level': 1}, 'skill_ranks': {}, 'captured_at': 100},
                **extra}

    def assert_saved_exact(self, cache, path):
        self.assertFalse(cache.preserve_original)
        self.assertIsNone(cache.save_issue)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')), cache.records)
        self.assertFalse(path.with_suffix('.tmp').exists())

    def assert_failed_notice(self, cache):
        text = cache.notice(OP)
        self.assertIn('保存未完成', text)
        self.assertIn('有效培养记录仍可在当前运行使用', text)
        self.assertIn('新的读取未保存到账号档案', text)
        self.assertIn('本次不再自动写入或覆盖账号档案', text)
        self.assertNotIn('原账号档案文件已保留', text)
        self.assertIsNone(cache.load_issue)

    def test_ordinary_unicode_json_keeps_original_platform_write_bytes(self):
        opaque = {'label': '中文', 'emoji': '\U0001f642', 'literal': '\\ud800',
                  'typed': [None, False, 0, 0.0, -0.0, 1.5]}
        cache, path = self.cache(self.original(**{UNKNOWN: opaque}))
        self.assertTrue(cache.observe(observation(), 200))
        self.assert_saved_exact(cache, path)
        reference = self.folder / 'original-writer.json'
        reference.write_text(json.dumps(cache.records, ensure_ascii=False, indent=2),
                             encoding='utf-8')
        self.assertEqual(path.read_bytes(), reference.read_bytes())
        self.assertEqual(cache.records[UNKNOWN], opaque)

    def test_ascii_loaded_lone_surrogate_key_and_value_preserve_decoded_points(self):
        for value in ('\ud800', '\udbff', '\udc00', '\udfff'):
            for role in ('key', 'value'):
                with self.subTest(codepoint=hex(ord(value)), role=role):
                    opaque = {value: 'public'} if role == 'key' else {'public': value}
                    cache, path = self.cache(self.original(**{UNKNOWN: opaque}))
                    before = cache.records[UNKNOWN]
                    self.assertTrue(cache.observe(observation(), 200))
                    self.assert_saved_exact(cache, path)
                    self.assertEqual(cache.records[UNKNOWN], before)
                    restored = json.loads(path.read_text(encoding='utf-8'))[UNKNOWN]
                    point = next(iter(restored)) if role == 'key' else restored['public']
                    self.assertEqual([ord(c) for c in point], [ord(value)])

    def test_same_operator_unconsumed_mapping_leaves_survive_lossless_save(self):
        raw = self.original()[OP]
        raw['fields']['opaque'] = '\ud800x\udc00'
        raw['sources'] = {'opaque': '\udfff'}
        raw['field_times'] = {'opaque': '\udbff'}
        raw['skill_times'] = {'opaque': '\udc00'}
        cache, path = self.cache({OP: raw})
        self.assertTrue(cache.observe(observation(), 200))
        self.assert_saved_exact(cache, path)
        for key in ('fields', 'sources', 'field_times', 'skill_times'):
            self.assertEqual(cache.records[OP][key]['opaque'], raw[key]['opaque'])

    def test_native_incoming_lone_points_and_low_high_order_are_not_replaced(self):
        for value in ('\ud800', '\udc00', '\ud800x\udc00', '\udc00\ud800'):
            with self.subTest(codepoints=[hex(ord(c)) for c in value]):
                cache, path = self.cache(self.original())
                incoming = observation(fields={'level': 2, 'opaque': value})
                self.assertTrue(cache.observe(incoming, 200))
                self.assert_saved_exact(cache, path)
                self.assertEqual(cache.view(OP)['fields']['opaque'], value)
                self.assertEqual(incoming['fields']['opaque'], value)

    def test_ascii_escaped_pair_already_decodes_to_normal_emoji(self):
        raw = (b'{"public_unknown_persistence":{"opaque":"\\ud83d\\ude42"},'
               b'"mechanist":{"id":"mechanist","fields":{"level":1}}}')
        path = self.folder / 'paired-source.json'
        path.write_bytes(raw)
        cache, _ = self.cache(path=path)
        self.assertEqual(cache.records[UNKNOWN]['opaque'], '\U0001f642')
        self.assertTrue(cache.observe(observation(), 200))
        self.assert_saved_exact(cache, path)
        self.assertEqual(cache.records[UNKNOWN]['opaque'], '\U0001f642')

    def test_literal_backslash_u_stays_distinct_from_surrogate_and_emoji(self):
        value = '\\ud800\\udc00'
        cache, path = self.cache(self.original(**{UNKNOWN: {'opaque': value}}))
        self.assertTrue(cache.observe(observation(), 200))
        self.assert_saved_exact(cache, path)
        self.assertEqual(cache.records[UNKNOWN]['opaque'], value)
        self.assertEqual(len(cache.records[UNKNOWN]['opaque']), 12)
        self.assertNotEqual(cache.records[UNKNOWN]['opaque'], '\U00010000')

    def test_adjacent_native_pair_refuses_without_changing_accepted_memory(self):
        for value in ('\ud800\udc00', '\udbff\udfff'):
            for role in ('key', 'value'):
                with self.subTest(codepoints=[hex(ord(c)) for c in value], role=role):
                    cache, path = self.cache(self.original())
                    original = path.read_bytes()
                    fields = {'level': 2, value: 'public'} if role == 'key' else {'level': 2, 'opaque': value}
                    incoming = observation(fields=fields)
                    with ExitStack() as stack:
                        spies = [stack.enter_context(patch.object(Path, name))
                                 for name in ('mkdir', 'write_text', 'replace')]
                        self.assertTrue(cache.observe(incoming, 200))
                        for spy in spies:
                            spy.assert_not_called()
                    self.assertTrue(cache.preserve_original)
                    self.assertEqual(cache.view(OP)['fields'], fields)
                    self.assertEqual(incoming['fields'], fields)
                    self.assertEqual(path.read_bytes(), original)
                    self.assertFalse(path.with_suffix('.tmp').exists())
                    self.assert_failed_notice(cache)
                    self.assertIn('无法无损保存', cache.notice(OP))

    def test_lossy_refusal_preserves_existing_temporary_and_original_files(self):
        cache, path = self.cache(self.original())
        original = path.read_bytes()
        pending = path.with_suffix('.tmp')
        pending.write_bytes(b'public-existing-temporary')
        self.assertTrue(cache.observe(observation(fields={'level': 2, 'opaque': '\ud800\udc00'}), 200))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(pending.read_bytes(), b'public-existing-temporary')
        self.assert_failed_notice(cache)

    def test_lossy_refusal_of_missing_file_does_not_create_parent_or_claim_original(self):
        path = self.folder / 'not-created' / 'account.json'
        cache, _ = self.cache(path=path)
        self.assertTrue(cache.observe(observation(fields={'level': 2, 'opaque': '\ud800\udc00'}), 200))
        self.assertFalse(path.parent.exists())
        self.assertFalse(path.exists())
        self.assertFalse(path.with_suffix('.tmp').exists())
        self.assert_failed_notice(cache)

    def test_each_oserror_write_stage_preserves_memory_and_target(self):
        for method in ('mkdir', 'write_text', 'replace'):
            for failure in (PermissionError('public denied'), OSError('public IO failure'),
                            FileExistsError('public conflict')):
                with self.subTest(stage=method, failure=type(failure).__name__):
                    cache, path = self.cache(self.original())
                    original = path.read_bytes()
                    incoming = observation()
                    with patch.object(Path, method, side_effect=failure):
                        self.assertTrue(cache.observe(incoming, 200))
                    self.assertTrue(cache.preserve_original)
                    self.assertEqual(cache.view(OP)['fields']['level'], 2)
                    self.assertEqual(incoming['fields'], {'level': 2})
                    self.assertEqual(path.read_bytes(), original)
                    self.assert_failed_notice(cache)

    def test_partial_temporary_write_failure_is_not_deleted_or_published(self):
        cache, path = self.cache(self.original())
        original = path.read_bytes()
        pending = path.with_suffix('.tmp')
        old_write_text = Path.write_text

        def interrupted_write(file, text, *args, **kwargs):
            if file == pending:
                file.write_bytes(b'public-partial-write')
                raise OSError('public interrupted write')
            return old_write_text(file, text, *args, **kwargs)

        with patch.object(Path, 'write_text', new=interrupted_write):
            self.assertTrue(cache.observe(observation(), 200))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(pending.read_bytes(), b'public-partial-write')
        self.assertEqual(cache.view(OP)['fields']['level'], 2)
        self.assert_failed_notice(cache)

    def test_replace_failure_keeps_complete_temporary_as_separate_evidence(self):
        cache, path = self.cache(self.original())
        original = path.read_bytes()
        with patch.object(Path, 'replace', side_effect=PermissionError('public replacement denied')):
            self.assertTrue(cache.observe(observation(), 200))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(json.loads(path.with_suffix('.tmp').read_text(encoding='utf-8')), cache.records)
        self.assert_failed_notice(cache)

    def test_save_failure_of_absent_original_is_reported_without_invented_file(self):
        cache, path = self.cache()
        with patch.object(Path, 'mkdir', side_effect=PermissionError('public directory denied')):
            self.assertTrue(cache.observe(observation(), 200))
        self.assertFalse(path.exists())
        self.assertEqual(cache.view(OP)['fields']['level'], 2)
        self.assert_failed_notice(cache)

    def test_failed_session_keeps_changed_unchanged_and_other_valid_reads_without_more_io(self):
        cache, path = self.cache(self.original())
        original = path.read_bytes()
        with patch.object(Path, 'mkdir', side_effect=OSError('public initial failure')):
            self.assertTrue(cache.observe(observation(), 200))
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            self.assertTrue(cache.observe(observation(3), 201))
            self.assertTrue(cache.observe(observation(3), 202))
            self.assertTrue(cache.observe({'id': OTHER, 'fields': {'level': 2}}, 203))
            self.assertFalse(cache.save())
            for spy in spies:
                spy.assert_not_called()
        self.assertEqual(cache.view(OP)['fields']['level'], 3)
        self.assertEqual(cache.view(OTHER)['fields']['level'], 2)
        self.assertEqual(path.read_bytes(), original)
        self.assert_failed_notice(cache)

    def test_save_notice_keeps_later_per_operator_invalidity_visible(self):
        cache, _ = self.cache(self.original())
        with patch.object(Path, 'mkdir', side_effect=OSError('public initial failure')):
            self.assertTrue(cache.observe(observation(), 200))
        cache.records[OTHER] = {'id': OTHER, 'fields': {'level': None}}
        self.assertEqual(cache.view(OTHER), {})
        text = cache.notice(OTHER)
        self.assertIn('账号参考的等级不可用', text)
        self.assertIn('保存未完成', text)
        self.assertIn('缺失项使用标注的档案预览', text)
        self.assertEqual(cache.view(OP)['fields']['level'], 2)
        self.assertNotIn('账号参考的等级不可用', cache.notice(OP))

    def test_metadata_only_native_pair_follows_existing_no_save_decision(self):
        cache, path = self.cache(self.original())
        original = path.read_bytes()
        incoming = observation(1, sources={'opaque': '\ud800\udc00'})
        self.assertTrue(cache.observe(incoming, 200))
        self.assertIsNone(cache.save_issue)
        self.assertFalse(cache.preserve_original)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(cache.records[OP]['sources']['opaque'], '\ud800\udc00')
        self.assertTrue(cache.observe(observation(), 201))
        self.assertTrue(cache.preserve_original)
        self.assertEqual(cache.view(OP)['fields']['level'], 2)
        self.assertEqual(cache.records[OP]['sources']['opaque'], '\ud800\udc00')
        self.assertEqual(path.read_bytes(), original)
        self.assert_failed_notice(cache)

    def test_non_io_errors_are_not_silently_converted_to_failed_save(self):
        for method, failure in (('mkdir', RuntimeError('public programming error')),
                                ('write_text', ValueError('public non-IO error'))):
            with self.subTest(stage=method, failure=type(failure).__name__):
                cache, _ = self.cache(self.original())
                with patch.object(Path, method, side_effect=failure):
                    with self.assertRaises(type(failure)):
                        cache.observe(observation(), 200)
                self.assertIsNone(cache.save_issue)
                self.assertFalse(cache.preserve_original)

    def test_new_independent_session_reads_original_without_resetting_failed_object(self):
        cache, path = self.cache(self.original())
        with patch.object(Path, 'mkdir', side_effect=OSError('public initial failure')):
            self.assertTrue(cache.observe(observation(), 200))
        reopened, _ = self.cache(path=path)
        self.assertIsNone(reopened.save_issue)
        self.assertFalse(reopened.preserve_original)
        self.assertEqual(reopened.view(OP)['fields']['level'], 1)
        self.assertTrue(reopened.observe(observation(3), 201))
        self.assert_saved_exact(reopened, path)
        self.assertTrue(cache.preserve_original)
        self.assertEqual(cache.view(OP)['fields']['level'], 2)
        self.assert_failed_notice(cache)


if __name__ == '__main__':
    unittest.main()
