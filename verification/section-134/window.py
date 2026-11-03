import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from rouge import app as product
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3));window.calculate()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.enemy_comparison_button.click();app.processEvents();dialog=window.enemy_comparison_dialog
        assert dialog.stage.count()==len(product.stage_previews())
        dialog.stage.setCurrentIndex(dialog.stage.findData('ro6_n_1_1'))
        for i in range(dialog.enemies.count()):dialog.enemies.item(i).setCheckState(Qt.CheckState.Checked if i==0 else Qt.CheckState.Unchecked)
        dialog.grades.setText('[4,5]');dialog.calculate_button.click()
        assert dialog.result is not None and dialog.table.rowCount()==2
        assert abs(dialog.result['rows'][1]['max_hp']/dialog.result['rows'][0]['max_hp']-1.3)<1e-8
        cases.append('actual entry, source stage/enemy selection and grade threshold')
        dialog.enemies.item(1).setCheckState(Qt.CheckState.Checked)
        assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.calculate_button.click();assert dialog.table.rowCount()==4
        dialog.copy_button.click();assert '用户对照选择' in app.clipboard().text() and '候选' in app.clipboard().text()
        cases.append('multiple candidates, explicit recalculation and complete copy')
        dialog.grades.setText('[5,5]');dialog.calculate_button.click()
        assert dialog.result is None and dialog.table.rowCount()==0 and not dialog.copy_button.isEnabled()
        dialog.grades.setText('[5]')
        for i in range(dialog.enemies.count()):dialog.enemies.item(i).setCheckState(Qt.CheckState.Unchecked)
        dialog.calculate_button.click();assert '需选择' in dialog.notice.toPlainText()
        cases.append('duplicate grades and empty target selection remove stale result')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        dialog.close();assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('original account/run/target/grade preserved, game/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
