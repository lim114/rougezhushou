import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(2));window.calculate()
        assert window.shield_timeline_button.isEnabled() and not window.charge_timeline_button.isEnabled()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.shield_timeline_button.click();app.processEvents();dialog=window.shield_timeline_dialog
        assert dialog.result is not None and dialog.table.rowCount()==3
        cases.append('actual entry restricted to successful mechanic S2 calculation')
        preview={'events':[{'source':'owner','break_seconds':1,'hit_seconds':2},{'source':'structure','break_seconds':1,'hit_seconds':2},{'source':'structure','break_seconds':2,'hit_seconds':None}], 'windows_seconds':[2,3]}
        dialog.editor.setPlainText(json.dumps(preview));assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.calculate_button.click();assert dialog.result['rows'][0]['owner_hits']==0
        assert dialog.result['rows'][1]['owner_hits']==1 and dialog.result['rows'][1]['structure_hits']==1
        dialog.copy_button.click();assert '用户事件' in app.clipboard().text() and '耗弹对应' in app.clipboard().text()
        cases.append('separate break/hit/source declarations, boundary windows and copy')
        preview['events'][0]['hit_seconds']=0
        dialog.editor.setPlainText(json.dumps(preview));dialog.calculate_button.click()
        assert dialog.result is None and dialog.table.rowCount()==0 and '早于' in dialog.notice.toPlainText()
        cases.append('invalid event removes stale outputs and copy')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        dialog.close();window.skill.setCurrentIndex(window.skill.findData(3));window.calculate()
        assert not window.shield_timeline_button.isEnabled()
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('state preserved, wrong skill disabled and game/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
