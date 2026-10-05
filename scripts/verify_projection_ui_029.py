"""Simple testing interface checks with temporary state and no game or chat target."""
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
from PySide6.QtWidgets import QApplication
from scripts.verify_relic_ui_025 import OfflineWindow, module


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
        try:
            assert '0.29' in window.windowTitle()
            assert not window.auto.isChecked() and window.capture.target is None
            cases = 0
            for op, profile in module.catalog()['operators'].items():
                window.operator.setCurrentIndex(window.operator.findData(op))
                for number in range(1, len(profile['skills']) + 1):
                    window.skill.setCurrentIndex(window.skill.findData(number))
                    window.calculate()
                    assert window.damage_result, window.damage_text.toPlainText()
                    for owner, key, supported, widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget) == (owner == op and number in supported), (op, number, key)
                    assert not window.damage_form.isRowVisible(window.received_sp_scenario)
                    assert not window.damage_form.isRowVisible(window.relic_context)
                    cases += 1
            assert cases == 87
            assert not window.desktop.process and not (isolated / 'chat').exists()
            assert 'sp_events' not in json.dumps(window.run.state)
            receipt = {'version': '0.29.0', 'passed': True, 'verified_at': time.time(),
                'seconds': round(time.perf_counter() - start, 3), 'skill_option_visibility_cases': cases,
                'private_state_isolated': True, 'no_irrelevant_special_fields': True,
                'game_captures': 0, 'chat_requests': 0,
                'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
                    'rouge/app.py', 'rouge/relic_recognition.py', 'rouge/reporting.py')},
                'limits': ['Offscreen UI wiring only; matching replay and queued flow are separately verified.']}
            (ROOT / 'UI_0.29_VERIFICATION.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({k: receipt[k] for k in ('passed', 'skill_option_visibility_cases', 'seconds')}, ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
