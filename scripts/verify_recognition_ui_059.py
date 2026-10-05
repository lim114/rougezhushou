"""Actual readers and sealed current-worker recovery through isolated Qt.

The six original reader checks still execute their actual readers. Recovery
checks use verified actual OCR output from POPUP_RECOVERY, without another OCR
call. Missing or stale receipts are errors, never optional skipped checks.
"""
import argparse
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
from rouge.run_state import RunState
from verify_final_059 import popup_recovery_evidence

RECOVERY=ROOT/'POPUP_RECOVERY_0.59_VERIFICATION.json'
MYRTLE='char_151_myrtle'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def public_path(name):
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT) and '.local' not in path.relative_to(ROOT).parts,name
    return path


def current_public_sources():
    files=set((ROOT/'rouge').rglob('*.py'))|set((ROOT/'rouge/data').rglob('*.json'))
    for folder in ('page-features','visual-anchors'):
        files|={p for p in (ROOT/'rouge/data'/folder).rglob('*') if p.is_file()}
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)}


def load_recovery_fixture(popup_freeze):
    """Load mandatory hash-closed public fixtures, not runtime state."""
    evidence={};proof=popup_recovery_evidence(current_public_sources(),evidence,popup_freeze)
    worker=read(public_path(proof['current_worker']))
    image_path=public_path(proof['image'])
    image=cv2.imdecode(np.fromfile(image_path,np.uint8),1)
    assert image is not None and image.size
    frame=worker['frames'][0];observation=deepcopy(frame['observation'])
    assert observation['viewport']['source_size']==[image.shape[1],image.shape[0]]
    assert observation['operator'] is None
    observation['performance']=deepcopy(frame['performance'])
    return image,observation,sorted(public_path(name) for name in proof['fixture_sha256']),proof


