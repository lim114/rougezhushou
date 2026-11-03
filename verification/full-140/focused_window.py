"""Actual Qt acceptance for unit preview provenance and range errors."""
import copy,hashlib,json,sys,tempfile
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(__file__).parent/'focused-output';OUT.mkdir(exist_ok=False)
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
import rouge.app as product
app=QApplication([]);rows=[];TOKEN='token_10001_deepcl_tentac'
with tempfile.TemporaryDirectory(prefix='full125-unit-preview-') as directory:
    temp=Path(directory);product.RUN_STATE=temp/'run.json';product.OPERATOR_STATE=temp/'account.json';product.SETTINGS=temp/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.auto_relics.setChecked(False);window.centralWidget().setCurrentIndex(1)
        window.select_operator('char_110_deepcl');window.skill.setCurrentIndex(window.skill.findData(1))
        window.limit_window.setChecked(True);window.window_seconds.setValue(10)
        original_run=copy.deepcopy(window.run.state);original_account=copy.deepcopy(window.operator_observations)
        for frames in (True,False):
            window.frame_timing.setChecked(frames)
            for value in (0,'0'):
                window.timing_scenario.setPlainText(json.dumps({'units':{TOKEN:{'target_disappears_seconds':value}}}))
                window.calculate();app.processEvents()
                result=window.damage_result['result']
                token=next(c for c in result['components'] if c['name']=='触手')
                assert token['total']==0
                assert '目标生命周期来源：单位自身声明' in window.damage_text.toPlainText()
                assert window.damage_result['scenario']['timing']['units'][TOKEN]['target_disappears_seconds']==value
                rows.append({'mode':'frames' if frames else 'continuous','lifetime':value,'token_damage':0,'provenance_visible':True})
            window.timing_scenario.setPlainText(json.dumps({'target_disappears_seconds':0,'units':{TOKEN:{}}}))
            window.calculate();app.processEvents()
            assert '目标生命周期来源：继承本体声明' in window.damage_text.toPlainText()
            rows.append({'mode':'frames' if frames else 'continuous','lifetime_source':'owner','provenance_visible':True})
            for options,label in (({'windup_frames':10**400},'windup_frames'),
                                  ({'target_windows':[[0,10**400]]},'时间'),
                                  ({'units':{TOKEN:{'target_disappears_seconds':10**400}}},'target_disappears_seconds')):
                window.timing_scenario.setPlainText(json.dumps(options));window.calculate();app.processEvents()
                assert window.damage_result is None
                assert label in window.damage_text.toPlainText()
                assert '需要有限非负数' in window.damage_text.toPlainText()
                rows.append({'mode':'frames' if frames else 'continuous','invalid_field':label,'stale_result_cleared':True,'labelled_error':True})
            window.timing_scenario.setPlainText('{}');window.calculate();app.processEvents()
            assert window.damage_result
            rows.append({'mode':'frames' if frames else 'continuous','valid_recovery':True})
        window.timing_scenario.setPlainText(json.dumps({'units':{TOKEN:{'target_disappears_seconds':'0'}}}))
        window.calculate();app.processEvents()
        window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
        assert window.damage_text.find('目标生命周期来源：单位自身声明')
        window.damage_text.ensureCursorVisible();app.processEvents()
        assert window.grab().save(str(OUT/'unit-provenance.png'))
        assert window.run.state==original_run and window.operator_observations==original_account
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
    finally:
        window.close();app.processEvents()
receipt={'passed':True,'actual_window_cases':rows,'private_state_included':False,'run_and_account_unchanged':True,'game_capture':False,'chat_requests':0,'native_windows_verified':False,'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('rouge/timing.py','rouge/reporting.py','rouge/app.py')}}
(OUT/'focused-window.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(rows)},ensure_ascii=False))
