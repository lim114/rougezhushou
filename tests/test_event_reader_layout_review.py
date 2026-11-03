from pathlib import Path
import ast,unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.current_vine_events_view import CurrentVineEventsDialog
from rouge.player_map_reader import readable
from rouge.reference_copy import mechanism_copy
from tests.test_current_vine_events_333 import by_original
R=Path(__file__).resolve().parents[1]
class EventReaderLayoutTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,title='呼吸的红苔'):
  d=readable(CurrentVineEventsDialog(title));d.show();self.qt.processEvents();self.addCleanup(d.close);return d
 def pick(self,p,key):
  c=by_original(p.result,key);p.choices.setCurrentRow(next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==c['id']));return c
 def test_external_class_is_exact_except_binding_imports(self):
  old=(R/'research/event-reader-layout-20261101/upstream-collapsible.py').read_text('utf8').replace('from qtpy.','from PySide6.');new=(R/'rouge/collapsible_section.py').read_text('utf8');self.assertEqual(ast.dump(ast.parse(old)),ast.dump(ast.parse(new)))
 def test_collapsed_condition_widgets_are_really_hidden_not_just_clipped(self):
  p=self.dialog().panel;self.assertFalse(p.conditions.isExpanded());self.assertFalse(p.controller.isVisible());self.assertFalse(p.seeds.isVisible());self.assertTrue(p.conditions.toggleButton().isVisible());self.assertIsNone(p.controller.currentData());self.assertEqual(p.seeds.value(),-1)
 def test_real_button_and_keyboard_expand_and_collapse_same_controls(self):
  p=self.dialog().panel;button=p.conditions.toggleButton();QTest.mouseClick(button,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertTrue(p.controller.isVisible());self.assertTrue(p.seeds.isVisible());button.setFocus();QTest.keyClick(button,Qt.Key.Key_Space);self.qt.processEvents();self.assertFalse(p.controller.isVisible());self.assertFalse(p.seeds.isVisible());self.assertFalse(p.controller.hasFocus())
 def test_expanded_refresh_and_collapse_preserve_local_values_choice_and_text(self):
  p=self.dialog().panel;p.conditions.expand(False);self.pick(p,'choice_ro6_normal3_1');p.controller.setCurrentIndex(p.controller.findData(True));p.seeds.setValue(2);before=(p.scene_id,p.choice_id,p.player.toPlainText());self.assertTrue(p.refresh_reference());self.assertTrue(p.conditions.isExpanded());self.assertEqual((p.scene_id,p.choice_id,p.player.toPlainText()),before);p.conditions.collapse(False);self.qt.processEvents();self.assertEqual(p.controller.currentData(),True);self.assertEqual(p.seeds.value(),2);self.assertEqual((p.scene_id,p.choice_id,p.player.toPlainText()),before)
 def test_seed_and_controller_keep_their_independent_condition_results(self):
  p=self.dialog().panel;p.conditions.expand(False);self.pick(p,'choice_ro6_normal3_1');p.controller.setCurrentIndex(p.controller.findData(False));self.assertFalse(p.follow_scene());p.controller.setCurrentIndex(p.controller.findData(True));self.assertTrue(p.follow_scene());p.go_start();self.pick(p,'choice_ro6_normal3_2');p.controller.setCurrentIndex(p.controller.findData(False));p.seeds.setValue(0);self.assertFalse(p.follow_scene());p.seeds.setValue(1);self.assertTrue(p.follow_scene())
 def test_gold_is_event_specific_and_gates_the_original_boundary(self):
  p=self.dialog('沉寂之屋').panel;self.assertFalse(hasattr(p,'controller'));self.assertFalse(hasattr(p,'seeds'));self.assertFalse(p.gold.isVisible());p.conditions.expand(False);self.qt.processEvents();self.pick(p,'choice_ro6_normal1_2');p.gold.setValue(7);self.assertFalse(p.follow_scene());p.gold.setValue(8);self.assertTrue(p.follow_scene())
 def test_headings_are_bold_without_changing_plain_original_or_body(self):
  p=self.dialog().panel;self.pick(p,'choice_ro6_normal3_1');self.qt.processEvents();p.heading_highlighter.rehighlight();from rouge import current_vine_events as m
  self.assertEqual(p.player.toPlainText(),mechanism_copy(m.player_text(p.result,p.scene_id,p.choice_id),'',extra_detail_headings=('【范围与未知】',))[0]);self.assertEqual(p.reference_notes.toPlainText(),m.player_text(p.result,p.scene_id,p.choice_id));first=p.player.document().firstBlock();formats=first.layout().formats();self.assertTrue(any(f.start==0 and f.format.fontWeight()==QFont.Weight.Bold for f in formats));self.assertEqual(p.player.toPlainText().splitlines()[0],'【正在查阅】呼吸的红苔')
 def test_source_loss_clears_old_reading_and_recovery_requires_selection(self):
  p=self.dialog().panel;p.conditions.expand(False);self.pick(p,'choice_ro6_normal3_1')
  with patch('rouge.current_vine_events.reference',return_value=None):self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertEqual(p.reference_notes.toPlainText(),'');self.assertFalse(p.reference_scope.isExpanded());self.assertFalse(p.next_button.isEnabled())
  self.assertTrue(p.refresh_reference());self.assertIsNone(p.scene_id);self.assertIsNone(p.choice_id);self.assertTrue(p.conditions.isExpanded())
 def test_no_empty_condition_panel_for_other_events(self):
  from rouge.current_encounters_view import CurrentEncountersDialog
  from rouge import current_encounters as m
  title=next(k for k in m.packet()['data']['events']if k!='黑诞');d=readable(CurrentEncountersDialog(title));d.show();self.addCleanup(d.close);self.qt.processEvents();self.assertTrue(d.panel.conditions.isHidden());self.assertFalse(hasattr(d.panel,'controller'))
 def test_all_six_condition_dialog_families_have_compact_visible_forms(self):
  from rouge.box_event_view import BoxEventDialog
  from rouge.current_exit_view import CurrentExitDialog
  from rouge.current_memory_tree_view import CurrentMemoryTreeDialog
  from rouge.current_encounters_view import CurrentEncountersDialog
  from rouge.current_resource_events_view import CurrentResourceEventsDialog
  from rouge import current_resource_events as m
  makers=[BoxEventDialog,CurrentExitDialog,CurrentMemoryTreeDialog,lambda:CurrentEncountersDialog('黑诞'),lambda:CurrentResourceEventsDialog(m.GOLD_EVENTS[0])]
  for make in makers:
   d=readable(make());d.show();self.addCleanup(d.close);self.qt.processEvents();self.assertEqual((d.width(),d.height()),(760,600));p=d.panel;self.assertFalse(p.conditions.isExpanded());self.assertFalse(p.conditions.isHidden());p.conditions.expand(False);self.qt.processEvents();self.assertTrue(p.conditions.content().isVisible());self.assertGreater(p.conditions.content().height(),0);self.assertLess(p.conditions.geometry().bottom(),p.scene.geometry().top())
 def test_common_factory_applies_same_external_theme_for_direct_catalog_route(self):
  from rouge import current_vine_events as m,current_node_readers as bridge
  from rouge.current_node_readers_view import make_dialog
  record=m.packet()['data']['catalogue_bindings']['community_group_009']['expected_summary'];d=make_dialog(bridge.binding_for(record));self.addCleanup(d.close);self.assertEqual(d.property('playerTheme'),'dark');self.assertEqual(d.panel.event_id,'呼吸的红苔');self.assertTrue(hasattr(d,'node_reference_binding'))
 def test_map_route_applies_common_theme_exactly_once(self):
  from rouge import current_vine_events as m,player_map_reader
  record=m.packet()['data']['catalogue_bindings']['community_group_009']['expected_summary']
  with patch.object(player_map_reader,'readable',wraps=player_map_reader.readable)as apply:
   d=player_map_reader.make_reader('event',record,None);self.addCleanup(d.close);self.assertIsNotNone(d);self.assertEqual(apply.call_count,1);self.assertEqual(d.property('playerTheme'),'dark')
 def test_current_event_directory_uses_the_same_qualified_theme_entry(self):
  from rouge import current_event_directory as m
  from rouge.current_event_directory_view import make_event_dialog
  row=next(r for r in m.reference()['rows']if r['title']=='呼吸的红苔');target=m.resolve(m.reference(row['id']));d=make_event_dialog(target);self.addCleanup(d.close);self.assertEqual(d.property('playerTheme'),'dark');self.assertEqual(d.panel.scene_id,target['scene_id']);self.assertEqual(d.panel.event_id,'呼吸的红苔')
 def test_recent_event_route_applies_theme_once_and_keeps_exact_scene(self):
  from types import SimpleNamespace
  from rouge.player_recent_scene import RecentScenePanel
  from rouge import player_map_reader
  p=RecentScenePanel(SimpleNamespace(state={'id':'public-theme-case','last_node_content':{'kind':'event','title':'呼吸的红苔'}}));self.addCleanup(p.close);p.event_choices.setCurrentIndex(1);target=p._target()
  with patch.object(player_map_reader,'readable',wraps=player_map_reader.readable)as apply:
   self.assertTrue(p.open_event());self.assertEqual(apply.call_count,1);self.assertEqual(p.event_dialog.property('playerTheme'),'dark');self.assertEqual(p.event_dialog.panel.scene_id,target['scene_id'])
 def test_source_rejected_before_styling_without_a_second_nullable_wrapper(self):
  from rouge import current_event_directory as m,player_map_reader
  from rouge.current_event_directory_view import make_event_dialog
  row=next(r for r in m.reference()['rows']if r['title']=='呼吸的红苔');target=m.resolve(m.reference(row['id']))
  with patch.object(m,'reference',return_value=None),patch.object(player_map_reader,'readable',wraps=player_map_reader.readable)as apply:
   self.assertIsNone(make_event_dialog(target));self.assertEqual(apply.call_count,0)
 def test_collapse_returns_the_space_to_actual_reading_after_layout_events(self):
  p=self.dialog().panel;p.choices.setCurrentRow(0);text=p.player.toPlainText();p.conditions.toggleButton().click();QTest.qWait(20);self.qt.processEvents();old=(p.scene.y(),p.tabs.height());p.conditions.toggleButton().click();QTest.qWait(20);self.qt.processEvents();self.assertLess(p.scene.y(),old[0]);self.assertGreater(p.tabs.height(),old[1]);self.assertEqual(p.player.toPlainText(),text)
if __name__=='__main__':unittest.main()
