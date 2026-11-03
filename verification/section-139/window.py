import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
from rouge.reference_dialog import ReferenceDialog
from rouge.skill_upgrade_comparison import compare_skill_upgrades,format_skill_upgrades
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3));window.calculate()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.damage_budget_button.click();app.processEvents();dialog=window.damage_budget_dialog
        assert dialog.result is not None and dialog.table.rowCount()==1
        p=json.loads(dialog.editor.toPlainText());p['targets'][0]['hp']=100
        p['events'].append(copy.deepcopy(p['events'][0]));dialog.editor.setPlainText(json.dumps(p));assert dialog.result is None
        dialog.calculate_button.click();assert dialog.result['rows'][0]['effective_damage']==100 and dialog.result['rows'][1]['effective_damage']==0
        dialog.copy_button.click();assert '不是实际击杀' in app.clipboard().text() and '逐目标来源' in app.clipboard().text()
        cases.append('actual main entry clips target budget and keeps later declared overkill')
        p['events'][0]['source']='unknown';dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
        assert dialog.result is None and not dialog.copy_button.isEnabled() and dialog.table.rowCount()==0
        cases.append('unknown damage reference rejected without stale values')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        window.select_operator('char_2025_shu');window.skill.setCurrentIndex(window.skill.findData(1));window.calculate()
        assert not window.damage_budget_button.isEnabled()
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('healing does not enable damage budget; account/run unchanged and capture/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
