"""Actual Windows public MainWindow check; no game/chat/private-state access."""
import argparse
from copy import deepcopy
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
    parser.add_argument('--visible-ms', type=int, default=4000)
    args = parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
    from rouge.skill_data_cost_reference import source_data
    if not source_data()['valid']:
        raise RuntimeError('Unbound skill data cost source')
    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py',
             'rouge/information_scope.py', 'rouge/skill_data_cost_reference.py',
             'tests/test_skill_data_cost_independent_278.py',
             'scripts/verify_skill_data_cost_window_278.py'}
    files.update(p.relative_to(ROOT).as_posix()
                 for p in (ROOT / 'research/p2-skill-data-cost-278').rglob('*') if p.is_file())
    before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-278-skill-data-') as state:
        temp = Path(state)
        app_module.ROOT = temp
        app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'
        app_module.RUN_STATE = temp / 'run.json'
        w = PublicWindow()
        w.resize(1500, 1050)
        w.setWindowTitle('第278节 · 技能费用逐次修饰（独立条件）')
        w.show()
        panel = w.offline_tools
        panel.select_query('calibration', 'sp-data')
        w.centralWidget().setCurrentWidget(panel)
        panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000:
                        raise TimeoutError('Public cost query stalled')
                    QTimer.singleShot(100, check)
                    return
                data = panel.result_snapshot()
                assert data is not None, panel.status.text()
                assert data == run_offline_query('calibration', 'sp-data', public_payload('calibration', 'sp-data'))
                assert data['source']['valid'] and data['rows']
                assert {row['kind'] for row in data['rows']} == {
                    'rune_mul', 'rune_add', 'relic_mul', 'scale_cost', 'replace_cost'}
                for key in ('actual_cost_after', 'actual_sp_after', 'complete_cycle'):
                    assert data[key] is None and all(row[key] is None for row in data['rows'])
                assert any(row['encoder_argument_reference'] is None for row in data['rows'])
                assert any(row['stored_prefixes'] for row in data['rows'])
                assert any(row['update_arguments'] for row in data['rows'])
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 33
                assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                rendered = panel.result_view.toPlainText()
                for phrase in ('技能费用', '逐次', '最近偶数取整', '实际费用、实际技力与完整技能周期：未知'):
                    assert phrase in rendered, phrase
                snapshot = (panel.current_query(), panel.editor.toPlainText(), deepcopy(data),
                            panel.result_view.toHtml(), panel.result_view.verticalScrollBar().value())
                panel.set_scenario({'operator': 'mechanist', 'skill': 2})
                gui.processEvents()
                assert not panel.import_scenario.isEnabled()
                assert snapshot == (panel.current_query(), panel.editor.toPlainText(), panel.result_snapshot(),
                                    panel.result_view.toHtml(), panel.result_view.verticalScrollBar().value())
                assert w.isVisible() and not w.auto.isChecked()
                assert w.capture.target is None and w.desktop.process is None
                after = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
                assert before == after
                report = {'passed': True, 'qpa': gui.platformName(), 'visible': True,
                          'query': ['calibration', 'sp-data'], 'public_rows': len(data['rows']),
                          'all_five_cost_kinds': True, 'exact_domain_and_inexact_unknown_displayed': True,
                          'independent_encoding_and_update_prefix_displayed': True,
                          'actual_cost_SP_cycle_unknown': True, 'calibration_and_battle_queries': 33,
                          'exploration_product_queries': 9, 'historical_exploration_queries': 13,
                          'scenario_import_disabled': True, 'refresh_preserved_input_result_selection_scroll': True,
                          'loaded_source_sha256': before, 'source_sha256_after': after,
                          'private_state_read': False, 'temporary_state_root': True,
                          'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                          'scope': 'Actual isolated current public Windows MainWindow; not game or private integration.'}
            except BaseException as error:
                report = {'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error)},
                          'loaded_source_sha256': before, 'private_state_read': False,
                          'temporary_state_root': True, 'game_operated': False, 'chat_sent': False}
                gui.exit(1)
            destination = Path(args.receipt)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

        QTimer.singleShot(500, check)
        QTimer.singleShot(args.visible_ms, w.close)
        return gui.exec()


if __name__ == '__main__':
    raise SystemExit(main())
