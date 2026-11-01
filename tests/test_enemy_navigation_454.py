from copy import deepcopy
from importlib import import_module
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget
from rouge import battle_enemy_readers as readers
from rouge.current_battle_view import CurrentBattlePanel
from rouge.player_reference_window import ReferenceWindow, ToolPage


class EnemyNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.fixtures = []
        for name, spec in readers._READERS.items():
            provider = import_module('rouge.'+spec.provider)
            stage = provider.STAGES[0]
            result = provider.reference(stage)
            row = (result.get('rows') or result.get('entities'))[0]
            key = row['enemy_key'] if name == 'boss_documents' else row['key']
            cls.fixtures.append((name, spec, stage, key))

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

    def battle(self, fixture):
        _, _, stage, key = fixture
        panel = CurrentBattlePanel(stage)
        page = ToolPage('固定作战', panel, self.owner)
        page.panel = panel
        page.prepare = panel.refresh_reference
        page.finished.connect(panel._close_readers)
        self.assertTrue(self.owner.present(page))
        self.assertTrue(panel.enemy_choices.select_value(key))
        self.qt.processEvents()
        return page, panel

    def test_seven_exact_mechanism_panels_use_one_host_and_keep_reading_on_back(self):
        for fixture in self.fixtures:
            name, spec, _, _ = fixture
            root, parent = self.battle(fixture)
            handle = int(self.host.winId())
            self.assertTrue(getattr(parent, 'open_'+name)())
            page = self.host.pages.currentWidget()
            self.assertIs(page.source_parent, root)
            self.assertIs(page.window(), self.host)
            self.assertEqual(int(self.host.winId()), handle)
            self.assertIsNone(getattr(parent, name+'_dialog', None))
            page.panel.tabs.setCurrentWidget(page.panel.technical)
            cursor = page.panel.technical.textCursor()
            cursor.setPosition(3)
            cursor.setPosition(14, cursor.MoveMode.KeepAnchor)
            page.panel.technical.setTextCursor(cursor)
            text = page.panel.player.toPlainText()
            self.owner.present(root)
            self.assertTrue(getattr(parent, 'open_'+name)())
            self.assertIs(self.host.pages.currentWidget(), page)
            self.assertEqual(page.panel.player.toPlainText(), text)
            self.assertEqual(page.panel.technical.textCursor().selectedText(), cursor.selectedText())
            self.assertIs(page.panel.tabs.currentWidget(), page.panel.technical)

    def test_five_fixed_maps_share_host_and_keep_selected_tile(self):
        count = 0
        for fixture in self.fixtures:
            name, spec, _, _ = fixture
            if spec.map_cleanup is None:
                continue
            root, parent = self.battle(fixture)
            self.assertTrue(getattr(parent, 'open_'+name)())
            mechanism = self.host.pages.currentWidget()
            self.assertTrue(mechanism.panel.open_map())
            mapped = self.host.pages.currentWidget()
            self.assertIs(mapped.source_parent, mechanism)
            self.assertEqual(mapped.panel.result['current_level_key'], mechanism.panel.result['level_key'])
            mapped.panel.combo.setCurrentIndex(1)
            selected = mapped.panel.selected
            self.owner.present(mechanism)
            self.assertTrue(mechanism.panel.open_map())
            self.assertIs(self.host.pages.currentWidget(), mapped)
            self.assertEqual(mapped.panel.selected, selected)
            count += 1
        self.assertEqual(count, 5)

    def test_six_original_battle_source_checks_including_elbert_base_are_retained(self):
        for fixture in self.fixtures:
            name, spec, _, _ = fixture
            if not spec.check_battle_source:
                continue
            root, parent = self.battle(fixture)
            getattr(parent, 'open_'+name)()
            page = self.host.pages.currentWidget()
            wrong = deepcopy(getattr(page.panel, spec.sync_result))
            wrong['battle_source_identity'] = ('different-fixed-source',)
            setattr(page.panel, spec.sync_result, wrong)
            with patch.object(page.panel, 'refresh_reference', return_value=True):
                self.assertFalse(self.owner.present(page))
            self.assertNotIn(page, self.host.history)
            self.assertIs(self.host.pages.currentWidget(), root)

    def test_changed_enemy_cannot_forward_to_previous_exact_mechanism(self):
        for fixture in self.fixtures:
            name, _, _, key = fixture
            root, parent = self.battle(fixture)
            getattr(parent, 'open_'+name)()
            page = self.host.pages.currentWidget()
            self.host.navigate(self.host.cursor-1)
            other = next(r['key'] for r in parent.result['enemies'] if r['key'] != key)
            self.assertTrue(parent.enemy_choices.select_value(other))
            self.host.navigate(self.host.cursor+1)
            self.assertIs(self.host.pages.currentWidget(), root)
            self.assertNotIn(page, self.host.history)

    def test_optional_fixed_map_loss_keeps_valid_mechanism_reader(self):
        fixture = next(f for f in self.fixtures if f[0] == 'guest_material')
        root, parent = self.battle(fixture)
        parent.open_guest_material()
        mechanism = self.host.pages.currentWidget()
        mechanism.panel.open_map()
        mapped = self.host.pages.currentWidget()
        with patch('rouge.current_map_position.stage_reference', return_value=None):
            self.assertFalse(self.owner.present(mapped))
        self.assertIs(self.host.pages.currentWidget(), mechanism)
        self.assertIsNotNone(mechanism.panel.result)
        self.assertNotIn(mapped, self.host.history)

    def test_boss_related_enemy_returns_to_exact_battle_selection(self):
        from rouge import current_boss_documents as model
        spec = readers._READERS['boss_documents']
        root, parent = self.battle(('boss_documents', spec, 'ro6_b_5', '0'))
        self.assertTrue(parent.open_boss_documents())
        page = self.host.pages.currentWidget()
        request = next(r for r in model.related_entities(page.panel.result, '0') if r['key'] == '1')
        page.panel.related.setCurrentIndex(page.panel.related.findData(request))
        self.assertTrue(page.panel.follow_entity())
        self.assertIs(self.host.pages.currentWidget(), root)
        self.assertEqual(parent.enemy_key, '1')
        self.assertEqual(parent.tabs.currentIndex(), 1)
        self.assertNotIn(page, self.host.history)


if __name__ == '__main__':
    unittest.main()
