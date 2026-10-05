"""Temporary Qt state; outgoing callbacks never become run memory or game input."""
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
from tests.test_event_sp_028 import HORN, WAVE, BOOK
from tests.test_received_sp_026 import TANK
from rouge.relics import matches, mechanics


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
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            window.auto_relics.setChecked(False)
            choose('mechanist', 3)
            relics(HORN)
            field = window.received_sp_scenario
            assert window.damage_form.isRowVisible(field)
            assert window.damage_form.labelForField(field).text() == '事件技力（局外测试）'
            assert 'kill=' in field.toolTip() and 'dealt_damage=' not in field.toolTip()
            horn_text = json.dumps({'initial': [{'at_seconds': t, 'type': 'kill'} for t in (1, 2, 3)],
                'cycle': [{'at_seconds': t, 'type': 'kill'} for t in (41, 42, 43)]})
            field.setPlainText(horn_text)
            assert window.damage_result['result']['estimate']['skill']['initial_seconds'] == 4
            assert window.damage_result['result']['estimate']['skill']['cycle_seconds'] == 69
            assert '本体击倒敌人' in window.damage_text.toPlainText()
            choose('mechanist', 1)
            assert field.toPlainText() == ''
            choose('mechanist', 3)
            assert field.toPlainText() == horn_text
            relics(WAVE)
            assert not window.damage_form.isRowVisible(field)
            assert 'sp_events' not in window.damage_result['scenario'].get('timing', {})
            choose('char_328_cammou', 2)
            assert window.damage_form.isRowVisible(field)
            assert 'dealt_damage=' in field.toolTip() and 'kill=' not in field.toolTip()
            wave_text = json.dumps({'initial': [{'at_seconds': t, 'type': 'dealt_damage'} for t in (1, 2, 3)],
                'cycle': [{'at_seconds': t, 'type': 'dealt_damage'} for t in (31, 32, 33)]})
            field.setPlainText(wave_text)
            assert window.damage_result['result']['estimate']['skill']['initial_seconds'] == 19
            assert window.damage_result['result']['estimate']['skill']['cycle_seconds'] == 69
            assert window.damage_result['result']['relic_resolution']['complete']
            window.frame_timing.setChecked(False)
            assert window.damage_result['result']['estimate']['skill']['initial_seconds'] == 19
            window.frame_timing.setChecked(True)
            choose('char_328_cammou', 1)
            assert field.toPlainText() == ''
            choose('char_328_cammou', 2)
            assert field.toPlainText() == wave_text
            relics(WAVE, BOOK)
            assert window.damage_form.isRowVisible(window.relic_context)
            window.relic_context.setPlainText('{"deployed_casters":2}')
            assert window.damage_result['result']['estimate']['skill']['cycle_seconds'] == 63
            assert '攻击叠层' in window.damage_text.toPlainText()
            assert not window.damage_result['result']['relic_resolution']['complete']
            choose('char_002_amiya', 1)
            assert not window.damage_form.isRowVisible(field)
            assert '攻击叠层' not in window.damage_text.toPlainText()
            relics(HORN)
            choose('char_1044_hsgma2', 1)
            interval = next(widget for owner, key, _, widget in window.model_option_widgets
                if owner == 'char_1044_hsgma2' and key == 'incoming_attack_interval')
            assert not window.damage_form.isRowVisible(interval)
            assert 'attack=' in field.toolTip() and 'kill=' in field.toolTip()
            assert 'incoming_attack_interval' not in window.damage_result['scenario']
            field.setPlainText('{"initial":' + json.dumps([{'at_seconds': 1, 'type': 'kill'}] * 8) + '}')
            assert window.damage_result['result']['estimate']['skill']['initial_seconds'] == 31 / 30
            relics()
            assert window.damage_form.isRowVisible(interval)
            assert not window.damage_form.isRowVisible(field)
            visibility_cases = skills = 0
            for op, profile in module.catalog()['operators'].items():
                for number in range(1, len(profile['skills']) + 1):
                    choose(op, number)
                    skills += 1
                    for rid in (HORN, WAVE):
                        relics(rid)
                        skill = profile['skills'][number - 1]['levels'][-1]
                        expected = skill['sp_type'] in ('INCREASE_WITH_TIME', 'INCREASE_WHEN_ATTACK', 'INCREASE_WHEN_TAKEN_DAMAGE') and matches(mechanics()['relics'][rid]['effects'][0], profile)
                        assert window.damage_form.isRowVisible(field) == expected, (op, number, rid)
                        if not expected:
                            assert 'sp_events' not in window.damage_result['scenario'].get('timing', {})
                        visibility_cases += 1
                    relics()
                    for owner, key, supported, widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget) == (owner == op and number in supported), (op, number, key)
            choose('mechanist', 3)
            window.target_buff_test.setChecked(True)
            item = next(window.target_buff_list.item(i) for i in range(window.target_buff_list.count())
                if window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole) == TANK)
            item.setCheckState(Qt.CheckState.Checked)
            window.calculate()
            assert window.damage_form.labelForField(field).text() == '受击技力事件（局外测试）'
            assert 'kill=' not in field.toolTip() and 'dealt_damage=' not in field.toolTip()
            assert 'attack=' in field.toolTip()
            assert skills == 87 and visibility_cases == 174
            state = json.dumps(window.run.state)
            assert 'sp_events' not in state and 'deployed_casters' not in state
            assert not window.desktop.process and not isolated.joinpath('chat').exists()
            receipt = {'version': '0.28.0', 'passed': True, 'verified_at': time.time(),
                'seconds': round(time.perf_counter() - start, 3), 'skill_option_visibility_cases': skills,
                'event_rule_visibility_cases': visibility_cases, 'per_operator_skill_preview_isolation': True,
                'outgoing_and_incoming_labels_scoped': True, 'inactive_rule_omits_event_scenario': True,
                'native_defensive_attack_tooltip_and_interval_protection': True,
                'wave_without_book_complete_and_with_book_attack_pending': True,
                'other_caster_has_no_wave_panel_or_synergy_warning': True,
                'event_preview_not_saved_to_run': True, 'private_state_isolated': True,
                'game_captures': 0, 'chat_requests': 0,
                'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
                    'rouge/app.py', 'rouge/reporting.py', 'rouge/sp_events.py', 'rouge/data/relic-mechanics.json')},
                'limits': ['Offscreen UI wiring; callback tables are explicit offline assumptions, no live combat reading.']}
            (ROOT / 'UI_0.28_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({k: receipt[k] for k in ('passed', 'skill_option_visibility_cases', 'event_rule_visibility_cases', 'seconds')}, ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
