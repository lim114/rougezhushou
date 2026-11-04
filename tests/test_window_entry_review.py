"""First-open sizing inputs and explicit/default frame theme behavior."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from types import SimpleNamespace
import unittest
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from rouge.player_reference_window import ReferenceWindow, ToolPage
from rouge.player_window_frame import PlayerDialog
from rouge.player_theme import apply_theme


class BindingOwner(QWidget):
    def __init__(self):
        super().__init__()
        self.binding_reads = 0

    @property
    def game_binding(self):
        self.binding_reads += 1
        return SimpleNamespace(enabled=False)


class WindowEntryReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_return_to_opened_page_does_not_read_first_open_binding_again(self):
        owner = BindingOwner()
        owner.reference_window = host = ReferenceWindow(owner)
        self.addCleanup(owner.deleteLater)
        self.addCleanup(host.close)
        first = ToolPage('第一份资料', QWidget(), owner)
        second = ToolPage('第二份资料', QWidget(), owner)
        self.assertTrue(host.present(first))
        self.assertTrue(host.present(second))
        self.assertEqual(owner.binding_reads, 2)
        self.assertTrue(host.present(first))
        self.assertEqual(owner.binding_reads, 2)
        self.assertIs(host.pages.currentWidget(), first)

    def test_first_show_defaults_only_when_theme_not_already_set(self):
        for explicit in (None, 'light'):
            with self.subTest(explicit=explicit):
                dialog = PlayerDialog()
                QVBoxLayout(dialog).addWidget(QWidget())
                self.addCleanup(dialog.deleteLater)
                if explicit:
                    apply_theme(dialog, explicit)
                dialog.show()
                self.qt.processEvents()
                self.assertEqual(dialog.property('playerTheme'), explicit or 'dark')
                dialog.hide()
                apply_theme(dialog, 'light')
                dialog.show()
                self.qt.processEvents()
                self.assertEqual(dialog.property('playerTheme'), 'light')
                self.assertIs(dialog.layout().itemAt(0).widget(), dialog.titleBar)
                dialog.close()
