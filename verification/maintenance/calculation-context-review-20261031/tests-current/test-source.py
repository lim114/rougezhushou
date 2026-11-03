"""A failed current calculation cannot remain an importable previous scenario."""
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QPlainTextEdit
from rouge import app as module
from tests import test_state_calculation_updates as fixture

ROOT=Path(__file__).resolve().parents[1]
COMPARISONS=[]

class CalculationContextReviewTests(unittest.TestCase):
    setUp=fixture.StateCalculationUpdateTests.setUp
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance()or QApplication([])
        scope=dict(module.__dict__)
        exec(compile((ROOT/'research/calculation-context-review-20261031/before-calculate.py').read_bytes(),'<own-prior-calculate>','exec'),scope)
        cls.prior=staticmethod(scope['calculate'])
    def importers(self):
        return [getattr(self.window,name)for name in('offline_tools','paired_calibration','timing_calibration','bounded_calibration','calibration_experiment')]
    def valid(self):
        self.window.select_operator('mechanist');self.window.calculate()
        self.assertIsNotNone(self.window.damage_result)
        self.assertTrue(all(p._scenario is not None for p in self.importers()))
    def cleared(self):
        self.assertIsNone(self.window.damage_result)
        self.assertTrue(all(p._scenario is None for p in self.importers()),'A previous scenario remains importable as current')
        self.assertFalse(self.window.paired_calibration.before_import_button.isEnabled())
        self.assertFalse(self.window.paired_calibration.after_import_button.isEnabled())
        for name in('timing_calibration','bounded_calibration','calibration_experiment'):
            self.assertFalse(getattr(self.window,name).import_button.isEnabled())
    def test_bad_timing_input_clears_current_import_cache_without_losing_drafts_and_can_recover(self):
        self.valid();w=self.window
        drafts={p:[e.toPlainText()for e in p.findChildren(QPlainTextEdit)]for p in self.importers()}
        w.timing_scenario.setPlainText('{');self.cleared()
        self.assertIn('战斗时序情景',w.damage_text.toPlainText())
        for p,body in drafts.items():self.assertEqual([e.toPlainText()for e in p.findChildren(QPlainTextEdit)],body)
        w.timing_scenario.clear();self.valid()
    def test_empty_operator_selection_clears_current_import_cache(self):
        self.valid();w=self.window;w.operator.blockSignals(True);w.operator.setCurrentIndex(-1);w.operator.blockSignals(False)
        w.calculate();self.cleared();self.assertIn('暂无已确认招募',w.damage_text.toPlainText())
    def test_no_selected_skill_clears_current_import_cache(self):
        self.valid();w=self.window;w.skill.blockSignals(True);w.skill.setCurrentIndex(-1);w.skill.blockSignals(False)
        w.calculate();self.cleared();self.assertIn('尚无已实现的技能',w.damage_text.toPlainText())
    def test_unimplemented_operator_clears_previous_current_cache(self):
        from rouge.catalog import operator_profiles,catalog
        self.valid();identity=next(i for i in operator_profiles()if i not in catalog()['operators'])
        self.window.select_operator(identity);self.window.calculate();self.cleared()
        self.assertIn('尚未实现',self.window.damage_text.toPlainText())
    def test_all_catalog_skill_scenarios_results_and_reports_remain_equal(self):
        from rouge.catalog import catalog
        w=self.window;COMPARISONS.clear()
        for op,profile in catalog()['operators'].items():
            w.select_operator(op)
            for skill in range(1,len(profile['skills'])+1):
                w.skill.setCurrentIndex(w.skill.findData(skill))
                self.prior(w);before=deepcopy(w.damage_result);report=w.damage_text.toPlainText()
                w.calculate();self.assertIsNotNone(before);self.assertEqual(w.damage_result,before);self.assertEqual(w.damage_text.toPlainText(),report)
                self.assertTrue(all(p._scenario==before['scenario']for p in self.importers()))
                COMPARISONS.append({'operator':op,'skill':skill,'complete_result_and_report_equal':True})
        self.assertEqual(len(COMPARISONS),sum(len(p['skills'])for p in catalog()['operators'].values()))
    def test_batched_input_does_not_publish_an_intermediate_invalid_cache(self):
        from rouge.ui_state import calculation_batch
        self.valid();w=self.window;before=deepcopy(w.damage_result)
        with calculation_batch(w):
            w.timing_scenario.setPlainText('{')
            self.assertEqual(w.damage_result,before)
            self.assertTrue(all(p._scenario==before['scenario']for p in self.importers()))
            w.timing_scenario.clear()
        self.assertEqual(w.damage_result,before)
