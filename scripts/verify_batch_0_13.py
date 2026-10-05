"""Public calculation + Qt sampling checks; isolated memory, zero chats."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys,json,time,tempfile
from pathlib import Path
import cv2,numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.run_state import RunState
from rouge.recognition import ScreenReader
from PySide6.QtWidgets import QApplication
import rouge.app as module

skills=0
for op,profile in catalog()['operators'].items():
    for number in range(1,len(profile['skills'])+1):
        base={'operator':op,'skill':number,'elite':2,'potential':1,'trust':100,'skill_rank':10,'timing_mode':'frames'}
        plain=calculate_damage(base)
        spear=calculate_damage({**base,'run_config':{'squad':{'id':'rogue_6_band_6','effect_verified':True}}})
        assert spear['run_resolution']['applied']
        assert spear['estimate']['base_stats']['attack']>plain['estimate']['base_stats']['attack']
        assert any(s['id']=='run_environment' for s in spear['report']['sections'])
        skills+=1
assert skills==87
variants=0
with tempfile.TemporaryDirectory() as directory:
    for group in config_data()['difficulty_upgrade_relic_groups'].values():
        base=group['relicData'][0]['relicId']
        for grade,suffix in [(0,''),(2,''),(3,'_a'),(5,'_a'),(6,'_b'),(8,'_b'),(9,'_c'),(15,'_c')]:
            memory=RunState(Path(directory)/'temporary-unused.json')
            icon={'id':base,'candidates':[base,base+'_a',base+'_b',base+'_c'],'confirmed':False}
            observed={'config':{'difficulty':{'value':grade}},'relics':{'ids':[],'count':1,'icons':[icon],'source':'held_bar'},'operators':[]}
            memory.apply(observed,time.time())
            assert memory.held_relic_ids()==[base+suffix],(grade,base,memory.held_relic_ids())
            assert memory.inventory_status()['complete'];variants+=1

with tempfile.TemporaryDirectory() as directory:
    module.RUN_STATE=Path(directory)/'run.json';module.OPERATOR_STATE=Path(directory)/'operators.json'
    app=QApplication([]);window=module.MainWindow();reader=ScreenReader()
    try:
        image=cv2.imdecode(np.fromfile(root/'samples/native-client/run-map-empty.png',dtype=np.uint8),1)
        observed=reader.read(image,client_rect=[2,45,2050,1125]);observed['captured_at']=time.time()
        window.sample_received((image,observed))
        assert window.run.inventory_status()['complete'] and window.run.inventory_status()['expected_count']==0
        assert '0 / 0 件' in window.run_summary.text()
        assert window.damage_result['scenario']['run_config']['difficulty']['value']==10
        assert window.damage_result['result']['run_resolution']['difficulty']['value']==10
        assert '敌方难度/区域/关卡修正尚未自动计算' in window.damage_text.toPlainText()
        run_id=window.run.state['id']
        image=cv2.imdecode(np.fromfile(root/'samples/native-client/run-info-trade.png',dtype=np.uint8),1)
        observed=reader.read(image,client_rect=[2,45,2050,1125]);observed['captured_at']=time.time()
        window.sample_received((image,observed))
        assert window.run.state['config']['squad']['id']=='rogue_6_band_20'
        assert window.run.state['id']==run_id
        assert window.desktop_context()['run_state']['config']['squad']['id']=='rogue_6_band_20'
        window.run.save();restored=RunState(module.RUN_STATE)
        assert restored.state['id']==run_id and restored.inventory_status()['complete']
        receipt={'version':'0.13.0','verified_at':time.time(),'spear_skill_profiles':skills,'difficulty_tier_cases':variants,
                 'qt_empty_inventory_and_auto_config':True,'same_run_and_restart':True,'chat_requests':0,
                 'source':config_data()['source_url'],'limits':['槽位/强化版本为公开观测入口回放验证，并非全部变体实机识别率。','敌方难度修正未自动套用。']}
        (root/'BATCH_0.13_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(receipt,ensure_ascii=False))
    finally:window.close();app.processEvents()
