"""87 isolated skill panels: partial elemental metrics and appropriate fields."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib,json,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from tests.test_neural_relic_034 import RIVER


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
        skills=references=partial=0
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill));select({RIVER})
                    r=window.damage_result['result'];text=window.damage_text.toPlainText()
                    reference=r.get('neural_relic_reference');subtotal=r.get('known_damage_subtotals')
                    assert ('河谷祭祈 · 神经爆发参考' in text)==bool(reference),(op,skill)
                    assert ('已建模伤害小计' in text)==bool(subtotal),(op,skill)
                    if reference:
                        assert '额外持续伤害首跳时刻：未知' in text
                        assert not reference['periodic_damage_scheduled'];references+=1
                    if subtotal:
                        assert not r['complete'] and not r['estimate']['complete']
                        for phase,fields in {'cast':('total_damage','phase_damage'),
                            'window':('window_dps',),'cycle':('cycle_damage','cycle_dps')}.items():
                            if reference['affected_damage_phases'][phase]:
                                assert all(r['estimate']['skill'][field] is None for field in fields),(op,skill,phase)
                        partial+=1
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    select(set());text=window.damage_text.toPlainText()
                    assert '河谷祭祈 · 神经爆发参考' not in text and '已建模伤害小计' not in text
                    skills+=1
            assert window.run.state['config']=={} and window.run.state['history']==[]
            assert skills==87 and not window.desktop.process and not window.auto.isChecked()
            receipt={'version':'0.34.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'neural_reference_sections':references,'partial_damage_sections':partial,
                'unrelated_sections_hidden':True,'native_options_appropriate':True,
                'no_periodic_tick_input_or_sampling':True,'event_input_absent':True,'private_data_isolated':True,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
                    for n in ('rouge/app.py','rouge/reporting.py','rouge/elemental_relics.py','scripts/verify_neural_ui_034.py')}}
            (ROOT/'UI_0.34_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({k:receipt[k] for k in ('passed','skills_checked','neural_reference_sections',
                'partial_damage_sections','private_data_isolated')}))
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
