"""Protocol doubles prove coverage guards; actual OCR is recorded separately."""
from copy import deepcopy
import unittest
from unittest.mock import patch
import numpy as np
from rouge.dynamic_ocr import DynamicOCR
from rouge.page_ocr import PageOCR, frame_signature
from rouge.recognition import ScreenReader

FLAGS=('full_frame_input','full_detection','full_text_coverage','complete_current_texts')

class PageOCRSeedBridgeTests(unittest.TestCase):
    def reader(self, mutate=None):
        image=np.full((480,900,3),17,np.uint8);calls=[]
        self.enterContext(patch('rouge.recognition.prepare_frame',side_effect=lambda im,rect:(im,{})))
        reader=ScreenReader()
        def engine(current):calls.append(current.shape);return [[[[1,1],[9,1],[9,9],[1,9]],'current-local',.99]],None
        reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
        class Router:
            page=True
            def classify(self,current):return {'specialized':self.page,'candidates':[{'page':'operator_detail','regions':[[0,0,200,240]]}] if self.page else [],'elapsed_ms':0.,'fallback_reason':''}
        class Page:
            def __init__(self):self.engine=engine;self.metrics={};self.raw=None
            def _supported(self):return True
            def complete_frame_matches(self,current):return np.array_equal(current,self.snapshot)
            def read(self,current,**kwargs):
                self.snapshot=current.copy()
                self.raw=[[[[20,20],[70,20],[70,50],[20,50]],'current-full-text',.99]]
                self.metrics={'mode':'page_detected_batches',**{key:True for key in FLAGS},'frame_signature':frame_signature(current),'raw_frame_size':[900,480]}
                if mutate:mutate(self.metrics,current)
                return self.raw,None
        reader._page_router=Router();reader._page_ocr=Page()
        reader._interpret=lambda im,vp,raw,*args,**kwargs:{'page':'operator_detail','operator':{'scope':'operator_profile','complete':True},'run':None,'node_content':None,'current_texts':[row[1] for row in raw or []],'performance':{'stages_ms':{},'ocr':dict(reader._frame_ocr.metrics)}}
        return reader,image,calls

    def test_verified_current_full_frame_is_seeded_without_sharing_mutations(self):
        reader,image,calls=self.reader();reader._read(image)
        self.assertTrue(np.array_equal(reader._frame_ocr.image,image));self.assertIsNone(reader._frame_ocr.regions)
        self.assertEqual(reader._frame_ocr.raw,reader._page_ocr.raw);self.assertEqual(reader._frame_ocr.age,0)
        reader._page_ocr.raw[0][1]='caller-change';image[30,30]=98
        self.assertEqual(reader._frame_ocr.raw[0][1],'current-full-text');self.assertEqual(reader._frame_ocr.image[30,30,0],17)

    def test_every_complete_coverage_flag_requires_literal_true(self):
        for key in FLAGS:
            for value in (False,None,1,np.bool_(True)):
                with self.subTest(key=key,value=repr(value)):
                    reader,image,_=self.reader(lambda meta,im,k=key,v=value:meta.__setitem__(k,v))
                    reader._read(image);self.assertIsNone(reader._frame_ocr.image);self.assertEqual(reader._frame_ocr.raw,[])

    def test_missing_or_stale_signature_cannot_seed_current_frame(self):
        changes=[lambda meta,im:meta.pop('frame_signature'),lambda meta,im:meta.__setitem__('frame_signature',None),lambda meta,im:meta.__setitem__('frame_signature',frame_signature(im+1)),lambda meta,im:meta.__setitem__('raw_frame_size',[900,481])]
        for mutation in changes:
            reader,image,_=self.reader(mutation);reader._read(image)
            self.assertIsNone(reader._frame_ocr.image);self.assertEqual(reader._frame_ocr.raw,[])

    def test_current_input_changed_after_complete_result_is_not_misattributed(self):
        reader,image,_=self.reader(lambda meta,im:im.__setitem__((30,30),99));reader._read(image)
        self.assertIsNone(reader._frame_ocr.image);self.assertEqual(reader._frame_ocr.raw,[])

    def test_digest_collision_cannot_reattribute_old_raw_to_changed_pixels(self):
        class Collision:
            def digest(self):return b'c'*32
        with patch('rouge.page_ocr.hashlib.sha256',return_value=Collision()):
            reader,image,_=self.reader(lambda meta,im:im.__setitem__((30,30),99))
            reader._read(image)
        self.assertIsNone(reader._frame_ocr.image);self.assertEqual(reader._frame_ocr.raw,[])

    def test_transition_reads_changed_pixels_and_retains_only_current_full_baseline(self):
        reader,image,calls=self.reader();reader._read(image)
        reader._page_router.page=False;image[430,830]=88
        result=reader._read(image)
        self.assertLess(result['performance']['ocr']['pixels'],image.shape[0]*image.shape[1])
        self.assertEqual(result['current_texts'],['current-full-text','current-local'])
        self.assertEqual(len(calls),1);self.assertNotEqual(calls[0],image.shape)

    def test_incomplete_current_semantics_do_not_promote_interpreted_page_facts(self):
        reader,image,_=self.reader()
        reader._interpret=lambda *a,**kw:{'page':'operator_detail','operator':{'scope':'operator_profile','complete':False,'fields':{}},'run':None,'node_content':None,'performance':{'stages_ms':{}}}
        result=reader._read(image)
        self.assertFalse(result['performance']['routing']['semantic_verified']);self.assertIsNone(reader._page_verified_identity)
        self.assertEqual(result['performance']['routing']['fallback_reason'],'semantic_validation_failed_complete_text')
        self.assertTrue(np.array_equal(reader._frame_ocr.image,image))

