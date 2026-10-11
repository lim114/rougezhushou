import unittest
from PySide6.QtWidgets import QApplication,QLabel
from rouge.token_budget_view import TokenBudgetDialog

OP='char_2027_wang';TOKEN='token_10064_wang_stone1'
TRAINING={'elite':2,'level':80,'potential':3,'module_id':'uniequip_002_wang','module_level':3}

class WangCountDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_existing_quota_window_exposes_count_limits_and_manual_scope(self):
        d=TokenBudgetDialog(OP,TRAINING);self.addCleanup(d.close)
        self.assertEqual(d.table.item(0,6).text(),'8')
        self.assertEqual(d.table.item(0,7).text(),'8')
        self.assertTrue(any('计入手动棋子限制' in label.text() for label in d.findChildren(QLabel)))
        self.assertIn('自动额外棋子',d.notice.toPlainText())

    def test_declared_overflow_warning_and_changed_values_need_recalculation(self):
        d=TokenBudgetDialog(OP,TRAINING);self.addCleanup(d.close)
        d.inputs[TOKEN]['available_stock'].setValue(9)
        self.assertIsNone(d.result)
        self.assertFalse(d.copy_button.isEnabled())
        d.calculate()
        self.assertIn('声明库存超出默认培养参考',d.notice.toPlainText())
        self.assertFalse(d.result['rows'][0]['stock_within_reference'])
        self.assertIsNone(d.result['rows'][0]['actual_deployable'])

if __name__=='__main__':unittest.main()
