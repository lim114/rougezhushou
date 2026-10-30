"""Visible thumbnail input, missing art, and retained explanations, without game I/O."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QIcon,QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.player_map_hover import NodeHoverCard,NodeEntryButton
from rouge.player_map import PreviewMapView
from rouge.player_map_acceptance import fixtures

class NodeVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_overlay_button_keeps_native_mouse_keyboard_and_disabled_behavior(self):
        with TemporaryDirectory()as folder:
            path=Path(folder)/'art.png';image=QPixmap(320,180);image.fill(QColor('#649b81'));image.save(str(path))
            title='较长的事件标题也保留完整名称供查看';button=NodeEntryButton(title,path,QIcon(str(path)));self.addCleanup(button.close)
            clicks=[];button.clicked.connect(lambda:clicks.append(True));original=button.artwork.toImage()
            for width in(130,166,240):
                button.resize(width,96);button.show();self.qt.processEvents();self.assertFalse(button.grab().isNull())
                self.assertTrue(button.rect().contains(button.caption_rect()));self.assertGreaterEqual(button.caption_rect().height(),button.fontMetrics().height())
                self.assertEqual(button.artwork.toImage(),original);self.assertEqual(button.accessibleName(),title)
            QTest.mouseClick(button,Qt.MouseButton.LeftButton);button.setFocus();QTest.keyClick(button,Qt.Key.Key_Space)
            self.assertEqual(len(clicks),2)
            button.setEnabled(False);QTest.mouseClick(button,Qt.MouseButton.LeftButton);self.assertEqual(len(clicks),2)
    def test_missing_art_uses_node_icon_without_borrowing_another_picture(self):
        pix=QPixmap(40,40);pix.fill(QColor('#23b6b0'));button=NodeEntryButton('没有已证图片',None,QIcon(pix));self.addCleanup(button.close)
        button.show();self.qt.processEvents();self.assertTrue(button.artwork.isNull());self.assertFalse(button.icon().isNull())
        self.assertEqual(button.text(),button.accessibleName());self.assertFalse(button.grab().isNull())
    def test_source_details_toggle_and_reading_survive_same_node_update(self):
        graphs,identity,*_=fixtures();graph=graphs[0];before=deepcopy(graph);view=PreviewMapView();self.addCleanup(view.close)
        view.historical=False;card=NodeHoverCard(view);self.addCleanup(card.close);binding=('isolated','zone_1',graph['template_id'],identity)
        card.install(binding,graph,identity,{},view);card.show();self.qt.processEvents()
        self.assertTrue(card.summary.isVisible());self.assertIn('不是本局概率',card.summary.text());self.assertFalse(card.notice.isVisible())
        choices=[(k,i,b.text())for k,i,b in card.entry_buttons]
        QTest.mouseClick(card.source_toggle,Qt.MouseButton.LeftButton);self.assertTrue(card.notice.isVisible());self.assertIn('路标统计更新',card.notice.text())
        card.scroll.verticalScrollBar().setValue(15);card.install(binding,graph,identity,{},view,force=True);self.qt.processEvents()
        self.assertTrue(card.source_toggle.isChecked());self.assertTrue(card.notice.isVisible());self.assertEqual(choices,[(k,i,b.text())for k,i,b in card.entry_buttons])
        self.assertEqual(card.scroll.horizontalScrollBarPolicy(),Qt.ScrollBarPolicy.ScrollBarAlwaysOff);self.assertEqual(graph,before)
    def test_histories_stay_separate_when_shown_as_image_tiles(self):
        graph={'zone_id':'zone_1','template_id':'isolated','grid':{'rows':3},'nodes':[{'id':'old','row':1,'col':1,'observed_type':'林间空地','remembered_type':'不期而遇','remembered_content':{'kind':'event','title':'桑尼的邀请'}}]}
        before=deepcopy(graph);view=PreviewMapView();view.historical=True;self.addCleanup(view.close);card=NodeHoverCard(view);self.addCleanup(card.close)
        card.install(('run','zone_1','isolated','old'),graph,'old',{},view);card.show();self.qt.processEvents()
        self.assertIn('历史地图',card.summary.text());self.assertTrue(card.entry_buttons)
        self.assertTrue(all(b.property('referenceScope')=='history'and isinstance(b,NodeEntryButton)for _,_,b in card.entry_buttons));self.assertEqual(graph,before)

if __name__=='__main__':unittest.main()
