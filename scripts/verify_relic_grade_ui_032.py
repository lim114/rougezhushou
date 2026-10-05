"""Isolated Qt grade correction and all-skill option conformance."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from tests.test_relic_grade_sync_032 import icon,bar,grade,BASE


def main():
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        try:
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            at=window.run.state['started_at']+1
            window.operator.setCurrentIndex(window.operator.findData('mechanist'))
            window.skill.setCurrentIndex(window.skill.findData(1))
            window.apply_run_observation(bar([icon()],1),at)
            assert window.run.held_relic_ids()==[] and not window.run.inventory_status()['complete']
            window.apply_run_observation(grade(10),at+1)
            assert window.run.held_relic_ids()==[BASE+'_c'] and window.run.inventory_status()['complete']
            assert window.damage_result['scenario']['relic_ids']==[BASE+'_c']
            assert '混沌化' in window.run_summary.text()
            old_history=copy.deepcopy(window.run.state['history'])
            window.apply_run_observation(grade(3),at+2)
            assert window.run.held_relic_ids()==[BASE+'_a']
            assert window.damage_result['scenario']['relic_ids']==[BASE+'_a']
            assert window.damage_result['scenario']['run_config']['difficulty']['value']==3
            assert window.run.state['history'][:len(old_history)]==old_history
            assert '半结构化' in window.run_summary.text()
            assert not window.difficulty.isEnabled()
            skills=0
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill));window.calculate()
                    assert window.damage_result,window.damage_text.toPlainText()
                    assert window.damage_result['scenario']['relic_ids']==[BASE+'_a']
                    assert not hasattr(window,'received_sp_scenario')
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    skills+=1
            window.reset_run()
            assert not window.run.held_relic_ids() and window.run.state['relic_icon_memory'] is None
            assert window.difficulty.isEnabled() and not window.run.recognition_context()['config']
            assert window.damage_result and not window.damage_result['scenario']['relic_ids']
            assert skills==87 and not window.desktop.process and not window.auto.isChecked()
            files=('rouge/app.py','rouge/run_state.py','rouge/relic_recognition.py','rouge/run_config.py',
                'scripts/verify_relic_grade_ui_032.py')
            receipt={'version':'0.32.0','passed':True,'verified_at':time.time(),'skills_checked':skills,
                'late_grade_updates_ui_and_calculation':True,'corrected_grade_replaces_tier_once':True,
                'tier_label_visible':True,'history_preserved':True,'reset_clears_run_context_and_icon_memory':True,
                'native_options_appropriate':True,'event_input_absent':True,'private_data_isolated':True,
                'game_actions':0,'chat_requests':0,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}}
            (ROOT/'UI_0.32_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(receipt,ensure_ascii=False))
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
