"""Isolated own-application UI checks, with no capture or chat transport."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from scripts.verify_relic_ui_025 import OfflineWindow, module
from tests.test_deployment_relics_027 import BIND, FIRE, PICTURE


def main():
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as folder:
        isolated = Path(folder)
        module.RUN_STATE = isolated / 'run.json'
        module.OPERATOR_STATE = isolated / 'operators.json'
        module.SETTINGS = isolated / 'settings.json'
        backend = module.DesktopBackend
        module.DesktopBackend = lambda _path, callback: backend(isolated / 'chat', callback)
        app = QApplication([])
        window = OfflineWindow()
        def choose(op, skill):
            window.operator.setCurrentIndex(window.operator.findData(op))
            window.skill.setCurrentIndex(window.skill.findData(skill))
            window.calculate()
            assert window.damage_result, window.damage_text.toPlainText()
        def relics(*ids):
            window.relic_list.blockSignals(True)
            for index in range(window.relic_list.count()):
                item = window.relic_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.calculate()
        def enemy(stage):
            window.target_stage.setCurrentIndex(window.target_stage.findData(stage))
            assert window.target_enemy.count() > 1
            window.target_enemy.setCurrentIndex(1)
            window.calculate()
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            window.auto_relics.setChecked(False)
            choose('mechanist', 3)
            assert not window.damage_form.isRowVisible(window.relic_context)
            relics(BIND)
            assert window.damage_form.isRowVisible(window.relic_context)
            hint = window.relic_context.toolTip()
            assert 'deployment_hp_ratio' in hint and 'deployment_loss_unused' in hint
            assert 'fire_rod_stacks' not in hint
            assert '实际部署扣费：未知' in window.damage_text.toPlainText()
            window.relic_context.setPlainText(json.dumps({'deployment_hp_ratio': .65, 'deployment_loss_unused': 1}))
            result = window.damage_result['result']
            hp = result['estimate']['base_stats']['hp']
            loss = result['deployment_reference']['hp_loss'][0]
            assert abs(loss['hp_after_loss'] - hp * .195) < 1e-8
            first = json.dumps(result['deployment_reference'], sort_keys=True)
            window.calculate()
            assert json.dumps(window.damage_result['result']['deployment_reference'], sort_keys=True) == first
            window.relic_context.setPlainText(json.dumps({'deployment_hp_ratio': .3, 'deployment_loss_unused': 0}))
            assert window.damage_result['result']['deployment_reference']['hp_loss'][0]['lost_hp'] == 0
            choose('mechanist', 1)
            assert window.damage_result['result']['deployment_reference']['hp_loss'][0]['hp_after_loss'] is None
            choose('mechanist', 3)
            assert window.damage_result['result']['deployment_reference']['hp_loss'][0]['lost_hp'] == 0
            relics()
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert '部署损血参考' not in window.damage_text.toPlainText()
            assert '实际部署扣费' not in window.damage_text.toPlainText()
            assert 'deployment_reference' not in window.damage_result['result']
            relics(FIRE)
            assert 'deployment_hp_ratio' not in window.relic_context.toolTip()
            window.relic_context.setPlainText('{"fire_rod_stacks":0,"deployment_hp_ratio":"ignored"}')
            enemy('ro6_t_8')
            assert window.damage_result['result']['relic_resolution']['enemy_effects']['resident_hp_applied']
            assert '厄运火杆：已确认居民关卡单项生命参考' in window.damage_text.toPlainText()
            result = window.damage_result['result']
            assert result['run_resolution']['enemy']['stats']['maxHp'] == 1500
            relics(FIRE, PICTURE)
            assert '居民生命组合待核验' in window.damage_text.toPlainText()
            assert '未额外乘0.6' in window.damage_text.toPlainText()
            relics(FIRE)
            enemy('ro6_n_1_2')
            assert not window.damage_result['result']['relic_resolution']['enemy_effects']['resident_hp_applied']
            assert '居民关卡单项生命参考' not in window.damage_text.toPlainText()
            relics()
            window.target_stage.setCurrentIndex(0)
            cases = 0
            for op, profile in module.catalog()['operators'].items():
                for skill in range(1, len(profile['skills']) + 1):
                    choose(op, skill)
                    for owner, key, supported, widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget) == (owner == op and skill in supported), (op, skill, key)
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    assert 'deployment_reference' not in window.damage_result['result']
                    cases += 1
            assert cases == 87
            state = json.dumps(window.run.state)
            assert 'deployment_hp_ratio' not in state and 'deployment_loss_unused' not in state
            assert not window.desktop.process and not isolated.joinpath('chat').exists()
            receipt = {'version': '0.27.0', 'passed': True, 'verified_at': time.time(),
                'seconds': round(time.perf_counter() - start, 3),
                'skill_option_visibility_cases': cases, 'deployment_input_scoped_to_selected_relic': True,
                'per_skill_preview_isolation': True, 'recalculation_does_not_deduct_twice': True,
                'already_consumed_event_loss_zero': True, 'unrounded_cost_and_actual_unknown_visible': True,
                'resident_stage_and_normal_stage_scoped': True, 'unknown_hp_combination_visible': True,
                'event_preview_not_saved_to_run': True, 'private_state_isolated': True,
                'game_captures': 0, 'chat_requests': 0,
                'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
                    'rouge/app.py', 'rouge/reporting.py', 'rouge/deployment.py', 'rouge/data/relic-mechanics.json')},
                'limits': ['Offscreen application wiring; no new live acquisition or game combat measurement.']}
            (ROOT / 'UI_0.27_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({k: receipt[k] for k in ('passed', 'skill_option_visibility_cases', 'seconds')}, ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
