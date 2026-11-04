"""Selection geometry and per-node memory used by the web entry points."""
import unittest

import cv2
import numpy as np

from rouge.node_events import annotate_map_content, mark_selected_node
from rouge.player_game_map import battle_targets


class SelectionGeometryTests(unittest.TestCase):
    def scene(self, selected=()):
        image = np.full((600, 1000, 3), 20, np.uint8)
        graph = {
            'status': 'matched',
            'current_node': None,
            'edges': [['0', '1'], ['1', '2']],
            'nodes': [
                {'id': str(i), 'center': [.25 + i * .25, .5], 'visible': True}
                for i in range(3)
            ],
        }
        for identity in selected:
            x = 250 + int(identity) * 250
            cv2.circle(image, (x + 7, 309), 40, (110, 110, 110), 2)
            cv2.ellipse(image, (x + 7, 309), (40, 40), 0, 0, 160, (255, 255, 255), 2)
        return image, graph

    def test_offset_dim_rim_binds_unique_node_and_content(self):
        image, graph = self.scene(['1'])
        mark_selected_node(image, graph)
        self.assertEqual(graph['selected_node'], '1')
        self.assertEqual(graph['selection_evidence'], 'same_frame_neutral_rim')
        annotate_map_content(graph, {'kind': 'battle', 'title': 'test'})
        self.assertEqual(graph['nodes'][1]['content']['source'], 'same_frame_selected_node')

    def test_two_visible_rims_remain_ambiguous(self):
        image, graph = self.scene(['0', '2'])
        mark_selected_node(image, graph)
        self.assertIsNone(graph['selected_node'])

    def test_route_and_panel_circle_do_not_select_a_map_node(self):
        image, graph = self.scene()
        cv2.line(image, (250, 300), (750, 300), (255, 255, 255), 3)
        cv2.circle(image, (900, 150), 40, (255, 255, 255), 3)
        mark_selected_node(image, graph)
        self.assertIsNone(graph['selected_node'])


class RememberedBattleLinkTests(unittest.TestCase):
    def test_confirmed_same_node_memory_supplies_both_links_after_map_return(self):
        content = {
            'kind': 'battle', 'title': '枝头陷阱',
            'variant_id': 'ro6_n_2_5', 'source': 'same_frame_selected_node',
        }
        links = battle_targets({'remembered_content': content})
        self.assertEqual(set(links), {'enemy', 'map'})
        self.assertEqual(links['enemy']['stage_id'], 'ro6_n_2_5')

    def test_unbound_or_mismatched_memory_cannot_supply_links(self):
        content = {
            'kind': 'battle', 'title': '枝头陷阱',
            'variant_id': 'ro6_n_2_5', 'source': 'visible_detail_panel',
        }
        self.assertEqual(battle_targets({'remembered_content': content}), {})
        content.update(source='same_frame_selected_node', title='another stage')
        self.assertEqual(battle_targets({'remembered_content': content}), {})

if __name__ == '__main__':
    unittest.main()
