"""User-approved worker boundaries and removal of rendering fallbacks."""
import importlib
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.offline_tools_view import OfflineToolsPanel, _QueryWorker
from rouge.route_scenarios_view import RouteScenarioMatrixPanel


class ExistingDefenseDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_all_six_approved_workers_deliver_unexpected_errors(self):
        targets = (
            ('route_constraints_view', 'constrained_routes'),
            ('route_resident_review_view', 'review_resident_routes'),
            ('route_resource_ledger_view', 'route_resource_ledger'),
            ('route_scenarios_view', 'scenario_route_matrix'),
            ('route_continuation_view', 'continue_route_plan'),
            ('offline_tools_view', 'run_offline_query'),
        )
        for name, calculation in targets:
            with self.subTest(module=name):
                module = importlib.import_module('rouge.' + name)
                worker = _QueryWorker(7, 'calibration', 'panel', {}) if name == 'offline_tools_view' else module._Worker(7, {})
                received = []
                worker.signals.finished.connect(lambda *args: received.append(args))
                with patch.object(module, calculation, side_effect=RuntimeError('计算内部错误')):
                    worker.run()
                self.assertEqual(len(received), 1)
                self.assertEqual(received[0][0], 7)
                self.assertIsNone(received[0][-2])
                self.assertIn('计算内部错误', received[0][-1])

    def test_scenario_renderer_error_is_no_longer_swallowed(self):
        panel = RouteScenarioMatrixPanel()
        self.addCleanup(panel.close)
        panel._contexts[panel._serial] = {'graph': {}, 'links': {}, 'input_text': ''}
        with patch('rouge.route_scenarios_view.render_scenario_matrix', side_effect=RuntimeError('显示内部错误')):
            with self.assertRaisesRegex(RuntimeError, '显示内部错误'):
                panel._finished(panel._serial, {}, '')
        self.assertTrue(panel.run_button.isEnabled())

    def test_offline_renderer_error_is_no_longer_swallowed(self):
        panel = OfflineToolsPanel()
        self.addCleanup(panel.close)
        panel._worker_context[panel._serial] = {'payload': {}, 'bindings': {}, 'origin': 'fixture'}
        with patch('rouge.offline_tools_view.render_offline_result', side_effect=RuntimeError('显示内部错误')):
            with self.assertRaisesRegex(RuntimeError, '显示内部错误'):
                panel._finished(panel._serial, *panel.current_query(), {}, '')
        self.assertTrue(panel.run_button.isEnabled())

    def test_approved_sixteen_input_boundaries_only_handle_input_errors(self):
        targets = (
            ('route_constraints_view', 'RouteConstraintsPanel', ('_run',)),
            ('route_resident_review_view', 'ResidentRouteReviewPanel', ('_run',)),
            ('route_continuation_view', 'RouteContinuationPanel', ('_set_progress', '_set_current_after', '_import_graph', '_run')),
            ('route_resource_ledger_view', 'RouteResourceLedgerPanel', ('_set_activation', '_set_after_battle', '_set_terminal', '_run')),
            ('route_scenarios_view', 'RouteScenarioMatrixPanel', ('_set_scenario_ap', '_set_snapshot_uses', '_run')),
            ('offline_tools_view', 'OfflineToolsPanel', ('_import_scenario', '_import_graph', '_fill_node')),
        )
        for name, kind, methods in targets:
            panel = getattr(importlib.import_module('rouge.' + name), kind)()
            self.addCleanup(panel.close)
            panel.set_graph({'nodes': []})
            for method in methods:
                if name == 'offline_tools_view':
                    if method == '_import_scenario':
                        panel.select_query('calibration', 'panel')
                        panel.set_scenario({'operator': 'kaltsit', 'level': 90, 'skill': 2})
                    else:
                        panel.select_query('exploration', 'targets')
                with self.subTest(module=name, method=method):
                    with patch.object(panel, '_payload', side_effect=ValueError('输入格式错误')):
                        getattr(panel, method)()
                    self.assertIn('输入格式错误', panel.status.text())
                    with patch.object(panel, '_payload', side_effect=RuntimeError('内部错误')):
                        with self.assertRaisesRegex(RuntimeError, '内部错误'):
                            getattr(panel, method)()
