"""Isolated skill panels: source uncertainty only on the applicable skill."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt

RIVER='rogue_6_relic_fight_22'


def main():
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        def select(ids):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False);window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
        skills=base_unknown=river_unknown=references=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill))
                    for ids in (set(),{RIVER}):
                        select(ids);r=window.damage_result['result'];text=window.damage_text.toPlainText()
                        has_secondary=op=='char_1042_phatm2' and skill==3
                        assert ('空剧场 · 持续损伤待核验' in text)==has_secondary,(op,skill,ids)
                        assert bool(r.get('neural_skill_reference'))==has_secondary,(op,skill,ids)
                        if has_secondary:
                            assert '当前情景损伤爆发次数：未知' in text
                            assert '持续神经损伤首跳时刻：未知' in text
                            assert '单次技能总伤：未知' in text
                            assert '可确定法伤' in text
                            assert not r['neural_skill_reference']['secondary_events_scheduled']
                        assert ('河谷祭祈 · 神经爆发参考' in text)==bool(r.get('neural_relic_reference'))
                        assert ('已建模伤害小计' in text)==bool(r.get('known_damage_subtotals'))
                        if not ids:
                            assert '河谷祭祈' not in text
                            base_unknown+=int(bool(r.get('known_damage_subtotals')))
                        else:
                            river_unknown+=int(bool(r.get('known_damage_subtotals')))
                            references+=int(bool(r.get('neural_relic_reference')))
                        assert not window.damage_form.isRowVisible(window.relic_context)
                        for owner,key,supported,widget in window.model_option_widgets:
                            assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    skills+=1
            assert window.run.state['config']=={} and window.run.state['history']==[]
            assert skills==87 and base_unknown==1 and river_unknown==3 and references==6
            assert not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.35.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'panel_scenarios':skills*2,'secondary_section_scenarios':2,
                'base_partial_sections':base_unknown,'river_partial_sections':river_unknown,
                'river_reference_sections':references,'unrelated_sections_hidden':True,
                'native_options_appropriate':True,'event_input_absent':True,'private_data_isolated':True,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                    for n in ('rouge/app.py','rouge/reporting.py','rouge/elemental_relics.py','scripts/verify_neural_sources_ui_035.py')}}
            (ROOT/'UI_0.35_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','skills_checked','panel_scenarios',
                'base_partial_sections','river_partial_sections','private_data_isolated')}))
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
