"""Reading and geometry regressions for the shared native reference window."""
import unittest
from PySide6.QtCore import QSize
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from rouge.player_reference_window import ReferenceWindow, ToolPage


class ReferenceViewportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.reference_window = self.host = ReferenceWindow(self.owner)
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.host.close()
        self.owner.deleteLater()
        self.qt.processEvents()

    def settle(self):
        self.qt.processEvents()
        QTest.qWait(40)
        self.qt.processEvents()

    def test_active_wrapped_text_scrolls_to_last_control_without_growing_window(self):
        body = QWidget()
        layout = QVBoxLayout(body)
        text = QLabel('公开长说明 ' * 450)
        text.setWordWrap(True)
        layout.addWidget(text)
        last = QPushButton('最后一项')
        layout.addWidget(last)
        page = ToolPage('正文', body, self.owner)
        page.resize(600, 250)
        self.assertTrue(self.host.present(page))
        self.settle()
        self.assertEqual(self.host.size(), QSize(600, 250))
        self.assertGreater(page.body_scroll.verticalScrollBar().maximum(), 0)
        page.body_scroll.ensureWidgetVisible(last)
        self.settle()
        viewport = page.body_scroll.viewport()
        self.assertGreaterEqual(last.mapTo(viewport, last.rect().topLeft()).y(), 0)
        self.assertLess(last.mapTo(viewport, last.rect().bottomRight()).y(), viewport.height())

    def test_hidden_tall_header_does_not_take_space_from_current_page(self):
        tall = ToolPage('资源', QWidget(), self.owner)
        label = QLabel('多行资源\n' * 14)
        tall.header_bar.addWidget(label)
        tall.resize(800, 600)
        self.host.present(tall)
        self.settle()
        tall_height = self.host.titleBar.height()
        short = ToolPage('概览', QWidget(), self.owner)
        short.resize(460, 350)
        self.host.present(short)
        self.settle()
        self.assertEqual(self.host.size(), QSize(460, 350))
        self.assertLess(self.host.titleBar.height(), tall_height)
        self.assertGreater(short.body_scroll.viewport().height(), 250)
        self.assertEqual(self.host.headers.sizeHint(), short.header.sizeHint())
        self.assertEqual(self.host.headers.minimumSizeHint(), short.header.minimumSizeHint())

    def test_back_preserves_scroll_reading_and_page_size(self):
        content = QLabel('第一行\n' * 180)
        first = ToolPage('第一份', content, self.owner)
        first.resize(600, 300)
        self.host.present(first)
        self.settle()
        scrollbar = first.body_scroll.verticalScrollBar()
        scrollbar.setValue(240)
        position = scrollbar.value()
        second = ToolPage('第二份', QWidget(), self.owner)
        second.resize(800, 430)
        self.host.present(second)
        self.settle()
        self.host.navigate(0)
        self.settle()
        self.assertIs(self.host.pages.currentWidget(), first)
        self.assertEqual(scrollbar.value(), position)
        self.assertEqual(self.host.size(), QSize(600, 300))

    def test_empty_header_stack_has_no_reserved_content_height(self):
        self.assertEqual(self.host.headers.sizeHint(), QSize(0, 0))
        self.assertEqual(self.host.headers.minimumSizeHint(), QSize(0, 0))
