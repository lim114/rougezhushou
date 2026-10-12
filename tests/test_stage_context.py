import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication,QComboBox
from rouge import node_catalog
from rouge.battle_preview import battle_data
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.stage_context import context_data,stage_context,stage_context_text
from rouge.view_catalog import stage_groups,add_groups,view_catalog
from scripts.build_stage_context_reference import build

ROOT=Path(__file__).resolve().parents[1]


class StageEntryContextTests(unittest.TestCase):
    def test_fixed_identity_membership_and_original_unknown_floor_are_preserved(self):
        data=context_data();self.assertEqual(len(data['stages']),21)
        self.assertEqual(sum(bool(s['conditions']) for s in data['stages'].values()),6)
        self.assertEqual(sum(not s['conditions'] for s in data['stages'].values()),15)
        expected={sid for sid,row in view_catalog()['stages'].items() if row['group']=='unconfirmed'}
        self.assertEqual(set(data['stages']),expected)
        for sid,row in data['stages'].items():
            self.assertEqual(row['name'],battle_data()['stages'][sid]['name'])
            self.assertIsNone(row['original_floor_metadata']['floor'])
            self.assertTrue(row['source_references']);self.assertTrue(row['settlement_context_references'])

    def test_shop_exact_ids_split_on_main_four_and_keep_real_entry_prerequisites_unknown(self):
        for floor in range(1,7):
            result=node_catalog.battle_candidates('诡意行商',floor=floor,context='content')
            wanted='ro6_t_6' if floor<4 else 'ro6_t_7'
            self.assertEqual([row['id'] for row in result['rows']],[wanted])
            self.assertEqual(len(result['excluded']),1)
            self.assertEqual(result['rows'][0]['entry_context_reference']['status'],'matched')
            self.assertEqual(result['excluded'][0]['entry_context_reference']['status'],'excluded')
            reference=result['rows'][0]['entry_context_reference']
            self.assertFalse(reference['actual_entry_verified']);self.assertIsNone(reference['server_eligibility'])
            self.assertIn('最高投资额50',reference['entry_reference'])

    def test_unknown_or_special_floor_does_not_exclude_shop_stage(self):
        for kwargs in ({},{'floor':None},{'floor':2,'special_region':True}):
            result=node_catalog.battle_candidates('诡意行商',context='content',**kwargs)
            self.assertEqual({row['id'] for row in result['rows']},{'ro6_t_6','ro6_t_7'})
            self.assertFalse(result['excluded'])
            self.assertTrue(all(row['entry_context_reference']['status']=='unknown' for row in result['rows']))

    def test_natural_stronghold_and_duel_gates_never_apply_to_forced_content(self):
        for node_type,ids,floor in [('“居民”据点',{'ro6_t_10','ro6_t_11'},1),('狭路相逢',{'ro6_duel_1','ro6_duel_2'},2)]:
            natural=node_catalog.battle_candidates(node_type,floor=floor,difficulty=0,context='all',entry_mode='natural')
            self.assertFalse(natural['rows']);self.assertEqual({r['id'] for r in natural['excluded']},ids)
            forced=node_catalog.battle_candidates(node_type,floor=floor,difficulty=0,context='all',entry_mode='content')
            self.assertEqual({r['id'] for r in forced['rows']},ids);self.assertFalse(forced['excluded'])
            self.assertTrue(all(r['entry_context_reference']['status']=='unknown' for r in forced['rows']))
        result=node_catalog.battle_candidates('“居民”据点',floor=2,difficulty=4)
        self.assertTrue(all(r['entry_context_reference']['status']=='matched' for r in result['rows']))
        result=node_catalog.battle_candidates('“居民”据点',floor=2)
        self.assertTrue(all(r['entry_context_reference']['status']=='unknown' for r in result['rows']))

    def test_clones_unproven_entries_and_directory_do_not_inherit_floor_ranges(self):
        for sid in ('ro6_t_8','ro6_t_8_b','ro6_t_8_c','ro6_t_9','ro6_t_9_b','ro6_t_9_c'):
            row=stage_context(sid,node_type='“居民”据点',floor=1,difficulty=0,entry_mode='natural')
            self.assertEqual(row['group'],'roaming_resident');self.assertEqual(row['status'],'unknown');self.assertFalse(row['checks'])
        result=node_catalog.battle_candidates(floor=1)
        self.assertEqual(len(result['rows']),105);self.assertFalse(result['excluded'])
        for row in context_data()['stages'].values():
            reference=stage_context(row['stage_id'],floor=1,entry_mode='natural')
            self.assertEqual(reference['status'],'unknown')
        self.assertIsNone(stage_context('ro6_t_7_clone',floor=4))

    def test_original_source_body_license_and_rebuild_are_exact(self):
        data=context_data();receipt=data['source'];path=ROOT/receipt['community_file']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),receipt['community_sha256'])
        self.assertEqual(path.stat().st_size,receipt['community_bytes'])
        self.assertEqual(receipt['community_revision'],433770)
        self.assertEqual(receipt['license']['community_text'],'CC BY-NC-SA 4.0')
        self.assertEqual(build(),data)
        self.assertIn('秘境口径未证',stage_context_text(stage_context('ro6_t_7',node_type='诡意行商',floor=4)))

    def test_input_boundaries_and_deep_copies(self):
        original=copy.deepcopy(context_data())
        row=stage_context('ro6_t_10',node_type='“居民”据点',floor=2,difficulty=4,entry_mode='natural')
        row['checks'][0]['allowed'].clear();row['source']['rules'].clear()
        self.assertEqual(context_data(),original)
        for kwargs in ({'floor':True},{'floor':7},{'difficulty':True},{'difficulty':16},{'special_region':1},{'entry_mode':'guessed'}):
            with self.assertRaises(ValueError):stage_context('ro6_t_6',**kwargs)


class StageEntryContextViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):self.panel=NodeCatalogPanel();self.panel.resize(1000,700);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()

    def test_fixed_dropdown_keeps_all_exact_ids_and_separates_21_entry_contexts(self):
        combo=QComboBox();groups=stage_groups(battle_data()['stages']);add_groups(combo,groups,'尚未选择')
        ids=[combo.itemData(i) for i in range(combo.count()) if combo.itemData(i)]
        self.assertEqual(set(ids),set(battle_data()['stages']));self.assertEqual(len(ids),105)
        headings=[label for label,_ in groups]
        self.assertIn('诡意行商 · 坎诺特挑战（入口层条件有引用）',headings)
        self.assertIn('流窜“居民”占领战斗（层数未知）',headings)
        self.assertIn('自然“居民”据点（入口层条件有引用）',headings)
        combo.setCurrentIndex(combo.findData('ro6_t_8_c'));self.assertEqual(combo.currentData(),'ro6_t_8_c')

    def test_uncovered_classification_is_preserved_in_original_unknown_group(self):
        data=copy.deepcopy(context_data());data['stages'].pop('ro6_t_8_c')
        with patch('rouge.view_catalog.context_data',return_value=data):groups=stage_groups(battle_data()['stages'])
        identities=[sid for _,items in groups for _,sid,_ in items]
        self.assertEqual(len(identities),105);self.assertEqual(set(identities),set(battle_data()['stages']))
        fallback=next(items for heading,items in groups if heading=='事件/特殊（层数未确认）')
        self.assertEqual([sid for _,sid,_ in fallback],['ro6_t_8_c'])

    def test_shop_matched_and_excluded_references_are_visible_and_preview_exact_stage(self):
        self.panel.kind.setCurrentIndex(self.panel.kind.findData('battle'))
        self.panel.node_type.setCurrentIndex(self.panel.node_type.findData('诡意行商'))
        self.panel.floor.setCurrentIndex(self.panel.floor.findData(2));self.app.processEvents()
        self.assertEqual({e['record']['id'] for e in self.panel.entries},{'ro6_t_6','ro6_t_7'})
        emitted=[];self.panel.stageSelected.connect(emitted.append)
        for sid,status in [('ro6_t_6','已列条件相符'),('ro6_t_7','已列条件不符')]:
            index=next(i for i,e in enumerate(self.panel.entries) if e['record']['id']==sid)
            self.panel.list.setCurrentRow(index);self.app.processEvents()
            text=self.panel.detail.toPlainText();self.assertIn(status,text);self.assertIn(sid,text)
            self.assertIn('最高投资额50',text);self.assertIn('秘境口径未证',text)
            self.panel.select_stage();self.assertEqual(emitted[-1],sid)
        self.assertTrue(any(e['group'].startswith('已列条件排除') for e in self.panel.entries))

    def test_unknown_floor_and_refresh_preserve_selection_text_scroll_and_groups(self):
        self.panel.kind.setCurrentIndex(self.panel.kind.findData('battle'))
        self.panel.node_type.setCurrentIndex(self.panel.node_type.findData('诡意行商'))
        self.panel.floor.setCurrentIndex(self.panel.floor.findData(None));self.app.processEvents()
        self.assertFalse(any(e['record'].get('entry_condition_excluded_reference') for e in self.panel.entries))
        self.panel.list.setCurrentRow(1);self.app.processEvents()
        cursor=self.panel.detail.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor);self.panel.detail.verticalScrollBar().setValue(31)
        key=self.panel.detail_key;text=cursor.selectedText();scroll=self.panel.detail.verticalScrollBar().value()
        groups=self.panel.list.expanded_groups();self.panel.refresh();self.app.processEvents()
        self.assertEqual(self.panel.detail_key,key);self.assertEqual(self.panel.detail.textCursor().selectedText(),text)
        self.assertEqual(self.panel.detail.verticalScrollBar().value(),scroll);self.assertEqual(self.panel.list.expanded_groups(),groups)
        self.assertIn('资格未确认',self.panel.detail.toPlainText())


if __name__=='__main__':unittest.main()
