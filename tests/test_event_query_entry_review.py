import unittest
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication
from rouge import current_event_directory as model
from rouge.current_event_directory_view import CurrentEventDirectoryPanel

class EventQueryEntryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_long_query_rejected_before_source_read_and_not_truncated(self):
        with patch.object(model,'packet')as source:
            with self.assertRaisesRegex(model.QueryTooLong,'160'):model.reference(query='字'*161)
            source.assert_not_called()
        self.assertIsNotNone(model.reference(query='字'*160))
        result=deepcopy(model.reference('flows321:button'));result['filters']['query']='字'*161
        self.assertIsNone(model.resolve(result))

    def test_ui_clears_old_result_and_recovers_after_shortening(self):
        panel=CurrentEventDirectoryPanel();self.addCleanup(panel.close)
        self.assertEqual(panel.events.count(),39)
        panel.query.setText('字'*161)
        self.assertEqual(len(panel.query.text()),161)
        self.assertIn('160',panel.count.text());self.assertIn('160',panel.player.toPlainText())
        self.assertIsNone(panel.result);self.assertEqual(panel.events.count(),0)
        self.assertFalse(panel.open_button.isEnabled())
        panel.query.clear();self.assertEqual(panel.events.count(),39)
        with patch.object(model,'reference',side_effect=TypeError('internal defect')):
            with self.assertRaisesRegex(TypeError,'internal defect'):panel.refresh_reference()

if __name__=='__main__':unittest.main()
