from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from types import SimpleNamespace
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge.relic_quantities import KETTLE,confirmed_bar_counts,kettle_copies
from rouge.run_state import RunState
from rouge.player_resource_facts import inventory_summary
from rouge.player_inventory import InventoryPanel

OTHER='rogue_6_relic_cargo_1';TOOL='rogue_6_active_tool_5'
def observe(run,ids,at=1):
 run.apply({'relics':{'ids':[k for k in ids if k!=TOOL],'count':len(ids),'source':'isolated-positive-slots','icons':[{'id':k,'candidates':[k],'confirmed':True}for k in ids]}},run.state['started_at']+at)

class KettleCopies446(unittest.TestCase):
 def run_state(self):
  folder=TemporaryDirectory();self.addCleanup(folder.cleanup);return RunState(Path(folder.name)/'run.json')
 def test_full_positive_copies_count_physical_items_keep_unique_ids(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);self.assertTrue(r.state['inventory_verified']);self.assertEqual(r.inventory_status()['recognized'],4);self.assertEqual(r.inventory_status()['recognized_tools'],1);self.assertTrue(r.inventory_status()['complete']);self.assertEqual(r.held_relic_ids(),sorted([KETTLE,OTHER]));self.assertEqual(inventory_summary(r.state)['relics'],4);self.assertEqual(inventory_summary(r.state)['expected_relics'],4)
 def test_restart_and_metadata_reuse_keep_copies_without_extra_acquisition_events(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);history=deepcopy(r.state['history']);r.apply({},r.state['started_at']+2);self.assertEqual(kettle_copies(r.state),3);self.assertEqual(r.state['history'],history);self.assertTrue(r.save());restored=RunState(r.file);self.assertEqual(kettle_copies(restored.state),3);self.assertTrue(restored.inventory_status()['complete'])
 def test_changed_badge_partial_bar_cannot_reuse_old_copy_quantity(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);r.apply({'relics':{'ids':[KETTLE],'count':6,'icons':[],'source':'partial-name'}},r.state['started_at']+2);self.assertIsNone(kettle_copies(r.state));self.assertFalse(r.inventory_status()['complete']);self.assertIn(OTHER,r.state['relics'])
 def test_complete_new_bar_marks_absence_without_erasing_old_records(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);observe(r,[KETTLE]*2,2);self.assertTrue(r.inventory_status()['complete']);self.assertEqual(kettle_copies(r.state),2);self.assertFalse(r.state['relics'][OTHER]['held']);self.assertFalse(r.state['tactical_tools'][TOOL]['held']);self.assertTrue(any(x.get('id')==OTHER for x in r.state['history']))
 def test_non_kettle_duplicates_or_ambiguous_slots_do_not_prove_complete(self):
  r=self.run_state();observe(r,[OTHER,OTHER]);self.assertFalse(r.inventory_status()['complete']);self.assertIsNone(confirmed_bar_counts([{'id':KETTLE,'confirmed':False}],1));self.assertIsNone(confirmed_bar_counts([{'id':KETTLE,'confirmed':1}],1))
 def test_unknown_flags_or_inconsistent_memory_cannot_supply_quantity(self):
  r=self.run_state();observe(r,[KETTLE,KETTLE]);baseline=deepcopy(r.state)
  for field,value in(('complete_bar','true'),('count',True),('count',3)):
   state=deepcopy(baseline);state['relic_icon_memory'][field]=value;before=deepcopy(state);self.assertIsNone(kettle_copies(state));self.assertEqual(state,before)
  state=deepcopy(baseline);state['relics'][KETTLE]['held']=None;self.assertIsNone(kettle_copies(state));self.assertFalse(inventory_summary(state)['complete'])
 def test_repeated_kettles_do_not_invent_current_resource_values(self):
  r=self.run_state();observe(r,[KETTLE]*3);self.assertNotIn('hope',r.state['resources']);self.assertNotIn('life',r.state['resources'])
 def test_healthy_legacy_complete_record_proves_one_but_large_badge_does_not(self):
  state={'inventory_verified':True,'relic_count':2,'relics':{KETTLE:{},OTHER:{}}};self.assertEqual(kettle_copies(state),1);state['relic_count']=5;self.assertIsNone(kettle_copies(state))
 def test_hundred_copy_boundary_and_manual_temporary_reset(self):
  r=self.run_state();observe(r,[KETTLE]*100);self.assertEqual(kettle_copies(r.state),100);self.assertEqual(r.inventory_status()['recognized'],100);old=r.state['id'];r.reset();self.assertNotEqual(r.state['id'],old);self.assertIsNone(kettle_copies(r.state));self.assertFalse(r.state['relics'])

class InventoryModes446(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def panel(self):
  folder=TemporaryDirectory();self.addCleanup(folder.cleanup);r=RunState(Path(folder.name)/'run.json');observe(r,[KETTLE]*3+[OTHER]);p=InventoryPanel(r);self.addCleanup(p.close);p.resize(1100,540);p.show();self.gui.processEvents();return p,r
 def test_merge_only_kettles_preserves_exact_identity_and_source_actions(self):
  p,r=self.panel();self.assertEqual(p.entries.count(),4);self.assertEqual(len(p.rows),2);p.entries.setCurrentRow(2);p.merge_kettles.click();self.assertEqual(p.entries.count(),2);self.assertEqual(p.entries.currentItem().data(Qt.ItemDataRole.UserRole),KETTLE);self.assertIn('×3',p.entries.currentItem().text());calls=[];p.openReference.connect(calls.append);p.open_selected();self.assertEqual(calls,[KETTLE]);self.assertIn('3件',p.detail.toPlainText());p.merge_kettles.click();self.assertEqual(p.entries.count(),4)
 def test_mode_changes_preserve_identity_description_and_selection(self):
  p,r=self.panel();p.entries.setCurrentRow(0);entry=p.entries.currentItem();text=p.detail.toPlainText();p.icon_scale.setValue(48);self.gui.processEvents();self.assertIs(p.entries.currentItem(),entry);self.assertTrue(p.entries.item(0).data(Qt.ItemDataRole.UserRole+2));self.assertEqual(p.detail.toPlainText(),text);p.icon_scale.setValue(104);self.assertIs(p.entries.currentItem(),entry)
 def test_reference_catalogue_and_other_variants_are_not_copy_expanded(self):
  p,r=self.panel();p.held.setChecked(False);self.assertEqual(p.entries.count(),len(p.rows));self.assertFalse(p.merge_kettles.isVisible());ids=[p.entries.item(i).data(Qt.ItemDataRole.UserRole)for i in range(p.entries.count())];self.assertEqual(len(ids),len(set(ids)))
 def test_unknown_copy_quantity_is_labeled_not_guessed(self):
  p,r=self.panel();r.state['relic_icon_memory']=None;r.state['inventory_verified']=False;p.refresh();self.assertEqual(p.entries.count(),2);self.assertIn('件数未确认',p.entries.item(0).text());self.assertIn('重复件数未确认',p.summary.text());self.assertNotIn('×3',p.entries.item(0).text())
 def test_card_layout_uses_available_width_and_keeps_all_items(self):
  p,r=self.panel();p.held.setChecked(False);p.icon_scale.setValue(48);p.reader.hide()
  for width in(480,760,1100):
   p.resize(width,540);self.gui.processEvents();p.entries.doItemsLayout();self.gui.processEvents();rect=p.entries.visualItemRect(p.entries.item(0));self.assertGreater(rect.width(),180);self.assertLessEqual(rect.width(),p.entries.viewport().width());self.assertEqual(p.entries.count(),len(p.rows))

if __name__=='__main__':unittest.main()
