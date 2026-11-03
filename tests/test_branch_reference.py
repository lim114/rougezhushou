from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge.branch_reference import branch_reference,branch_reference_text,origin_data,_document
from rouge.branch_reference_view import BranchReferencePanel
from rouge.battle_preview import battle_data
from rouge.battle_planning import branch_phase_catalog
from rouge.battle_view import BattlePreviewPanel


class BranchReferenceTests(unittest.TestCase):
    def test_full_fixed_scope_preserves_every_phase_action_and_actual_unknowns(self):
        keys=set(origin_data()['stages']);self.assertEqual(keys,set(battle_data()['stages']))
        levels=set();branches=phases=actions=activated=0
        for sid in keys:
            result=branch_reference(sid);old=branch_phase_catalog(sid)['branches']
            self.assertEqual([r['branch_id'] for r in result['rows']],[r['branch_id'] for r in old])
            self.assertEqual(result['source']['sha256'],battle_data()['stages'][sid]['level_source']['sha256'])
            for row,before in zip(result['rows'],old):
                self.assertIsNone(row['actual_trigger']);self.assertIsNone(row['actual_global_seconds']);self.assertIsNone(row['phase_selection'])
                self.assertEqual([p['phase'] for p in row['phases']],[p['phase'] for p in before['phases']])
                for p,q in zip(row['phases'],before['phases']):self.assertEqual([a['action'] for a in p['actions']],[a['action'] for a in q['actions']])
            key=origin_data()['stages'][sid]['level_key']
            if key not in levels:
                levels.add(key);branches+=len(result['rows'])
                phases+=sum(len(r['phases']) for r in result['rows']);actions+=sum(len(p['actions']) for r in result['rows'] for p in r['phases'])
                activated+=sum(a['action']['actionType']=='ACTIVATE_PREDEFINED' for r in result['rows'] for p in r['phases'] for a in p['actions'])
        self.assertEqual((len(keys),len(levels),branches,phases,actions,activated),(105,68,151,160,203,9))

    def test_trigger_documents_require_exact_device_instance_skill_and_phase(self):
        row=next(r for r in branch_reference('ro6_n_3_5')['rows'] if r['branch_id']=='larva1')
        origin=row['origins'][0];self.assertEqual(origin['entity_id'],'trap_086_larva')
        self.assertIn('所有预配置敌方单位',origin['documented_trigger_reference']['trigger_reference'])
        self.assertFalse(origin['actual_trigger_verified']);self.assertIsNone(origin['actual_trigger'])
        for change in ({'entity_id':'trap_unknown'},{'instance_level':2},{'instance_level':True},{'skill_level':2},{'skill_level':True},{'kind':'enemy_reference'}):
            changed=deepcopy(origin);changed.update(change);self.assertIsNone(_document(changed))
        changed=deepcopy(origin);changed['raw']['inst']['phase']='PHASE_1';self.assertIsNone(_document(changed))

    def test_cloned_terminal_ids_have_direct_fields_without_borrowed_model_trigger(self):
        rows=branch_reference('ro6_n_4_7')['rows']
        terminal=next(r for r in rows if r['branch_id']=='dlancer_branch_1')['origins'][0]
        self.assertEqual(terminal['entity_id'],'enemy_10071_ftprg_a')
        self.assertTrue(terminal['field_reference_verified']);self.assertIsNone(terminal['documented_trigger_reference'])
        self.assertIsNone(terminal['display_cell']);self.assertIsNone(terminal['actual_seconds'])

    def test_non_spawn_actions_bind_unique_alias_not_route_index(self):
        row=branch_reference('ro6_b_5','boss_trap')['rows'][0]
        actions=[a for p in row['phases'] for a in p['actions']]
        self.assertEqual(len(actions),9);self.assertTrue(all(a['action']['actionType']=='ACTIVATE_PREDEFINED' for a in actions))
        self.assertTrue(all(a['predefined_binding']['binding_status']=='exact_alias' for a in actions))
        self.assertTrue(all(a['display_cell'] for a in actions))
        self.assertEqual(len(row['map_references']),9)
        spawn=branch_reference('ro6_n_1_1')['rows'][0]['phases'][0]['actions'][0]
        self.assertIsNone(spawn['display_cell']);self.assertIsNone(spawn['predefined_binding'])

    def test_empty_phase_and_missing_source_never_create_actions_or_times(self):
        original=branch_phase_catalog('ro6_b_5','boss_trap');fake=deepcopy(original)
        fake['branches'][0]['phases'][0]['actions']=[]
        with patch('rouge.branch_reference.branch_phase_catalog',return_value=fake):
            result=branch_reference('ro6_b_5','boss_trap',1)
        row=result['rows'][0];self.assertEqual(row['origin_status'],'unknown');self.assertFalse(row['phases'][0]['actions'])
        self.assertIn('空配置阶段',branch_reference_text(result));self.assertIsNone(row['actual_global_seconds'])

    def test_explicit_namespace_and_ambiguous_alias_remain_independent(self):
        path=Path(__file__).resolve().parents[1]/'scripts/build_branch_origin_reference.py'
        spec=importlib.util.spec_from_file_location('branch_origin_builder',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        obj={'inst':{'characterKey':'trap_x'},'alias':'same','overrideSkillBlackboard':[{'key':'talent@branch_id','valueStr':'q'}]}
        raw={'predefines':{'tokenInsts':[obj]},'hardPredefines':{'tokenInsts':[deepcopy(obj)]},
             'branches':{'q':{'phases':[{'actions':[{'actionType':'ACTIVATE_PREDEFINED','key':'same','routeIndex':999}]}]}}}
        result=m.extract(raw,{})['q'];self.assertEqual(len(result['origins']),2)
        self.assertEqual(result['activations'][0]['binding_status'],'ambiguous_alias');self.assertEqual(len(result['activations'][0]['objects']),2)

    def test_invalid_phase_and_queries_are_copies(self):
        before=deepcopy(origin_data());result=branch_reference('ro6_n_1_1')
        result['rows'][0]['origins'][0]['related_parameters'].clear();self.assertEqual(origin_data(),before)
        for sid,bid,phase in ((None,None,None),('missing',None,None),('ro6_n_1_1','unknown',None),('ro6_n_1_1',None,1),('ro6_n_1_1','shsbox1',True),('ro6_n_1_1','shsbox1',999)):
            with self.assertRaises(ValueError):branch_reference(sid,bid,phase)


class BranchReferenceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_branch_and_phase_detail_refresh_preserves_selection_cursor_and_scroll(self):
        panel=BranchReferencePanel();self.addCleanup(panel.close);panel.resize(760,400);panel.show();panel.set_stage('ro6_b_5');self.qt.processEvents()
        index=next(i for i in range(panel.branch.count()) if panel.branch.itemData(i)=='boss_trap');panel.branch.setCurrentIndex(index);panel.phase.setCurrentIndex(1)
        panel.set_technical(True);self.qt.processEvents();text=panel.detail.toPlainText()
        self.assertIn('ACTIVATE_PREDEFINED',text);self.assertIn('完整动作原参数',text)
        cursor=panel.detail.textCursor();cursor.setPosition(12);cursor.setPosition(25,QTextCursor.MoveMode.KeepAnchor);selection=cursor.selectedText();panel.detail.setTextCursor(cursor)
        panel.detail.verticalScrollBar().setValue(10);scroll=panel.detail.verticalScrollBar().value();location=panel.location.currentData()
        panel.refresh();panel.set_stage('ro6_b_5');self.qt.processEvents()
        self.assertEqual(panel.branch.currentData(),'boss_trap');self.assertEqual(panel.phase.currentData(),1)
        self.assertEqual(panel.location.currentData(),location);self.assertEqual(panel.detail.textCursor().selectedText(),selection)
        self.assertEqual(panel.detail.verticalScrollBar().value(),scroll)

    def test_fixed_window_fold_entrance_marks_alias_object_and_survives_row_refresh(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.resize(1050,850);panel.show();panel.set_stage('ro6_b_5');panel.branch_toggle.setChecked(True);self.qt.processEvents()
        branch=panel.branch_panel;index=next(i for i in range(branch.branch.count()) if branch.branch.itemData(i)=='boss_trap');branch.branch.setCurrentIndex(index)
        branch.locate.click();reference=branch.location.currentData()
        self.assertEqual(reference['source_kind'],'activation_object');self.assertEqual(panel.grid.reference_cell,reference['cell'])
        self.assertEqual(panel.original.reference_cell,reference['cell']);self.assertIn('唯一alias',panel.spawn_detail.toPlainText())
        panel.render_rows();self.assertEqual(panel.grid.reference_cell,reference['cell']);self.assertEqual(branch.branch.currentData(),'boss_trap')
        panel.technical.setChecked(True);self.assertIn(reference['source_selector'],panel.spawn_detail.toPlainText())
        panel.branch_toggle.setChecked(False);self.assertFalse(branch.isVisible());panel.branch_toggle.setChecked(True);self.assertEqual(branch.branch.currentData(),'boss_trap')
        panel.set_stage('ro6_n_1_1');self.assertIsNone(panel._branch_marker)
        panel._branch_reference_cell(reference);self.assertIsNone(panel._branch_marker)
        bad=deepcopy(reference);bad.update(stage_id='ro6_n_1_1',level_sha256='wrong');panel._branch_reference_cell(bad);self.assertIsNone(panel._branch_marker)
        panel.set_stage('ro6_b_5');tampered=deepcopy(reference);tampered['cell']={'row':0,'col':0}
        panel._branch_reference_cell(tampered);self.assertIsNone(panel._branch_marker)

    def test_source_only_locations_and_spawn_phase_do_not_invent_route_points(self):
        panel=BranchReferencePanel();self.addCleanup(panel.close);panel.set_stage('ro6_n_4_7')
        index=next(i for i in range(panel.branch.count()) if panel.branch.itemData(i)=='dlancer_branch_1');panel.branch.setCurrentIndex(index)
        self.assertEqual(panel.location.count(),0);self.assertFalse(panel.locate.isEnabled())
        self.assertIn('实际触发',panel.detail.toPlainText());self.assertIn('路线数组未知',panel.detail.toPlainText())


if __name__=='__main__':unittest.main()
