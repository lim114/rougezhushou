"""Actual collision comparison dialog, isolated from game and private state."""
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
import rouge.app as product

app=QApplication([])
cases=[]
with tempfile.TemporaryDirectory(prefix='charge-timeline127-') as directory:
    base=Path(directory)
    product.RUN_STATE=base/'run.json'; product.OPERATOR_STATE=base/'account.json'; product.SETTINGS=base/'settings.json'
    window=product.MainWindow(); window.show(); app.processEvents()
    try:
        window.auto_relics.setChecked(False); window.centralWidget().setCurrentIndex(1)
        window.select_operator('mechanist')
        window.skill.setCurrentIndex(window.skill.findData(3))
        window.charge_count.setValue(4); window.calculate(); app.processEvents()
        assert window.charge_timeline_button.isEnabled()
        before_run=copy.deepcopy(window.run.state)
        before_account=copy.deepcopy(window.operator_observations)
        before_damage=copy.deepcopy(window.damage_result)
        window.charge_timeline_button.click(); app.processEvents()
        dialog=window.charge_timeline_dialog
        assert dialog.isVisible() and dialog.comparison_result is not None
        assert dialog.comparison_result['hit_times_seconds']==[]
        assert dialog.window_table.rowCount()==3
        cases.append('real button opens with no invented collisions')
        dialog.editor.setPlainText('{"hit_times_seconds":[0,3.5,3.5,5],"windows_seconds":[0,3.5,4,10]}')
        app.processEvents()
        assert dialog.comparison_result is None and dialog.window_table.rowCount()==0
        assert not dialog.copy_button.isEnabled()
        dialog.calculate_button.click(); app.processEvents()
        result=copy.deepcopy(dialog.comparison_result)
        assert [r['charge_hits'] for r in result['windows']]==[0,1,3,4]
        assert dialog.event_table.rowCount()==4 and dialog.window_table.rowCount()==4
        assert dialog.window_table.item(0,5).text()=='未知'
        assert '当前培养预览尚未确认' in dialog.notice.toPlainText()
        assert result['full_cast_damage'] is None and result['cycle_damage'] is None
        dialog.copy_button.click(); app.processEvents()
        copied=QApplication.clipboard().text()
        assert '冲锋3次' in copied and '完整施放总伤：未知' in copied
        assert '"charge_count": 4' in copied
        cases.append('exact endpoint, duplicate events, zero window, copyable conditions')
        assert dialog.grab().save(str(OUT/'charge-windows.png'))
        # A later main-window change does not silently reinterpret this snapshot.
        window.defense.setValue(window.defense.value()+100); app.processEvents()
        dialog.calculate_button.click(); app.processEvents()
        assert dialog.comparison_result==result
        window.defense.setValue(before_damage['scenario']['enemy_defense']); app.processEvents()
        assert window.damage_result==before_damage
        cases.append('opened calculation conditions frozen across later edits')
        for invalid in ('{"hit_times_seconds":[true],"windows_seconds":[1]}',
                        '{"hit_times_seconds":[],"windows_seconds":[41]}',
                        '{"hit_times_seconds":[],"hit_times_seconds":[1],"windows_seconds":[1]}'):
            dialog.editor.setPlainText(invalid); dialog.calculate_button.click(); app.processEvents()
            assert dialog.comparison_result is None and dialog.window_table.rowCount()==0
            assert dialog.event_table.rowCount()==0 and not dialog.copy_button.isEnabled()
            assert dialog.notice.toPlainText()
        cases.append('invalid numeric, duration and duplicate JSON clear stale tables')
        assert window.run.state==before_run and window.operator_observations==before_account
        assert window.damage_result==before_damage
        dialog.close(); app.processEvents()
        window.skill.setCurrentIndex(window.skill.findData(2)); app.processEvents()
        assert not window.charge_timeline_button.isEnabled()
        window.select_operator('kaltsit'); app.processEvents()
        assert not window.charge_timeline_button.isEnabled()
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('other skills disabled; account/run/calculation unchanged; no capture/chat')
    finally:
        window.close(); app.processEvents()

receipt={'passed':True,'actual_window_cases':cases,'private_state_included':False,
    'native_windows_verified':False,'game_capture':False,'chat_requests':0,
    'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        for name in ('rouge/app.py','rouge/charge_timeline.py','rouge/charge_timeline_view.py')}}
(OUT/'window.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)},ensure_ascii=False))
