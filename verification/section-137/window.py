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
        from rouge.supplemental_skills import defaults
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.supplemental_skill_button.click();app.processEvents();dialog=window.supplemental_skill_dialog
        p=defaults('char_124_kroos');dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
        assert dialog.table.rowCount()==6 and dialog.table.item(5,1).text()=='未知'
        dialog.copy_button.click();assert '边际期望' in app.clipboard().text() and '独立抽样未知' in app.clipboard().text()
        cases.append('ordinary critical expectation distinct from unknown double-hit combination')
        p=defaults('char_210_stward');p['enemy_resistance']=100
        dialog.editor.setPlainText(json.dumps(p));assert dialog.result is None
        dialog.calculate_button.click();assert dialog.result['rows'][1]['value']>0 and dialog.table.rowCount()==2
        cases.append('caster strike, resistance cap and stale result invalidation')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('independent preview preserves account/run, capture/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
