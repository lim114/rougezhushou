import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.base_settlement_planning import _data
from rouge.catalog import catalog
from rouge.battle_preview import battle_data
from rouge.stage_floor_reference import sixth_floor_reference,floor_reference_text
from rouge.view_catalog import stage_groups,view_catalog
from rouge.node_catalog import battle_candidates
from rouge.battle_view import BattlePreviewPanel
from rouge.node_catalog_view import NodeCatalogPanel

IDS={'ro6_n_6_1','ro6_n_6_2','ro6_e_6_1','ro6_e_6_2','ro6_b_6'}


class SixthFloorBrowsingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_named_area_identity_covers_only_exact_five_preserving_original_zero(self):
        matched={sid for sid in battle_data()['stages'] if sixth_floor_reference(sid)}
        self.assertEqual(matched,IDS)
        for sid in matched:
            r=sixth_floor_reference(sid)
            self.assertEqual(r['floor'],6);self.assertEqual(view_catalog()['stages'][sid]['floor'],0)
            self.assertIsNone(r['documented_floors']);self.assertFalse(r['map_connections_known'])
            self.assertIsNone(r['actual_server_eligibility']);self.assertIsNone(r['actual_occurrence'])

    def test_changed_reference_source_and_identity_do_not_borrow_sixth_floor(self):
        for change in ('source_floor','zone','heading','name'):
            data=copy.deepcopy(_data());r=data['stages']['ro6_n_6_1']
            if change=='source_floor':r['settlement_source_floors']=[5]
            elif change=='zone':r['floor_zero_binding']['original_zone_id']='zone_5'
            elif change=='heading':r['floor_zero_binding']['document_heading']='0 某区域 (V)'
            else:r['original']['name']='同编号不同内容'
            with patch('rouge.stage_floor_reference._data',return_value=data):
                self.assertIsNone(sixth_floor_reference('ro6_n_6_1'))
        stage=copy.deepcopy(battle_data()['stages']['ro6_n_6_1']);stage['difficulty']='FOUR_STAR'
        self.assertIsNone(sixth_floor_reference('ro6_n_6_1',stage))
        self.assertIsNone(sixth_floor_reference('invented_6_1'))

    def test_group_has_exact_five_and_every_variant_once_without_source_mutation(self):
        before=copy.deepcopy(view_catalog());groups=stage_groups(battle_data()['stages'])
        sixth=next(items for label,items in groups if label=='第VI层 · 源流交汇处')
        self.assertEqual({sid for _,sid,_ in sixth},IDS)
        all_ids=[sid for _,rows in groups for _,sid,_ in rows]
        self.assertEqual(len(all_ids),105);self.assertEqual(set(all_ids),set(battle_data()['stages']))
        self.assertEqual(view_catalog(),before)

    def test_natural_directory_matches_sixth_and_excludes_other_main_floors(self):
        for kind,expected in (('作战',{'ro6_n_6_1','ro6_n_6_2'}),
                              ('紧急作战',{'ro6_e_6_1','ro6_e_6_2'}),('险路恶敌',{'ro6_b_6'})):
            self.assertEqual({r['id'] for r in battle_candidates(kind,6)['rows']},expected)
            for floor in range(1,6):
                r=battle_candidates(kind,floor)
                self.assertFalse(expected&{row['id'] for row in r['rows']})
                self.assertTrue(expected<={row['id'] for row in r['excluded']})

    def test_content_and_special_region_do_not_turn_reference_into_entry_exclusion(self):
        for kwargs in ({'context':'content'},{'context':'all','entry_mode':'content'}, {'special_region':True}):
            ids={r['id'] for r in battle_candidates('作战',1,**kwargs)['rows']}
            self.assertTrue({'ro6_n_6_1','ro6_n_6_2'}<=ids)
        self.assertEqual(len(battle_candidates()['rows']),105)
        self.assertFalse(battle_candidates('“居民”据点',6,difficulty=15)['rows'])

    def test_original_pool_marker_and_layer_unknown_scenes_remain_separate(self):
        rows={r['id']:r for r in battle_candidates()['rows']}
        for sid in IDS:
            self.assertEqual(rows[sid]['floor'],6);self.assertIsNone(rows[sid]['documented_floors'])
            self.assertTrue(rows[sid]['hidden_layer_reference'])
        self.assertIsNone(rows['ro6_duel_1']['floor_reference_source'])
        self.assertIsNone(rows['ro6_duel_1']['floors'])

    def test_returned_sources_do_not_mutate_later_queries(self):
        r=sixth_floor_reference('ro6_n_6_1');r['source']['url']='changed';r['binding']['original_icon']='changed'
        fresh=sixth_floor_reference('ro6_n_6_1')
        self.assertEqual(fresh['binding']['original_icon'],'zone_6');self.assertIn('prts',fresh['source']['url'])
        self.assertIn('没有按关卡编号',floor_reference_text(fresh));self.assertEqual(floor_reference_text(None),'')

    def test_actual_battle_branch_selection_preserves_identity_and_source_caption(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.show();self.qt.processEvents()
        panel.stage_choices.select_branch('第VI层 · 源流交汇处')
        self.assertEqual({panel.stage_combo.itemData(i) for i in range(panel.stage_combo.count()) if panel.stage_combo.itemData(i)},IDS)
        for sid in IDS:
            panel.set_stage(sid);self.qt.processEvents()
            self.assertEqual(panel.current_stage,sid);self.assertIn('第VI层',panel.summary.text())
            self.assertIn('模板或连接',panel.summary.text())
        before=panel.summary.text();panel.render_rows();self.assertEqual(panel.summary.text(),before)

    def test_actual_catalog_detail_links_exact_battle_and_displays_provenance(self):
        panel=NodeCatalogPanel();self.addCleanup(panel.close);panel.kind.setCurrentIndex(panel.kind.findData('battle'))
        for sid in IDS:
            row=next(i for i,e in enumerate(panel.entries) if e['record'].get('id')==sid)
            panel.list.setCurrentRow(row);self.qt.processEvents();text=panel.detail.toPlainText()
            self.assertIn('第6层',text);self.assertIn('源流交汇处',text)
            self.assertIn('当前入口资格与实际出现未知',text)
            self.assertTrue(panel.battle_button.isEnabled())


if __name__=='__main__':unittest.main()
