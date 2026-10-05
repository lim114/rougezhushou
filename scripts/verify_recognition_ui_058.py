"""Actual readers through Qt's public sampling seam, with temporary state only."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from copy import deepcopy
import hashlib,json,sys,tempfile,time
from pathlib import Path
import cv2,numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication
from rouge.recognition import ScreenReader
from rouge.visual_recognition import VisualReader


def source_hashes():
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
           *[p for folder in ('page-features','visual-anchors')
             for p in (ROOT/'rouge/data'/folder).iterdir() if p.is_file()],
           Path(__file__),ROOT/'scripts/verify_relic_ui_025.py',
           ROOT/'samples/native-client/operator-mechanist.png']
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def main():
    started=time.perf_counter();checks=[];before=source_hashes()
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        try:
            assert window.windowTitle()=='黑流树海助手 0.58 · 识别与计算测试版'
            adaptive=window.recognition_mode.findData('adaptive')
            assert adaptive>=0
            assert window.recognition_mode.itemText(adaptive)=='视觉判页与区域 OCR'
            assert window.recognition_mode.currentData()=='adaptive'
            checks.append({'scope':'hybrid_mode_choice','data':'adaptive','label':'视觉判页与区域 OCR'})
            path=ROOT/'samples/native-client/operator-mechanist.png'
            image=cv2.imdecode(np.fromfile(path,np.uint8),1)
            def deliver(frame,result):
                result['captured_at']=time.time()
                window.sample_received((frame,result));app.processEvents()
            reader=ScreenReader()
            full=reader.read(image);deliver(image,full)
            state=window.operator_observations['mechanist']
            assert state['fields']['level']==90 and state['fields']['elite']==2
            assert '动态OCR' in window.capture_status.text()
            assert full['performance']['routing']['strategy']=='visual_region_ocr'
            assert full['performance']['ocr']['complete_current_texts'] is True
            assert '页面区域优先' in window.capture_status.text()
            checks.append({'scope':'real_ocr_current_cultivation','level':90,'elite':2,
                'routing':'visual_region_ocr','current_detector_texts_complete':True})
            deliver(image,reader.read(image.copy()))
            assert '静帧精确复用' in window.capture_status.text()
            checks.append({'scope':'ocr_exact_frame_status'})
            window.recognition_mode.setCurrentIndex(window.recognition_mode.findData('visual'))
            pure=VisualReader();partial=pure.read(image);deliver(image,partial)
            assert partial['operator']['fields']=={'potential':6}
            assert not partial['operator']['complete'] and partial['performance']['ocr_model_calls']==0
            assert window.operator_observations['mechanist']['fields']['level']==90
            assert '以前已确认记录' in window.operator_summary.toPlainText()
            assert '纯视觉' in window.capture_status.text()
            checks.append({'scope':'visual_partial_fields_account_history_retained','ocr_calls':0})
            cached=pure.read(image.copy());deliver(image,cached)
            assert '静帧精确复用' in window.capture_status.text() and '纯视觉' in window.capture_status.text()
            checks.append({'scope':'visual_exact_frame_status'})
            blank=np.full((720,1280,3),8,np.uint8)
            unknown=pure.read(blank);deliver(blank,unknown)
            assert unknown['operator'] is None and unknown['run'] is None
            assert window.operator_observations['mechanist']['fields']['level']==90
            checks.append({'scope':'unsupported_current_page_no_fabricated_fields'})
            assert window.run.state['history']==[] and window.run.state['config']=={}
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            after=source_hashes()
            changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
            assert not changed,changed
            receipt={'version':'0.58.0','passed':True,'verified_at':time.time(),'checks':checks,
                'real_reader_results_used':True,'private_state_isolated':True,'game_actions':0,'chat_requests':0,
                'sample_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'elapsed_seconds':time.perf_counter()-started,
                'source_sha256':before,'source_sha256_after':after,'source_drift':changed,'runner_sealed':True}
            with (ROOT/'RECOGNITION_UI_0.58_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks),'elapsed_seconds':receipt['elapsed_seconds']}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':main()
