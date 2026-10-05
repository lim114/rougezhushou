"""Exercise actual Qt controls with isolated offline HP branch fixtures."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from PySide6.QtGui import QFont,QFontDatabase
from rouge.run_config import config_data

COFFEE='rogue_6_relic_fight_25';DRAGON='rogue_6_start_3';PROBE='rogue_6_relic_fight_30'
HAND='rogue_6_relic_hand_4';PICTURE='rogue_6_relic_legacy_84'

def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    start=time.perf_counter();out=ROOT/'.cache/relic-composition-052';out.mkdir(exist_ok=True)
    names=('rouge/app.py','rouge/relics.py','rouge/reporting.py','rouge/run_modifiers.py',
           'rouge/data/relic-mechanics.json','scripts/verify_relic_composition_ui_052.py')
    hashes={n:sha(n) for n in names};cases=[];screenshots={}
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder);module.RUN_STATE=root/'run.json';module.OPERATOR_STATE=root/'operators.json';module.SETTINGS=root/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(root/'chat',callback)
        app=QApplication([])
        font=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'));assert font>=0
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(font)[0],9))
        window=OfflineWindow();window.resize(1300,1000);window.show();window.centralWidget().setCurrentIndex(1)
        def selected(ids,context=None):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.relic_context.blockSignals(True)
            window.relic_context.setPlainText(json.dumps(context) if context is not None else '')
            window.relic_context.blockSignals(False);window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
            return window.damage_result['result']
        def image(name):
            window.damage_text.moveCursor(window.damage_text.textCursor().MoveOperation.Start)
            assert window.damage_text.find('【猎犬咖啡出生生命分支】')
            app.processEvents();path=out/name;assert window.grab().save(str(path))
            screenshots[path.relative_to(ROOT).as_posix()]=sha(path.relative_to(ROOT))
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            window.auto_relics.setChecked(False)
            for op in module.catalog()['operators']:
                window.select_operator(op)
                window.skill.setCurrentIndex(window.skill.findData(1))
                result=selected({HAND})
                assert result['relic_resolution']['records'][0]['status']=='inapplicable'
                assert '慑空之手：未覆盖' not in window.damage_text.toPlainText()
                assert not window.damage_form.isRowVisible(window.relic_context)
                cases.append({'case':'hand_wrong_branch','operator':op,'passed':True})
            window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3))
            window.run.apply({'config':{'difficulty':{'value':4,'source':'isolated_test'},
                'zone':{'id':'zone_1','name':config_data()['zones']['zone_1']['name'],'source':'isolated_test'}}},
                window.run.state['started_at']+1)
            window.target_stage_choices.select_value('ro6_n_1_2')
            target=next(window.target_enemy.itemData(i) for i in range(window.target_enemy.count())
                if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2137_shsdgo')
            window.target_enemy_choices.select_value(target)
            baseline=selected(set())['run_resolution']['enemy']['stats']['maxHp']
            for ids,context,factor,label in [
                ({COFFEE,DRAGON},{'entered_zone_count':1},.5,'coffee_dragon'),
                ({COFFEE,PROBE},{'probe_stacks':2},1.4,'coffee_probe'),
                ({COFFEE,DRAGON,PROBE},{'entered_zone_count':1,'probe_stacks':2},.7,'both_final_scalers')]:
                result=selected(ids,context);spawn=result['run_resolution']['enemy']['spawn_hp']
                assert abs(spawn['untriggered_max_hp']-baseline*factor)<1e-7
                assert abs(spawn['triggered_max_hp']-baseline*factor*2)<1e-7
                assert not spawn['excluded_hp_sources'] and spawn['current_variant'] is None
                assert '已核对的最终生命倍率' in window.damage_text.toPlainText()
                assert '未观测当前出生分支' in window.damage_text.toPlainText()
                assert window.damage_form.isRowVisible(window.relic_context)
                cases.append({'case':label,'untriggered_hp':spawn['untriggered_max_hp'],
                              'triggered_hp':spawn['triggered_max_hp'],'passed':True})
            image('known-composition.png')
            saved=window.target_enemy.currentData();text=window.relic_context.toPlainText()
            for _ in range(3):window.calculate()
            window.damage_technical.setChecked(True);window.damage_technical.setChecked(False)
            assert window.target_enemy.currentData()==saved and window.relic_context.toPlainText()==text
            assert '已核对的最终生命倍率' in window.damage_text.toPlainText()
            cases.append({'case':'recalculation_keeps_target_and_context','passed':True})
            for ids,context,blocked,label in [
                ({COFFEE,PROBE},None,PROBE,'missing_probe_counter'),
                ({COFFEE,DRAGON},None,DRAGON,'missing_dragon_counter'),
                ({COFFEE,PROBE,PICTURE},{'probe_stacks':2},PICTURE,'unknown_hp_script')]:
                result=selected(ids,context);spawn=result['run_resolution']['enemy']['spawn_hp']
                assert spawn['triggered_max_hp'] is None and spawn['excluded_hp_sources']==[blocked]
                assert '复合触发生命值保持未知' in window.damage_text.toPlainText()
                cases.append({'case':label,'passed':True})
            image('unknown-composition.png')
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert not (root/'chat').exists() and not (root/'settings.json').exists()
            assert all('probe_stacks' not in json.dumps(v) and 'entered_zone_count' not in json.dumps(v)
                       for v in window.run.state.get('resources',{}).values())
            assert hashes=={n:sha(n) for n in names}
            receipt={'version':'0.52.0','passed':True,'cases':cases,'screenshots':screenshots,
                'source_sha256':hashes,'private_state_isolated':True,'game_captures':0,'game_actions':0,'chat_requests':0,
                'no_automatic_counter_reading_claim':True,'seconds':time.perf_counter()-start}
            (ROOT/'RELIC_UI_0.52_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({'passed':True,'cases':len(cases),'screenshots':len(screenshots)}))
        except Exception:
            i=len(list(out.glob('failed-*.json')))+1
            (out/f'failed-{i}.json').write_text(json.dumps({'passed':False,'cases_completed':cases,
                'traceback':traceback.format_exc(),'source_sha256':hashes},ensure_ascii=False,indent=2),encoding='utf-8')
            raise
        finally:window.close();app.processEvents()

if __name__=='__main__':main()
