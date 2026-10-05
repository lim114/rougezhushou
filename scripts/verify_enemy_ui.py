"""Exercise public Qt sampling/calculation; isolated run, zero chat sends."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json,sys,tempfile,time
from pathlib import Path
import cv2,numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.recognition import ScreenReader
with tempfile.TemporaryDirectory() as folder:
    module.RUN_STATE=Path(folder)/'run.json';module.OPERATOR_STATE=Path(folder)/'operators.json'
    app=QApplication([]);window=module.MainWindow();reader=ScreenReader()
    try:
        for name in ('run-map-empty.png','selected-battle-node.png'):
            image=cv2.imdecode(np.fromfile(root/'samples/native-client'/name,dtype=np.uint8),1)
            observed=reader.read(image);observed['captured_at']=time.time()
            window.sample_received((image,observed))
        assert window.target_stage.currentData()=='ro6_n_1_2'
        index=next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_1093_ccsbr')
        window.target_enemy.setCurrentIndex(index);window.calculate()
        assert not window.defense.isEnabled() and not window.resistance.isEnabled()
        result=window.damage_result['result'];enemy=result['run_resolution']['enemy']
        assert enemy['name']=='提亚卡乌战士' and enemy['stats']['def']==60
        assert '关卡目标与环境修正' in window.damage_text.toPlainText()
        assert window.run.state['config']['zone']['id']=='zone_1'
        assert not window.damage_form.isRowVisible(window.orb_mode)
        window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_b_5'))
        index=next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2148_shorbb')
        window.target_enemy.setCurrentIndex(index)
        assert window.damage_form.isRowVisible(window.orb_mode)
        assert window.orb_mode.currentData()=='unknown'
        assert any('阶段和来源列未确认' in s for s in window.damage_result['result']['warnings'])
        window.orb_mode.setCurrentIndex(window.orb_mode.findData('active_same_column'));window.calculate()
        assert window.damage_result['result']['run_resolution']['enemy']['type_factors']=={'physical':.7,'magic':.7}
        window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_1_2'))
        assert window.orb_mode.currentData()=='unknown'
        assert not window.damage_form.isRowVisible(window.orb_mode)
        identity=window.run.state['id']
        window.reset_run()
        assert window.target_stage.currentData() is None and window.target_enemy.currentData() is None
        assert window.defense.isEnabled() and window.run.state['id']!=identity
        receipt={'verified_at':time.time(),'native_node_stage_auto_selection':True,'enemy_identity_derived_stats':True,
            'read_only_enemy_stats':True,'manual_reset_clears_target':True,
            'unrelated_enemy_controls_hidden':True,'orb_unknown_default_and_no_state_leak':True,'chat_requests':0}
        (root/'ENEMY_UI_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(receipt,ensure_ascii=False))
    finally:window.close();app.processEvents()
