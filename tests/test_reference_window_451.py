import unittest
from types import SimpleNamespace
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPlainTextEdit, QVBoxLayout
from PySide6.QtTest import QTest
from rouge.player_reference_window import ReferenceWindow, ToolPage, NotesPage


class ReferenceWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.reference_window = self.host = ReferenceWindow(self.owner)
        self.addCleanup(self.owner.close)
        self.addCleanup(self.host.close)

    def page(self, title):
        content = QWidget()
        layout = QVBoxLayout(content)
        search = QLineEdit()
        reading = QPlainTextEdit('\n'.join('段落 '+str(i) for i in range(150)))
        layout.addWidget(search)
        layout.addWidget(reading)
        page = ToolPage(title, content, self.owner)
        return page, search, reading

    def test_resizing_visible_host_keeps_window_inside_current_screen(self):
        page,search,reading=self.page('地图标记');self.assertTrue(self.host.present(page));self.qt.processEvents()
        area=self.host.screen().availableGeometry();self.host.resize(420,320);self.host.move(area.right()-self.host.width()+1,area.bottom()-self.host.height()+1)
        search.setText('保留搜索');self.host.resize(min(650,area.width()-24),min(620,area.height()-24));self.qt.processEvents()
        self.assertTrue(area.contains(self.host.geometry()));self.assertEqual(search.text(),'保留搜索');self.assertIs(self.host.pages.currentWidget(),page)

    def test_same_native_host_and_back_forward_preserve_reading_and_size(self):
        a, search, reading = self.page('地图')
        b, _, _ = self.page('历史')
        self.assertTrue(self.host.present(a))
        self.qt.processEvents()
        handle = int(self.host.winId())
        self.host.resize(850, 650)
        search.setText('古老')
        reading.verticalScrollBar().setValue(80)
        cursor = reading.textCursor()
        cursor.setPosition(15)
        cursor.setPosition(23, cursor.MoveMode.KeepAnchor)
        reading.setTextCursor(cursor)
        offset = reading.verticalScrollBar().value()
        self.assertTrue(self.host.present(b))
        self.assertFalse(a.isVisible())
        self.assertFalse(a.isWindow())
        QTest.mouseClick(self.host.back, Qt.MouseButton.LeftButton)
        self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(), a)
        self.assertEqual(int(self.host.winId()), handle)
        self.assertEqual((self.host.width(), self.host.height()), (850, 650))
        self.assertEqual(search.text(), '古老')
        self.assertEqual(reading.textCursor().selectedText(), cursor.selectedText())
        self.assertEqual(reading.verticalScrollBar().value(), offset)
        QTest.mouseClick(self.host.forward, Qt.MouseButton.LeftButton)
        self.assertIs(self.host.pages.currentWidget(), b)

    def test_branch_after_back_replaces_only_forward_history(self):
        a, _, _ = self.page('地图')
        b, _, _ = self.page('历史')
        c, _, _ = self.page('藏品')
        self.host.present(a)
        self.host.present(b)
        self.host.navigate(0)
        self.host.present(c)
        self.assertEqual(self.host.history, [a, c])
        self.assertFalse(self.host.forward.isEnabled())
        self.assertEqual(self.host.headers.currentWidget(), c.header)

    def test_unsaved_notes_veto_switch_close_and_back_without_changing_history(self):
        a, _, _ = self.page('地图')
        note = NotesPage('笔记', QWidget(), self.owner)
        state = {'saved': False}
        note.panel = SimpleNamespace(finish_edit=lambda: state['saved'])
        self.host.present(a)
        self.host.present(note)
        self.assertFalse(self.host.present(a))
        self.assertFalse(self.host.close())
        QTest.keyClick(self.host, Qt.Key.Key_Escape)
        self.assertTrue(self.host.isVisible())
        self.host.navigate(0)
        self.assertEqual(self.host.cursor, 1)
        self.assertIs(self.host.pages.currentWidget(), note)
        self.assertTrue(note.isVisible())
        state['saved'] = True
        self.assertTrue(self.host.close())

    def test_close_reopen_refreshes_current_page_and_retains_header(self):
        a, _, _ = self.page('地图')
        calls = []
        a.on_show = lambda: calls.append('show')
        self.host.present(a)
        self.qt.processEvents()
        before = len(calls)
        self.host.close()
        self.assertFalse(self.host.isVisible())
        self.host.present(a)
        self.qt.processEvents()
        self.assertGreater(len(calls), before)
        self.assertTrue(a.header.isVisible())
        self.assertEqual(self.host.history, [a])

    def test_unregistered_pages_stay_hidden_and_do_not_force_other_page_size(self):
        a, _, _ = self.page('地图')
        unused, _, _ = self.page('尚未打开的设置')
        unused.setMinimumSize(1000, 800)
        self.host.present(a)
        self.qt.processEvents()
        self.assertFalse(unused.isVisible())
        b, _, _ = self.page('小笔记')
        b.resize(500, 300)
        self.host.present(b)
        self.qt.processEvents()
        self.assertEqual(self.host.size(), b.preferred_size)


if __name__ == '__main__':
    unittest.main()
