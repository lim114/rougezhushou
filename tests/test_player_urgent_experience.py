"""Actual user regressions: outside docking, stationary hits and open selectors."""
from types import SimpleNamespace
import unittest
from PySide6.QtCore import QRect,QPoint,QSize,Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication,QWidget,QComboBox
from PySide6.QtTest import QTest,QSignalSpy
from rouge.player_game_binding import outside_position
from rouge.player_compact import CompactAssistant
from rouge.branch_choice import BranchChoice
from rouge.current_enemy_spawns_view import CurrentEnemySpawnsPanel


class PlayerUrgentExperienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])

    def setUp(self):self.addCleanup(self.app.processEvents)

    def test_outside_dock_fits_realistic_screens_and_partial_offscreen_games(self):
        for area,client in ((QRect(0,0,1707,1040),QRect(69,103,1365,720)),
                            (QRect(0,0,1920,1040),QRect(0,0,1920,960)),
                            (QRect(-1920,0,1920,1040),QRect(-1900,50,1600,900)),
                            (QRect(0,0,1200,800),QRect(-800,30,600,700)),
                            (QRect(0,0,1200,800),QRect(20,-100,1000,600))):
            for preferred in(None,QPoint(400,400)):
                p=outside_position(client,area,QSize(278,36),preferred);self.assertIsNotNone(p)
                rect=QRect(p,QSize(278,36));self.assertTrue(area.contains(rect));self.assertFalse(client.intersects(rect))
        self.assertIsNone(outside_position(QRect(0,0,1920,1040),QRect(0,0,1920,1040),QSize(278,36)))

    def test_stationary_hover_and_click_keep_all_icon_centers_fixed(self):
        owner=QWidget();owner.run=SimpleNamespace(state={});owner.closing=True
        owner.open_scene_notes=lambda:None;owner.open_public_statistics=lambda:None;owner.node_statistics_source=lambda:None
        bar=CompactAssistant(owner);self.addCleanup(owner.deleteLater);self.addCleanup(bar.close)
        bar.show();self.app.processEvents();before=[b.mapToGlobal(b.rect().center())for b in bar.tool_buttons]
        button=bar.tool_buttons[-1];spy=QSignalSpy(button.clicked)
        QTest.mouseMove(button,button.rect().center());QTest.qWait(800)
        self.assertEqual(before,[b.mapToGlobal(b.rect().center())for b in bar.tool_buttons])
        QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=button.rect().center());self.app.processEvents()
        self.assertEqual(spy.count(),1);self.assertIs(bar.reference_window.pages.currentWidget(),bar.settings_popup)
        self.assertFalse(bar.tray.icon().isNull())

    def test_identical_category_refresh_keeps_popup_and_selection_without_model_reset(self):
        combo=QComboBox();groups=[('近卫',[('干员甲','a',QIcon()),('干员乙','b',QIcon())])]
        branches=BranchChoice(combo,groups,overview_label='总览');self.addCleanup(branches.close)
        branches.show();combo.show();branches.select_value('b');combo.showPopup();self.app.processEvents()
        resets=QSignalSpy(combo.model().modelReset);branch_resets=QSignalSpy(branches.branch.model().modelReset)
        for _ in range(10):branches.set_groups([('近卫',[('干员甲','a',QIcon()),('干员乙','b',QIcon())])],emit=False)
        self.assertEqual(combo.currentData(),'b');self.assertTrue(combo.view().isVisible())
        self.assertEqual(resets.count(),0);self.assertEqual(branch_resets.count(),0);combo.hidePopup()

    def test_unchanged_enemy_spawn_choices_do_not_reset_open_popup(self):
        combo=QComboBox();self.addCleanup(combo.close);rows=[{'label':'出怪条目甲','key':'a'}]
        CurrentEnemySpawnsPanel._fill(combo,rows,'a');combo.show();combo.showPopup();self.app.processEvents()
        resets=QSignalSpy(combo.model().modelReset)
        CurrentEnemySpawnsPanel._fill(combo,rows,'a')
        self.assertEqual(resets.count(),0);self.assertTrue(combo.view().isVisible());combo.hidePopup()

    def test_timestamp_refresh_preserves_enemy_forecast_and_open_selection(self):
        from copy import deepcopy
        from unittest.mock import patch
        from rouge.current_battle_view import CurrentBattlePanel
        from rouge.current_enemy_forecast import forecasts
        panel=CurrentBattlePanel('ro6_n_1_1');self.addCleanup(panel.close)
        config={'difficulty':{'value':15,'captured_at':1},'zone':{'id':'zone_1','captured_at':1}}
        panel.set_context(config);numbers=deepcopy(panel.enemy_forecasts)
        panel.show();panel.enemy_combo.showPopup();self.app.processEvents()
        resets=QSignalSpy(panel.enemy_combo.model().modelReset)
        with patch('rouge.current_enemy_forecast.forecasts',wraps=forecasts)as compute:
            for i in range(2,12):
                updated=deepcopy(config)
                for row in updated.values():row['captured_at']=i
                panel.set_context(updated)
            self.assertEqual(compute.call_count,0)
            self.assertEqual(panel.run_config['difficulty']['captured_at'],11)
            self.assertEqual(panel.enemy_forecasts,numbers)
            self.assertTrue(panel.enemy_combo.view().isVisible());self.assertEqual(resets.count(),0)
            updated['difficulty']['value']=14;panel.set_context(updated)
            self.assertEqual(compute.call_count,1);self.assertNotEqual(panel.enemy_forecasts,numbers)
        panel.enemy_combo.hidePopup()


if __name__=='__main__':unittest.main()
