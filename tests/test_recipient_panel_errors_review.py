import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.recipient_native_ratio_view import RecipientNativeRatioPanel


class RecipientPanelErrorsReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel=RecipientNativeRatioPanel();self.panel._load_template()
        self.addCleanup(self.panel.close)

    def test_internal_type_error_propagates_from_both_actions(self):
        for action in (self.panel._append,self.panel.calculate):
            with self.subTest(action=action.__name__),patch('rouge.recipient_native_ratio_view.recipient_native_ratio_diagnostic',side_effect=TypeError('internal')):
                with self.assertRaises(TypeError):action()

    def test_serialization_failure_is_not_an_input_error(self):
        with patch('rouge.recipient_native_ratio_view.recipient_native_ratio_diagnostic',return_value={'declaration':{}}),patch('rouge.recipient_native_ratio_view.json.dumps',side_effect=ValueError('render')):
            with self.assertRaisesRegex(ValueError,'render'):self.panel._append()

    def test_invalid_json_still_prompts_without_replacing_text(self):
        self.panel.editor.setPlainText('{')
        for action in (self.panel._append,self.panel.calculate):
            action();self.assertIn('JSON格式错误',self.panel.status.text())
            self.assertEqual(self.panel.editor.toPlainText(),'{')
