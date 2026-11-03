from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import resting_corner_results as results
from rouge.resting_corner_view import RestingCornerPanel
from rouge.node_catalog_view import NodeCatalogPanel

EVENT='community_group_023'
KEYS=[f'{EVENT}:scene:{scene}:choice:{choice}' for scene,choice in [(1,0),(6,0),(9,1),(11,0)]]


class RestingCornerViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel=RestingCornerPanel();self.panel.resize(900,660)
        self.panel.set_reference(EVENT,scope_key='public:rest');self.panel.show();self.qt.processEvents()

    def tearDown(self):
        self.panel.close();self.panel.deleteLater();self.qt.processEvents()

    def choose(self,control,key):
        index=control.findData(key);self.assertGreaterEqual(index,0)
        control.setCurrentIndex(index);self.qt.processEvents()

    def state(self,reader):
        c=reader.textCursor()
        return c.anchor(),c.position(),reader.verticalScrollBar().value()

    def select_reading(self,reader):
        self.qt.processEvents();bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0)
        cursor=QTextCursor(reader.document());cursor.setPosition(4)
        cursor.setPosition(25,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
        bar.setValue(max(1,bar.maximum()//2));self.qt.processEvents()
        self.assertGreater(bar.value(),0);return self.state(reader)

    def test_default_lists_four_distinct_choices_without_selecting_one(self):
        self.assertEqual([self.panel.choice.itemData(i) for i in range(self.panel.choice.count())],KEYS)
        self.assertEqual(self.panel.choice.currentIndex(),-1);self.assertEqual(self.panel.branch.count(),0)
        self.assertFalse(self.panel.open_scene_button.isEnabled())
        self.assertIn('尚未认定本局',self.panel.result_text.toPlainText())

    def test_four_exact_cards_keep_counts_conflicts_and_future_quantity_layer(self):
        counts=[]
        for key in KEYS:
            self.choose(self.panel.choice,key);counts.append(self.panel.branch.count())
            text=self.panel.result_text.toPlainText()
            self.assertIn('后续按钮',text);self.assertIn('不能把各项相加',text)
            self.assertIn('是否领取',text);self.assertNotIn('community_group',text)
            self.assertNotIn('destination_mismatch',text);self.assertNotIn('https://',text)
            self.assertIsNone(self.panel.branch.currentData())
            if key in KEYS[2:]:self.assertIn('资料数量对不上',text)
            else:self.assertNotIn('资料数量对不上',text)
        self.assertEqual(counts,[3,2,1,3])

    def test_all_nine_source_branches_open_exact_six_local_scenes(self):
        expected_targets=[[2,4,5],[7,3],[10],[7,3,10]];seen=[]
        for key,targets in zip(KEYS,expected_targets):
            self.choose(self.panel.choice,key)
            branches=[self.panel.branch.itemData(i) for i in range(self.panel.branch.count())]
            for branch,target in zip(branches,targets):
                self.choose(self.panel.branch,branch);self.panel.open_scene_button.click();self.qt.processEvents()
                self.assertEqual(self.panel._scene_identity[-1],f'{EVENT}:scene:{target}')
                self.assertEqual(self.panel.reading_tabs.currentWidget(),self.panel.scene_text)
                self.assertIn(f'后续场景{target+1}',self.panel.scene_text.toPlainText())
                self.assertIn('不表示已进入游戏',self.panel.scene_text.toPlainText());seen.append(target)
        self.assertEqual(len(seen),9);self.assertEqual(set(seen),{2,3,4,5,7,10})

    def test_ninety_nine_gold_remains_future_text_with_unmatched_original_entry(self):
        self.choose(self.panel.choice,KEYS[2])
        text=self.panel.result_text.toPlainText()
        self.assertIn('99源石锭',text);self.assertIn('尚未与原游戏入口对应',text)
        self.assertIn('当前能否进入或领取未知',text)
        card=next(row for row in self.panel.packet['cards'] if row['choice_key']==KEYS[2])
        button=card['branches'][0]['future_buttons'][0]
        self.assertEqual(button['game_choice_ids'],[])
        self.assertEqual(button['game_match_basis'],'destination_mismatch')

    def test_same_scope_refresh_keeps_exact_selection_tab_cursor_and_nonzero_scroll(self):
        self.choose(self.panel.choice,KEYS[3]);branch=self.panel.branch.itemData(2)
        self.choose(self.panel.branch,branch);self.panel.open_scene_button.click()
        self.panel.reading_tabs.setCurrentWidget(self.panel.source_text)
        reading=self.select_reading(self.panel.source_text);identity=deepcopy(self.panel._scene_identity)
        scene_before=self.panel.scene_text.toPlainText()
        self.panel.set_reference(EVENT,scope_key='public:rest');self.qt.processEvents()
        self.assertEqual(self.panel.choice.currentData(),KEYS[3]);self.assertEqual(self.panel.branch.currentData(),branch)
        self.assertEqual(self.panel._scene_identity,identity);self.assertEqual(self.panel.scene_text.toPlainText(),scene_before)
        self.assertEqual(self.panel.reading_tabs.currentWidget(),self.panel.source_text)
        self.assertEqual(self.state(self.panel.source_text),reading)

    def test_same_title_choice_switch_clears_old_branch_and_scene(self):
        self.choose(self.panel.choice,KEYS[1]);self.panel.branch.setCurrentIndex(0)
        self.panel.open_scene_button.click();self.choose(self.panel.choice,KEYS[3])
        self.assertIsNone(self.panel.branch.currentData());self.assertFalse(self.panel.open_scene_button.isEnabled())
        self.assertIsNone(self.panel._scene_identity);self.assertIn('尚未手动打开',self.panel.scene_text.toPlainText())
        self.assertEqual(self.panel.branch.count(),3)

    def test_explicit_reopen_without_a_supported_choice_clears_old_card_but_refresh_keeps_it(self):
        self.choose(self.panel.choice,KEYS[1]);self.panel.branch.setCurrentIndex(0)
        branch=self.panel.branch.currentData()
        self.panel.set_reference(EVENT,scope_key='public:rest')
        self.assertEqual(self.panel.choice.currentData(),KEYS[1]);self.assertEqual(self.panel.branch.currentData(),branch)
        self.panel.set_reference(EVENT,None,scope_key='public:rest')
        self.assertIsNone(self.panel.choice.currentData());self.assertIsNone(self.panel.branch.currentData())
        self.panel.set_reference(EVENT,KEYS[2],scope_key='public:rest')
        self.assertEqual(self.panel.choice.currentData(),KEYS[2])
        self.panel.set_reference(EVENT,EVENT+':scene:0:choice:0',scope_key='public:rest')
        self.assertIsNone(self.panel.choice.currentData());self.assertFalse(self.panel.open_scene_button.isEnabled())

    def test_scope_change_and_non_target_clear_all_old_reference_pages(self):
        self.choose(self.panel.choice,KEYS[2]);self.panel.branch.setCurrentIndex(0);self.panel.open_scene_button.click()
        self.panel.set_reference(EVENT,scope_key='another:node')
        self.assertIsNone(self.panel.choice.currentData());self.assertIsNone(self.panel.branch.currentData())
        self.assertFalse(self.panel.open_scene_button.isEnabled())
        self.panel.set_reference('community_group_014',scope_key='duck')
        self.assertEqual(self.panel.choice.count(),0);self.assertIsNone(self.panel._scene_identity)
        for reader in (self.panel.result_text,self.panel.scene_text,self.panel.source_text):
            self.assertIn('当前未查阅安眠一隅',reader.toPlainText());self.assertNotIn('99源石锭',reader.toPlainText())

    def test_source_failure_clears_every_page_and_recovery_does_not_reselect(self):
        self.choose(self.panel.choice,KEYS[2]);self.panel.branch.setCurrentIndex(0);self.panel.open_scene_button.click()
        with patch.object(results,'resting_result_cards',side_effect=OSError('isolated failure')):
            self.panel.refresh_reference()
        for reader in (self.panel.result_text,self.panel.scene_text,self.panel.source_text):
            self.assertIn('旧选择已清除',reader.toPlainText());self.assertNotIn('99源石锭',reader.toPlainText())
        self.assertEqual(self.panel.choice.count(),0);self.assertFalse(self.panel.open_scene_button.isEnabled())
        self.panel.refresh_reference()
        self.assertEqual(self.panel.choice.count(),4);self.assertIsNone(self.panel.choice.currentData())
        self.assertIsNone(self.panel.branch.currentData());self.assertIsNone(self.panel._scene_identity)

    def test_tampered_branch_key_is_rejected_before_old_scene_can_be_opened(self):
        self.choose(self.panel.choice,KEYS[0]);self.panel.branch.setCurrentIndex(0)
        self.panel.branch.blockSignals(True)
        self.panel.branch.setItemData(0,KEYS[3]+':sub:0');self.panel.branch.blockSignals(False)
        self.panel.open_selected_scene();self.qt.processEvents()
        self.assertIsNone(self.panel._scene_identity);self.assertFalse(self.panel.open_scene_button.isEnabled())
        self.assertIn('旧内容已清除',self.panel.scene_text.toPlainText())

    def test_parent_opens_only_exact_event_and_preserves_main_reading_and_filters(self):
        parent=NodeCatalogPanel();parent.resize(1050,720);parent.show();self.qt.processEvents()
        try:
            index=next(i for i,row in enumerate(parent.entries) if row['kind']=='event' and row['record']['id']==EVENT)
            parent.list.setCurrentRow(index);self.qt.processEvents()
            self.assertTrue(parent.resting_button.isVisible())
            self.choose(parent.event_choice_filter,KEYS[2])
            parent.reading_tabs.setCurrentWidget(parent.detail);reading=self.select_reading(parent.detail)
            selected=parent.list.selected_key();context=deepcopy((parent.map_context,parent.node_context,parent.dossier,parent.runtime_context))
            parent.resting_button.click();self.qt.processEvents();window=parent.resting_window
            self.assertIsNotNone(window);self.assertFalse(window.isModal());self.assertTrue(window.isVisible())
            self.assertEqual(window.choice.currentData(),KEYS[2]);window.branch.setCurrentIndex(0);window.open_scene_button.click()
            parent.refresh();self.qt.processEvents()
            self.assertEqual(parent.list.selected_key(),selected);self.assertEqual(parent.event_choice_filter.currentData(),KEYS[2])
            self.assertEqual(parent.reading_tabs.currentWidget(),parent.detail);self.assertEqual(self.state(parent.detail),reading)
            self.assertEqual((parent.map_context,parent.node_context,parent.dossier,parent.runtime_context),context)
            self.assertEqual(window._scene_identity[-1],EVENT+':scene:10')
            other=next(i for i,row in enumerate(parent.entries) if row['kind']=='event' and row['record']['id']=='community_group_014')
            parent.list.setCurrentRow(other);self.qt.processEvents()
            self.assertFalse(parent.resting_button.isVisible());self.assertEqual(window.choice.count(),0)
            for reader in (window.result_text,window.scene_text,window.source_text):self.assertNotIn('99源石锭',reader.toPlainText())
        finally:
            if parent.resting_window:parent.resting_window.close()
            parent.close();parent.deleteLater();self.qt.processEvents()


if __name__=='__main__':unittest.main()
