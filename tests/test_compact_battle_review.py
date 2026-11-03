"""Four player categories, one refresh and optional detail without losing data."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.current_battle_view import CurrentBattlePanel
from rouge.current_reward_view import CurrentRewardPanel
from rouge import current_battle_reference as battle, current_reward_reference as rewards
from rouge import current_settlement_modes_reference as settlement


class CompactBattleReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def panel(self):
        p=CurrentBattlePanel('ro6_n_2_6');p.resize(780,650);p.show();self.qt.processEvents();self.addCleanup(p.close);return p

    def test_four_main_sections_and_both_reward_categories_keep_original_results(self):
        p=self.panel()
        self.assertEqual([p.tabs.tabText(i)for i in range(p.tabs.count())],['地图与关卡','敌人和机制','出怪与条件','奖励与条件'])
        self.assertEqual([p.rewards.sections.tabText(i)for i in range(2)],['可能获得','通关收入'])
        self.assertIs(p.rewards.sections.widget(1),p.settlement)
        self.assertEqual(p.result,battle.stage_reference(p.stage_id))
        self.assertNotIn('待迁移',p.summary.toPlainText())
        self.assertEqual(p.rewards.result,rewards.stage_rewards(p.stage_id))
        self.assertEqual(p.settlement.result,settlement.stage_reference(p.stage_id,p.settlement.entry.currentData(),p.settlement.region.currentData()))

    def test_embedded_view_has_one_refresh_and_explicit_scope_while_standalone_keeps_its_controls(self):
        p=self.panel();self.assertTrue(p.refresh_button.isVisible())
        self.assertTrue(p.notice.isHidden());self.assertTrue(p.rewards.notice.isHidden());self.assertTrue(p.settlement.notice.isHidden())
        self.assertTrue(p.rewards.refresh_button.isHidden());self.assertTrue(p.settlement.refresh_button.isHidden())
        p.details_toggle.setChecked(True)
        self.assertEqual(p.notice.text(),battle.NOTICE);self.assertEqual(p.rewards.notice.text(),rewards.NOTICE)
        self.assertFalse(p.notice.isHidden());self.assertFalse(p.rewards.notice.isHidden());self.assertFalse(p.settlement.notice.isHidden())
        standalone=CurrentRewardPanel(p.stage_id);standalone.show();self.addCleanup(standalone.close);self.qt.processEvents()
        self.assertIsNone(standalone.sections);self.assertTrue(standalone.refresh_button.isVisible());self.assertTrue(standalone.notice.isVisible())

    def test_one_refresh_updates_all_three_original_models_exactly_once(self):
        p=self.panel()
        with patch.object(battle,'stage_reference',wraps=battle.stage_reference)as a,patch.object(rewards,'stage_rewards',wraps=rewards.stage_rewards)as b,patch.object(settlement,'stage_reference',wraps=settlement.stage_reference)as c:
            p.refresh_button.click()
        self.assertEqual((a.call_count,b.call_count,c.call_count),(1,1,1))

    def test_raw_source_is_optional_and_same_source_refresh_preserves_reading_and_player_page(self):
        p=self.panel();p.tabs.setCurrentWidget(p.rewards);p.rewards.sections.setCurrentWidget(p.settlement)
        p.details_toggle.setChecked(True);p.source_toggle.setChecked(True);self.qt.processEvents()
        self.assertIs(p.reading_stack.currentWidget(),p.technical);self.assertEqual(json.loads(p.technical.toPlainText()),p.result)
        cursor=p.technical.textCursor();cursor.setPosition(4);cursor.setPosition(20,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(cursor)
        p.technical.verticalScrollBar().setValue(30);before=(cursor.anchor(),cursor.position(),p.technical.verticalScrollBar().value())
        self.assertTrue(p.refresh_reference());self.qt.processEvents();cursor=p.technical.textCursor()
        self.assertEqual(before,(cursor.anchor(),cursor.position(),p.technical.verticalScrollBar().value()))
        self.assertTrue(p.source_toggle.isChecked());self.assertTrue(p.details_toggle.isChecked())
        p.source_toggle.setChecked(False);self.assertIs(p.tabs.currentWidget(),p.rewards);self.assertIs(p.rewards.sections.currentWidget(),p.settlement)

    def test_selected_base_entry_and_region_survive_shared_refresh_without_becoming_actual_claim(self):
        p=self.panel();p.tabs.setCurrentWidget(p.rewards);p.rewards.sections.setCurrentWidget(p.settlement)
        p.settlement.entry.setCurrentIndex(1);p.settlement.region.setCurrentIndex(1)
        before=(p.settlement.entry.currentData(),p.settlement.region.currentData(),deepcopy(p.settlement.result))
        self.assertTrue(p.refresh_reference())
        self.assertEqual(before,(p.settlement.entry.currentData(),p.settlement.region.currentData(),p.settlement.result))
        self.assertIs(p.rewards.sections.currentWidget(),p.settlement)

    def test_child_source_failure_only_clears_that_reward_kind(self):
        p=self.panel();base=deepcopy(p.settlement.result);configured=deepcopy(p.result)
        with patch.object(rewards,'stage_rewards',return_value=None):
            self.assertTrue(p.refresh_reference());self.assertIsNone(p.rewards.result)
            self.assertEqual(p.settlement.result,base);self.assertEqual(p.result,configured)
        self.assertTrue(p.refresh_reference());conditional=deepcopy(p.rewards.result)
        with patch.object(settlement,'stage_reference',return_value=None):
            self.assertTrue(p.refresh_reference());self.assertIsNone(p.settlement.result)
            self.assertEqual(p.rewards.result,conditional);self.assertEqual(p.result,configured)

    def test_parent_source_loss_clears_all_data_and_recovers_without_old_selection(self):
        p=self.panel();p.source_toggle.setChecked(True);p.details_toggle.setChecked(True)
        p.rewards.sections.setCurrentWidget(p.settlement)
        with patch.object(battle,'stage_reference',return_value=None):
            self.assertFalse(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.rewards.result);self.assertIsNone(p.settlement.result)
            self.assertEqual(p.technical.toPlainText(),'');self.assertFalse(p.source_toggle.isChecked());self.assertFalse(p.details_toggle.isChecked())
        self.assertTrue(p.refresh_reference());self.assertEqual(p.rewards.sections.currentIndex(),0);self.assertIsNone(p.rewards.combo.currentData())

    def test_exact_action_jump_returns_from_raw_source_to_player_action_page(self):
        p=self.panel();p.source_toggle.setChecked(True);action=p.result['actions'][0]
        self.assertTrue(p.focus_action(action));self.assertEqual(p.action_key,action['key'])
        self.assertFalse(p.source_toggle.isChecked());self.assertIs(p.reading_stack.currentWidget(),p.tabs)
        self.assertEqual(p.tabs.currentIndex(),2);self.assertIn('准确时刻：未知',p.action_player.toPlainText())


if __name__=='__main__':unittest.main()
