from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,shutil,unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import current_settlement_reference as model
from rouge.current_settlement_view import CurrentSettlementPanel
from rouge.current_battle_view import CurrentBattlePanel
ROOT=Path(__file__).resolve().parents[1]

class CurrentSettlementView318Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def panel(self,sid='ro6_n_1_2'):
        p=CurrentSettlementPanel(sid);p.resize(850,430);p.show();self.addCleanup(p.close);self.qt.processEvents();return p
    def test_default_unknown_and_explicit_gold_no_experience1013(self):
        p=self.panel();self.assertIsNone(p.result['conditional_base_gold']);p.entry.setCurrentIndex(p.entry.findData('map'));self.assertEqual(p.result['conditional_base_gold'],{'minimum':1,'maximum':1});self.assertIn('旧版经验',p.player.toPlainText());self.assertNotIn('1013',p.player.toPlainText());self.assertNotIn('433770',p.player.toPlainText());self.assertNotIn('未闭合',p.player.toPlainText());self.assertEqual(json.loads(p.technical.toPlainText()),p.result)
    def test_same_name_special_vs_pursuit_and_regional_switch_no_stale_numbers(self):
        ref=model.packet();sid=next(sid for sid,r in ref['directory']['data']['rows'].items()if r['name']=='“闹乐”'and r['original_stage']['difficulty']=='NORMAL');p=self.panel(sid)
        for key,expected in [('event',{'minimum':3,'maximum':3}),('pursuit',{'minimum':0,'maximum':0}),('unknown',None)]:p.entry.setCurrentIndex(p.entry.findData(key));self.assertEqual(p.result['conditional_base_gold'],expected)
        p.region.setCurrentIndex(p.region.findData('side_path'));self.assertIsNone(p.result['conditional_base_gold'])
    def test_nonzero_both_readers_preserve_context_tab_scroll_selection_on_refresh(self):
        p=self.panel();p.entry.setCurrentIndex(p.entry.findData('map'));p.region.setCurrentIndex(p.region.findData('portal'));p.resize(850,300)
        for reader in(p.player,p.technical):
            p.tabs.setCurrentWidget(reader);self.qt.processEvents();c=reader.textCursor();c.setPosition(2);c.setPosition(12,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(5,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.entry.currentData(),p.region.currentData(),p.tabs.currentIndex());self.assertTrue(p.refresh_reference());self.qt.processEvents();c=reader.textCursor();self.assertEqual(before,(c.anchor(),c.position(),bar.value(),p.entry.currentData(),p.region.currentData(),p.tabs.currentIndex()))
    def test_actual_source_damage_clears_numeric_and_historical_reference_manual_recheck(self):
        p=self.panel();p.entry.setCurrentIndex(p.entry.findData('map'));manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
        with TemporaryDirectory()as folder:
            root=Path(folder)
            for name in(model.MANIFEST,*manifest['files']):
                dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
            with patch.object(model,'ROOT',root):
                file=root/model.DATA;raw=file.read_bytes();file.write_bytes(raw+b' ');self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertEqual(p.technical.toPlainText(),'');self.assertNotIn('10',p.player.toPlainText());file.write_bytes(raw);self.assertTrue(p.refresh_reference());self.assertEqual(p.result['conditional_base_gold'],{'minimum':1,'maximum':1})
    def test_parent_indices_unchanged_and_parent_loss_clears_base_subpanel(self):
        p=CurrentBattlePanel('ro6_n_1_2');self.addCleanup(p.close);self.assertEqual([p.tabs.tabText(i)for i in range(6)],['地图与关卡','敌人和机制','出怪与条件','完整原值与来源','奖励与条件','通关基础奖励']);p.settlement.entry.setCurrentIndex(p.settlement.entry.findData('map'));p._clear();self.assertIsNone(p.settlement.result);self.assertEqual(p.settlement.technical.toPlainText(),'')
    def test_only_base_source_failure_does_not_claim_other_evidence_failed(self):
        p=CurrentBattlePanel('ro6_n_1_2');self.addCleanup(p.close)
        with patch.object(model,'packet',return_value=None):self.assertTrue(p.refresh_reference());self.assertIsNone(p.settlement.result);self.assertIsNotNone(p.result);self.assertIsNotNone(p.rewards.result);self.assertFalse(p.map_image.pixmap().isNull())

if __name__=='__main__':unittest.main()
