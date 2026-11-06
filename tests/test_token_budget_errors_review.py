import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.token_budget_view import TokenBudgetDialog


class TokenBudgetErrorsReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.dialog=TokenBudgetDialog('char_110_deepcl',{'elite':2,'level':70})
        self.addCleanup(self.dialog.close)

    def test_invalid_cultivation_is_reported_and_old_result_invalidated(self):
        self.dialog.training['level']=0
        self.dialog.calculate()
        self.assertIsNone(self.dialog.result)
        self.assertFalse(self.dialog.copy_button.isEnabled())
        self.assertIn('等级或信赖超出范围',self.dialog.notice.toPlainText())

    def test_internal_missing_field_and_type_error_propagate(self):
        for error in (KeyError('internal_field'),TypeError('internal_type')):
            with self.subTest(error=type(error).__name__):
                with patch('rouge.token_budget_view.token_budget',side_effect=error):
                    with self.assertRaises(type(error)):
                        self.dialog.calculate()
                self.assertIsNone(self.dialog.result)
                self.assertFalse(self.dialog.copy_button.isEnabled())

    def test_rendering_error_is_not_an_input_error(self):
        with patch('rouge.token_budget_view.format_token_budget',side_effect=ValueError('rendering defect')):
            with self.assertRaisesRegex(ValueError,'rendering defect'):
                self.dialog.calculate()
