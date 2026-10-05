"""Public Qt calculation flow, isolated run, no game input or chat sends."""
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
        select('rogue_6_relic_legacy_103')
        assert window.damage_form.isRowVisible(window.relic_context)
        assert 'altar_stacks' in window.relic_context.placeholderText() and 'chitin_recipient' not in window.relic_context.placeholderText()
        window.relic_context.setPlainText('{"altar_stacks":3}');window.calculate()
        assert abs(window.damage_result['result']['estimate']['base_stats']['attack']-658.95)<1e-6
        assert 'altar_stacks' not in json.dumps(window.run.state)
        select('rogue_6_relic_legacy_91')
        assert not window.damage_form.isRowVisible(window.relic_context)
        assert abs(window.damage_result['result']['relic_regeneration_rate']-36.31)<1e-6
        select('rogue_6_relic_legacy_100')
        window.operator.setCurrentIndex(window.operator.findData('char_110_deepcl'))
        window.relic_context.setPlainText('{"blocked_enemies":0,"token_conditions":{"token_10001_deepcl_tentac":{"blocked_enemies":1}}}')
        window.calculate()
        assert window.damage_result['result']['estimate']['base_stats']['attack']==403
        assert window.damage_result['result']['relic_token_stats'][0]['attack']==924
        select('rogue_6_relic_fight_30')
        window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_1_2'))
        window.target_enemy.setCurrentIndex(next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2137_shsdgo'))
        assert window.damage_form.isRowVisible(window.relic_context)
        window.relic_context.setPlainText('{"probe_stacks":2}');window.calculate()
        assert window.damage_result['result']['run_resolution']['enemy']['stats']['maxHp']==25200
        window.target_enemy.setCurrentIndex(next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_1093_ccsbr'))
        assert not window.damage_form.isRowVisible(window.relic_context)
        receipt={'version':'0.16.0','verified_at':time.time(),'new_relics_in_calculation':True,
            'current_conditions_only':True,'manual_conditions_not_saved_to_run':True,
            'independent_token_conditions':True,'irrelevant_enemy_conditions_hidden':True,'chat_requests':0}
        (root/'RELIC_UI_0.16_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(receipt,ensure_ascii=False))
    finally:window.close();app.processEvents()
