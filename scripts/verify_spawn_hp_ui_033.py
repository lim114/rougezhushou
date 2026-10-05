"""87 skill-panel checks in temporary settings without capture/chat actions."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from tests.test_spawn_hp_033 import COFFEE,PICTURE


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
        skills=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_1_2'))
            chosen=next(i for i in range(window.target_enemy.count())
                if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_1093_ccsbr')
            window.target_enemy.setCurrentIndex(chosen)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill));select({COFFEE})
                    r=window.damage_result['result'];text=window.damage_text.toPlainText()
                    prediction=r['run_resolution']['enemy']['spawn_hp']
                    assert prediction['current_variant'] is None
                    assert prediction['triggered_max_hp']==prediction['untriggered_max_hp']*2
                    assert '猎犬咖啡出生生命分支' in text and '单个敌人出生触发概率：3 %' in text
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    select({COFFEE,PICTURE})
                    assert window.damage_result['result']['run_resolution']['enemy']['spawn_hp']['triggered_max_hp'] is None
                    assert '触发的生命参考：未知' in window.damage_text.toPlainText()
                    assert '单件猎犬咖啡强化生命参考' in window.damage_text.toPlainText()
                    select({PICTURE});assert '猎犬咖啡出生生命分支' not in window.damage_text.toPlainText()
                    skills+=1
            select({COFFEE});window.target_enemy.setCurrentIndex(0)
            assert '猎犬咖啡出生生命分支' not in window.damage_text.toPlainText()
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert window.run.state['config']=={} and window.run.state['history']==[]
            assert skills==87 and not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.33.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'spawn_variant_sections':87,'hp_combination_unknown_sections':87,
                'unrelated_sections_hidden':True,'native_options_appropriate':True,
                'no_spawn_input_or_sampling':True,'event_input_absent':True,'private_data_isolated':True,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                    for n in ('rouge/app.py','rouge/reporting.py','rouge/run_modifiers.py','scripts/verify_spawn_hp_ui_033.py')}}
            (ROOT/'UI_0.33_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','skills_checked','spawn_variant_sections',
                'hp_combination_unknown_sections','private_data_isolated')}))
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
