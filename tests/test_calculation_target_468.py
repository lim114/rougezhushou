from copy import deepcopy
from unittest.mock import patch,Mock
import unittest
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QTextCursor
from rouge import current_battle_reference as model,player_calculation_target as route
from tests import test_state_calculation_updates as fixture

class CalculationTargetTests(unittest.TestCase):
 setUp=fixture.StateCalculationUpdateTests.setUp
 @classmethod
 def setUpClass(cls):cls.qt=fixture.QApplication.instance()or fixture.QApplication([])
 def target(self,sid='ro6_n_2_3',enemy=True):
  w=self.window;self.assertTrue(w.target_stage_choices.select_value(sid));ref=model.stage_reference(sid);e=ref['enemies'][0]
  if enemy:self.assertTrue(w.target_enemy_choices.select_value({'stage_id':sid,'enemy_id':e['id'],'level':e['level']}))
  return e
 def opened(self):
  self.assertTrue(self.window.open_calculation_target());self.qt.processEvents();return self.window.compact_window.reference_window.pages.currentWidget()
 def test_exact_target_enemy_opens_in_shared_host_without_changing_calculation(self):
  w=self.window;e=self.target();before=deepcopy(w.damage_result);state=deepcopy(w.run.state);page=self.opened();c=w.compact_window;self.assertIs(page.source_parent,c.workspace_popup);self.assertEqual(page.panel.stage_id,'ro6_n_2_3');self.assertEqual(page.panel.enemy_key,e['key']);self.assertEqual(page.panel.tabs.currentIndex(),1);self.assertEqual(page.panel.run_config,{});self.assertGreaterEqual(page.panel.enemy_player.viewport().visibleRegion().boundingRect().height(),4*page.panel.enemy_player.fontMetrics().lineSpacing());self.assertEqual(w.damage_result,before);self.assertEqual(w.run.state,state)
  next(b for b in page.header.findChildren(QPushButton)if b.text()=='返回计算').click();self.assertIs(c.reference_window.pages.currentWidget(),c.workspace_popup);self.assertIs(w.workspace.currentWidget(),w.damage_page);self.assertEqual(w.damage_result,before)
 def test_enemy_default_copy_is_short_and_full_notes_can_be_opened(self):
  self.target();p=self.opened().panel;text=p.enemy_player.toPlainText();self.assertIn('预计面板：待补齐当前版本修正。',text);self.assertNotIn('【适用提醒】',text);self.assertNotIn('不代表被击倒',text)
  enemy=next(e for e in p.result['enemies']if e['key']==p.enemy_key);full=model.enemy_text(enemy,p.enemy_forecasts.get(p.enemy_key));p.details_toggle.setChecked(True);self.assertEqual(p.enemy_player.toPlainText(),full);self.assertIn('【适用提醒】',p.enemy_player.toPlainText());p.details_toggle.setChecked(False);self.assertEqual(p.enemy_player.toPlainText(),text)
 def test_reopen_keeps_original_reader_query_manual_enemy_and_reading(self):
  w=self.window;self.target();page=self.opened();p=page.panel;other=p.result['enemies'][1];p.enemy_choices.select_value(other['key'],emit=True);p.enemy_search.setText(other['name']);p.tabs.setCurrentIndex(1);cursor=p.enemy_player.textCursor();cursor.setPosition(2);cursor.setPosition(5,QTextCursor.MoveMode.KeepAnchor);p.enemy_player.setTextCursor(cursor);selected=cursor.selectedText();w.compact_window.open_full(w.damage_page);self.assertIs(self.opened(),page);self.assertEqual(p.enemy_search.text(),other['name']);self.assertEqual(p.enemy_key,other['key']);self.assertEqual(p.enemy_player.textCursor().selectedText(),selected)
 def test_target_change_expires_reference_and_map_descendant(self):
  w=self.window;self.target();page=self.opened();self.assertTrue(page.panel.open_map_positions());mapped=w.compact_window.reference_window.pages.currentWidget();w.compact_window.open_full(w.damage_page);self.target('ro6_n_1_1');host=w.compact_window.reference_window;host.navigate(host.cursor-1);self.assertNotIn(page,host.history);self.assertNotIn(mapped,host.history);self.assertIs(host.pages.currentWidget(),w.compact_window.workspace_popup)
 def test_calculation_mode_change_expires_target_reader(self):
  w=self.window;self.target();page=self.opened();w.compact_window.open_full(w.damage_page);w.calculation_scope.setCurrentIndex(w.calculation_scope.findData('archive'));host=w.compact_window.reference_window;host.navigate(host.cursor-1);self.assertNotIn(page,host.history);self.assertEqual(self.opened().link_context[-1],'archive')
 def test_legacy_stage_entry_uses_its_own_source_without_overwriting_calculator_target(self):
  w=self.window;self.target();target=w.target_stage.currentData();before=deepcopy(w.damage_result);w.battle_preview.set_stage('ro6_n_1_1');w.battle_preview.current_reference_button.click();host=w.compact_window.reference_window;page=host.pages.currentWidget();self.assertEqual(page.panel.stage_id,'ro6_n_1_1');self.assertEqual(w.target_stage.currentData(),target);self.assertEqual(w.damage_result,before)
 def test_missing_stage_keeps_calculation_and_shows_short_notice(self):
  w=self.window;self.target();before=deepcopy(w.damage_result)
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(w.open_calculation_target())
  self.assertEqual(w.target_preview_status.text(),'该关卡暂无作战资料。');self.assertEqual(w.damage_result,before)
 def test_no_selected_stage_has_no_visible_entry_or_new_window(self):
  w=self.window;w.target_stage_choices.select_value(None);self.assertTrue(w.target_preview_button.isHidden());self.assertFalse(w.open_calculation_target());self.assertIsNone(w.compact_window)
 def test_ambiguous_exact_id_level_is_not_silently_selected(self):
  w=self.window;self.target();original=route.make_reader
  def ambiguous(*args,**kwargs):
   page=original(*args,**kwargs);page.panel.result=deepcopy(page.panel.result);row=deepcopy(page.panel.result['enemies'][0]);row['key']='synthetic-second-reference';page.panel.result['enemies'].append(row);page.panel.refresh_reference=Mock(return_value=True);page.panel.enemy_choices.select_value=Mock(side_effect=AssertionError('ambiguous identity must remain unselected'));return page
  with patch.object(route,'make_reader',side_effect=ambiguous):page=self.opened()
  self.assertIsNone(page.panel.enemy_key);self.assertEqual(page.panel.tabs.currentIndex(),0)
 def test_unmatched_enemy_level_keeps_fixed_stage_without_name_fallback(self):
  w=self.window;e=self.target();target={'stage_id':'ro6_n_2_3','enemy_id':e['id'],'level':999};w.target_enemy.addItem('Synthetic unmatched level',target);w.target_enemy.setCurrentIndex(w.target_enemy.count()-1);page=self.opened();self.assertEqual(page.panel.stage_id,'ro6_n_2_3');self.assertIsNone(page.panel.enemy_key)

if __name__=='__main__':unittest.main()
