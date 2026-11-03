"""Explicit player query actions reach their existing reader, without a debug menu."""
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from tests import test_state_calculation_updates as fixture


class PlayerToolNavigationReviewTests(unittest.TestCase):
    setUp=fixture.StateCalculationUpdateTests.setUp
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def open(self,name,query):
        w=self.window;w.skill.setCurrentIndex(w.skill.findData(2));w.show();w.mechanist_reference_tools.toggle.setChecked(True);self.qt.processEvents()
        workspace=w.centralWidget();workspace.setCurrentWidget(next(p for p,(_,label)in workspace.pages.items()if label=='干员与技能'))
        button=getattr(w,name);self.assertTrue(button.isEnabled());button.click();self.qt.processEvents()
        self.assertEqual(w.offline_tools.current_query(),('calibration',query))
        self.assertTrue(w.centralWidget().developer_dialog.isVisible(),'Player action selected a hidden page instead of opening it')
        self.assertIs(w.centralWidget().currentWidget(),w.offline_tools)
        self.assertFalse(w.centralWidget().developer_tools)
        self.assertFalse(w.centralWidget().developer_tabs.tabBar().isVisible())
        self.assertTrue(w.offline_tools.isVisible())
    def test_barrier_query_action_opens_selected_reader(self):self.open('barrier_ledger_button','barrier-ledger')
    def test_shield_grants_action_opens_selected_reader(self):self.open('shield_grant_button','shield-grants')
    def test_shield_inventory_action_opens_selected_reader(self):self.open('shield_inventory_button','shield-inventory')
    def test_explosion_values_action_opens_selected_reader(self):self.open('explosion_values_button','explosion-values')
    def test_technical_actions_are_collapsed_by_default_and_absent_for_other_operators(self):
        w=self.window;w.skill.setCurrentIndex(w.skill.findData(2));w.show();self.qt.processEvents()
        workspace=w.centralWidget();workspace.setCurrentWidget(next(p for p,(_,label)in workspace.pages.items()if label=='干员与技能'));self.qt.processEvents()
        self.assertFalse(w.mechanist_reference_tools.toggle.isChecked())
        self.assertTrue(w.mechanist_reference_tools.isVisible());self.assertFalse(w.barrier_ledger_button.isVisible())
        w.select_operator('kaltsit');self.qt.processEvents()
        self.assertFalse(w.mechanist_reference_tools.isVisible());self.assertFalse(w.barrier_ledger_button.isVisible())
    def test_switching_queries_preserves_manual_draft_and_back_returns_to_player_page(self):
        w=self.window;state=deepcopy(w.run.state);workspace=w.centralWidget()
        page=next(p for p,(_,label)in workspace.pages.items()if label=='干员与技能');workspace.setCurrentWidget(page)
        self.open('barrier_ledger_button','barrier-ledger');w.offline_tools.editor.setPlainText('{"manual_test_draft": true}')
        self.open('shield_inventory_button','shield-inventory');self.open('barrier_ledger_button','barrier-ledger')
        self.assertEqual(w.offline_tools.editor.toPlainText(),'{"manual_test_draft": true}')
        self.assertTrue(workspace.go_back());self.assertIs(workspace.currentWidget(),page)
        self.assertFalse(workspace.developer_dialog.isVisible());self.assertEqual(w.run.state,state)
    def test_explicit_player_query_does_not_enable_generic_development_navigation(self):
        self.open('shield_grant_button','shield-grants');workspace=self.window.centralWidget()
        workspace.developer_dialog.close();self.qt.processEvents()
        self.assertFalse(workspace.setCurrentWidget(self.window.paired_calibration))
        self.assertFalse(workspace.developer_dialog.isVisible())


class DiagnosticToolCompatibilityTests(unittest.TestCase):
    def test_original_flat_workspace_accepts_explicit_tool_target_without_new_navigation(self):
        from PySide6.QtWidgets import QWidget
        from rouge.diagnostic_workspace import DiagnosticWorkspace
        qt=QApplication.instance()or QApplication([]);workspace=DiagnosticWorkspace();self.addCleanup(workspace.close)
        page=QWidget();workspace.addTab(page,'局外工具')
        self.assertTrue(workspace.setCurrentWidget(page,explicit_tool=True));self.assertIs(workspace.currentWidget(),page)
        self.assertFalse(workspace.setCurrentWidget(QWidget(),explicit_tool=True));self.assertIs(workspace.currentWidget(),page)

