"""Pixel identity, mutation isolation and forced reads across both OCR caches."""
from copy import deepcopy
import unittest
import numpy as np
from rouge.page_ocr import PageOCR
from rouge.recognition_cache import ExactImageCache
from tests.test_page_ocr_058 import _Provider
from rouge.recognition import ScreenReader
from unittest.mock import patch


class OCRCacheReviewTests(unittest.TestCase):
    def test_public_screen_read_rejects_empty_input_before_engine_initialization(self):
        for image in(None,np.zeros((0,40,3),np.uint8)):
            reader=ScreenReader()
            with self.assertRaisesRegex(ValueError,'没有有效画面'):reader.read(image)
            self.assertIsNone(reader._engine)

    def test_public_screen_read_keeps_exact_frame_reuse_after_validated_entry(self):
        reader=ScreenReader();image=np.zeros((40,60,3),np.uint8)
        with patch.object(reader,'_read',return_value={'performance':{},'page':'test_page'})as backend:
            first=reader.read(image);second=reader.read(image.copy())
        self.assertEqual(first['page'],second['page']);self.assertEqual(backend.call_count,1)
        self.assertEqual(second['performance']['reuse'],'exact_frame')

    def test_strided_and_contiguous_pixels_share_exact_image_result(self):
        image=np.arange(24*40*3,dtype=np.uint8).reshape(24,40,3)[:,::2]
        self.assertFalse(image.flags.c_contiguous)
        cache=ExactImageCache();calls=[]
        def compute():calls.append(True);return {'texts':['123','生命值']}
        before=cache.call(image,('detail',),compute)
        self.assertEqual(before,cache.call(image.copy(),('detail',),compute))
        self.assertEqual(len(calls),1)
        changed=image.copy();changed[2,3,1]^=1
        cache.call(changed,('detail',),compute)
        self.assertEqual((cache.hits,cache.misses),(1,2))

    def test_strided_batch_pixels_reuse_without_changing_outputs(self):
        p=_Provider();reader=PageOCR(p)
        crops=[np.full((10,40,3),29,np.uint8)[:,::2],np.full((10,20,3),44,np.uint8)]
        original,_,reused=reader._recognize_batch(crops)
        self.assertFalse(reused)
        actual,elapsed,reused=reader._recognize_batch([a.copy()for a in crops])
        self.assertEqual(original,actual);self.assertTrue(reused);self.assertEqual(elapsed,0)
        self.assertEqual(len(p.text_rec.calls),1)
        actual[0]=('mutated',0)
        self.assertEqual(reader._recognize_batch(crops)[0],original)

    def test_batch_order_shape_and_dtype_stay_distinct(self):
        p=_Provider();reader=PageOCR(p)
        a=np.full((10,20,3),29,np.uint8);b=np.full((10,20,3),44,np.uint8)
        for crops in ([a,b],[b,a],[a.astype(np.uint16),b],[a.reshape(20,10,3),b]):
            _,_,reused=reader._recognize_batch(crops);self.assertFalse(reused)
        self.assertEqual(len(p.text_rec.calls),4)
        self.assertTrue(reader._recognize_batch([a,b])[2])

    def test_forced_batch_replacement_counts_bytes_once_and_remains_reusable(self):
        p=_Provider();crops=[p.crops[0]];size=crops[0].nbytes
        reader=PageOCR(p,max_bytes=size,max_entries=1)
        first=deepcopy(reader._recognize_batch(crops)[0])
        for _ in range(3):
            value,_,reused=reader._recognize_batch(crops,force_discovery=True)
            self.assertEqual(value,first);self.assertFalse(reused)
            self.assertEqual(reader._bytes,size)
        self.assertTrue(reader._recognize_batch(crops)[2]);self.assertEqual(len(p.text_rec.calls),4)

    def test_batch_cache_limits_evict_oldest_and_zero_entries_never_reuse(self):
        p=_Provider();reader=PageOCR(p,max_bytes=2400,max_entries=2)
        for value in range(4):
            reader._recognize_batch([np.full((10,20,3),value,np.uint8)])
            self.assertLessEqual(reader._bytes,2400);self.assertLessEqual(len(reader._cache),2)
        self.assertTrue(reader._recognize_batch([np.full((10,20,3),3,np.uint8)])[2])
        self.assertFalse(reader._recognize_batch([np.full((10,20,3),0,np.uint8)])[2])
        disabled=PageOCR(p,max_entries=0)
        for _ in range(2):self.assertFalse(disabled._recognize_batch([p.crops[0]])[2])
        self.assertEqual(disabled._bytes,0)

    def test_failed_image_read_does_not_install_a_cached_success(self):
        cache=ExactImageCache();image=np.zeros((30,60,3),np.uint8)
        def fail():raise RuntimeError('OCR unavailable')
        with self.assertRaisesRegex(RuntimeError,'OCR unavailable'):cache.call(image,(),fail)
        self.assertEqual(cache.bytes,0);self.assertEqual(len(cache.entries),0)
        value=cache.call(image,(),lambda:['recovered']);self.assertEqual(value,['recovered'])
        self.assertEqual(cache.hits,0)
