"""Replay arbitrary frame geometry through reader and Qt without game input/chat."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys,json,time,tempfile
from pathlib import Path
import cv2,numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from rouge.recognition import ScreenReader
from PySide6.QtWidgets import QApplication
import rouge.app as module
source=cv2.imdecode(np.fromfile(root/'samples/native-client/run-info-trade.png',dtype=np.uint8),1)[45:-2,2:-2]
reader=ScreenReader();rows=[]
with tempfile.TemporaryDirectory() as folder:
    module.RUN_STATE=Path(folder)/'run.json';module.OPERATOR_STATE=Path(folder)/'operator.json'
    app=QApplication([]);window=module.MainWindow()
    try:
        for width,height in [(1280,720),(1920,1080),(2560,1440),(1024,768),(1379,829)]:
            factor=min(width/source.shape[1],height/source.shape[0])
            cw,ch=round(source.shape[1]*factor),round(source.shape[0]*factor)
            resized=cv2.resize(source,(cw,ch),interpolation=cv2.INTER_AREA if factor<1 else cv2.INTER_CUBIC)
            left,top=(width-cw)//2,(height-ch)//2
            frame=cv2.copyMakeBorder(resized,top,height-ch-top,left,width-cw-left,cv2.BORDER_CONSTANT,value=0)
            observed=reader.read(frame);config=observed['run']['config']
            assert config['difficulty']['value']==10,(width,height,config)
            assert config['squad']['id']=='rogue_6_band_20',(width,height,config)
            observed['captured_at']=time.time();window.sample_received((frame,observed))
            assert window.difficulty.currentData()==10 and not window.difficulty.isEnabled()
            assert '多边贸易分队（强化）' in window.run_summary.text()
            assert window.desktop_context()['run_state']['config']['difficulty']['value']==10
            rows.append({'frame_size':[width,height],'viewport':observed['viewport'],'difficulty':10,'squad':'rogue_6_band_20'})
            print(width,height,'reader + Qt + analysis context passed',flush=True)
        prior=window.run.state['id'];history=len(window.run.state['history'])
        window.apply_run_observation({'relics':{'count':None,'ids':[],'icons':[],'source':'held_bar'},'operators':[]},time.time())
        assert window.run.state['id']==prior and len(window.run.state['history'])==history
        assert window.difficulty.currentData()==10 and not window.difficulty.isEnabled()
        window.run.save();restored=module.RunState(module.RUN_STATE)
        assert restored.state['config']['squad']['id']=='rogue_6_band_20'
        window.reset_run();assert window.difficulty.isEnabled() and window.run.state['config']=={}
        receipt={'verified_at':time.time(),'cases':rows,'same_run_memory_and_restart':True,
                 'manual_reset_only':True,'qt_autofill_and_context':True,'chat_requests':0,
                 'scope':'captured real layout resized continuously; black padding changes; physical-client cropping'}
        (root/'RESOLUTION_0.12_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:window.close();app.processEvents()
