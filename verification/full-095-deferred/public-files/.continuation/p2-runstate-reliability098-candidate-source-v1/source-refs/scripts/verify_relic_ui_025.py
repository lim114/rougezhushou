"""Isolated Qt wiring; no game capture, private settings, or chat requests."""
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
import rouge.app as module


class OfflineWindow(module.MainWindow):
    def refresh_windows(self):
        self.windows.clear()


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
        def select_relic(rid):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item = window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) == rid
                                   else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.relic_context.clear()
            window.calculate()
        def select_op(op, skill):
            window.operator.setCurrentIndex(window.operator.findData(op))
            window.skill.setCurrentIndex(window.skill.findData(skill))
            window.calculate()
            assert window.damage_result, window.damage_text.toPlainText()
        def binding(bid, checked):
            item = next((window.target_buff_list.item(i) for i in range(window.target_buff_list.count())
                         if window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole) == bid), None)
            assert item is not None, bid
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            window.calculate()
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            window.auto_relics.setChecked(False)
            select_op('mechanist', 3)
            select_relic('rogue_6_relic_cargo_11')
            assert window.damage_form.isRowVisible(window.relic_context)
            assert 'fire_rod_stacks' in window.relic_context.placeholderText()
            assert '任意战斗' in window.relic_context.toolTip()
            window.relic_context.setPlainText('{"fire_rod_stacks":99}')
            assert window.damage_result
            text = window.damage_text.toPlainText()
            assert '攻速：1,090' in text and '攻击间隔使用攻速 600' in text, text
            assert 'fire_rod_stacks' not in json.dumps(window.run.state)
            select_relic(None)
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert 'fire_rod_stacks' not in window.damage_result['scenario']['relic_context']
            select_op('char_151_myrtle', 1)
            window.target_buff_test.setChecked(True)
            binding('rogue_6_from_relic_15', True)
            assert window.damage_result['result']['estimate']['skill']['initial_seconds'] == 5
            assert '个人强化测试' in window.damage_text.toPlainText()
            select_op('mechanist', 3)
            assert 'rogue_6_from_relic_15' not in window.damage_result['scenario']['char_buff_ids']
            binding('rogue_6_from_relic_15', True)
            assert window.damage_result['result']['estimate']['skill']['sp_recovery_per_second'] == 1.8
            window.skill.setCurrentIndex(window.skill.findData(1))
            assert window.damage_result['result']['relic_resolution']['records'][0]['status'] == 'inapplicable'
            window.skill.setCurrentIndex(window.skill.findData(3))
            window.target_buff_test.setChecked(False)
            select_relic('rogue_6_relic_legacy_56')
            assert '【关卡目标与环境修正】' not in window.damage_text.toPlainText()
            window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_1_2'))
            index = next(i for i in range(window.target_enemy.count())
                         if (window.target_enemy.itemData(i) or {}).get('enemy_id') == 'enemy_1093_ccsbr')
            window.target_enemy.setCurrentIndex(index)
            assert window.damage_result['result']['run_resolution']['enemy']['stats']['massLevel'] == -1
            assert '预计重量：-1' in window.damage_text.toPlainText()
            assert '不据此计算位移' in window.damage_text.toPlainText()
            select_relic(None)
            assert '预计重量：' not in window.damage_text.toPlainText()
            window.target_stage.setCurrentIndex(0)
            skills = 0
            for op, profile in module.catalog()['operators'].items():
                for skill in range(1, len(profile['skills']) + 1):
                    select_op(op, skill)
                    for owner, key, supported, widget in window.model_option_widgets:
                        expected = owner == op and skill in supported
                        assert window.damage_form.isRowVisible(widget) == expected, (op, skill, key)
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    skills += 1
            assert skills == 87, skills
            assert not window.desktop.process and not window.auto.isChecked()
            assert not isolated.joinpath('chat').exists()
            state = json.dumps(window.run.state)
            assert 'fire_rod_stacks' not in state and 'rogue_6_from_relic_15' not in state
            receipt = {'version': '0.25.0', 'verified_at': time.time(),
                'seconds': round(time.perf_counter() - start, 3), 'passed': True,
                'fire_count_input_and_raw_as_cap': True, 'removed_relic_hides_condition': True,
                'cookie_binding_scoped_to_current_operator': True, 'cookie_attack_recovery_inapplicable': True,
                'gravity_target_display_and_negative_weight': True, 'weight_hidden_without_modifier': True,
                'skill_option_visibility_cases': skills, 'preview_not_saved_to_run': True,
                'private_state_isolated': True, 'game_captures': 0, 'chat_requests': 0,
                'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                  for p in ('rouge/app.py', 'rouge/reporting.py', 'rouge/data/relic-mechanics.json')},
                'limits': ['Offscreen wiring only; no new live acquisition of these three relics.']}
            (ROOT / 'UI_0.25_VERIFICATION.json').write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(receipt, ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
