"""Actual MainWindow wiring, temporary public state, no capture or chat sends."""
import tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
import rouge.app as module


class Batch185WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='public-185-');self.addCleanup(temp.cleanup);directory=Path(temp.name)
        for key,name in (('RUN_STATE','run.json'),('OPERATOR_STATE','account.json'),('SETTINGS','settings.json')):
            patched=patch.object(module,key,directory/name);patched.start();self.addCleanup(patched.stop)
        backend=module.DesktopBackend
        patched=patch.object(module,'DesktopBackend',lambda _path,callback:backend(directory/'chat',callback))
        patched.start();self.addCleanup(patched.stop)
        patched=patch.object(module,'list_game_windows',return_value=[]);patched.start();self.addCleanup(patched.stop)
        self.window=module.MainWindow();self.addCleanup(self.window.close)
        self.window.show();self.qt.processEvents();self.assertFalse(self.window.auto.isChecked())

    def test_mainwindow_public_tools_run_and_refresh_preserves_user_query(self):
        panel=self.window.offline_tools;self.window.centralWidget().setCurrentWidget(panel)
        panel.select_query('calibration','worksheets');panel.run_button.click()
        end=time.monotonic()+8
        while panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(panel._workers);self.assertEqual(panel.result_snapshot()['case_count'],10)
        editor=panel.editor.toPlainText();before=panel.result_view.toHtml()
        self.window.select_battle_stage('ro6_n_1_2');self.qt.processEvents()
        self.assertEqual(panel.current_query(),('calibration','worksheets'))
        self.assertEqual(panel.editor.toPlainText(),editor);self.assertEqual(panel.result_view.toHtml(),before)
        self.assertEqual(panel._stage,'ro6_n_1_2');self.assertTrue(self.window.isVisible())

    def test_map_position_bind_and_fixed_battle_navigation(self):
        graph={'zone_id':'zone_1','template_id':'public-t','grid':{'rows':3,'cols':4},'edges':[],
               'nodes':[{'id':'a','row':1,'col':2,'distance':2,'observed_type':'不期而遇'}]}
        self.window.map_view.graph=graph;self.window.map_view.historical=False
        self.window.map_view.select_node('a');panel=self.window.node_catalog
        self.assertEqual(self.window.map_view.selected,'a')
        self.assertTrue(panel.bind_button.isEnabled());panel.bind_button.click()
        self.assertIn('第2行、第3列',panel.context_label.text());self.assertTrue(panel.dossier['rows'])
        self.window.show_catalog_battle('ro6_n_1_2');self.qt.processEvents()
        self.assertEqual(self.window.target_stage.currentData(),'ro6_n_1_2')
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.battle_preview)

    def test_successful_calculation_caches_copy_without_rewriting_tools_editor(self):
        panel=self.window.offline_tools;before=panel.editor.toPlainText()
        self.window.use_run_training.setChecked(False);self.window.select_operator('mechanist');self.window.calculate()
        self.assertIsNotNone(self.window.damage_result)
        self.assertEqual(panel._scenario,self.window.damage_result['scenario'])
        self.assertEqual(before,panel.editor.toPlainText())
        panel.import_scenario.click();self.assertIn('mechanist',panel.editor.toPlainText())
