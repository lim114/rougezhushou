"""Manual reading skips unrelated live data, while resume/reset still updates."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from rouge.player_notes import NoteStore, content_key
from rouge.player_recent_notes import RecentNotesPanel


class ObservedState(dict):
    scene_reads = 0

    def get(self, key, default=None):
        if key == 'last_node_content':
            self.scene_reads += 1
        return super().get(key, default)


class NoteRefreshEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = NoteStore(Path(temp.name))
        self.a = {'kind': 'battle', 'title': '手动阅读', 'variant_id': 'a'}
        self.b = {'kind': 'event', 'title': '最新场景', 'event_id': 'b'}
        self.state = ObservedState(id='one', last_node_content=self.a)
        with patch('rouge.player_note_selector.catalogue_snapshot', return_value={'rows': [], 'unavailable': []}):
            self.panel = RecentNotesPanel(SimpleNamespace(state=self.state), self.store)
        self.panel.timer.stop()
        self.addCleanup(self.panel.close)

    def test_manual_refresh_skips_live_data_but_follow_and_new_run_read_it(self):
        self.panel.select_context(self.a)
        self.state['last_node_content'] = self.b
        self.state.scene_reads = 0
        self.panel.refresh(force=True)
        self.panel.refresh(force=True)
        self.assertEqual(self.panel.context, self.a)
        self.assertEqual(self.state.scene_reads, 0)
        self.panel.follow.setChecked(True)
        self.assertEqual(self.state.scene_reads, 1)
        self.assertEqual(self.panel.context, self.b)
        self.panel.follow.setChecked(False)
        self.state['id'] = 'two'
        self.state['last_node_content'] = None
        self.state.scene_reads = 0
        self.panel.refresh(force=True)
        self.assertEqual(self.state.scene_reads, 1)
        self.assertIsNone(self.panel.context)
        self.assertFalse(self.panel.edit.isEnabled())

    def test_read_failure_clears_preview_and_next_refresh_recovers_without_writing(self):
        key = content_key(self.a)
        self.store.save(key, '原笔记', self.store.read(key)[1])
        self.panel.refresh(force=True)
        before = self.store.path(key).read_bytes()
        with patch.object(self.store, 'read', side_effect=PermissionError('isolated')):
            self.panel.refresh(force=True)
        self.assertEqual(self.panel.preview.toPlainText(), '')
        self.assertIn('权限', self.panel.status.text())
        self.panel.refresh(force=True)
        self.assertIn('原笔记', self.panel.preview.toPlainText())
        self.assertEqual(self.store.path(key).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
