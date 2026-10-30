from types import SimpleNamespace
import unittest
from PySide6.QtCore import Qt,QPoint
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtTest import QTest
from rouge.player_toolbar import DockButton,DIAMETER,LABEL_SPACE,ORDER
from rouge.player_compact import CompactAssistant

class ToolbarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
    def toolbar(self):
        owner=QWidget();owner.run=SimpleNamespace(state={});owner.closing=True
        owner.open_scene_notes=lambda:None;owner.open_public_statistics=lambda:None
        owner.node_statistics_source=lambda:None
        bar=CompactAssistant(owner);self.addCleanup(owner.deleteLater);self.addCleanup(bar.close);return bar
    def test_single_row_order_transparency_and_gap_input_region(self):
        bar=self.toolbar();self.assertEqual(tuple(b.accessibleName()for b in bar.tool_buttons),ORDER)
        self.assertTrue(bar.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground));self.assertLess(bar.height(),45)
        self.assertEqual(len({b.y()for b in bar.tool_buttons}),1);self.assertIsNone(bar.findChild(QWidget,'toolbarShell'))
        first,second=bar.tool_buttons[:2];gap=QPoint((first.geometry().right()+second.x())//2,first.geometry().center().y())
        self.assertFalse(bar.mask().contains(gap));self.assertTrue(bar.mask().contains(first.geometry().center()))
    def test_name_expands_inside_button_and_collapses_without_second_row(self):
        bar=self.toolbar();button=bar.tool_buttons[-1];height=bar.height();width=bar.width()
        button.set_expanded(True,animate=False);self.assertGreater(bar.width(),width);self.assertEqual(bar.height(),height)
        self.assertEqual(button.width(),DIAMETER+LABEL_SPACE);self.assertEqual(button.label,'设置')
        button.set_expanded(False,animate=False);self.assertEqual(bar.width(),width)
    def test_one_hover_target_and_smooth_geometry_changes(self):
        bar=self.toolbar();bar._hover_tool(bar.tool_buttons[1]);QTest.qWait(220)
        self.assertEqual(bar.tool_buttons[1].width(),DIAMETER+LABEL_SPACE)
        bar._hover_tool(bar.tool_buttons[-1]);QTest.qWait(220)
        self.assertEqual(sum(b._target for b in bar.tool_buttons),1);self.assertEqual(bar.tool_buttons[1].width(),DIAMETER)
    def test_transparent_corner_and_white_round_face_are_actual_painted_pixels(self):
        button=DockButton('设置','settings');self.addCleanup(button.deleteLater)
        image=button.grab().toImage();self.assertEqual(image.pixelColor(0,0).alpha(),0)
        self.assertGreater(image.pixelColor(DIAMETER//2,2).lightness(),230)
    def test_displayed_names_do_not_replace_accessible_actions(self):
        bar=self.toolbar();self.assertEqual(bar.buttons['地图与节点'].label,'地图')
        self.assertEqual(bar.buttons['场景笔记'].accessibleName(),'场景笔记')
        self.assertEqual(len(bar.tool_buttons),7);self.assertIsNotNone(bar.buttons['节点统计'])

if __name__=='__main__':unittest.main()
