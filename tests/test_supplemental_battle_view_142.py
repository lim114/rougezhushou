import json
import os
import unittest
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment
from tests.test_supplemental_battle_142 import PARTS,EMERGENCY


class SupplementalBattleView142Tests(unittest.TestCase):
    def test_refresh_keeps_preview_and_updates_ordinary_sources(self):
        os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ModuleNotFoundError:
            self.skipTest('Qt unavailable; native verification separately required')
        app=QApplication.instance() or QApplication([])
        e=environment([PARTS,EMERGENCY]);e['relic_context']['parts_count']=1
        e['operator_metadata']={'char_120_hibisc':{'recruitment_kind':'emergency_hire'}}
        p=defaults('char_120_hibisc');p['count']=2
        dialog=SupplementalRunDialog(p,lambda:e)
        app.processEvents();before=dialog.result['rows'][1]['value']
        editor=dialog.editor.toPlainText()
        e['relic_context']['parts_count']=3
        e['operator_metadata']['char_120_hibisc']['recruitment_kind']='non_emergency'
        self.assertEqual(dialog.environment['relic_context']['parts_count'],1)
        dialog.refresh_button.click();app.processEvents()
        self.assertEqual(dialog.editor.toPlainText(),editor)
        self.assertEqual(dialog.result['preview']['count'],2)
        self.assertLess(dialog.result['rows'][1]['value'],before)
        self.assertIn('非应急招募',dialog.notice.toPlainText())
        self.assertIn('零件3个',dialog.notice.toPlainText())
        # Selecting another identity must not inherit the known hire category.
        p['operator']='char_124_kroos'
        dialog.editor.setPlainText(json.dumps(p,ensure_ascii=False))
        dialog.calculate();app.processEvents()
        self.assertFalse(dialog.result['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('emergency_hire',dialog.notice.toPlainText())
        dialog.close()
