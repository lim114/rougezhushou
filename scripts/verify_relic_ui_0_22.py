"""Isolated Qt acceptance for conditional relics and capability-specific protection."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json,sys,tempfile,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import rouge.app as module
with tempfile.TemporaryDirectory() as folder:
    module.RUN_STATE=Path(folder)/'run.json';module.OPERATOR_STATE=Path(folder)/'operators.json'
    module.SETTINGS=Path(folder)/'settings.json'
    app=QApplication([]);window=module.MainWindow()
    def select(rid):
        window.relic_list.blockSignals(True)
        for i in range(window.relic_list.count()):
            item=window.relic_list.item(i)
            item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)==rid else Qt.CheckState.Unchecked)
        window.relic_list.blockSignals(False);window.relic_context.clear();window.calculate()
    try:
        window.auto_relics.setChecked(False)
        window.operator.setCurrentIndex(window.operator.findData('mechanist'))
        window.skill.setCurrentIndex(window.skill.findData(3))
        conditions={'rogue_6_relic_legacy_136':{'mercenary_recipient':1,'mercenary_stacks':1},
            'rogue_6_relic_artifact_4':{'active_other_aura_sources':1},
            'rogue_6_start_3':{'entered_zone_count':2},'rogue_6_relic_cargo_12':{'probe_stacks':2}}
        for rid,values in conditions.items():
            select(rid)
            assert window.damage_form.isRowVisible(window.relic_context)
            placeholder=window.relic_context.placeholderText()
            assert all(key in placeholder for key in values),(rid,placeholder)
            assert 'enemy_first_damage_unused' not in placeholder
            window.relic_context.setPlainText(json.dumps(values));window.calculate()
            assert window.damage_result,(rid,window.damage_text.toPlainText())
            assert all(key not in json.dumps(window.run.state) for key in values)
        select('rogue_6_relic_legacy_101')
        assert not window.damage_form.isRowVisible(window.relic_context)
        assert '【藏品防护】' in window.damage_text.toPlainText()
        window.operator.setCurrentIndex(window.operator.findData('char_133_mm'))
        assert '【藏品防护】' not in window.damage_text.toPlainText()
        select('rogue_6_relic_fight_7')
        assert '【藏品防护】' in window.damage_text.toPlainText()
        select('rogue_6_relic_legacy_91')
        assert '【藏品防护】' not in window.damage_text.toPlainText()
        receipt={'version':'0.22.0','verified_at':time.time(),'compound_recipient_conditions':True,
            'current_conditions_only':True,'protection_panel_only_when_applicable':True,
            'manual_preview_not_saved_to_run':True,'real_settings_and_run_isolated':True,'chat_requests':0}
        (root/'RELIC_UI_0.22_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
        print(json.dumps(receipt,ensure_ascii=False))
    finally:window.close();app.processEvents()
