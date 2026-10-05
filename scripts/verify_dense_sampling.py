"""Replay brief saved pages through the production buffer, reader, and state seams.

This is a stitched replay of development screenshots, not a fresh capture of one
live exploration. It never opens, clicks, or changes the game. All mutable app
state and the dormant desktop bridge are redirected into a temporary directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import queue
import sys
import tempfile
import threading
import time
from pathlib import Path

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from PySide6.QtWidgets import QApplication

import rouge.app as app_module
from rouge.app import MainWindow
from rouge.frame_buffer import FrameBuffer


FILES = [
    ('map', 'exploration-map.png'),
    ('account_detail', 'operator-mechanist.png'),
    ('module', 'module-mechanist.png'),
    ('run_roster', 'run-mechanist-selected.png'),
    ('relic_open', 'run-relic-multicard.png'),
    ('relic_closed', 'run-relic-multicard-closed.png'),
]


class ReplayWindow(MainWindow):
    def refresh_windows(self):
        # Only capture discovery is bypassed. Recognition and both state merge
        # paths are the same public methods used by the normal application.
        self.windows.clear()


def summarize(observation):
    result = {'page': observation['page']}
    operator = observation.get('operator')
    if operator:
        result['operator'] = {key: operator.get(key) for key in
                              ('id', 'fields', 'skill_ranks', 'missing_fields')}
    run = observation.get('run')
    if run:
        result['run'] = {
            'operators': [{key: member.get(key) for key in ('id', 'fields', 'skill_ranks')}
                          for member in run.get('operators', [])],
            'relic_ids': run.get('relics', {}).get('ids', []),
            'relic_count': run.get('relics', {}).get('count'),
            'tool_ids': run.get('tactical_tools', {}).get('ids', []),
        }
    graph = observation.get('map')
    if graph:
        result['map'] = {key: graph.get(key) for key in
                         ('status', 'zone_id', 'template_id', 'current_node')}
    return result


def verify():
    source_paths = [ROOT / 'rouge/frame_buffer.py', ROOT / 'rouge/recognition.py',
                    ROOT / 'rouge/run_state.py', ROOT / 'rouge/app.py', Path(__file__)]
    source_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in source_paths}
    frame_interval = .1
    frames_per_page = 3
    page_seconds = frame_interval * frames_per_page
    samples = []
    for label, filename in FILES:
        path = ROOT / 'samples/native-client' / filename
        payload = path.read_bytes()
        image = cv2.imdecode(np.frombuffer(payload, np.uint8), cv2.IMREAD_COLOR)
        assert image is not None, path
        samples.append({'label': label, 'path': str(path), 'image': image,
                        'size': [image.shape[1], image.shape[0]],
                        'file_sha256': hashlib.sha256(payload).hexdigest()})

    # Initial image arrays remain shared by the producer; no per-tick full-size
    # copies are made outside the bounded production buffer.
    frames = FrameBuffer(max_bytes=96 * 1024 * 1024, max_frames=16, settle_seconds=.12)
    supplied = []
    taken = []
    outputs = queue.Queue()
    producer_done = threading.Event()
    worker_done = threading.Event()
    cancelled = threading.Event()
    app = QApplication.instance() or QApplication([])
    started = time.perf_counter()
    emitted_at = None
    with tempfile.TemporaryDirectory(prefix='rouge-dense-replay-') as directory:
        directory = Path(directory)
        app_module.OPERATOR_STATE = directory / 'operator-state.json'
        app_module.RUN_STATE = directory / 'run-state.json'
        app_module.SETTINGS = directory / 'settings.json'
        backend_type = app_module.DesktopBackend
        app_module.DesktopBackend = lambda _path, on_state: backend_type(directory / 'desktop', on_state)
        window = ReplayWindow()
        reader = window.reader

        def producer():
            nonlocal emitted_at
            try:
                begin = time.perf_counter()
                for index, sample in enumerate(samples):
                    for tick in range(frames_per_page):
                        due = begin + (index * frames_per_page + tick) * frame_interval
                        if cancelled.wait(max(0, due - time.perf_counter())):
                            return
                        captured_at = time.time()
                        seq = frames.offer(sample['image'], captured_at,
                                           target={'replay_page': sample['label']})
                        supplied.append({'label': sample['label'], 'seq': seq,
                                         'captured_at': captured_at,
                                         'offset_seconds': time.perf_counter() - begin,
                                         'buffer': frames.stats()})
                # The user has left every test page by this point. Subsequent
                # recognition must work from candidates already retained.
                cancelled.wait(max(0, begin + len(samples) * page_seconds - time.perf_counter()))
                emitted_at = time.time()
                # An unrelated neutral screen is the next page; no test page
                # is supplied again while their queued information is read.
                neutral = np.full((480, 640, 3), 16, np.uint8)
                seq = frames.offer(neutral, emitted_at, target={'replay_page': 'neutral_end'})
                supplied.append({'label': 'neutral_end', 'seq': seq, 'captured_at': emitted_at,
                                 'offset_seconds': time.perf_counter() - begin,
                                 'buffer': frames.stats(),
                                 'source': 'generated neutral frame, not a game screenshot'})
            except BaseException as error:
                outputs.put(('error', repr(error)))
            finally:
                producer_done.set()

        def worker():
            try:
                while not cancelled.is_set():
                    if producer_done.is_set() and frames.stats()['pending'] == 0:
                        break
                    frame = frames.take(force=producer_done.is_set())
                    if frame is None:
                        if producer_done.is_set():
                            break
                        cancelled.wait(.015)
                        continue
                    wall_start = time.time()
                    mark = time.perf_counter()
                    observed = reader.read(frame['image'], client_rect=frame.get('client_rect'))
                    recognition_seconds = time.perf_counter() - mark
                    # Deliberately keep this single consumer slower than pages
                    # switch, even when exact-result caching is unusually fast.
                    cancelled.wait(max(0, 1.0 - (time.perf_counter() - mark)))
                    record = {'seq': frame['seq'], 'generation': frame['generation'],
                              'label': frame.get('target', {}).get('replay_page'),
                              'captured_at': frame['captured_at'], 'read_started_at': wall_start,
                              'read_finished_at': time.time(), 'recognition_seconds': recognition_seconds,
                              'worker_seconds': time.perf_counter() - mark,
                              'observation': summarize(observed)}
                    outputs.put(('observation', (frame, observed, record)))
            except BaseException as error:
                outputs.put(('error', repr(error)))
            finally:
                worker_done.set()

        producer_thread = threading.Thread(target=producer, name='replay-10hz-producer', daemon=True)
        worker_thread = threading.Thread(target=worker, name='replay-single-reader', daemon=True)
        try:
            producer_thread.start()
            worker_thread.start()
            while not worker_done.is_set() or not outputs.empty():
                try:
                    kind, value = outputs.get(timeout=.05)
                except queue.Empty:
                    app.processEvents()
                    continue
                if kind == 'error':
                    raise AssertionError(value)
                frame, observed, record = value
                if observed.get('run'):
                    record['run_applied'] = window.apply_run_observation(observed['run'], frame['captured_at'])
                if observed.get('operator'):
                    window.apply_operator_observation(observed['operator'], frame['captured_at'])
                    record['account_applied'] = True
                taken.append(record)
                print(json.dumps({'processed': record['label'], 'page': observed['page'],
                                  'recognition_seconds': round(record['recognition_seconds'], 3)},
                                 ensure_ascii=False), flush=True)
                app.processEvents()
            producer_thread.join(timeout=2)
            worker_thread.join(timeout=2)
            assert not producer_thread.is_alive() and not worker_thread.is_alive()
            assert [record['seq'] for record in taken] == sorted(record['seq'] for record in taken)
            seen = {record['label'] for record in taken}
            assert seen == {label for label, _ in FILES} | {'neutral_end'}, (seen, frames.stats())
            assert any(record['read_finished_at'] > emitted_at for record in taken)
            assert all(item['buffer']['bytes'] <= frames.max_bytes and
                       item['buffer']['retained_frames'] <= frames.max_frames for item in supplied)
            account = window.operator_observations['mechanist']
            assert account['fields']['elite'] == 2 and account['fields']['level'] == 90
            assert account['fields']['potential'] == 6 and account['fields']['trust_display'] == 113
            assert account['fields']['module_id'] == 'uniequip_002_mcnist'
            assert account['fields']['module_level'] == 3
            assert {str(k): v for k, v in account['skill_ranks'].items()} == {'1': 10, '2': 9, '3': 10}
            member = window.run.state['operators']['mechanist']
            assert member['fields']['elite'] == 1 and member['fields']['level'] == 80
            assert member['skill_ranks'] == {'1': 7, '2': 7}
            assert set(window.run.held_relic_ids()) == {'rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26'}
            assert window.run.held_tool_ids() == ['rogue_6_active_tool_5']
            assert window.run.state['relic_count'] == 3 and window.run.state['inventory_verified']
            assert window.run.state['maps']['zone_1']['template_id'] == '1b'
            receipt = {
                'passed': True, 'mode': 'saved_development_screenshot_replay',
                'not_new_live_game_capture': True, 'screenshots_from_different_recorded_runs': True,
                'ui_state_isolated': True, 'game_input_actions': 0, 'desktop_chat_requests': 0,
                'samples': [{key: value for key, value in sample.items() if key != 'image'} for sample in samples],
                'requested_capture_hz': 1 / frame_interval, 'frames_per_page': frames_per_page,
                'nominal_page_dwell_seconds': page_seconds, 'single_reader': True,
                'minimum_worker_seconds': 1.0, 'all_pages_left_at': emitted_at,
                'supplied_frames': supplied, 'recognized_candidates': taken, 'buffer_final_stats': frames.stats(),
                'buffer_peak_recorded_bytes': max(item['buffer']['bytes'] for item in supplied),
                'buffer_peak_recorded_pending': max(item['buffer']['pending'] for item in supplied),
                'total_seconds': time.perf_counter() - started,
                'merged': {'account_mechanist': {key: account[key] for key in ('fields', 'skill_ranks')},
                           'run_mechanist': {key: member[key] for key in ('fields', 'skill_ranks')},
                           'relic_ids': window.run.held_relic_ids(), 'tool_ids': window.run.held_tool_ids(),
                           'inventory_count': window.run.state['relic_count'],
                           'map_template': window.run.state['maps']['zone_1']['template_id']},
                'limits': ['This controlled replay is not independent field accuracy validation.',
                           '10 Hz acquisition does not mean 10 Hz full recognition.',
                           'Only visible, readable samples can yield information; hidden or sub-frame pages are not guaranteed.'],
                'source_sha256': source_hashes,
                'source_unchanged_during_verification': all(
                    hashlib.sha256(path.read_bytes()).hexdigest() == source_hashes[str(path.relative_to(ROOT))]
                    for path in source_paths),
            }
            destination = ROOT / 'DENSE_SAMPLING_REPLAY_VERIFICATION.json'
            destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'passed': True, 'receipt': str(destination),
                              'offered': len(supplied), 'recognized': len(taken)}, ensure_ascii=False))
        finally:
            cancelled.set()
            producer_thread.join(timeout=2)
            worker_thread.join(timeout=2)
            window.close()
            app.processEvents()


if __name__ == '__main__':
    verify()
