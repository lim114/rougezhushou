from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_reward_reference as model
from rouge.current_reward_view import CurrentRewardPanel
ROOT=Path(__file__).resolve().parents[1]

class CurrentRewardView315Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self,sid='ro6_n_2_6'):
        p=CurrentRewardPanel(sid);p.resize(900,430);p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def test_real_branches_default_summary_and_manual_choice_not_actual_total(self):
        p=self.panel();self.assertIsNone(p.combo.currentData());self.assertFalse(p.source_button.isEnabled());self.assertIn('完整结算奖励',p.player.toPlainText());self.assertEqual(p.choices.branch.count(),4)
        for kind,label in(('device','宝箱与装置'),('moving','移动恶笼草'),('rare','稀有敌人')):
            self.assertTrue(p.choices.select_branch(label));self.assertEqual(p.combo.count()-1,sum(r['kind']==kind for r in p.result['rows']));self.assertIsNone(p.combo.currentData())
    def test_every_row_has_player_conditions_and_complete_technical_source(self):
        p=self.panel()
        for row in p.result['rows']:
            self.assertTrue(p.choices.select_value(row['id']));self.app.processEvents();self.assertIn(row['name'],p.player.toPlainText());self.assertIn('实际奖励总量',p.player.toPlainText());self.assertEqual(json.loads(p.technical.toPlainText())['selected_row'],row)
            if row['kind']=='device':self.assertFalse(p.portrait.isVisible())
            elif model.battle.picture_bytes(row['portrait'])is not None:self.assertFalse(p.portrait.pixmap().isNull())
    def test_action_jump_is_explicit_checked_and_emits_only_exact_source_key(self):
        p=self.panel();row=next(r for r in p.result['rows']if r['source_action_keys']);p.choices.select_value(row['id']);sent=[];p.actionSelected.connect(sent.append)
        self.assertFalse(p.follow_action());self.assertEqual(sent,[]);p.source_combo.setCurrentIndex(1);self.assertTrue(p.follow_action());self.assertEqual(sent,[row['source_action_keys'][0]])
        with patch.object(model,'stage_rewards',return_value=None):self.assertFalse(p.follow_action());self.assertIsNone(p.result);self.assertFalse(p.source_button.isEnabled());self.assertEqual(sent,[row['source_action_keys'][0]])
    def test_same_source_refresh_retains_branch_row_source_tab_and_nonzero_reading(self):
        p=self.panel();row=next(r for r in p.result['rows']if r['kind']=='device'and r['candidate_groups']);p.choices.select_value(row['id']);p.source_combo.setCurrentIndex(1)
        for widget in(p.player,p.technical):
            p.tabs.setCurrentWidget(widget);self.app.processEvents();cursor=widget.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor);bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(7,bar.maximum()));before=(cursor.anchor(),cursor.position(),bar.value(),p.choices.branch.currentData(),p.combo.currentData(),p.source_combo.currentData(),p.tabs.currentIndex())
            self.assertTrue(p.refresh_reference());self.app.processEvents();cursor=widget.textCursor();self.assertEqual(before,(cursor.anchor(),cursor.position(),bar.value(),p.choices.branch.currentData(),p.combo.currentData(),p.source_combo.currentData(),p.tabs.currentIndex()))
    def test_actual_public_file_damage_removes_old_quantities_and_links_manual_recovery(self):
        p=self.panel();p.choices.select_value(p.result['rows'][0]['id']);p.source_combo.setCurrentIndex(1);manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for n in(model.MANIFEST,*manifest['files']):
                target=root/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,target)
            file=root/model.PACK/'selected-originals.json';raw=file.read_bytes()
            with patch.object(model,'ROOT',root):
                file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertEqual(p.source_combo.count(),0);self.assertFalse(p.source_button.isEnabled());self.assertNotIn('+10',p.player.toPlainText())
                file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertIsNone(p.combo.currentData());self.assertIsNone(p.source_combo.currentData());self.assertFalse(p.source_button.isEnabled())

if __name__=='__main__':unittest.main()
