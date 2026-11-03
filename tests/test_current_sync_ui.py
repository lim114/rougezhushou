"""Current-first UI and bounded readers in fully isolated application state."""
import time,unittest
from copy import deepcopy
from types import SimpleNamespace
from PySide6.QtCore import QRect,QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QSignalSpy
from tests import test_sampling_flow as fixtures
from rouge.player_reference_window import ToolPage


class CurrentSyncUiTests(unittest.TestCase):
    setUpClass=classmethod(fixtures.SamplingFlowTests.setUpClass.__func__)
    setUp=fixtures.SamplingFlowTests.setUp
    offer=fixtures.SamplingFlowTests.offer
    wait_for=fixtures.SamplingFlowTests.wait_for

    def test_current_arrives_before_backlog_and_all_short_pages_are_retained(self):
        at=time.time()
        self.offer(20,at);self.window.auto.setChecked(True);self.wait_for(self.entered.is_set)
        self.offer(30,at);self.offer(40,at);self.offer(50,at);self.offer(80,at);self.release.set()
        self.wait_for(lambda:len(self.seen)==5 and not self.window.busy)
        self.assertEqual(self.seen[:2],[20,80]);self.assertEqual(set(self.seen),{20,30,40,50,80})
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)
        self.assertEqual(self.window.observation['operator']['fields']['level'],80)
        self.assertEqual(self.window.capture.stats()['pending'],0)
        self.assertFalse(self.window.observation_timeline.pending)

    def test_same_training_refresh_preserves_open_skill_menu(self):
        w=self.window;w.operator_choices.select_value('kaltsit');w.update_operator()
        w.show();w.skill.showPopup();self.qt.processEvents();spy=QSignalSpy(w.skill.model().modelReset)
        before=w.skill.currentData();w.update_operator(preserve_level=True)
        self.assertEqual(spy.count(),0);self.assertEqual(w.skill.currentData(),before);self.assertTrue(w.skill.view().isVisible());w.skill.hidePopup()

    def show_bar(self):
        self.window.show_compact();c=self.window.compact_window
        for timer in c.findChildren(QTimer):timer.stop()
        c.game_binding.snapshot={'active':True,'logical_client':QRect(60,70,1200,700),'key':(1,2),'screen':self.qt.primaryScreen()}
        return c

    def test_first_reader_is_compact_and_user_resize_survives_refresh(self):
        c=self.show_bar();c.open_map();self.qt.processEvents();host=c.reference_window
        self.assertLessEqual(host.width(),max(360,round(host.screen().availableGeometry().width()*.28))+24)
        host.resize(650,450);self.qt.processEvents();size=host.size();pos=host.pos()
        c.refresh();self.qt.processEvents();self.assertEqual(host.size(),size);self.assertEqual(host.pos(),pos)

    def test_recent_stage_and_spawn_details_use_shared_host_and_back_keeps_selection(self):
        c=self.show_bar();self.window.run.state['last_node_content']={'kind':'battle','stage_id':'ro6_n_1_1','title':'遗忘时间'}
        c.open_scene_battle();source=c.scene_popup;panel=source.panel;panel.stages.setCurrentIndex(1)
        selected=panel.stages.currentData();self.assertTrue(panel.open_stage());self.qt.processEvents()
        child=c.reference_window.pages.currentWidget();self.assertIsInstance(child,ToolPage);self.assertIs(child.source_parent,source);self.assertIsNone(panel.dialog)
        self.assertEqual(child.panel.stage_id,selected)
        c.reference_window.navigate(c.reference_window.cursor-1);self.assertEqual(panel.stages.currentData(),selected)
        self.assertIs(c.reference_window.pages.currentWidget(),source)

    def test_recent_event_uses_shared_host_without_clearing_reader_on_back(self):
        c=self.show_bar();self.window.run.state['last_node_content']={'kind':'event','title':'呼吸的红苔'}
        c.open_scene_battle();source=c.scene_popup;panel=source.panel;panel.event_choices.setCurrentIndex(1)
        self.assertTrue(panel.open_event());self.qt.processEvents();child=c.reference_window.pages.currentWidget()
        self.assertIsInstance(child,ToolPage);self.assertIsNone(panel.event_dialog);self.assertIsNotNone(child.panel.result)
        c.reference_window.navigate(c.reference_window.cursor-1);self.assertIs(c.reference_window.pages.currentWidget(),source)
        self.assertTrue(panel.open_event());self.assertIs(c.reference_window.pages.currentWidget(),child);self.assertIsNotNone(child.panel.result)

    def test_all_event_reader_types_keep_exact_target_in_shared_pages(self):
        from rouge import current_event_directory as model
        from rouge.current_event_directory_view import make_event_dialog
        c=self.show_bar();seen=set()
        for row in model.reference()['rows']:
            if row['reader']in seen:continue
            seen.add(row['reader']);entry=row['entries'][-1]
            with self.subTest(reader=row['reader']):
                target=model.resolve(model.reference(row['id']),entry['key']);page=make_event_dialog(target,page_owner=c)
                self.assertIsInstance(page,ToolPage);self.assertEqual((page.panel.scene_id,page.panel.choice_id),(entry['scene_id'],entry['choice_id']))
                page.close();page.deleteLater();self.qt.processEvents()
        self.assertEqual(len(seen),21)

    def test_first_static_map_is_current_without_waiting_for_a_second_sample(self):
        from rouge.player_map_acceptance import fixtures as maps
        c=self.show_bar();c.open_map();graph=deepcopy(maps()[0][0]);graph['status']='matched'
        at=max(time.time(),self.window.run.state['started_at']+1)
        packet={'page':'exploration','nodes':[],'captured_at':at,'map':graph,'run':{'map':graph,'config':{'zone':{'id':'zone_1','name':'玻利瓦尔肤层'}}}}
        import numpy as np
        self.window.sample_received((np.full((24,36,3),65,np.uint8),packet));self.qt.processEvents()
        self.assertFalse(self.window.map_view.historical)
        self.assertFalse(c.map_popup.panel.view.historical)
        self.assertEqual(c.map_popup.panel.view.graph['captured_at'],at)

    def test_unbound_startup_reader_also_defaults_to_compact_size(self):
        self.window.show_compact();c=self.window.compact_window
        for timer in c.findChildren(QTimer):timer.stop()
        c.game_binding.snapshot=None;c.open_map();self.qt.processEvents()
        host=c.reference_window
        self.assertLessEqual(host.width(),max(360,round(host.screen().availableGeometry().width()*.28))+24)

    def test_fit_map_shows_all_node_centers_without_forcing_scroll_in_compact_reader(self):
        from rouge.player_map_acceptance import fixtures as maps
        c=self.show_bar();c.open_map();self.window.run.state['maps']={'zone_1':deepcopy(maps()[0][0])}
        self.window.run.state['config']['zone']={'id':'zone_1','name':'玻利瓦尔肤层'}
        self.window.render_map();self.qt.processEvents();panel=c.map_popup.panel
        self.assertEqual(panel.scroll.horizontalScrollBar().maximum(),0)
        self.assertEqual(panel.scroll.verticalScrollBar().maximum(),0)
        _,points=panel.view._positions()
        self.assertTrue(points)
        for point in points.values():self.assertTrue(panel.view.rect().contains(point.toPoint()))
        panel.zoom.setCurrentIndex(2);self.qt.processEvents();self.assertGreater(panel.scroll.horizontalScrollBar().maximum(),0)
        panel.zoom.setCurrentIndex(0);self.qt.processEvents();self.assertEqual(panel.scroll.horizontalScrollBar().maximum(),0)

if __name__=='__main__':unittest.main()
