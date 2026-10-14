"""Actual public initialization-prefix MainWindow; isolated state, no capture/chat.

Draft script. Run only after the production query and source manifest are bound.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = next(path for path in Path(__file__).resolve().parents if (path / 'rouge/app.py').exists())
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--query', default='sp-init')
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
    from rouge.sp_initialization_reference import SOURCE, source_data, natural_clock_link
    from rouge.sp_recovery_clock import public_example as clock_example

    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
             'rouge/sp_initialization_reference.py', SOURCE,
             'rouge/sp_recovery_clock.py', 'rouge/data/sp-recovery-clock-source.json',
             'rouge/mechanist_explosion_math.py', 'tests/test_sp_initialization_reference.py',
             'scripts/verify_sp_initialization_window_276.py'}
    source = source_data()
    if source is None:
        raise RuntimeError('Initialization/lifecycle sources failed binding before window creation')
    files.update(source['source_artifacts_sha256'])
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-276-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicWindow(); window.resize(1550, 1100)
        window.setWindowTitle('第276节 · 初始技力、容量与数据切换（独立声明）'); window.show()
        panel = window.offline_tools; panel.select_query('calibration', args.query)
        window.centralWidget().setCurrentWidget(panel); panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000: raise TimeoutError('Public initialization query did not return')
                    QTimer.singleShot(100, check); return
                result = panel.result_snapshot(); assert result is not None, panel.status.text()
                assert result == run_offline_query('calibration', args.query, public_payload('calibration', args.query))
                assert result['source_valid']
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 31
                assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                constructors = [row for row in result['rows'] if row['kind'] == 'construct']
                initializers = [row for row in result['rows'] if row['kind'] == 'entity_init']
                cost_updates = [row for row in result['rows'] if row['kind'] == 'entity_update']
                assert len(result['rows']) == 4
                assert len(constructors) == 1 and len(initializers) == 2 and len(cost_updates) == 1
                constructed = constructors[0]
                assert constructed['normal_return_reference']
                assert constructed['state_after_reference']['timer']['period_raw'] == 0
                assert constructed['state_after_reference']['timer']['remaining_raw'] == 0
                initialized = initializers[0]
                assert initialized['normal_return_reference']
                assert [reading['returned_max_sp_reference'] for reading in initialized['capacity_reads']] == [20, 21]
                assert initialized['initial_sp_prefix']['signed_min_reference'] == 20
                assert initialized['initial_sp_prefix']['encoder_constructor_argument_raw_reference'] == 85899345920
                assert initialized['initial_sp_prefix']['copied_byte_count_reference'] == 40
                assert initialized['state_after_reference']['max_sp'] == 21
                assert initialized['state_after_reference']['timer']['period_raw'] == 1073741824
                assert initialized['state_after_reference']['timer']['remaining_raw'] == 1073741824
                assert cost_updates[0]['normal_return_reference']
                assert cost_updates[0]['state_after_reference']['timer'] == initialized['state_after_reference']['timer']
                assert cost_updates[0]['state_after_reference']['max_sp'] == 27
                negative = initializers[-1]['initial_sp_prefix']
                assert negative['signed_min_reference'] == -5
                assert negative['encoder_constructor_argument_raw_reference'] == -21474836480
                assert negative['copied_byte_count_reference'] == 40
                assert initializers[-1]['state_after_reference']['max_sp'] == 15
                assert result['actual_current_sp'] is None and result['complete_cycle'] is None

                original = deepcopy(result); clock = clock_example(); old_clock = deepcopy(clock)
                linked = natural_clock_link(result, {
                    'after_action_id': constructed['id'], 'controller_exists': True,
                    'precise_timer_identity': True, 'no_intervening_timer_changes': True,
                    'actions': clock['actions']})
                assert linked['qualified_reference']
                assert linked['request']['timer'] == {'exists': True, 'period_raw': 0, 'remaining_raw': 0}
                assert result == original and clock == old_clock
                assert linked['actual_clock'] is None and linked['complete_cycle'] is None

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
                          'calibration_and_battle_query_count': 31,
                          'current_product_exploration_query_count': 9,
                          'explicit_historical_exploration_query_count': 13,
                          'default_constructor_period_and_remaining_raw': [0, 0],
                          'independent_first_and_second_max_sp': [20, 21],
                          'initial_signed_min': 20, 'initial_encoder_constructor_argument_raw': 85899345920,
                          'initial_opaque_sp_payload_copy_bytes': 40,
                          'reset_waitfirst_period_and_remaining_raw': [1073741824, 1073741824],
                          'entity_cost_only_writes_max_before_update_and_preserves_timer': True,
                          'negative_initial_sp_prefix_is_not_alive_or_zero_clamped': True,
                          'selected_constructor_snapshot_not_replaced_by_later_timer': True,
                          'independent_clock_request_and_report_preserved': True,
                          'actual_current_sp_and_complete_cycle_unknown': True,
                          'scenario_import_disabled_for_independent_initialization_declarations': True,
                          'refresh_preserved_editor_result_selection_and_scroll': True,
                          'loaded_source_sha256': loaded, 'source_sha256_after': after_sources,
                          'private_state_read': False, 'temporary_state_root': True,
                          'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                          'scope': 'Actual changed MainWindow/public source-prefix declarations only; not live controller/SP/codec/cycle/private/native-history validation'}
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
