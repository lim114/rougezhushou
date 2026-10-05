"""Current visual domains restrict work, never inherit values across pages."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import numpy as np
from rouge.dynamic_ocr import DynamicOCR,normalize_regions
from rouge.recognition import ScreenReader,specialized_observation_valid


class PageOCRTests(unittest.TestCase):
    def engine(self):
        calls=[]
        def read(image):
            calls.append(image.copy())
            value=int(image[image.shape[0]//2,image.shape[1]//2,0])
            return [[[[4,4],[12,4],[12,12],[4,12]],str(value),.99]],None
        return read,calls

    def test_first_specialized_call_maps_current_crop_coordinates(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((120,240,3),17,np.uint8)
        raw,_=reader(image,regions=[[80,30,160,90]])
        self.assertEqual(raw[0][0],[[84.,34.],[92.,34.],[92.,42.],[84.,42.]])
        self.assertEqual(raw[0][1],'17');self.assertEqual(calls[0].shape,(60,80,3))
        self.assertEqual(reader.metrics['pixels'],4800)

    def test_background_only_change_skips_ocr_but_current_region_change_is_read(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((200,300,3),17,np.uint8);domain=[[100,50,200,150]]
        reader(image,regions=domain)
        image[0:30,0:30]=99;reader(image,regions=domain)
        self.assertEqual(len(calls),1);self.assertEqual(reader.metrics['pixels'],0)
        image[50:150,100:200]=26;raw,_=reader(image,regions=domain)
        self.assertEqual(len(calls),2);self.assertEqual(raw[0][1],'26')

    def test_region_geometry_change_rediscovers_instead_of_reusing_old_values(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((180,300,3),17,np.uint8)
        reader(image,regions=[[10,20,80,100]])
        image[20:100,100:170]=42
        raw,_=reader(image,regions=[[100,20,170,100]])
        self.assertEqual(raw[0][1],'42');self.assertEqual(len(calls),2)
        self.assertEqual(reader.metrics['mode'],'page_discovery')

    def test_unknown_page_full_discovery_discards_prior_domain(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((180,300,3),17,np.uint8)
        reader(image,regions=[[10,20,80,100]]);image[90,150]=65
        raw,_=reader(image)
        self.assertEqual(calls[-1].shape,image.shape);self.assertEqual(raw[0][1],'65')
        self.assertEqual(reader.metrics['mode'],'full_discovery')

    def test_periodic_discovery_includes_every_current_domain_pixel(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((120,240,3),17,np.uint8);domain=[[80,30,160,90]]
        for _ in range(10):reader(image,regions=domain)
        self.assertEqual(len(calls),2);self.assertEqual(reader.metrics['mode'],'page_discovery')

    def test_invalid_regions_fail_open_to_full_discovery(self):
        for region in ([],[[1,2,1,4]],[[0,0,float('nan'),1]],[[1,2]],[[300,0,400,20]]):
            self.assertIsNone(normalize_regions(region,(120,240)))

    def test_strategy_and_dtype_are_part_of_identity(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.full((120,240,3),17,np.uint8)
        reader(image,regions=[[80,30,160,90]])
        reader(image.astype(np.uint16),regions=[[80,30,160,90]])
        self.assertEqual(len(calls),2);self.assertEqual(reader.metrics['mode'],'page_discovery')

    def test_rectangular_overlapping_domains_are_merged_without_duplicate_reads(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        raw,_=reader(np.zeros((120,240,3),np.uint8),regions=[[10,10,90,70],[40,10,100,70]])
        self.assertEqual(len(calls),1);self.assertEqual(len(raw),1)

    def test_l_shaped_domain_preserves_excluded_animated_corner(self):
        domain=normalize_regions([[10,10,90,70],[40,40,100,90]],(120,240))
        mask=np.zeros((120,240),bool)
        for x0,y0,x1,y1 in domain:mask[y0:y1,x0:x1]=True
        self.assertFalse(mask[15,95]);self.assertFalse(mask[80,15])
        self.assertEqual(int(mask.sum()),6300)
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.zeros((120,240,3),np.uint8);reader(image,regions=domain)
        count=len(calls);image[80:85,15:20]=91
        reader(image,regions=domain)
        self.assertEqual(len(calls),count);self.assertEqual(reader.metrics['pixels'],0)

    def test_full_seed_keeps_only_unchanged_text_fully_inside_current_domain(self):
        calls=[]
        records=[[[[20,20],[40,20],[40,40],[20,40]],'inside',.97],
                 [[[110,20],[130,20],[130,40],[110,40]],'outside',.95],
                 [[[80,20],[110,20],[110,40],[80,40]],'crossing',.96]]
        def engine(image):calls.append(image.shape);return deepcopy(records),None
        reader=DynamicOCR(engine);image=np.zeros((160,240,3),np.uint8)
        reader(image);image[120:140,200:220]=99
        raw,_=reader(image,regions=[[0,0,100,100]],seed_from_full=True)
        self.assertEqual([record[1] for record in raw],['inside'])
        self.assertEqual(calls,[(160,240,3)]);self.assertEqual(reader.metrics['pixels'],0)

    def test_full_seed_changed_text_is_replaced_from_current_pixels(self):
        calls=[]
        def engine(image):
            calls.append(image.copy());value=int(image[30,30,0])
            return [[[[20,20],[40,20],[40,40],[20,40]],str(value),.97]],None
        reader=DynamicOCR(engine);image=np.zeros((160,240,3),np.uint8)
        reader(image);image[30,30]=43
        raw,_=reader(image,regions=[[0,0,100,100]],seed_from_full=True)
        self.assertEqual([record[1] for record in raw],['43']);self.assertEqual(len(calls),2)

    def test_full_seed_does_not_allow_geometry_or_dtype_changes(self):
        for changed in (np.zeros((180,240,3),np.uint8),np.zeros((160,240,3),np.uint16)):
            engine,calls=self.engine();reader=DynamicOCR(engine)
            reader(np.zeros((160,240,3),np.uint8))
            reader(changed,regions=[[0,0,100,100]],seed_from_full=True)
            self.assertEqual(len(calls),2);self.assertEqual(reader.metrics['mode'],'full_discovery')

    def test_explicit_whole_discovery_never_reuses_unchanged_cached_text(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.zeros((160,240,3),np.uint8)
        reader(image);reader(image,force_discovery=True)
        self.assertEqual(len(calls),2);self.assertEqual(reader.age,0)

    def test_large_seed_change_uses_one_whole_read_instead_of_multiple_crops(self):
        engine,calls=self.engine();reader=DynamicOCR(engine)
        image=np.zeros((160,240,3),np.uint8);reader(image)
        image[:120,:120]=43
        reader(image,regions=[[0,0,120,120]],seed_from_full=True)
        self.assertEqual(len(calls),2);self.assertEqual(calls[-1].shape,image.shape)
        self.assertIsNone(reader.regions);self.assertEqual(reader.metrics['mode'],'full_discovery')


class SemanticRoutingTests(unittest.TestCase):
    def observation(self,page='operator_detail',complete=True):
        return {'page':page,'operator':{'scope':'operator_profile','complete':complete,
                'fields':{'module_id':'observed','module_level':3}},'run':None,'node_content':None,
                'performance':{'stages_ms':{}}}

    def test_visual_label_does_not_accept_missing_incomplete_or_conflicting_owner(self):
        valid=self.observation()
        self.assertTrue(specialized_observation_valid(valid,'operator_detail'))
        for altered in ({'operator':None},{'page':'unknown'},{'run':{'page':'run_roster'}},
                {'node_content':{'kind':'event'}},{'operator':{'scope':'run','complete':True}},
                {'operator':{'scope':'operator_profile','complete':False}}):
            self.assertFalse(specialized_observation_valid({**valid,**altered},'operator_detail'))

    def test_module_requires_current_equipped_fields_and_never_account_cultivation(self):
        valid=self.observation('operator_module',False)
        self.assertTrue(specialized_observation_valid(valid,'operator_module'))
        for missing in ('module_id','module_level'):
            altered=deepcopy(valid);del altered['operator']['fields'][missing]
            self.assertFalse(specialized_observation_valid(altered,'operator_module'))
        self.assertFalse(specialized_observation_valid(valid,'unknown'))

    def reader(self,result_from_crop,*,warm=False):
        image=np.full((1127,2052,3),17,np.uint8);calls=[]
        reader=ScreenReader()
        def engine(crop):
            mode='full' if crop.shape==image.shape else 'crop';calls.append(mode)
            return [[[[1,1],[5,1],[5,5],[1,5]],mode,.99]],None
        reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
        class Router:
            def classify(self,current):
                return {'candidates':[{'page':'operator_detail','regions':[[100,100,900,800]]}],
                        'specialized':True,'elapsed_ms':0.,'fallback_reason':''}
        reader._page_router=Router()
        def interpret(current,viewport,raw,elapsed,timings,*,run_context=None):
            return deepcopy(result_from_crop if raw[0][1]=='crop' else self.observation())
        reader._interpret=interpret
        if warm:
            reader._read(image);calls.clear();image[450:500,475:525]=25
        return reader,image,calls

    def test_first_visual_candidate_must_be_confirmed_by_whole_current_frame(self):
        reader,image,calls=self.reader(self.observation())
        result=reader._read(image)
        self.assertEqual(calls,['full'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'page_initial_discovery')
        self.assertIsNotNone(reader._page_verified_identity)

    def test_failed_specialist_reads_whole_current_frame_and_resets_domain(self):
        reader,image,calls=self.reader(self.observation(complete=False),warm=True)
        result=reader._read(image,run_context={'run_id':'current'})
        self.assertEqual(calls,['crop','full']);self.assertTrue(result['operator']['complete'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'semantic_validation_failed')
        self.assertIsNone(reader._frame_ocr.regions)

    def test_semantic_failure_backoff_uses_full_discovery_without_retrying_crop(self):
        reader,image,calls=self.reader(self.observation(complete=False),warm=True)
        reader._read(image)
        for count in (1,0):
            result=reader._read(image)
            self.assertEqual(result['performance']['routing']['fallback_reason'],'semantic_retry_backoff')
            self.assertEqual(reader._page_route_retry_after,count)
        self.assertEqual(calls,['crop','full'])

    def test_missing_visual_assets_do_not_block_whole_frame_reading(self):
        reader,image,calls=self.reader(self.observation());reader._page_router=None
        with patch('rouge.page_features.PageFeatureRouter',side_effect=OSError('missing public asset')):
            result=reader._read(image)
        self.assertEqual(calls,['full'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'visual_unavailable:OSError')

    def test_failed_pass_time_is_preserved_in_stage_metrics(self):
        reader,image,calls=self.reader(self.observation(complete=False),warm=True)
        def interpret(current,viewport,raw,elapsed,timings,*,run_context=None):
            elapsed('semantic')
            result=self.observation(complete=raw[0][1]=='full')
            result['performance']['stages_ms']=timings
            return result
        reader._interpret=interpret
        with patch('rouge.recognition.time.perf_counter',side_effect=range(20)):
            result=reader._read(image)
        self.assertEqual(result['performance']['stages_ms']['semantic'],2000.)

    def test_periodic_full_frame_discovery_keeps_unknown_overlays_visible(self):
        reader,image,calls=self.reader(self.observation(),warm=True)
        reader._page_route_age=8
        result=reader._read(image)
        self.assertEqual(calls,['full']);self.assertEqual(reader._page_route_age,0)
        self.assertEqual(result['performance']['routing']['fallback_reason'],'periodic_full_discovery')

    def test_opt_out_avoids_visual_classifier_and_still_reads_current_frame(self):
        reader,image,calls=self.reader(self.observation());reader.page_routing_enabled=False
        with patch.object(reader._page_router,'classify',side_effect=AssertionError('must not classify')):
            result=reader._read(image)
        self.assertEqual(calls,['full']);self.assertEqual(result['performance']['routing']['fallback_reason'],'disabled')

    def test_visual_identity_change_requires_whole_discovery(self):
        reader,image,calls=self.reader(self.observation(),warm=True)
        reader._page_verified_identity=('other_page',image.shape,image.dtype.str,None)
        result=reader._read(image)
        self.assertEqual(calls,['full'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'page_initial_discovery')

    def test_cache_disabled_does_not_seed_or_focus_page_reads(self):
        reader,image,calls=self.reader(self.observation(),warm=True);reader.cache_enabled=False
        result=reader._read(image)
        self.assertEqual(calls,['full'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'cache_disabled')

    def test_large_current_page_change_bypasses_specialist_before_ocr(self):
        reader,image,calls=self.reader(self.observation(complete=False),warm=True)
        image[100:800,100:900]=25
        result=reader._read(image)
        self.assertEqual(calls,['full'])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'page_changed_area_full')
        self.assertEqual(reader._page_route_retry_after,0)


if __name__=='__main__':unittest.main()
