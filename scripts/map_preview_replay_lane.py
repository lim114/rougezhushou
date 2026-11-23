"""Run the map preview alongside the normal reader in an isolated Windows replay.

Construct ReplayMapLane after connecting the fixture to its isolated-replay
source window. Pass the fixture's TemporaryDirectory and close the lane before
closing the fixture. Ordinary desktop startup does not install this experiment.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import copy, deepcopy
from pathlib import Path
from tempfile import gettempdir
import time

import cv2
import numpy as np
from PySide6.QtCore import QTimer

from rouge.recognition_cache import CachedOCR
from rouge.run_config import confirmed_config
from rouge.viewport import map_evidence, prepare_frame
from scripts.probe_map_glyph_preview import preview


def _read(frame, reader, context):
    start = time.perf_counter()
    image, viewport = prepare_frame(frame['image'], frame['client_rect'])
    evidence = preview(image, reader, confirmed_config(context))
    if evidence is None:
        return None
    observation = deepcopy(dict(evidence, page='exploration', size=viewport['source_size'],
                                stage=None, run=None, operator=None, node_content=None, limitations=[]))
    map_evidence(observation, viewport)
    observation['viewport'] = viewport
    elapsed = (time.perf_counter() - start) * 1000
    observation['performance'] = {'stages_ms': {'glyph_map': elapsed}, 'total_ms': elapsed}
    return observation


class ReplayMapLane:
    def __init__(self, window, temporary_directory):
        state_dir = Path(temporary_directory.name).resolve()
        temp = Path(gettempdir()).resolve()
        if (state_dir == temp or not state_dir.is_relative_to(temp)
                or Path(window.run.file).resolve().parent != state_dir
                or (window.capture.target or {}).get('executable') != 'isolated-replay'):
            raise ValueError('地图实验需要临时本局目录和独立录像源窗口。')
        self.window = window
        self.source = dict(window.capture.target)
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='replay-map-preview')
        self.job = self.reader = self.frame = self.marker = None
        self.read_seq = self.checked_seq = self.thumb = None
        self.until = self.rearm = 0.
        self.dispatch = window.sample_now
        self.settle = window.prepare_settling_page
        window.sample_now = self.sample_now
        window.prepare_settling_page = self.prepare_settling
        self.timer = QTimer(window)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.poll)
        self.timer.start()

    def active(self):
        w = self.window
        popup = w.compact_window.map_popup
        return (not w.closing and w.auto.isChecked() and popup and popup.panel.isVisible()
                and w.capture.target == self.source)

    def defer(self):
        if self.reader is None or not self.active():
            return False
        now = time.perf_counter()
        frame = self.window.capture.buffer.latest(after_seq=self.checked_seq)
        if frame is not None:
            self.checked_seq = frame['seq']
            thumb = frame['image'][::24, ::24].copy()
            if (self.thumb is not None and now >= self.rearm
                    and (self.thumb.shape != thumb.shape or np.mean(cv2.absdiff(thumb, self.thumb)) > 18)):
                self.until = now + .75
                self.rearm = self.until + .5
            self.thumb = thumb
        return now < self.until

    def sample_now(self, *args, **options):
        if options.get('automatic') and self.defer():
            if not self.window.ready_timer.isActive():
                self.window.ready_timer.start(25)
            return
        return self.dispatch(*args, **options)

    def prepare_settling(self):
        if not self.defer():
            self.settle()

    def poll(self):
        w = self.window
        if not self.active():
            return
        if self.job is not None:
            if not self.job.done():
                return
            observation = self.job.result()
            self.job = None
            marker = (w.sample_epoch, w.capture.stats()['generation'], w.run.state['id'])
            if observation and self.marker == marker and self.frame['seq'] > w.last_sample_seq:
                frame = self.frame
                observation.update(captured_at=frame['captured_at'], _sampling={
                    'epoch': marker[0], 'generation': marker[1], 'seq': frame['seq'],
                    'phase': 'map', 'job_id': -1, 'age_at_read_ms': self.age_ms})
                observation['_overlay_frame'] = dict(frame, run_id=marker[2])
                w.events.sample.emit((frame['image'], observation))
                self.until = 0.
        if self.reader is None:
            provider = w.reader._engine
            if provider is None:
                return
            provider = provider.engine if isinstance(provider, CachedOCR) else provider
            self.reader = copy(provider)
            self.reader.text_rec = copy(provider.text_rec)
        if not self.defer():
            return
        frame = w.capture.buffer.latest(after_seq=self.read_seq)
        if frame is None:
            return
        self.frame = frame
        self.read_seq = frame['seq']
        self.age_ms = (time.time() - frame['captured_at']) * 1000
        run_id = w.run.state['id']
        self.marker = (w.sample_epoch, frame['generation'], run_id)
        self.job = self.worker.submit(_read, frame, self.reader,
                                      {'run_id': run_id, 'config': deepcopy(w.run.state['config'])})

    def close(self):
        self.timer.stop()
        self.window.sample_now = self.dispatch
        self.window.prepare_settling_page = self.settle
        self.worker.shutdown(cancel_futures=True)
