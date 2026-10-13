"""Public destination collisions and normal first-record usage."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge.account_cache import AccountCache
from rouge.run_state import RunState


class InitialInstallTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory(prefix='public-initial-install-')
        self.addCleanup(folder.cleanup)
        self.folder=Path(folder.name)

    def test_run_first_complete_save_then_existing_record_save(self):
        path=self.folder/'run.json';run=RunState(path)
        run.state['notice']='公开初次完整内容'
        self.assertTrue(run.save())
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),run.state)
        self.assertFalse(path.with_suffix('.tmp').exists())
        run.state['notice']='后续内容'
        self.assertTrue(run.save())
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),run.state)

    def test_cache_first_complete_save_then_existing_record_save(self):
        path=self.folder/'cache.json';cache=AccountCache(path,{})
        self.assertTrue(cache.save());self.assertEqual(path.read_text(encoding='utf-8'),'{}')
        self.assertFalse(path.with_suffix('.tmp').exists())
        self.assertTrue(cache.save());self.assertFalse(cache.preserve_original)

    def test_run_raced_new_destination_survives_and_failure_latches(self):
        path=self.folder/'run.json';run=RunState(path)
        original=b'{"public_created_after_load":true}';path.write_bytes(original)
        self.assertFalse(run.save());self.assertEqual(path.read_bytes(),original)
        self.assertIsNotNone(run.save_issue)
        run.reset();self.assertFalse(run.save());self.assertEqual(path.read_bytes(),original)

    def test_cache_raced_new_destination_survives_and_failure_latches(self):
        path=self.folder/'cache.json';cache=AccountCache(path,{})
        original=b'{"public_created_after_load":true}';path.write_bytes(original)
        self.assertFalse(cache.save());self.assertEqual(path.read_bytes(),original)
        self.assertTrue(cache.preserve_original);self.assertIsNotNone(cache.save_issue)
        self.assertFalse(cache.save());self.assertEqual(path.read_bytes(),original)

    def test_run_first_install_unavailable_does_not_replace_or_retry(self):
        path=self.folder/'run.json';run=RunState(path)
        with patch('rouge.persistence_install.os.link',side_effect=OSError('public unsupported hard links')):
            with patch.object(Path,'replace',side_effect=AssertionError('must not fall back')):
                self.assertFalse(run.save());run.reset();self.assertFalse(run.save())
        self.assertFalse(path.exists());self.assertIsNotNone(run.save_issue)

    def test_cache_first_install_unavailable_does_not_replace_or_retry(self):
        path=self.folder/'cache.json';cache=AccountCache(path,{})
        with patch('rouge.persistence_install.os.link',side_effect=OSError('public unsupported hard links')):
            with patch.object(Path,'replace',side_effect=AssertionError('must not fall back')):
                self.assertFalse(cache.save());self.assertFalse(cache.save())
        self.assertFalse(path.exists());self.assertTrue(cache.preserve_original)

    def test_explicit_new_run_does_not_replace_an_unloaded_new_destination(self):
        path=self.folder/'run.json';run=RunState(path)
        path.write_bytes(b'{"public_created_after_load":true}')
        run.reset()
        self.assertIsNotNone(run.save_issue);self.assertFalse(run.preserve_unreadable)
        self.assertEqual(path.read_bytes(),b'{"public_created_after_load":true}')

    def test_manual_reset_archives_damaged_original_before_creating_new_record(self):
        path=self.folder/'run.json';original=b'{"public_damaged":'
        path.write_bytes(original);run=RunState(path)
        self.assertTrue(run.preserve_unreadable);run.reset()
        self.assertEqual(run.archived_original.parent,path.parent)
        self.assertEqual(run.archived_original.read_bytes(),original)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),run.state)
        self.assertIn(run.archived_original.name,run.state['notice'])

    def test_manual_reset_retains_relative_link_text_and_target_resolution(self):
        target=self.folder/'public-damaged-target.json';original=b'{"public_damaged":'
        target.write_bytes(original);path=self.folder/'run.json'
        path.symlink_to(target.name);link=path.readlink()
        run=RunState(path);self.assertTrue(run.preserve_unreadable);run.reset()
        self.assertIsNone(run.save_issue)
        self.assertTrue(run.archived_original.is_symlink())
        self.assertEqual(run.archived_original.readlink(),link)
        self.assertEqual(run.archived_original.parent,path.parent)
        self.assertEqual(run.archived_original.read_bytes(),original)
        self.assertEqual(target.read_bytes(),original)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),run.state)

    def test_archive_destination_collision_preserves_both_records(self):
        path=self.folder/'run.json';original=b'{"public_damaged":'
        path.write_bytes(original);run=RunState(path)
        archive=path.with_name(path.name+'.preserved-'+'0'*32)
        other=b'PUBLIC EXISTING ARCHIVE';archive.write_bytes(other)
        class PublicFixedUUID:hex='0'*32
        with patch('uuid.uuid4',return_value=PublicFixedUUID()):run.reset()
        self.assertEqual(path.read_bytes(),original);self.assertEqual(archive.read_bytes(),other)
        self.assertIsNone(run.archived_original);self.assertIsNotNone(run.save_issue)
        self.assertFalse(path.with_suffix('.tmp').exists())

    def test_creation_racing_after_archive_is_preserved_and_archived_bytes_remain(self):
        from rouge.persistence_install import archive_unreadable_record
        path=self.folder/'run.json';original=b'{"public_damaged":'
        path.write_bytes(original);run=RunState(path);other=b'PUBLIC RACING RECORD'
        def raced(source):
            result=archive_unreadable_record(source);source.write_bytes(other);return result
        with patch('rouge.persistence_install.archive_unreadable_record',side_effect=raced):run.reset()
        self.assertEqual(path.read_bytes(),other)
        self.assertEqual(run.archived_original.read_bytes(),original)
        self.assertIsNotNone(run.save_issue)

    def test_failed_archive_keeps_original_and_prevents_retry_even_after_reset(self):
        path=self.folder/'run.json';original=b'{"public_damaged":'
        path.write_bytes(original);run=RunState(path)
        with patch('rouge.persistence_install.archive_unreadable_record',side_effect=OSError('public failed archive')) as move:
            run.reset();run.reset();self.assertEqual(move.call_count,1)
        self.assertEqual(path.read_bytes(),original);self.assertIsNotNone(run.save_issue)
        occupied=self.folder/'public-directory.json';occupied.mkdir()
        child=occupied/'public-child';child.write_bytes(b'PUBLIC DIRECTORY CONTENTS')
        directory_run=RunState(occupied);directory_run.reset()
        self.assertTrue(occupied.is_dir());self.assertEqual(child.read_bytes(),b'PUBLIC DIRECTORY CONTENTS')
        self.assertIsNone(directory_run.archived_original);self.assertIsNotNone(directory_run.save_issue)

    def test_raced_dangling_link_after_missing_load_survives_first_save(self):
        for kind in ('run','cache'):
            with self.subTest(kind=kind):
                path=self.folder/(kind+'-race.json');target=self.folder/(kind+'-missing.json')
                instance=RunState(path) if kind=='run' else AccountCache(path,{})
                path.symlink_to(target);self.assertTrue(path.is_symlink());link=path.readlink()
                self.assertFalse(instance.save());self.assertTrue(path.is_symlink())
                self.assertEqual(path.readlink(),link);self.assertFalse(target.exists())
                self.assertIsNotNone(instance.save_issue)

    def test_interrupted_reset_reopens_without_auto_save_and_requires_explicit_new_run(self):
        path=self.folder/'run.json';original=b'{"public_damaged":'
        path.write_bytes(original);run=RunState(path)
        with patch.object(run,'save',side_effect=KeyboardInterrupt('public reset interruption')):
            with self.assertRaises(KeyboardInterrupt):run.reset()
        archive=run.archived_original
        self.assertEqual(archive.read_bytes(),original);self.assertFalse(path.exists())
        reopened=RunState(path)
        self.assertTrue(reopened.preserve_unreadable);self.assertIn('原件归档',reopened.state['notice'])
        self.assertEqual(reopened.preserved_originals,(archive,));self.assertFalse(reopened.save())
        self.assertFalse(path.exists());reopened.reset()
        self.assertIsNone(reopened.save_issue)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),reopened.state)
        self.assertEqual(archive.read_bytes(),original)
