"""Original-map marker clicks resolve exact existing observations only."""
from copy import deepcopy
from unittest.mock import patch
import unittest,json
from PySide6.QtCore import Qt,QPoint,QPointF
from PySide6.QtTest import QTest,QSignalSpy
from PySide6.QtWidgets import QApplication,QMenu
from rouge import current_map_position as model
from rouge.current_map_position_view import CurrentMapPositionPanel,CurrentOriginalCenters
from rouge.current_action_positions_view import CurrentActionPositionsPanel


class MapMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def panel(self):
        p=CurrentMapPositionPanel('ro6_n_2_3');p.resize(1000,700);p.show();self.qt.processEvents();self.addCleanup(p.close);return p

    def position(self,widget,point):
        rect=widget.image_rect()
        return QPointF(rect.left()+rect.width()*point['pixel'][0]/widget.pixmap.width(),rect.top()+rect.height()*point['pixel'][1]/widget.pixmap.height()).toPoint()

    def test_each_marker_comes_from_an_original_observation_and_matches_combo_number(self):
        p=self.panel();self.assertEqual(len(p.original.markers),len(p.result['points']))
        for i,(marker,point)in enumerate(zip(p.original.markers,p.result['points']),1):
            self.assertEqual(marker['point'],point);self.assertEqual(marker['number'],i);self.assertEqual(marker['key'],p.combo.itemData(i))
            self.assertTrue(p.combo.itemText(i).startswith(str(i)+' · '))
        self.assertIsNone(p.selected)

    def test_native_original_click_selects_exact_grid_and_combo_at_two_sizes(self):
        p=self.panel();point=p.result['points'][0]
        for width,height in((1000,700),(650,780)):
            p.resize(width,height);self.qt.processEvents();QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=self.position(p.original,point));self.qt.processEvents()
            self.assertEqual(p.selected,(point['row'],point['col']));self.assertEqual(p.grid.selected,p.selected);self.assertEqual(p.combo.currentIndex(),1)
        self.assertEqual(p.map_split.orientation(),Qt.Orientation.Vertical)

    def test_background_and_hidden_marker_clicks_do_not_change_selection(self):
        p=self.panel();p.combo.setCurrentIndex(2);before=p.selected;point=p.result['points'][0]
        QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=QPoint(1,1));self.assertEqual(p.selected,before)
        p.marker_toggle.setChecked(False);QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=self.position(p.original,point));self.assertEqual(p.selected,before)
        self.assertFalse(p.original.markers_visible);self.assertIsNotNone(p.original.point_center())

    def test_same_source_refresh_keeps_toggle_selection_and_reading(self):
        p=self.panel();p.combo.setCurrentIndex(1);p.marker_toggle.setChecked(False);p.tabs.setCurrentIndex(1);p.technical.verticalScrollBar().setValue(8)
        before=(p.selected,p.combo.currentData(),p.technical.verticalScrollBar().value(),p.tabs.currentIndex())
        self.assertTrue(p.refresh_reference());self.qt.processEvents()
        self.assertEqual(before,(p.selected,p.combo.currentData(),p.technical.verticalScrollBar().value(),p.tabs.currentIndex()));self.assertFalse(p.original.markers_visible)

    def test_source_loss_clears_old_markers_and_full_prose_remains_in_details(self):
        p=self.panel();p.combo.setCurrentIndex(1);full=model.cell_text(p.result,model.cell_reference(p.result,*p.selected))
        self.assertEqual(json.loads(p.technical.toPlainText())['完整说明'],full)
        with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
        self.assertEqual(p.original.markers,());self.assertTrue(p.original.pixmap.isNull());self.assertIsNone(p.selected)
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.selected)

    def test_action_marker_selects_its_exact_record_without_creating_extra_points(self):
        p=CurrentActionPositionsPanel('ro6_n_2_3','1');p.resize(1000,700);p.show();self.qt.processEvents();self.addCleanup(p.close)
        expected=[e for e in p.result['entries']if e['center']is not None];self.assertEqual(len(p.original.markers),len(expected));self.assertTrue(expected)
        e=expected[0];QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=self.position(p.original,e['center']));self.qt.processEvents()
        self.assertEqual(p.entry_key,e['key']);self.assertEqual(p.grid.selected,(e['cell']['row'],e['cell']['col']));self.assertEqual(p.original.point,e['center'])

    def test_overlapping_marker_choice_is_explicit_and_source_clear_closes_menu(self):
        p=self.panel();widget=p.original;first=deepcopy(widget.markers[0]);second=deepcopy(first);second.update(key='synthetic-other-record',number=99,label='99 · 测试记录')
        widget.set_image(p.image_raw,markers=[first,second]);spy=QSignalSpy(widget.markerSelected)
        QTest.mouseClick(widget,Qt.MouseButton.LeftButton,pos=self.position(widget,first['point']));self.qt.processEvents();menu=next(m for m in widget.findChildren(QMenu)if m.isVisible())
        self.assertEqual(spy.count(),0);self.assertEqual(len(menu.actions()),2)
        QTest.mouseClick(menu,Qt.MouseButton.LeftButton,pos=menu.actionGeometry(menu.actions()[1]).center());self.qt.processEvents();self.assertEqual(spy.at(0),['synthetic-other-record'])
        widget.set_image(p.image_raw,markers=[first,second]);QTest.mouseClick(widget,Qt.MouseButton.LeftButton,pos=self.position(widget,first['point']));self.qt.processEvents();widget.set_image(None);self.qt.processEvents();self.assertFalse(any(m.isVisible()for m in widget.findChildren(QMenu)))


if __name__=='__main__':unittest.main()
