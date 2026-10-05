"""Exercise the real automatic capture -> OCR -> read-only Qt report path.

Requires the authorized game window on an operator page. Sends no chat message.
"""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import win32gui
from PySide6.QtWidgets import QApplication, QLabel
from rouge.app import MainWindow
from rouge.catalog import operator_profiles,catalog

root=Path(__file__).resolve().parents[1]
app=QApplication([])
before=win32gui.GetForegroundWindow()
started=time.time()
window=MainWindow()
latest={}
window.events.sample.connect(lambda result:latest.update(image=result[0]))
try:
    window.auto.setChecked(True)
    deadline=time.monotonic()+35
    complete_frames=set()
    while time.monotonic()<deadline:
        app.processEvents()
        if window.observation and window.observation.get('operator') and not window.busy:
            op=window.observation['operator']
            if op.get('complete'):
                complete_frames.add(window.observation['captured_at'])
                if len(complete_frames)>=2:break
        time.sleep(.02)
    window.auto.setChecked(False)
    if not window.observation or not window.observation.get('operator'):
        raise RuntimeError('未取得新的干员页识别：'+window.capture_status.text())
    observed=window.observation
    assert observed['captured_at']>=started
    assert len(complete_frames)>=2,'Continuous sampling must read more than one fresh complete frame'
    operator=observed['operator']
    fields=operator['fields']
    if not operator.get('complete'):
        import cv2
        (root/'.cache/auto-operator-page.png').write_bytes(cv2.imencode('.png',latest['image'])[1].tobytes())
        (root/'.cache/auto-operator-page.json').write_text(json.dumps(observed,ensure_ascii=False,indent=2),encoding='utf-8')
        raise RuntimeError('本帧培养信息仍不完整：'+json.dumps(operator,ensure_ascii=False))
    assert window.level.value()==fields['level']
    if operator['id'] in catalog()['operators']:
        assert window.damage_result
        assert window.damage_result['scenario']['potential']==fields['potential']
        assert 'base_attack' not in window.damage_result['scenario']
    else:assert not window.damage_result
    readonly=all(isinstance(field,QLabel) for field in (window.elite,window.trust,window.potential,window.module,window.rank,window.attack))
    receipt={'captured_at':observed['captured_at'],'fresh_capture':True,'complete_frames':len(complete_frames),
        'foreground_unchanged':before==win32gui.GetForegroundWindow(),
        'game_in_background':window.capture.target['hwnd']!=before,
        'operator':operator['name'],'fields':fields,'skill_ranks':operator['skill_ranks'],
        'page':observed['page'],'missing_fields':operator['missing_fields'],'all_required_fields_read':True,
        'readonly_cultivation':readonly,'automatically_applied':True,'chat_requests':0,
        'limits':operator.get('limitations',[])}
    assert receipt['foreground_unchanged'] and readonly
    (root/'OPERATOR_AUTO_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    (root/f'OPERATOR_{operator["id"]}_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
finally:
    window.close()
