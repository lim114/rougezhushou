"""Current pixels guard scheduling reuse and discover unsupported overlays now."""
from copy import deepcopy
from unittest.mock import patch
import unittest

import numpy as np

from rouge.dynamic_ocr import DynamicOCR,union_area
from rouge.page_features import PageFeatureRouter
from rouge.recognition import ScreenReader


class OutsideDomainTests(unittest.TestCase):
    def reader(self):
        calls=[]
        def engine(image):
            calls.append(image.copy())
            return [[[[20,20],[40,20],[40,40],[20,40]],str(int(image.sum())),.97]],None
        return DynamicOCR(engine),calls

    def test_single_new_pixel_outside_verified_domain_discovers_whole_frame_now(self):
        reader,calls=self.reader();image=np.zeros((240,360,3),np.uint8)
        reader(image)
        image[210,320]=1
        raw,_=reader(image,regions=[[0,0,180,160]],seed_from_full=True,guard_outside=True)
        self.assertEqual(len(calls),2)
        self.assertEqual(calls[-1].shape,image.shape)
        self.assertEqual(raw[0][1],'3')
        self.assertEqual(reader.metrics['mode'],'full_discovery')
        self.assertTrue(reader.metrics['outside_page_regions_changed'])
        self.assertEqual(reader.age,0);self.assertIsNone(reader.regions)

    def test_overlay_after_focused_read_is_not_delayed_until_eighth_frame(self):
        reader,calls=self.reader();image=np.zeros((240,360,3),np.uint8)
        domain=[[0,0,180,160]]
        reader(image);reader(image,regions=domain,seed_from_full=True,guard_outside=True)
        self.assertEqual(len(calls),1)
        image[170:220,200:340]=41
        reader(image,regions=domain,guard_outside=True)
        self.assertEqual(len(calls),2)
        self.assertTrue(reader.metrics['outside_page_regions_changed'])

    def test_outside_guard_preserves_existing_generic_domain_contract(self):
        reader,calls=self.reader();image=np.zeros((240,360,3),np.uint8)
        domain=[[0,0,180,160]]
        reader(image,regions=domain);image[210,320]=1
        reader(image,regions=domain)
        self.assertEqual(len(calls),1)
        self.assertNotIn('outside_page_regions_changed',reader.metrics)

    def test_new_pixel_in_l_shape_excluded_corner_requires_full_discovery(self):
        reader,calls=self.reader();image=np.zeros((160,240,3),np.uint8)
        domain=[[10,10,90,70],[40,40,100,90]]
        reader(image);reader(image,regions=domain,seed_from_full=True,guard_outside=True)
        image[80,15]=1
        reader(image,regions=domain,guard_outside=True)
        self.assertEqual(len(calls),2);self.assertEqual(calls[-1].shape,image.shape)
        self.assertTrue(reader.metrics['outside_page_regions_changed'])

    def test_l_shape_overlap_area_is_counted_once_without_filling_corner(self):
        rects=[[10,10,90,70],[40,40,100,90]]
        self.assertEqual(union_area(rects),6300)
        self.assertEqual(union_area(rects+rects),6300)
        self.assertEqual(union_area([[0,0,20,10],[20,0,40,10]]),400)
        self.assertEqual(union_area([]),0)

    def test_union_matches_pixel_oracle_for_overlapping_dynamic_domains(self):
        rng=np.random.default_rng(57)
        for _ in range(40):
            rects=[];mask=np.zeros((70,90),bool)
            for _ in range(7):
                xs=sorted(rng.integers(0,91,2));ys=sorted(rng.integers(0,71,2))
                if xs[0]==xs[1] or ys[0]==ys[1]:continue
                rect=[int(xs[0]),int(ys[0]),int(xs[1]),int(ys[1])]
                rects.append(rect);mask[rect[1]:rect[3],rect[0]:rect[2]]=True
            self.assertEqual(union_area(rects),int(mask.sum()))


