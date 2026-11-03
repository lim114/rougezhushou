"""Actual isolated Windows main-panel fixture; promote before running.

Preparation alone is not a Windows receipt. No game, private state or chat is
used. This verifies the real panel query and shared report, not native code or
the already tested arithmetic algorithms.
"""
import argparse
from collections import Counter
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
        raise FileExistsError('Preserve the first receipt; choose a new receipt path.')
    before = {}
    completed = []
    facts = {}

    def write_report(report):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError('A prior actual receipt must not be overwritten.')
        destination.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

    def failure_report(error):
        return {'passed': False,
                'failure': {'type': type(error).__name__, 'message': str(error),
                            'traceback': traceback.format_exc()},
                'completed_checks': list(completed), 'observed_public_facts': deepcopy(facts),
                'loaded_source_sha256': before, 'private_state_read': False,
                'temporary_state_root': True, 'game_operated': False,
                'game_captures': 0, 'chat_sent': False,
                'scope': 'Actual Windows fixture failed; earlier checks are not whole-window acceptance.'}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual Windows is required; Wine/offscreen cannot prove this window.')
        promoted = ROOT / 'scripts/verify_panel_native_window_283.py'
        if Path(__file__).resolve() != promoted.resolve():
            raise RuntimeError('Promote the reviewed draft to scripts/ before actual execution.')
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from rouge import app as app_module
        from rouge.damage import calculate_damage
        from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
        from rouge.panel_native_finalization import source_data
        from rouge.reporting import format_report

        source = source_data()
        if source is None:
            raise RuntimeError('The current panel native source guard did not validate.')
        packet = ROOT / 'research/p2-panel-native-finalization-283'
        if not packet.is_dir():
            raise FileNotFoundError(str(packet))
        files = {
            'rouge/app.py', 'rouge/calibration.py', 'rouge/offline_tools_view.py',
            'rouge/information_scope.py', 'rouge/panel_native_finalization.py',
            'rouge/panel_native_precision.py', 'rouge/panel_native_bridge.py',
            'rouge/relic_attributes.py', 'rouge/estimate.py', 'rouge/operator_engine.py',
            'rouge/relics.py', 'rouge/damage.py', 'rouge/reporting.py',
            'rouge/catalog.py', 'rouge/data/catalog.json',
            'tests/test_panel_native_finalization_283.py',
            'scripts/verify_panel_native_window_283.py',
        }
        files.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        files.update(source['files'])
        before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
        gui = QApplication([])
        if gui.platformName() != 'windows':
            raise RuntimeError('This receipt requires the actual Windows QPA platform.')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-283-panel-native-') as state:
            temp = Path(state)
            app_module.ROOT = temp
            app_module.SETTINGS = temp / 'settings.json'
            app_module.OPERATOR_STATE = temp / 'operators.json'
            app_module.RUN_STATE = temp / 'run.json'
            w = PublicWindow()
            w.resize(1500, 1050)
            w.setWindowTitle('第283节 · 主面板四层原生算式与精度资格')
            w.show()
            panel = w.offline_tools
            panel.select_query('calibration', 'panel')
            w.centralWidget().setCurrentWidget(panel)
            public = public_payload('calibration', 'panel')
            assert set(public) == {'scenario'}
            assert public['scenario'] == {'operator': 'mechanist', 'skill': 3, 'charge_count': 0}
            # Whitespace does not alter the default public request; it gives
            # the editable view a real nonzero scroll position to preserve.
            panel.editor.setPlainText(json.dumps(public, ensure_ascii=False, indent=2) + '\n' * 80)
            panel.run_button.click()
            elapsed = [0]
            checked = [False]
            failed = [False]
            phase = ['public']
            imported_scenario = {'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10,
                                 '_resolved_private_marker': 'must_be_stripped'}

            def snapshot():
                return (panel.current_query(), panel.editor.toPlainText(), deepcopy(panel.result_snapshot()),
                        panel.result_view.toHtml(), panel.raw_result.toPlainText(),
                        panel.technical.isChecked(),
                        panel.editor.verticalScrollBar().value(),
                        panel.result_view.verticalScrollBar().value(),
                        panel.raw_result.verticalScrollBar().value())

            def assert_isolated():
                assert w.isVisible() and not w.auto.isChecked()
                assert not w.timer.isActive()
                assert w.capture.target is None and w.desktop.process is None

            def validate_main_query(data, payload):
                assert data is not None, panel.status.text()
                assert data == run_offline_query('calibration', 'panel', payload)
                direct = calculate_damage(deepcopy(payload['scenario']))
                native = data['native_panel_reference']
                assert native == direct['panel_native_finalization']
                assert data['panels']['已覆盖常态天赋与效果'] == direct['estimate']['base_stats']
                assert native['source_valid'] is True
                assert len(native['fields']) == 17
                counts = Counter(row['phase'] for row in native['fields'])
                assert counts == {'cultivation': 5, 'rune': 5, 'normal': 5, 'skill': 2}
                assert set(native['phase_ids']) == {'cultivation', 'rune', 'normal', 'skill'}
                for name, count in counts.items():
                    assert len(native['phase_ids'][name]) == count
                assert native['complete_native_panel'] is False and native['actual_panel'] is None
                assert all(row['actual_decoded_value'] is None and row['actual_getter_raw'] is None
                           and row['complete_native_value'] is False for row in native['fields'])
                for row in native['fields']:
                    if row['phase'] in ('normal', 'skill'):
                        assert row['references']['writer'] is None
                provenance = native['input_provenance']
                assert provenance['basis'] == 'independent_nominal_model_snapshots'
                assert provenance['protected_parent_result_propagated'] is False
                assert provenance['normal_native_calls_inferred'] is False
                assert data['native_verified'] is False
                rendered = panel.result_view.toPlainText()
                for phrase in ('同一主结果 · 原生算式与精度核验', '完整原生值', '原生完整面板：未知'):
                    assert phrase in rendered, phrase
                report_text = format_report(direct)
                assert '面板算式与精度核验' in report_text
                assert '完整原生面板' in report_text
                assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 37
                assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                assert panel.query.count() == len(PRODUCT_QUERIES['calibration'])
                assert panel.current_query() == ('calibration', 'panel')
                assert_isolated()
                return native

            def check():
                try:
                    if panel._workers:
                        elapsed[0] += 100
                        if elapsed[0] > 20000:
                            raise TimeoutError('The actual public panel query did not finish.')
                        QTimer.singleShot(100, check)
                        return
                    data = panel.result_snapshot()
                    if phase[0] == 'public':
                        native = validate_main_query(data, public)
                        completed.append('public_mechanist3_panel_and_shared_main_result')
                        facts['initial_query'] = ['calibration', 'panel']
                        facts['initial_payload'] = deepcopy(public)
                        facts['native_field_count'] = len(native['fields'])
                        facts['phase_counts'] = dict(Counter(row['phase'] for row in native['fields']))
                        facts['legacy_base_stats'] = deepcopy(data['panels']['已覆盖常态天赋与效果'])
                        panel.technical.setChecked(True)
                        gui.processEvents()
                        # Changing an editor cursor is a view operation, not a
                        # second declaration. Apply scrolls after cursor moves.
                        cursor = panel.editor.textCursor()
                        cursor.setPosition(3)
                        cursor.setPosition(10, QTextCursor.MoveMode.KeepAnchor)
                        panel.editor.setTextCursor(cursor)
                        for widget in (panel.editor, panel.result_view, panel.raw_result):
                            bar = widget.verticalScrollBar()
                            assert bar.maximum() > 0, 'The view must really scroll before claiming scroll preservation.'
                            bar.setValue(max(1, bar.maximum() // 2))
                        saved = snapshot()
                        panel.set_scenario(imported_scenario)
                        gui.processEvents()
                        assert panel.import_scenario.isEnabled(), 'panel supports explicit current-scenario import.'
                        assert snapshot() == saved
                        completed.append('automatic_context_refresh_preserves_selection_input_result_and_nonzero_scroll')
                        facts['preserved_scroll_values'] = list(saved[-3:])
                        # This is an explicit public import, not an automatic
                        # context refresh. Existing panel behavior invalidates
                        # the old result until the user runs the new request.
                        panel.import_scenario.click()
                        imported = json.loads(panel.editor.toPlainText())
                        assert imported == {'scenario': {'operator': 'kaltsit', 'skill': 2, 'skill_rank': 10}}
                        assert panel.current_query() == ('calibration', 'panel')
                        assert panel.result_snapshot() is None
                        completed.append('explicit_scenario_import_enabled_and_internal_fields_stripped')
                        facts['explicit_import_payload'] = deepcopy(imported)
                        phase[0] = 'imported'
                        elapsed[0] = 0
                        panel.run_button.click()
                        QTimer.singleShot(100, check)
                        return
                    imported = facts['explicit_import_payload']
                    validate_main_query(data, imported)
                    completed.append('explicit_import_query_recomputed_in_same_real_panel')
                    saved = snapshot()
                    panel.set_scenario(public['scenario'])
                    gui.processEvents()
                    assert snapshot() == saved and panel.import_scenario.isEnabled()
                    completed.append('later_context_refresh_does_not_replace_imported_view')
                    after = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in sorted(files)}
                    assert before == after
                    assert_isolated()
                    completed.append('source_files_unchanged_and_no_capture_or_chat')
                    report = {
                        'passed': True, 'qpa': gui.platformName(), 'visible': True,
                        'completed_checks': list(completed), 'observed_public_facts': deepcopy(facts),
                        'query': ['calibration', 'panel'], 'payload_key': 'scenario',
                        'native_fields': 17, 'native_phases': 4,
                        'native_reference_is_same_main_result': True,
                        'legacy_base_stats_same_as_main_result': True,
                        'actual_panel_getter_decoded_values_unknown': True,
                        'normal_and_skill_do_not_invent_typed_writer': True,
                        'ordinary_report_contains_panel_native_section': True,
                        'calibration_and_battle_queries': 37,
                        'exploration_product_queries': 9, 'historical_exploration_queries': 13,
                        'refresh_preserved_selection_input_result_and_real_nonzero_scroll': True,
                        'scenario_import_enabled_and_exercised': True,
                        'scenario_import_invalidates_old_result_until_explicit_run': True,
                        'source_sha256_after': after, 'loaded_source_sha256': before,
                        'private_state_read': False, 'temporary_state_root': True,
                        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                        'new_native_primary_readback_performed_by_window': False,
                        'new_native_fresh_methods_claimed': 0, 'new_native_fresh_spans_claimed': 0,
                        'scope': 'Actual isolated Windows public MainWindow/panel and shared report; not private or game integration, native execution, current RC, full native panel, or codec roundtrip.'}
                except BaseException as error:
                    report = failure_report(error)
                    failed[0] = True
                checked[0] = True
                write_report(report)
                if failed[0]:
                    w.close()
                    gui.exit(1)

            def close():
                if not checked[0]:
                    write_report(failure_report(TimeoutError('The actual window closed before verification completed.')))
                    checked[0] = True
                    failed[0] = True
                w.close()

            QTimer.singleShot(500, check)
            QTimer.singleShot(max(25000, args.visible_ms), close)
            result = gui.exec()
            if not checked[0] and not destination.exists():
                write_report(failure_report(RuntimeError('The actual window exited before verification.')))
                failed[0] = True
            return 1 if failed[0] else result
    except BaseException as error:
        if not destination.exists():
            write_report(failure_report(error))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
