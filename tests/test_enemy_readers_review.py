"""Shared reader lifecycle checked against the actual previous parent and data."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
from types import ModuleType
from unittest.mock import patch,Mock
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_battle_reference as battle,battle_enemy_readers as readers

ROOT=Path(__file__).resolve().parents[1]


class EnemyReadersReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([]);cls.fixtures=[]
  assert set(readers._READERS)=={'hanko','elbert','sun_boss','boss_documents','guest_knights','guest_crystals','guest_material'}
  for name,spec in readers._READERS.items():
   provider=import_module('rouge.'+spec.provider);sid=provider.STAGES[0];result=provider.reference(sid)
   row=(result.get('rows')or result.get('entities'))[0];cls.fixtures.append((name,spec,sid,row['enemy_key']if name=='boss_documents'else row['key']))
  raw=(ROOT/'research/enemy-readers-review-20261031/before-current-battle-view.py').read_bytes()
  assert sha256(raw).hexdigest()=='6284bf31f449f135121ba8acf7849accda73416841bf36447dda556bd8fdeb78'
  previous=ModuleType('rouge._before_enemy_readers_parent');previous.__package__='rouge'
  exec(compile(raw,'<verified-own-prior-parent>','exec'),previous.__dict__);cls.previous=previous.CurrentBattlePanel

 def parent(self,fixture,cls=CurrentBattlePanel):
  name,spec,sid,key=fixture;p=cls(sid);p.show();self.addCleanup(p.close)
  self.assertTrue(p.enemy_choices.select_value(key));self.qt.processEvents();return p

 def test_seven_real_readers_keep_complete_results_and_both_reading_texts(self):
  for fixture in self.fixtures:
   outputs=[]
   for cls in [self.previous,CurrentBattlePanel]:
    p=self.parent(fixture,cls);name=fixture[0];self.assertTrue(getattr(p,'open_'+name)());self.qt.processEvents()
    c=getattr(p,name+'_dialog').panel
    outputs.append(deepcopy((c.result,getattr(c,'base',None),c.player.toPlainText(),c.technical.toPlainText())))
   self.assertEqual(outputs[0],outputs[1],fixture[0])

 def test_same_source_sync_keeps_actual_tab_text_selection_and_scroll(self):
  for fixture in self.fixtures:
   p=self.parent(fixture);name=fixture[0];self.assertTrue(getattr(p,'open_'+name)());c=getattr(p,name+'_dialog').panel
   c.tabs.setCurrentWidget(c.technical);cursor=c.technical.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);c.technical.setTextCursor(cursor)
   bar=c.technical.verticalScrollBar();bar.setValue(min(3,bar.maximum()));before=(c.tabs.currentIndex(),cursor.anchor(),cursor.position(),bar.value())
   getattr(p,'_sync_'+name)(True);cursor=c.technical.textCursor()
   self.assertEqual(before,(c.tabs.currentIndex(),cursor.anchor(),cursor.position(),bar.value()),name)

 def test_changed_enemy_closes_and_clears_each_owned_reader(self):
  for fixture in self.fixtures:
   p=self.parent(fixture);name=fixture[0];self.assertTrue(getattr(p,'open_'+name)());d=getattr(p,name+'_dialog')
   getattr(p,'_sync_'+name)(False);self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result)

 def test_unavailable_target_clears_content_and_disables_the_exact_button(self):
  for fixture in self.fixtures:
   name,spec,_,_=fixture;p=self.parent(fixture);self.assertTrue(getattr(p,'open_'+name)());d=getattr(p,name+'_dialog')
   provider=import_module('rouge.'+spec.provider)
   with patch.object(provider,spec.availability,return_value=None if spec.availability=='locate'else False):getattr(p,'_sync_'+name)(True)
   self.assertIsNone(d.panel.result);self.assertFalse(getattr(p,name+'_button').isEnabled());self.assertTrue(getattr(p,name+'_button').isHidden())

 def test_parent_source_loss_refuses_opening_and_clears_parent_selection(self):
  for fixture in self.fixtures:
   p=self.parent(fixture)
   with patch.object(battle,'stage_reference',return_value=None):self.assertFalse(getattr(p,'open_'+fixture[0])())
   self.assertIsNone(p.result);self.assertIsNone(p.enemy_key)

 def test_original_six_source_checks_preserve_elbert_base_distinction(self):
  for fixture in self.fixtures:
   name,spec,_,_=fixture
   if not spec.check_battle_source:continue
   p=self.parent(fixture);self.assertTrue(getattr(p,'open_'+name)());d=getattr(p,name+'_dialog');c=d.panel
   wrong=deepcopy(getattr(c,spec.sync_result));wrong['battle_source_identity']=('synthetic different source',);setattr(c,spec.sync_result,wrong)
   with patch.object(c,'refresh_reference',return_value=True):getattr(p,'_sync_'+name)(True)
   self.assertFalse(d.isVisible());self.assertIsNone(c.result)

 def test_boss_document_related_entity_signal_is_connected_once(self):
  fixture=next(row for row in self.fixtures if row[0]=='boss_documents');p=self.parent(fixture)
  with patch.object(p,'_boss_documents_enemy_requested')as receive:
   self.assertTrue(p.open_boss_documents());p.boss_documents_dialog.panel.enemy_requested.emit(fixture[3]);receive.assert_called_once_with(fixture[3])

 def test_invalid_child_still_clears_and_never_shows(self):
  for fixture in self.fixtures:
   name,spec,_,_=fixture;p=self.parent(fixture);view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view')
   child=Mock();child.panel.result=None
   with patch.object(view,spec.dialog,return_value=child):self.assertFalse(getattr(p,'open_'+name)())
   child.show.assert_not_called();child.panel.clear_reference.assert_called_once();child.close.assert_called_once()


if __name__=='__main__':unittest.main()
