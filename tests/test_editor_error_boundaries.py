"""Editable JSON errors are distinct from failures in application code."""
import unittest
import sys
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from rouge.route_constraints_view import RouteConstraintsPanel, _Worker
from rouge.route_resident_review_view import ResidentRouteReviewPanel
from rouge.route_continuation_view import RouteContinuationPanel
from rouge.route_resource_ledger_view import RouteResourceLedgerPanel
from rouge.route_scenarios_view import RouteScenarioMatrixPanel
from rouge.offline_tools_view import OfflineToolsPanel


class EditorErrorBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_child_examples_load_once_after_controls_exist(self):
        for kind, control in ((RouteContinuationPanel, 'failure_match'),
                              (RouteResourceLedgerPanel, 'passive_select'),
                              (RouteScenarioMatrixPanel, 'scenario_select')):
            with self.subTest(panel=kind.__name__):
                reads = []
                original = kind._load_example
                def load(panel):
                    reads.append(getattr(panel, control).count())
                    return original(panel)
                with patch.object(kind, '_load_example', load):
                    panel = kind()
                self.addCleanup(panel.close)
                self.assertEqual(len(reads), 1)
                self.assertIsInstance(panel._payload(), dict)

    def test_editor_errors_report_but_programmer_errors_propagate(self):
        cases = ((RouteConstraintsPanel, ('_apply_node', '_import_graph')),
                 (ResidentRouteReviewPanel, ('_add_resident', '_declare_victory', '_import_graph')),
                 (RouteContinuationPanel, ('_set_failure',)))
        for kind, methods in cases:
            panel = kind()
            self.addCleanup(panel.close)
            panel.set_graph({'nodes': []})
            for method in methods:
                with self.subTest(panel=kind.__name__, method=method):
                    with patch.object(panel, '_payload', side_effect=ValueError('输入格式错误')):
                        getattr(panel, method)()
                    self.assertIn('输入格式错误', panel.status.text())
                    with patch.object(panel, '_payload', side_effect=RuntimeError('内部错误')):
                        with self.assertRaisesRegex(RuntimeError, '内部错误'):
                            getattr(panel, method)()

    def test_task_boundary_still_reports_unexpected_failure(self):
        worker = _Worker(7, {})
        received = []
        worker.signals.finished.connect(lambda *args: received.append(args))
        with patch('rouge.route_constraints_view.constrained_routes', side_effect=RuntimeError('计算失败')):
            worker.run()
        self.assertEqual(received, [(7, None, '计算失败')])

    def test_shared_parser_preserves_valid_zero_and_rejects_invalid_json(self):
        for kind in (RouteConstraintsPanel, ResidentRouteReviewPanel):
            panel = kind()
            self.addCleanup(panel.close)
            for raw in ('{', '[]', '{"action_points": NaN}'):
                with self.subTest(panel=kind.__name__, raw=raw):
                    panel.editor.setPlainText(raw)
                    with self.assertRaises(ValueError):
                        panel._payload()
            panel.editor.setPlainText('{"action_points": 0}')
            self.assertEqual(panel._payload(), {'action_points': 0})

    def test_offline_run_parses_editor_once(self):
        panel = OfflineToolsPanel()
        self.addCleanup(panel.close)
        panel.select_query('exploration', 'targets')
        with patch.object(panel, '_payload', wraps=panel._payload) as read:
            with patch('rouge.offline_tools_view.QThreadPool.globalInstance') as pool:
                panel._run()
            read.assert_called_once()
            pool.return_value.start.assert_called_once()

    def test_offline_entry_does_not_hide_internal_errors(self):
        panel = OfflineToolsPanel()
        self.addCleanup(panel.close)
        panel.select_query('battle', 'compare')
        panel.set_stage('ro6_n_1_2')
        for method in ('_run', '_import_stage'):
            with self.subTest(method=method):
                with patch.object(panel, '_payload', side_effect=ValueError('输入格式错误')):
                    getattr(panel, method)()
                self.assertIn('输入格式错误', panel.status.text())
                with patch.object(panel, '_payload', side_effect=RuntimeError('内部错误')):
                    with self.assertRaisesRegex(RuntimeError, '内部错误'):
                        getattr(panel, method)()

    def test_editor_change_parses_one_snapshot_for_linked_controls(self):
        for kind in (ResidentRouteReviewPanel, RouteResourceLedgerPanel, RouteScenarioMatrixPanel):
            panel = kind()
            self.addCleanup(panel.close)
            for text in (panel.editor.toPlainText() + ' ', '{'):
                with self.subTest(panel=kind.__name__, valid=text != '{'):
                    with patch.object(panel, '_payload', wraps=panel._payload) as read:
                        panel.editor.setPlainText(text)
                    read.assert_called_once()

    def test_partial_nested_inputs_do_not_raise_from_widget_signals(self):
        texts = ('{', '{}', '{"graph": 3}', '{"graph": {"nodes": 3}}',
                 '{"routes": [3], "scenarios": [3]}',
                 '{"routes": [{"id": "r", "steps": null}]}',
                 '{"scenarios": [{"id": "s", "inventory": null}]}')
        for kind in (RouteConstraintsPanel, ResidentRouteReviewPanel, RouteResourceLedgerPanel,
                     RouteScenarioMatrixPanel, RouteContinuationPanel):
            panel = kind()
            self.addCleanup(panel.close)
            with patch.object(sys, 'excepthook') as unhandled:
                for text in texts:
                    panel.editor.setPlainText(text)
                self.qt.processEvents()
            with self.subTest(panel=kind.__name__):
                unhandled.assert_not_called()

    def test_linked_readers_do_not_silence_programmer_errors(self):
        for kind, methods in (
            (RouteConstraintsPanel, ('_refresh_nodes',)),
            (ResidentRouteReviewPanel, ('_editor_changed', '_refresh_steps', '_update_victory_button')),
            (RouteScenarioMatrixPanel, ('_editor_changed', '_refresh_scenario_fields', '_refresh_uses')),
            (RouteContinuationPanel, ('_editor_changed',)),
        ):
            panel = kind()
            self.addCleanup(panel.close)
            with patch.object(panel, '_payload', side_effect=RuntimeError('内部错误')):
                for method in methods:
                    with self.subTest(panel=kind.__name__, method=method):
                        with self.assertRaisesRegex(RuntimeError, '内部错误'):
                            getattr(panel, method)()
