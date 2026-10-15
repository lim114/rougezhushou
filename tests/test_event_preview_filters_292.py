"""Public Qt tests for a manual reference filter, never game execution/state."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.node_catalog_view import NodeCatalogPanel
from rouge import event_planning
from rouge import node_catalog


ROLE=Qt.ItemDataRole.UserRole+1


class EventPreviewFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel=NodeCatalogPanel();self.panel.resize(1050,720);self.panel.show();self.qt.processEvents()

    def tearDown(self):
        self.panel.close();self.panel.deleteLater();self.qt.processEvents()

    def select(self,event_id):
        index=next(i for i,row in enumerate(self.panel.entries) if row['kind']=='event' and row['record']['id']==event_id)
        self.panel.list.setCurrentRow(index);self.qt.processEvents()

    def choose(self,combo,value):
        index=combo.findData(value);self.assertGreaterEqual(index,0);combo.setCurrentIndex(index);self.qt.processEvents()

    def tokens(self):return [self.panel.event_stage.itemData(i,ROLE) for i in range(self.panel.event_stage.count())]

    def test_default_all_keeps_original_duck_option_variant_domain(self):
        self.select('community_group_014')
        self.assertIsNone(self.panel.event_scene_filter.currentData());self.assertIsNone(self.panel.event_choice_filter.currentData())
        self.assertEqual(self.tokens(),[
            ['community_group_014:scene:1','community_group_014:scene:1:choice:0','ro6_t_3'],
            ['community_group_014:scene:1','community_group_014:scene:1:choice:0','ro6_e_t_3'],
            ['community_group_014:scene:2','community_group_014:scene:2:choice:0','ro6_e_t_3']])
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_3')
        self.assertTrue(self.panel.battle_button.isEnabled())

    def test_all_catalog_scenes_and_choices_are_available_as_manual_reference_filters(self):
        events=node_catalog.all_events(include_indirect=True)['rows'];scene_count=choice_count=0
        for event in events:
            with self.subTest(event=event['id']):
                self.select(event['id']);scenes=node_catalog.event_details(event['id'])['rows']
                self.assertEqual([self.panel.event_scene_filter.itemData(i) for i in range(1,self.panel.event_scene_filter.count())],
                    [scene['key'] for scene in scenes])
                self.assertEqual([self.panel.event_choice_filter.itemData(i) for i in range(1,self.panel.event_choice_filter.count())],
                    [choice['key'] for scene in scenes for choice in scene['choices']])
                scene_count+=len(scenes);choice_count+=sum(len(scene['choices']) for scene in scenes)
        self.assertEqual((len(events),scene_count,choice_count),(38,190,233))

    def test_scene_and_option_filters_keep_ordinary_dual_and_emergency_only(self):
        self.select('community_group_014')
        self.choose(self.panel.event_scene_filter,'community_group_014:scene:2')
        self.assertEqual([token[2] for token in self.tokens()],['ro6_e_t_3'])
        self.assertEqual(self.panel.event_stage.currentIndex(),-1);self.assertFalse(self.panel.battle_button.isEnabled())
        self.choose(self.panel.event_choice_filter,'community_group_014:scene:2:choice:0')
        self.choose(self.panel.event_scene_filter,'community_group_014:scene:1')
        self.assertIsNone(self.panel.event_choice_filter.currentData())
        self.assertEqual([token[2] for token in self.tokens()],['ro6_t_3','ro6_e_t_3'])

    def test_exact_choice_filter_works_across_all_scenes_without_scene_inference(self):
        self.select('community_group_015')
        self.choose(self.panel.event_choice_filter,'community_group_015:scene:2:choice:0')
        self.assertIsNone(self.panel.event_scene_filter.currentData())
        self.assertEqual(self.tokens(),[['community_group_015:scene:2','community_group_015:scene:2:choice:0','ro6_e_t_4']])

    def test_nonbattle_choices_and_empty_scene_do_not_fallback_to_event_battles(self):
        self.select('community_group_014')
        self.choose(self.panel.event_choice_filter,'community_group_014:scene:0:choice:2')
        self.assertEqual(self.panel.event_stage.count(),0);self.assertFalse(self.panel.battle_button.isEnabled())
        events=[];self.panel.stageSelected.connect(events.append);self.panel.select_stage();self.assertEqual(events,[])
        self.choose(self.panel.event_scene_filter,'community_group_014:scene:3')
        self.assertEqual(self.panel.event_choice_filter.count(),1)
        self.assertEqual(self.panel.event_stage.count(),0);self.assertFalse(self.panel.battle_button.isEnabled())

    def test_same_title_and_same_original_choice_are_three_distinct_reading_choices(self):
        self.select('community_group_016')
        values=[(self.panel.event_choice_filter.itemText(i),self.panel.event_choice_filter.itemData(i))
                for i in range(self.panel.event_choice_filter.count()) if '休想骗我' in self.panel.event_choice_filter.itemText(i)]
        self.assertEqual({value for _,value in values},{'community_group_016:scene:2:choice:1',
            'community_group_016:scene:5:choice:1','community_group_016:scene:6:choice:1'})
        self.assertEqual(len({label for label,_ in values}),3)
        for _,value in values:
            self.choose(self.panel.event_choice_filter,value);self.panel.refresh();self.qt.processEvents()
            self.assertEqual(self.panel.event_choice_filter.currentData(),value)
            self.assertEqual(self.panel.event_stage.count(),0)

    def test_shared_stage_from_another_option_does_not_restore_the_old_origin(self):
        self.select('community_group_014')
        self.panel.event_stage.setCurrentIndex(1)
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_e_t_3')
        self.choose(self.panel.event_choice_filter,'community_group_014:scene:2:choice:0')
        self.assertEqual(self.tokens(),[['community_group_014:scene:2','community_group_014:scene:2:choice:0','ro6_e_t_3']])
        self.assertEqual(self.panel.event_stage.currentIndex(),-1)
        self.panel.event_stage.setCurrentIndex(0);self.assertTrue(self.panel.battle_button.isEnabled())
        self.panel.refresh();self.qt.processEvents()
        self.assertEqual(self.panel.event_stage.currentData(ROLE),['community_group_014:scene:2','community_group_014:scene:2:choice:0','ro6_e_t_3'])

    def test_black_birth_six_original_aliases_remain_separate_and_open_exact_ids(self):
        self.select('community_group_008')
        self.choose(self.panel.event_scene_filter,'community_group_008:scene:0')
        self.choose(self.panel.event_choice_filter,'community_group_008:scene:0:choice:1')
        ids=['ro6_t_13','ro6_c_5','ro6_t_14','ro6_c_6','ro6_t_15','ro6_c_7']
        self.assertEqual([token[2] for token in self.tokens()],ids)
        events=[];self.panel.stageSelected.connect(events.append)
        for index in range(6):self.panel.event_stage.setCurrentIndex(index);self.panel.select_stage()
        self.assertEqual(events,ids)

    def test_cave_known_pool_then_missing_context_clears_stage_without_selecting_another(self):
        context={'floor':2,'entry_mode':'content','special_region':False}
        self.assertIsNone(self.panel.floor.currentData())
        with patch.object(self.panel,'_event_context',return_value=context):
            self.panel.refresh();self.select('community_group_017')
            self.choose(self.panel.event_choice_filter,'community_group_017:scene:6:choice:0')
            self.assertEqual([token[2] for token in self.tokens()],['ro6_n_3_1','ro6_n_3_2','ro6_n_3_3','ro6_n_3_4','ro6_n_3_5','ro6_n_3_6'])
            self.panel.event_stage.setCurrentIndex(1)
            context['floor']=None;self.panel.refresh();self.qt.processEvents()
            self.assertEqual(self.panel.event_choice_filter.currentData(),'community_group_017:scene:6:choice:0')
            self.assertEqual(self.panel.event_stage.count(),0);self.assertFalse(self.panel.battle_button.isEnabled())
            context['floor']=3;self.panel.refresh();self.qt.processEvents()
            self.assertEqual(self.panel.event_stage.count(),7)
            self.assertEqual(self.panel.event_stage.currentIndex(),-1);self.assertFalse(self.panel.battle_button.isEnabled())

    def test_preview_click_revalidates_latest_context_before_emitting(self):
        context={'floor':2,'entry_mode':'content','special_region':False}
        self.assertIsNone(self.panel.floor.currentData())
        with patch.object(self.panel,'_event_context',return_value=context):
            self.panel.refresh();self.select('community_group_017')
            self.assertTrue(self.panel.battle_button.isEnabled())
            context['special_region']=True;declaration_before=deepcopy(context)
            before=deepcopy(self.panel.runtime_context);events=[];self.panel.stageSelected.connect(events.append)
            self.panel.select_stage()
            self.assertEqual(events,[]);self.assertEqual(self.panel.event_stage.count(),0)
            self.assertFalse(self.panel.battle_button.isEnabled());self.assertEqual(self.panel.runtime_context,before)
            self.assertEqual(context,declaration_before)

    def test_changing_event_resets_both_filters_and_never_borrows_choice_title(self):
        self.select('community_group_014');self.choose(self.panel.event_scene_filter,'community_group_014:scene:2')
        self.choose(self.panel.event_choice_filter,'community_group_014:scene:2:choice:0')
        self.select('community_group_015')
        self.assertIsNone(self.panel.event_scene_filter.currentData());self.assertIsNone(self.panel.event_choice_filter.currentData())
        self.assertTrue(all(token[0].startswith('community_group_015:') for token in self.tokens()))
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_4')

    def test_manual_filters_and_refresh_preserve_reading_tabs_cursor_and_nonzero_scroll(self):
        self.select('community_group_016');self.panel.reading_tabs.setCurrentIndex(1);self.qt.processEvents()
        reader=self.panel.detail;self.assertGreater(reader.verticalScrollBar().maximum(),0)
        cursor=reader.textCursor();cursor.setPosition(5);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor);reader.verticalScrollBar().setValue(max(1,reader.verticalScrollBar().maximum()//2))
        state=(reader.toPlainText(),reader.textCursor().selectedText(),reader.verticalScrollBar().value(),self.panel.reading_tabs.currentIndex())
        self.choose(self.panel.event_scene_filter,'community_group_016:scene:8')
        self.choose(self.panel.event_choice_filter,'community_group_016:scene:8:choice:0')
        self.panel.event_stage.setCurrentIndex(0);self.panel.refresh();self.qt.processEvents()
        self.assertEqual((reader.toPlainText(),reader.textCursor().selectedText(),reader.verticalScrollBar().value(),self.panel.reading_tabs.currentIndex()),state)
        self.assertEqual(self.panel.event_scene_filter.currentData(),'community_group_016:scene:8')
        self.assertEqual(self.panel.event_choice_filter.currentData(),'community_group_016:scene:8:choice:0')
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_e_t_5')

    def test_source_failure_during_click_clears_old_entry_and_never_emits(self):
        self.select('community_group_014');events=[];self.panel.stageSelected.connect(events.append)
        with patch.object(event_planning,'event_battle_links',side_effect=ValueError('公开来源不再相符')):
            self.panel.select_stage()
        self.assertEqual(events,[]);self.assertEqual(self.panel.event_stage.count(),0)
        self.assertFalse(self.panel.battle_button.isEnabled());self.assertIn('未通过核对',self.panel.status.text())

    def test_direct_battle_reference_button_is_independent_of_event_source_failure(self):
        events=[];self.panel.stageSelected.connect(events.append)
        with patch.object(event_planning,'event_battle_links',side_effect=ValueError('事件来源不可用')):
            self.choose(self.panel.kind,'battle')
            self.panel.list.setCurrentRow(1);self.qt.processEvents()
            entry=self.panel.entries[1]
            expected=entry['record'].get('id') or entry['record']['stage_id']
            self.assertTrue(self.panel.battle_button.isEnabled())
            self.panel.battle_button.click()
        self.assertEqual(events,[expected])

    def test_excluded_event_can_still_be_manually_read_as_fixed_battle_reference(self):
        context={'floor':1,'entry_mode':'content','special_region':False}
        self.assertIsNone(self.panel.floor.currentData())
        with patch.object(self.panel,'_event_context',return_value=context):
            self.panel.refresh();self.select('community_group_014')
            entry=next(row for row in self.panel.entries if row['key']==self.panel.list.selected_key())
            self.assertEqual(entry['qualification']['status'],'excluded')
            self.choose(self.panel.event_choice_filter,'community_group_014:scene:2:choice:0')
            self.assertEqual(self.tokens(),[['community_group_014:scene:2','community_group_014:scene:2:choice:0','ro6_e_t_3']])
            self.panel.event_stage.setCurrentIndex(0)
            events=[];self.panel.stageSelected.connect(events.append);self.panel.battle_button.click()
            self.assertEqual(events,['ro6_e_t_3'])
            self.assertEqual(entry['qualification']['status'],'excluded')


if __name__=='__main__':unittest.main()
