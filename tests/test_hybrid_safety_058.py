"""The independent hybrid verifier cannot hide changed facts or evidence."""
import importlib.util
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from rouge.dynamic_ocr import DynamicOCR
from rouge.recognition import ScreenReader,specialized_observation_valid

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('hybrid_verifier_058',ROOT/'scripts/verify_hybrid_058.py')
VERIFIER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class HybridReplayPolicyTests(unittest.TestCase):
    def test_confidence_and_box_changes_are_strict_failures(self):
        old={'operator':{'confidence':.92,'fields':{'level':70},'box':[[.1,.2],[.3,.4]]}}
        new={'operator':{'confidence':.91,'fields':{'level':70},'box':[[.1,.2],[.31,.4]]}}
        rows=VERIFIER.differences(VERIFIER.strict(old),VERIFIER.strict(new))
        self.assertEqual({row['path'] for row in rows},{'/operator/confidence','/operator/box/1/0'})

    def test_missing_field_and_explicit_unknown_are_distinct(self):
        rows=VERIFIER.differences({'operator':{'level':None}},{'operator':{}})
        self.assertEqual(rows,[{'path':'/operator/level','before':None,'after':None,'reason':'missing_after'}])

    def test_array_length_difference_does_not_hide_surviving_element_changes(self):
        rows=VERIFIER.differences([{'name':'a'},{'name':'b'}],[{'name':'wrong'}])
        self.assertEqual({row['path'] for row in rows},{'/length','/0/name'})

    def test_only_elapsed_ms_is_exempted_recursively(self):
        old={'page':'x','nested':[{'elapsed_ms':3,'score':.9,'count':1}]}
        new={'page':'x','nested':[{'elapsed_ms':4,'score':.9,'count':1}]}
        self.assertEqual(VERIFIER.differences(VERIFIER.strict(old),VERIFIER.strict(new)),[])
        new['nested'][0]['count']=2
        self.assertEqual(VERIFIER.differences(VERIFIER.strict(old),VERIFIER.strict(new))[0]['path'],'/nested/0/count')

    def test_more_than_eighty_leaf_regressions_are_preserved(self):
        old={str(i):i for i in range(150)};new={str(i):i+1 for i in range(150)}
        self.assertEqual(len(VERIFIER.differences(old,new)),150)

    def test_numeric_types_remain_strict_after_json_wire_serialization(self):
        self.assertEqual(VERIFIER.differences({'value':1},{'value':1.0})[0]['reason'],'type_or_value')

    def test_no_approximate_pixel_or_rounded_confidence_projection(self):
        rows=VERIFIER.differences({'confidence':.993154,'box':[100.0001]},
            {'confidence':.9931539,'box':[100.0002]})
        self.assertEqual(len(rows),2)

    def test_inventory_labels_derived_and_real_sources_explicitly(self):
        samples=[{'id':name,'image':'samples/'+name+'.png','sha256':'fixture-hash','client_rect':None}
            for name in sorted(VERIFIER.REPRESENTATIVE|{'operator-kaltsit-animated'})]
        myrtle=next(s for s in samples if s['id']=='myrtle_owned')
        myrtle.update(animation_image='samples/myrtle-animation.png',animation_sha256='fixture-hash')
        capture={'frames':[{'file':str(i)+'.png','sha256':'fixture-hash','client_rect':None} for i in range(2)]}
        with patch.object(VERIFIER,'read',side_effect=lambda p: {'samples':samples}
                if p==VERIFIER.OLD_INVENTORY else capture),patch.object(VERIFIER,'sha',return_value='fixture-hash'):
            cases=VERIFIER.planned_cases()
        self.assertEqual(len(cases),22)
        self.assertEqual(sum(c['group']=='cold' for c in cases),17)
        self.assertEqual(sum(c['group']=='continuous' for c in cases),2)
        derived=[c for c in cases if c['id'].endswith(':scaled_translated')]
        self.assertEqual(len(derived),4)
        self.assertTrue(all('not independent source' in c['provenance'] for c in derived))
        self.assertTrue(all('concatenated' in c['provenance'] for c in cases if c['group']=='transition'))


