"""One actual isolated regression probe; expected to expose the current defect."""
import ast
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
NAMES = ('rouge/app.py', 'rouge/map_view.py', 'rouge/node_catalog_view.py',
         'rouge/peace_guardian_results.py', 'rouge/resident_location_references.py',
         'rouge/event_planning.py', 'rouge/player_node_information.py')
attempts = {}
observation = {}


def source_hashes():
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in NAMES}


def deny_private_reads(event, args):
    if event != 'open' or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    if path.is_relative_to(ROOT / '.local') or path == ROOT / 'local-settings.json':
        attempts['private_open'] = attempts.get('private_open', 0) + 1
        raise AssertionError('Original private runtime files must not be read')


def forbidden(name):
    def stopped(*_args, **_kwargs):
        attempts[name] = attempts.get(name, 0) + 1
        raise AssertionError('Forbidden external/whole-window operation: ' + name)
    return stopped


def main():
    before = source_hashes()
    sys.addaudithook(deny_private_reads)
    from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QLabel, QPlainTextEdit
    from rouge import app as app_module
    from rouge.map_view import MapView
    from rouge.node_catalog_view import NodeCatalogPanel
    fixture = ROOT / 'verification/sections/291-preparation/location-fixtures/fixtures/readable-map-047-graph.json'
    graph = json.loads(fixture.read_bytes())
    graph['nodes'][0]['observed_type'] = '“居民”据点'
    graph['nodes'][1]['remembered_type'] = '“居民”据点'
    gui = QApplication([])
    if gui.platformName() != 'offscreen':
        raise AssertionError('Only isolated offscreen reproduction is authorized')
    with tempfile.TemporaryDirectory(prefix='rouge-291-directory-button-') as directory, ExitStack() as stack:
        temp = Path(directory)
        for key, value in {'ROOT': temp, 'SETTINGS': temp / 'settings.json', 'OPERATOR_STATE': temp / 'operators.json', 'RUN_STATE': temp / 'run.json'}.items():
            stack.enter_context(patch.object(app_module, key, value))
        for owner, method, name in ((app_module, 'list_game_windows', 'game_enumeration'),
                (app_module.GameCapture, 'connect', 'game_connect'), (app_module.GameCapture, 'capture', 'game_capture'),
                (app_module.GameCapture, 'next_frame', 'game_next_frame'), (app_module.DesktopBackend, 'start', 'desktop_start'),
                (app_module.DesktopBackend, 'request', 'desktop_request'), (app_module, 'stream_chat', 'provider_chat'),
                (app_module, 'read_key', 'credential_read'), (app_module, 'save_key', 'credential_write'),
                (app_module.MainWindow, '__init__', 'whole_main_window'), (app_module.RunState, '__init__', 'run_state_constructor'),
                (app_module.AccountCache, '__init__', 'account_state_constructor')):
            stack.enter_context(patch.object(owner, method, side_effect=forbidden(name)))
        view, panel = MapView(), NodeCatalogPanel()
        controls = [QLabel(), QPlainTextEdit(), QCheckBox(), QComboBox()]
        tabs = []
        class CallbackHolder:
            pass
        holder = CallbackHolder()
        holder.__dict__.update(map_view=view, node_catalog=panel,
            include_historical_route_diagnostics=False,
            run=types.SimpleNamespace(state={'id': 'isolated-public-run', 'config': {}}),
            map_route=controls[0], map_detail=controls[1], map_technical=controls[2],
            map_nodes=controls[3], map_detail_key=None, exploration_map_tab='isolated-map-tab',
            centralWidget=lambda: types.SimpleNamespace(setCurrentWidget=tabs.append))
        for name in ('map_node_selected', 'map_reference_node_selected', 'show_catalog_map_node', 'show_selected_map_node_contents'):
            setattr(holder, name, types.MethodType(getattr(app_module.MainWindow, name), holder))
        view.nodeSelected.connect(holder.map_node_selected)
        view.referenceNodeSelected.connect(holder.map_reference_node_selected)
        panel.mapNodeSelected.connect(holder.show_catalog_map_node)
        panel.bind_button.clicked.disconnect(panel.bind_current_node)
        panel.bind_button.clicked.connect(holder.show_selected_map_node_contents)
        holder.map_nodes.addItem('请选择地图上的节点', None)
        for node in graph['nodes']:
            holder.map_nodes.addItem(node['id'], node['id'])
        view.set_map(deepcopy(graph), historical=False)
        panel.set_map_context(graph, {'floor': 4}, epoch='isolated-public-run', historical=False)
        panel.search.setText('和平守卫者')
        panel.list.setCurrentRow(next(index for index, entry in enumerate(panel.entries)
            if entry['kind'] == 'event' and entry['record']['id'] == 'community_group_019'))

        class DirectoryReferenceButtonProbe(unittest.TestCase):
            def test_selected_reference_without_prior_context_exposes_explicit_view(self):
                self.assertIsNone(panel.node_context)
                self.assertIsNone(panel.dossier)
                self.assertFalse(panel.bind_button.isEnabled())
                self.assertIsNone(view.selected)
                old_key = panel.detail_key
                panel.resident_location.setCurrentIndex(1)
                self.assertTrue(panel.resident_map_button.isEnabled())
                panel.resident_map_button.click()
                gui.processEvents()
                self.assertEqual(view.selected, '0,2')
                self.assertEqual(holder.map_nodes.currentData(), '0,2')
                self.assertIsNone(panel.node_context)
                self.assertIsNone(panel.dossier)
                self.assertEqual(panel.detail_key, old_key)
                observation.update(selected_node=view.selected, node_context_is_none=True,
                    dossier_is_none=True, event_reading_preserved=panel.detail_key == old_key,
                    reference_binding_present=view.reference_binding is not None,
                    explicit_view_button_enabled=panel.bind_button.isEnabled(),
                    assistant_tab_requests=list(tabs))
                print(json.dumps(observation, ensure_ascii=False), flush=True)
                self.assertTrue(panel.bind_button.isEnabled(), 'A valid manually selected map reference must expose the explicit-view button even without any prior node_context.')

        try:
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DirectoryReferenceButtonProbe))
        finally:
            panel.close(); view.close()
            for widget in controls:
                widget.close()
            gui.processEvents()
        after = source_hashes()
        record = {'kind': 'ACTUAL_ISOLATED_DIRECTORY_REFERENCE_BUTTON_REPRODUCTION',
            'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'expected_product_contract_violated': observation.get('explicit_view_button_enabled') is False and len(result.failures) == 1 and not result.errors,
            'observation': observation, 'source_before': before, 'source_after': after,
            'source_unchanged': before == after, 'operation_attempts': attempts,
            'all_runtime_paths_redirected_before_widget_construction': True,
            'whole_main_window_constructed': False, 'actual_game_or_chat_operations': 0,
            'QPA': gui.platformName(), 'not_native_window_acceptance': True,
            'private_runtime_contents_read_or_copied': False}
        (OUT / 'actual-reproduction.json').write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        if before != after or attempts:
            raise AssertionError('Reproduction altered source or attempted a prohibited operation')
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
