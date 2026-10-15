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
