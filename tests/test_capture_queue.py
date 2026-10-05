"""Window capture boundary: native callbacks keep feeding a slow consumer."""
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock
import numpy as np
from rouge.capture import GameCapture


class FakeWGC:
    instances=[]
    def __init__(self,**kwargs):
        self.options=kwargs;self.events={};self.control=Mock()
        self.instances.append(self)
    def event(self,callback):self.events[callback.__name__]=callback
    def start_free_threaded(self):return self.control
    def push(self,value):
        pixels=np.full((60,80,4),value,dtype=np.uint8)
        self.events['on_frame_arrived'](SimpleNamespace(frame_buffer=pixels),self.control)
        pixels.fill(0)  # Native mapped storage is gone after callback return.


class CaptureQueueTests(unittest.TestCase):
    def setUp(self):
        FakeWGC.instances.clear()
        self.target={'hwnd':12,'pid':123,'title':'Arknights'}
        for p in (patch('rouge.capture.list_game_windows',return_value=[self.target]),
                  patch('windows_capture.WindowsCapture',FakeWGC),
                  patch('rouge.capture.frame_client_rect',return_value=[0,0,80,60]),
                  patch('rouge.capture.win32gui.IsWindow',return_value=True),
                  patch('rouge.capture.win32gui.IsIconic',return_value=False)):
            p.start();self.addCleanup(p.stop)
        self.capture=GameCapture();self.capture.connect(self.target)
        self.addCleanup(self.capture.close)

    def test_capture_retains_short_pages_while_consumer_is_busy(self):
        native=FakeWGC.instances[-1]
        self.assertEqual(native.options['minimum_update_interval'],100)
        self.assertEqual(native.options['window_hwnd'],12)
        for value in [40,100,200]:native.push(value)
        self.assertEqual([self.capture.next_frame(force=True)['image'][0,0,0]
                          for _ in range(3)],[40,100,200])

    def test_previous_session_callback_cannot_pollute_reconnected_window(self):
        old=FakeWGC.instances[-1];old.push(40)
        generation=self.capture.stats()['generation']
        self.capture.connect(self.target)
        old.push(100);old.events['on_closed']()
        self.assertFalse(self.capture.closed)
        self.assertEqual(self.capture.stats()['pending'],0)
        self.assertGreater(self.capture.stats()['generation'],generation)
        old.control.stop.assert_called_once()
        FakeWGC.instances[-1].push(200)
        self.assertEqual(self.capture.next_frame(force=True)['image'][0,0,0],200)

    def test_pause_stops_accumulating_and_resume_needs_new_evidence(self):
        native=FakeWGC.instances[-1];native.push(40)
        self.capture.set_collecting(False);native.push(100)
        self.assertEqual(self.capture.stats()['pending'],0)
        self.capture.set_collecting(True);native.push(200)
        self.assertEqual(self.capture.next_frame(force=True)['image'][0,0,0],200)

    def test_minimized_window_does_not_discard_previously_captured_page(self):
        FakeWGC.instances[-1].push(100)
        with patch('rouge.capture.win32gui.IsIconic',return_value=True):
            self.assertEqual(self.capture.next_frame(force=True)['image'][0,0,0],100)
            with self.assertRaisesRegex(RuntimeError,'最小化'):
                self.capture.next_frame()


if __name__=='__main__':unittest.main()
