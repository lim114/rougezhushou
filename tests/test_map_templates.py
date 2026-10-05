"""Map behavior through the existing ScreenReader and RunState public seams."""
import unittest
from functools import lru_cache
from pathlib import Path
import tempfile
import copy
import cv2
import numpy as np
from rouge.recognition import ScreenReader
from rouge.run_state import RunState

ROOT = Path(__file__).resolve().parents[1]

@lru_cache(maxsize=1)
def first_map():
    image = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png', dtype=np.uint8), 1)
    return ScreenReader().read(image)


class MapTemplateTests(unittest.TestCase):
    def test_real_first_floor_map_recovers_graph_and_current_node_without_manual_floor(self):
        observed = first_map()
        graph = observed['map']
        self.assertEqual(graph['status'], 'matched')
        self.assertEqual(graph['template_id'], '1b')
        self.assertEqual((graph['zone_id'], len(graph['nodes']), len(graph['edges'])), ('zone_1', 12, 13))
        self.assertEqual(graph['current_node'], '1,0')
        self.assertEqual({n['id']: n['distance'] for n in graph['nodes']}['0,1'], 4)
        self.assertEqual({n['id'] for n in graph['nodes'] if n['template_type']=='险路尽头'}, {'0,4','2,4'})

    def test_hidden_nodes_use_fixed_layout_and_graph_distance_without_inventing_probability(self):
        graph = first_map()['map']
        nodes = {n['id']: n for n in graph['nodes']}
        self.assertEqual(nodes['1,3']['observed_type'], '未知的诡秘')
        self.assertEqual(nodes['1,3']['prediction']['candidates'], ['诡意行商'])
        self.assertEqual(nodes['0,1']['prediction']['candidates'], ['作战','紧急作战'])
        self.assertEqual(nodes['2,4']['prediction']['candidates'], ['险路尽头'])
        self.assertIsNone(nodes['0,1']['prediction']['probability'])
        self.assertEqual(nodes['0,1']['prediction']['evidence'], 'community_constraints')

    def test_same_run_map_survives_partial_frame_restart_and_only_manual_reset_clears_it(self):
        observed = copy.deepcopy(first_map())
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory)/'run.json'; run = RunState(file); at = run.state['started_at']+1
            self.assertTrue(run.apply(observed['run'], at))
            self.assertEqual(run.state['maps']['zone_1']['template_id'], '1b')
            # A revealed name belongs to the captured grid, not another node
            # with the same artwork. Replaying later fog must retain the name.
            revealed = copy.deepcopy(observed['run'])
            next(n for n in revealed['map']['nodes'] if n['id']=='0,1')['observed_type']='紧急作战'
            run.apply(revealed, at+1)
            run.apply(observed['run'], at+2)
            saved = RunState(file)
            nodes = {n['id']:n for n in saved.state['maps']['zone_1']['nodes']}
            self.assertEqual(nodes['0,1']['remembered_type'], '紧急作战')
            self.assertEqual(nodes['0,3']['prediction']['candidates'], ['作战'])
            partial = copy.deepcopy(observed['run']); partial['map']={'status':'insufficient','zone_id':'zone_1'}
            saved.apply(partial, at+3)
            self.assertEqual(saved.state['maps']['zone_1']['template_id'],'1b')
            saved.reset()
            self.assertEqual(saved.state['maps'],{})
            self.assertFalse(saved.apply(observed['run'],saved.state['started_at']-1))

    def test_scaled_letterboxed_map_preserves_graph_and_original_capture_coordinates(self):
        original = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png', dtype=np.uint8),1)
        scaled = cv2.resize(original,(960,720),interpolation=cv2.INTER_AREA)
        image = np.zeros((720,1280,3),np.uint8); image[:,160:1120]=scaled
        graph = ScreenReader().read(image)['map']
        self.assertEqual((graph['status'],graph['template_id']),('matched','1b'))
        self.assertEqual(graph['current_node'],'1,0')
        center = next(n['center'] for n in graph['nodes'] if n['id']=='1,0')
        self.assertAlmostEqual(center[0],.230,delta=.012)
        self.assertAlmostEqual(center[1],.463,delta=.012)

    def test_partial_map_never_fabricates_full_layout(self):
        image = cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png', dtype=np.uint8),1)
        image[:,650:]=15  # Incomplete map view, not a new map or empty inventory.
        graph = ScreenReader().read(image)['map']
        self.assertNotEqual(graph['status'],'matched')
        self.assertIsNone(graph['template_id'])
        self.assertEqual(graph['edges'],[])

    def test_native_wide_map_with_detail_panel_and_split_current_marker_is_recognized(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/map-template-node-detail.png',dtype=np.uint8),1)
        graph=ScreenReader().read(image,client_rect=[2,45,2050,1125])['map']
        self.assertEqual((graph['status'],graph['template_id']),('matched','1c'))
        self.assertEqual((len(graph['nodes']),len(graph['edges'])),(13,12))
        self.assertEqual(graph['current_node'],'1,2')
        self.assertEqual(next(n for n in graph['nodes'] if n['id']=='1,4')['observed_type'],'未知的诡秘')

    def test_temporarily_unreadable_current_marker_retains_last_confirmed_position_as_history(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            observed=copy.deepcopy(first_map()['run']);run.apply(observed,at)
            observed['map']['current_node']=None;run.apply(observed,at+1)
            saved=run.state['maps']['zone_1']
            self.assertIsNone(saved['current_node'])
            self.assertEqual(saved['last_confirmed_current_node'],'1,0')
            self.assertEqual(saved['current_node_confirmed_at'],at)
            observed['map']['current_node']='1,1';run.apply(observed,at+2)
            self.assertEqual(run.state['maps']['zone_1']['last_confirmed_current_node'],'1,1')
            positions=[r['current'] for r in run.state['history'] if r['kind']=='map_position_updated']
            self.assertEqual(positions,['1,0','1,1'])


if __name__ == '__main__': unittest.main()
