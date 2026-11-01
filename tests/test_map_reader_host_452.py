import json
from pathlib import Path
import unittest
from PySide6.QtWidgets import QApplication, QWidget
from rouge import current_node_readers as model
from rouge.current_node_readers_view import READERS, make_dialog
from rouge.player_reference_window import ReferenceWindow, ToolPage


class MapReaderHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.reference_window = self.host = ReferenceWindow(self.owner)
        self.addCleanup(self.owner.close)
        self.addCleanup(self.host.close)

    def page(self, title):
        return ToolPage(title, QWidget(), self.owner)

    def test_every_current_event_reader_kind_uses_its_exact_panel_in_shared_host(self):
        data = json.loads((Path(__file__).resolve().parents[1]/'rouge/data/node-catalog.json').read_bytes())
        seen = set()
        fallback = self.page('地图')
        self.host.present(fallback)
        handle = int(self.host.winId())
        for record in data['events']:
            binding = model.binding_for(record)
            if binding is None or binding['reader'] in seen:
                continue
            seen.add(binding['reader'])
            page = make_dialog(binding, page_owner=self.owner, historical=True)
            self.assertIsNotNone(page, binding['reader'])
            self.assertTrue(model.matches_current(binding, page.panel.result))
            self.assertEqual('历史节点资料', page.node_reference_banner.text())
            self.assertEqual(model.NOTICE, page.node_reference_banner.toolTip())
            self.assertTrue(self.host.present(page))
            self.qt.processEvents()
            self.assertIs(page.window(), self.host)
            self.assertFalse(page.isWindow())
            self.assertEqual(int(self.host.winId()), handle)
            self.host.discard(page, fallback=fallback)
        self.assertEqual(seen, set(READERS))

    def test_rejected_source_keeps_current_page_and_history(self):
        a, expired = self.page('地图'), self.page('旧资料')
        self.host.present(a)
        expired.prepare = lambda: False
        self.assertFalse(self.host.present(expired))
        self.assertEqual(self.host.history, [a])
        self.assertIs(self.host.pages.currentWidget(), a)
        self.assertTrue(a.isVisible())

    def test_discard_active_source_removes_both_back_and_forward_entries(self):
        a, old, b = self.page('地图'), self.page('失效资料'), self.page('笔记')
        for page in (a, old, b, old):
            self.host.present(page)
        self.host.discard(old, fallback=a)
        self.qt.processEvents()
        self.assertNotIn(old, self.host.history)
        self.assertEqual(self.host.pages.indexOf(old), -1)
        self.assertIs(self.host.pages.currentWidget(), a)
        self.assertTrue(a.isVisible())
        self.assertIs(self.owner.active_popup, a)

    def test_closing_or_discarding_hidden_source_does_not_hide_another_page(self):
        a, old = self.page('地图'), self.page('旧资料')
        self.host.present(old)
        self.host.present(a)
        old.close()
        self.assertTrue(self.host.isVisible())
        self.host.discard(old, fallback=a)
        self.assertTrue(a.isVisible())

    def test_restore_rechecks_source_before_using_retained_reader(self):
        a, old = self.page('地图'), self.page('待核对资料')
        self.host.present(a)
        self.host.present(old)
        self.host.hide()
        checked = []
        def invalidate():
            checked.append(True)
            self.host.discard(old, fallback=a)
            return False
        old.prepare = invalidate
        self.host.show()
        self.qt.processEvents()
        self.assertEqual(checked, [True])
        self.assertIs(self.host.pages.currentWidget(), a)
        self.assertNotIn(old, self.host.history)


if __name__ == '__main__':
    unittest.main()
