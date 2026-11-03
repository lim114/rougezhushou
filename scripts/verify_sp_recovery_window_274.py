"""Actual natural-SP MainWindow using public temporary state only."""
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
    from rouge.sp_recovery_clock import source_data
    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
             'rouge/sp_recovery_clock.py', 'rouge/data/sp-recovery-clock-source.json',
             'rouge/mechanist_explosion_math.py', 'tests/test_sp_recovery_clock.py',
             'scripts/verify_sp_recovery_window_274.py'}
    source = source_data()
    if source is None:
        raise RuntimeError('natural SP timer sources failed binding before window creation')
    files.update(source['source_artifacts_sha256'])
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-274-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicWindow(); window.resize(1550, 1100)
        window.setWindowTitle('第274节 · 自然技力批量时钟（隔离独立读取）'); window.show()
        panel = window.offline_tools; panel.select_query('calibration', 'sp-clock')
        window.centralWidget().setCurrentWidget(panel); panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000: raise TimeoutError('public natural-SP query did not return')
                    QTimer.singleShot(100, check); return
                result = panel.result_snapshot(); assert result is not None, panel.status.text()
                assert result == run_offline_query('calibration', 'sp-clock', public_payload('calibration', 'sp-clock'))
                assert result['source_valid'] and result['declared_chain_complete']
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 29
                assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                first, second, third = result['rows']
                assert first['tick']['updated_remaining_raw_reference'] == -3221225472
                assert first['tick']['quotient_raw_reference'] == 12884901888
                assert first['tick']['floor_count_reference'] == 3 and first['tick']['batch_count_reference'] == 4
                assert first['tick']['recovery']['sp_read_raw_reference'] == 21474836480
                assert first['tick']['recovery']['getter_called_reference']
                assert first['tick']['recovery']['setter_value_argument_raw_reference'] == 38654705664
                assert second['tick']['batch_count_reference'] == 1
                assert second['tick']['next_advanced_reference']
                assert not second['tick']['recovery']['getter_called_reference']
                assert not second['tick']['recovery']['setter_called_reference']
                assert third['recovery']['sp_read_raw_reference'] == 38654705664
                assert not third['recovery']['stop_read_called_reference']
                assert third['recovery']['setter_value_argument_raw_reference'] == 30064771072
                assert result['declared_complete_setter_request_count'] == 2
                assert result['final_period_raw_reference'] == result['final_remaining_raw_reference'] == 1073741824
                assert all(result[key] is None for key in ('actual_sp_after', 'actual_complete_recovery', 'actual_skill_cycle',
                                                          'actual_clock', 'actual_attribute_values'))
                assert not result['events_scheduled'] and not result['hotfix_equivalence_proven']
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
                          'main_window_public_query': list(panel.current_query()),
                          'calibration_and_battle_query_count': 29,
                          'current_product_exploration_query_count': 9,
                          'explicit_historical_exploration_query_count': 13,
                          'public_first_and_second_batch_counts': [4, 1],
                          'independent_sp_read_raw_references': [21474836480, 38654705664],
                          'setter_argument_raw_references': [38654705664, 30064771072],
                          'second_pause_skipped_sp_access_after_next': True,
                          'force_negative_skipped_stop_read': True,
                          'declared_complete_setter_request_count': 2,
                          'final_period_and_remaining_raw_reference': 1073741824,
                          'actual_sp_recovery_cycle_clock_and_attributes_unknown': True,
                          'scenario_import_disabled_for_independent_sp_clock': True,
                          'refresh_preserved_editor_result_selection_and_scroll': True,
                          'loaded_source_sha256': loaded, 'source_sha256_after': after_sources,
                          'private_state_read': False, 'temporary_state_root': True,
                          'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                          'scope': 'Actual changed MainWindow/public natural-SP declarations only; not actual game/controller/cache/SP acceptance/private/native-history validation'}
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
