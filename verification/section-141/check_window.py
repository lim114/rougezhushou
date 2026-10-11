"""Native Qt entry checks with isolated state, no game/chat interaction."""
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import rouge.app as product
from rouge.supplemental_skills import supplemental_profiles

app=QApplication([])
with tempfile.TemporaryDirectory(prefix='rouge-141-') as directory:
    root=Path(directory)
    product.ROOT=root
    product.SETTINGS=root/'local-settings.json'
    product.OPERATOR_STATE=root/'.local/operator-state.json'
    product.RUN_STATE=root/'.local/run-state.json'
    window=product.MainWindow()
    window.auto.setChecked(False)
    window.auto_relics.setChecked(False)
    for i in range(window.relic_list.count()):
        item=window.relic_list.item(i)
        item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_legacy_27'
                           else Qt.CheckState.Unchecked)
    cases=[]
    for identity,profile in supplemental_profiles()['operators'].items():
        window.select_operator(identity)
        window.show_supplemental_skills()
        app.processEvents()
        dialog=window.supplemental_skill_dialog
        assert dialog.isVisible() and dialog.result is not None,identity
        assert dialog.result['operator_name']==profile['name']
        assert dialog.result['preview']['skill_rank']==7
        assert dialog.result['run_attributes']['hp']>0
        assert 'rogue_6_relic_legacy_27' in dialog.result['environment']['relic_ids']
        assert set(dialog.result['environment']['operator_metadata'][identity])<= {
            'char_buff_ids','char_buffs_complete','char_buff_absent_ids','char_buff_pending_ids','recruitment_kind'}
        cases.append({'operator':identity,'entry':'passed','rank':7,'columns':dialog.table.columnCount()})
        dialog.close()
    window.show_supplemental_skills();app.processEvents()
    dialog=window.supplemental_skill_dialog
    preview=json.loads(dialog.editor.toPlainText());preview['count']=3
    text=json.dumps(preview,ensure_ascii=False,indent=2);dialog.editor.setPlainText(text)
    dialog.refresh_button.click();app.processEvents()
    assert dialog.result is not None and dialog.result['preview']['count']==3
    assert dialog.editor.toPlainText()==text
    window.close();app.processEvents()
print(json.dumps({'native_qt':True,'isolated_state':True,'seven_entry_cases':cases,
                  'refresh_preserved_preview':True,'game_operated':False,'chat_sent':False},ensure_ascii=True))
