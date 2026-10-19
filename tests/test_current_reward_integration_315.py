from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.current_battle_view import CurrentBattlePanel
from rouge.battle_preview import battle_data

class CurrentRewardIntegration315Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def panel(self):
        p=CurrentBattlePanel('ro6_n_2_6');p.resize(1050,720);p.show();self.addCleanup(p.close);self.app.processEvents();return p
    def test_current_preview_reward_tab_links_to_exact_queue_not_old_map_or_game(self):
        old=deepcopy(battle_data());p=self.panel();r=p.rewards;self.assertGreaterEqual(p.tabs.indexOf(r),0);row=next(x for x in r.result['rows']if x['source_action_keys']);r.choices.select_value(row['id']);r.source_combo.setCurrentIndex(1);key=r.source_combo.currentData();self.assertTrue(r.follow_action());self.assertEqual(p.action_key,key);self.assertEqual(p.tabs.currentIndex(),2);action=next(x for x in p.result['actions']if x['key']==key);self.assertIn('准确时刻：未知',p.action_player.toPlainText());self.assertEqual(action['source_selector'],row['source_actions'][0]['source_selector']);self.assertEqual(old,battle_data())
    def test_battle_refresh_preserves_nested_reward_reading_and_bad_battle_clears_it(self):
        p=self.panel();r=p.rewards;r.choices.select_value(r.result['rows'][0]['id']);r.source_combo.setCurrentIndex(1);p.tabs.setCurrentWidget(r);r.tabs.setCurrentIndex(1);before=(p.tabs.currentIndex(),r.tabs.currentIndex(),r.combo.currentData(),r.source_combo.currentData());self.assertTrue(p.refresh_reference());self.assertEqual(before,(p.tabs.currentIndex(),r.tabs.currentIndex(),r.combo.currentData(),r.source_combo.currentData()))
        with patch('rouge.current_battle_reference.packet',return_value=None):self.assertFalse(p.refresh_reference());self.assertIsNone(r.result);self.assertFalse(r.source_button.isEnabled())
    def test_reward_only_failure_does_not_clear_or_recalculate_current_battle(self):
        p=self.panel();before=deepcopy(p.result)
        with patch('rouge.current_reward_reference.packet',return_value=None):self.assertFalse(p.rewards.refresh_reference());self.assertEqual(before,p.result);self.assertIsNone(p.rewards.result)

if __name__=='__main__':unittest.main()
