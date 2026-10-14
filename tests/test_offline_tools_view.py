"""Public fixtures only: no MainWindow, run directory, game or chat integration."""
from copy import deepcopy
import json
import time
import unittest

from PySide6.QtWidgets import QApplication
from rouge.offline_tools_view import (OfflineToolsPanel, QUERIES, public_payload,
    run_offline_query, render_offline_result)


class OfflineToolQueryTests(unittest.TestCase):
    def test_twenty_public_queries_and_chinese_renderers(self):
        count=0
        for family in ('calibration','battle'):
            queries=QUERIES[family]
            for command,title in queries:
                with self.subTest(query=(family,command)):
                    payload=public_payload(family,command);before=deepcopy(payload)
                    result=run_offline_query(family,command,payload)
                    self.assertEqual(payload,before)
                    rendered=render_offline_result(family,command,result)
                    self.assertIn(title,rendered)
                    self.assertIn('尚未验证当前客户端实机',rendered)
                    self.assertIn('技术详情',rendered)
                    json.dumps(result,allow_nan=False)
                    count+=1
        self.assertEqual(count,26)

    def test_skills_keep_complete_totals_unknown_and_conditionals_separate(self):
        result=run_offline_query('calibration','skills',public_payload('calibration','skills'))
        for row in result['rows']:
            self.assertFalse(row.get('native_clock_verified',False))
            self.assertIn(row['full_skill_damage'],(None,0))
            self.assertIn(row['full_skill_healing'],(None,0))
        rendered=render_offline_result('calibration','skills',result)
        self.assertIn('此项不等于原生完整总量',rendered)
        self.assertIn('未知',rendered)

    def test_time_window_is_fragment_local_and_candidates_are_not_probabilities(self):
        window=run_offline_query('battle','window',public_payload('battle','window'))
        self.assertIn('不是全局时间轴',render_offline_result('battle','window',window))
        candidates=run_offline_query('battle','candidates',public_payload('battle','candidates'))
        self.assertIn('生成概率：不提供',render_offline_result('battle','candidates',candidates))

    def test_invalid_public_input_is_rejected(self):
        for payload in ([],{'scenario':{'operator':'unknown'}},{'scenario':{'operator':'mechanist','level':float('nan')}}):
            with self.subTest(payload=payload),self.assertRaises((ValueError,KeyError)):
                run_offline_query('calibration','panel',payload)
        with self.assertRaises(ValueError):run_offline_query('battle','actions',{'stage_id':'invalid'})


class OfflineToolsPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):self.panel=OfflineToolsPanel();self.panel.resize(900,650)

    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()

    def wait_done(self, timeout=8):
        end=time.monotonic()+timeout
        while self.panel._workers and time.monotonic()<end:
            self.app.processEvents();time.sleep(.005)
        self.assertFalse(self.panel._workers,'离线查询未在必要测试窗口内返回。')
        self.app.processEvents()

    def test_all_twenty_queries_run_from_widget(self):
        for family in ('calibration','battle'):
            queries=QUERIES[family]
            for command,title in queries:
                with self.subTest(query=(family,command)):
                    self.panel.select_query(family,command)
                    self.panel.run_button.click();self.wait_done()
                    self.assertIsNotNone(self.panel.result_snapshot(),self.panel.status.text())
                    self.assertIn(title,self.panel.result_view.toPlainText())

    def test_context_refresh_preserves_selection_editor_result_and_scroll(self):
        self.panel.select_query('calibration','skills');self.panel._run();self.wait_done()
        self.panel.show();self.app.processEvents()
        bar=self.panel.result_view.verticalScrollBar();bar.setValue(bar.maximum()//2)
        before=(self.panel.current_query(),self.panel.editor.toPlainText(),
            self.panel.result_snapshot(),self.panel.result_view.toHtml(),bar.value())
        scenario={'operator':'kaltsit','skill':2,'level':90}
        self.panel.set_scenario(scenario);self.panel.set_stage('ro6_n_1_2')
        scenario['level']=1
        self.assertEqual(self.panel._scenario['level'],90)
        self.panel.set_scenario({'operator':'kaltsit','skill':2,'level':90})
        self.panel.set_stage('ro6_n_1_2');self.app.processEvents()
        after=(self.panel.current_query(),self.panel.editor.toPlainText(),
            self.panel.result_snapshot(),self.panel.result_view.toHtml(),bar.value())
        self.assertEqual(before,after)

    def test_explicit_import_and_input_invalidation(self):
        self.panel._run();self.wait_done();self.assertIsNotNone(self.panel.result_snapshot())
        before=self.panel.editor.toPlainText()
        self.panel.set_scenario({'operator':'kaltsit','skill':2,'level':90})
        self.assertEqual(before,self.panel.editor.toPlainText())
        self.panel.import_scenario.click()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['scenario']['operator'],'kaltsit')
        self.assertIsNone(self.panel.result_snapshot())
        self.assertEqual(self.panel.raw_result.toPlainText(),'')
        self.panel.set_stage('ro6_n_1_2');self.panel.select_query('battle','compare')
        payload=json.loads(self.panel.editor.toPlainText());payload['right_stage']='ro6_n_1_2'
        self.panel.editor.setPlainText(json.dumps(payload));self.panel.import_stage.click()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['right_stage'],payload['right_stage'])

    def test_pair_import_does_not_relabel_existing_observations(self):
        self.panel.select_query('calibration','pair')
        before=json.loads(self.panel.editor.toPlainText())['observation']
        self.panel.set_scenario({'operator':'kaltsit','skill':2});self.panel.import_scenario.click()
        after=json.loads(self.panel.editor.toPlainText())
        self.assertEqual(before,after['observation'])
        self.panel._run();self.wait_done();self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('条件不一致',self.panel.status.text())

    def test_query_buffers_invalid_json_and_unsupported_context(self):
        self.panel.editor.setPlainText('{ broken');self.panel._run()
        self.assertIn('JSON 格式不正确',self.panel.status.text())
        self.assertTrue(self.panel.run_button.isEnabled())
        self.panel.select_query('battle','actions')
        self.panel.select_query('calibration','panel')
        self.assertEqual(self.panel.editor.toPlainText(),'{ broken')
        self.panel._load_example();before=self.panel.editor.toPlainText()
        self.panel.set_scenario({'operator':'not-first-three','skill':1})
        self.panel.import_scenario.click()
        self.assertEqual(before,self.panel.editor.toPlainText())
        self.assertIn('仅支持',self.panel.status.text())

    def test_empty_worksheets_and_technical_details(self):
        self.panel.select_query('calibration','worksheets');self.panel.editor.clear()
        self.panel._run();self.wait_done()
        self.assertEqual(self.panel.result_snapshot()['case_count'],10)
        self.assertFalse(self.panel.technical.isChecked())
        self.panel.technical.setChecked(True)
        self.assertFalse(self.panel.raw_result.isHidden())
        self.assertIn('case_count',self.panel.raw_result.toPlainText())

    def test_stale_worker_cannot_overwrite_changed_input(self):
        old=self.panel._serial
        result=run_offline_query('calibration','panel',public_payload('calibration','panel'))
        self.panel.editor.appendPlainText(' ')
        self.panel._finished(old,'calibration','panel',result,'')
        self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('旧结果已失效',self.panel.status.text())


if __name__=='__main__':unittest.main()
