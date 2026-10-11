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
        window.skill_upgrade_button.click();app.processEvents();dialog=window.skill_upgrade_dialog
        assert dialog.result is not None and dialog.table.rowCount()==10
        assert dialog.result['rows'][-1]['delta_window_damage']==0
        assert dialog.table.item(0,6).text()=='不适用'
        dialog.copy_button.click();assert '同一计算条件' in app.clipboard().text() and '原表' in app.clipboard().text()
        cases.append('main entry all ranks, baseline difference, absent healing and source copy')
        dialog.editor.setPlainText('{"ranks":[7,7]}');dialog.calculate_button.click()
        assert dialog.result is None and dialog.table.rowCount()==0 and not dialog.copy_button.isEnabled()
        cases.append('duplicate proposal clears stale result')
        e1={'operator':'mechanist','skill':2,'elite':1,'skill_rank':7}
        preview=ReferenceDialog('公开精一对照','公开测试',{'ranks':[7,8]},lambda p:compare_skill_upgrades(e1,p),format_skill_upgrades,[('status','状态'),('window_damage','伤害')],window)
        assert preview.result['rows'][1]['status']=='不可测算' and '未开放' in preview.notice.toPlainText()
        preview.close();cases.append('unopened mastery remains an explicit unavailable row')
        assert (window.run.state,window.operator_observations,window.damage_result)==before
        dialog.close();assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
        cases.append('original account run and calculation preserved, game/chat off')
    finally:window.close();app.processEvents()
(Path(__file__).parent/'window.json').write_text(json.dumps({'passed':True,'cases':cases,'native_windows_game_chat_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
