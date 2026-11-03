import unittest
from copy import deepcopy

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog

from rouge.p2_wang_resource_view import WangReceiptDialog, WangResourceLedgerDialog


class WangResourceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.training = {'elite': 2, 'level': 90, 'potential': 1,
                         'module_id': None, 'module_level': 0}
        self.window = WangResourceLedgerDialog(self.training, rank=10)
        self.window.show(); self.app.processEvents()

    def tearDown(self):
        self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_initial_unknown_and_frozen_training_do_not_import_live_quantities(self):
        self.assertTrue(self.window.isVisible())
        self.assertTrue(all(control.value() == -1 for control in self.window.initial_controls.values()))
        self.assertTrue(all(value is None for value in self.window.result['final'].values()))
        self.assertIn('跟子基础参数9', self.window.source_label.text())
        self.training['level'] = 1
        self.assertEqual(self.window.training['level'], 90)

    def test_actual_modal_receipt_addition_calculation_and_edit_invalidation(self):
        for key, value in {'stock': 4, 'manual_active': 0, 'extra_active': 0,
                           'currency': 20, 'sp': 40}.items():
            self.window.initial_controls[key].setValue(value)

        def complete_editor():
            editor = QApplication.activeModalWidget()
            self.assertIsInstance(editor, WangReceiptDialog)
            for key, value in {'manual_created': 1, 'extra_created': 0,
                               'stock_spent': 1, 'currency_spent': 3, 'sp_spent': 0}.items():
                editor.controls[key].setValue(value)
            editor.accept()
        QTimer.singleShot(0, complete_editor)
        self.window.add_buttons['manual_receipt'].click()
        self.assertEqual(len(self.window.steps), 1)
        self.assertIsNone(self.window.result)
        self.window.calculate_button.click()
        self.assertEqual(self.window.result['final'], {'stock': 3, 'manual_active': 1,
                                                       'extra_active': 0, 'currency': 17, 'sp': 40})
        self.assertEqual(self.window.table.item(0, 4).text(), '0')
        before = deepcopy(self.window.steps)
        self.window.initial_controls['stock'].setValue(5)
        self.assertIsNone(self.window.result); self.assertFalse(self.window.copy_button.isEnabled())
        self.assertEqual(self.window.steps, before)
        self.assertEqual(self.window.table.item(0, 2).text(), '待核对')

    def test_unknown_refund_controls_are_not_default_zero(self):
        editor = WangReceiptDialog('loss_receipt', 'loss', '', parent=self.window)
        self.assertTrue(all(value is None for key, value in editor.declaration().items()
                            if key not in ('id', 'kind')))
        editor.controls['stock_returned'].setValue(0)
        self.assertEqual(editor.declaration()['stock_returned'], 0)
        self.assertIsNone(editor.declaration()['currency_returned'])
        editor.deleteLater()

    def test_duplicate_snapshot_error_is_visible_and_does_not_reset_declarations(self):
        self.window.steps = [{'id': 'observation', 'kind': 'snapshot',
                              'state': self.window.preview()['initial']}]
        self.window.calculate_button.click()
        self.assertIsNone(self.window.result)
        self.assertIn('唯一命名独立快照', self.window.details.toPlainText())
        self.assertEqual(len(self.window.steps), 1)
        self.window.table.selectRow(0); self.window.remove_button.click()
        self.assertEqual(self.window.steps, [])
        self.window.calculate_button.click(); self.assertIsNotNone(self.window.result)


if __name__ == '__main__':
    unittest.main()
