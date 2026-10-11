"""Native Qt actual entry with temporary state and qualified raw conditions."""
import json
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
import rouge.app as product
from rouge.supplemental_skills import supplemental_profiles

app=QApplication([])
with tempfile.TemporaryDirectory(prefix='rouge-142-') as directory:
    root=Path(directory)
    product.ROOT=root;product.SETTINGS=root/'local-settings.json'
    product.OPERATOR_STATE=root/'.local/operator-state.json'
    product.RUN_STATE=root/'.local/run-state.json'
    window=product.MainWindow();window.auto.setChecked(False)
    identities=list(supplemental_profiles()['operators'])
    environment={'relic_ids':['rogue_6_relic_cargo_2','rogue_6_relic_cargo_10','rogue_6_relic_artifact_7'],
        'run_config':{},'relic_context':{'parts_count':2,'grudge_stacks':100},
        'inventory_status':{'complete':True},
        'operator_metadata':{identity:{'recruitment_kind':'emergency_hire'} for identity in identities}}
    # Synthetic provider only in this isolated process, never writes real state.
    window.supplemental_run_environment=lambda:environment
    cases=[]
    for identity in identities:
        window.select_operator(identity);window.show_supplemental_skills();app.processEvents()
        dialog=window.supplemental_skill_dialog;result=dialog.result
        assert dialog.isVisible() and result is not None,identity
        assert len(result['attribute_resolution']['ordinary'])==6
        assert result['attribute_resolution']['complete_for_attribute_scope']
        assert '与天赋/技能相加' in dialog.notice.toPlainText()
        cases.append({'operator':identity,'stable_ordinary_sources':3,'status':'passed'})
        dialog.close()
    window.show_supplemental_skills();app.processEvents()
    dialog=window.supplemental_skill_dialog
    editor=dialog.editor.toPlainText()
    environment['relic_context']['parts_count']=3
    dialog.refresh_button.click();app.processEvents()
    assert dialog.editor.toPlainText()==editor
    assert '零件3个' in dialog.notice.toPlainText()
    dialog.close();window.close();app.processEvents()
receipt={'native_qt':True,'isolated_state':True,'synthetic_provider':True,
    'entry_cases':cases,'refresh_preserved_preview':True,'game_operated':False,'chat_sent':False}
(Path(__file__).parent/'native-qt.json').write_bytes(json.dumps(receipt,ensure_ascii=False,indent=2).encode('utf-8'))
print(json.dumps(receipt,ensure_ascii=True))
