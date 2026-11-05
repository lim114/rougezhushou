import unittest
from types import SimpleNamespace
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget
from rouge.player_reference_window import ReferenceWindow, ToolPage
from rouge.current_encounters_view import CurrentEncountersPanel
from rouge.documented_event_flow_view import DocumentedEventFlowPanel
from rouge.current_ritual_view import CurrentRitualPanel


class LinkedBattleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.owner = QWidget()
        self.owner.reference_window = self.host = ReferenceWindow(self.owner)
        def present(page):
            shown = self.host.present(page)
            if shown:
                self.owner.active_popup = page
            return shown
        self.owner.present = present
        self.addCleanup(self.owner.close)
        self.addCleanup(self.host.close)

    def wrap(self, panel):
        page = ToolPage('公开事件测试', panel, self.owner)
        page.panel = panel
        page.prepare = panel.refresh_reference
        page.finished.connect(panel._close_battle)
        self.assertTrue(self.owner.present(page))
        self.qt.processEvents()
        return page

    def encounter(self):
        panel = CurrentEncountersPanel('黑诞')
        page = self.wrap(panel)
        panel.controller.setCurrentIndex(panel.controller.findData(True))
        key = next(c['id'] for c in panel.result['choices'].values() if 'choice_ro6_normal2_2' in c['variant_ids'])
        self.select(panel, key)
        return page, panel

    def select(self, panel, key):
        index = next(i for i in range(panel.choices.count()) if panel.choices.item(i).data(Qt.ItemDataRole.UserRole) == key)
        panel.choices.setCurrentRow(index)

    def test_variants_require_selection_and_nested_stage_uses_same_window(self):
        source, panel = self.encounter()
        handle = int(self.host.winId())
        self.assertTrue(panel.open_battle())
        configurations = self.host.pages.currentWidget()
        self.assertIs(configurations.source_parent, source)
        self.assertIsNone(configurations.panel.stages.currentData())
        self.assertFalse(configurations.panel.open_battle())
        configurations.panel.stages.setCurrentIndex(configurations.panel.stages.findData('ro6_t_13'))
        self.assertTrue(configurations.panel.open_battle())
        stage = self.host.pages.currentWidget()
        self.assertEqual(stage.panel.stage_id, 'ro6_t_13')
        self.assertIs(stage.source_parent, configurations)
        self.assertEqual(int(self.host.winId()), handle)
        self.assertIsNone(panel.battle_dialog)
        self.assertIsNone(configurations.panel.battle_dialog)

    def test_back_and_repeat_open_keep_same_configuration_page_and_choice(self):
        source, panel = self.encounter()
        panel.open_battle()
        configurations = self.host.pages.currentWidget()
        configurations.panel.stages.setCurrentIndex(configurations.panel.stages.findData('ro6_t_13'))
        self.host.navigate(0)
        self.assertIs(self.host.pages.currentWidget(), source)
        self.assertTrue(panel.open_battle())
        self.assertIs(self.host.pages.currentWidget(), configurations)
        self.assertEqual(configurations.panel.stages.currentData(), 'ro6_t_13')

    def test_parent_choice_change_rejects_old_configuration_on_forward(self):
        source, panel = self.encounter()
        panel.open_battle()
        configurations = self.host.pages.currentWidget()
        self.host.navigate(0)
        other=next(panel.choices.item(i).data(Qt.ItemDataRole.UserRole) for i in range(panel.choices.count()) if panel.choices.item(i).data(Qt.ItemDataRole.UserRole)!=panel.choice_id)
        self.select(panel, other)
        self.host.navigate(1)
        self.assertIs(self.host.pages.currentWidget(), source)
        self.assertNotIn(configurations, self.host.history)
        self.assertFalse(self.host.forward.isEnabled())

    def test_unrelated_controller_change_does_not_invalidate_battle_branch(self):
        source, panel = self.encounter()
        panel.open_battle()
        configurations = self.host.pages.currentWidget()
        self.host.navigate(0)
        panel.controller.setCurrentIndex(panel.controller.findData(False))
        self.host.navigate(1)
        self.assertIs(self.host.pages.currentWidget(), configurations)
        self.assertTrue(configurations.isVisible())

    def test_discard_parent_removes_all_dependent_levels_not_unrelated_page(self):
        source, panel = self.encounter()
        panel.open_battle()
        configurations = self.host.pages.currentWidget()
        configurations.panel.stages.setCurrentIndex(configurations.panel.stages.findData('ro6_t_13'))
        configurations.panel.open_battle()
        stage = self.host.pages.currentWidget()
        fallback = ToolPage('地图', QWidget(), self.owner)
        self.host.discard(source, fallback=fallback)
        self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(), fallback)
        for page in (source, configurations, stage):
            self.assertNotIn(page, self.host.history)
            self.assertEqual(self.host.pages.indexOf(page), -1)
        self.assertFalse(self.host.linked_pages)

    def test_direct_documented_stage_and_ritual_related_stage_use_host(self):
        panel = DocumentedEventFlowPanel('button', 'scene_ro6_end4_1')
        self.wrap(panel)
        self.select(panel, 'choice_ro6_end4_3')
        self.assertTrue(panel.open_battle())
        self.assertEqual(self.host.pages.currentWidget().panel.stage_id, 'ro6_s_1')
        ritual = CurrentRitualPanel()
        self.wrap(ritual)
        self.assertTrue(ritual.open_related())
        self.assertEqual(self.host.pages.currentWidget().panel.stage_id, ritual.result['data']['related_boss_stage_id'])

    def test_opening_new_main_page_refreshes_once_and_reopening_still_refreshes(self):
        from rouge.player_compact import CompactAssistant
        calls = []
        self.owner.pin = SimpleNamespace(isChecked=lambda: True)
        self.owner.game_binding = SimpleNamespace(enabled=False)
        self.owner.active_popup = None
        self.owner.refresh = lambda: calls.append(True)
        a = ToolPage('地图', QWidget(), self.owner, on_show=self.owner.refresh)
        b = ToolPage('藏品', QWidget(), self.owner, on_show=self.owner.refresh)
        self.assertTrue(CompactAssistant.present(self.owner, a))
        self.assertEqual(len(calls), 1)
        self.assertTrue(CompactAssistant.present(self.owner, b))
        self.assertEqual(len(calls), 2)
        self.assertTrue(CompactAssistant.present(self.owner, b))
        self.assertEqual(len(calls), 3)


if __name__ == '__main__':
    unittest.main()
