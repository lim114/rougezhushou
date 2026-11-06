import json
import os
from copy import deepcopy
from unittest.mock import patch
import unittest

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from PySide6.QtWidgets import QApplication
from rouge import recipient_native_ratio_view as view
from rouge import recipient_native_ratio as native
from rouge.recipient_native_ratio import recipient_native_ratio_diagnostic


class RecipientAppendBoundaryReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def test_append_uses_one_complete_diagnostic(self):
        panel=view.RecipientNativeRatioPanel()
        try:
            panel.load_template.click()
            original=panel.current_query()
            with patch.object(view,'recipient_native_ratio_diagnostic',wraps=recipient_native_ratio_diagnostic) as diagnostic:
                with patch.object(native,'_positive_ratio_division',wraps=native._positive_ratio_division) as divide:
                    panel.append_observation.click()
            self.assertEqual(diagnostic.call_count,1)
            self.assertEqual(divide.call_count,0)
            self.assertEqual(panel.current_query()['observations'][:-1],original['observations'])
            self.assertEqual(len(panel.current_query()['observations']),4)
        finally:
            panel.close();panel.deleteLater();self.app.processEvents()

    def test_failed_append_preserves_editor_and_existing_result(self):
        panel=view.RecipientNativeRatioPanel()
        try:
            for change in ('scope','duplicate','overflow','number','shape'):
                panel.operator.setCurrentIndex(0);panel.load_template.click()
                panel.hp.setText('49999');panel.label.setText('新原值观察')
                if change=='overflow':
                    payload=panel.current_query()
                    row=payload['observations'][0]
                    payload['observations']=[{**deepcopy(row),'label':str(i)} for i in range(32)]
                    panel.editor.setPlainText(json.dumps(payload))
                elif change=='shape':panel.editor.setPlainText('{}')
                panel.calculate_button.click()
                if change=='scope':panel.operator.setCurrentIndex(1)
                elif change=='duplicate':panel.label.setText(panel.current_query()['observations'][0]['label'])
                elif change=='number':panel.hp.setText('1.1')
                before=(panel.editor.toPlainText(),panel.result_snapshot(),panel.result_view.toPlainText())
                panel.append_observation.click()
                with self.subTest(change=change):
                    self.assertEqual((panel.editor.toPlainText(),panel.result_snapshot(),panel.result_view.toPlainText()),before)
        finally:
            panel.close();panel.deleteLater();self.app.processEvents()
