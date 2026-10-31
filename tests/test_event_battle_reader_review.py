"""Exact event links retain their data while using the shared player window."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt,QCoreApplication,QEvent
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid
from rouge import current_event_battles as events,current_battle_reference as battle
from rouge.current_event_battles_view import CurrentEventBattlesPanel,CurrentEventBattlesDialog
from rouge.player_map_reader import REFERENCE_STYLE

ROOT=Path(__file__).resolve().parents[1];COMPARISONS=[]

class EventBattleReaderReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def panel(self,*args,**kwargs):
  p=CurrentEventBattlesPanel(*args,**kwargs);self.addCleanup(p.close);return p
 def choose(self,p,cid,sid):
  index=next(i for i in range(p.choices.count())if p.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid)
  p.choices.setCurrentRow(index);p.stages.setCurrentIndex(p.stages.findData(sid));self.assertEqual(p.stages.currentData(),sid)
 def test_all_twenty_event_choice_stage_links_keep_complete_own_prior_reference_and_reading(self):
  raw=(ROOT/'research/event-battle-reader-review-20261031/before-current-event-battles-view.py').read_bytes()
  old=ModuleType('rouge._before_event_battle_reader_review');old.__package__='rouge';exec(compile(raw,'<verified-own-prior-event-reader>','exec'),old.__dict__)
  p=self.panel();prior=old.CurrentEventBattlesPanel();self.addCleanup(prior.close);COMPARISONS.clear()
  for row in p.result['rows']:
   for sid in row['stage_ids']:
    values=[]
    for instance in [prior,p]:
     self.choose(instance,row['id'],sid);self.assertTrue(instance.open_battle());child=instance.battle_dialog
     values.append(deepcopy((instance.result,instance.player.toPlainText(),instance.technical.toPlainText(),child.panel.result,child.panel.rewards.result,child.panel.settlement.result)))
     instance._close_battle()
    self.assertEqual(values[0],values[1]);COMPARISONS.append({'choice_id':row['id'],'stage_id':sid,'full_parent_and_child_reference_and_text_equal':True,'result_sha256':sha256(json.dumps(values[1],ensure_ascii=False,sort_keys=True,default=str).encode('utf8')).hexdigest()})
  self.assertEqual(len(COMPARISONS),20);self.assertEqual(len({v['stage_id']for v in COMPARISONS}),17)
 def test_same_exact_stage_reuses_shared_window_and_preserves_reward_choice_after_close(self):
  p=self.panel('鸭托邦','choice_ro6_bat3_3');self.choose(p,'choice_ro6_bat3_3','ro6_t_3');self.assertTrue(p.open_battle());d=p.battle_dialog
  self.assertTrue(d.windowFlags()&Qt.WindowType.FramelessWindowHint);self.assertEqual(d.objectName(),'mapReferenceWindow');self.assertEqual(d.styleSheet(),REFERENCE_STYLE)
  self.assertEqual(d.palette().color(QPalette.ColorRole.Window).name(),'#262528');self.assertEqual((d.width(),d.height()),(920,720));self.assertEqual(d.panel.tabs.count(),4)
  reward=d.panel.rewards;row=next(r for r in reward.result['rows']if r['source_action_keys']);reward.choices.select_value(row['id']);reward.source_combo.setCurrentIndex(1);choice=(reward.combo.currentData(),reward.source_combo.currentData());d.panel.tabs.setCurrentWidget(reward)
  for _ in range(3):
   d.close();self.assertIsNone(d.panel.settlement.result)
   with patch.object(battle,'stage_reference',wraps=battle.stage_reference)as load:self.assertTrue(p.open_battle())
   self.assertEqual(load.call_count,1);self.assertIs(p.battle_dialog,d);self.assertIsNotNone(d.panel.settlement.result);self.assertEqual(choice,(reward.combo.currentData(),reward.source_combo.currentData()));self.assertIs(d.panel.tabs.currentWidget(),reward)
 def test_different_stage_retires_old_owned_window_and_never_reuses_wrong_identity(self):
  p=self.panel('黑诞','choice_ro6_normal2_2');p.stages.setCurrentIndex(1);self.assertTrue(p.open_battle());old=p.battle_dialog;sid=old.panel.stage_id
  p.stages.setCurrentIndex(2);self.assertIsNone(p.battle_dialog);self.assertFalse(old.isVisible());self.assertTrue(p.open_battle());self.assertNotEqual(p.battle_dialog.panel.stage_id,sid)
  QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);self.assertFalse(isValid(old))
 def test_shared_stage_source_failure_never_returns_a_visible_empty_reader_and_recovery_manual(self):
  p=self.panel('鸭托邦','choice_ro6_bat3_3');self.choose(p,'choice_ro6_bat3_3','ro6_t_3')
  with patch.object(battle,'stage_reference',return_value=None):self.assertFalse(p.open_battle())
  self.assertIsNone(p.battle_dialog);self.assertTrue(p.open_battle());old=p.battle_dialog
  with patch.object(battle,'stage_reference',return_value=None):self.assertFalse(p.open_battle())
  self.assertFalse(old.isVisible());self.assertIsNone(p.battle_dialog);self.assertTrue(p.open_battle());self.assertIsNone(p.battle_dialog.panel.rewards.combo.currentData())
 def test_event_source_failure_clears_nested_readers_recovery_needs_new_choice(self):
  p=self.panel('鸭托邦','choice_ro6_bat3_3');self.choose(p,'choice_ro6_bat3_3','ro6_t_3');p.open_battle();d=p.battle_dialog;self.assertTrue(d.panel.open_event_origins());nested=d.panel.event_origins_dialog
  with patch.object(events,'reference',return_value=None):self.assertFalse(p.open_battle())
  self.assertIsNone(p.result);self.assertIsNone(p.battle_dialog);self.assertFalse(d.isVisible());self.assertFalse(nested.isVisible());self.assertEqual(p.technical.toPlainText(),'')
  self.assertTrue(p.refresh_reference());self.assertIsNone(p.choice_id);self.assertIsNone(p.stages.currentData());self.assertFalse(p.open_battle())
 def test_dialog_reject_closes_owned_battle_and_full_flow_without_discarding_parent_reading(self):
  d=CurrentEventBattlesDialog('鸭托邦','choice_ro6_bat3_3');d.show();self.addCleanup(d.close);p=d.panel;self.choose(p,'choice_ro6_bat3_3','ro6_t_3');p.open_battle();child=p.battle_dialog;self.assertTrue(p.open_full_flow());flow=p.flow_dialog;reading=p.player.toPlainText();d.reject()
  self.assertIsNone(p.battle_dialog);self.assertFalse(child.isVisible());self.assertFalse(flow.isVisible());self.assertEqual(p.player.toPlainText(),reading)

if __name__=='__main__':unittest.main()
