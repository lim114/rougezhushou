"""Actual Qt report capture only; this is not the full UI validation suite."""
import hashlib
import json
import platform
import sys
import tempfile
import traceback
from copy import deepcopy
from pathlib import Path

ROOT = Path(r'Z:\workspace\rougezhushou')
OUT = Path(r'Z:\workspace\.compat')
sys.path.insert(0, str(ROOT))


def source_hashes():
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / 'rouge').rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}


before = source_hashes()
receipt = {'scope': 'Actual isolated MainWindow human/technical report diagnostic capture; not a full UI validation',
           'diagnostic_only': True, 'passed': False, 'capture_complete': False,
           'complete_ui_validation': False, 'native_windows_verified': False,
           'game_captures': 0, 'chat_requests': 0, 'private_state_isolated': True,
           'platform': platform.platform(), 'source_sha256': before, 'cases': []}
window = app = None
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QTextCursor
    from PySide6.QtWidgets import QApplication, QPushButton
    import rouge.app as module
    from rouge.reporting import format_report
    with tempfile.TemporaryDirectory() as folder:
        isolated = Path(folder)
        module.RUN_STATE = isolated / 'run.json'
        module.OPERATOR_STATE = isolated / 'operators.json'
        module.SETTINGS = isolated / 'settings.json'
        backend = module.DesktopBackend
        module.DesktopBackend = lambda _path, callback: backend(isolated / 'chat', callback)
        app = QApplication([])
        window = module.MainWindow()
        window.show()
        app.processEvents()
        assert window.isVisible() and not window.auto.isChecked()
        assert window.capture.target is None and not window.desktop.process
        window.centralWidget().setCurrentIndex(1)
        window.auto_relics.setChecked(False)
        window.use_run_training.setChecked(True)
        window.limit_window.setChecked(True)
        window.window_seconds.setValue(3)
        rid = 'rogue_6_relic_cargo_10'
        for index in range(window.relic_list.count()):
            item = window.relic_list.item(index)
            item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) == rid
                               else Qt.CheckState.Unchecked)
        op = 'silverash'
        fields = {'elite': 2, 'level': 90, 'potential': 1, 'trust': 100,
                  'module_id': None, 'module_level': 0}
        button = next(b for b in window.findChildren(QPushButton)
                      if b.text() == '计算属性与技能预估')
        for frames in (True, False):
            window.frame_timing.setChecked(frames)
            for kind in (None, 'unknown', 'non_emergency', 'emergency_hire'):
                member = {'id': op, 'scope': 'run', 'present': True,
                          'fields': deepcopy(fields), 'skill_ranks': {'1': 10, '2': 10, '3': 10},
                          'recruitment_kind': kind, 'char_buff_ids': [], 'char_buffs_complete': False}
                window.run.state['operators'] = {op: member}
                window.operator_observations[op] = {**deepcopy(member), 'scope': 'account'}
                window.select_operator(op)
                assert window.operator.currentData() == op
                window.update_operator()
                window.skill.setCurrentIndex(window.skill.findData(3))
                window.timing_scenario.clear()
                window.damage_technical.setChecked(False)
                button.click()
                app.processEvents()
                assert window.damage_result, window.damage_text.toPlainText()
                result = window.damage_result['result']
                record = next(r for r in result['relic_resolution']['records'] if r['id'] == rid)
                actual_human = window.damage_text.toPlainText()
                assert actual_human == format_report(result).replace(chr(160), ' ')
                captured = {'mode': 'frames' if frames else 'continuous', 'recruitment_kind': kind,
                            'scenario': deepcopy(window.damage_result['scenario']),
                            'record': deepcopy(record), 'warnings_raw': list(result['estimate']['warnings']),
                            'actual_human_text': actual_human,
                            'human_known_condition_label_visible': any(label in actual_human for label in
                                ('应急雇佣来源', '应急雇佣身份', '本局应急来源', '应急身份')),
                            'human_internal_key_visible': 'emergency_hire' in actual_human}
                if frames and kind is None:
                    window.damage_text.moveCursor(QTextCursor.MoveOperation.Start)
                    assert window.damage_text.find('同行者')
                    window.damage_text.ensureCursorVisible()
                    app.processEvents()
                    screenshot = OUT / 'wine-emergency-diagnostic-human-060.png'
                    assert window.grab().save(str(screenshot))
                    captured['human_screenshot'] = screenshot.name
                window.damage_technical.setChecked(True)
                app.processEvents()
                actual_technical = window.damage_text.toPlainText()
                assert actual_technical == format_report(result, technical=True).replace(chr(160), ' ')
                captured['actual_technical_text'] = actual_technical
                captured['technical_internal_key_visible'] = 'emergency_hire' in actual_technical
                captured['training_status_text'] = window.training_status.text()
                receipt['cases'].append(captured)
        assert len(receipt['cases']) == 8
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not isolated.joinpath('chat').exists()
        receipt['capture_complete'] = receipt['passed'] = True
        window.close()
        app.processEvents()
        window = None
except BaseException as error:
    receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
                          'traceback': traceback.format_exc()}
finally:
    if window is not None:
        window.close()
        if app is not None:
            app.processEvents()
    after = source_hashes()
    receipt['source_sha256_after'] = after
    receipt['source_drift'] = [name for name in sorted(set(before) | set(after))
                               if before.get(name) != after.get(name)]
    if receipt['source_drift']:
        receipt['capture_complete'] = receipt['passed'] = False
    path = OUT / 'wine-emergency-diagnostic-060.json'
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'diagnostic_only': True, 'capture_complete': receipt['capture_complete'],
                      'complete_ui_validation': False, 'cases_captured': len(receipt['cases']),
                      'receipt': str(path), 'failure': receipt.get('failure'),
                      'source_drift': receipt['source_drift']}, ensure_ascii=False))
    sys.exit(0 if receipt['passed'] else 1)
