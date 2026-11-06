from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from rouge import current_startup_view as view


class StartupMissingImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_missing_and_corrupt_image_keep_name_and_explanation(self):
        dialog = view.CurrentStartupDialog(view.model.locate('choices', 'choice_ro6_startbuff_7'))
        self.addCleanup(dialog.close)
        panel = dialog.panel
        name, text = panel.reward_name.text(), panel.player.toPlainText()
        self.assertFalse(panel.reward_icon.pixmap().isNull())
        with TemporaryDirectory() as folder:
            missing, corrupt = Path(folder) / 'missing.png', Path(folder) / 'corrupt.png'
            corrupt.write_bytes(b'not PNG')
            for path in (missing, corrupt):
                with self.subTest(path=path.name), patch.object(view, 'QPixmap', side_effect=lambda _: QPixmap(str(path))):
                    panel._choice_changed(panel.choices.currentItem())
                    self.assertEqual(panel.reward_icon.text(), '图片暂缺')
                    self.assertTrue(panel.reward_icon.pixmap().isNull())
                    self.assertEqual(panel.reward_name.text(), name)
                    self.assertEqual(panel.player.toPlainText(), text)
        panel._choice_changed(panel.choices.currentItem())
        self.assertFalse(panel.reward_icon.pixmap().isNull())
        self.assertEqual(panel.reward_icon.text(), '')
