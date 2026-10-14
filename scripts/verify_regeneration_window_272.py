"""Actual recovery-clock MainWindow over public temporary state only."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
    from rouge.regeneration_clock import source_data
    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
        'rouge/regeneration_clock.py', 'rouge/data/regeneration-clock-source.json',
        'rouge/mechanist_explosion_math.py', 'tests/test_regeneration_clock.py', 'scripts/verify_regeneration_window_272.py'}
    source = source_data()
    if source is None:
        raise RuntimeError('recovery timer sources failed binding before window creation')
    files.update(source['source_artifacts_sha256'])
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-272-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicWindow(); window.resize(1550, 1100)
        window.setWindowTitle('第272节 · 常态生命回复时钟（隔离独立读取）'); window.show()
        panel = window.offline_tools; panel.select_query('calibration', 'regen-clock')
        window.centralWidget().setCurrentWidget(panel); panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000: raise TimeoutError('public regeneration query did not return')
                    QTimer.singleShot(100, check); return
                result = panel.result_snapshot(); assert result is not None, panel.status.text()
                assert result == run_offline_query('calibration', 'regen-clock', public_payload('calibration', 'regen-clock'))
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 27
                assert len(PRODUCT_QUERIES['exploration']) == 9
                assert result['final_period_raw_reference'] == result['final_remaining_raw_reference'] == 1073741824
                assert result['declared_complete_request_count'] == 4
                requests = result['rows'][2]['drain']['requests']
                assert [row['setter_value_argument_raw_reference'] for row in requests] == [3869765533696, 3874060500992, 3878355468288, 3882650435584]
                assert all(result[key] is None for key in ('actual_attribute_values', 'actual_clock', 'actual_hp_after', 'actual_complete_healing'))
                assert not result['events_scheduled']
                before = (panel.editor.toPlainText(), panel.result_view.toHtml(), panel.current_query(),
                          panel.result_snapshot(), panel.result_view.verticalScrollBar().value())
                panel.set_scenario({'operator': 'kaltsit', 'skill': 1}); gui.processEvents()
                assert not panel.import_scenario.isEnabled()
                after = (panel.editor.toPlainText(), panel.result_view.toHtml(), panel.current_query(),
                         panel.result_snapshot(), panel.result_view.verticalScrollBar().value())
                assert before == after
                assert window.isVisible() and window.centralWidget().currentWidget() is panel
                assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
                after_sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
                assert after_sources == loaded, 'source changed during window validation'
                report = {'passed': True, 'qpa': gui.platformName(), 'visible': window.isVisible(),
                    'main_window_public_query': list(panel.current_query()), 'calibration_and_battle_query_count': 27,
                    'current_product_exploration_query_count': 9,
                    'final_period_and_remaining_raw_reference': 1073741824,
                    'independent_setter_argument_raw_references': [row['setter_value_argument_raw_reference'] for row in requests],
                    'declared_complete_request_count': 4, 'actual_clock_hp_and_complete_healing_unknown': True,
                    'scenario_import_disabled_for_independent_clock': True,
                    'refresh_preserved_editor_result_selection_and_scroll': True,
                    'loaded_source_sha256': loaded, 'source_sha256_after': after_sources,
                    'private_state_read': False, 'temporary_state_root': True,
                    'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                    'scope': 'Actual changed MainWindow/public timer declarations only; not complete game/private/native-history validation'}
            except BaseException as error:
                report = {'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error)},
                    'loaded_source_sha256': loaded, 'private_state_read': False, 'temporary_state_root': True,
                    'game_operated': False, 'chat_sent': False}
                gui.exit(1)
            path = Path(args.receipt); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

        QTimer.singleShot(500, check); QTimer.singleShot(args.visible_ms, window.close)
        return gui.exec()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        destination = next((arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('--receipt=')), None)
        if destination is None and '--receipt' in sys.argv:
            index = sys.argv.index('--receipt')
            if index + 1 < len(sys.argv): destination = sys.argv[index + 1]
        if destination:
            path = Path(destination); path.parent.mkdir(parents=True, exist_ok=True)
            report = {'passed': False, 'phase': 'startup_before_timer',
                'failure': {'type': type(error).__name__, 'message': str(error)},
                'loaded_source_verified': False, 'private_state_read': False,
                'temporary_state_root': True, 'game_operated': False, 'chat_sent': False}
            path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
        raise SystemExit(1)
