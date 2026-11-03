"""Actual MainWindow uses the update reader without writing the temporary run."""
from copy import deepcopy
from tests import test_batch185_mainwindow as setup_module
import unittest
from rouge.expansion_view import ExpansionUpdatePanel
from rouge import expansion_reference as model

class ExpansionIntegration313Tests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def test_actual_mainwindow_tab_and_both_legacy_version_notices(self):
        tabs=self.window.centralWidget();p=self.window.expansion_update
        self.assertIsInstance(p,ExpansionUpdatePanel);self.assertEqual(tabs.tabText(tabs.indexOf(p)),'版本与更新')
        self.assertIn('更新前',self.window.battle_preview.version_notice.text());self.assertIn('尚未完整适配',self.window.damage_version_notice.text())
        self.assertIsNone(p.result);tabs.setCurrentWidget(p);self.qt.processEvents();self.assertTrue(p.isVisible())
    def test_update_reading_does_not_apply_current_items_difficulty_or_reset_run(self):
        p=self.window.expansion_update;tabs=self.window.centralWidget();before=deepcopy(self.window.run.state);context=deepcopy(self.window.battle_preview.context)
        tabs.setCurrentWidget(p)
        for cat in('difficulty','relics','squads','choices'):
            p.category.setCurrentIndex(p.category.findData(cat));self.assertGreater(p.entries.count(),0);p.entries.setCurrentRow(0);p.refresh_reference();self.qt.processEvents()
            self.assertIsNotNone(p.result);self.assertFalse(p.result['mutations_applied'])
        self.assertEqual(self.window.run.state,before);self.assertEqual(self.window.battle_preview.context,context);self.assertFalse(self.window.auto.isChecked())
    def test_existing_preview_and_update_catalog_remain_explicitly_different_versions(self):
        self.assertEqual(len(__import__('rouge.battle_preview',fromlist=['battle_data']).battle_data()['stages']),105)
        self.assertEqual(len(model.rows('stages',changes_only=False)),184)
        self.window.show_catalog_battle('ro6_n_1_2');self.qt.processEvents()
        self.assertEqual(self.window.battle_preview.current_stage,'ro6_n_1_2');self.assertIn('版本与更新',self.window.battle_preview.version_notice.text())

if __name__=='__main__':unittest.main()
