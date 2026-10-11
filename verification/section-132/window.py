import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.select_operator('char_196_sunbr');window.skill.setCurrentIndex(window.skill.findData(1));window.calculate()
        assert window.healing_budget_button.isEnabled()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.healing_budget_button.click();app.processEvents();dialog=window.healing_budget_dialog
        assert dialog.result is not None and dialog.table.rowCount()==0
        source=dialog.result['sources'][0]['id'];amount=dialog.result['sources'][0]['per_heal_reference']
        cases.append('actual healing skill entry and current source references')
        data={'recipients':[{'id':'公开甲','max_hp':3000,'hp':2500},{'id':'公开乙','max_hp':3000,'hp':1000}], 'events':[{'kind':'heal','recipient':'公开甲','at_seconds':1,'source':source},{'kind':'loss','recipient':'公开乙','at_seconds':1,'amount':200},{'kind':'heal','recipient':'公开乙','at_seconds':2,'source':source}]}
        dialog.editor.setPlainText(json.dumps(data));assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.calculate_button.click();assert dialog.result['rows'][0]['effective_healing']==min(500,amount)
        assert dialog.result['rows'][1]['hp_after']==800 and dialog.table.rowCount()==3
        dialog.copy_button.click();assert '过量治疗' in app.clipboard().text() and '公开甲' in app.clipboard().text()
        cases.append('individual deficits, event order, clipped heal and copy')
        data['events'][0]['source']='unavailable';dialog.editor.setPlainText(json.dumps(data));dialog.calculate_button.click()
        assert dialog.result is None and dialog.table.rowCount()==0 and not dialog.copy_button.isEnabled()
        cases.append('unavailable source clears stale results')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        dialog.close();window.select_operator('mechanist');window.calculate();assert not window.healing_budget_button.isEnabled()
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('original state preserved, no-heal entry disabled and game/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
