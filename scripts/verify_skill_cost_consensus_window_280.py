"""Actual public Windows MainWindow checks; no game/chat/private-state access."""
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
    from rouge.skill_cost_rounding_consensus import source_data
    if not source_data()['valid']:
        raise RuntimeError('Unbound skill cost consensus source')
    files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py',
             'rouge/information_scope.py', 'rouge/skill_cost_rounding_consensus.py',
             'tests/test_skill_cost_rounding_consensus_independent_280.py',
             'scripts/verify_skill_cost_consensus_window_280.py'}
    files.update(p.relative_to(ROOT).as_posix()
                 for p in (ROOT / 'research/p2-cost-rounding-consensus-280').rglob('*') if p.is_file())
    before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
    gui = QApplication([])

    class PublicWindow(app_module.MainWindow):
        def refresh_windows(self):
            self.windows.clear()

    with tempfile.TemporaryDirectory(prefix='rouge-280-cost-consensus-') as state:
        temp = Path(state)
        app_module.ROOT = temp
        app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'
        app_module.RUN_STATE = temp / 'run.json'
        w = PublicWindow()
        w.resize(1500, 1050)
        w.setWindowTitle('第280节 · 技能费用相容结果（条件参考）')
        w.show()
        panel = w.offline_tools
        panel.select_query('calibration', 'sp-cost-consensus')
        w.centralWidget().setCurrentWidget(panel)
        panel.run_button.click()
        elapsed = [0]

        def check():
            try:
                if panel._workers:
                    elapsed[0] += 100
                    if elapsed[0] > 15000:
                        raise TimeoutError('Public cost consensus query stalled')
                    QTimer.singleShot(100, check)
                    return
                data = panel.result_snapshot()
                assert data is not None, panel.status.text()
                assert data == run_offline_query('calibration', 'sp-cost-consensus', public_payload('calibration', 'sp-cost-consensus'))
                assert data['source']['valid'] and len(data['rows']) == 10
                assert {row['kind'] for row in data['rows']} == {'rune_add', 'rune_mul', 'relic_mul'}
                expected = [2, None, 21, None, 0, None, -2, 10, 50, None]
                assert [row['encoder_argument_reference'] for row in data['rows']] == expected
                refs = [row['consensus_reference'] for row in data['rows']]
                assert refs[1]['integer_candidates'] == [0, 1]
                assert refs[3]['integer_candidates'] == [31, 32]
                assert refs[5]['integer_candidates'] == [16777216, 16777218]
                for key in ('actual_cost_after', 'actual_sp_after', 'complete_cycle'):
                    assert data[key] is None and all(row[key] is None for row in data['rows'])
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 35
                assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                rendered = panel.result_view.toPlainText()
                for phrase in ('所有允许的正常舍入结果一致时才给整数参考', '相容整数有分歧',
                               '对象资格、编码和写入需要独立核对', '实际费用、当前技力与完整周期：未知'):
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
                          'query': ['calibration', 'sp-cost-consensus'], 'public_rows': 10,
                          'all_three_cost_kinds': True, 'consensus_and_ambiguous_public_rows': True,
                          'expanded_inexact_domain_without_default_RC': True,
                          'independent_next_decoded_cost': True, 'encoder_or_store_called_not_claimed': True,
                          'actual_cost_SP_cycle_unknown': True, 'calibration_and_battle_queries': 35,
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
