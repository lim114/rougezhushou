import unittest
from copy import deepcopy

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from rouge.p2_technology_upgrade_view import TechnologyTargetDialog, TechnologyUpgradePlannerDialog


class TechnologyUpgradeViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.snapshot = {'profile_name': '公开临时账户声明', 'nodes': {
            'rogue_6_outbuff_10': 'locked', 'rogue_6_outbuff_11': 'locked', 'rogue_6_difficulty_1': 'locked'}}
        self.window = TechnologyUpgradePlannerDialog(self.snapshot); self.window.show(); self.app.processEvents()

    def tearDown(self): self.window.close(); self.window.deleteLater(); self.app.processEvents()

    def test_initial_mode_grade_budget_are_unknown_and_refunds_not_default_zero(self):
        self.assertTrue(self.window.isVisible()); self.assertIsNone(self.window.mode.currentData())
        self.assertEqual((self.window.grade.value(), self.window.budget.value()), (-1, -1))
        editor = TechnologyTargetDialog(parent=self.window)
        self.assertIsNone(editor.declaration()['accepted']); self.assertIsNone(editor.declaration()['charged_tokens'])
        self.assertIsNone(editor.declaration()['refunded_tokens']); editor.deleteLater()
        self.assertEqual(self.window.gates.item(0, 7).text(), '未知')

    def test_actual_modal_target_addition_updates_gate_in_a_temporary_branch(self):
        self.window.mode.setCurrentIndex(self.window.mode.findData('regular'))
        self.window.grade.setValue(3); self.window.budget.setValue(5)
        before = deepcopy(self.snapshot)
        def fill():
            editor = QApplication.activeModalWidget(); self.assertIsInstance(editor, TechnologyTargetDialog)
            editor.node.setCurrentIndex(editor.node.findData('rogue_6_outbuff_10'))
            editor.acceptance.setCurrentIndex(editor.acceptance.findData(True)); editor.charge.setValue(2); editor.refund.setValue(0)
            editor.accept()
        QTimer.singleShot(0, fill); self.window.add_button.click(); self.window.calculate_button.click()
        self.assertEqual(self.window.table.rowCount(), 1); self.assertEqual(self.window.table.item(0, 6).text(), '3')
        self.assertEqual(self.window.gates.item(0, 4).text(), '不符合'); self.assertEqual(self.window.gates.item(0, 5).text(), '符合')
        self.assertEqual(self.window.gates.item(0, 6).text(), '未解锁（声明）')
        self.assertEqual(self.snapshot, before); self.assertEqual(self.window.snapshot, before)

    def test_context_change_invalidates_without_overwriting_targets_or_account_snapshot(self):
        self.window.steps = [{'node_id': 'rogue_6_outbuff_10', 'accepted': True, 'charged_tokens': 2, 'refunded_tokens': 0}]
        self.window.mode.setCurrentIndex(self.window.mode.findData('regular')); self.window.grade.setValue(3)
        self.window.calculate_button.click(); steps = deepcopy(self.window.steps)
        self.window.mode.setCurrentIndex(self.window.mode.findData('other'))
        self.assertIsNone(self.window.result); self.assertFalse(self.window.copy_button.isEnabled())
        self.assertEqual(self.window.steps, steps); self.window.calculate_button.click()
        self.assertFalse(self.window.result['final_gates'][0]['eligible_reference'])
        self.assertEqual(self.window.gates.item(0, 7).text(), '未知')


if __name__ == '__main__': unittest.main()


class TechnologyUpgradeEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_actual_reference_entry_captures_independent_readonly_snapshot(self):
        from rouge.technology_view import TechnologyReferencePanel
        from rouge.p2_technology_upgrade import capture_account_reference
        panel=TechnologyReferencePanel();panel.show()
        before=capture_account_reference(panel.account_state)
        panel.upgrade_planner_button.click();self.app.processEvents()
        window=panel.upgrade_planner_window;self.assertTrue(window.isVisible())
        self.assertEqual(window.snapshot,before)
        window.mode.setCurrentIndex(window.mode.findData('regular'));window.budget.setValue(100)
        self.assertEqual(capture_account_reference(panel.account_state),before)
        panel.close();window.close();panel.deleteLater();self.app.processEvents()