def source_hashes(fixtures):
    files=[*(ROOT/'rouge').rglob('*.py'),*(ROOT/'rouge/data').rglob('*.json'),
           *[p for folder in ('page-features','visual-anchors')
             for p in (ROOT/'rouge/data'/folder).iterdir() if p.is_file()],
           Path(__file__),ROOT/'scripts/verify_final_059.py',ROOT/'scripts/verify_relic_ui_025.py',
           ROOT/'samples/native-client/operator-mechanist.png',*fixtures]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def main(popup_freeze):
    started=time.perf_counter();checks=[]
    recovery_image,recovery_observation,fixtures,recovery_evidence=load_recovery_fixture(popup_freeze)
    before=source_hashes(fixtures)
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(p/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        try:
            assert window.windowTitle()=='黑流树海助手 0.59 · 识别与计算测试版'
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
            assert len(checks)==6

            # A real current-worker result from the independent recovery run
            # crosses the same public UI seam. Only delivery time is fresh.
            account_before=deepcopy(window.operator_observations)
            account_file_before=module.OPERATOR_STATE.read_bytes()
            deliver(recovery_image,deepcopy(recovery_observation))
            member=window.run.state['operators'][MYRTLE]
            expected_ids=recovery_evidence['char_buff_ids']
            assert member['char_buff_ids']==expected_ids and member['char_buffs_complete'] is True
            assert member['recipient_buffs']['count']==2 and member['recipient_buffs']['complete'] is True
            assert member['fields']=={} and member['skill_ranks']=={}
            assert window.run.held_relic_ids()==recovery_evidence['current_confirmed_held_ids']
            assert 'rogue_6_relic_legacy_99' not in window.run.state['relics']
            assert window.run.state['selected_operator']==MYRTLE and window.operator.currentData()==MYRTLE
            assert window.current_operator_state()['char_buff_ids']==expected_ids
            assert window.operator_observations==account_before
            assert module.OPERATOR_STATE.read_bytes()==account_file_before
            assert '桃金娘' in window.run_summary.text() and '等级：未确认' in window.operator_summary.toPlainText()
            checks.append({'scope':'sealed_current_worker_popup_recovery_to_real_qt',
                'operator':MYRTLE,'char_buff_ids':expected_ids,'count':2,
                'complete':True,'cultivation_fields':{},'new_ocr_calls':0,
                'mechanist_account_unchanged':True,'held_inventory_complete_claimed':False,
                'held_legacy_99_ambiguous_not_injected':True,
                'current_confirmed_held_ids':recovery_evidence['current_confirmed_held_ids']})

            window.run.save()
            saved=read(module.RUN_STATE);reloaded=RunState(module.RUN_STATE)
            assert reloaded.state['id']==saved['id']==window.run.state['id']
            assert reloaded.state['operators'][MYRTLE]==saved['operators'][MYRTLE]==member
            assert reloaded.state['history']==saved['history']==window.run.state['history']
            assert reloaded.state['operators'][MYRTLE]['char_buff_ids']==expected_ids
            assert reloaded.held_relic_ids()==recovery_evidence['current_confirmed_held_ids']
            assert 'rogue_6_relic_legacy_99' not in reloaded.state['relics']
            checks.append({'scope':'temporary_run_save_reload_preserves_complete_strengthening',
                'operator':MYRTLE,'count':2,'cultivation_fields':{},'same_run':True})

            # Manually browse the known account operator; repeated page reads
            # are current facts but must not steal that browsing selection.
            assert window.select_operator('mechanist');app.processEvents()
            assert window.operator.currentData()=='mechanist'
            identity=window.run.state['id'];history_before=deepcopy(window.run.state['history'])
            deliver(recovery_image,deepcopy(recovery_observation))
            assert window.operator.currentData()=='mechanist'
            assert window.run.state['id']==identity and window.run.state['selected_operator']==MYRTLE
            assert window.run.state['history']==history_before
            assert window.run.state['operators'][MYRTLE]['char_buff_ids']==expected_ids
            assert window.run.state['operators'][MYRTLE]['fields']=={}
            assert window.operator_observations==account_before
            assert module.OPERATOR_STATE.read_bytes()==account_file_before
            checks.append({'scope':'repeated_recovery_page_keeps_manual_mechanist_browsing',
                'display_operator':'mechanist','observed_run_operator':MYRTLE,
                'same_run':True,'duplicate_history_added':False,'new_ocr_calls':0})

            run_before_unknown=deepcopy(window.run.state)
            deliver(blank,deepcopy(unknown))
            assert window.run.state==run_before_unknown and window.operator.currentData()=='mechanist'
            assert window.operator_observations==account_before
            assert module.OPERATOR_STATE.read_bytes()==account_file_before
            final_reload=RunState(module.RUN_STATE)
            assert final_reload.state['id']==identity
            assert final_reload.state['operators'][MYRTLE]==window.run.state['operators'][MYRTLE]
            checks.append({'scope':'unknown_page_retains_recovered_current_run_and_manual_browsing',
                'operator':MYRTLE,'count':2,'display_operator':'mechanist','new_ocr_calls':0})
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert read(RECOVERY)['source_sha256']==current_public_sources()
            after=source_hashes(fixtures)
            changed=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
            assert not changed,changed
            receipt={'version':'0.59.0','passed':True,'verified_at':time.time(),'checks':checks,
                'real_reader_results_used':True,'private_state_isolated':True,'game_actions':0,'chat_requests':0,
                'sample_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'original_actual_reader_checks':6,'sealed_current_worker_recovery_checks':4,
                'recovery_evidence':recovery_evidence,'recovery_new_ocr_calls':0,
                'personal_buff_complete_required':True,'held_inventory_complete_claimed':False,
                'held_legacy_99_ambiguous_not_injected':True,
                'elapsed_seconds':time.perf_counter()-started,
                'source_sha256':before,'source_sha256_after':after,'source_drift':changed,'runner_sealed':True}
            with (ROOT/'RECOGNITION_UI_0.59_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks),'elapsed_seconds':receipt['elapsed_seconds']}),flush=True)
        finally:window.close();app.processEvents()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--popup-freeze',required=True)
    main(parser.parse_args().popup_freeze)