class ExactControlSchedulingTests(unittest.TestCase):
    def router(self):
        router=PageFeatureRouter.__new__(PageFeatureRouter)
        router._plan_cache=None;router.long_edge=1100;router.pages=[]
        image=np.zeros((480,900,3),np.uint8)
        controls=[[20,30,90,60],[20,100,90,130],[760,30,830,60],[760,100,830,130]]
        for i,(x0,y0,x1,y1) in enumerate(controls):image[y0:y1,x0:x1]=30+i
        plan={'specialized':True,'candidates':[{'page':'operator_detail','regions':[[0,0,160,200]],
            'control_regions':controls,'transform':[[1.,0.,0.],[0.,1.,0.]]}],
            'facts_from_features':False,'coordinate_space':'input_frame_pixels',
            'elapsed_ms':100.,'fallback_reason':'','feature_reuse':'none'}
        router._remember_plan(image,plan)
        return router,image,plan

    def test_all_exact_controls_skip_feature_detection_but_never_supply_facts(self):
        router,image,plan=self.router();image[300:310,400:410]=99
        with patch('rouge.page_features._scene_features',side_effect=AssertionError('not needed')):
            current=router.classify(image)
        self.assertEqual(current['feature_reuse'],'exact_controls')
        self.assertFalse(current['facts_from_features'])
        self.assertEqual(current['candidates'],plan['candidates'])
        self.assertLess(current['elapsed_ms'],plan['elapsed_ms'])

    def test_one_pixel_in_any_core_control_forces_new_matching(self):
        for index in range(4):
            router,image,plan=self.router()
            x0,y0,_,_=plan['candidates'][0]['control_regions'][index]
            image[y0,x0,0]^=1
            with patch('rouge.page_features._scene_features',return_value=(np.empty((0,2)),None)) as detector:
                current=router.classify(image)
            detector.assert_called_once()
            self.assertFalse(current['specialized']);self.assertIsNone(router._plan_cache)

    def test_shape_dtype_or_unsupported_frame_cannot_reuse_plan(self):
        router,image,_=self.router()
        self.assertIsNone(router._cached_plan(image[:470]))
        self.assertIsNone(router._cached_plan(image.astype(np.uint16)))
        current=router.classify(image.astype(np.uint16))
        self.assertFalse(current['specialized']);self.assertIsNone(router._plan_cache)

    def test_cached_result_and_returned_candidate_do_not_share_mutable_state(self):
        router,image,plan=self.router();plan['candidates'][0]['regions'][0][0]=999
        first=router.classify(image);first['candidates'][0]['transform'][0][0]=777
        first['candidates'][0]['regions'].clear()
        second=router.classify(image)
        self.assertEqual(second['candidates'][0]['transform'][0][0],1.)
        self.assertEqual(second['candidates'][0]['regions'],[[0,0,160,200]])

    def test_missing_or_out_of_frame_controls_disable_cache(self):
        for controls in ([],[[-1,0,20,20]],[[0,0,901,20]]):
            router,image,plan=self.router()
            plan['candidates'][0]['control_regions']=controls
            router._remember_plan(image,plan)
            self.assertIsNone(router._plan_cache)


class ScreenOverlayDiscoveryTests(unittest.TestCase):
    def observation(self):
        return {'page':'operator_detail','operator':{'scope':'operator_profile','complete':True},
                'run':None,'node_content':None,'performance':{'stages_ms':{}}}

    def test_new_exterior_overlay_immediately_reads_whole_current_frame(self):
        image=np.full((1127,2052,3),17,np.uint8);calls=[]
        reader=ScreenReader()
        def engine(frame):
            calls.append(frame.shape)
            return [[[[1,1],[5,1],[5,5],[1,5]],'current',.99]],None
        reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
        class Router:
            def classify(self,current):
                return {'candidates':[{'page':'operator_detail','regions':[[100,100,900,800]]}],
                        'specialized':True,'elapsed_ms':0.,'fallback_reason':'','feature_reuse':'exact_controls'}
        reader._page_router=Router()
        reader._interpret=lambda *a,**k:deepcopy(self.observation())
        reader._read(image);calls.clear()
        image[950:1000,1300:1500]=41
        result=reader._read(image)
        self.assertEqual(calls,[image.shape])
        self.assertEqual(result['performance']['routing']['fallback_reason'],'page_outside_regions_changed')
        self.assertEqual(result['performance']['routing']['feature_reuse'],'exact_controls')
        self.assertEqual(reader._page_route_retry_after,0)


if __name__=='__main__':unittest.main()
