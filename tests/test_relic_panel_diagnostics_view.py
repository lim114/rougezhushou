import time,unittest,json
from PySide6.QtWidgets import QApplication
from rouge.offline_tools_view import OfflineToolsPanel,public_payload

class RelicPanelDiagnosticViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.p=OfflineToolsPanel();self.p.resize(1050,750);self.p.show();self.p.select_query('calibration','relic-panels')
    def tearDown(self):self.p.close();self.p.deleteLater();self.qt.processEvents()
    def execute(self):
        self.p.run_button.click();end=time.monotonic()+8
        while self.p._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(self.p._workers);self.assertIsNotNone(self.p.result_snapshot(),self.p.status.text())
    def test_default_combo_runs_from_actual_widget_and_labels_model_and_unknown(self):
        self.execute();r=self.p.result_snapshot();text=self.p.result_view.toPlainText()
        self.assertEqual(len(r['source_rows']),3);self.assertIn('藏品组合与面板差值诊断',text)
        for phrase in ('移除单件边际差值','非相加模型残差','实际加成','共同背景','未知'):self.assertIn(phrase,text)
        self.assertFalse(r['native_verified'])
    def test_refresh_and_switch_do_not_replace_declared_combo_or_reading(self):
        self.execute();before=(self.p.editor.toPlainText(),self.p.result_snapshot())
        self.p.set_scenario({'operator':'kaltsit','skill':2})
        self.p.select_query('calibration','panel');self.p.select_query('calibration','relic-panels')
        self.qt.processEvents();self.assertEqual(before,(self.p.editor.toPlainText(),self.p.result_snapshot()))
    def test_import_scenario_retains_independent_targeted_buffs_and_only_explicit_subset(self):
        s={'operator':'kaltsit','skill':2,'relic_ids':['rogue_6_relic_assign_13','rogue_6_relic_legacy_29'],
           'char_buff_ids':['rogue_6_from_relic_13'],'char_buffs_complete':True}
        payload=public_payload('calibration','relic-panels');payload['relic_ids']=['rogue_6_relic_assign_13']
        self.p.editor.setPlainText(json.dumps(payload));self.p.set_scenario(s);self.p.import_scenario.click();self.execute()
        r=self.p.result_snapshot();self.assertEqual(r['background_relic_ids'],['rogue_6_relic_legacy_29'])
        self.assertEqual(r['preserved_targeted_buff_ids'],['rogue_6_from_relic_13'])
        self.assertEqual(json.loads(self.p.editor.toPlainText())['scenario'],s)

if __name__=='__main__':unittest.main()
