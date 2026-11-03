"""UNEXECUTED DRAFT: real MapView signals and narrowly qualified App callbacks.

These methods do not replace the isolated native bound-event window acceptance.
No MainWindow is constructed here; all App callback holders are public in-memory
objects. Origin means UI viewing intent, never eligibility or an actual target.
"""
from copy import deepcopy
import types
import unittest
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow
from rouge.map_view import MapView
from rouge.resident_location_references import resident_location_references
from tests.test_readable_map_047 import graph as original_graph


def source_graph():
    result = original_graph()
    result['nodes'][0]['observed_type'] = '“居民”据点'
    result['nodes'][1]['remembered_type'] = '“居民”据点'
    return result


class ResidentReferenceSignal291Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.view = MapView()
        self.addCleanup(self.view.close)
        self.graph = source_graph()
        self.view.set_map(self.graph, historical=False)
        self.binding = resident_location_references(self.graph, epoch='public-run', historical=False)['rows'][0]['binding']

    def test_reference_path_copies_full_binding_and_emits_only_dedicated_signal(self):
        regular, reference = [], []
        self.view.nodeSelected.connect(regular.append)
        self.view.referenceNodeSelected.connect(reference.append)
        saved = deepcopy(self.binding)
        self.view.select_node('0,2', emit_selected=False, reference_binding=self.binding)
        self.assertEqual(reference, ['0,2'])
        self.assertEqual(regular, [])
        self.assertEqual(self.view.selected, '0,2')
        self.binding['grid']['rows'] = 99
        self.assertEqual(self.view.reference_binding, saved)

    def test_same_map_refresh_retains_reference_but_ordinary_selection_restores_old_flow(self):
        regular, reference = [], []
        self.view.nodeSelected.connect(regular.append)
        self.view.referenceNodeSelected.connect(reference.append)
        self.view.select_node('0,2', emit_selected=False, reference_binding=self.binding)
        self.view.set_map(deepcopy(self.graph), historical=False)
        self.assertEqual(reference, ['0,2', '0,2'])
        self.assertEqual(regular, [])
        self.assertEqual(self.view.reference_binding, self.binding)
        self.view.select_node('1,1')
        self.view.set_map(deepcopy(self.graph), historical=False)
        self.assertEqual(regular, ['1,1', '1,1'])
        self.assertEqual(reference, ['0,2', '0,2'])
        self.assertIsNone(self.view.reference_binding)

    def test_identity_or_removed_node_expires_origin_without_normal_signal_fallback(self):
        variants = []
        changed = deepcopy(self.graph); changed['template_id'] = 'public-other-template'; variants.append(changed)
        changed = deepcopy(self.graph); changed['nodes'] = changed['nodes'][1:]; variants.append(changed)
        for changed in variants:
            with self.subTest(graph=changed):
                view = MapView(); self.addCleanup(view.close)
                view.set_map(self.graph, historical=False)
                view.select_node('0,2', emit_selected=False, reference_binding=self.binding)
                regular, reference = [], []
                view.nodeSelected.connect(regular.append); view.referenceNodeSelected.connect(reference.append)
                view.set_map(changed, historical=False)
                self.assertEqual(reference, [''])
                self.assertEqual(regular, [])
                self.assertIsNone(view.selected)
                self.assertIsNone(view.reference_binding)

    def test_App_callback_checks_latest_epoch_history_coordinates_and_type_evidence(self):
        variants = []
        changed = deepcopy(self.graph); changed['nodes'][0]['col'] = 4; variants.append((changed, False, 'public-run'))
        changed = deepcopy(self.graph); changed['nodes'][0]['observed_type'] = '林间空地'; variants.append((changed, False, 'public-run'))
        variants.extend([(deepcopy(self.graph), True, 'public-run'),
                         (deepcopy(self.graph), False, 'same-map-IDs-in-different-run')])
        for graph, historical, epoch in variants:
            with self.subTest(graph=graph, historical=historical, epoch=epoch):
                view = MapView(); self.addCleanup(view.close)
                view.set_map(self.graph, historical=False)
                view.select_node('0,2', emit_selected=False, reference_binding=self.binding)
                calls, statuses = [], []
                holder = types.SimpleNamespace(map_view=view, run=types.SimpleNamespace(state={'id': 'public-run'}),
                    node_catalog=types.SimpleNamespace(status=types.SimpleNamespace(setText=statuses.append)),
                    map_node_selected=lambda node_id, **kwargs:calls.append((node_id, kwargs)))
                self.assertIs(MainWindow.map_reference_node_selected(holder, '0,2'), True)
                self.assertEqual(calls, [('0,2', {'update_catalog': False})])
                view.graph = graph; view.historical = historical; holder.run.state['id'] = epoch
                self.assertIs(MainWindow.map_reference_node_selected(holder, '0,2'), False)
                self.assertIsNone(view.reference_binding)
                self.assertIsNone(view.selected)
                self.assertEqual(calls[-1], ('', {'update_catalog': False}))
                self.assertIn('链接已过期', statuses[-1])

    def test_directory_reference_enables_explicit_view_without_prior_node_context(self):
        from contextlib import ExitStack
        from pathlib import Path
        import tempfile
        from unittest.mock import patch
        from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QPlainTextEdit
        from rouge import app as app_module
        from rouge.node_catalog_view import NodeCatalogPanel

        def forbidden(*_args, **_kwargs):
            raise AssertionError('No whole-window, game, chat, credential or private-state construction is needed')

        with tempfile.TemporaryDirectory(prefix='rouge-291-directory-view-') as directory, ExitStack() as stack:
            temporary = Path(directory)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                               'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, key, value))
            for owner, name in ((app_module.MainWindow, '__init__'), (app_module.RunState, '__init__'),
                                (app_module.AccountCache, '__init__'), (app_module, 'list_game_windows'),
                                (app_module.GameCapture, 'connect'), (app_module.GameCapture, 'capture'),
                                (app_module.GameCapture, 'next_frame'), (app_module.DesktopBackend, 'start'),
                                (app_module.DesktopBackend, 'request'), (app_module, 'stream_chat'),
                                (app_module, 'read_key'), (app_module, 'save_key')):
                stack.enter_context(patch.object(owner, name, side_effect=forbidden))
            panel = NodeCatalogPanel(); self.addCleanup(panel.close)
            controls = [QLabel(), QPlainTextEdit(), QCheckBox(), QComboBox()]
            for control in controls: self.addCleanup(control.close)
            class CallbackHolder:
                pass
            holder = CallbackHolder()
            holder.__dict__.update(map_view=self.view, node_catalog=panel,
                include_historical_route_diagnostics=False,
                run=types.SimpleNamespace(state={'id': 'public-run', 'config': {}}),
                map_route=controls[0], map_detail=controls[1], map_technical=controls[2],
                map_nodes=controls[3], map_detail_key=None, exploration_map_tab='isolated-map-tab',
                centralWidget=lambda:types.SimpleNamespace(setCurrentWidget=lambda _widget:None))
            for name in ('map_node_selected', 'map_reference_node_selected', 'show_catalog_map_node',
                         'show_selected_map_node_contents'):
                setattr(holder, name, types.MethodType(getattr(MainWindow, name), holder))
            self.view.nodeSelected.connect(holder.map_node_selected)
            self.view.referenceNodeSelected.connect(holder.map_reference_node_selected)
            panel.mapNodeSelected.connect(holder.show_catalog_map_node)
            panel.bind_button.clicked.disconnect(panel.bind_current_node)
            panel.bind_button.clicked.connect(holder.show_selected_map_node_contents)
            holder.map_nodes.addItem('请选择地图上的节点', None)
            for node in self.graph['nodes']: holder.map_nodes.addItem(node['id'], node['id'])
            panel.set_map_context(self.graph, {'floor': 4}, epoch='public-run', historical=False)
            panel.search.setText('和平守卫者')
            panel.list.setCurrentRow(next(index for index, entry in enumerate(panel.entries)
                if entry['kind']=='event' and entry['record']['id']=='community_group_019'))
            reading_key = panel.detail_key
            self.assertIsNone(panel.node_context)
            self.assertIsNone(panel.dossier)
            self.assertFalse(panel.bind_button.isEnabled())
            panel.resident_location.setCurrentIndex(1)
            panel.resident_map_button.click()
            self.assertEqual(self.view.selected, '0,2')
            self.assertTrue(panel.bind_button.isEnabled())
            self.assertIsNone(panel.node_context)
            self.assertIsNone(panel.dossier)
            self.assertEqual(panel.detail_key, reading_key)
            self.view.set_map(deepcopy(self.graph), historical=False)
            self.assertTrue(panel.bind_button.isEnabled())
            self.assertIsNone(panel.node_context)
            changed = deepcopy(self.graph); changed['nodes'][0]['observed_type'] = '林间空地'
            self.view.set_map(changed, historical=False)
            self.assertIsNone(self.view.selected)
            self.assertFalse(panel.bind_button.isEnabled())
            self.assertEqual(panel.detail_key, reading_key)
            self.view.set_map(deepcopy(self.graph), historical=False)
            panel.resident_map_button.click()
            self.assertTrue(panel.bind_button.isEnabled())
            panel.bind_button.click()
            self.assertEqual(panel.node_context[1], '0,2')
            self.assertEqual(panel.dossier['position']['node_id'], '0,2')
            self.assertIsNone(self.view.reference_binding)

    def test_explicit_view_without_current_selection_never_falls_back_to_old_context(self):
        calls, statuses, tabs = [], [], []
        panel = types.SimpleNamespace(node_context=(self.graph, '0,2', {}),
            status=types.SimpleNamespace(setText=statuses.append), bind_current_node=lambda:calls.append('bound'))
        holder = types.SimpleNamespace(map_view=self.view, node_catalog=panel,
            centralWidget=lambda:types.SimpleNamespace(setCurrentWidget=tabs.append))
        self.assertIsNone(self.view.selected)
        MainWindow.show_selected_map_node_contents(holder)
        self.assertEqual(calls, [])
        self.assertEqual(tabs, [])
        self.assertEqual(panel.node_context[1], '0,2')
        self.assertIn('地图当前没有可查看', statuses[-1])


if __name__ == '__main__':
    unittest.main()
