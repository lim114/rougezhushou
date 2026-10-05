"""Public Qt sample/calculation path, plus all skill/wine reference combinations."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json,sys,time,tempfile,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import cv2,numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import rouge.app as app_module
from rouge.app import MainWindow
from rouge.recognition import ScreenReader
from rouge.damage import calculate_damage
from rouge.catalog import catalog

with tempfile.TemporaryDirectory() as directory:
    app_module.OPERATOR_STATE=Path(directory)/'operator-state.json'
    app_module.RUN_STATE=Path(directory)/'run-state.json'
    app=QApplication([]);window=MainWindow();reader=ScreenReader()
    try:
        for name in ('run-relic-multicard.png','run-relic-multicard-closed.png'):
            image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,dtype=np.uint8),cv2.IMREAD_COLOR)
            observed=reader.read(image);observed['captured_at']=time.time()
            window.sample_received((image,observed))
            assert set(window.run.held_relic_ids())=={'rogue_6_relic_cargo_1','rogue_6_relic_fight_26'}
            assert window.run.held_tool_ids()==['rogue_6_active_tool_5']
        status=window.run.inventory_status()
        assert status['complete'] and status['total_badge_count']==3 and status['expected_count']==2
        assert '支援防暴桩' in window.run_summary.text() and '3 / 3' in window.run_summary.text()
        assert 'rogue_6_active_tool_5' not in window.damage_result['scenario']['relic_ids']
        window.operator.setCurrentIndex(window.operator.findData('mechanist'))
        window.skill.setCurrentIndex(window.skill.findData(1))
        window.auto_relics.setChecked(False)
        window.relic_list.blockSignals(True)
        for i in range(window.relic_list.count()):
            item=window.relic_list.item(i)
            item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_legacy_97' else Qt.CheckState.Unchecked)
        window.relic_list.blockSignals(False)
        window.calculate()
        assert window.damage_result and '预计回转：' in window.damage_text.toPlainText()
        assert '（相位范围）' in window.damage_text.toPlainText()
        assert window.damage_result['result']['estimate']['skill']['cycle_dps_range']['lower']>0
        assert window.run.inventory_status()==status
        print('Qt: expanded/collapsed3-item inventory, separate tool, automatic calculation, wine range display passed',flush=True)
    finally:window.close()

cases=phase_cases=0
for op,profile in catalog()['operators'].items():
    for number,skill in enumerate(profile['skills'],1):
        for wine in ('rogue_6_relic_legacy_95','rogue_6_relic_legacy_96','rogue_6_relic_legacy_97'):
            result=calculate_damage({'operator':op,'skill':number,'relic_ids':[wine]})
            for key,value in result['estimate']['skill'].items():
                if key.endswith('_range'):
                    assert math.isfinite(value['lower']) and math.isfinite(value['upper'])
                    assert 0<=value['lower']<=value['upper'],(op,number,wine,key,value)
            if 'phase_estimate' in result['relic_resolution']:
                assert skill['levels'][9]['sp_type'] in ('INCREASE_WHEN_ATTACK','INCREASE_WHEN_TAKEN_DAMAGE')
                assert not result['relic_resolution']['phase_estimate']['verified_phase']
                phase_cases+=1
            cases+=1
receipt={'verified_at':time.time(),'version':'0.11.0','qt_public_path_verified':True,
    'expanded_and_collapsed_inventory_verified':True,'total_items':3,'relics':2,'tactical_tools':1,
    'tactical_tools_excluded_from_damage_relics':True,'wine_range_visible_in_ui':True,
    'skill_wine_combinations':cases,'applicable_phase_envelopes':phase_cases,
    'phase_and_hidden_blocking_script_live_verified':False,'chat_requests':0,
    'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
        ('rouge/damage.py','rouge/timing.py','rouge/relics.py','rouge/estimate.py','rouge/operator_engine.py',
         'rouge/reporting.py','rouge/run_state.py','rouge/run_recognition.py','rouge/relic_recognition.py','rouge/app.py')}}
(ROOT/'BATCH_0.11_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False),flush=True)
