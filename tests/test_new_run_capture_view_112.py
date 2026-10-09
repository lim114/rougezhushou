"""Real MainWindow reset lifecycle, using public temporary observation inputs.

Native game-window enumeration alone is isolated. The original calculator,
RunState, AccountCache, backend and Qt widgets remain real. No OCR, actual game
frame, chat/network or private account/run file is used by this fixture.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.run_state import RunState


class NewRunCaptureView112Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        temporary=tempfile.TemporaryDirectory(prefix='public-new-run-112-')
        self.addCleanup(temporary.cleanup);self.directory=Path(temporary.name)
        for key,name in (('RUN_STATE','run.json'),('OPERATOR_STATE','account.json'),('SETTINGS','settings.json')):
            replacement=patch.object(module,key,self.directory/name)
            replacement.start();self.addCleanup(replacement.stop)
        replacement=patch.object(module,'list_game_windows',return_value=[])
        replacement.start();self.addCleanup(replacement.stop)
        original_backend=module.DesktopBackend
        replacement=patch.object(module,'DesktopBackend',
            lambda _path,callback:original_backend(self.directory/'chat',callback))
        replacement.start();self.addCleanup(replacement.stop)
        self.window=module.MainWindow();self.addCleanup(self.window.close)
        self.image=np.full((24,36,3),65,dtype=np.uint8)
        self.image[:,::2,1]=120
        self.assertFalse(self.window.auto.isChecked())

    def stamp(self):
        return max(time.time(),self.window.run.state['started_at']+.001,self.window.last_sample_at+.001)

    def sample(self,observation):
        before=deepcopy(observation);self.window.sample_received((self.image,observation));self.qt.processEvents()
        self.assertEqual(observation,before)

    def current_run_observation(self,level=20,gold=10):
        return {'page':'crew','nodes':[],'captured_at':self.stamp(),'run':{
            'operators':[{'id':'mechanist','scope':'run','fields':{
                'elite':1,'level':level,'module_id':None,'module_level':0},
                'skill_ranks':{'1':7,'2':7},'recruitment_kind':'non_emergency',
                'char_buff_ids':[],'char_buffs_complete':True}],
            'selected_operator':'mechanist','crew_count':1,
            'relics':{'ids':[],'icons':[],'count':0,'source':'public112-empty-held-bar'},
            'resources':{'gold':{'value':gold,'source':'public112-confirmed-counter'},
                         'parts_count':{'value':1,'source':'public112-confirmed-counter'}}}}

    def seed_reading(self):
        account={'id':'mechanist','scope':'account','fields':{'elite':2,'level':90,
            'trust':100,'potential':1,'module_id':None,'module_level':0},
            'skill_ranks':{'1':10,'2':10,'3':10}}
        self.window.apply_operator_observation(account,self.stamp())
        self.assertEqual(self.window.account_cache.records['mechanist']['fields'],account['fields'])
        self.assertEqual(self.window.account_cache.records['mechanist']['skill_ranks'],account['skill_ranks'])
        self.assertTrue((self.directory/'account.json').is_file())
        identity='ro6_n_1_2';stage=module.catalog()['stages'][identity]
        self.sample({'page':'node_detail','nodes':[],'captured_at':self.stamp(),
            'stage':{'id':identity,'visible_variant_id':identity,'name':stage['name']}})
        observed=self.current_run_observation();self.sample(observed)
        self.assertEqual(self.window.capture_operator_picture.key[:2],('operator','mechanist'))
        self.assertTrue(self.window.operator_summary.toPlainText())
        self.assertFalse(self.window.preview.pixmap().isNull())
        self.assertEqual(json.loads(self.window.observed_text.toPlainText())['page'],'crew')
        self.assertIn('最近节点详情',self.window.target_stage.toolTip())
        self.assertIn('源石锭 10',self.window.run_summary.text())
        return observed

    def cleared_reading(self):
        self.assertIsNone(self.window.observation)
        self.assertEqual(self.window.capture_operator_picture.key,(None,None,''))
        self.assertFalse(self.window.capture_operator_picture.caption.text())
        self.assertTrue(self.window.capture_operator_picture.image.pixmap().isNull())
        self.assertEqual(self.window.operator_summary.toPlainText(),
            '本局已重置，等待新的干员页面读取；账号档案仍保留。')
        self.assertTrue(self.window.preview.pixmap().isNull())
        self.assertEqual(self.window.preview.text(),'本局尚未采样')
        self.assertEqual(self.window.observed_text.toPlainText(),'')
        self.assertEqual(self.window.capture_status.text(),'已开始新局，等待新的页面采样；账号档案已保留。')
        self.assertNotIn('最近节点详情',self.window.target_stage.toolTip())
        self.assertIn('待识别0帧',self.window.sampling_status.text())

    def test_new_run_clears_current_snapshot_and_preserves_real_account_file(self):
        self.seed_reading();old_identity=self.window.run.state['id']
        account_before=deepcopy(self.window.account_cache.records)
        account_bytes=(self.directory/'account.json').read_bytes()
        self.window.reset_run();self.qt.processEvents();self.cleared_reading()
        self.assertNotEqual(self.window.run.state['id'],old_identity)
        self.assertEqual(self.window.run.state['resources'],{})
        self.assertNotIn('源石锭 10',self.window.run_summary.text())
        self.assertEqual(self.window.account_cache.records,account_before)
        self.assertEqual((self.directory/'account.json').read_bytes(),account_bytes)
        loaded=RunState(self.directory/'run.json')
        self.assertEqual(loaded.state['id'],self.window.run.state['id'])
        self.assertEqual(loaded.state['operators'],{})
        self.assertEqual(loaded.state['resources'],{})

    def test_old_epoch_and_pre_reset_frame_cannot_repopulate_cleared_view(self):
        observed=self.seed_reading();old_epoch=self.window.sample_epoch
        observed['_sampling']={'epoch':old_epoch,'generation':self.window.capture.stats()['generation']}
        self.window.reset_run();before=deepcopy(self.window.run.state)
        self.sample(observed);self.cleared_reading();self.assertEqual(self.window.run.state,before)
        stale=deepcopy(observed);stale.pop('_sampling')
        stale['captured_at']=self.window.run.state['started_at']-1
        self.sample(stale);self.cleared_reading();self.assertEqual(self.window.run.state,before)

    def test_new_valid_sample_fills_only_new_run_reading_after_reset(self):
        self.seed_reading();account_bytes=(self.directory/'account.json').read_bytes()
        self.window.reset_run();identity=self.window.run.state['id']
        observed=self.current_run_observation(level=30,gold=2)
        observed['_sampling']={'epoch':self.window.sample_epoch,'generation':self.window.capture.stats()['generation']}
        self.sample(observed)
        self.assertEqual(self.window.run.state['id'],identity)
        self.assertEqual(self.window.run.state['operators']['mechanist']['fields']['level'],30)
        self.assertEqual(self.window.run.state['resources']['gold']['value'],2)
        self.assertEqual(self.window.capture_operator_picture.key[:2],('operator','mechanist'))
        self.assertFalse(self.window.preview.pixmap().isNull())
        self.assertEqual(json.loads(self.window.observed_text.toPlainText())['run']['resources']['gold']['value'],2)
        self.assertIn('crew',self.window.capture_status.text())
        self.assertNotIn('等待新的页面采样',self.window.capture_status.text())
        self.assertEqual((self.directory/'account.json').read_bytes(),account_bytes)

    def test_reset_before_first_sample_and_repeated_reset_remain_usable(self):
        self.window.reset_run();self.qt.processEvents();self.cleared_reading()
        first=self.window.run.state['id']
        self.window.reset_run();self.qt.processEvents();self.cleared_reading()
        self.assertNotEqual(self.window.run.state['id'],first)
        self.assertEqual(self.window.account_cache.records,{})
        self.assertFalse((self.directory/'account.json').exists())
        self.sample(self.current_run_observation(level=40,gold=3))
        self.assertEqual(self.window.run.state['resources']['gold']['value'],3)


if __name__=='__main__':unittest.main()
