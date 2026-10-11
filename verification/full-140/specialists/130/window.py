import sys, json, tempfile, copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
from rouge.token_budget_view import TokenBudgetDialog
app=QApplication([]); cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory); product.RUN_STATE=base/'run.json'; product.OPERATOR_STATE=base/'operator.json'; product.SETTINGS=base/'settings.json'
    window=product.MainWindow(); window.show(); app.processEvents()
    try:
        window.select_operator('mechanist'); window.calculate(); original=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.token_budget_button.click(); app.processEvents(); dialog=window.token_budget_dialog
        assert dialog.table.rowCount()==1 and dialog.result is not None
        controls=next(iter(dialog.inputs.values())); controls['additional'].setValue(2)
        assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.budget.setValue(99); dialog.calculate_button.click(); app.processEvents()
        assert dialog.result['total_cost_reference'] is not None
        cases.append('main calculator entry, current cultivation and stale result invalidation')
        dialog.close()
        preview=TokenBudgetDialog('char_110_deepcl',{'elite':2,'level':70,'module_id':'uniequip_002_deepcl','module_level':3},window)
        preview.show(); app.processEvents(); controls=next(iter(preview.inputs.values()))
        for key,value in (('additional',3),('present',5),('available_stock',2)):controls[key].setValue(value)
        preview.budget.setValue(10); preview.calculate_button.click()
        assert preview.result['total_cost_reference']==9 and '库存不足' in preview.notice.toPlainText() and '超出' in preview.notice.toPlainText()
        preview.copy_button.click(); assert '总费用9' in app.clipboard().text()
        cases.append('known module cost, separate declared stock/cap warnings and copy')
        preview.close()
        from rouge.catalog import catalog
        module=catalog()['operators']['mechanist']['modules'][0]['id']
        unknown=TokenBudgetDialog('mechanist',{'elite':2,'level':90,'module_id':module,'module_level':1},window)
        next(iter(unknown.inputs.values()))['additional'].setValue(1); unknown.calculate_button.click()
        assert unknown.result['total_cost_reference'] is None
        assert unknown.table.item(0,4).text()=='未知'
        unknown.close(); cases.append('unsupported module fields stay unknown in actual table')
        assert (window.run.state,window.operator_observations,window.damage_result)==original
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('account run and original result preserved; game and chat off')
    finally:window.close(); app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
