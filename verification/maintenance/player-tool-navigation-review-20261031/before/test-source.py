"""Explicit player query actions reach their existing reader, without a debug menu."""
from copy import deepcopy
from unittest.mock import patch
import time,unittest
from PySide6.QtWidgets import QApplication
from tests import test_state_calculation_updates as fixture

PROFILE=[]

class PlayerToolNavigationReviewTests(unittest.TestCase):
    setUp=fixture.StateCalculationUpdateTests.setUp
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def open(self,name,query):
        w=self.window;w.skill.setCurrentIndex(w.skill.findData(2));w.show();self.qt.processEvents()
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


class StartupPanelMeasurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_measure_existing_eight_constructors_without_changing_product_code(self):
        from rouge.offline_tools_view import OfflineToolsPanel
        from rouge.paired_calibration_view import PairedCalibrationPanel
        from rouge.attack_state_sequence_view import AttackStateSequencePanel
        from rouge.timing_calibration_view import TimingCalibrationPanel
        from rouge.bounded_calibration_view import BoundedCalibrationPanel
        from rouge.calibration_experiment_view import CalibrationExperimentPanel
        from rouge.recipient_native_ratio_view import RecipientNativeRatioPanel
        from rouge.relic_order_precision_view import RelicOrderPrecisionPanel
        for cls in(OfflineToolsPanel,PairedCalibrationPanel,AttackStateSequencePanel,TimingCalibrationPanel,BoundedCalibrationPanel,CalibrationExperimentPanel,RecipientNativeRatioPanel,RelicOrderPrecisionPanel):
            original=cls.__init__
            def measured(obj,*a,_original=original,_name=cls.__name__,**kw):
                start=time.perf_counter();_original(obj,*a,**kw);PROFILE.append({'class':_name,'constructor_seconds':time.perf_counter()-start})
            self.enterContext(patch.object(cls,'__init__',measured))
        fixture.StateCalculationUpdateTests.setUp(self)
        self.assertEqual(len(PROFILE),8)