class HybridIntegrationSafetyTests(unittest.TestCase):
    def observation(self,*,page='operator_detail',complete=True):
        return {'page':page,'operator':{'scope':'operator_profile','complete':complete,
                'fields':{'module_id':'observed','module_level':3}},'run':None,'node_content':None,
                'performance':{'stages_ms':{}}}

    def reader(self,*,complete=True,supported=True,coverage=True):
        image=np.full((480,900,3),17,np.uint8);calls=[]
        # These are orchestration tests. Viewport transforms have independent
        # coverage; keep current pixel coordinates explicit for the fake OCR.
        self.enterContext(patch('rouge.recognition.prepare_frame',side_effect=lambda image,rect:(image,{})))
        reader=ScreenReader()
        def engine(current):
            calls.append(('legacy',current.shape))
            return [[[[20,20],[70,20],[70,50],[20,50]],'legacy-current',.99]],None
        reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
        class Router:
            page='operator_detail'
            def classify(self,current):
                return {'candidates':([] if self.page is None else [{'page':self.page,'regions':[[0,0,200,240]]}]),
                    'specialized':self.page is not None,'elapsed_ms':0.,'fallback_reason':'unknown' if self.page is None else ''}
        class Page:
            def __init__(self):
                self.engine=engine;self.metrics={};self.calls=[]
            def _supported(self):return supported
            def read(self,current,*,regions=None):
                self.calls.append((current.copy(),regions));calls.append(('page',current.shape))
                self.metrics={'mode':'page_detected_batches' if coverage else 'full_discovery',
                    'full_detection':True if coverage else None,'coverage_verified':coverage,
                    'complete_current_texts':True if coverage else None,
                    'fallback_reason':None if coverage else 'unsupported_provider'}
                # Both records are current detections; the second is outside
                # the visual priority domain and cannot be silently discarded.
                value=str(int(current[450,800,0]))
                return [[[[20,20],[70,20],[70,50],[20,50]],'current-name',.99],
                    [[[790,440],[850,440],[850,470],[790,470]],'current-exterior-'+value,.98]],None
        reader._page_router=Router();reader._page_ocr=Page()
        def interpret(current,viewport,raw,elapsed,timings,*,run_context=None):
            result=self.observation(complete=complete)
            result['current_texts']=[r[1] for r in raw or []]
            if raw and raw[0][1]=='legacy-current':
                result.update(page='unknown',operator=None)
            return result
        reader._interpret=interpret
        return reader,image,calls

    def test_first_visual_candidate_uses_region_priority_once_without_full_seed(self):
        reader,image,calls=self.reader();result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['page'])
        self.assertIsNotNone(reader._page_ocr.calls[0][1])
        self.assertEqual(result['performance']['routing']['strategy'],'visual_region_ocr')
        self.assertTrue(result['performance']['routing']['semantic_verified'])
        self.assertEqual(result['current_texts'],['current-name','current-exterior-17'])

    def test_exterior_current_overlay_updates_on_same_page_without_legacy_text(self):
        reader,image,calls=self.reader();reader._read(image)
        image[450,800]=88;result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['page','page'])
        self.assertEqual(result['current_texts'],['current-name','current-exterior-88'])
        self.assertNotIn('current-exterior-17',result['current_texts'])

    def test_incomplete_semantics_rejects_hint_without_duplicate_complete_ocr(self):
        reader,image,calls=self.reader(complete=False);result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['page'])
        self.assertFalse(result['operator']['complete'])
        self.assertEqual(result['performance']['routing']['strategy'],'full_discovery')
        self.assertEqual(result['performance']['routing']['fallback_reason'],'semantic_validation_failed_complete_text')
        self.assertEqual(reader._page_route_retry_after,2)
        self.assertIsNone(reader._page_verified_identity)

    def test_unverified_provider_return_does_not_claim_complete_region_coverage_or_double_read(self):
        reader,image,calls=self.reader(coverage=False);result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['page'])
        self.assertFalse(result['performance']['ocr']['coverage_verified'])
        self.assertIsNone(result['performance']['ocr']['complete_current_texts'])
        self.assertEqual(result['performance']['routing']['strategy'],'full_discovery')
        self.assertEqual(result['performance']['routing']['fallback_reason'],'unsupported_provider')
        self.assertFalse(result['performance']['routing']['semantic_verified'])

    def test_unsupported_split_provider_uses_legacy_whole_frame_once(self):
        reader,image,calls=self.reader(supported=False);result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['legacy'])
        self.assertEqual(reader._page_ocr.calls,[])
        self.assertEqual(result['page'],'unknown')

    def test_hybrid_clears_dirty_reader_before_returning_to_unknown_page(self):
        reader,image,calls=self.reader()
        reader._frame_ocr.image=image.copy();reader._frame_ocr.raw=[['old-cached-text']]
        reader._frame_ocr.regions=((0,0,100,100),);reader._frame_ocr.age=7
        reader._read(image)
        self.assertIsNone(reader._frame_ocr.image);self.assertEqual(reader._frame_ocr.raw,[])
        self.assertIsNone(reader._frame_ocr.regions);self.assertEqual(reader._frame_ocr.age,0)
        reader._page_router.page=None;image[470,870]=29
        result=reader._read(image)
        self.assertEqual([kind for kind,_ in calls],['page','legacy'])
        self.assertEqual(result['current_texts'],['legacy-current'])
        self.assertEqual(result['page'],'unknown')

    def test_current_roster_family_accepts_run_without_account_owner(self):
        current={'page':'run_roster','run':{'page':'run_roster','operators':[{'id':'actual-current'}]},
            'operator':None,'node_content':None}
        self.assertTrue(specialized_observation_valid(current,'run_roster'))
        for key,value in (('page','unknown'),('operator',{'scope':'operator_profile'}),
                ('node_content',{'kind':'event'}),('run',{'page':'run_roster','operators':[]})):
            with self.subTest(key=key,value=value):
                self.assertFalse(specialized_observation_valid({**current,key:value},'run_roster'))
        altered=deepcopy(current);altered['run']['page']='recruitment_offer'
        self.assertFalse(specialized_observation_valid(altered,'run_roster'))


if __name__=='__main__':unittest.main()
