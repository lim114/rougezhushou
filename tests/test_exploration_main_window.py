"""Exploration workflow navigation in actual MainWindow, temporary public records."""
from copy import deepcopy
from collections import deque
import time,unittest
from PySide6.QtCore import QUrl
from urllib.parse import quote
from tests import test_batch185_mainwindow as setup_module


class ExplorationMainWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    def setUp(self):
        setup_module.Batch185WindowTests.setUp(self)
        # Explicitly opt this diagnostic workflow into its real tools dialog.
        # Keep information-only exploration and the ordinary product default.
        self.window.centralWidget().developer_tools=True
        self.assertFalse(self.window.include_historical_route_diagnostics)

    def test_imported_source_map_navigates_and_same_clock_new_id_rejects_old_result(self):
        from rouge.offline_tools_view import public_payload
        graph=deepcopy(public_payload('exploration','targets')['graph'])
        graph['grid']={'rows':max(n['row'] for n in graph['nodes'])+1,'cols':max(n['col'] for n in graph['nodes'])+1}
        graph['source']={'url':'https://example.invalid/public-mainwindow-ui-fixture'}
        # The API example has topology but no reporting distances; derive them
        # from its declared edges instead of inventing game observations.
        adjacent={n['id']:[] for n in graph['nodes']}
        for a,b in graph['edges']:adjacent[a].append(b);adjacent[b].append(a)
        start=graph.get('current_node') or graph['nodes'][0]['id'];distances={start:0};queue=deque([start])
        while queue:
            current=queue.popleft()
            for target in adjacent[current]:
                if target not in distances:distances[target]=distances[current]+1;queue.append(target)
        for node in graph['nodes']:node['distance']=distances.get(node['id'])
        graph.update(captured_at=self.window.run.state['started_at']+1)
        self.window.run.state['maps'][graph['zone_id']]=graph
        self.window.run.state['config']['zone']={'id':graph['zone_id']}
        self.window.render_map();panel=self.window.offline_tools
        panel.select_query('exploration','targets');self.window.centralWidget().setCurrentWidget(panel)
        panel.import_graph.click();editor=panel.editor.toPlainText();panel.run_button.click()
        end=time.monotonic()+8
        while panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(panel._workers);self.assertTrue(panel._result_links,panel.status.text())
        key=next(iter(panel._result_links));url=QUrl('rouge-map-node:'+quote(key,safe=''))
        panel.result_view.anchorClicked.emit(url)
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.exploration_map_tab)
        self.assertEqual(self.window.map_view.selected,key)
        self.assertEqual(panel.editor.toPlainText(),editor)
        self.window.centralWidget().setCurrentWidget(panel);self.window.run.state['id']='new-local-run-same-clock'
        panel.result_view.anchorClicked.emit(url)
        self.assertIs(self.window.centralWidget().currentWidget(),panel)
        self.assertIn('链接已过期',self.window.node_catalog.status.text())
