"""Exact crop reuse, invalidation and bounded admission on real popup pixels."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.recognition_cache import CachedOCR, ExactImageCache


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.cache/research/p1-live-recipient-055'
EPOCH = '1791128222941309200'


class CropCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = cv2.imdecode(np.fromfile(SOURCE/f'cached-pair-{EPOCH}-0.png', np.uint8), 1)
        observation = json.loads((SOURCE/f'cached-pair-{EPOCH}-0-observation.json').read_text(encoding='utf-8'))
        # Current actual header anchors the crop; this is not a fixed field ROI.
        header = next(t for t in observation['texts'] if '此干员已拥有以下' in t['text'])
        h, w = cls.image.shape[:2]
        points = header['box']
        cls.bounds = (int(min(p[0] for p in points)*w), int(min(p[1] for p in points)*h),
                      int(max(p[0] for p in points)*w)+1, int(max(p[1] for p in points)*h)+1)
        x0,y0,x1,y1 = cls.bounds
        cls.crop = cls.image[y0:y1,x0:x1]

    @staticmethod
    def backend(calls):
        def call(image, **kwargs):
            # Engine output records the supplied current input and parameters.
            calls.append((image.copy(), deepcopy(kwargs)))
            return [{'sum': int(image.sum()), 'shape': list(image.shape), 'kwargs': kwargs}], None
        return call

    def test_same_actual_crop_in_changed_frame_reuses_only_identical_crop(self):
        calls=[]; reader=CachedOCR(self.backend(calls))
        first=reader(self.crop,use_cls=False)
        changed=self.image.copy()
        changed[0,0,0]^=1
        x0,y0,x1,y1=self.bounds
        second=reader(changed[y0:y1,x0:x1],use_cls=False)
        self.assertFalse(np.array_equal(self.image,changed))
        self.assertEqual(first,second)
        self.assertEqual(len(calls),1)
        self.assertEqual(reader.cache.hits,1)
        changed[y0,x0,0]^=1
        reader(changed[y0:y1,x0:x1],use_cls=False)
        self.assertEqual(len(calls),2)
        self.assertEqual(reader.cache.misses,2)

    def test_parameters_shape_and_dtype_cannot_share_a_cached_value(self):
        calls=[]; reader=CachedOCR(self.backend(calls))
        reader(self.crop,use_cls=False)
        reader(self.crop,use_cls=True)
        reader(self.crop,use_cls=False,use_det=False)
        reader(self.crop.astype(np.uint16),use_cls=False)
        reader(self.crop.reshape(1,-1,3),use_cls=False)
        self.assertEqual(len(calls),5)
        self.assertEqual(reader.cache.hits,0)

    def test_cached_return_is_independent_and_collision_requires_actual_bytes(self):
        calls=[]; reader=CachedOCR(self.backend(calls))
        result=reader(self.crop,use_cls=False)
        expected=deepcopy(result)
        result[0][0]['sum']=-1
        self.assertEqual(reader(self.crop,use_cls=False),expected)
        class SameDigest:
            def digest(self):return b'x'*32
        with patch('rouge.recognition_cache.hashlib.sha256',return_value=SameDigest()):
            a=self.crop.copy(); b=a.copy(); b[0,0,0]^=1
            collision=CachedOCR(self.backend(calls))
            av=collision(a); bv=collision(b)
            self.assertNotEqual(av,bv)
            self.assertEqual(collision.cache.hits,0)
            self.assertEqual(collision.cache.misses,2)

    def test_larger_default_budget_and_byte_entry_limits_remain_hard_bounds(self):
        reader=CachedOCR(self.backend([]))
        self.assertEqual(reader.cache.max_bytes,24*1024*1024)
        self.assertEqual(reader.cache.max_entries,48)
        cache=ExactImageCache(max_bytes=self.crop.nbytes*2,max_entries=2)
        for value in range(5):
            pixels=self.crop.copy(); pixels[0,0,0]=value
            cache.call(pixels,('owned_popup',),lambda:{'value':value})
            self.assertLessEqual(cache.bytes,cache.max_bytes)
            self.assertLessEqual(len(cache.entries),cache.max_entries)
        before=cache.bytes
        big=np.zeros((self.crop.shape[0]*3,self.crop.shape[1],3),np.uint8)
        cache.call(big,('owned_popup',),lambda:{'large':True})
        self.assertEqual(cache.bytes,before)

    def test_same_pixels_cannot_reuse_different_semantic_contexts(self):
        cache=ExactImageCache(max_bytes=self.crop.nbytes*4,max_entries=4)
        for context in ('run_owned_popup','account_detail','reward_offer'):
            value=cache.call(self.crop,(context,),lambda:{'context':context})
            self.assertEqual(value,{'context':context})
        self.assertEqual(cache.hits,0)
        self.assertEqual(cache.misses,3)
        again=cache.call(self.crop,('run_owned_popup',),lambda: self.fail('must hit exact original context'))
        self.assertEqual(again,{'context':'run_owned_popup'})
        self.assertEqual(cache.hits,1)


if __name__=='__main__':unittest.main()
