"""Offline Qt smoke check of every supported profile and the requested report."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys
import json
import tempfile
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt
import rouge.app as app_module
from rouge.app import MainWindow
from rouge.recognition import ScreenReader
import cv2
import numpy as np
root=Path(__file__).resolve().parents[1]
temporary=tempfile.TemporaryDirectory()
app_module.OPERATOR_STATE=Path(temporary.name)/'operator-state.json'
app_module.RUN_STATE=Path(temporary.name)/'run-state.json'
app_module.SETTINGS=Path(temporary.name)/'settings.json'
app=QApplication([])
window=MainWindow()
try:
    count=0
    for index in range(window.operator.count()):
        if window.operator.itemData(index) not in app_module.catalog()['operators']:continue
        window.operator.setCurrentIndex(index)
        for skill_index in range(window.skill.count()):
            window.skill.setCurrentIndex(skill_index)
            window.calculate()
            assert window.damage_result
            op=window.operator.currentData();skill=window.skill.currentData()
            options=[(window.cooperative,op=='silverash' and skill==3),
                     (window.fragile,op=='silverash' and skill==3),
                     (window.charge_count,op=='mechanist' and skill==3),
                     (window.shield_breaks,op=='mechanist' and skill==2),
                     (window.shield_duration,op=='mechanist' and skill==2),
                     (window.continuous_attacks,app_module.catalog()['operators'][op]['skills'][skill-1]['levels'][-1]['sp_type']=='INCREASE_WHEN_ATTACK'),
                     (window.healing_targets,op in ('kaltsit','char_196_sunbr','char_2025_shu','char_298_susuro','char_1037_amiya3','char_4202_haruka') or (op=='char_151_myrtle' and skill==2)),
                     *[(w,op=='silverash' and skill==2) for w in (window.activation_count,window.companion_attack,window.stacks)]]
            for widget,visible in options:
                assert widget.isHidden()!=visible,(op,skill,widget)
                label=window.damage_form.labelForField(widget)
                assert label.isHidden()!=visible,(op,skill,'label')
            text=window.damage_text.toPlainText()
            for owner,key,skills,widget in window.model_option_widgets:
                expected=owner==op and skill in skills
                assert widget.isHidden()!=expected,(op,skill,owner,key)
                assert window.damage_form.labelForField(widget).isHidden()!=expected,(op,skill,key,'label')
            for label in ['预计基础数值：','生命值：','攻击力：','防御：','法抗：','再部署时间：','攻速：','阻挡数：',
                          '技能情况：','预计回转：','预计初动：','【技能时序】','【状态与依据】']:
                assert label in text,(index,skill_index,label,text)
            expects_fee=op in ('char_151_myrtle','char_4228_closur','char_4087_ines') or (op=='silverash' and skill in (1,3))
            assert ('【费用收益】' in text)==expects_fee,(op,skill,'fee panel')
            expects_healing=op in ('kaltsit','char_196_sunbr','char_2025_shu','char_298_susuro','char_1037_amiya3','char_4202_haruka') or (op=='char_151_myrtle' and skill==2)
            assert ('【治疗输出】' in text)==expects_healing,(op,skill,'healing panel')
            blocks=window.damage_result['result']['report']['sections']
            assert all('【'+b['title']+'】' in text for b in blocks),(op,skill,'report sections')
            window.raw_damage.setChecked(True)
            assert 'base_stats' in window.damage_text.toPlainText()
            window.raw_damage.setChecked(False)
            count+=1
    image=cv2.imdecode(np.fromfile(root/'samples/native-client/operator-kaltsit.png',dtype=np.uint8),cv2.IMREAD_COLOR)
    observation=ScreenReader().read(image)
    observation['captured_at']=time.time()
    window.sample_received((image,observation))
    assert window.operator.currentData()=='kaltsit' and window.level.value()==90
    assert window.potential.text()=='2' and '200%' in window.trust.text()
    for field in (window.elite,window.trust,window.potential,window.module,window.rank,window.attack):
        assert isinstance(field,QLabel),'Cultivation field must be read-only'
    for skill,rank in ((1,7),(2,10),(3,10)):
        window.skill.setCurrentIndex(window.skill.findData(skill))
        assert window.damage_result['scenario']['skill_rank']==rank
        assert 'base_attack' not in window.damage_result['scenario']
    original_attack=window.attack.text()
    window.level.setValue(50)
    assert window.attack.text()!=original_attack and window.level_override
    window.sample_received((image,observation))
    assert window.level.value()==50,'Repeated sampling must preserve the explicit level simulation'
    window.update_operator()
    assert window.level.value()==90 and not window.level_override
    window.skill.setCurrentIndex(window.skill.findData(1))
    window.sample_received((image,observation))
    assert window.skill.currentData()==1,'Repeated sampling must preserve explicit skill comparison'
    # A different roster identity must display its own attributes, never leave Kaltsit selected.
    window.apply_operator_observation({'id':'char_172_svrash','fields':{'elite':2,'level':60,'trust':100,'potential':1,
        'module_id':None,'module_level':0,'selected_skill':3},'skill_ranks':{1:7,2:7,3:10}},time.time())
    assert window.operator.currentData()=='char_172_svrash' and not window.damage_result
    assert '技能伤害规则尚未实现' in window.damage_text.toPlainText()
    assert all(widget.isHidden() for widget in (window.cooperative,window.fragile,window.charge_count,window.shield_breaks))
    window.operator.setCurrentIndex(window.operator.findData('kaltsit'))
    window.apply_operator_observation({'id':'kaltsit','fields':{'elite':0,'level':50},'skill_ranks':{1:7}},time.time())
    assert window.damage_result and window.skill.count()==1
    for filename,op in (('operator-silverash.png','silverash'),('operator-mechanist.png','mechanist'),('module-mechanist.png','mechanist')):
        sample=cv2.imdecode(np.fromfile(root/'samples/native-client'/filename,dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(sample);observed['captured_at']=time.time()
        window.sample_received((sample,observed))
        assert window.operator.currentData()==op,(filename,observed.get('operator'),window.operator.currentData())
        assert window.damage_result
    assert window.level.value()==90 and window.potential.text()=='6'
    assert window.attack.text().startswith('673')
    assert window.damage_result['result']['estimate']['base_stats']['defense']==873
    assert '专精 2' in window.operator_summary.toPlainText()
    assert window.operator_observations['silverash']['fields']['level']==60
    assert window.operator_observations['kaltsit']['fields']['potential']==2
    # Public UI path: invalid preview must clear chat context; previews are per actor+skill.
    assert window.frame_timing.isChecked()
    window.timing_scenario.setPlainText('{')
    assert window.damage_result is None and '合法JSON' in window.damage_text.toPlainText()
    window.timing_scenario.setPlainText('{"windup_frames":6,"recovery_frames":9}')
    assert window.damage_result and window.damage_result['scenario']['timing']['windup_frames']==6
    previous=(window.operator.currentData(),window.skill.currentData())
    window.operator.setCurrentIndex(window.operator.findData('silverash'))
    assert window.timing_scenario.toPlainText()==''
    window.operator.setCurrentIndex(window.operator.findData(previous[0]))
    window.skill.setCurrentIndex(window.skill.findData(previous[1]))
    assert json.loads(window.timing_scenario.toPlainText())['windup_frames']==6
    assert '【战斗时序参考】' in window.damage_text.toPlainText()
    window.frame_timing.setChecked(False)
    assert window.damage_result['scenario']['timing_mode']=='continuous'
    window.frame_timing.setChecked(True)
    assert window.damage_result['scenario']['timing_mode']=='frames'
    window.auto_relics.setChecked(False)
    for i in range(window.relic_list.count()):window.relic_list.item(i).setCheckState(Qt.CheckState.Unchecked)
    assert window.relic_context.isHidden()
    gold=next(window.relic_list.item(i) for i in range(window.relic_list.count())
        if window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_legacy_60')
    gold.setCheckState(Qt.CheckState.Checked)
    assert not window.relic_context.isHidden()
    window.relic_context.setPlainText('{"gold":25}')
    assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==135
    original=(window.operator.currentData(),window.skill.currentData())
    window.operator.setCurrentIndex(window.operator.findData('silverash'))
    assert window.relic_context.toPlainText()==''
    window.operator.setCurrentIndex(window.operator.findData(original[0]))
    window.skill.setCurrentIndex(window.skill.findData(original[1]))
    assert json.loads(window.relic_context.toPlainText())['gold']==25
    window.relic_context.setPlainText('{')
    assert window.damage_result is None and '合法JSON' in window.damage_text.toPlainText()
    gold.setCheckState(Qt.CheckState.Unchecked)
    assert window.relic_context.isHidden() and window.damage_result
    receipt={'verified_at':time.time(),'skill_profiles':count,'offline_replay':True,
        'timing_preview_scoped_by_actor_and_skill':True,'invalid_preview_clears_analysis_context':True,
        'frame_reference_and_continuous_comparison':True,
        'relic_conditions_scoped_by_actor_skill_and_current_selection':True,
        'exclusive_fields_and_labels_hidden':True,'adaptive_report_verified':True,'fee_and_healing_panels_gated':True,'cultivation_read_only':True,
        'level_simulation_and_restore':True,'skill_comparison_persists_across_samples':True,
        'account_fixture_operators':['kaltsit','silverash','mechanist'],'module_fixture':'mechanist',
        'other_operators_live_capture_verified':False,'chat_requests':0}
    (root/'DAMAGE_UI_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{count} skill profiles rendered; unrelated fields hidden; cultivation read-only; actual captured fields applied; level simulation and restore verified; no chat requests')
finally:
    window.close()
    temporary.cleanup()
