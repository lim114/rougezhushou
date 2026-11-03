"""Exact original pointers with independent condition / battle preview boundaries."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as catalog,original_destinations as nav
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.original_destinations_view import OriginalDestinationPanel

ROOT=Path(__file__).resolve().parents[1]


class OriginalDestinationTests(unittest.TestCase):
    def test_all_original_fields_match_complete_primary_selected_source(self):
        selected=json.loads((ROOT/'research/p3-original-destinations/selected-original.json').read_text(encoding='utf8'))
        original=catalog._original()
        self.assertEqual(selected['source'],original['source']['game_data'])
        self.assertEqual(len(selected['choices']),396);self.assertEqual(len(selected['choiceScenes']),338)
        for key,row in original['choices'].items():
            self.assertEqual(row,{field:selected['choices'][key][field] for field in row})
            self.assertEqual(selected['choices'][key]['id'],key)
        for key,row in original['scenes'].items():
            self.assertEqual(row,{field:selected['choiceScenes'][key][field] for field in row})
            self.assertEqual(selected['choiceScenes'][key]['id'],key)
        self.assertNotIn('choiceIds',next(iter(selected['choiceScenes'].values())))

    def test_all_306_literal_destinations_and_90_missing_are_preserved(self):
        found=empty=battle_count=0
        for key,choice in catalog._original()['choices'].items():
            result=nav.destination_reference(key)
            self.assertEqual(result['destination_scene_id'],choice['nextSceneId'])
            if choice['nextSceneId']:
                found+=1;self.assertEqual(result['destination_scene'],catalog._original()['scenes'][choice['nextSceneId']])
                battle_count+=any(r['battle_links']['rows'] for r in result['catalog_references'])
            else:
                empty+=1;self.assertIsNone(result['destination_scene']);self.assertEqual(result['catalog_references'],[])
                self.assertEqual(result['status'],'no_explicit_destination')
            self.assertIsNone(result['source_scene_id']);self.assertFalse(result['source_scene_origin_verified'])
            self.assertIsNone(result['reachable_from_entry']);self.assertIsNone(result['generation_probability'])
            self.assertFalse(result['inventory_updated']);self.assertFalse(result['map_node_binding_created'])
        self.assertEqual((found,empty,battle_count),(306,90,11))

    def test_original_pointer_does_not_prove_battle_or_source_chain(self):
        terminal=nav.destination_reference('choice_ro6_bat6_19')
        self.assertEqual(terminal['destination_scene_id'],'scene_ro6_bat6_22')
        self.assertFalse(any(r['battle_links']['rows'] for r in terminal['catalog_references']))
        portal=nav.destination_reference('choice_ro6_portal1a_6')
        self.assertEqual(portal['catalog_references'],[])
        self.assertEqual(portal['destination_scene_id'],'scene_ro6_portal1a_3')
        self.assertIn('只显示原文',nav.destination_text(portal))
        no_pointer=next(k for k,r in catalog._original()['choices'].items() if r['type']=='NEXT_PROB' and not r['nextSceneId'])
        self.assertIsNone(nav.destination_reference(no_pointer)['destination_scene'])
        with self.assertRaises(ValueError):nav.destination_reference('choice_ro6_bat1_not_a_real_id')

    def test_conditions_are_independent_declared_comparisons_not_origin_state(self):
        context={'floor':6,'node_type':'林间空地','entry_mode':'natural','gold':0,'resources':{'hp':1}}
        before=deepcopy(context);r=nav.destination_reference('choice_ro6_bat1_1',context)
        self.assertEqual(context,before)
        self.assertEqual(r['context']['entry_mode'],'content');self.assertIsNone(r['context']['node_type'])
        q=r['catalog_references'][0]['event_qualification'];self.assertEqual(q['status'],'excluded')
        self.assertIsNone(r['actual_server_eligible']);self.assertFalse(r['state_after_transition_known'])
        self.assertTrue(r['catalog_references'][0]['battle_links']['rows'])
        self.assertFalse(r['catalog_references'][0]['original_next_field_proves_battle'])
        self.assertIsNone(r['actual_selected_battle_id'])
        with self.assertRaises(ValueError):nav.destination_reference('choice_ro6_bat1_1',{'floor':True})

    def test_independent_scene_choices_keep_unknown_special_conditions(self):
        # Section291 classifies this exact annotation as a documented selection
        # result. A literal destination still proves neither completion nor movement.
        result=nav.destination_reference('choice_ro6_task1_1')
        choices=[ch for ref in result['catalog_references'] for ch in ref['choice_qualifications']['rows']]
        selected=next(ch for ch in choices if ch['choice_key']=='community_group_019:scene:1:choice:0')
        self.assertEqual(selected['conditional_text'],'若已完成当前层的【“居民”据点】作战则不会移动')
        self.assertIsNone(selected['unparsed_condition_text'])
        movement=selected['movement_result_reference']
        self.assertEqual(movement['status'],'documented_reference')
        self.assertTrue(movement['source_valid'])
        self.assertEqual(movement['annotation_role'],'selection_result')
        self.assertEqual(movement['choice_key'],selected['choice_key'])
        exception=movement['completion_exception_reference']
        self.assertEqual(exception['condition_text'],selected['conditional_text'])
        self.assertTrue(exception['one_way_implication'])
        self.assertFalse(exception['documented_movement_if_condition_matches'])
        self.assertIsNone(exception['condition_matches'])
        self.assertFalse(exception['converse_verified'])
        self.assertFalse(exception['negation_implies_successful_movement_verified'])
        for field in ('actual_current_floor_completion','actual_target_node_id','actual_moved',
                      'actual_battle_triggered','actual_position_after'):
            self.assertIsNone(movement[field])
        self.assertFalse(movement['source_scene_link_verified'])
        self.assertFalse(movement['complete_movement_result_known'])
        self.assertEqual(selected['status'],'unknown');self.assertIsNone(selected['actual_selectable'])
        self.assertIn(selected['conditional_text'],nav.destination_text(result))
        self.assertFalse(result['source_scene_origin_verified'])

    def test_file_and_record_identity_guards_fail_without_guessing_or_mutation(self):
        frozen=deepcopy(nav._data());frozen['runtime_source_sha256']['node-events.json']='0'*64
        with patch.object(nav,'_data',return_value=frozen),self.assertRaises(ValueError):nav.destination_reference('choice_ro6_bat1_1')
        original=deepcopy(catalog._original());original['choices']['choice_ro6_bat1_1']['nextSceneId']='scene_ro6_bat2_1'
        with patch.object(catalog,'_original',return_value=original),self.assertRaises(ValueError):nav.destination_reference('choice_ro6_bat1_1')
        current=deepcopy(catalog._data());event=next(e for e in current['events'] if e['id']=='community_group_012')
        event['scenes'][1]['game_scene_ids']=[]
        with patch.object(catalog,'_data',return_value=current),self.assertRaises(ValueError):nav.destination_reference('choice_ro6_bat1_1')
        self.assertEqual(nav.destination_reference('choice_ro6_bat1_1')['destination_scene_id'],'scene_ro6_bat1_1')

    def test_catalog_candidates_and_same_original_variants_are_not_collapsed(self):
        event=next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id']=='community_group_016')
        rows=nav.event_destination_choices(event['id'])['rows']
        duplicate=[r for r in rows if r['original_choice_id']=='choice_ro6_bat5_4']
        self.assertEqual(len(duplicate),3)
        self.assertEqual(len({r['scene_key'] for r in duplicate}),3)
        self.assertTrue(all(not r['source_origin_scene_binding_verified'] for r in rows))
        first=nav.destination_reference('choice_ro6_bat1_1');first['destination_scene']['title']='改'
        first['catalog_references'][0]['battle_links']['rows'].clear()
        again=nav.destination_reference('choice_ro6_bat1_1')
        self.assertEqual(again['destination_scene']['title'],'思乡心切');self.assertTrue(again['catalog_references'][0]['battle_links']['rows'])
        text=nav.destination_text(again);self.assertNotIn('choice_ro6',text);self.assertNotIn('nextSceneId',text)
        self.assertIn('choice_ro6_bat1_1',nav.destination_text(again,True))


class OriginalDestinationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=NodeCatalogPanel();self.panel.resize(1100,850);self.panel.show();self.qt.processEvents()
    def tearDown(self):
        if self.panel.destination_window:self.panel.destination_window.close()
        self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def select(self,kind,identity):
        index=next(i for i,e in enumerate(self.panel.entries) if e['kind']==kind and
            ((kind=='original' and e['record']['record']['record_id']==identity) or e['record'].get('id')==identity or (kind=='function' and e['record'].get('node_type')==identity)))
        self.panel.list.setCurrentRow(index);self.qt.processEvents()
    def reading(self,widget):
        c=widget.textCursor();c.setPosition(2);c.setPosition(10,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(c)
        widget.verticalScrollBar().setValue(min(20,widget.verticalScrollBar().maximum()))
        return (widget.textCursor().selectedText(),widget.verticalScrollBar().value())

    def test_unmapped_original_destination_real_click_and_irrelevant_controls_hidden(self):
        self.select('original','choice_ro6_portal1a_6')
        self.assertTrue(self.panel.destination_button.isVisible());self.panel.destination_button.click();self.qt.processEvents()
        win=self.panel.destination_window;self.assertTrue(win.isVisible());self.assertFalse(win.isModal())
        self.assertEqual(win.result['destination_scene_id'],'scene_ro6_portal1a_3')
        self.assertIn('不应该贸然踏入',win.detail.toPlainText());self.assertFalse(win.battle_button.isVisible())
        self.select('function','林间空地')
        self.assertFalse(self.panel.destination_button.isVisible());self.assertFalse(self.panel.destination_choice.isVisible())
        self.assertEqual(win.choice_id,'choice_ro6_portal1a_6')

    def test_event_pointer_opens_independent_battle_map_and_keeps_condition_unknown(self):
        self.select('event','community_group_012')
        index=self.panel.destination_choice.findData('choice_ro6_bat1_1');self.assertGreaterEqual(index,0)
        self.panel.destination_choice.setCurrentIndex(index);events=[];self.panel.stageSelected.connect(events.append)
        self.panel.destination_button.click();self.qt.processEvents();win=self.panel.destination_window
        self.assertTrue(win.stage.count());self.assertTrue(win.battle_button.isVisible())
        self.assertIn('资格未确认',win.detail.toPlainText())
        allowed={r['stage_id'] for ref in win.result['catalog_references'] for link in ref['battle_links']['rows'] for r in link['preview_stage_candidates']}
        expected=win.stage.currentData();self.assertIn(expected,allowed)
        win.battle_button.click();self.assertEqual(events,[expected])
        win.set_context({'floor':6});self.assertIn('已列条件不符',win.detail.toPlainText())
        win.battle_button.click();self.assertEqual(events,[expected,expected])

    def test_refresh_retains_choice_dialog_stage_and_reading_with_context_update(self):
        self.select('event','community_group_015')
        chosen='choice_ro6_bat4_2';self.panel.destination_choice.setCurrentIndex(self.panel.destination_choice.findData(chosen))
        self.panel.destination_button.click();self.qt.processEvents();win=self.panel.destination_window
        if win.stage.count()>1:win.stage.setCurrentIndex(1)
        stage=win.stage.currentData(Qt.ItemDataRole.UserRole+1);before=self.reading(win.detail)
        self.panel.refresh();self.qt.processEvents()
        self.assertEqual(self.panel.destination_choice.currentData(),chosen);self.assertEqual(win.choice_id,chosen)
        self.assertEqual(win.stage.currentData(Qt.ItemDataRole.UserRole+1),stage);self.assertEqual(self.reading_state(win.detail),before)
        self.panel.set_map_context(None,runtime_context={'gold':7});self.qt.processEvents()
        self.assertEqual(win.context.get('gold'),7);self.assertEqual(self.panel.destination_choice.currentData(),chosen)
        self.assertEqual(win.stage.currentData(Qt.ItemDataRole.UserRole+1),stage)
        self.assertEqual(self.reading_state(win.detail)[0],before[0])
        win.technical.setChecked(True);self.assertEqual(win.choice_id,chosen);self.assertEqual(win.stage.currentData(Qt.ItemDataRole.UserRole+1),stage)
    @staticmethod
    def reading_state(widget):return (widget.textCursor().selectedText(),widget.verticalScrollBar().value())

    def test_same_original_id_in_separate_community_branches_keeps_exact_picker_row(self):
        self.select('event','community_group_016')
        indexes=[i for i in range(self.panel.destination_choice.count())
            if self.panel.destination_choice.itemData(i)=='choice_ro6_bat5_4']
        self.assertEqual(len(indexes),3)
        selected=indexes[-1];self.panel.destination_choice.setCurrentIndex(selected)
        stable=self.panel.destination_choice.currentData(Qt.ItemDataRole.UserRole+1)
        self.panel.destination_button.click();self.qt.processEvents()
        self.panel.refresh();self.qt.processEvents()
        self.assertEqual(self.panel.destination_choice.currentIndex(),selected)
        self.assertEqual(self.panel.destination_choice.currentData(Qt.ItemDataRole.UserRole+1),stable)
        self.assertEqual(self.panel.destination_window.choice_id,'choice_ro6_bat5_4')

    def test_destination_reference_does_not_bind_future_scene_to_current_map_or_write_state(self):
        graph={'zone_id':'zone_1','template_id':'readonly','nodes':[{'id':'n','row':0,'col':0,
            'observed_type':'林间空地','remembered_type':'不期而遇','content_history':[{'kind':'event','title':'思乡心切'}]}]}
        before=deepcopy(graph);self.panel.set_map_context(graph,{'floor':1},epoch='declared',historical=True)
        self.select('original','choice_ro6_portal1a_6');self.panel.destination_button.click();self.qt.processEvents()
        self.assertEqual(graph,before);self.assertEqual(self.panel.map_location.count(),0)
        self.assertFalse(self.panel.destination_window.result['map_node_binding_created'])
        self.assertIsNone(self.panel.destination_window.result['actual_destination_entered'])


if __name__=='__main__':unittest.main()
