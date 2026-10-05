"""Chinese presentation, original profession assets, and retained UI state."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,hashlib,json,unittest
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import QApplication
from rouge.catalog import catalog,operator_profiles
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.view_catalog import DATA,PROFESSIONS,profession_catalog,profession_icon,stage_groups
from rouge.battle_preview import battle_data
from tests import test_branch_choices_046 as prior

APP=QApplication.instance() or QApplication([])


class ChineseReportTests(unittest.TestCase):
    def test_report_orders_prediction_before_explanations_and_keeps_results_unchanged(self):
        result=calculate_damage({'operator':'silverash','skill':3})
        before=copy.deepcopy(result);text=format_report(result)
        for title in ('培养信息','预计属性','当前技能','技能时序','费用收益','伤害输出','计算说明','待确认与适用范围'):
            self.assertIn('【'+title+'】',text)
        self.assertLess(text.index('【伤害输出】'),text.index('【计算说明】'))
        self.assertIn('每秒伤害',text);self.assertNotIn(' DPS',text);self.assertNotIn('http',text)
        self.assertIn('7级 · 专精3',text);self.assertEqual(result,before)

    def test_technical_sources_and_original_keys_remain_available(self):
        result=calculate_damage({'operator':'mechanist','skill':1})
        plain=format_report(result);technical=format_report(result,technical=True)
        self.assertNotIn('projectile_delay_time',plain);self.assertNotIn('attack@interval',plain)
        self.assertIn('【技术资料】',technical);self.assertIn('projectile_delay_time',technical)
        self.assertIn('档案弹道延迟参数',plain)

    def test_capability_sections_stay_specific_and_unknowns_do_not_become_zero(self):
        medic=format_report(calculate_damage({'operator':'char_298_susuro','skill':1}))
        self.assertIn('【治疗输出】',medic);self.assertIn('每秒治疗',medic)
        self.assertNotIn('【伤害输出】',medic);self.assertNotIn('【费用收益】',medic)
        result=calculate_damage({'operator':'mechanist','skill':2})
        self.assertIsNone(result['estimate']['skill']['cycle_seconds'])
        self.assertIn('预计回转：未知',format_report(result))

    def test_unverified_script_warning_stays_unknown_without_exposing_raw_key(self):
        result=calculate_damage({'operator':'mechanist','skill':1})
        result['estimate']['warnings']=['藏品：未覆盖 global_buff_normal:rogue_6_unknown[dark]。']
        text=format_report(result)
        self.assertIn('未核验配置',text);self.assertNotIn('global_buff_normal',text)
        self.assertIn('global_buff_normal:rogue_6_unknown[dark]',format_report(result,technical=True))


class ProfessionAssetsTests(unittest.TestCase):
    def test_all_eight_professions_have_source_verified_originals(self):
        data=profession_catalog();self.assertEqual(set(data['professions']),set(PROFESSIONS))
        paths=set()
        for key,entry in data['professions'].items():
            self.assertEqual(entry['label'],PROFESSIONS[key]);raw=(DATA/entry['file']).read_bytes()
            self.assertEqual(len(raw),entry['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),entry['sha256'])
            self.assertEqual(hashlib.sha1(raw).hexdigest(),entry['sha1'])
            self.assertEqual(entry['game_profession'],key.upper())
            self.assertEqual(entry['correspondence']['game_profession'],key.upper())
            with Image.open(DATA/entry['file']) as pic:self.assertEqual(pic.size,(26,26))
            self.assertFalse(profession_icon(key).isNull());paths.add((DATA/entry['file']).resolve())
        self.assertEqual(paths,{p.resolve() for p in (DATA/'profession-icons').glob('*.png')})

    def test_stage_labels_keep_identity_in_data_without_raw_id_in_title(self):
        for _,items in stage_groups(battle_data()['stages']):
            self.assertEqual(len({title for title,_,_ in items}),len(items))
            for title,sid,_ in items:self.assertNotIn(sid,title);self.assertIn(sid,battle_data()['stages'])


class PresentationAppTests(unittest.TestCase):
    setUp=prior.AppBranchTests.setUp
    close=prior.AppBranchTests.close

    def test_branch_and_operator_caption_have_the_correct_profession_picture(self):
        w=self.window
        for key,label in PROFESSIONS.items():
            branch=w.operator_choices.branch.findData(label)
            self.assertGreaterEqual(branch,0);self.assertFalse(w.operator_choices.branch.itemIcon(branch).isNull())
            w.operator_choices.select_branch(label)
            self.assertFalse(w.operator_picture.profession.isHidden())
            self.assertEqual(w.operator_picture.profession.accessibleName(),label+'职业图标')
        w.operator_choices.select_branch('__overview__');self.assertTrue(w.operator_picture.profession.isHidden())

    def test_technical_switch_keeps_operator_skill_and_simulation_conditions(self):
        w=self.window;w.select_operator('silverash');w.skill.setCurrentIndex(w.skill.findData(3))
        w.level.setValue(61);w.charge_count.setValue(4)
        previous=copy.deepcopy(w.damage_result)
        for mode in (True,False,True):
            w.damage_technical.setChecked(mode);APP.processEvents()
            self.assertEqual(w.operator.currentData(),'silverash');self.assertEqual(w.skill.currentData(),3)
            self.assertEqual(w.level.value(),61);self.assertEqual(w.charge_count.value(),4)
            self.assertEqual(w.damage_result,previous)

    def test_battle_technical_switch_keeps_filters_row_and_occurrence(self):
        p=self.window.battle_preview
        sid=next(sid for sid,s in battle_data()['stages'].items() if any(
            a['action']['count']>1 for wave in s['waves'] for f in wave['fragments'] for a in f['actions'] if a['action']['actionType']=='SPAWN'))
        p.set_stage(sid)
        index=next(i for i,row in enumerate(p.rows) if row['action']['count']>1)
        p.spawn_list.setCurrentRow(index);p.occurrence.setValue(2)
        row_id=p.grid.selected['id'];branch=p.stage_choices.branch.currentData()
        for mode in (True,False):
            p.technical.setChecked(mode);APP.processEvents()
            self.assertEqual(p.grid.selected['id'],row_id);self.assertEqual(p.occurrence.value(),2)
            self.assertEqual(p.stage_choices.branch.currentData(),branch)
            if mode:self.assertIn('preDelay',p.spawn_detail.toPlainText())
            else:self.assertNotIn('preDelay',p.spawn_detail.toPlainText())


if __name__=='__main__':unittest.main()
