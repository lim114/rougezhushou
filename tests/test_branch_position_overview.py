from copy import deepcopy
import unittest
from unittest.mock import patch
from rouge.branch_position_overview import branch_position_overview,overview_text
from rouge.branch_reference import branch_reference
from rouge.battle_preview import battle_data


class BranchPositionTests(unittest.TestCase):
    def test_all105_stages_preserve230_source_positions_without_route_inference(self):
        references=0;cells=0;present=0
        for sid,stage in battle_data()['stages'].items():
            raw=branch_reference(sid);r=branch_position_overview(sid)
            expected=[ref for branch in raw['rows'] for ref in branch['map_references']]
            actual=[ref for group in r['rows'] for ref in group['references']]
            self.assertCountEqual(actual,expected)
            self.assertEqual(r['level_sha256'],stage['level_source']['sha256'])
            self.assertEqual([g['ordinal'] for g in r['rows']],list(range(1,len(r['rows'])+1)))
            self.assertIsNone(r['actual_activation']);self.assertIsNone(r['actual_spawn_positions'])
            self.assertFalse(r['all_branch_routes_bound'])
            self.assertNotIn('route',r)
            references+=r['reference_count'];cells+=r['cell_count'];present+=bool(r['cell_count'])
        self.assertEqual((present,references,cells),(67,230,230))

    def test_phase_filter_does_not_turn_producer_position_into_phase_spawn(self):
        full=branch_position_overview('ro6_b_5','boss_trap')
        one=branch_position_overview('ro6_b_5','boss_trap',1)
        self.assertEqual(full['reference_count'],9)
        self.assertTrue(all(ref['source_kind']=='activation_object' for g in one['rows'] for ref in g['references']))
        original=branch_reference('ro6_n_1_1')
        branch=original['rows'][0]['branch_id']
        r=branch_position_overview('ro6_n_1_1',branch,1)
        self.assertTrue(all(ref['source_kind']=='producer_declaration' for g in r['rows'] for ref in g['references']))
        self.assertTrue(all('phase' not in ref for g in r['rows'] for ref in g['references']))

    def test_same_cell_references_are_separate_not_counted_as_enemies(self):
        # Explicit synthetic overlap fixture; real frozen corpus currently has no overlapping cells.
        raw=branch_reference('ro6_b_5','boss_trap')
        refs=raw['rows'][0]['map_references'];refs[1]['cell']=deepcopy(refs[0]['cell'])
        with patch('rouge.branch_position_overview.branch_reference',return_value=raw):
            r=branch_position_overview('ro6_b_5','boss_trap')
        self.assertEqual((r['reference_count'],r['cell_count']),(9,8))
        overlap=next(g for g in r['rows'] if len(g['references'])==2)
        self.assertEqual(len({x['reference_id'] for x in overlap['references']}),2)
        self.assertIn('不等于同时出现或敌人数',overview_text(r))
        r['rows'][0]['references'][0]['name']='changed'
        self.assertNotEqual(raw['rows'][0]['map_references'][0]['name'],'changed')

    def test_unknown_location_and_empty_stages_remain_empty(self):
        r=branch_position_overview('ro6_n_4_7','dlancer_branch_1')
        self.assertEqual(r['rows'],[]);self.assertEqual(r['reference_count'],0)
        self.assertIsNone(r['actual_spawn_positions'])
        for args in [('absent',None,None),('ro6_b_5','absent',None),('ro6_b_5',None,1),('ro6_b_5','boss_trap',True)]:
            with self.assertRaises(ValueError):branch_position_overview(*args)


class BranchPositionWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def panel(self,stage='ro6_n_1_2'):
        from rouge.battle_view import BattlePreviewPanel
        p=BattlePreviewPanel();self.addCleanup(p.close);p.set_stage(stage);p.branch_toggle.setChecked(True)
        return p

    def test_real_fixed_image_and_grid_share_source_numbers_and_projection_gate(self):
        p=self.panel();expected=branch_position_overview('ro6_n_1_2')['rows']
        self.assertEqual(p.grid.branch_positions,expected)
        self.assertEqual(p.original.branch_positions,expected)
        self.assertEqual(len(p.original.projected_branch_positions()),2)
        self.assertIn('P1',p.branch_panel.location.itemText(0))
        self.assertIn('P2',p.branch_panel.location.itemText(1))
        p.original.projection=None
        self.assertEqual(p.original.projected_branch_positions(),[])
        self.assertEqual(len(p.grid.branch_positions),2)

    def test_branch_phase_and_overlay_changes_rebuild_not_borrow_other_stage(self):
        p=self.panel('ro6_b_5');b=p.branch_panel
        b.branch.setCurrentIndex(b.branch.findData('boss_trap'))
        b.phase.setCurrentIndex(b.phase.findData(1))
        self.assertEqual(p.grid.branch_positions,branch_position_overview('ro6_b_5','boss_trap',1)['rows'])
        b.overlay.setChecked(False);self.assertEqual(p.grid.branch_positions,[])
        self.assertEqual(p.original.branch_positions,[])
        b.overlay.setChecked(True);self.assertEqual(len(p.grid.branch_positions),3)
        p.branch_toggle.setChecked(False);self.assertEqual(p.grid.branch_positions,[])
        p.branch_toggle.setChecked(True);self.assertEqual(len(p.grid.branch_positions),3)
        p.set_stage('ro6_n_4_7');b.branch.setCurrentIndex(b.branch.findData('dlancer_branch_1'))
        self.assertEqual(p.grid.branch_positions,[])

    def test_refresh_preserves_phase_location_and_text_selection(self):
        from PySide6.QtGui import QTextCursor
        p=self.panel('ro6_b_5');b=p.branch_panel
        b.branch.setCurrentIndex(b.branch.findData('boss_trap'));b.phase.setCurrentIndex(b.phase.findData(1))
        b.location.setCurrentIndex(2);snapshot=deepcopy(p.grid.branch_positions)
        cursor=b.position_detail.textCursor();cursor.setPosition(3);cursor.setPosition(9,QTextCursor.MoveMode.KeepAnchor)
        b.position_detail.setTextCursor(cursor);selected=cursor.selectedText()
        b.refresh();p.render_rows()
        self.assertEqual(b.phase.currentData(),1);self.assertEqual(b.location.currentIndex(),2)
        self.assertEqual(p.grid.branch_positions,snapshot)
        self.assertEqual(b.position_detail.textCursor().selectedText(),selected)

    def test_highland_not_added_to_ground_plane_and_input_copies_are_isolated(self):
        p=self.panel();saved=deepcopy(p.grid.branch_positions)
        marker=p.original.branch_positions[0];cell=marker['cell']
        fake=deepcopy(p.original.stage)
        index=fake['map'][cell['row']][cell['col']]
        fake['tiles'][index]['heightType']='HIGHLAND';p.original.stage=fake
        self.assertFalse(any(g['cell']==cell for g,_ in p.original.projected_branch_positions()))
        p.original.branch_positions[0]['references'][0]['name']='changed'
        self.assertEqual(p.grid.branch_positions,saved)
        p.original.set_file(None);self.assertEqual(p.original.branch_positions,[])


if __name__=='__main__':unittest.main()
