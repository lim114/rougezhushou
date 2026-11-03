from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtGui import QTextCursor,QFont
from PySide6.QtWidgets import QLabel,QTextBrowser
from rouge.reporting import format_report
from tests import test_state_calculation_updates as fixture

class CalculatorLayoutTests(unittest.TestCase):
 setUp=fixture.StateCalculationUpdateTests.setUp
 @classmethod
 def setUpClass(cls):cls.qt=fixture.QApplication.instance()or fixture.QApplication([])
 def test_result_first_controls_and_read_only_stats_keep_original_output(self):
  w=self.window;w.workspace.setCurrentWidget(w.damage_page);w.show();self.qt.processEvents();self.assertFalse(w.damage_settings_fold.isExpanded());self.assertTrue(w.operator_choices.isVisible());self.assertTrue(w.skill.isVisible());self.assertTrue(w.damage_text.isVisible());self.assertIsInstance(w.damage_text,QTextBrowser);self.assertTrue(w.damage_text.isReadOnly());self.assertTrue(w.level.visibleRegion().isEmpty());self.assertEqual(w.damage_text.toPlainText(),format_report(w.damage_result['result']));self.assertTrue(all(isinstance(x,QLabel)for x in(w.elite,w.trust,w.potential,w.module,w.rank)))
 def test_settings_open_close_preserves_inputs_and_does_not_recalculate(self):
  w=self.window;before=deepcopy(w.damage_result);state=deepcopy(w.run.state);values=(w.level.value(),w.operator.currentData(),w.skill.currentData(),w.auto_relics.isChecked(),w.target_enemy.currentData())
  with patch.object(w,'calculate',side_effect=AssertionError('layout must not calculate')):
   w.damage_settings_fold.expand(animate=False);self.qt.processEvents();w.damage_settings_fold.collapse(animate=False);self.qt.processEvents()
  self.assertEqual(w.damage_result,before);self.assertEqual(w.run.state,state);self.assertEqual(values,(w.level.value(),w.operator.currentData(),w.skill.currentData(),w.auto_relics.isChecked(),w.target_enemy.currentData()))
 def test_all_nine_first_three_skills_reach_original_models_without_opening_settings(self):
  w=self.window
  for op in('kaltsit','silverash','mechanist'):
   w.select_operator(op)
   for n in(1,2,3):
    self.assertGreaterEqual(w.skill.findData(n),0);w.skill.setCurrentIndex(w.skill.findData(n));self.assertIsNotNone(w.damage_result);self.assertEqual(w.damage_result['scenario']['operator'],op);self.assertEqual(w.damage_result['scenario']['skill'],n);self.assertFalse(w.damage_settings_fold.isExpanded());self.assertEqual(w.damage_text.toPlainText(),format_report(w.damage_result['result']))
 def test_report_navigation_only_contains_current_capabilities(self):
  w=self.window;w.select_operator('char_151_myrtle');w.skill.setCurrentIndex(w.skill.findData(1));items=[w.damage_sections.itemText(i)for i in range(w.damage_sections.count())];self.assertIn('费用收益',items);self.assertNotIn('治疗输出',items);self.assertNotIn('伤害输出',items);w.select_operator('char_298_susuro');items=[w.damage_sections.itemText(i)for i in range(w.damage_sections.count())];self.assertIn('治疗输出',items);self.assertNotIn('费用收益',items);self.assertNotIn('伤害输出',items)
 def test_same_source_refresh_retains_navigation_and_text_selection(self):
  w=self.window;index=w.damage_sections.findText('技能时序');self.assertGreater(index,0);w.damage_sections.setCurrentIndex(index);cursor=w.damage_text.textCursor();cursor.setPosition(2);cursor.setPosition(6,QTextCursor.MoveMode.KeepAnchor);w.damage_text.setTextCursor(cursor);text=cursor.selectedText();w.render_damage();self.assertEqual(w.damage_sections.currentText(),'技能时序');self.assertEqual(w.damage_text.textCursor().selectedText(),text);w.select_operator('kaltsit');self.assertEqual(w.damage_sections.currentIndex(),0)
 def test_archive_preview_is_explicit_and_preserves_current_grade16_record(self):
  w=self.window;w.run.state['config']['difficulty']={'value':16,'source':'public-fixed-current-example'};state=deepcopy(w.run.state);w.calculate();self.assertIsNone(w.damage_result);self.assertIn('保密等级',w.damage_text.toPlainText());self.assertEqual(w.calculation_scope.currentData(),'run');w.calculation_scope.setCurrentIndex(w.calculation_scope.findData('archive'));self.assertIsNotNone(w.damage_result);self.assertEqual(w.damage_result['scenario']['run_config'],{});self.assertEqual(w.damage_result['calculation_mode'],'archive');self.assertTrue(w.damage_text.toPlainText().startswith('档案预览'));self.assertEqual(w.run.state,state);w.calculation_scope.setCurrentIndex(w.calculation_scope.findData('run'));self.assertIsNone(w.damage_result);self.assertEqual(w.run.state,state)
 def test_heading_is_bold_and_debug_replaces_old_navigation(self):
  w=self.window;block=w.damage_text.document().findBlockByNumber(0);cursor=QTextCursor(block);cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock,QTextCursor.MoveMode.KeepAnchor);self.assertGreaterEqual(cursor.charFormat().fontWeight(),QFont.Weight.Bold);w.raw_damage.setChecked(True);self.assertEqual(w.damage_sections.count(),1);self.assertTrue(w.damage_text.toPlainText().startswith('{'));w.raw_damage.setChecked(False);self.assertGreater(w.damage_sections.count(),1)

if __name__=='__main__':unittest.main()
