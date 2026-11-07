from unittest.mock import patch
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from rouge import player_map
from rouge.player_map_acceptance import fixtures


class MapGeometryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def setUp(self):
        graphs,*_=fixtures();self.view=player_map.PreviewMapView();self.addCleanup(self.view.close)
        self.view.resize(900,600);self.view.set_map(graphs[0])

    def test_hit_reuses_current_positions(self):
        _,points=self.view._positions();identity=next(iter(points))
        with patch.object(self.view,'_positions',wraps=self.view._positions)as positions:
            self.assertEqual(self.view._hit(points[identity]),identity)
            self.assertEqual(positions.call_count,1)

    def test_paint_computes_geometry_once_for_all_nodes(self):
        with patch.object(self.view,'_positions',wraps=self.view._positions)as positions,patch.object(self.view,'_badge_width',wraps=self.view._badge_width)as badges:
            image=self.view.grab().toImage()
            self.assertFalse(image.isNull());self.assertEqual(positions.call_count,1);self.assertEqual(badges.call_count,1)

    def test_hover_and_paint_share_layout_until_map_or_drawing_area_changes(self):
        view=self.view
        def hit_first():
            _, points=player_map.PreviewMapView._positions(view)
            identity=next(iter(points))
            self.assertEqual(view._hit(points[identity]),identity)

        with patch.object(view,'_positions',wraps=view._positions) as positions:
            hit_first();view.grab();hit_first()
            self.assertEqual(positions.call_count,1)
            view.resize(1024,720);hit_first();view.grab()
            self.assertEqual(positions.call_count,2)
            view.setContentsMargins(25,10,5,5);hit_first()
            self.assertEqual(positions.call_count,3)
            changed=deepcopy(view.graph)
            changed['nodes'][0]['id']='replacement'
            view.set_map(changed);hit_first()
            self.assertEqual(positions.call_count,4)
            view.set_map(None)
            self.assertIsNone(view._hit(view.rect().center()))


class MapRefreshReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_floor_labels_share_finder_and_location_uses_one_selection_callback(self):
        from tests.test_batch185_mainwindow import Batch185WindowTests
        Batch185WindowTests.setUp(self)
        graphs,*_=fixtures();self.window.run.state['maps']={g['zone_id']:g for g in graphs}
        self.window.show_compact();self.window.compact_window.open_map();page=self.window.compact_window.map_popup.panel
        with patch('rouge.player_map_find.NodeFinder') as rebuild:
            page.node_query.setText('不存在的记录')
            self.assertEqual(page.node_results.count(),0)
            page.node_query.clear()
            page.read_scope.setCurrentIndex(1)
            page.read_scope.setCurrentIndex(0)
            self.assertGreater(page.node_results.count(),0)
            rebuild.assert_not_called()
        with patch.object(player_map,'zone_info',wraps=player_map.zone_info)as zone:
            page.refresh()
            # One per saved zone, plus current artwork and current status label.
            self.assertEqual(zone.call_count,len(graphs)+2)
        index=next(i for i in range(page.node_results.count())if page.node_results.itemData(i)[0]==page.selected_zone)
        page.node_results.setCurrentIndex(index);key=page.node_results.currentData()
        with patch.object(page,'selected',wraps=page.selected)as selected:
            self.assertTrue(page.locate_found_node());self.assertEqual(selected.call_count,1)
        self.assertEqual(page.view.selected,key[2]);self.assertTrue(page.details_toggle.isChecked())


if __name__=='__main__':unittest.main()
