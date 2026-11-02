"""Readable original spawn settings and keyboard-to-map navigation."""
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_battle_view import CurrentBattlePanel
from rouge.mechanism_reading import MechanismTextBrowser
from rouge.player_spawn_filters import record_text


class SpawnReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def panel(self):
        p=CurrentBattlePanel('ro6_n_2_3');p.resize(800,600);p.show();p.tabs.setCurrentIndex(2)
        self.qt.processEvents();self.addCleanup(p.close);return p

    def test_real_rows_expose_original_parameters_without_combining_queues(self):
        p=self.panel();self.assertEqual(p.actions.count(),len(p.result['actions']))
        for i,a in enumerate(p.result['actions']):
            item=p.actions.item(i);self.assertEqual(item.data(Qt.ItemDataRole.UserRole),a['key'])
            self.assertTrue(item.text().startswith(model.action_label(a).rsplit(' · ',1)[0]+' · '))
            self.assertIn('本条等待：'+model.number(a['raw'].get('preDelay'))+'秒',item.text())
            if a['raw']['actionType']in('SPAWN','ACTIVATE_PREDEFINED'):
                self.assertIn('配置数量：'+model.number(a['raw'].get('count')),item.text())
                self.assertIn('间隔：'+model.number(a['raw'].get('interval'))+'秒',item.text())
        self.assertIsNone(p.action_key)

    def test_synthetic_flags_are_visible_without_merging_them(self):
        p=self.panel();a=deepcopy(p.result['actions'][0]);a['queue'].update(kind='branch',branch_index=1,phase=1);a['raw'].update(hiddenGroup='fixture-hidden',randomSpawnGroupKey='fixture-random',blockFragment=True,count=0,interval=0,preDelay=0)
        before=deepcopy(a);text=record_text(a,{})
        for value in('配置数量：0','间隔：0秒','本条等待：0秒','条件分支','隐藏候选','随机候选','需等待本组条件'):self.assertIn(value,text)
        self.assertEqual(a,before)

    def test_short_body_and_complete_original_notes_keep_the_same_parameters(self):
        p=self.panel();p.actions.setCurrentRow(0);self.assertIsInstance(p.action_player,MechanismTextBrowser)
        action=next(a for a in p.result['actions']if a['key']==p.action_key);short=p.action_player.toPlainText();full=model.action_text(action)
        self.assertLess(len(short),len(full));self.assertIn('开场后的出怪时刻：待核对。',short)
        self.assertIn('本条配置数量：'+model.number(action['raw'].get('count')),short)
        p.details_toggle.setChecked(True);self.assertEqual(p.action_player.toPlainText(),full)
        p.details_toggle.setChecked(False);self.assertEqual(p.action_player.toPlainText(),short)

    def test_keyboard_activation_opens_exact_selected_action_positions(self):
        p=self.panel();i=next(i for i,a in enumerate(p.result['actions'])if a['raw']['actionType']=='SPAWN')
        p.actions.setCurrentRow(i);p.actions.setFocus();self.qt.processEvents();key=p.action_key
        QTest.keyClick(p.actions,Qt.Key.Key_Return);self.qt.processEvents()
        child=p.action_position_dialog;self.addCleanup(child.close)
        self.assertTrue(child.isVisible());self.assertEqual((child.panel.stage_id,child.panel.action_key),(p.stage_id,key))

    def test_same_source_refresh_keeps_action_reading_and_split_sizes(self):
        p=self.panel();p.actions.setCurrentRow(0);cursor=p.action_player.textCursor();cursor.setPosition(2);cursor.setPosition(8,QTextCursor.MoveMode.KeepAnchor);p.action_player.setTextCursor(cursor);p.action_player.verticalScrollBar().setValue(4)
        before=(p.action_key,cursor.selectedText(),p.action_player.verticalScrollBar().value(),p.action_split.sizes())
        self.assertTrue(p.refresh_reference());self.qt.processEvents()
        self.assertEqual(before,(p.action_key,p.action_player.textCursor().selectedText(),p.action_player.verticalScrollBar().value(),p.action_split.sizes()))

    def test_details_open_source_loss_clears_text_selection_and_position_entry(self):
        p=self.panel();p.actions.setCurrentRow(0);p.details_toggle.setChecked(True)
        with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
        self.assertEqual(p.action_player.toPlainText(),'');self.assertIsNone(p.action_key);self.assertEqual(p.actions.count(),0);self.assertFalse(p.action_position_button.isEnabled())
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.actions.currentItem())

    def test_filters_still_select_separate_main_branch_and_random_ranges(self):
        p=self.panel()
        for kind in('main','branch'):
            p.queue_kind.setCurrentIndex(p.queue_kind.findData(kind));self.assertEqual(p.actions.count(),sum(a['queue']['kind']==kind for a in p.result['actions']))
        p.queue_kind.setCurrentIndex(0);p.action_focus.setCurrentIndex(p.action_focus.findData('random'))
        for i in range(p.actions.count()):self.assertIn('随机候选',p.actions.item(i).text())

    def test_predefined_record_names_use_exact_pinned_object_declaration(self):
        from rouge import current_stage_objects as objects
        p=self.panel();reference=objects.stage_reference(p.stage_id)
        names={r['source_selector']:r['name']for r in reference['entries']}
        self.assertEqual(reference['battle_source_identity'],p.result['source_identity'])
        i=next(i for i,a in enumerate(p.result['actions'])if len(a['predefined_candidates'])==1 and a['predefined_candidates'][0]['source_selector']in names)
        a=p.result['actions'][i];name=names[a['predefined_candidates'][0]['source_selector']]
        self.assertIn(name,p.actions.item(i).text());p.actions.setCurrentRow(i);self.assertIn(name,p.action_player.toPlainText().splitlines()[0])
        duplicate=deepcopy(a);duplicate['predefined_candidates']*=2
        self.assertEqual(record_text(duplicate,names).splitlines()[0],model.action_label(duplicate))

    def test_filter_uses_existing_object_names_without_reloading_source(self):
        from rouge import current_stage_objects as objects
        p=self.panel()
        with patch.object(objects,'from_battle',side_effect=AssertionError('Filter must reuse names')):
            p.action_focus.setCurrentIndex(p.action_focus.findData('predefined'))
            self.assertGreater(p.actions.count(),0)

    def test_object_source_mismatch_removes_old_name_mapping(self):
        from rouge import current_stage_objects as objects
        p=self.panel();fresh=deepcopy(objects.stage_reference(p.stage_id));fresh['battle_source_identity']='synthetic-other-source'
        with patch.object(objects,'from_battle',return_value=fresh):self.assertTrue(p.refresh_reference())
        self.assertEqual(p._action_object_names,{})
        for i,a in enumerate(p.result['actions']):self.assertEqual(p.actions.item(i).text().splitlines()[0],model.action_label(a))

    def test_verified_battle_interface_avoids_duplicate_primary_read(self):
        from rouge import current_stage_objects as objects
        current=model.stage_reference('ro6_n_2_3');expected=objects.stage_reference(current['id'])
        with patch.object(model,'stage_reference',side_effect=AssertionError('Battle entry already validated')):
            self.assertEqual(objects.from_battle(current),expected)


if __name__=='__main__':unittest.main()
