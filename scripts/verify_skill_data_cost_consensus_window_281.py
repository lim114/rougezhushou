"""Actual isolated Windows MainWindow fixture; promote before running. No game/chat."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import traceback

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt)
    if destination.exists():
        raise FileExistsError('Preserve the first receipt; use a new receipt path.')
    before = {}

    def write_report(report):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError('The fixture does not overwrite a prior receipt.')
        destination.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

    def failure_report(error):
        return {'passed': False,
                'failure': {'type': type(error).__name__, 'message': str(error),
                            'traceback': traceback.format_exc()},
                'loaded_source_sha256': before, 'private_state_read': False,
                'temporary_state_root': True, 'game_operated': False,
                'game_captures': 0, 'chat_sent': False}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('This fixture requires actual Windows, not compatibility/headless validation.')
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from rouge import app as app_module
        from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
        from rouge.skill_data_cost_consensus_reference import source_data, SINGLE_KINDS, SINGLE_STAGES
        from rouge.skill_data_cost_reference import skill_data_cost_reference
        if not source_data()['valid']:
            raise RuntimeError('Unbound complete skill-data consensus source')
        files = {'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py',
                 'rouge/information_scope.py', 'rouge/skill_data_cost_consensus_reference.py',
                 'rouge/skill_data_cost_reference.py', 'rouge/skill_cost_rounding_consensus.py',
                 'tests/test_skill_data_cost_consensus_independent_281.py',
                 'scripts/verify_skill_data_cost_consensus_window_281.py'}
        for directory in ('p2-skill-data-cost-consensus-281', 'p2-skill-data-cost-278',
                          'p2-cost-rounding-consensus-280'):
            packet = ROOT / 'research' / directory
            if not packet.is_dir():
                raise FileNotFoundError(str(packet))
            files.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
        gui = QApplication([])
        if gui.platformName() != 'windows':
            raise RuntimeError('A non-Windows QPA cannot prove the actual Windows window.')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-281-complete-cost-consensus-') as state:
            temp = Path(state)
            app_module.ROOT = temp
            app_module.SETTINGS = temp / 'settings.json'
            app_module.OPERATOR_STATE = temp / 'operators.json'
            app_module.RUN_STATE = temp / 'run.json'
            w = PublicWindow()
            w.resize(1500, 1050)
            w.setWindowTitle('第281节 · 技能费用共识接入完整流程（条件参考）')
            w.show()
            panel = w.offline_tools
            panel.select_query('calibration', 'sp-data-consensus')
            w.centralWidget().setCurrentWidget(panel)
            panel.run_button.click()
            elapsed = [0]
            checked = [False]
            failed = [False]

            def check():
                try:
                    if panel._workers:
                        elapsed[0] += 100
                        if elapsed[0] > 15000:
                            raise TimeoutError('Public complete cost consensus query stalled')
                        QTimer.singleShot(100, check)
                        return
                    data = panel.result_snapshot()
                    assert data is not None, panel.status.text()
                    public = public_payload('calibration', 'sp-data-consensus')
                    assert set(public) == {'sp_data_consensus'}
                    assert data == run_offline_query('calibration', 'sp-data-consensus', public)
                    assert data['source']['valid'] and len(data['rows']) == 11
                    assert data['source']['method_count'] == 32 and data['source']['byte_span_count'] == 4034
                    assert {row['kind'] for row in data['rows']} == {
                        'rune_add', 'rune_mul', 'relic_mul', 'scale_cost', 'replace_cost'}
                    assert [row['encoder_argument_reference'] for row in data['rows'][:7]] == [
                        2, None, 21, 10, None, 50, None]

                    def stage(row, name):
                        return next(s for s in row['stages'] if s['name'] == name)

                    for index in (0, 1, 2, 3, 4, 5):
                        row = data['rows'][index]
                        assert row['normal'] is True
                        assert stage(row, 'encode')['called'] is True and stage(row, 'encode')['normal'] is True
                        assert stage(row, 'store')['called'] is True and stage(row, 'store')['normal'] is True
                        assert row['stored_prefixes'] == [{
                            'field': 'spCost', 'byte_count': 20,
                            'payload_identity': public['sp_data_consensus']['actions'][index]['encoded_payload_identity'],
                            'decoded_value': None}]
                    for index in (1, 4):
                        encoded = stage(data['rows'][index], 'encode')['reference']
                        assert encoded['argument'] is None and encoded['argument_known'] is False
                        assert encoded['returned_payload'] is None
                    assert stage(data['rows'][1], 'encode')['reference']['argument_candidates'] == [0, 1]
                    assert stage(data['rows'][4], 'encode')['reference']['argument_candidates'] == []
                    unknown = data['rows'][6]
                    assert unknown['normal'] is None and not unknown['stored_prefixes']
                    assert stage(unknown, 'round')['called'] is True and stage(unknown, 'round')['normal'] is None
                    assert stage(unknown, 'encode')['called'] is None and stage(unknown, 'store')['called'] is None
                    assert stage(data['rows'][5], 'cost_decode')['reference']['value'] == 101

                    old = skill_data_cost_reference(public['sp_data_consensus'])
                    non_single_count = 0
                    for row, original in zip(data['rows'], old['rows']):
                        if row['kind'] in SINGLE_KINDS:
                            assert tuple(s['name'] for s in row['stages']) == SINGLE_STAGES
                            assert row['update_arguments'] is None
                        else:
                            non_single_count += 1
                            assert {k: v for k, v in row.items()
                                    if k not in ('calculation_route', 'consensus_reference')} == original
                    assert non_single_count == 4
                    for key in ('actual_cost_after', 'actual_sp_after', 'complete_cycle'):
                        assert data[key] is None and all(row[key] is None for row in data['rows'])
                    assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 36
                    assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                    rendered = panel.result_view.toPlainText()
                    for phrase in ('共识已接入完整费用流程',
                                   '整数未知仍可保留正常的保护值复制前缀',
                                   '实际费用、实际技力与完整技能周期：未知'):
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
                              'query': ['calibration', 'sp-data-consensus'], 'payload_key': 'sp_data_consensus',
                              'public_rows': 11, 'all_five_cost_kinds': True,
                              'single_consensus_integer_to_complete_store': True,
                              'opaque_normal_encode_and_twenty_byte_store': True,
                              'unknown_round_does_not_claim_store': True,
                              'single_no_owner_update_appended': True,
                              'legacy_non_single_rows_unchanged': non_single_count,
                              'independent_next_decoded_cost': True,
                              'actual_cost_SP_cycle_unknown': True,
                              'calibration_and_battle_queries': 36,
                              'exploration_product_queries': 9, 'historical_exploration_queries': 13,
                              'scenario_import_disabled': True,
                              'refresh_preserved_input_result_selection_scroll': True,
                              'loaded_source_sha256': before, 'source_sha256_after': after,
                              'private_state_read': False, 'temporary_state_root': True,
                              'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                              'new_native_fresh_methods_claimed': 0,
                              'new_native_fresh_spans_claimed': 0,
                              'scope': 'Actual isolated current public Windows MainWindow; not game or private integration.'}
                except BaseException as error:
                    report = failure_report(error)
                    failed[0] = True
                checked[0] = True
                write_report(report)
                if failed[0]:
                    gui.exit(1)

            def close():
                if not checked[0]:
                    error = TimeoutError('Window closed before a checked result was obtained')
                    write_report(failure_report(error))
                    failed[0] = True
                w.close()

            QTimer.singleShot(500, check)
            QTimer.singleShot(max(20000, args.visible_ms), close)
            result = gui.exec()
            if not checked[0] and not destination.exists():
                write_report(failure_report(RuntimeError('The actual window exited before verification')))
                failed[0] = True
            return 1 if failed[0] else result
    except BaseException as error:
        if not destination.exists():
            write_report(failure_report(error))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
