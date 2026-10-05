"""Exact visual reuse keeps current pixels/context and unsupported fields honest."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.visual_recognition import VisualReader
from tests.test_adaptive_recognition import sample


def semantic(result):
    return {k:deepcopy(v) for k,v in result.items() if k not in ('observed_at','performance')}


class CountingORB:
    def __init__(self,orb):self.orb=orb;self.calls=0
    def detectAndCompute(self,*args,**kwargs):
        self.calls+=1
        return self.orb.detectAndCompute(*args,**kwargs)
    def __getattr__(self,name):return getattr(self.orb,name)


class CountingMatcher:
    def __init__(self,matcher):self.matcher=matcher;self.calls=0
    def knnMatch(self,*args,**kwargs):
        self.calls+=1
        return self.matcher.knnMatch(*args,**kwargs)


class VisualExactCacheTests(unittest.TestCase):
    def reader(self,**kwargs):
        reader=VisualReader(**kwargs)
        reader.orb=CountingORB(reader.orb)
        reader.matcher=CountingMatcher(reader.matcher)
        return reader

    def blank(self):return np.full((720,1280,3),8,np.uint8)

    def context(self,run='public-run-a',value=9,**metadata):
        return {'run_id':run,'config':{'difficulty':{
            'value':value,'captured_at':1.,'source':'public fixture',**metadata}}}

    def test_exact_public_operator_reuses_only_equal_source_and_is_immutable(self):
        reader=self.reader();image=sample('operator-mechanist')
        first=reader.read(image);expected=semantic(first)
        calls=reader.orb.calls;matching=reader.matcher.calls
        self.assertEqual(first['operator']['fields'],{'potential':6})
        first['operator']['fields']['potential']=99
        first['visual_landmarks'].clear()
        cached=reader.read(image.copy())
        self.assertEqual(semantic(cached),expected)
        self.assertEqual(cached['performance']['reuse'],'exact_frame')
        self.assertEqual(reader.orb.calls,calls);self.assertEqual(reader.matcher.calls,matching)
        self.assertEqual(cached['performance']['current_frame_feature_calls'],0)
        self.assertEqual(cached['performance']['ocr_model_calls'],0)

    def test_one_changed_pixel_invalidates_whole_frame_reuse(self):
        reader=self.reader();image=self.blank();reader.read(image)
        changed=image.copy();changed[200,200]=255
        result=reader.read(changed)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(reader.orb.calls,2)
        self.assertIsNone(result['operator']);self.assertIsNone(result['run'])

    def test_colour_change_with_exact_gray_reuses_features_but_recomputes_result(self):
        reader=self.reader()
        first=np.full((720,1280,3),(10,20,30),np.uint8)
        changed=np.full((720,1280,3),(20,20,26),np.uint8)
        self.assertFalse(np.array_equal(first,changed))
        self.assertTrue(np.array_equal(cv2.cvtColor(first,cv2.COLOR_BGR2GRAY),
                                       cv2.cvtColor(changed,cv2.COLOR_BGR2GRAY)))
        reader.read(first);result=reader.read(changed)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['feature_cache_hits'],1)
        self.assertEqual(reader.orb.calls,1)
        self.assertIsNone(result['operator']);self.assertIsNone(result['run'])

    def test_run_context_change_recomputes_matching_against_current_exact_features(self):
        reader=self.reader();image=sample('operator-mechanist')
        reader.read(image,run_context=self.context())
        previous=reader.matcher.calls
        result=reader.read(image,run_context=self.context(run='public-run-b'))
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['feature_cache_hits'],1)
        self.assertEqual(reader.orb.calls,1)
        self.assertGreater(reader.matcher.calls,previous)
        self.assertEqual(result['operator']['fields'],{'potential':6})

    def test_feature_reuse_never_reuses_current_icon_fields(self):
        reader=self.reader();image=sample('operator-mechanist')
        image[100,100]=(10,20,30)
        changed=image.copy();changed[100,100]=(20,20,26)
        self.assertTrue(np.array_equal(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY),
                                       cv2.cvtColor(changed,cv2.COLOR_BGR2GRAY)))
        with patch('rouge.visual_recognition.match_potential',side_effect=[{'value':6},{'value':1}]) as current:
            first=reader.read(image);second=reader.read(changed)
        self.assertEqual(current.call_count,2)
        self.assertEqual(first['operator']['fields'],{'potential':6})
        self.assertEqual(second['operator']['fields'],{'potential':1})
        self.assertEqual(second['performance']['reuse'],'none')
        self.assertEqual(second['performance']['feature_cache_hits'],1)

    def test_context_snapshot_prevents_mutation_during_read_poisoning_cache(self):
        reader=self.reader();image=self.blank();context=self.context();original=reader._read
        def read_and_mutate(frame,**kwargs):
            context['config']['difficulty']['value']=0
            self.assertEqual(kwargs['run_context']['config']['difficulty']['value'],9)
            return original(frame,**kwargs)
        with patch.object(reader,'_read',side_effect=read_and_mutate):reader.read(image,run_context=context)
        result=reader.read(image,run_context=context)
        self.assertEqual(result['performance']['reuse'],'none')

    def test_full_confirmed_config_metadata_and_value_are_cache_identity(self):
        reader=self.reader();image=self.blank()
        contexts=[self.context(),self.context(source='new provenance'),
                  self.context(captured_at=2.),self.context(value=0),
                  self.context(value=0,independent_note='new public metadata')]
        for context in contexts:
            result=reader.read(image,run_context=context)
            self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(reader.orb.calls,1)

    def test_real_client_rect_change_invalidates_even_equivalent_full_rect(self):
        reader=self.reader();image=self.blank();reader.read(image)
        result=reader.read(image,client_rect=(0,0,1280,720))
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['feature_cache_hits'],1)

    def test_client_rect_snapshot_prevents_mutation_during_read_poisoning_cache(self):
        reader=self.reader();image=self.blank();rect=[0,0,1280,720];original=reader._read
        def read_and_mutate(frame,**kwargs):
            rect[0]=8
            self.assertEqual(kwargs['client_rect'],(0,0,1280,720))
            return original(frame,**kwargs)
        with patch.object(reader,'_read',side_effect=read_and_mutate):reader.read(image,client_rect=rect)
        self.assertEqual(reader._last_rect,(0,0,1280,720))
        result=reader.read(image,client_rect=rect)
        self.assertEqual(result['performance']['reuse'],'none')

    def test_geometry_changes_cannot_reuse_prior_frame_or_features(self):
        reader=self.reader();reader.read(self.blank())
        result=reader.read(np.full((900,1400,3),8,np.uint8))
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['feature_cache_hits'],0)
        self.assertEqual(reader.orb.calls,2)

    def test_detector_setting_changes_invalidate_both_cache_levels(self):
        reader=self.reader();image=self.blank();reader.read(image)
        reader.orb.setFastThreshold(11)
        result=reader.read(image)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['feature_cache_hits'],0)
        self.assertEqual(reader.orb.calls,2)

    def test_cache_disabled_reads_every_frame_without_cache_entries(self):
        reader=self.reader(cache_enabled=False);image=self.blank()
        first=reader.read(image);second=reader.read(image)
        self.assertEqual(semantic(first),semantic(second))
        self.assertEqual(reader.orb.calls,2)
        self.assertEqual(second['performance']['reuse'],'none')
        self.assertIsNone(reader._last_frame)
        self.assertIsNone(reader.feature_cache);self.assertIsNone(reader.icon_cache)

    def test_disabling_a_warm_reader_bypasses_all_reuse(self):
        reader=self.reader();image=self.blank();reader.read(image)
        reader.cache_enabled=False
        result=reader.read(image)
        self.assertEqual(reader.orb.calls,2)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(result['performance']['current_frame_feature_calls'],1)
        self.assertIsNone(reader._last_frame)

    def test_frame_capacity_bypass_and_feature_cache_are_bounded(self):
        reader=self.reader();reader._frame_cache_max_bytes=16
        image=self.blank();reader.read(image);result=reader.read(image)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertIsNone(reader._last_frame)
        self.assertLessEqual(reader.feature_cache.bytes,reader.feature_cache.max_bytes)
        self.assertLessEqual(len(reader.feature_cache.entries),reader.feature_cache.max_entries)

    def test_source_snapshot_prevents_caller_mutation_during_compute_poisoning_cache(self):
        reader=self.reader();image=self.blank();seen=[]
        original=reader._read
        def read_and_mutate(frame,**kwargs):
            seen.append(int(frame[200,200,0]));image[200,200]=255
            return original(frame,**kwargs)
        with patch.object(reader,'_read',side_effect=read_and_mutate):reader.read(image)
        self.assertEqual(seen,[8]);self.assertEqual(int(reader._last_frame[200,200,0]),8)
        result=reader.read(image)
        self.assertEqual(result['performance']['reuse'],'none')
        self.assertEqual(reader.orb.calls,2)

    def test_transition_to_unrelated_public_page_clears_old_operator_facts(self):
        reader=self.reader();operator=reader.read(sample('operator-mechanist'))
        self.assertEqual(operator['operator']['id'],'mechanist')
        unrelated=reader.read(sample('module-mechanist'))
        self.assertIsNone(unrelated['operator']);self.assertIsNone(unrelated['run'])
        self.assertEqual(unrelated['texts'],[])
        self.assertEqual(unrelated['performance']['reuse'],'none')


if __name__=='__main__':unittest.main()
