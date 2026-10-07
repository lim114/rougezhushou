"""Real Windows Qt widgets under Wine; isolated state; no capture/chat operations."""
import hashlib, importlib, importlib.metadata, json, os, platform, subprocess, sys, tempfile, time, traceback
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou')
OUT=Path(r'Z:\workspace\.compat')
sys.path.insert(0,str(ROOT))
def source_hashes():
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in (ROOT/'rouge',) for p in sorted(folder.rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
checks=[];started=time.perf_counter();window=None;app=None;before=source_hashes()
receipt={'scope':'Wine Windows binary compatibility; no native Windows or game integration',
         'native_windows_verified':False,'game_captures':0,'chat_requests':0,
         'private_state_isolated':True,'platform':platform.platform(),'python':sys.version,
         'checks':checks,'passed':False,'plain_text_normalization':'QPlainTextEdit converts non-breaking spaces to ordinary spaces'}
try:
    for name in ('PySide6.QtWidgets','numpy','cv2','win32gui','win32process','win32api','httpx','rapidocr_onnxruntime','windows_capture'):
        importlib.import_module(name)
        checks.append({'scope':'real_dependency_import','module':name,'passed':True})
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication,QPushButton
    import rouge.app as module
    from rouge.reporting import format_report
    from rouge.capture import list_game_windows
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()
        assert window.isVisible()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not list_game_windows()
        checks.append({'scope':'actual_main_window_visible','title':window.windowTitle(),
                       'win32_game_enumeration':'no Arknights.exe window present',
                       'auto_sampling':False,'desktop_backend_started':False})
        window.auto_relics.setChecked(False)
        skills=0
        for op,profile in module.catalog()['operators'].items():
            for skill in range(1,len(profile['skills'])+1):
                window.select_operator(op)
                window.skill.setCurrentIndex(window.skill.findData(skill))
                window.calculate();app.processEvents()
                assert window.damage_result,window.damage_text.toPlainText()
                result=window.damage_result['result']
                actual=window.damage_text.toPlainText();expected=format_report(result,technical=window.damage_technical.isChecked()).replace(chr(160),' ')
                if actual!=expected:
                    (OUT/'wine-ui-report-difference.json').write_text(json.dumps({'operator':op,'skill':skill,'actual':actual,'expected':expected},ensure_ascii=False,indent=2),encoding='utf-8')
                    raise AssertionError(f'report text differs for {op} skill {skill}')
                skills+=1
        assert skills==87,skills
        checks.append({'scope':'actual_controls_calculate_all_profiles','skills':skills,'passed':True})
        window.select_operator('char_1042_phatm2')
        window.skill.setCurrentIndex(window.skill.findData(1));window.calculate();app.processEvents()
        assert window.damage_result
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        calculate_button=next(b for b in window.findChildren(QPushButton) if b.text()=='计算属性与技能预估')
        calculate_button.click();app.processEvents()
        assert window.damage_result and window.damage_text.toPlainText()
        checks.append({'scope':'actual_calculate_button_click','passed':True})
        screenshot=OUT/'wine-window.png'
        assert window.grab().save(str(screenshot))
        receipt['window_screenshot']='wine-window.png'
        assert not isolated.joinpath('chat').exists()
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process
        checks.append({'scope':'no_external_operations','game_captures':0,'chat_requests':0,'temporary_state':True})
        window.close();app.processEvents();window=None
    receipt['passed']=True
except BaseException as error:
    receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
finally:
    if window is not None:
        window.close()
        if app is not None:app.processEvents()
    receipt['elapsed_seconds']=round(time.perf_counter()-started,3)
    after=source_hashes();drift=[n for n in sorted(set(before)|set(after)) if before.get(n)!=after.get(n)]
    receipt['source_sha256']=before;receipt['source_sha256_after']=after;receipt['source_drift']=drift
    if drift:receipt['passed']=False
    (OUT/'wine-ui-smoke.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
