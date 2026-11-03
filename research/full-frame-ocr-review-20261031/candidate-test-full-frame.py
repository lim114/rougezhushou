"""Full discovery batches do not replace current dirty-region coverage."""
from copy import deepcopy
from unittest.mock import patch
import unittest
import numpy as np
from rouge.dynamic_ocr import DynamicOCR
from rouge.recognition import ScreenReader


class FullFrameOCRReviewTests(unittest.TestCase):
    def test_full_and_local_backends_are_chosen_by_existing_discovery_gates(self):
        calls=[]
        def full(image):calls.append(('full',image.shape));return [],None
        def local(image):calls.append(('local',image.shape));return [],None
        image=np.zeros((480,900,3),np.uint8);reader=DynamicOCR(local,full_engine=full)
        reader(image);self.assertEqual(calls,[('full',image.shape)])
        image[210,310]=88;reader(image)
        self.assertEqual(calls[-1][0],'local');self.assertLess(np.prod(calls[-1][1]),image.size)
        self.assertEqual(reader.metrics['mode'],'dirty_regions')
        image[:400,:700]=99;reader(image)
        self.assertEqual(calls[-1],('full',image.shape));self.assertEqual(reader.metrics['mode'],'full_discovery')

    def test_explicit_force_geometry_dtype_and_age_keep_the_full_discovery_gate(self):
        calls=[]
        def engine(im):calls.append(im.shape);return [],None
        image=np.zeros((480,900,3),np.uint8);reader=DynamicOCR(engine,full_engine=engine)
        reader(image);reader(image,force_discovery=True)
        self.assertEqual(len(calls),2)
        reader.age=8;reader(image);self.assertEqual(len(calls),3)
        reader(np.zeros((481,900,3),np.uint8));self.assertEqual(len(calls),4)
        reader(np.zeros((481,900,3),np.uint16));self.assertEqual(len(calls),5)

    def test_ordinary_dynamic_reader_still_uses_its_original_engine(self):
        calls=[]
        def engine(im):calls.append(im.shape);return [],None
        image=np.zeros((480,900,3),np.uint8);reader=DynamicOCR(engine);reader(image)
        self.assertEqual(calls,[image.shape]);self.assertIs(reader.full_engine,engine)

    def reader(self,*,page_ocr_enabled=True):
        image=np.full((480,900,3),17,np.uint8);calls=[]
        self.enterContext(patch('rouge.recognition.prepare_frame',side_effect=lambda im,rect:(im,{})))
        reader=ScreenReader(page_ocr_enabled=page_ocr_enabled)
        def engine(im):calls.append(('original',im.shape));return [[[[1,1],[9,1],[9,9],[1,9]],'local',.99]],None
        reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
        class Router:
            def classify(self,im):return {'candidates':[],'specialized':False,'elapsed_ms':0.,'fallback_reason':'unknown_or_incomplete_controls'}
        class Page:
            def __init__(self):self.engine=engine;self.metrics={};self.released=0
            def read(self,im):
                calls.append(('complete',im.shape));self.metrics={'mode':'page_detected_batches','detected_boxes':1,'recognized_batches':1,'reused_batches':0,'full_detection':True,'complete_current_texts':True,'frame_signature':'not-to-be-exported'}
                return [[[[20,20],[70,20],[70,50],[20,50]],'current-complete',.99]],None
            def release_frame_snapshot(self):self.released+=1
        reader._page_router=Router();reader._page_ocr=Page()
        reader._interpret=lambda im,vp,raw,*args,**kwargs:{'page':'unknown','operator':None,'run':None,'node_content':None,'current_texts':[r[1]for r in raw or[]],'performance':{'stages_ms':{},'ocr':deepcopy(reader._frame_ocr.metrics)}}
        return reader,image,calls

    def test_unknown_page_uses_complete_backend_once_without_guessing_a_page(self):
        reader,image,calls=self.reader();result=reader._read(image)
        self.assertEqual(calls,[('complete',image.shape)])
        self.assertEqual(result['current_texts'],['current-complete'])
        self.assertEqual(result['page'],'unknown');self.assertEqual(result['performance']['routing']['candidates'],[])
        self.assertEqual(result['performance']['routing']['strategy'],'full_discovery')
        self.assertNotIn('semantic_verified',result['performance']['routing'])
        meta=result['performance']['ocr']['full_frame_ocr']
        self.assertTrue(meta['full_detection']);self.assertNotIn('frame_signature',meta)
        self.assertIsNone(reader._page_verified_identity);self.assertEqual(reader._page_ocr.released,1)

    def test_changed_small_region_keeps_the_original_reader_and_current_full_baseline(self):
        reader,image,calls=self.reader();reader._read(image);image[430,830]=88
        result=reader._read(image)
        self.assertEqual([name for name,shape in calls],['complete','original'])
        self.assertNotEqual(calls[-1][1],image.shape)
        self.assertEqual(result['current_texts'],['current-complete','local'])
        self.assertEqual(result['performance']['ocr']['mode'],'dirty_regions')
        self.assertNotIn('full_frame_ocr',result['performance']['ocr'])

    def test_disabling_page_ocr_does_not_call_the_batch_backend(self):
        reader,image,calls=self.reader(page_ocr_enabled=False);result=reader._read(image)
        self.assertEqual(calls,[('original',image.shape)])
        self.assertEqual(result['current_texts'],['local'])

    def test_missing_visual_assets_do_not_stop_complete_current_read(self):
        reader,image,calls=self.reader();reader._page_router=None
        with patch('rouge.page_features.PageFeatureRouter',side_effect=OSError('missing feature files')):
            result=reader._read(image)
        self.assertEqual(calls,[('complete',image.shape)])
        self.assertEqual(result['current_texts'],['current-complete'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'visual_unavailable:OSError')
