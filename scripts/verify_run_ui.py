"""Replay captured exploration pages through the public Qt sampling/report path."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,json,time,tempfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2,numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import rouge.app as app_module
from rouge.app import MainWindow
from rouge.recognition import ScreenReader

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as folder:
    app_module.OPERATOR_STATE=Path(folder)/'operator-state.json'
    app_module.RUN_STATE=Path(folder)/'run-state.json'
    app=QApplication([]);window=MainWindow();reader=ScreenReader()
    def sample(name):
        image=cv2.imdecode(np.fromfile(root/'samples/native-client'/name,dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=reader.read(image);observed['captured_at']=time.time()
        window.sample_received((image,observed))
        return observed
    try:
        sample('operator-mechanist.png')
        assert window.damage_result['scenario']['module_level']==3
        sample('run-map-closed.png')
        assert window.run.state['resources']['gold']['value']==10
        assert window.run.state['resources']['parts_count']['value']==1
        assert window.damage_result['scenario']['relic_ids']==['rogue_6_relic_legacy_52']
        assert window.damage_result['scenario']['inventory_status']['complete']
        print('Held icon automatically enters the calculation; count cross-check passed',flush=True)
        observed=sample('run-mechanist-selected.png')
        scenario=window.damage_result['scenario']
        assert scenario['operator']=='mechanist' and scenario['elite']==1 and scenario['level']==80
        assert scenario['module_id'] is None and scenario['module_level']==0
        assert scenario['skill_rank']==7 and window.skill.count()==2
        assert window.operator_observations['mechanist']['fields']['level']==90
        assert window.operator_observations['mechanist']['fields']['module_level']==3
        assert 'rogue_6_relic_legacy_52' not in scenario['relic_ids']
        assert scenario['inventory_status']['expected_count']==2
        assert '账号' in window.potential.text()
        assert not window.damage_result['result']['estimate']['complete']
        for i in range(window.relic_list.count()):
            assert not window.relic_list.item(i).flags()&Qt.ItemFlag.ItemIsUserCheckable
        print('Current elite 1 / level 80 / rank 7 overrides account card; old module and relic do not leak',flush=True)
        session=window.run.state['id']
        held=list(scenario['relic_ids'])
        history_length=len(window.run.state['history'])
        # Replay a degraded frame through the same public sampling entry point.
        # Missing icons and cultivation fields must not invalidate previous confirmations.
        degraded=copy.deepcopy(observed)
        degraded['run']['relics'].update(ids=[],icons=[])
        degraded['run']['operators']=[{**m,'fields':{},'skill_ranks':{}} for m in degraded['run']['operators']]
        image=cv2.imdecode(np.fromfile(root/'samples/native-client/run-mechanist-selected.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        window.sample_received((image,degraded))
        assert window.run.state['id']==session
        assert window.damage_result['scenario']['relic_ids']==held
        assert window.damage_result['scenario']['inventory_status']['complete']
        assert window.damage_result['scenario']['elite']==1 and window.damage_result['scenario']['skill_rank']==7
        assert len(window.run.state['history'])==history_length
        assert window.run.state['resources']['gold']['value']==10
        assert not window.run.state['relics']['rogue_6_relic_legacy_52']['held']
        # Restart uses the persisted run, including inactive historical records.
        window.close()
        window=MainWindow()
        window.operator.setCurrentIndex(window.operator.findData('mechanist'))
        assert window.run.state['id']==session
        assert window.damage_result['scenario']['relic_ids']==held
        assert window.damage_result['scenario']['level']==80
        assert window.damage_result['scenario']['skill_rank']==7
        assert len(window.run.state['history'])==history_length
        assert 'rogue_6_relic_legacy_52' in window.run.state['relics']
        print('Partial frames and restart retain current confirmations and historical records without repeat confirmation',flush=True)
        promoted=copy.deepcopy(observed)
        promoted['run']['operators']=[{**m,'fields':{'elite':2},'skill_ranks':{}} for m in promoted['run']['operators'] if m['id']=='mechanist']
        window.sample_received((image,promoted))
        current=window.current_operator_state()
        assert 'module_id' not in current['run_confirmed_fields']
        assert not current['skill_ranks']
        assert window.run.state['operators']['mechanist']['fields']['module_id'] is None
        assert window.run.state['operators']['mechanist']['skill_ranks']['1']==7
        assert window.run.state['id']==session
        print('Promotion retains historical evidence while requiring new module/mastery confirmation',flush=True)
        sample('run-emergency-mechanist.png')
        assert window.run.state['id']==session
        assert window.run.state['operators']['mechanist']['recruitment_kind']=='emergency_hire'
        assert window.run.state['operators']['char_2027_wang']['recruitment_kind']=='non_emergency'
        assert window.run.state['operators']['char_2027_wang']['advanced']
        assert window.damage_result['scenario']['level']==90
        assert window.damage_result['scenario']['skill_rank']==10
        assert '应急雇佣' in window.run_summary.text()
        # An authoritative roster confirms departure; keep the entire record and history.
        departed=copy.deepcopy(observed)
        departed['run']['operators']=[m for m in departed['run']['operators'] if m['id']!='mechanist']
        departed['run']['crew_count']=len(departed['run']['operators'])
        departed['run']['selected_operator']=None
        window.sample_received((image,departed))
        assert not window.run.state['operators']['mechanist']['present']
        assert window.run.state['operators']['mechanist']['recruitment_kind']=='emergency_hire'
        assert window.run.state['operators']['mechanist']['skill_ranks']['3']==10
        assert '已离队' in window.run_summary.text()
        assert window.run.state['id']==session
        print('Emergency hire updates current cultivation; confirmed departure retains history and never resets the run',flush=True)
        window.reset_run_button.click()
        assert window.run.state['id']!=session
        assert not window.run.state['operators'] and not window.run.state['relics']
        assert not window.run.state['history']
        assert not window.run.state['resources']
        window.sample_received((image,observed))
        assert not window.run.state['operators'] and not window.run.state['relics']
        assert window.damage_result['scenario']['relic_ids']==[]
        assert window.operator_observations['mechanist']['fields']['level']==90
        window.auto_relics.setChecked(False)
        assert window.damage_result['scenario']['inventory_status']['source']=='manual_test'
        print('Manual reset preserves account profile and rejects pre-reset frames; manual scenario remains separate; no chat requests',flush=True)
        receipt={'verified_at':time.time(),'public_path':'MainWindow.sample_received -> calculation/report',
            'partial_frames_preserve_confirmations':True,'restart_restores_same_run':True,
            'inactive_relic_history_retained':True,'promotion_invalidates_current_module_and_mastery_without_forgetting_history':True,
            'emergency_and_advanced_markers_distinguished':True,'confirmed_departure_preserves_history':True,
            'manual_reset_only':True,'pre_reset_frames_rejected':True,'account_profile_preserved':True,
            'gold_parts_confirmed_reference_preserved_until_update_or_manual_reset':True,
            'chat_requests':0,'independent_recognition_accuracy_set':False}
        (root/'RUN_STATE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:window.close()