class PageOCRSnapshotCompletionTests(unittest.TestCase):
    def test_inference_failure_does_not_expose_a_complete_current_snapshot(self):
        from tests.test_page_ocr_058 import _Provider
        provider = _Provider()
        reader = PageOCR(provider)
        reader._supported = lambda: True
        image = np.zeros((50, 120, 3), np.uint8)
        with patch.object(provider, "auto_text_det", side_effect=RuntimeError("detector failed")):
            with self.assertRaisesRegex(RuntimeError, "detector failed"):
                reader(image)
        self.assertIsNone(reader._current_frame)
        self.assertFalse(reader.complete_frame_matches(image))


class SeededDynamicDiscoveryGatesTests(unittest.TestCase):
    def baseline(self):
        calls=[]
        def engine(im):calls.append(im.shape);return [],None
        reader=DynamicOCR(engine);image=np.zeros((480,900,3),np.uint8);reader.seed_full_frame(image,[])
        return reader,image,calls

    def test_geometry_dtype_age_and_explicit_force_still_rediscover(self):
        variants=[(np.zeros((481,900,3),np.uint8),{}),(np.zeros((480,900,3),np.uint16),{}),(np.zeros((480,900,3),np.uint8),{'force_discovery':True})]
        for image,kwargs in variants:
            reader,_,calls=self.baseline();reader(image,**kwargs)
            self.assertEqual(reader.metrics['mode'],'full_discovery');self.assertEqual(calls,[image.shape])
        reader,image,calls=self.baseline();reader.age=8;reader(image)
        self.assertEqual(reader.metrics['mode'],'full_discovery');self.assertEqual(calls,[image.shape])

    def test_large_change_retains_original_forty_five_percent_gate(self):
        reader,image,calls=self.baseline();image[:300,:700]=88;reader(image)
        self.assertEqual(reader.metrics['mode'],'full_discovery');self.assertEqual(calls,[image.shape])

    def test_more_than_twelve_regions_still_force_full_discovery(self):
        reader,image,calls=self.baseline()
        for y in (70,240):
            for x in (70,200,330,460,590,720,850):image[y,x]=88
        reader(image);self.assertEqual(reader.metrics['mode'],'full_discovery');self.assertEqual(calls,[image.shape])

    def test_exterior_changes_with_guarded_domain_still_force_full(self):
        reader,image,calls=self.baseline();image[430,830]=88
        reader(image,regions=[[0,0,200,200]],seed_from_full=True,guard_outside=True)
        self.assertEqual(reader.metrics['mode'],'full_discovery');self.assertTrue(reader.metrics['outside_page_regions_changed'])
        self.assertEqual(calls,[image.shape])
