"""87-skill isolated Qt conformance without game/chat/private settings access."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt


def main():
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        def select(rids):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in rids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False);window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
        skills=tanks=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None and not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op));window.skill.setCurrentIndex(window.skill.findData(skill))
                    select({'rogue_6_relic_book_3'})
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    actual='首次部署费用参考' in window.damage_text.toPlainText()
                    assert actual==(profile['profession']=='tank'),(op,skill,actual)
                    if actual:
                        tanks+=1
                        assert '实际部署扣费：未知' in window.damage_text.toPlainText() and '后续部署' in window.damage_text.toPlainText()
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    select({'rogue_6_relic_cargo_2'})
                    assert window.damage_form.isRowVisible(window.relic_context)
                    assert 'parts_count' in window.relic_context.placeholderText() and '99' in window.relic_context.toolTip()
                    window.relic_context.setPlainText('{"parts_count":10000}')
                    assert window.damage_result and '计数上限，按99' in window.damage_text.toPlainText()
                    select({'rogue_6_relic_fight_6'})
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    assert not window.damage_result['scenario']['relic_context']
                    assert 'parts_count' not in json.dumps(window.run.state)
                    skills+=1
            window.operator.setCurrentIndex(window.operator.findData('mechanist'));window.skill.setCurrentIndex(window.skill.findData(3))
            select({'rogue_6_relic_book_3','rogue_6_relic_fight_11'})
            first=window.damage_result['result']['deployment_reference']['first_deployment_cost']
            assert first['combined_reference'] is None
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert '本次事件前当前生命参考' not in window.damage_text.toPlainText()
            assert skills==87 and not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.31.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'tank_first_cost_skill_cases':tanks,'non_tank_fee_panel_hidden':True,'native_options_appropriate':True,
                'parts_input_scoped_and_capped':True,'combined_fee_unknown':True,'event_input_absent':True,
                'temporary_context_not_saved':True,'private_data_isolated':True,'game_actions':0,'chat_requests':0,
                'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                    ('rouge/app.py','rouge/reporting.py','rouge/deployment.py','scripts/verify_offline_relic_ui_031.py')}}
            (ROOT/'UI_0.31_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(receipt,ensure_ascii=False))
        finally:
            window.close();app.processEvents()


if __name__=='__main__':main()
