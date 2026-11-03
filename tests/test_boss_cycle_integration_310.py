"""Manual parent entry and old reader isolation; not executed in preparation."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import boss_cycle_reference as model
from rouge.battle_preview import battle_data
from rouge.battle_view import BattlePreviewPanel

KEYS=(('ro6_b_5','enemy_2147_shophm',0),('ro6_b_5','enemy_2148_shorbb',0))

class BossCycleIntegration310Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def battle(self):
        panel=BattlePreviewPanel();panel.show();self.addCleanup(panel.close)
        self.addCleanup(lambda:panel.boss_cycle_window.close()if panel.boss_cycle_window else None)
        panel._load_stage(KEYS[0][0]);panel._render_enemy(*KEYS[0][1:]);self.qt.processEvents();return panel

    def snapshot(self,panel):
        def reader(widget):
            c=widget.textCursor();return(widget.toPlainText(),c.anchor(),c.position(),widget.verticalScrollBar().value())
        return deepcopy({'stage':panel.current_stage,'context':panel.context,'wave':panel.wave_combo.currentData(),
            'enemy_branch':panel.enemy_choices.branch.currentData(),'enemy':panel.enemy_combo.currentData(),
            'include_branches':panel.include_branches.isChecked(),'technical':panel.technical.isChecked(),
            'tile':panel._tile_cell,'row':panel.grid.selected,'original_row':panel.original.selected,
            'original_cell':panel.original.reference_cell,'detail_key':panel._detail_key,
            'spawn':reader(panel.spawn_detail),'enemy_text':reader(panel.enemy_detail)})

    def test_both_exact_entries_are_manual_modeless_and_keep_selected_entry_name(self):
        panel=self.battle();self.assertIsNone(panel.boss_cycle_window)
        for key in KEYS:
            panel._render_enemy(*key[1:]);panel._refresh_boss_cycle()
            self.assertTrue(panel.boss_cycle_button.isVisible());self.assertTrue(panel.boss_cycle_button.isEnabled())
            self.assertTrue(panel.open_boss_cycle_reference());window=panel.boss_cycle_window
            self.assertEqual(window.identity,key);self.assertFalse(window.isModal());self.assertIsNone(window.topic.currentData())
            self.assertIn(window.result['reference']['entry_name'],window.windowTitle())

    def test_reading_all_topics_from_both_entries_does_not_change_parent(self):
        panel=self.battle()
        for key in KEYS:
            panel._render_enemy(*key[1:]);before=self.snapshot(panel);panel.open_boss_cycle_reference();window=panel.boss_cycle_window
            for index in range(window.topic.count()):window.topic.setCurrentIndex(index);self.qt.processEvents()
            self.assertEqual(self.snapshot(panel),before);self.assertEqual(window.identity,key)

    def test_other_enemies_and_particle_have_no_cycle_entry(self):
        panel=self.battle();panel.open_boss_cycle_reference();window=panel.boss_cycle_window
        for entry in battle_data()['stages'][KEYS[0][0]]['enemies']:
            if(entry['id'],entry['level'])in{(key[1],key[2])for key in KEYS}:continue
            panel._render_enemy(entry['id'],entry['level'])
            self.assertTrue(panel.boss_cycle_button.isHidden());self.assertFalse(panel.open_boss_cycle_reference())
            self.assertIsNone(window.identity);self.assertEqual(window.topic.count(),0)
            self.assertEqual(window.lorentz_picture.key,(None,None,''));self.assertEqual(window.cube_picture.key,(None,None,''))

    def test_switching_exact_entry_clears_old_topic_until_manual_reopen(self):
        panel=self.battle();panel.open_boss_cycle_reference();window=panel.boss_cycle_window;window.topic.setCurrentIndex(1)
        panel._render_enemy(*KEYS[1][1:]);self.assertIsNone(window.identity);self.assertEqual(window.topic.count(),0)
        self.assertTrue(panel.boss_cycle_button.isEnabled());self.assertTrue(panel.open_boss_cycle_reference())
        self.assertEqual(window.identity,KEYS[1]);self.assertIsNone(window.topic.currentData())

    def test_no_stage_and_wrong_stage_cannot_reuse_old_cycle_reader(self):
        panel=self.battle();panel.open_boss_cycle_reference();window=panel.boss_cycle_window
        panel.current_stage=None;panel._render_enemy(*KEYS[0][1:])
        self.assertTrue(panel.boss_cycle_button.isHidden());self.assertIsNone(window.identity)
        panel._load_stage('ro6_b_6');panel._render_enemy(*KEYS[0][1:])
        self.assertTrue(panel.boss_cycle_button.isHidden());self.assertIsNone(window.identity)

    def test_source_loss_disables_target_and_recovery_never_restores_prior_topic(self):
        panel=self.battle()
        for key in KEYS:
            panel._render_enemy(*key[1:]);panel.open_boss_cycle_reference();window=panel.boss_cycle_window;window.topic.setCurrentIndex(1)
            with patch.object(model,'cycle_reference',return_value={'source_valid':False,'status':'source_unavailable','reference':None,'source_identity':None}):
                panel._refresh_boss_cycle();self.assertFalse(panel.boss_cycle_button.isEnabled())
                self.assertIsNone(window.identity);self.assertFalse(panel.open_boss_cycle_reference())
            panel._refresh_boss_cycle();self.assertTrue(panel.boss_cycle_button.isEnabled());self.assertIsNone(window.identity)
            self.assertTrue(panel.open_boss_cycle_reference());self.assertIsNone(window.topic.currentData())

    def test_existing306_and309_reader_methods_still_have_independent_identity_and_windows(self):
        panel=self.battle();panel.open_boss_cycle_reference();cycle=panel.boss_cycle_window
        key=('ro6_b_6','enemy_2150_shchmr',0);panel._load_stage(key[0]);panel._render_enemy(*key[1:])
        self.assertTrue(panel.boss_cycle_button.isHidden());self.assertIsNone(cycle.identity)
        self.assertTrue(panel.open_boss_phase_reference());phase=panel.boss_phase_window;self.addCleanup(phase.close)
        self.assertEqual(phase.identity,key);self.assertIsNot(phase,cycle)
        key=('ro6_n_2_3','enemy_2133_shdopl_lancer',0);panel._load_stage(key[0]);panel._render_enemy(*key[1:])
        self.assertTrue(panel.open_enemy_form());form=panel.enemy_form_window;self.addCleanup(form.close)
        self.assertEqual(form.identity,key);self.assertIsNot(form,cycle);self.assertIsNone(phase.identity)
