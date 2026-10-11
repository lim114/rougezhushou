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
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        assert window.supplemental_skill_button.isEnabled() and window.supplemental_skill_button.isVisible()
        window.supplemental_skill_button.click();app.processEvents();dialog=window.supplemental_skill_dialog
        assert dialog.result['operator_name']=='玫兰莎' and dialog.table.rowCount()==3
        dialog.copy_button.click();assert '固定资料' in app.clipboard().text() and '时刻' in app.clipboard().text()
        cases.append('actual main entry, parameter rows and complete source/conditions copy')
        from rouge.supplemental_skills import defaults
        dialog.editor.setPlainText(json.dumps(defaults('char_123_fang')));assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.calculate_button.click();assert dialog.result['rows'][0]['value']==6
        cases.append('independent proposal switches to instant DP and invalidates stale calculation')
        dialog.editor.setPlainText('{"operator":"bad"}');dialog.calculate_button.click()
        assert dialog.result is None and dialog.table.rowCount()==0 and not dialog.copy_button.isEnabled()
        cases.append('invalid input clears result')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('account/run unchanged, game and chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
