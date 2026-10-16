"""Manual entry reading keeps source bounds and reading state separate."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import battle_event_references as events, stage_entry_reference as configuration
from rouge.battle_entry_reference_view import BattleEntryReferencePanel

STAGES=('ro6_t_1','ro6_t_2','ro6_t_3','ro6_t_4','ro6_t_5','ro6_e_t_3','ro6_e_t_4','ro6_e_t_5')

class BattleEntryReferenceView296Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=BattleEntryReferencePanel();self.panel.show();self.qt.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()

    def test_all_eight_exact_versions_default_unselected_and_only_admit_matching_source_rows(self):
        admitted=excluded=0
        for stage in STAGES:
            self.panel.set_stage(stage);packet=events.stage_event_references(stage)
            admitted+=len(packet['rows']);excluded+=len(packet['excluded_rows'])
            self.assertEqual(self.panel.event_choice.count(),len(packet['rows']))
            self.assertEqual(self.panel.event_choice.currentIndex(),-1)
            self.assertFalse(self.panel.open_event_button.isEnabled());self.assertTrue(self.panel.event_bar.isVisible())
            self.assertIn('请选择',self.panel.reference_text.toPlainText())
            ids={self.panel.event_choice.itemData(i) for i in range(self.panel.event_choice.count())}
            self.assertEqual(ids,{r['reference_id'] for r in packet['rows']})
            self.assertTrue(ids.isdisjoint({r['reference_id'] for r in packet['excluded_rows']}))
        self.assertEqual((admitted,excluded),(11,3))

    def test_every_admitted_choice_emits_exact_fresh_token_only_after_manual_click(self):
        selected=[];self.panel.eventReferenceSelected.connect(selected.append)
        for stage in STAGES:
            self.panel.set_stage(stage);packet=events.stage_event_references(stage)
            for row in packet['rows']:
                before=len(selected);self.panel.event_choice.setCurrentIndex(self.panel.event_choice.findData(row['reference_id']))
                self.assertEqual(len(selected),before)
                text=self.panel.reference_text.toPlainText()
                self.assertIn(row['event_title'],text);self.assertIn(row['choice_title'],text)
                self.assertIn('只属于这条事件入口',text);self.assertNotIn('community_group_',text)
                self.panel.open_event_button.click()
                self.assertEqual(selected[-1],row['token']);self.assertEqual(len(selected),before+1)
        self.assertEqual(len(selected),11)

    def test_same_stage_refresh_preserves_choice_tab_nonzero_scroll_and_selection(self):
        self.panel.set_stage('ro6_e_t_3');self.panel.event_choice.setCurrentIndex(0)
        reader=self.panel.source_text;self.panel.reading_tabs.setCurrentWidget(reader);self.qt.processEvents()
        cursor=QTextCursor(reader.document());cursor.setPosition(5);cursor.setPosition(35,QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0)
        bar.setValue(max(1,bar.maximum()//2));self.qt.processEvents()
        def state():
            c=reader.textCursor();return self.panel.event_choice.currentData(),c.anchor(),c.position(),bar.value()
        before=state();self.panel.set_stage('ro6_e_t_3');self.qt.processEvents()
        self.assertEqual(state(),before);self.assertIs(self.panel.reading_tabs.currentWidget(),reader)

    def test_cross_stage_clears_old_choice_and_unsupported_stage_clears_both_pages(self):
        self.panel.set_stage('ro6_t_1');self.panel.event_choice.setCurrentIndex(0)
        self.panel.set_stage('ro6_e_t_5');self.assertIsNone(self.panel.event_choice.currentData())
        self.assertFalse(self.panel.open_event_button.isEnabled())
        self.panel.set_stage('ro6_n_1_1');self.assertEqual(self.panel.event_choice.count(),0)
        for reader in (self.panel.reference_text,self.panel.source_text):
            self.assertIn('已清除',reader.toPlainText());self.assertNotIn('community_group_',reader.toPlainText())

    def test_source_failure_clears_old_event_token_and_recovery_stays_unselected(self):
        self.panel.set_stage('ro6_t_1');self.panel.event_choice.setCurrentIndex(0)
        with patch.object(events,'MANIFEST','research/nonexistent-296.json'):
            self.panel.refresh_reference()
        self.assertEqual(self.panel.event_choice.count(),0);self.assertFalse(self.panel.open_event_button.isEnabled())
        for reader in (self.panel.reference_text,self.panel.source_text):self.assertIn('已清除',reader.toPlainText())
        self.panel.refresh_reference();self.assertIsNone(self.panel.event_choice.currentData())
        self.assertFalse(self.panel.open_event_button.isEnabled())

    def test_tampered_token_does_not_emit_or_fall_back_to_first_source(self):
        selected=[];self.panel.eventReferenceSelected.connect(selected.append)
        self.panel.set_stage('ro6_t_1');self.panel.event_choice.setCurrentIndex(0)
        self.panel.packet['result']['rows'][0]['token']['event_id']='another-event'
        self.panel.open_selected_event();self.assertEqual(selected,[])
        self.assertEqual(self.panel.event_choice.count(),0);self.assertIn('已清除',self.panel.reference_text.toPlainText())

    def test_autopsy_lists_four_source_scopes_and_separates_documented_conditions_from_actuals(self):
        selected=[];self.panel.eventReferenceSelected.connect(selected.append)
        self.panel.set_stage('ro6_t_12');self.assertFalse(self.panel.event_bar.isVisible())
        self.assertEqual(self.panel.event_choice.count(),0);self.assertFalse(self.panel.open_event_button.isEnabled())
        text=self.panel.reference_text.toPlainText()
        for floor in (3,4,5):self.assertIn(f'第{floor}层普通作战',text)
        self.assertIn('假层',text);self.assertIn('不能据此归到第4层或秘境',text)
        self.assertIn('光明之末',text);self.assertIn('怦然信标',text);self.assertIn('湮没“光明”',text)
        self.assertIn('其中的“未持有”条件来自这段资料',text);self.assertIn('不保证每层都有一场',text)
        self.assertNotIn('zone_4_1',text);self.assertNotIn('FEATURE',text);self.assertNotIn('limit',text)
        self.panel.open_selected_event();self.assertEqual(selected,[])

    def test_autopsy_source_failure_cannot_keep_old_configuration_or_related_item_text(self):
        self.panel.set_stage('ro6_t_12');self.assertIn('光明之末',self.panel.reference_text.toPlainText())
        with patch.object(configuration,'MANIFEST','research/nonexistent-autopsy-296.json'):
            self.panel.refresh_reference()
        for reader in (self.panel.reference_text,self.panel.source_text):
            self.assertNotIn('光明之末',reader.toPlainText());self.assertIn('已清除',reader.toPlainText())
        self.panel.refresh_reference();self.assertIn('光明之末',self.panel.reference_text.toPlainText())

if __name__=='__main__':unittest.main()
