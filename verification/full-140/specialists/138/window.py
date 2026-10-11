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
        from rouge.supplemental_skills import defaults
        before=copy.deepcopy((window.run.state,window.operator_observations,window.damage_result))
        window.centralWidget().setCurrentIndex(1);window.supplemental_skill_button.click();app.processEvents();dialog=window.supplemental_skill_dialog
        for identity,name in [('char_209_ardign','卡缇'),('char_122_beagle','米格鲁'),('char_120_hibisc','芙蓉')]:
            p=defaults(identity);p['count']=2;p['missing_hp']=100
            dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
            assert dialog.result['operator_name']==name and dialog.table.rowCount()>0
            if identity!='char_122_beagle':assert dialog.result['rows'][2]['value']==100
        dialog.copy_button.click();assert '生命缺口' in app.clipboard().text() and '本局' in app.clipboard().text()
        assert dialog.grab().save(str(Path(__file__).parent/'supplemental-healing.png'))
        cases.append('actual three support operators, clipped healing totals and source copy')
        p=defaults('char_209_ardign');p['missing_hp']=100000
        dialog.editor.setPlainText(json.dumps(p));dialog.calculate_button.click()
        assert dialog.result is None and not dialog.copy_button.isEnabled() and '最大生命' in dialog.notice.toPlainText()
        cases.append('impossible self HP gap clears result with actionable explanation')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('independent support preview preserves account/run, capture/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
