import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
from rouge.scenario_library_view import ScenarioLibraryDialog
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3));window.calculate()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.centralWidget().setCurrentIndex(1);app.processEvents()
        assert window.scenario_library_button.isVisible() and window.skill_upgrade_button.isVisible()
        assert window.grab().save(str(Path(__file__).parent/'calculator-tools.png'))
        window.scenario_library_button.click();app.processEvents();dialog=window.scenario_library_dialog
        assert dialog.records.count()==0 and dialog.result is not None and not dialog.library.path.exists()
        cases.append('actual calculator grid and library entry without startup writes')
        dialog.name.setText('公开专三');dialog.save_button.click();app.processEvents()
        assert dialog.records.count()==1 and dialog.library.path.exists()
        first=dialog.library.records()[0]['id'];original_conditions=dialog.library.get(first)['scenario']
        scenario=copy.deepcopy(original_conditions);scenario['skill_rank']=7
        dialog.editor.setPlainText(json.dumps(scenario,ensure_ascii=False,indent=2));assert dialog.result is None and not dialog.copy_button.isEnabled()
        dialog.name.setText('公开七级');dialog.save_button.click();assert dialog.records.count()==2
        dialog.name.setText('公开七级');dialog.save_button.click();assert dialog.records.count()==2 and '同名' in dialog.notice.toPlainText()
        cases.append('save proposals, strict names and stale result invalidation')
        for i in range(dialog.records.count()):dialog.records.item(i).setSelected(True)
        assert not dialog.load_button.isEnabled() and not dialog.delete_button.isEnabled()
        dialog.compare_button.click();assert dialog.result is not None and dialog.table.rowCount()==3
        upgrade=next(r for r in dialog.result['rows'] if r['name']=='公开专三')
        assert upgrade['delta_window_damage']>0 and any(d['path']=='/skill_rank' for d in upgrade['differences'])
        dialog.copy_button.click();assert '字段差异' in app.clipboard().text() and '窗口不同或未知' in app.clipboard().text()
        cases.append('multi-selection current-model recomputation and condition differences')
        assert dialog.grab().save(str(Path(__file__).parent/'scenario-library.png'))
        for i in range(dialog.records.count()):dialog.records.item(i).setSelected(i==0)
        dialog.load_button.click();assert json.loads(dialog.editor.toPlainText())==original_conditions
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        saved=dialog.library.path.read_bytes();path=dialog.library.path
        dialog.close();window.scenario_library_button.click();app.processEvents();restored=window.scenario_library_dialog
        assert restored.records.count()==2 and path.read_bytes()==saved
        cases.append('load only independent editor and close/reopen saved conditions')
        restored.records.item(1).setSelected(True);restored.delete_button.click();assert restored.records.count()==1
        assert len(restored.library.records())==1
        restored.editor.setPlainText('{bad');restored.compare_button.click()
        assert restored.result is None and restored.table.rowCount()==0 and not restored.copy_button.isEnabled()
        cases.append('explicit selected deletion and malformed preview invalidation')
        restored.close()
        damaged=base/'damaged-library.json';damaged.write_text('{broken')
        protected=ScenarioLibraryDialog(original_conditions,damaged,window);protected.name.setText('窗口条件');protected.save_button.click()
        assert damaged.read_text()=='{broken' and protected.records.count()==1 and '当前窗口有效' in protected.persistence.text()
        protected.close();cases.append('unusable file protected with clear session-only save notice')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('main conditions account/run preserved; game capture and chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
