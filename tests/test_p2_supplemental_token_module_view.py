import unittest
from copy import deepcopy

from PySide6.QtWidgets import QApplication
from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog


class SupplementalTokenModuleViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.training = {'elite': 2, 'level': 90}
        self.window = SupplementalTokenModuleDialog('char_248_mgllan', self.training)
        self.window.show(); self.app.processEvents()

    def tearDown(self):
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_initial_selection_is_empty_and_does_not_assume_host_endpoint(self):
        self.assertTrue(self.window.isVisible())
        self.assertIsNone(self.window.phase.currentData()); self.assertIsNone(self.window.endpoint.currentData())
        self.assertIsNone(self.window.result); self.assertFalse(self.window.copy_button.isEnabled())
        self.window.calculate_button.click()
        self.assertIsNone(self.window.result)
        self.assertIn('需要0、1或2', self.window.details.toPlainText())

    def test_explicit_endpoint_builds_all_skill_variants_and_keeps_zero_attack(self):
        self.window.phase.setCurrentIndex(self.window.phase.findData(2))
        self.window.endpoint.setCurrentIndex(self.window.endpoint.findData('last'))
        self.window.calculate_button.click()
        self.assertEqual(self.window.table.rowCount(), 12)
        self.assertEqual(self.window.table.item(3, 6).text(), '0')
        self.assertEqual(self.window.table.item(7, 10).text(), '103')
        self.assertIn('当前完整实体面板', self.window.details.toPlainText())
        self.assertTrue(self.window.copy_button.isEnabled())

    def test_endpoint_change_invalidates_and_preserves_captured_training(self):
        self.window.phase.setCurrentIndex(self.window.phase.findData(2))
        self.window.endpoint.setCurrentIndex(self.window.endpoint.findData('last'))
        self.window.calculate_button.click()
        captured = deepcopy(self.window.training)
        self.training['level'] = 1
        self.window.endpoint.setCurrentIndex(self.window.endpoint.findData('first'))
        self.assertIsNone(self.window.result); self.assertEqual(self.window.table.rowCount(), 0)
        self.assertFalse(self.window.copy_button.isEnabled()); self.assertEqual(self.window.training, captured)
        self.window.calculate_button.click()
        self.assertEqual(self.window.result['variants'][2]['token_level_endpoint'], 1)
        self.assertEqual(self.window.result['host_training']['level'], 90)


if __name__ == '__main__':
    unittest.main()
