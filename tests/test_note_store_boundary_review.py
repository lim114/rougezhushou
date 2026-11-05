"""Existing note protections, exercised only with isolated temporary files."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from rouge.player_notes import NoteStore


class NoteStoreBoundaryTests(unittest.TestCase):
    def test_reported_link_is_rejected_before_read_or_publication(self):
        with TemporaryDirectory() as folder:
            store = NoteStore(folder)
            note = store.path('isolated-linked-key')
            note.write_text('保留原件内容', encoding='utf8')
            with patch.object(Path, 'is_symlink', return_value=True):
                with patch.object(Path, 'read_bytes') as read, patch('rouge.player_notes.os.replace') as publish:
                    with self.assertRaisesRegex(ValueError, '链接'):
                        store.read('isolated-linked-key')
                    with self.assertRaisesRegex(ValueError, '链接'):
                        store.save('isolated-linked-key', '不能写入', '')
                    read.assert_not_called()
                    publish.assert_not_called()
            self.assertEqual(note.read_text('utf8'), '保留原件内容')

    def test_existing_save_claim_is_not_removed_or_taken_over(self):
        with TemporaryDirectory() as folder:
            store = NoteStore(folder)
            key = 'isolated-owned-key'
            expected = store.save(key, '原文', store.read(key)[1])
            note = store.path(key)
            claim = note.with_name(note.name + '.saving')
            claim.mkdir()
            with self.assertRaises(FileExistsError):
                store.save(key, '新文', expected)
            self.assertTrue(claim.is_dir())
            self.assertEqual(store.read(key), ('原文', expected))


if __name__ == '__main__':
    unittest.main()
