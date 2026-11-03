import json,unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_guest_material as model
from rouge.current_guest_material_view import CurrentGuestMaterialPanel,CurrentGuestMaterialDialog
class GuestBossView380Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
 def make(self,key=None):
  panel=CurrentGuestMaterialPanel(model.STAGES[0],key);self.addCleanup(panel.close);return panel
 def test_unselected_default_and_explicit_exact_selection(self):
  p=self.make();self.assertIsNone(p.selected_key);self.assertIsNotNone(p.result)
  key=p.result['rows'][0]['key'];self.assertTrue(p.entities.select_value(key))
  self.assertEqual(p.selected_key,key);self.assertIn(model.entity(p.result,key)['enemy']['name'],p.player.toPlainText())
 def test_related_controls_not_other_enemy_special_options(self):
  p=self.make();key=p.result['rows'][0]['key'];p.entities.select_value(key)
  self.assertEqual(p.topic.count()-1,len(model.topics(p.result,key)))
  self.assertEqual(p.related.count()-1,len(model.related_entities(p.result,key)))
  self.assertEqual(p.related_button.isEnabled(),len(p.result['rows'])>1)
 def test_selected_card_and_complete_sources_remain_separate(self):
  p=self.make();key=p.result['rows'][0]['key'];p.entities.select_value(key)
  topic=model.topics(p.result,key)[0][0];p.topic.setCurrentIndex(p.topic.findData(topic))
  actual=json.loads(p.technical.toPlainText());self.assertEqual(actual['selected_document_card'],model.selected_card(p.result,key,topic))
  self.assertIsNone(actual['actual_skill_time']);self.assertFalse(actual['numeric_model_added'])
  self.assertEqual(actual['retained_documentary_scope'],model.technical_scope_notes(p.result,key,topic))
  self.assertEqual(actual['retained_documentary_scope']['original_limits'],p.result['data']['limits'])
  self.assertNotIn('数据库级别',p.player.toPlainText());self.assertNotIn('dynamic',p.player.toPlainText())
 def test_same_source_refresh_preserves_selection_topic_and_tab(self):
  p=self.make();key=p.result['rows'][0]['key'];p.entities.select_value(key);p.topic.setCurrentIndex(1);p.tabs.setCurrentIndex(1)
  before=(p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),p.player.toPlainText(),p.technical.toPlainText())
  self.assertTrue(p.refresh_reference());self.assertEqual(before,(p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),p.player.toPlainText(),p.technical.toPlainText()))
 def test_source_loss_clears_all_then_recovery_requires_manual_choice(self):
  p=self.make();p.entities.select_value(p.result['rows'][0]['key'])
  with patch.object(model,'reference',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertIsNone(p.result);self.assertIsNone(p.selected_key);self.assertEqual(p.topic.count(),0);self.assertEqual(p.related.count(),0)
  self.assertEqual(p.player.toPlainText(),model.UNAVAILABLE);self.assertEqual(p.technical.toPlainText(),'');self.assertTrue(p.portrait.isHidden())
  self.assertFalse(p.map_button.isEnabled());self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected_key)
 def test_related_forgery_clears_current_source(self):
  p=self.make();p.entities.select_value(p.result['rows'][0]['key'])
  p.related.addItem('forged',{'enemy_key':'999'});p.related.setCurrentIndex(p.related.count()-1)
  self.assertFalse(p.follow_related());self.assertIsNone(p.result)
 def test_dialog_close_and_escape_clear_actual_source(self):
  d=CurrentGuestMaterialDialog(model.STAGES[0]);self.addCleanup(d.close);d.show();self.app.processEvents();d.close();self.app.processEvents();self.assertIsNone(d.panel.result)
  e=CurrentGuestMaterialDialog(model.STAGES[0]);self.addCleanup(e.close);e.reject();self.assertIsNone(e.panel.result)
if __name__=='__main__':unittest.main()
