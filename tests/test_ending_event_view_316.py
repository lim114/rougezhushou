from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import ending_event_reference as model
from rouge.ending_event_view import EndingEventPanel
from rouge.expansion_view import ExpansionUpdatePanel
ROOT=Path(__file__).resolve().parents[1]

class EndingEventView316Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self):
        p=EndingEventPanel();p.resize(900,720);p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def test_real_branches_no_auto_event_or_battle(self):
        p=self.panel();self.assertEqual(p.choices.branch.count(),5);self.assertIsNone(p.combo.currentData());self.assertFalse(p.battle_button.isEnabled())
        for group in ('命运所指','不期而遇','出现类型未确认'):self.assertTrue(p.choices.select_branch(group));self.assertIsNone(p.combo.currentData());self.assertEqual(p.combo.count(),2)
    def test_all_records_full_technical_originals_and_manual_battles(self):
        p=self.panel()
        for r in model.packet()['data']['records']:
            self.assertTrue(p.choices.select_value(r['id']));self.assertIn(r['title'],p.player.toPlainText());self.assertEqual(json.loads(p.technical.toPlainText()),p.result);self.assertEqual(p.battle_combo.count()-1,len(r['stage_ids']));self.assertFalse(p.battle_button.isEnabled())
    def test_conditions_change_preserves_choice_and_unknown_is_not_no(self):
        p=self.panel();p.choices.select_value('entry')
        for key,value in [('floor',1),('node_type','险路尽头'),('post_update_clear',True)]:p.controls[key].setCurrentIndex(p.controls[key].findData(value))
        p.gold.setText('9');self.assertEqual(p.result['listed_conditions_status'],'listed_matched');self.assertEqual(p.result['choice_conditions_status']['choice_ro6_final1_8'],'not_matched');p.gold.clear();self.assertEqual(p.result['choice_conditions_status']['choice_ro6_final1_8'],'unknown');self.assertEqual(p.combo.currentData(),'entry')
        for text in ('-1','abc','1.5'):
            p.gold.setText(text);self.assertIsNone(p.result);self.assertFalse(p.battle_button.isEnabled());self.assertEqual(p.technical.toPlainText(),'')
        p.gold.setText('10');self.assertEqual(p.result['choice_conditions_status']['choice_ro6_final1_8'],'listed_matched')
    def test_nonzero_reader_states_survive_same_source_refresh(self):
        p=self.panel();p.resize(900,520);self.app.processEvents();p.choices.select_value('hidden_region');p.battle_combo.setCurrentIndex(6)
        for widget in(p.player,p.technical):
            p.tabs.setCurrentWidget(widget);self.app.processEvents();cursor=widget.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor);bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(5,bar.maximum()));before=(cursor.anchor(),cursor.position(),bar.value(),p.tabs.currentIndex(),p.combo.currentData(),p.battle_combo.currentData())
            self.assertTrue(p.refresh_reference());self.app.processEvents();c=widget.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.tabs.currentIndex(),p.combo.currentData(),p.battle_combo.currentData()))
    def test_exact_current_battle_links_repeat_closes_prior_and_source_loss_clears(self):
        p=self.panel();self.assertFalse(p.open_battle());p.choices.select_value('button');p.battle_combo.setCurrentIndex(1);self.assertTrue(p.open_battle());old=p.battle_dialog;self.assertTrue(old.isVisible());self.assertEqual(old.panel.stage_id,'ro6_s_1');self.assertTrue(p.open_battle());self.assertFalse(old.isVisible())
        with patch.object(model,'packet',return_value=None):self.assertFalse(p.open_battle());self.assertFalse(p.battle_dialog.isVisible());self.assertIsNone(p.result);self.assertEqual(p.battle_combo.count(),0)
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.combo.currentData());self.assertFalse(p.battle_button.isEnabled())
    def test_actual_corrupted_file_clears_all_then_manual_recovery(self):
        p=self.panel();p.choices.select_value('button');manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
            with patch.object(model,'ROOT',root):
                file=root/model.DATA;raw=file.read_bytes();file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.combo.currentData())
    def test_update_page_entry_owns_dialog_and_closes_on_source_loss(self):
        p=ExpansionUpdatePanel();p.show();self.addCleanup(p.close);self.assertTrue(p.open_ending_events());old=p.ending_dialog;self.assertTrue(p.open_ending_events());self.assertFalse(old.isVisible());p._unavailable();self.assertFalse(p.ending_dialog.isVisible())

if __name__=='__main__':unittest.main()
