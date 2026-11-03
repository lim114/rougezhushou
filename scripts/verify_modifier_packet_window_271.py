"""Actual public packet-reference MainWindow; never reads real private state."""
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
    from rouge.offline_tools_view import public_payload, run_offline_query
    from rouge.modifier_packet_reference import source_data
    gui = QApplication([])
    files = {
        'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
        'rouge/modifier_packet_reference.py', 'rouge/data/modifier-packet-source.json',
        'rouge/mechanist_explosion_math.py', 'rouge/shield_source_inventory.py',
        'tests/test_modifier_packet_reference.py', 'scripts/verify_modifier_packet_window_271.py',
    }
    source = source_data()
    if source is None:
        raise RuntimeError('packet sources failed binding before window creation')
    files.update(source['source_artifacts_sha256'])
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-271-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicWindow()
        window.setWindowTitle('第271节 · 藏品逐包修饰与独立顺序（隔离公开声明）')
        window.resize(1550, 1100); window.show()
        panel = window.offline_tools
        panel.select_query('calibration', 'modifier-values')
        window.centralWidget().setCurrentWidget(panel)
        panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000:
                        raise TimeoutError('public packet query did not return in verification window')
                    QTimer.singleShot(100, check); return
                result = panel.result_snapshot()
                assert result is not None, panel.status.text()
                expected = run_offline_query('calibration', 'modifier-values', public_payload('calibration', 'modifier-values'))
                assert result == expected
                assert result['known_discrete_raw_references'] == [9380208443390, 9380208443391]
                assert result['declared_order_combination_count'] == 36
                assert not result['order_counts_are_probabilities'] and not result['events_scheduled']
                unknown = ('actual_modifier_value', 'actual_hp_loss', 'actual_healing', 'actual_complete_total',
                           'actual_order', 'actual_probability_by_order')
                assert all(result[key] is None for key in unknown)
                assert window.isVisible() and window.centralWidget().currentWidget() is panel
                before = (panel.editor.toPlainText(), panel.result_view.toHtml(), panel.current_query(),
                          panel.result_snapshot(), panel.result_view.verticalScrollBar().value())
                panel.set_scenario({'operator': 'kaltsit', 'skill': 1}); gui.processEvents()
                assert not panel.import_scenario.isEnabled()
                after = (panel.editor.toPlainText(), panel.result_view.toHtml(), panel.current_query(),
                         panel.result_snapshot(), panel.result_view.verticalScrollBar().value())
                assert before == after
                assert not window.auto.isChecked() and window.capture.target is None
                assert window.desktop.process is None
                source_after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
                assert loaded == source_after, 'source changed during window validation'
                report = {
                    'passed': True, 'qpa': gui.platformName(), 'visible': window.isVisible(),
                    'main_window_public_query': list(panel.current_query()),
                    'literal_healing_discrete_raw_references': result['known_discrete_raw_references'],
                    'declared_order_combination_count': 36,
                    'actual_modifier_hp_healing_complete_total_and_order_unknown': True,
                    'order_counts_not_probabilities': True,
                    'scenario_import_disabled_for_independent_packet': True,
                    'refresh_preserved_editor_result_selection_and_scroll': True,
                    'loaded_source_sha256': loaded, 'source_sha256_after': source_after,
                    'private_state_read': False, 'temporary_state_root': True,
                    'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                    'scope': 'Actual Windows changed MainWindow/public packet declarations only; not complete game/private/native-history validation',
                }
            except BaseException as error:
                report = {
                    'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error)},
                    'loaded_source_sha256': loaded, 'private_state_read': False,
                    'temporary_state_root': True, 'game_operated': False, 'chat_sent': False,
                }
                gui.exit(1)
            path = Path(args.receipt); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

        QTimer.singleShot(500, check)
        QTimer.singleShot(args.visible_ms, window.close)
        return gui.exec()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        # Preserve a failed receipt even when construction/query selection fails
        # before the timer callback. No success or loaded-source claim is made.
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
