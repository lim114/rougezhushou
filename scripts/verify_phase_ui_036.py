"""Isolated Qt panels for base, neural and both periodic-phase inventories."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt

RIVER='rogue_6_relic_fight_22'
WINES=('rogue_6_relic_legacy_95','rogue_6_relic_legacy_97')


def main():
    started=time.perf_counter()
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
        skills=panels=range_panels=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill))
                    for ids in (set(),{RIVER},{WINES[0]},{WINES[1]}):
                        select(ids);r=window.damage_result['result'];text=window.damage_text.toPlainText()
                        secondary=op=='char_1042_phatm2' and skill==3
                        assert ('空剧场 · 持续损伤待核验' in text)==secondary,(op,skill,ids)
                        if secondary:
                            assert '当前情景损伤爆发次数：未知' in text
                            assert r['estimate']['skill']['total_damage'] is None
                            assert r['estimate']['skill']['cycle_damage'] is None
                        assert ('河谷祭祈 · 神经爆发参考' in text)==bool(r.get('neural_relic_reference'))
                        assert ('已建模伤害小计' in text)==bool(r.get('known_damage_subtotals'))
                        if 'phase_estimate' in r['relic_resolution']:
                            assert ids in ({WINES[0]},{WINES[1]})
                            assert not r['relic_resolution']['phase_estimate']['verified_phase']
                            assert '相位范围' in text
                            range_panels+=1
                        assert not window.damage_form.isRowVisible(window.relic_context)
                        for owner,key,supported,widget in window.model_option_widgets:
                            assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                        panels+=1
                    skills+=1
            assert skills==87 and panels==348
            assert window.run.state['config']=={} and window.run.state['history']==[]
            assert not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.36.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'panel_scenarios':panels,'wine_phase_panels':range_panels,
                'unrelated_sections_hidden':True,'native_options_appropriate':True,
                'event_input_absent':True,'private_data_isolated':True,'elapsed_seconds':time.perf_counter()-started,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                    for n in ('rouge/app.py','rouge/damage.py','scripts/verify_phase_ui_036.py')}}
            (ROOT/'UI_0.36_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','skills_checked','panel_scenarios',
                'wine_phase_panels','private_data_isolated','elapsed_seconds')}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
