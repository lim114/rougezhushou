from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget
from rouge import current_event_battles as model
from rouge.player_map_reader import make_reader
from rouge.player_reference_window import ReferenceWindow, ToolPage


class ReverseEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.reference_window = self.host = ReferenceWindow(self.owner)
        self.owner.present = self.host.present
        self.addCleanup(self.owner.close)
        self.addCleanup(self.host.close)

    def stage(self, sid='ro6_t_13'):
        page = make_reader('battle', {'id':sid,'title':'作战资料'}, self.owner, historical=True, page_owner=self.owner)
        page.prepare = page.panel.refresh_reference
        self.assertTrue(self.host.present(page))
        return page

    def choose(self, panel, cid):
        panel.choices.setCurrentRow(next(i for i in range(panel.choices.count()) if panel.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid))

    def origins(self, sid='ro6_t_13', cid='choice_ro6_normal2_2'):
        root = self.stage(sid)
        self.assertTrue(root.panel.open_event_origins())
        page = self.host.pages.currentWidget()
        self.choose(page.panel, cid)
        return root, page

    def test_exact_stage_filter_and_full_encounter_share_host(self):
        root, origins = self.origins()
        self.assertEqual(origins.panel.stage_id, root.panel.stage_id)
        self.assertEqual({r['id'] for r in model.stage_rows(origins.panel.result, origins.panel.choice_id)}, {'ro6_t_13'})
        self.assertIsNone(origins.panel.stages.currentData())
        self.assertIsNone(getattr(root.panel,'event_origins_dialog',None))
        self.assertTrue(origins.panel.open_full_flow())
        flow = self.host.pages.currentWidget()
        kind, target = origins.panel._flow_target(origins.panel.choice_id)
        self.assertEqual(kind, 'encounter')
        self.assertEqual((flow.panel.event_id, flow.panel.scene_id, flow.panel.choice_id), (target['event_id'],target['scene_id'],target['choice_id']))
        self.assertIs(flow.source_parent, origins)
        self.assertIs(flow.window(), root.window())
        self.assertIsNone(origins.panel.flow_dialog)

    def test_back_reopen_retains_reading_and_configuration_change_keeps_flow(self):
        root, origins = self.origins()
        self.assertTrue(origins.panel.open_full_flow())
        flow = self.host.pages.currentWidget()
        cursor = flow.panel.player.textCursor(); cursor.setPosition(2); cursor.setPosition(11,cursor.MoveMode.KeepAnchor); flow.panel.player.setTextCursor(cursor)
        flow.panel.tabs.setCurrentIndex(1)
        self.host.present(origins)
        origins.panel.stages.setCurrentIndex(origins.panel.stages.findData('ro6_t_13'))
        self.assertTrue(origins.panel.open_full_flow())
        self.assertIs(self.host.pages.currentWidget(), flow)
        self.assertEqual(flow.panel.player.textCursor().selectedText(),cursor.selectedText())
        self.assertEqual(flow.panel.tabs.currentIndex(),1)

    def test_lake_choices_open_their_exact_stage_and_selected_phase(self):
        for cid in ('choice_ro6_bat5_5','choice_ro6_bat5_9'):
            reference = model.reference('湖中仙女')
            sid = model.choice(reference,cid)['stage_ids'][0]
            root, origins = self.origins(sid,cid)
            self.assertTrue(origins.panel.open_full_flow())
            flow = self.host.pages.currentWidget()
            _, target = origins.panel._flow_target(cid)
            self.assertEqual((flow.panel.event_id,flow.panel.scene_id,flow.panel.choice_id), ('lake',target['scene_id'],cid))
            self.assertIs(flow.source_parent,origins)
            self.assertNotIn('【范围与未知】',flow.panel.player.toPlainText())
            self.assertIn('【范围与未知】',flow.panel.reference_notes.toPlainText())
            self.assertFalse(flow.panel.reference_scope.isExpanded())
            flow.panel.reference_scope.expand(animate=False)
            self.assertTrue(flow.panel.refresh_reference())
            self.assertTrue(flow.panel.reference_scope.isExpanded())
            self.host.present(root)
            self.assertTrue(root.panel.open_event_origins())
            self.assertIs(self.host.pages.currentWidget(),origins)

    def test_existing_stage_and_event_ancestors_are_reused_without_parent_cycle(self):
        root, origins = self.origins()
        origins.panel.stages.setCurrentIndex(origins.panel.stages.findData('ro6_t_13'))
        before = len(self.host.linked_pages)
        self.assertTrue(origins.panel.open_battle())
        self.assertIs(self.host.pages.currentWidget(),root)
        self.assertEqual(len(self.host.linked_pages),before)
        self.assertIsNone(root.source_parent)
        self.host.present(origins)
        self.assertTrue(origins.panel.open_full_flow())
        flow = self.host.pages.currentWidget()
        self.assertTrue(flow.panel.open_battle())
        configurations = self.host.pages.currentWidget()
        before = len(self.host.linked_pages)
        self.assertTrue(configurations.panel.open_full_flow())
        self.assertIs(self.host.pages.currentWidget(),flow)
        self.assertEqual(len(self.host.linked_pages),before)
        self.assertIs(flow.source_parent,origins)

    def test_ancestor_return_rechecks_dependent_source(self):
        root, origins = self.origins()
        origins.panel.stages.setCurrentIndex(origins.panel.stages.findData('ro6_t_13'))
        with patch.object(root,'prepare',return_value=False):
            self.assertFalse(origins.panel.open_battle())
        self.assertIs(self.host.pages.currentWidget(),origins)

    def test_changed_choice_and_missing_flow_source_remove_only_dependents(self):
        root, origins = self.origins()
        origins.panel.open_full_flow(); flow = self.host.pages.currentWidget()
        with patch('rouge.current_encounters.reference',return_value=None):
            self.assertFalse(self.host.present(flow))
        self.assertIs(self.host.pages.currentWidget(),origins)
        self.assertNotIn(flow,self.host.history)
        self.assertTrue(origins.panel.open_full_flow()); flow = self.host.pages.currentWidget()
        self.host.present(origins); origins.panel.choices.setCurrentRow(-1)
        self.assertFalse(self.host.present(flow))
        self.assertNotIn(flow,self.host.history)
        self.assertIn(root,self.host.history)

    def test_short_summary_full_notes_and_refresh_state(self):
        root, page = self.origins()
        panel = page.panel
        self.assertNotIn('不是本局实际入口',panel.player.toPlainText())
        self.assertIn('不是本局实际入口',panel.reference_notes.toPlainText())
        self.assertFalse(panel.scope.isExpanded())
        panel.scope.expand(animate=False)
        before = (panel.player.toPlainText(),panel.reference_notes.toPlainText())
        self.assertTrue(panel.refresh_reference())
        self.assertTrue(panel.scope.isExpanded())
        self.assertEqual(before,(panel.player.toPlainText(),panel.reference_notes.toPlainText()))
        panel.clear_reference()
        self.assertEqual(panel.reference_notes.toPlainText(),'')
        self.assertFalse(panel.scope.isExpanded())


if __name__ == '__main__':
    unittest.main()
