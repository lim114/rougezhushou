"""Actual recovery-attribute MainWindow with public temporary state only.

No live capture, game input, chat send or private-state fixture is permitted.
"""
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
    from rouge.recovery_attributes import source_data
    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
             'rouge/recovery_attributes.py', 'rouge/data/recovery-attribute-source.json',
             'rouge/regeneration_clock.py', 'rouge/data/regeneration-clock-source.json',
             'rouge/mechanist_explosion_math.py', 'tests/test_recovery_attributes.py',
             'scripts/verify_recovery_attributes_window_273.py'}
    source = source_data()
    if source is None:
        raise RuntimeError('recovery attribute sources failed binding before window creation')
    files.update(source['source_artifacts_sha256'])
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-273-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicWindow(); window.resize(1550, 1100)
        window.setWindowTitle('第273节 · 常态回复属性与缓存（隔离独立读取）'); window.show()
        panel = window.offline_tools; panel.select_query('calibration', 'regen-attributes')
        window.centralWidget().setCurrentWidget(panel); panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000:
                        raise TimeoutError('public recovery-attribute query did not return')
                    QTimer.singleShot(100, check); return
                result = panel.result_snapshot(); assert result is not None, panel.status.text()
                assert result == run_offline_query('calibration', 'regen-attributes', public_payload('calibration', 'regen-attributes'))
                assert result['source_valid']
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 28
                assert len(PRODUCT_QUERIES['exploration']) == 9
                assert len(QUERIES['exploration']) == 13
                assert [row['getter_raw_reference'] for row in result['rows']] == [81604379520, 510027372, 81604379520, 510027372]
                assert [row['buckets_reference']['multiplier_delta'] for row in result['rows']] == [8160437952] * 4
                channels = sorted((entry['relic_id'], entry['attribute'], entry['source_buff_index'], entry['parameter_fp_raw'])
                                  for entry in source['flower_channels'])
                assert channels == [('rogue_6_relic_legacy_81', 13, 1, 858993472),
                                    ('rogue_6_relic_legacy_81', 19, 2, 858993472),
                                    ('rogue_6_relic_legacy_82', 13, 1, 1288490240),
                                    ('rogue_6_relic_legacy_82', 19, 2, 1288490240),
                                    ('rogue_6_relic_legacy_83', 13, 1, 1717986944),
                                    ('rogue_6_relic_legacy_83', 19, 2, 1717986944)]
                clock = result['clock_reference']; assert clock['declared_chain_complete']
                rates = [clock['rows'][0]['can_recover']['rate_raw_reference'], clock['rows'][0]['period_rate']['rate_raw_reference']]
                assert rates == [132607116720, 132607116720]
                assert all(link['qualified'] for link in result['clock_links'])
                assert [link['point'] for link in result['clock_links']] == ['can_recover_snapshot', 'period_snapshot']
                assert all(result[key] is None for key in ('actual_attribute_values', 'actual_cache_or_dirty_state', 'actual_clock',
                                                          'actual_hp_after', 'actual_complete_healing'))
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
                          'calibration_and_battle_query_count': 28,
                          'current_product_exploration_query_count': 9,
                          'explicit_historical_exploration_query_count': 13,
                          'qualified_flower_attribute_channel_count': 6,
                          'qualified_attribute_raw_references': [row['getter_raw_reference'] for row in result['rows']],
                          'independent_can_recover_and_period_rate_raw_references': rates,
                          'actual_attributes_clock_hp_and_complete_healing_unknown': True,
                          'scenario_import_disabled_for_independent_attribute_reads': True,
                          'refresh_preserved_editor_result_selection_and_scroll': True,
                          'loaded_source_sha256': loaded, 'source_sha256_after': after_sources,
                          'private_state_read': False, 'temporary_state_root': True,
                          'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                          'scope': 'Actual changed MainWindow/public FP attribute declarations only; not actual inventory/cache/game/private/native-history validation'}
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
