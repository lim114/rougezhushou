import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch
from PySide6.QtWidgets import QApplication,QComboBox
from rouge.ui_state import calculation_batch
from rouge.current_spawn_candidates_view import CurrentSpawnCandidatesPanel
from rouge.current_elbert_view import CurrentElbertPanel


class ApprovedFinallyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def test_failed_nested_batch_releases_without_calculating(self):
        window=SimpleNamespace(_calculation_batch_depth=0,_calculation_requested=False,calculate=Mock())
        with self.assertRaisesRegex(RuntimeError,'input failed'):
            with calculation_batch(window):
                with calculation_batch(window):
                    window._calculation_requested=True
                    raise RuntimeError('input failed')
        self.assertEqual(window._calculation_batch_depth,0)
        self.assertFalse(window._calculation_requested)
        window.calculate.assert_not_called()
        with calculation_batch(window):window._calculation_requested=True
        window.calculate.assert_called_once_with()

    def test_failed_calculation_still_releases_batch(self):
        window=SimpleNamespace(_calculation_batch_depth=0,_calculation_requested=False,calculate=Mock(side_effect=RuntimeError('calculate failed')))
        with self.assertRaisesRegex(RuntimeError,'calculate failed'):
            with calculation_batch(window):window._calculation_requested=True
        self.assertEqual(window._calculation_batch_depth,0)
        self.assertFalse(window._calculation_requested)

    def test_spawn_fill_restores_original_signal_state_and_raises(self):
        combo=QComboBox()
        for blocked in (False,True):
            combo.blockSignals(blocked)
            with self.subTest(blocked=blocked),patch.object(combo,'addItem',side_effect=RuntimeError('fill failed')):
                with self.assertRaisesRegex(RuntimeError,'fill failed'):
                    CurrentSpawnCandidatesPanel._fill(combo,[],None,'select')
                self.assertEqual(combo.signalsBlocked(),blocked)

    def test_elbert_three_cleanup_paths_restore_signals_and_raise(self):
        for method,widget_name,target_name,attribute in [('clear_reference','topic','topic','clear'),('refresh_reference','entity_combo','entities','set_groups'),('_entity_changed','topic','topic','clear')]:
            for blocked in (False,True):
                panel=CurrentElbertPanel('ro6_b_3')
                self.addCleanup(panel.close)
                widget=getattr(panel,widget_name);widget.blockSignals(blocked)
                with self.subTest(method=method,blocked=blocked),patch.object(getattr(panel,target_name),attribute,side_effect=RuntimeError('update failed')):
                    with self.assertRaisesRegex(RuntimeError,'update failed'):getattr(panel,method)()
                    self.assertEqual(widget.signalsBlocked(),blocked)
