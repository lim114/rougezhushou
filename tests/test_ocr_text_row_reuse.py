"""Current detection with exact normalized-line reuse under animated pages."""
from copy import deepcopy
import unittest
import numpy as np

from rouge.page_ocr import PageOCR
from rouge.dynamic_ocr import DynamicOCR
from tests.test_page_ocr_058 import _Provider


class TextRowReuseTests(unittest.TestCase):
    def reader(self,**kwargs):
        provider=_Provider()
        reader=PageOCR(provider,reuse_text_rows=True,**kwargs)
        reader._supported=lambda:True
        return reader,provider

    def test_changed_line_does_not_reinfer_unchanged_batch_neighbour(self):
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        reader(frame);p.crops[2][:]=67
        actual,_=reader(frame)
        self.assertEqual([r[1] for r in actual],['10','11','67','13','14'])
        self.assertEqual(reader.metrics['inferred_text_rows'],1)
        self.assertEqual(reader.metrics['reused_text_rows'],4)
        self.assertEqual(p.text_rec.calls[-1].shape[0],1)
        self.assertEqual(actual[2][2],.504)
        self.assertEqual(p.detection_calls,2)

    def test_only_model_input_equivalence_allows_changed_raw_crop_reuse(self):
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        first,_=reader(frame)
        # This provider's normalization uses the first pixel, so this change
        # produces an identical model input; changing the first pixel does not.
        p.crops[2][-1,-1]=92
        second,_=reader(frame)
        self.assertEqual(first,second)
        self.assertEqual(reader.metrics['inferred_text_rows'],0)
        p.crops[2][0,0]=93
        third,_=reader(frame)
        self.assertEqual(third[2][1],'93')
        self.assertEqual(reader.metrics['inferred_text_rows'],1)

    def test_changed_padding_and_decode_ratio_match_fresh_original_batches(self):
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        reader(frame);p.crops[3]=np.full((10,90,3),13,np.uint8)
        actual,_=reader(frame)
        oracle=PageOCR(p,cache_enabled=False);oracle._supported=lambda:True
        expected,_=oracle(frame)
        self.assertEqual(actual,expected)

    def test_current_detection_controls_new_moved_and_removed_lines(self):
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        reader(frame);p.boxes[1][:,1]+=7
        p.crops.append(np.full((10,70,3),99,np.uint8))
        p.boxes.append(np.array([[100,30],[115,30],[115,40],[100,40]],np.float32))
        actual,_=reader(frame)
        self.assertEqual(actual[1][0],p.boxes[1].tolist())
        self.assertEqual(actual[-1][1],'99')
        p.boxes=p.crops=[]
        actual,_=reader(frame)
        self.assertIsNone(actual)
        self.assertEqual(p.detection_calls,3)

    def test_force_and_configuration_change_recompute_all_current_rows(self):
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        reader(frame);reader(frame,force_discovery=True)
        self.assertEqual(reader.metrics['inferred_text_rows'],5)
        self.assertEqual(reader.metrics['reused_text_rows'],0)
        p.text_score=.7;reader(frame)
        self.assertEqual(reader.metrics['inferred_text_rows'],5)
        self.assertEqual(reader.metrics['reused_text_rows'],0)

    def test_bounded_cache_zero_budget_and_mutation_isolation(self):
        for kwargs in ({'max_bytes':0},{'max_entries':0},{'cache_enabled':False}):
            with self.subTest(kwargs=kwargs):
                reader,p=self.reader(**kwargs);frame=np.zeros((50,120,3),np.uint8)
                reader(frame);reader(frame)
                self.assertEqual(reader.metrics['inferred_text_rows'],5)
                self.assertEqual(reader._bytes,0)
        reader,p=self.reader();frame=np.zeros((50,120,3),np.uint8)
        result,_=reader(frame);expected=deepcopy(result);result[0][1]='mutated'
        self.assertEqual(reader(frame)[0],expected)

    def test_forced_replacement_accounts_normalized_bytes_once(self):
        reader,p=self.reader(max_entries=1)
        for _ in range(3):
            reader._recognize_batch([p.crops[0]],force_discovery=True)
            self.assertEqual(len(reader._cache),1)
            self.assertEqual(reader._bytes,sum(len(key[-1]) for key in reader._cache))
            self.assertLessEqual(reader._bytes,reader.max_bytes)

    def test_unknown_page_animation_uses_current_detector_and_catches_new_text(self):
        discovery,p=self.reader();crop_calls=[]
        def crop_engine(image):crop_calls.append(image.shape);return [],None
        reader=DynamicOCR(crop_engine,discovery_engine=discovery)
        frame=np.zeros((50,120,3),np.uint8);reader(frame)
        p.crops[4][:]=77;frame[:]=35
        actual,_=reader(frame)
        self.assertEqual(actual[4][1],'77')
        self.assertEqual(p.detection_calls,2)
        self.assertEqual(crop_calls,[])
        self.assertEqual(reader.metrics['inferred_text_rows'],1)
        self.assertEqual(reader.metrics['mode'],'full_discovery')

    def test_small_dirty_area_keeps_original_crop_engine(self):
        discovery_calls=[];crop_calls=[]
        def discover(image):discovery_calls.append(image.shape);return [],None
        def crop(image):crop_calls.append(image.shape);return [],None
        reader=DynamicOCR(crop,discovery_engine=discover)
        frame=np.zeros((400,600,3),np.uint8);reader(frame)
        frame[200,300]=250;reader(frame)
        self.assertEqual(len(discovery_calls),1)
        self.assertEqual(len(crop_calls),1)
        self.assertLess(crop_calls[0][0]*crop_calls[0][1],400*600)


if __name__=='__main__':unittest.main()
