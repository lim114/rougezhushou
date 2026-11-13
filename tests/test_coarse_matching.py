"""Coarse references overlap in bounded batches without changing RGB evidence."""
import threading
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge import relic_recognition as icons
from tests.test_projection_screen_029 import prepared


class CoarseMatchingTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(1311)
        self.image=rng.integers(0,256,(35,67,3),dtype=np.uint8)
        self.template=self.image[4:14,7:19].copy()
        self.mask=np.full(self.template.shape[:2],255,np.uint8)
        self.refs=[prepared(str(i),self.template,self.mask) for i in range(40)]

    def test_actual_bar_path_overlaps_references_but_keeps_tie_order(self):
        started=threading.Event()
        def possible(template,mask,energy,projection=None):
            if template is self.refs[0][3]:self.assertTrue(started.wait(2),'coarse references still serialize')
            if template is self.refs[16][3]:started.set()
            return True
        with patch.object(icons,'prepared_templates',return_value=self.refs), \
             patch.object(icons.ProjectionScreen,'possible',side_effect=possible), \
             patch.object(icons,'artwork_families',return_value={}):
            result=icons._match_bar(self.image,900,1600,0,0)
        self.assertEqual(result[0]['id'],'0')
        self.assertEqual(result[0]['candidates'],sorted(str(i) for i in range(40)))
        self.assertFalse(result[0]['confirmed'])

    def test_matrices_equal_original_rgb_verifier_and_are_independent(self):
        expected=cv2.matchTemplate(self.image,self.template,cv2.TM_SQDIFF_NORMED,mask=self.mask)
        expected=np.nan_to_num(expected,nan=10,posinf=10,neginf=10)
        original=self.image.copy()
        rows=list(icons._coarse_matches(self.image,self.refs))
        self.assertEqual([r[0] for r in rows],[str(i) for i in range(40)])
        for row in rows:np.testing.assert_array_equal(row[3],expected)
        rows[0][3][:]=10
        np.testing.assert_array_equal(rows[1][3],expected)
        np.testing.assert_array_equal(self.image,original)
        self.assertFalse(any(t.name.startswith('rouge-relic-coarse') for t in threading.enumerate()))

    def test_workers_own_their_projection_scratch_and_batches_yield_on_caller(self):
        bound_to_thread={};lock=threading.Lock();original=icons.ProjectionScreen.possible
        def possible(bound,*args):
            with lock:bound_to_thread.setdefault(id(bound),set()).add(threading.get_ident())
            return original(bound,*args)
        caller=threading.get_ident();yields=[]
        with patch.object(icons.ProjectionScreen,'possible',possible), \
             patch('rouge.recognition_priority.yield_to_current',side_effect=lambda:yields.append(threading.get_ident())):
            rows=list(icons._coarse_matches(self.image,self.refs))
        self.assertEqual(len(rows),40)
        self.assertEqual(len(bound_to_thread),2)
        self.assertTrue(all(len(threads)==1 for threads in bound_to_thread.values()))
        self.assertEqual(yields,[caller,caller])

    def test_small_catalog_stays_serial_and_failure_propagates(self):
        with patch('concurrent.futures.ThreadPoolExecutor',side_effect=AssertionError('small catalog needs no pool')):
            self.assertEqual(len(list(icons._coarse_matches(self.image,self.refs[:2]))),2)
        with patch.object(icons.ProjectionScreen,'possible',side_effect=ValueError('fixture failure')):
            with self.assertRaisesRegex(ValueError,'fixture failure'):
                list(icons._coarse_matches(self.image,self.refs))
        self.assertFalse(any(t.name.startswith('rouge-relic-coarse') for t in threading.enumerate()))

    def test_changed_frame_is_screened_again(self):
        self.assertEqual(len(list(icons._coarse_matches(self.image,self.refs))),40)
        self.assertEqual(list(icons._coarse_matches(np.zeros_like(self.image),self.refs)),[])

    def test_dispatch_respects_pending_matrix_budget(self):
        from concurrent.futures import ThreadPoolExecutor
        batches=[]
        class RecordingPool(ThreadPoolExecutor):
            def __init__(pool,*args,**kwargs):
                self.assertEqual(kwargs['max_workers'],2)
                super().__init__(*args,**kwargs)
            def map(pool,fn,jobs):
                jobs=list(jobs);batches.append([len(j) for j in jobs])
                return super().map(fn,jobs)
        # At this geometry only two full-size result matrices fit in 8 MiB.
        large=np.zeros((900,900,3),np.uint8)
        with patch('concurrent.futures.ThreadPoolExecutor',RecordingPool):
            self.assertEqual(list(icons._coarse_matches(large,self.refs)),[])
        self.assertEqual(batches,[[1,1]]*20)


if __name__=='__main__':unittest.main()
