"""Exact manual battle entry and old reader isolation; root runs actual Qt tests."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
from rouge import boss_phase_reference as model
from rouge.battle_preview import battle_data
from rouge.battle_view import BattlePreviewPanel

KEY=('ro6_b_6','enemy_2150_shchmr',0)


class BossPhaseIntegration309Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def battle(self):
        panel=BattlePreviewPanel();panel.show();self.addCleanup(panel.close)
        self.addCleanup(lambda:panel.boss_phase_window.close()if panel.boss_phase_window else None)
        panel._load_stage(KEY[0]);panel._render_enemy(*KEY[1:]);self.qt.processEvents();return panel

    def snapshot(self,panel):
        def reading(widget):
            cursor=widget.textCursor()
            return(widget.toPlainText(),cursor.anchor(),cursor.position(),widget.verticalScrollBar().value())
        return deepcopy({'stage':panel.current_stage,'context':panel.context,'wave':panel.wave_combo.currentData(),
            'enemy_branch':panel.enemy_choices.branch.currentData(),'enemy':panel.enemy_combo.currentData(),
            'include_branches':panel.include_branches.isChecked(),'technical':panel.technical.isChecked(),
            'tile':panel._tile_cell,'row':panel.grid.selected,'original_row':panel.original.selected,
            'original_cell':panel.original.reference_cell,'detail':panel._detail_key,
            'spawn':reading(panel.spawn_detail),'enemy_text':reading(panel.enemy_detail)})

    def test_exact_target_only_is_visible_and_open_is_manual_modeless(self):
        panel=self.battle();self.assertTrue(panel.boss_phase_button.isVisible());self.assertTrue(panel.boss_phase_button.isEnabled())
        self.assertIsNone(panel.boss_phase_window);panel._refresh_boss_phase();self.assertIsNone(panel.boss_phase_window)
        self.assertTrue(panel.open_boss_phase_reference());self.assertEqual(panel.boss_phase_window.identity,KEY)
        self.assertTrue(panel.boss_phase_window.isVisible());self.assertFalse(panel.boss_phase_window.isModal())

    def test_reading_does_not_change_parent_filters_selection_map_context_or_text(self):
        panel=self.battle();before=self.snapshot(panel);panel.open_boss_phase_reference()
        window=panel.boss_phase_window
        for index in range(window.phase.count()):window.phase.setCurrentIndex(index);self.qt.processEvents()
        self.assertEqual(self.snapshot(panel),before)

    def test_change_enemy_hides_entry_and_clears_previous_window(self):
        panel=self.battle();panel.open_boss_phase_reference();window=panel.boss_phase_window
        entry=next(e for e in battle_data()['stages'][KEY[0]]['enemies']if e['id']!=KEY[1])
        panel._render_enemy(entry['id'],entry['level'])
        self.assertTrue(panel.boss_phase_button.isHidden());self.assertFalse(panel.open_boss_phase_reference())
        self.assertIsNone(window.identity);self.assertEqual(window.player.toPlainText(),'')
        self.assertEqual(window.boss_picture.key,(None,None,''))

    def test_stage_clear_and_other_stage_cannot_borrow_same_named_enemy(self):
        panel=self.battle();panel.open_boss_phase_reference();window=panel.boss_phase_window
        panel.current_stage=None;panel._render_enemy(KEY[1],KEY[2])
        self.assertTrue(panel.boss_phase_button.isHidden());self.assertIsNone(window.identity)
        panel.set_stage(None);self.assertTrue(panel.boss_phase_button.isHidden());self.assertIsNone(window.identity)
        panel._load_stage('ro6_n_1_1');panel._render_enemy(KEY[1],KEY[2])
        self.assertTrue(panel.boss_phase_button.isHidden());self.assertIsNone(window.identity)

    def test_source_failure_and_recovery_never_automatically_refill_old_window(self):
        panel=self.battle();panel.open_boss_phase_reference();window=panel.boss_phase_window;window.phase.setCurrentIndex(1)
        with patch.object(model,'phase_reference',return_value={'source_valid':False,'status':'source_unavailable','reference':None,'source_identity':None}):
            panel._refresh_boss_phase();self.assertFalse(panel.boss_phase_button.isEnabled())
            self.assertIsNone(window.identity);self.assertEqual(window.phase.count(),0)
            self.assertFalse(panel.open_boss_phase_reference())
        panel._refresh_boss_phase();self.assertTrue(panel.boss_phase_button.isEnabled());self.assertIsNone(window.identity)
        self.assertEqual(window.player.toPlainText(),'');self.assertTrue(panel.open_boss_phase_reference())
        self.assertIsNone(window.phase.currentData())

    def test_existing306_form_reader_has_independent_button_window_and_behavior(self):
        panel=self.battle();panel.open_boss_phase_reference();boss_window=panel.boss_phase_window
        identity=('ro6_n_2_3','enemy_2133_shdopl_lancer',0)
        panel._load_stage(identity[0]);panel._render_enemy(*identity[1:])
        self.assertTrue(panel.boss_phase_button.isHidden());self.assertIsNone(boss_window.identity)
        self.assertTrue(panel.enemy_form_button.isVisible());self.assertTrue(panel.enemy_form_button.isEnabled())
        self.assertTrue(panel.open_enemy_form());self.addCleanup(panel.enemy_form_window.close)
        self.assertEqual(panel.enemy_form_window.identity,identity)
        self.assertIsNot(panel.enemy_form_window,boss_window)
