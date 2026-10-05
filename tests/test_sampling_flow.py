"""Public UI sampling flow, with only native/recognizer boundaries substituted."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import numpy as np
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.app import MainWindow


class SamplingFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        for name,file in [('SETTINGS','settings.json'),('RUN_STATE','run.json'),('OPERATOR_STATE','operators.json')]:
            p=patch.object(module,name,Path(self.tmp.name)/file);p.start();self.addCleanup(p.stop)
        for p in (patch.object(module,'list_game_windows',return_value=[]),
                  patch.object(module,'DesktopBackend',return_value=Mock()),
                  patch('rouge.capture.win32gui.IsWindow',return_value=True),
                  patch('rouge.capture.win32gui.IsIconic',return_value=False)):
            p.start();self.addCleanup(p.stop)
        self.window=MainWindow()
        self.window.capture.target={'hwnd':1,'pid':1}
        self.addCleanup(self.window.close)
        self.seen=[];self.entered=threading.Event();self.release=threading.Event()
        self.addCleanup(self.release.set)
        def read(image,**kwargs):
            level=int(image[0,0,0]);self.seen.append(level)
            if len(self.seen)==1:
                self.entered.set();self.release.wait(5)
            return {'page':'operator','nodes':[],
                    'operator':{'id':'kaltsit','fields':{'level':level},'scope':'account'}}
        self.window.reader=Mock(read=read)

    def offer(self,level):
        image=np.full((120,180,3),level*2,dtype=np.uint8)
        image[::3,:,1]=200-level
        image[0,0,0]=level
        return self.window.capture.buffer.offer(image,time.time())

    def wait_for(self,predicate,timeout=5):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            self.qt.processEvents()
            if predicate():return
            time.sleep(.01)
        self.fail('Timed out waiting for queued sampling')

    def test_short_pages_are_drained_after_busy_reader_without_revisiting(self):
        self.offer(20)
        self.window.auto.setChecked(True)
        self.wait_for(self.entered.is_set)
        self.offer(50);self.offer(80)
        self.release.set()
        self.wait_for(lambda:len(self.seen)==3 and not self.window.busy)
        self.assertEqual(self.seen,[20,50,80])
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)
        self.assertEqual(self.window.capture.stats()['pending'],0)

    def test_reset_discards_queued_and_inflight_results(self):
        self.offer(20);self.window.auto.setChecked(True)
        self.wait_for(self.entered.is_set)
        self.offer(50);self.window.reset_run();self.release.set()
        self.wait_for(lambda:not self.window.busy)
        self.assertFalse(self.window.operator_observations)
        self.assertIsNone(self.window.observation)
        self.assertEqual(self.window.capture.stats()['pending'],0)
        self.offer(80)
        self.wait_for(lambda:bool(self.window.operator_observations))
        self.assertEqual(self.seen,[20,80])

    def test_pause_discards_late_result_and_resume_reads_new_frames(self):
        self.offer(20);self.window.auto.setChecked(True)
        self.wait_for(self.entered.is_set)
        self.window.auto.setChecked(False);self.release.set()
        self.wait_for(lambda:not self.window.busy)
        self.assertFalse(self.window.operator_observations)
        self.window.auto.setChecked(True);self.offer(80)
        self.wait_for(lambda:bool(self.window.operator_observations))
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)

    def test_late_observation_cannot_replace_newer_fields(self):
        stamp=time.time();image=np.full((20,20,3),50,dtype=np.uint8)
        def obs(level,at):return {'page':'operator','nodes':[],'captured_at':at,
            'operator':{'id':'kaltsit','fields':{'level':level},'scope':'account'}}
        self.window.sample_received((image,obs(80,stamp)))
        self.window.sample_received((image,obs(20,stamp-1)))
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)
        self.assertEqual(self.window.observation['captured_at'],stamp)

    def test_changing_recognition_mode_rechecks_same_static_page(self):
        self.release.set();self.window.visual_reader=self.window.reader
        self.window.recognition_mode.setCurrentIndex(1)
        self.offer(50);self.window.auto.setChecked(True)
        self.wait_for(lambda:not self.window.busy and len(self.seen)==1)
        self.window.recognition_mode.setCurrentIndex(0)
        self.offer(50)
        self.wait_for(lambda:not self.window.busy and len(self.seen)==2)

    def test_manual_failure_keeps_automatic_capture_paused(self):
        self.window.capture.set_collecting(False)
        with patch('rouge.capture.win32gui.IsIconic',return_value=True):
            self.window.sample_now()
        self.assertFalse(self.window.auto.isChecked())
        self.assertFalse(self.window.capture.stats()['collecting'])

    def test_transient_reader_failure_retries_saved_page_without_reopening(self):
        self.release.set();original=self.window.reader.read;attempts=[]
        def unreliable(image,**kwargs):
            attempts.append(1)
            if len(attempts)==1:raise RuntimeError('temporary recognition failure')
            return original(image,**kwargs)
        self.window.reader.read=unreliable
        self.offer(50);self.window.auto.setChecked(True)
        self.wait_for(lambda:bool(self.window.operator_observations))
        self.assertEqual(len(attempts),2)
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],50)

    def test_manual_wait_for_first_frame_keeps_fifo_when_auto_resumes(self):
        self.window.sample_now()
        self.assertTrue(self.window.busy)
        self.offer(20);self.offer(80)
        self.window.auto.setChecked(True)
        self.wait_for(self.entered.is_set);self.release.set()
        self.wait_for(lambda:len(self.seen)==2 and not self.window.busy)
        self.assertEqual(self.seen,[20,80])

    def test_late_run_settings_cannot_overwrite_newer_evidence(self):
        at=time.time()
        self.assertTrue(self.window.run.apply({'config':{'difficulty':{'value':10,'source':'test'}}},at+2))
        history=list(self.window.run.state['history'])
        self.assertFalse(self.window.run.apply({'config':{'difficulty':{'value':3,'source':'old'}}},at+1))
        self.assertEqual(self.window.run.state['config']['difficulty']['value'],10)
        self.assertEqual(self.window.run.state['history'],history)


if __name__=='__main__':unittest.main()
