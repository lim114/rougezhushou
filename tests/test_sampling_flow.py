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


class StubReader:
    def __init__(self, read):self.read = read
    def fork(self):return StubReader(self.read)


class SamplingFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root_patch=patch.object(module,'ROOT',Path(self.tmp.name));root_patch.start();self.addCleanup(root_patch.stop)
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
        self.window.reader=StubReader(read)
        self.window.secondary_reader=StubReader(read)

    def offer(self,level,at=None):
        image=np.full((120,180,3),level*2,dtype=np.uint8)
        image[::3,:,1]=200-level
        image[0,0,0]=level
        return self.window.capture.buffer.offer(image,time.time()if at is None else at)

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
        self.assertEqual(self.seen,[20,80,50])
        self.assertEqual(self.window.observation['operator']['fields']['level'],80)
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)
        self.assertEqual(self.window.capture.stats()['pending'],0)

    def test_current_page_commits_before_old_read_finishes_and_history_is_retained(self):
        from copy import deepcopy
        from rouge.observation_timeline import memory_model
        window = self.window
        at = time.time()
        rows = {
            20: {'page': 'operator', 'nodes': [], 'captured_at': at,
                 'run': {'resources': {'gold': {'value': 2}}},
                 'operator': {'id': 'kaltsit', 'scope': 'account', 'fields': {'level': 20, 'potential': 3}}},
            80: {'page': 'operator', 'nodes': [], 'captured_at': at + 1,
                 'run': {'resources': {'gold': {'value': 9}}},
                 'operator': {'id': 'kaltsit', 'scope': 'account', 'fields': {'level': 80}}},
        }
        expected_run = memory_model(window.run, ('state',))
        expected_account = memory_model(window.account_cache, ('records', 'issues'))
        for row in rows.values():
            expected_run.apply(row['run'], row['captured_at'])
            expected_account.observe(row['operator'], row['captured_at'])
        def read(image, **kwargs):
            level = int(image[0, 0, 0])
            self.seen.append(level)
            if level == 20:
                self.entered.set();self.release.wait(8)
            return deepcopy(rows[level])
        window.reader.read = window.secondary_reader.read = read
        self.offer(20, at);window.auto.setChecked(True)
        self.wait_for(self.entered.is_set)
        self.offer(80, at + 1)
        try:
            self.wait_for(lambda: window.last_sample_seq == 2, timeout=2)
            self.assertTrue(window.busy)
            self.assertEqual(window.run.state['resources']['gold']['value'], 9)
            self.assertEqual(window.observation_timeline.committed_seq, 0)
        finally:
            self.release.set()
        self.wait_for(lambda: not window.busy)
        self.assertEqual(window.run.state, expected_run.state)
        self.assertEqual(window.account_cache.records, expected_account.records)
        self.assertEqual(window.observation['operator']['fields']['level'], 80)
        self.assertEqual(window.observation_timeline.committed_seq, 2)

    def test_map_updates_while_inventory_is_still_reading_then_replaces_same_frame(self):
        from copy import deepcopy
        from rouge.player_map_acceptance import fixtures
        from rouge.observation_timeline import memory_model
        graph = deepcopy(fixtures()[0][0]);graph['status'] = 'matched'
        at = time.time();window = self.window
        expected = memory_model(window.run, ('state',))
        config = {'difficulty': {'value': 5}}
        complete = {'page': 'exploration', 'nodes': [], 'map': graph,
                    'run': {'map': graph, 'config': config, 'resources': {'gold': {'value': 9}}}}
        expected.apply(complete['run'], at)
        window.show_compact();window.compact_window.open_map()
        def read(image, **options):
            options['on_map']({'page': 'exploration', 'nodes': [], 'map': deepcopy(graph),
                               'map_config': config, 'run': None, 'operator': None})
            options['on_hud']({'life': {'value': 8}})
            self.entered.set();self.release.wait(8)
            return deepcopy(complete)
        window.reader.read = read
        self.offer(20, at);window.sample_now()
        try:
            self.wait_for(lambda: bool(window.run.state['maps']), timeout=2)
            self.assertTrue(window.busy)
            self.assertEqual(window.compact_window.map_popup.panel.view.graph['template_id'], graph['template_id'])
            self.assertEqual(window.run.state['resources'], {})
            self.assertEqual(window.run.state['config']['difficulty']['value'], 5)
            self.assertEqual(window.sample_hud['life']['value'], 8)
            self.assertIsNone(window.run.state['inventory_confirmed_at'])
            self.assertEqual(window.observation_timeline.committed_seq, 0)
        finally:self.release.set()
        self.wait_for(lambda: not window.busy)
        self.assertEqual(window.run.state, expected.state)
        self.assertEqual(window.observation_timeline.committed_seq, 1)

    def test_failed_inventory_does_not_invent_resources_or_remove_confirmed_map(self):
        from copy import deepcopy
        from rouge.player_map_acceptance import fixtures
        graph=deepcopy(fixtures()[0][0]);graph['status']='matched'
        def read(image, **options):
            options['on_map']({'page':'exploration','nodes':[],'map':deepcopy(graph),'run':None,'operator':None})
            self.entered.set();self.release.wait(8)
            raise ValueError('inventory incomplete')
        window=self.window;window.reader.read=read
        self.offer(20)
        with patch.object(window,'show_error') as error:
            window.sample_now()
            try:
                self.wait_for(lambda:bool(window.run.state['maps']),timeout=2)
                self.assertTrue(window.busy)
            finally:self.release.set()
            self.wait_for(lambda:not window.busy)
        self.assertEqual(error.call_count,1)
        self.assertIn(graph['zone_id'],window.run.state['maps'])
        self.assertFalse(window.run.state['resources'])
        self.assertIsNone(window.run.state['inventory_confirmed_at'])

    def test_map_progress_arriving_after_reset_is_discarded_with_the_full_read(self):
        from copy import deepcopy
        from rouge.player_map_acceptance import fixtures
        graph=deepcopy(fixtures()[0][0]);graph['status']='matched'
        def read(image, **options):
            self.entered.set();self.release.wait(8)
            options['on_map']({'page':'exploration','nodes':[],'map':deepcopy(graph),'run':None,'operator':None})
            return {'page':'exploration','nodes':[],'map':graph,'run':{'map':graph}}
        window=self.window;window.reader.read=read
        self.offer(20);window.sample_now();self.wait_for(self.entered.is_set)
        window.reset_run();self.release.set();self.wait_for(lambda:not window.busy)
        self.assertFalse(window.run.state['maps'])
        self.assertIsNone(window.observation)

    def test_two_inflight_reads_bound_concurrency_and_reset_invalidates_both(self):
        second_entered = threading.Event()
        def read(image, **kwargs):
            level = int(image[0, 0, 0]);self.seen.append(level)
            (self.entered if level == 20 else second_entered).set()
            self.release.wait(8)
            return {'page': 'operator', 'nodes': [],
                    'operator': {'id': 'kaltsit', 'scope': 'account', 'fields': {'level': level}}}
        self.window.reader.read = self.window.secondary_reader.read = read
        self.offer(20);self.window.auto.setChecked(True)
        self.wait_for(self.entered.is_set);self.offer(50)
        try:
            self.wait_for(second_entered.is_set, timeout=2)
            self.offer(80)
            self.window.sample_now(automatic=True)
            self.assertEqual(self.seen, [20, 50])
            self.assertEqual(self.window.capture.stats()['pending'], 1)
            self.window.reset_run()
        finally:
            self.release.set()
        self.wait_for(lambda: not self.window.busy)
        self.assertFalse(self.window.operator_observations)
        self.assertIsNone(self.window.observation)

    def test_old_failure_does_not_finish_new_reader_or_replace_its_hud(self):
        window = self.window
        window.show_compact();window.compact_window.open_inventory()
        chip = window.compact_window.inventory_popup.resources.chips['life']
        current_entered = threading.Event();current_release = threading.Event()
        self.addCleanup(current_release.set)
        def old_read(image, *, on_hud, **kwargs):
            self.entered.set();self.release.wait(8)
            on_hud({'life': {'value': 2}})
            raise ValueError('older page failed')
        def new_read(image, *, on_hud, **kwargs):
            on_hud({'life': {'value': 8}});current_entered.set();current_release.wait(8)
            return {'page': 'operator', 'nodes': [], 'run': {'resources': {'life': {'value': 8}}}}
        window.reader.read = old_read;window.secondary_reader.read = new_read
        self.offer(20);window.auto.setChecked(True);self.wait_for(self.entered.is_set)
        self.offer(80)
        try:
            self.wait_for(current_entered.is_set, timeout=2)
            self.wait_for(lambda: chip.accessibleName() == '目标生命 8')
            with patch.object(window, 'show_error', wraps=window.show_error) as error:
                self.release.set()
                self.wait_for(lambda: error.call_count == 1)
                self.assertTrue(window.busy)
                self.assertFalse(window.sample_button.isEnabled())
                self.assertEqual(chip.accessibleName(), '目标生命 8')
        finally:
            self.release.set();current_release.set()
        self.wait_for(lambda: not window.busy)
        self.assertEqual(window.run.state['resources']['life']['value'], 8)

    def test_pause_and_mode_change_discard_both_inflight_results(self):
        second_entered = threading.Event()
        def read(image, **kwargs):
            level = int(image[0, 0, 0])
            (self.entered if level == 20 else second_entered).set();self.release.wait(8)
            return {'page': 'operator', 'nodes': [],
                    'operator': {'id': 'kaltsit', 'scope': 'account', 'fields': {'level': level}}}
        self.window.reader.read = self.window.secondary_reader.read = read
        self.offer(20);self.window.auto.setChecked(True);self.wait_for(self.entered.is_set)
        self.offer(50)
        try:
            self.wait_for(second_entered.is_set, timeout=2)
            self.window.auto.setChecked(False)
            self.window.change_recognition_mode()
        finally:self.release.set()
        self.wait_for(lambda: not self.window.busy)
        self.assertFalse(self.window.operator_observations)
        self.assertEqual(self.window.capture.stats()['pending'], 0)
        self.window.auto.setChecked(True);self.offer(80)
        self.wait_for(lambda: bool(self.window.operator_observations) and not self.window.busy)
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'], 80)

    def test_close_during_two_reads_returns_and_does_not_apply_late_results(self):
        second_entered = threading.Event();finished = []
        def read(image, **kwargs):
            level = int(image[0, 0, 0])
            (self.entered if level == 20 else second_entered).set();self.release.wait(8)
            finished.append(level)
            return {'page': 'operator', 'nodes': [],
                    'operator': {'id': 'kaltsit', 'scope': 'account', 'fields': {'level': level}}}
        self.window.reader.read = self.window.secondary_reader.read = read
        self.offer(20);self.window.auto.setChecked(True);self.wait_for(self.entered.is_set)
        self.offer(50)
        try:
            self.wait_for(second_entered.is_set, timeout=2)
            self.window.close()
            self.assertTrue(self.window.closing)
        finally:self.release.set()
        self.wait_for(lambda: len(finished) == 2)
        self.qt.processEvents()
        self.assertFalse(self.window.operator_observations)
        self.assertIsNone(self.window.observation)

    def test_current_hud_paints_while_worker_busy_and_failure_restores_committed_read(self):
        window = self.window
        window.show_compact()
        window.compact_window.open_inventory()
        chip = window.compact_window.inventory_popup.resources.chips['life']
        original = chip.accessibleName()
        before = dict(window.run.state['resources'])

        def read(image, *, on_hud, **options):
            on_hud({'life': {'value': 0, 'capacity': 8}})
            self.release.wait(8)
            raise ValueError('test incomplete observation')

        window.reader.read = read
        self.offer(20)
        with patch.object(window, 'show_error'):
            window.sample_now()
            try:
                self.wait_for(lambda: chip.accessibleName() == '目标生命 0/8')
                self.assertTrue(window.busy)
                self.assertEqual(window.run.state['resources'], before)
            finally:
                self.release.set()
            self.wait_for(lambda: not window.busy)
        self.assertEqual(chip.accessibleName(), original)
        self.assertEqual(window.run.state['resources'], before)

    def test_hud_rejects_old_sources_and_excludes_a_historical_floor(self):
        window = self.window
        window.show_compact()
        bar = window.compact_window
        bar.open_map()
        panel = bar.map_popup.panel
        self.qt.processEvents()
        self.assertIn(panel.resources, bar.visible_current_resource_strips())
        with patch.object(panel.view, 'graph', {'zone_id': 'old'}), patch.object(panel.view, 'historical', True):
            self.assertNotIn(panel.resources, bar.visible_current_resource_strips())
        window.busy = True
        epoch, generation, run_id = window.sample_epoch, window.capture.stats()['generation'], window.run.state['id']
        at = time.time()
        window.last_sample_at, window.last_sample_seq = at, 4
        with patch.object(bar, 'update_current_hud') as show:
            for marker, stamp, seq in [
                ((epoch+1, generation, run_id), at+1, 5),
                ((epoch, generation+1, run_id), at+1, 5),
                ((epoch, generation, 'other-run'), at+1, 5),
                ((epoch, generation, run_id), at, 3),
            ]:
                window.show_sample_hud((marker, stamp, seq, {'shield': {'value': 1}}))
            show.assert_not_called()

    def test_busy_gold_preserves_other_partial_fields_through_refresh_and_older_commit(self):
        from rouge.busy_gold import GoldReference
        window = self.window
        window.show_compact()
        bar = window.compact_window
        bar.open_inventory()
        chips = bar.inventory_popup.resources.chips
        probe = window.busy_gold
        marker = probe.current_marker()
        ref = GoldReference(marker, {'seq': 1, 'target': window.capture.target, 'client_rect': [0, 0, 360, 200]}, {}, Mock())
        at = time.time()
        window.busy = True
        with patch.object(window.auto, 'isChecked', return_value=True):
            probe.accept_reference(ref)
            window.show_sample_hud((marker, at, 1, {'life': {'value': 6}, 'gold': {'value': 20}}))
            probe.accept_result((ref, at, 2, {'value': 22}))
            bar.refresh()
            self.assertEqual(chips['life'].accessibleName(), '目标生命 6')
            self.assertEqual(chips['gold'].accessibleName(), '源石锭 22')
            window.run.state['resources']['gold'] = {'value': 20, 'captured_at': at}
            probe.complete(marker, 1, map_read=True)
            window.restore_committed_hud()
            bar.refresh()
            self.assertEqual(chips['gold'].accessibleName(), '源石锭 22')
            probe.complete(marker, 2, map_read=False)
            self.assertEqual(chips['gold'].accessibleName(), '源石锭 20')

    def test_overlay_reference_keeps_pointer_bounds_from_its_recognized_frame(self):
        self.release.set();image=np.full((120,180,3),60,dtype=np.uint8)
        self.window.capture.buffer.offer(image,time.time(),pointer_bounds=[20,30,50,80])
        self.window.auto.setChecked(True)
        self.wait_for(lambda:not self.window.busy and self.window.map_overlay_reference is not None)
        self.assertEqual(self.window.map_overlay_reference['pointer_bounds'],(20,30,50,80))

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

    def test_reader_failure_reports_once_and_next_frame_still_runs(self):
        self.release.set();original=self.window.reader.read;attempts=[];errors=[]
        self.window.events.sample_error.connect(errors.append)
        def unreliable(image,**kwargs):
            attempts.append(int(image[0,0,0]))
            if len(attempts)==1:raise RuntimeError('temporary recognition failure')
            return original(image,**kwargs)
        self.window.reader.read=unreliable
        self.offer(50);self.window.auto.setChecked(True)
        self.wait_for(lambda:len(errors)==1 and not self.window.busy)
        self.assertEqual(attempts,[50])
        self.assertIn('temporary recognition failure',errors[0][2])
        self.assertFalse(self.window.operator_observations)
        self.assertTrue(self.window.sample_button.isEnabled())
        self.offer(80)
        self.wait_for(lambda:bool(self.window.operator_observations) and not self.window.busy)
        self.assertEqual(attempts,[50,80])
        self.assertEqual(self.window.operator_observations['kaltsit']['fields']['level'],80)
        self.assertEqual(self.window.observation['_sampling']['recognition_attempts'],1)

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
