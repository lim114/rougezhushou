"""Entry navigation selects source text and leaves battle calculations untouched."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication,QTabWidget
from rouge import app as app_module, battle_event_references as events
from rouge.battle_view import BattlePreviewPanel
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.player_node_information import node_information_text
from rouge import node_catalog as catalog

STAGES=('ro6_t_1','ro6_t_2','ro6_t_3','ro6_t_4','ro6_t_5','ro6_e_t_3','ro6_e_t_4','ro6_e_t_5')

def reading(widget):
    c=widget.textCursor();return widget.toPlainText(),c.anchor(),c.position(),widget.verticalScrollBar().value()

class BattleEntryIntegration296Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.tabs=QTabWidget();self.battle=BattlePreviewPanel();self.node=NodeCatalogPanel()
        self.tabs.addTab(self.battle,'战斗');self.tabs.addTab(self.node,'节点');self.tabs.resize(1050,720)
        self.holder=SimpleNamespace(battle_preview=self.battle,node_catalog=self.node,centralWidget=lambda:self.tabs)
        self.battle.entryEventSelected.connect(lambda token:app_module.MainWindow.show_battle_event_reference(self.holder,token))
        self.tabs.show();self.qt.processEvents()
    def tearDown(self):
        if self.battle.entry_reference_window:self.battle.entry_reference_window.close()
        self.tabs.close();self.tabs.deleteLater();self.qt.processEvents()

    def state(self):
        row=self.battle.spawn_list.currentItem()
        return deepcopy((self.battle.current_stage,self.battle.stage_combo.currentData(),self.battle.wave_combo.currentData(),
            self.battle.enemy_combo.currentData(),self.battle.enemy_choices.branch.currentData(),
            row.data(Qt.ItemDataRole.UserRole)['id'] if row else None,
            self.battle.occurrence.value(),self.battle._tile_cell,self.battle._branch_marker,
            self.battle.grid.selected,self.battle.grid.reference_cell,self.battle.original.selected,
            self.battle.context,reading(self.battle.spawn_detail),reading(self.battle.enemy_detail)))

    def test_all_eleven_real_entry_buttons_open_exact_scene_choice_without_resetting_battle(self):
        count=0
        for stage in STAGES:
            self.battle.set_stage(stage);self.tabs.setCurrentWidget(self.battle);self.qt.processEvents()
            before=self.state();self.assertTrue(self.battle.entry_reference_button.isVisible())
            self.battle.entry_reference_button.click();self.qt.processEvents();dialog=self.battle.entry_reference_window
            self.assertIsNone(dialog.event_choice.currentData());self.assertIs(self.tabs.currentWidget(),self.battle)
            for row in events.stage_event_references(stage)['rows']:
                self.tabs.setCurrentWidget(self.battle);self.battle.open_entry_references()
                dialog.event_choice.setCurrentIndex(dialog.event_choice.findData(row['reference_id']))
                dialog.open_event_button.click();self.qt.processEvents()
                self.assertIs(self.tabs.currentWidget(),self.node)
                selected=next(r for r in self.node.entries if r['key']==self.node.list.selected_key())
                self.assertEqual(selected['record']['id'],row['event_id'])
                self.assertEqual(self.node.event_scene_filter.currentData(),row['scene_key'])
                self.assertEqual(self.node.event_choice_filter.currentData(),row['choice_key'])
                from rouge.player_node_information import _plain
                reader=self.node.player_detail;cursor=reader.textCursor();document=reader.document()
                self.assertIs(self.node.reading_tabs.currentWidget(),reader)
                self.assertEqual(cursor.selectedText(),f'选项 {row["choice_number"]}：{_plain(row["choice_title"])}')
                scene=document.find(f'【场景 {row["scene_number"]}】')
                next_scene=document.find(f'【场景 {row["scene_number"]+1}】',scene)
                self.assertFalse(scene.isNull());self.assertGreater(cursor.selectionStart(),scene.selectionEnd())
                if not next_scene.isNull():self.assertLessEqual(cursor.selectionEnd(),next_scene.selectionStart())
                rect=reader.cursorRect();self.assertGreaterEqual(rect.top(),0)
                self.assertLessEqual(rect.bottom(),reader.viewport().height())
                self.assertEqual(self.state(),before);self.assertFalse(dialog.isVisible());count+=1
        self.assertEqual(count,11)

    def test_wrong_stage_or_forged_token_cannot_change_node_or_tab(self):
        self.battle.set_stage('ro6_t_1');token=events.stage_event_references('ro6_t_1')['rows'][0]['token']
        key=self.node.list.selected_key();self.battle.set_stage('ro6_t_2')
        self.assertFalse(app_module.MainWindow.show_battle_event_reference(self.holder,token))
        self.assertEqual(self.node.list.selected_key(),key);self.assertIs(self.tabs.currentWidget(),self.battle)
        self.battle.set_stage('ro6_t_1');bad=deepcopy(token);bad['event_id']='wrong'
        self.assertFalse(self.node.open_battle_event_reference('ro6_t_1',bad));self.assertEqual(self.node.list.selected_key(),key)

    def test_same_stage_refresh_keeps_dialog_and_parent_reading(self):
        self.battle.set_stage('ro6_e_t_3');self.battle.open_entry_references();dialog=self.battle.entry_reference_window
        dialog.event_choice.setCurrentIndex(0);dialog.reading_tabs.setCurrentWidget(dialog.source_text)
        self.qt.processEvents();reader=dialog.source_text;bar=reader.verticalScrollBar()
        self.assertGreater(bar.maximum(),0);c=QTextCursor(reader.document());c.setPosition(4)
        c.setPosition(32,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);bar.setValue(max(1,bar.maximum()//2))
        self.qt.processEvents();before=(dialog.event_choice.currentData(),reading(reader));battle=self.state()
        self.battle.render_rows();self.qt.processEvents()
        self.assertEqual((dialog.event_choice.currentData(),reading(reader)),before);self.assertEqual(self.state(),battle)
        self.assertIs(dialog.reading_tabs.currentWidget(),reader)

    def test_source_failure_clears_child_and_disables_main_button_without_changing_battle(self):
        self.battle.set_stage('ro6_t_1');self.battle.open_entry_references();dialog=self.battle.entry_reference_window
        dialog.event_choice.setCurrentIndex(0);before=self.state()
        with patch.object(events,'MANIFEST','research/missing-battle-reference-296.json'):
            self.battle.render_rows();self.qt.processEvents()
            self.assertFalse(self.battle.entry_reference_button.isEnabled());self.assertEqual(dialog.event_choice.count(),0)
            self.assertIn('已清除',dialog.reference_text.toPlainText());self.assertEqual(self.state(),before)
        self.battle.render_rows();self.assertTrue(self.battle.entry_reference_button.isEnabled())
        self.assertIsNone(dialog.event_choice.currentData());self.assertFalse(dialog.open_event_button.isEnabled())

    def test_changed_stage_clears_child_and_unrelated_stage_hides_entry_button(self):
        self.battle.set_stage('ro6_t_1');self.battle.open_entry_references();dialog=self.battle.entry_reference_window
        dialog.event_choice.setCurrentIndex(0);self.battle.set_stage('ro6_t_12')
        self.assertEqual(dialog.stage_id,'ro6_t_12');self.assertEqual(dialog.event_choice.count(),0)
        self.assertFalse(dialog.event_bar.isVisible());self.assertIn('光明之末',dialog.reference_text.toPlainText())
        self.battle.set_stage('ro6_n_1_1');self.assertFalse(self.battle.entry_reference_button.isVisible())
        self.assertIn('已清除',dialog.reference_text.toPlainText())

    def test_autopsy_player_summary_has_separate_entry_and_reward_sections_without_reclassifying(self):
        records=catalog.battle_candidates(context='all')['rows']
        record=next(r for r in records if (r.get('id') or r.get('stage_id'))=='ro6_t_12')
        before=deepcopy(record);text=node_information_text({'kind':'battle','record':record})
        self.assertIn('第3、4、5层',text);self.assertIn('假层',text);self.assertIn('全部进入方式仍未确认',text)
        self.assertLess(text.index('【资料记录的关联入口】'),text.index('【战后基础奖励】'))
        self.assertEqual(record,before);self.assertFalse(record.get('floors'))

if __name__=='__main__':unittest.main()
