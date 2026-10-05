"""Numeric fast paths keep pixel proof and the observed upright UI orientation."""
import unittest
from pathlib import Path
import cv2
import numpy as np
from rouge.recognition import ScreenReader
from rouge.run_recognition import near_number

ROOT = Path(__file__).resolve().parents[1]


class NumericRecognition024Tests(unittest.TestCase):
    def counter(self, value='0', width=400, height=240):
        image = np.zeros((240,400,3),np.uint8)
        zero = cv2.imdecode(np.fromfile(ROOT/'rouge/data/ui-icons/collection-counter-zero.png',dtype=np.uint8),0)
        zero = cv2.resize((zero > 0).astype(np.uint8)*255,(22,25),interpolation=cv2.INTER_NEAREST)
        image[117:142,190:212] = zero[:,:,None]
        if value == '10':
            cv2.rectangle(image,(178,117),(182,141),(255,255,255),-1)
        if value == 'blank':image[:]=0
        if value == '8':
            cv2.line(image,(191,129),(211,129),(255,255,255),3)
        image=cv2.resize(image,(width,height),interpolation=cv2.INTER_NEAREST)
        anchor={'text':'收藏品','confidence':.99,
                'box':[[.375,.67],[.625,.67],[.625,.67+38.3/240],[.375,.67+38.3/240]]}
        return image,anchor

    def test_verified_zero_uses_only_recognizer_across_moved_resized_panels(self):
        for width,height,pad in [(400,240,0),(713,428,39),(800,480,73)]:
            with self.subTest(width=width):
                image,anchor=self.counter(width=width,height=height)
                image=cv2.copyMakeBorder(image,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
                anchor['box']=[[(x*width+pad)/(width+pad*2),(y*height+pad)/(height+pad*2)] for x,y in anchor['box']]
                calls=[]
                def engine(crop,**kwargs):
                    calls.append(kwargs)
                    return ([['0',.8]] if kwargs.get('use_det') is False else []),None
                self.assertEqual(near_number(image,[],anchor,engine),0)
                self.assertEqual(calls,[{'use_det':False,'use_cls':False}])

    def test_ten_or_empty_or_wrong_topology_cannot_shortcut_to_zero(self):
        for value in ('10','blank','8'):
            with self.subTest(value=value):
                image,anchor=self.counter(value)
                calls=[]
                def engine(crop,**kwargs):
                    calls.append(kwargs)
                    return ([['0',.99]] if kwargs.get('use_det') is False else []),None
                self.assertIsNone(near_number(image,[],anchor,engine))
                self.assertFalse(any(c.get('use_det') is False for c in calls))

    def test_weak_recognizer_result_falls_back_without_relaxing_threshold(self):
        image,anchor=self.counter()
        calls=[]
        def engine(crop,**kwargs):
            calls.append(kwargs)
            if kwargs.get('use_det') is False:return [['0',.49]],None
            return [[[[0,0],[1,0],[1,1],[0,1]],'3',.95]],None
        self.assertEqual(near_number(image,[],anchor,engine),3)
        self.assertEqual(calls,[{'use_det':False,'use_cls':False},{'use_cls':False}])

    def test_live_capture_has_zero_items_and_six_upright_operators(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/live-0.23.png',dtype=np.uint8),1)
        observed=ScreenReader().read(image,client_rect=[2,45,2050,1125])
        self.assertEqual(observed['run']['relics']['count'],0)
        self.assertEqual(observed['run']['crew_count'],6)
        self.assertEqual(observed['run']['config']['difficulty']['value'],15)

    def test_multicard_and_roster_still_supply_observed_counts_and_skill_ranks(self):
        reader=ScreenReader()
        sample=ROOT/'samples/native-client/run-relic-multicard-closed.png'
        image=cv2.imdecode(np.fromfile(sample,dtype=np.uint8),1)
        run=reader.read(image)['run']
        self.assertEqual(run['relics']['count'],3)
        self.assertEqual(set(run['relics']['ids']),{'rogue_6_relic_fight_26','rogue_6_relic_cargo_1'})
        sample=ROOT/'samples/native-client/run-mechanist-selected.png'
        run=reader.read(cv2.imdecode(np.fromfile(sample,dtype=np.uint8),1))['run']
        self.assertEqual(run['selected_operator'],'mechanist')
        member=next(m for m in run['operators'] if m['id']=='mechanist')
        self.assertTrue(member['skill_ranks'])


if __name__ == '__main__':unittest.main()
