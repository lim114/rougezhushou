import sys,json,tempfile,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from rouge import app as product
from rouge.reference_dialog import ReferenceDialog
from rouge.skill_upgrade_comparison import compare_skill_upgrades,format_skill_upgrades
app=QApplication([]);cases=[]
with tempfile.TemporaryDirectory() as directory:
    base=Path(directory);product.RUN_STATE=base/'run.json';product.OPERATOR_STATE=base/'operator.json';product.SETTINGS=base/'settings.json'
    window=product.MainWindow();window.show();app.processEvents()
    try:
        from tests.test_cultivation_comparison_140 import proposal
        window.select_operator('char_124_kroos');window.calculate()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.centralWidget().setCurrentIndex(1);window.cultivation_comparison_button.click();app.processEvents();dialog=window.cultivation_comparison_dialog
        assert dialog.result is not None
        p={'proposals':[proposal('54级'),proposal('55级',level=55,potential=5)]}
        dialog.editor.setPlainText(json.dumps(p));assert dialog.result is None
        dialog.calculate_button.click();assert dialog.table.rowCount()==2 and dialog.result['rows'][1]['skill_differences']['普通单次边际期望']>0
        dialog.copy_button.click();assert '单次分项差值' in app.clipboard().text() and '独立抽样未知' in app.clipboard().text()
        cases.append('unsupported main skill still opens meaningful cultivation and talent breakpoint comparison')
        assert dialog.grab().save(str(Path(__file__).parent/'cultivation-comparison.png'))
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        p['proposals'][1]['name']='54级';dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
        assert dialog.result is None and not dialog.copy_button.isEnabled()
        cases.append('duplicate proposal clears stale result without state writes')
        window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3));window.calculate()
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.cultivation_comparison_button.click();app.processEvents();dialog=window.cultivation_comparison_dialog
        p={'proposals':[proposal('精一'),proposal('精二',elite=2,level=90)]}
        dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
        assert dialog.result['rows'][0]['window_damage'] is None and dialog.result['rows'][1]['window_damage']>0
        assert dialog.result['rows'][1]['delta_window_damage'] is None
        cases.append('core skill recomputed at each cultivation gate; unknown difference stays unknown')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        assert window.grab().save(str(Path(__file__).parent/'calculator140.png'))
        cases.append('main tools usable with preserved account/run, capture/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
