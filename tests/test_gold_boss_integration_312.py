"""Actual parent-widget seams; prepared only, root executes after promotion."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from rouge import gold_boss_reference as model
from rouge.battle_view import BattlePreviewPanel
from rouge.gold_boss_view import PICTURES

KEYS = (('ro6_b_2', 'enemy_2140_shsgzd', 0), ('ro6_b_2', 'enemy_2142_shsggd', 0),
        ('ro6_b_2_b', 'enemy_2141_shsgz2', 0))


class GoldBossIntegration312Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def parent(self):
        panel = BattlePreviewPanel()
        panel.resize(1280, 900)
        panel.show()
        def cleanup():
            if panel.gold_boss_window is not None:
                panel.gold_boss_window.close()
            panel.close()
        self.addCleanup(cleanup)
        self.qt.processEvents()
        return panel

    def show_entry(self, panel, identity):
        panel.set_stage(identity[0])
        panel._render_enemy(identity[1], identity[2])
        self.qt.processEvents()

    def snapshot(self, panel):
        return deepcopy({'context': panel.context, 'stage': panel.current_stage,
            'wave': panel.wave_combo.currentData(), 'enemy': panel.enemy_combo.currentData(),
            'technical': panel.technical.isChecked(), 'row': panel.grid.selected, 'tile': panel._tile_cell,
            'original_selected': panel.original.selected, 'original_cell': panel.original.reference_cell,
            'spawn': panel.spawn_detail.toPlainText(), 'enemy_text': panel.enemy_detail.toPlainText()})

    def test_all_three_exact_entries_open_only_manually_with_selected_identity(self):
        panel = self.parent()
        self.assertIsNone(panel.gold_boss_window)
        for identity in KEYS:
            self.show_entry(panel, identity)
            self.assertTrue(panel.gold_boss_button.isVisible())
            self.assertTrue(panel.gold_boss_button.isEnabled())
            self.assertTrue(panel.open_gold_boss_reference())
            window = panel.gold_boss_window
            self.assertTrue(window.isVisible())
            self.assertEqual(window.identity, identity)
            self.assertEqual(window.result['reference']['enemy_id'], identity[1])
            self.assertIsNone(window.topic.currentData())

    def test_other_stage_same_enemy_names_other_boss_and_no_stage_hide_entry_and_clear_old_reader(self):
        panel = self.parent()
        for identity in (('ro6_b_4', KEYS[0][1], 0), ('ro6_b_6', 'enemy_2150_shchmr', 0), None):
            self.show_entry(panel, KEYS[0])
            self.assertTrue(panel.open_gold_boss_reference())
            if identity is None:
                panel.set_stage(None)
            else:
                self.show_entry(panel, identity)
            self.qt.processEvents()
            self.assertTrue(panel.gold_boss_button.isHidden())
            self.assertFalse(panel.open_gold_boss_reference())
            self.assertIsNone(panel.gold_boss_window.identity)
            self.assertEqual(panel.gold_boss_window.player.toPlainText(), '')
            for attribute, _, _ in PICTURES:
                self.assertEqual(getattr(panel.gold_boss_window, attribute).key, (None, None, ''))

    def test_reader_open_topic_and_refresh_keep_parent_map_filters_context_and_text(self):
        panel = self.parent()
        self.show_entry(panel, KEYS[0])
        panel.technical.setChecked(True)
        starts = {(row['route']['start']['row'], row['route']['start']['col'])
                  for row in panel.rows if row['route']['start'] is not None}
        cell = next({'row': r, 'col': c} for r, line in enumerate(panel.grid.stage['map'])
                    for c, _ in enumerate(line) if (r, c) not in starts)
        panel._cell_selected(cell)
        before = self.snapshot(panel)
        self.assertTrue(panel.open_gold_boss_reference())
        window = panel.gold_boss_window
        for i in range(1, window.topic.count()):
            window.topic.setCurrentIndex(i)
            panel._refresh_gold_boss()
            self.qt.processEvents()
            self.assertEqual(self.snapshot(panel), before)

    def test_source_loss_and_recovery_do_not_repopulate_or_reopen_old_reader(self):
        panel = self.parent()
        self.show_entry(panel, KEYS[1])
        panel.open_gold_boss_reference()
        window = panel.gold_boss_window
        window.topic.setCurrentIndex(1)
        with patch.object(model, 'gold_reference', return_value=None):
            panel._refresh_gold_boss()
            self.assertFalse(panel.gold_boss_button.isEnabled())
            self.assertIsNone(window.identity)
            self.assertEqual(window.topic.count(), 0)
        panel._refresh_gold_boss()
        self.assertTrue(panel.gold_boss_button.isEnabled())
        self.assertIsNone(window.identity)
        self.assertEqual(window.player.toPlainText(), '')
        self.assertTrue(panel.open_gold_boss_reference())
        self.assertEqual(window.identity, KEYS[1])
        self.assertIsNone(window.topic.currentData())

    def test_switching_exact_subject_clears_topic_before_the_next_manual_open(self):
        panel = self.parent()
        for before_key, after_key in zip(KEYS, KEYS[1:] + KEYS[:1]):
            self.show_entry(panel, before_key)
            panel.open_gold_boss_reference()
            window = panel.gold_boss_window
            window.topic.setCurrentIndex(1)
            self.show_entry(panel, after_key)
            self.assertIsNone(window.identity)
            self.assertEqual(window.topic.count(), 0)
            self.assertEqual(window.technical.toPlainText(), '')
            self.assertTrue(panel.open_gold_boss_reference())
            self.assertEqual(window.identity, after_key)
            self.assertIsNone(window.topic.currentData())

    def test_existing_phase_and_cycle_entries_still_open_their_own_readers(self):
        panel = self.parent()
        entries = (('ro6_b_6', 'enemy_2150_shchmr', 0, 'boss_phase_button', 'open_boss_phase_reference', 'boss_phase_window'),
                   ('ro6_b_5', 'enemy_2147_shophm', 0, 'boss_cycle_button', 'open_boss_cycle_reference', 'boss_cycle_window'))
        for sid, eid, level, button_name, method_name, window_name in entries:
            self.show_entry(panel, (sid, eid, level))
            self.assertTrue(getattr(panel, button_name).isEnabled())
            self.assertTrue(getattr(panel, method_name)())
            self.assertEqual(getattr(panel, window_name).identity, (sid, eid, level))
            self.assertTrue(panel.gold_boss_button.isHidden())
            getattr(panel, window_name).close()


if __name__ == '__main__':
    unittest.main()
