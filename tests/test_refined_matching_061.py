"""Exact refined scores/order, bounded workers and no cross-frame state."""
import json
import hashlib
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from rouge import relic_recognition as icons

ROOT=Path(__file__).resolve().parents[1]


class RefinedMatching061Tests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(61)
        self.image=rng.integers(0,256,(35,67,3),dtype=np.uint8)
        self.template=self.image[4:14,7:19].copy()
        self.mask=np.full(self.template.shape[:2],255,np.uint8)
        self.jobs=[('sample',n) for n in range(13)]

    def test_parallel_matrices_are_exact_original_verifier_and_order(self):
        expected=cv2.matchTemplate(self.image,self.template,cv2.TM_SQDIFF_NORMED,mask=self.mask)
        expected=np.nan_to_num(expected,nan=10,posinf=10,neginf=10)
        image=self.image.copy();template=self.template.copy();mask=self.mask.copy()
        with patch.object(icons,'_refined_template',return_value=(self.template,self.mask)):
            results=list(icons._refined_matches(self.image,self.jobs))
        self.assertEqual([r[:3] for r in results],[('sample',12,10)]*13)
        for row in results:np.testing.assert_array_equal(row[3],expected)
        np.testing.assert_array_equal(self.image,image)
        np.testing.assert_array_equal(self.template,template)
        np.testing.assert_array_equal(self.mask,mask)
        results[0][3][:]=0
        np.testing.assert_array_equal(results[1][3],expected)
        self.assertFalse(any(t.name.startswith('rouge-relic-refine') for t in threading.enumerate()))

    def test_completion_order_cannot_reorder_identity_ties(self):
        jobs=[(str(n),n) for n in range(8)];second_started=threading.Event()
        def ref(rid,size):
            if size==0:self.assertTrue(second_started.wait(3))
            if size==1:second_started.set()
            return self.template,self.mask
        with patch.object(icons,'_refined_template',side_effect=ref):
            result=list(icons._refined_matches(self.image,jobs))
        self.assertEqual([r[0] for r in result],[str(n) for n in range(8)])

    def test_dispatch_is_two_workers_and_at_most_four_pending_results(self):
        batches=[]
        class RecordingPool(ThreadPoolExecutor):
            def __init__(pool,*args,**kwargs):
                self.assertEqual(kwargs['max_workers'],2)
                super().__init__(*args,**kwargs)
            def map(pool,fn,jobs):
                jobs=list(jobs);batches.append(len(jobs))
                return super().map(fn,jobs)
        with patch('concurrent.futures.ThreadPoolExecutor',RecordingPool), \
             patch.object(icons,'_refined_template',return_value=(self.template,self.mask)):
            result=list(icons._refined_matches(self.image,self.jobs))
        self.assertEqual(len(result),13);self.assertEqual(batches,[4,4,4,1])

    def test_small_work_or_large_matrices_keep_serial_path(self):
        with patch('concurrent.futures.ThreadPoolExecutor',side_effect=AssertionError('unneeded pool')), \
             patch.object(icons,'_refined_template',return_value=None):
            self.assertEqual(list(icons._refined_matches(self.image,self.jobs[:7])),[None]*7)
            # Only geometry is required here; no matcher allocates a large matrix.
            large=np.broadcast_to(np.zeros((1,1,3),np.uint8),(1500,1500,3))
            self.assertEqual(list(icons._refined_matches(large,self.jobs)),[None]*13)

    def test_missing_oversize_and_nonfinite_results_preserve_old_rules(self):
        def ref(rid,size):
            if size==0:return None
            if size==1:return self.image,np.ones(self.image.shape[:2],np.uint8)
            return self.template,self.mask
        with patch.object(icons,'_refined_template',side_effect=ref), \
             patch.object(icons.cv2,'matchTemplate',return_value=np.array([[np.nan,np.inf,-np.inf,.05]],np.float32)):
            rows=list(icons._refined_matches(self.image,self.jobs))
        self.assertEqual(rows[:2],[None,None])
        for row in rows[2:]:np.testing.assert_array_equal(row[3],np.array([[10,10,10,.05]],np.float32))

    def test_worker_failure_reaches_caller_and_pool_is_closed(self):
        def ref(rid,size):
            if size==2:raise ValueError('fixture failure')
            return self.template,self.mask
        with patch.object(icons,'_refined_template',side_effect=ref):
            with self.assertRaisesRegex(ValueError,'fixture failure'):
                list(icons._refined_matches(self.image,self.jobs))
        self.assertFalse(any(t.name.startswith('rouge-relic-refine') for t in threading.enumerate()))

    def test_changed_frame_does_not_reuse_previous_correlation(self):
        with patch.object(icons,'_refined_template',return_value=(self.template,self.mask)):
            a=list(icons._refined_matches(self.image,self.jobs))
            changed=self.image.copy();changed[4:14,7:19]=0
            b=list(icons._refined_matches(changed,self.jobs))
        self.assertFalse(np.array_equal(a[0][3],b[0][3]))

    def test_two_actual_bars_keep_every_frozen_score_center_and_candidate(self):
        before=json.loads((ROOT/'.cache/research/held-performance-061/baseline-profile.json').read_text(encoding='utf-8'))
        for fixture,row in zip(before['sources']['cases'],before['rows']):
            with self.subTest(case=row['case']):
                path=ROOT/fixture['file']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),fixture['sha256'])
                with np.load(path,allow_pickle=False) as saved:
                    actual=icons._match_bar(saved['roi'],int(saved['height']),int(saved['width']),0,0)
                canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'))
                self.assertEqual(canonical(actual),canonical(row['result']))


if __name__=='__main__':unittest.main()
