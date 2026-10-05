"""Selectable branches, recruited-only overview and exact skill pictures."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,hashlib,json,tempfile,time,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication,QComboBox
from rouge.branch_choice import BranchChoice,OVERVIEW
from rouge.view_catalog import skill_catalog,portrait_record,skill_icon,PROFESSIONS,ENEMY_TIERS,DATA
from rouge.catalog import operator_profiles
from rouge.battle_preview import battle_data
import rouge.app as module
import tests.test_ui_refresh_045 as prior

APP=QApplication.instance() or QApplication([])
ROOT=Path(__file__).resolve().parents[1]


def values(combo):return [combo.itemData(i) for i in range(combo.count()) if combo.itemData(i) is not None]


class BranchControlTests(unittest.TestCase):
    def setUp(self):
        self.combo=QComboBox()
        self.groups=[('A',[('one',1,QIcon()),('two',2,QIcon())]),('B',[('three',3,QIcon())])]
        self.choice=BranchChoice(self.combo,self.groups,overview_label='Overview',overview=(2,3))
        self.addCleanup(self.choice.close)

    def test_branch_is_selectable_and_child_has_only_that_branch(self):
        self.assertEqual(values(self.combo),[2,3])
        self.assertTrue(self.choice.select_branch('A'));self.assertEqual(values(self.combo),[1,2])
        self.assertEqual(self.combo.currentData(),2)
        self.choice.select_branch('B');self.assertEqual(values(self.combo),[3])
        for i in range(self.choice.branch.count()):self.assertTrue(self.choice.branch.model().item(i).isEnabled())

    def test_external_selection_reveals_identity_and_emits_only_once(self):
        events=[];self.combo.currentIndexChanged.connect(lambda _:events.append(self.combo.currentData()))
        self.assertTrue(self.choice.select_value(1))
        self.assertEqual(self.choice.branch.currentData(),'A');self.assertEqual(events,[1])
        self.assertFalse(self.choice.select_value(999));self.assertEqual(events,[1])

    def test_refresh_keeps_branch_and_selected_identity(self):
        self.choice.select_branch('A');self.choice.select_value(2)
        self.choice.set_groups(copy.copy(self.groups))
        self.assertEqual(self.choice.branch.currentData(),'A');self.assertEqual(self.combo.currentData(),2)

    def test_overview_whitelist_updates_and_does_not_leak_other_branch_items(self):
        self.choice.set_overview((3,));self.assertEqual(values(self.combo),[3])
        self.choice.set_overview(());self.assertEqual(values(self.combo),[])
        self.assertIsNone(self.combo.currentData());self.assertFalse(self.combo.isEnabled())
        self.choice.select_branch('A');self.assertEqual(values(self.combo),[1,2]);self.assertTrue(self.combo.isEnabled())

    def test_branch_retaining_identity_does_not_emit_a_false_selection_change(self):
        events=[];self.combo.currentIndexChanged.connect(lambda _:events.append(1))
        self.choice.select_branch('A');self.assertEqual(self.combo.currentData(),2);self.assertEqual(events,[])

    def test_branch_filter_notifies_even_if_placeholder_selection_stays_none(self):
        combo=QComboBox();choice=BranchChoice(combo,self.groups,overview_label='Overview',placeholder='Choose',notify_unchanged=True)
        events=[];combo.currentIndexChanged.connect(lambda _:events.append(combo.currentData()))
        choice.select_branch('B');self.assertEqual(events,[None]);self.assertEqual(values(combo),[3]);choice.close()


class AppBranchTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.folder=Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        backend=module.DesktopBackend
        for key,name in [('RUN_STATE','run.json'),('OPERATOR_STATE','operators.json'),('SETTINGS','settings.json')]:
            self.stack.enter_context(patch.object(module,key,self.folder/name))
        self.stack.enter_context(patch.object(module,'DesktopBackend',lambda _path,callback:backend(self.folder/'chat',callback)))
        self.window=prior.OfflineWindow();self.window.show();APP.processEvents();self.addCleanup(self.close)

    def close(self):
        self.assertFalse(self.window.auto.isChecked());self.assertIsNone(self.window.capture.target)
        self.assertIsNone(self.window.desktop.process);self.assertFalse((self.folder/'chat').exists())
        self.assertFalse((self.folder/'settings.json').exists());self.window.close();APP.processEvents()

    def team(self,members,selected=None):
        observed={'operators':[{'id':op,'scope':'run','fields':{'elite':2,'level':70},'skill_ranks':{'1':7,'2':7,'3':7}}
                               for op in members],'selected_operator':selected,
                  'relics':{'ids':[],'icons':[],'source':'test'}}
        self.assertTrue(self.window.apply_run_observation(observed,time.time()))

    def test_operator_overview_excludes_account_unrecruited_and_absent_members(self):
        w=self.window;self.team(['mechanist','silverash'])
        w.operator_observations['kaltsit']={'id':'kaltsit','scope':'account','fields':{}}
        w.run.state['operators']['silverash']['present']=False
        w.run.state['operators']['kaltsit']={'id':'kaltsit','scope':'account','fields':{},'present':True}
        w.refresh_operator_overview();w.operator_choices.select_branch(OVERVIEW)
        self.assertEqual(values(w.operator),['mechanist'])

    def test_empty_operator_overview_clears_result_skill_picture_and_special_options(self):
        w=self.window;w.select_operator('silverash');w.skill.setCurrentIndex(w.skill.findData(3))
        w.operator_choices.select_branch(OVERVIEW)
        self.assertIsNone(w.operator.currentData());self.assertIsNone(w.damage_result)
        self.assertEqual(w.skill.count(),0);self.assertIsNone(w.skill_picture.key[1])
        self.assertIn('暂无已确认招募',w.damage_text.toPlainText())
        self.assertFalse(w.damage_form.isRowVisible(w.cooperative))
        self.assertFalse(w.damage_form.isRowVisible(w.fragile));self.assertFalse(w.level.isEnabled())
        w.select_operator('mechanist');self.assertTrue(w.level.isEnabled());self.assertIsNotNone(w.damage_result)

    def test_profession_branches_are_separate_and_cover_every_profile_once(self):
        w=self.window;seen=[]
        for profession,label in PROFESSIONS.items():
            self.assertTrue(w.operator_choices.select_branch(label))
            selected=values(w.operator)
            self.assertTrue(selected);self.assertTrue(all(operator_profiles()[key]['profession']==profession for key in selected))
            seen+=selected
        self.assertEqual(len(seen),431);self.assertEqual(set(seen),set(operator_profiles()))

    def test_recruited_overview_updates_in_real_time_and_preserves_viewed_member(self):
        w=self.window;self.team(['mechanist']);w.operator_choices.select_branch(OVERVIEW)
        w.level.setValue(61);selected=w.skill.currentData();run_id=w.run.state['id']
        self.team(['silverash']);self.assertCountEqual(values(w.operator),['mechanist','silverash'])
        self.assertEqual(w.operator.currentData(),'mechanist');self.assertEqual(w.level.value(),61)
        self.assertEqual(w.skill.currentData(),selected);self.assertEqual(w.run.state['id'],run_id)

    def test_account_observation_does_not_make_operator_recruited(self):
        w=self.window;w.apply_operator_observation({'id':'kaltsit','scope':'account','fields':{'elite':2,'level':90},'skill_ranks':{}},time.time())
        w.operator_choices.select_branch(OVERVIEW);self.assertEqual(values(w.operator),[])
        self.assertEqual(w.run.state['operators'],{})

    def test_switch_between_overview_and_same_operator_profession_keeps_simulation(self):
        w=self.window;self.team(['mechanist']);w.operator_choices.select_branch(OVERVIEW)
        w.level.setValue(61);w.skill.setCurrentIndex(w.skill.findData(2))
        w.operator_choices.select_branch(PROFESSIONS[operator_profiles()['mechanist']['profession']])
        self.assertEqual(w.operator.currentData(),'mechanist');self.assertEqual(w.level.value(),61)
        self.assertEqual(w.skill.currentData(),2)

    def test_floor_branch_limits_stages_and_external_follow_reveals_other_floor(self):
        w=self.window;panel=w.battle_preview
        panel.stage_choices.select_branch('第Ⅰ层');self.assertEqual(len(values(panel.stage_combo)),11)
        self.assertTrue(all('第Ⅰ层'==panel.stage_choices.branch.currentData() for _ in values(panel.stage_combo)))
        panel.set_stage('ro6_b_1');self.assertEqual(panel.stage_combo.currentData(),'ro6_b_1')
        self.assertEqual(panel.stage_choices.branch.currentData(),'第Ⅲ层')
        w.select_battle_stage('ro6_n_6_1');self.assertEqual(w.target_stage.currentData(),'ro6_n_6_1')
        self.assertEqual(panel.current_stage,'ro6_n_6_1')

    def test_same_stage_branch_switch_preserves_spawn_and_ordinal(self):
        panel=self.window.battle_preview;panel.set_stage('ro6_n_1_2')
        row=next(i for i,r in enumerate(panel.rows) if r['action']['count']>1)
        panel.spawn_list.setCurrentRow(row);panel.occurrence.setValue(panel.occurrence.maximum())
        identity=panel.grid.selected['id'];ordinal=panel.occurrence.value()
        panel.stage_choices.select_branch('第Ⅰ层')
        self.assertEqual(panel.grid.selected['id'],identity);self.assertEqual(panel.occurrence.value(),ordinal)

    def test_enemy_branch_filters_both_choices_and_map_spawn_references(self):
        panel=self.window.battle_preview;panel.set_stage('ro6_n_1_2')
        stage=battle_data()['stages'][panel.current_stage];all_rows=len(panel.rows)
        self.assertTrue(panel.enemy_choices.select_branch('普通'))
        ids={e['id'] for e in stage['enemies'] if e['level_type']=='NORMAL'}
        self.assertTrue(panel.rows);self.assertTrue(all(r['action']['key'] in ids for r in panel.rows))
        self.assertTrue(all(identity[0] in ids for identity in values(panel.enemy_combo)))
        panel.enemy_choices.select_branch(OVERVIEW);self.assertEqual(len(panel.rows),all_rows)

    def test_unknown_enemy_tier_has_its_own_branch_and_overview_keeps_it(self):
        panel=self.window.battle_preview;panel.set_stage('ro6_n_2_3')
        all_values=values(panel.enemy_combo);self.assertTrue(panel.enemy_choices.select_branch('类别未确认'))
        self.assertEqual(len(values(panel.enemy_combo)),4)
        panel.enemy_choices.select_branch(OVERVIEW);self.assertCountEqual(values(panel.enemy_combo),all_values)

    def test_skill_selector_and_selected_detail_use_exact_skill_id(self):
        w=self.window
        for op in ('kaltsit','silverash','mechanist'):
            w.select_operator(op)
            for i in range(w.skill.count()):
                w.skill.setCurrentIndex(i);sid=operator_profiles()[op]['skills'][w.skill.currentData()-1]['id']
                self.assertFalse(w.skill.itemIcon(i).isNull());self.assertEqual(w.skill_picture.key[1],sid)
                self.assertFalse(w.skill_picture.image.pixmap().isNull())


class SkillOriginalTests(unittest.TestCase):
    def test_all_profile_skill_slots_have_verified_original_icons(self):
        d=skill_catalog();ids={s['id'] for p in operator_profiles().values() for s in p['skills']}
        self.assertEqual(set(d['skills']),ids);self.assertEqual(len(ids),893);self.assertEqual(len(d['images']),884)
        self.assertEqual(sum(len(p['skills']) for p in operator_profiles().values()),949)
        for sid in ids:self.assertFalse(skill_icon(sid).isNull(),sid)
        for record in d['images'].values():
            raw=(DATA/record['file']).read_bytes();self.assertEqual(len(raw),record['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),record['sha256'])
            self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),record['blob_sha1'])
            with Image.open(DATA/record['file']) as image:
                self.assertEqual(image.format,'PNG');self.assertEqual(image.size,(record['width'],record['height']));image.verify()

    def test_source_icon_overrides_are_not_replaced_by_similar_skill_names(self):
        d=skill_catalog();table=json.loads((ROOT/'.cache/game-data/skill_table.json').read_text(encoding='utf-8'))
        self.assertEqual(hashlib.sha256((ROOT/'.cache/game-data/skill_table.json').read_bytes()).hexdigest(),d['skill_source']['sha256'])
        overrides=0
        for sid,r in d['skills'].items():
            self.assertEqual(r['icon_id'],table[sid].get('iconId') or sid)
            self.assertEqual(portrait_record('skill',sid)['file'],'skill-icons/skill_icon_'+r['icon_id']+'.png')
            overrides+=r['icon_id']!=sid
        self.assertGreater(overrides,0);self.assertIsNone(portrait_record('skill','unknown-skill'))


if __name__=='__main__':unittest.main()
