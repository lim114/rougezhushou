import json
import os
import unittest
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalRunView141Tests(unittest.TestCase):
    def test_refresh_preserves_editor_and_uses_new_snapshot(self):
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ModuleNotFoundError:
            self.skipTest('Qt dependency unavailable; native entry has a separate receipt')
        app=QApplication.instance() or QApplication([])
        e=environment();dialog=SupplementalRunDialog(defaults(),lambda:e)
        p=defaults('char_210_stward');p['count']=3
        text=json.dumps(p,ensure_ascii=False,indent=2);dialog.editor.setPlainText(text)
        self.assertIsNone(dialog.result)
        e['relic_ids']=['rogue_6_relic_legacy_27']
        self.assertEqual(dialog.environment['relic_ids'],[])
        dialog.refresh_button.click();app.processEvents()
        self.assertEqual(dialog.editor.toPlainText(),text)
        self.assertEqual(dialog.result['operator_name'],'史都华德')
        self.assertEqual(dialog.result['preview']['count'],3)
        self.assertGreater(dialog.result['rows'][1]['delta'],0)
        self.assertEqual(dialog.table.columnCount(),6)
        dialog.close()
