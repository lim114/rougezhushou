"""Saving must not truncate a retained temporary entry or its linked target."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge.account_cache import AccountCache
from rouge.run_state import RunState
from rouge.persistence_install import record_save_lock


class TemporaryRecordNoClobberTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix='public-temporary-record-261-')
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)

    def model(self, kind, existing):
        path = self.folder / f'{kind}-{existing}.json'
        model = RunState(path) if kind == 'run' else AccountCache(path, {})
        if existing:
            self.assertTrue(model.save())
        original = path.read_bytes() if existing else None
        if kind == 'run':
            model.state['notice'] = 'public new in-memory state'
        return model, path, original

    def assert_failed_and_latched(self, model, path, original):
        self.assertFalse(model.save())
        self.assertIsNotNone(model.save_issue)
        if isinstance(model, RunState):
            self.assertTrue(model.persistence_notice())
        else:
            self.assertTrue(model.preserve_original)
        self.assertFalse(model.save())
        if original is None:
            self.assertFalse(path.exists())
        else:
            self.assertEqual(path.read_bytes(), original)

    def assert_saved_safely(self, model, path):
        self.assertTrue(model.save())
        self.assertIsNone(model.save_issue)
        expected = model.state if isinstance(model, RunState) else model.records
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')), expected)
        self.assertTrue(model.save())

    def retained_temporary(self, temporary):
        archives = list(temporary.parent.glob(temporary.name + '.preserved-*'))
        self.assertLessEqual(len(archives), 1)
        return archives[0] if archives else temporary

    def test_existing_regular_temporary_is_retained_for_first_and_later_saves(self):
        for kind in ('run', 'cache'):
            for existing in (False, True):
                with self.subTest(kind=kind, existing=existing):
                    model, path, original = self.model(kind, existing)
                    temporary = path.with_suffix('.tmp')
                    retained = b'PUBLIC incomplete previous write\n'
                    temporary.write_bytes(retained)
                    self.assert_saved_safely(model, path)
                    self.assertEqual(self.retained_temporary(temporary).read_bytes(), retained)

    def test_live_temporary_symlink_does_not_write_its_original_target(self):
        for kind in ('run', 'cache'):
            for existing in (False, True):
                with self.subTest(kind=kind, existing=existing):
                    model, path, original = self.model(kind, existing)
                    target = self.folder / f'{kind}-{existing}-retained.txt'
                    retained = b'PUBLIC linked original must survive\n'
                    target.write_bytes(retained)
                    temporary = path.with_suffix('.tmp')
                    temporary.symlink_to(target)
                    self.assert_saved_safely(model, path)
                    self.assertEqual(target.read_bytes(), retained)
                    self.assertEqual(self.retained_temporary(temporary).read_bytes(), retained)

    def test_dangling_temporary_symlink_does_not_create_the_target(self):
        for kind in ('run', 'cache'):
            for existing in (False, True):
                with self.subTest(kind=kind, existing=existing):
                    model, path, original = self.model(kind, existing)
                    target = self.folder / f'{kind}-{existing}-absent.txt'
                    path.with_suffix('.tmp').symlink_to(target)
                    self.assert_saved_safely(model, path)
                    self.assertFalse(target.exists())

    def test_hard_linked_temporary_does_not_truncate_another_record(self):
        for kind in ('run', 'cache'):
            for existing in (False, True):
                with self.subTest(kind=kind, existing=existing):
                    model, path, original = self.model(kind, existing)
                    target = self.folder / f'{kind}-{existing}-hard-link.txt'
                    retained = b'PUBLIC other hard-linked record\n'
                    target.write_bytes(retained)
                    temporary = path.with_suffix('.tmp')
                    os.link(target, temporary)
                    self.assert_saved_safely(model, path)
                    self.assertEqual(target.read_bytes(), retained)
                    self.assertEqual(self.retained_temporary(temporary).read_bytes(), retained)

    def test_temporary_directory_and_its_children_survive_the_save(self):
        for kind in ('run', 'cache'):
            with self.subTest(kind=kind):
                model, path, original = self.model(kind, False)
                temporary = path.with_suffix('.tmp')
                temporary.mkdir()
                child = temporary / 'public-retained.txt'
                child.write_bytes(b'PUBLIC retained child')
                self.assert_failed_and_latched(model, path, original)
                self.assertEqual(child.read_bytes(), b'PUBLIC retained child')

    def test_explicit_new_run_retains_both_unreadable_original_and_older_temp(self):
        path = self.folder / 'unreadable.json'
        original = b'{"public interrupted original":'
        path.write_bytes(original)
        temporary = path.with_suffix('.tmp')
        retained = b'PUBLIC conflicting write evidence'
        temporary.write_bytes(retained)
        model = RunState(path)
        self.assertTrue(model.preserve_unreadable)
        old_id = model.state['id']
        model.reset()
        self.assertNotEqual(model.state['id'], old_id)
        self.assertTrue(model.save())
        self.assertEqual(model.archived_original.read_bytes(), original)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')), model.state)
        self.assertEqual(self.retained_temporary(temporary).read_bytes(), retained)

    def test_uuid_temporary_conflict_never_replaces_an_existing_alternative(self):
        class PublicFixedUUID:
            hex = '0' * 32
        for kind in ('run', 'cache'):
            with self.subTest(kind=kind):
                model, path, original = self.model(kind, True)
                temporary = path.with_suffix('.tmp')
                temporary.write_bytes(b'PUBLIC stable temporary')
                archive = temporary.with_name(temporary.name + '.preserved-' + '0' * 32)
                archive.write_bytes(b'PUBLIC pre-existing retained temporary')
                alternative = path.with_name(path.name + '.' + '0' * 32 + '.tmp')
                alternative.write_bytes(b'PUBLIC pre-existing UUID temporary')
                with patch('uuid.uuid4', return_value=PublicFixedUUID()):
                    self.assert_failed_and_latched(model, path, original)
                self.assertEqual(temporary.read_bytes(), b'PUBLIC stable temporary')
                self.assertEqual(archive.read_bytes(), b'PUBLIC pre-existing retained temporary')
                self.assertEqual(alternative.read_bytes(), b'PUBLIC pre-existing UUID temporary')

    def test_destination_named_tmp_is_not_used_as_its_own_temporary(self):
        for kind in ('run', 'cache'):
            with self.subTest(kind=kind):
                path = self.folder / f'{kind}.tmp'
                model = RunState(path) if kind == 'run' else AccountCache(path, {})
                self.assert_saved_safely(model, path)

    def test_private_directory_name_collision_never_enters_an_old_namespace(self):
        for kind in ('run', 'cache'):
            for entry_kind in ('file', 'directory', 'live_link', 'dangling_link'):
                with self.subTest(kind=kind, entry_kind=entry_kind):
                    folder = self.folder / f'{kind}-{entry_kind}'
                    folder.mkdir()
                    conflict = folder / '.rouge-record-collision'
                    retained = b'PUBLIC private-name collision must survive'
                    target = folder / 'retained-target'
                    if entry_kind == 'file':
                        conflict.write_bytes(retained)
                    elif entry_kind == 'directory':
                        conflict.mkdir()
                        (conflict / 'retained.txt').write_bytes(retained)
                    else:
                        if entry_kind == 'live_link':
                            target.mkdir()
                            (target / 'retained.txt').write_bytes(retained)
                        conflict.symlink_to(target, target_is_directory=True)
                    link_before = os.readlink(conflict) if entry_kind.endswith('link') else None
                    path = folder / 'record.json'
                    model = RunState(path) if kind == 'run' else AccountCache(path, {})
                    # Force real OS creation to meet a known old entry first.
                    # OS mkdir, link, descriptor writes and cleanup remain real.
                    with patch('tempfile._get_candidate_names',
                               side_effect=lambda: iter(('collision', 'fresh-directory', 'fresh-anchor'))):
                        self.assert_saved_safely(model, path)
                    if entry_kind == 'file':
                        self.assertEqual(conflict.read_bytes(), retained)
                    elif entry_kind == 'directory':
                        self.assertEqual((conflict / 'retained.txt').read_bytes(), retained)
                    else:
                        self.assertEqual(os.readlink(conflict), link_before)
                        if entry_kind == 'live_link':
                            self.assertEqual((target / 'retained.txt').read_bytes(), retained)
                        else:
                            self.assertFalse(target.exists())
                    self.assertFalse((folder / '.rouge-record-fresh-directory').exists())

    def test_overlapping_save_cannot_archive_an_active_writers_temporary(self):
        for kind in ('run', 'cache'):
            for existing in (False, True):
                with self.subTest(kind=kind, existing=existing):
                    model, path, original = self.model(kind, existing)
                    temporary = path.with_suffix('.tmp')
                    active = b'PUBLIC active producer bytes'
                    with record_save_lock(path):
                        temporary.write_bytes(active)
                        self.assert_failed_and_latched(model, path, original)
                        self.assertEqual(temporary.read_bytes(), active)
                        self.assertEqual(list(path.parent.glob(temporary.name + '.preserved-*')), [])
                    self.assertFalse(model.save())
                    self.assertEqual(temporary.read_bytes(), active)
                    self.assertFalse(path.with_name(path.name + '.saving').exists())

    def test_preexisting_save_claim_and_its_private_children_are_never_taken_over(self):
        for kind in ('run', 'cache'):
            with self.subTest(kind=kind):
                model, path, original = self.model(kind, True)
                claim = path.with_name(path.name + '.saving')
                claim.mkdir()
                retained = claim / 'public-retained-owner.txt'
                retained.write_bytes(b'PUBLIC interrupted owner claim')
                self.assert_failed_and_latched(model, path, original)
                self.assertEqual(retained.read_bytes(), b'PUBLIC interrupted owner claim')
                self.assertFalse(path.with_suffix('.tmp').exists())

    def test_successful_save_keeps_platform_text_bytes_and_removes_only_own_temp(self):
        for kind in ('run', 'cache'):
            with self.subTest(kind=kind):
                model, path, _ = self.model(kind, False)
                record = model.state if kind == 'run' else model.records
                expected = self.folder / f'{kind}-platform-writer.txt'
                expected.write_text(json.dumps(record, ensure_ascii=False, indent=2),
                                    encoding='utf-8')
                other = self.folder / f'{kind}-other.tmp'
                other.write_bytes(b'PUBLIC unrelated temporary')
                self.assertTrue(model.save())
                self.assertEqual(path.read_bytes(), expected.read_bytes())
                self.assertFalse(path.with_suffix('.tmp').exists())
                self.assertEqual(other.read_bytes(), b'PUBLIC unrelated temporary')
                self.assertTrue(model.save())


if __name__ == '__main__':
    unittest.main()
