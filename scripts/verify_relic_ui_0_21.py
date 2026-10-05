"""Isolated public Qt flow; no writes to real run/settings and no chat sends."""
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
        window.run.state['resources']['parts_count']={'capacity':12,'value':3}
        select('rogue_6_relic_cargo_3')
        assert window.damage_result['scenario']['relic_context']['empty_slots']==9
        assert window.damage_result['result']['deployment_cost']==17
        conditions={'rogue_6_relic_legacy_63':'deployed_seconds',
            'rogue_6_relic_legacy_58':'near_protection_point',
            'rogue_6_relic_artifact_7':'grudge_stacks',
            'rogue_6_relic_fight_2':'enemy_first_damage_unused'}
        values={'deployed_seconds':80,'near_protection_point':1,'grudge_stacks':100,'enemy_first_damage_unused':1}
        for rid,key in conditions.items():
            select(rid)
            assert window.damage_form.isRowVisible(window.relic_context),(rid,key)
            placeholder=window.relic_context.placeholderText()
            assert key in placeholder and 'empty_slots' not in placeholder,(rid,placeholder)
            window.relic_context.setPlainText(json.dumps({key:values[key]}));window.calculate()
            assert window.damage_result,(rid,window.damage_text.toPlainText())
            assert key not in json.dumps(window.run.state),key
        select('rogue_6_relic_legacy_91')
        assert not window.damage_form.isRowVisible(window.relic_context)
        receipt={'version':'0.21.0','verified_at':time.time(),'automatic_empty_slots_from_capacity':True,
            'current_conditions_only':True,'manual_preview_not_saved_to_run':True,
            'real_settings_and_run_isolated':True,'chat_requests':0}
        (root/'RELIC_UI_0.21_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(receipt,ensure_ascii=False))
    finally:window.close();app.processEvents()
