"""A real owned popup and counterexamples; transforms are not new training data."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
import unittest

import cv2
import numpy as np

from rouge.recipient_recognition import read_recipient_buffs,_canonical

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/'.cache/research/p1-recipient-training-054'


class RecipientRecognitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((RESEARCH/'novell-ocr-fixture.json').read_text(encoding='utf-8'))
        file=RESEARCH/cls.fixture['file']
        if hashlib.sha256(file.read_bytes()).hexdigest()!=cls.fixture['sha256']:
            raise AssertionError('Frozen public source changed')
        cls.image=cv2.imdecode(np.fromfile(file,dtype=np.uint8),cv2.IMREAD_COLOR)

    def read(self,*,image=None,texts=None,member=None):
        return read_recipient_buffs(self.image if image is None else image,
            deepcopy(self.fixture['texts']) if texts is None else texts,
            deepcopy(self.fixture['selected']) if member is None else member)

    def test_public_raw_ocr_confirms_owned_medical_buff(self):
        result=self.read()
        self.assertEqual(result['operator_id'],'char_4173_nowell')
        self.assertEqual(result['ids'],['rogue_6_from_relic_6'])
        self.assertEqual(result['count'],1)
        self.assertTrue(result['complete'])
        self.assertGreater(result['entries'][0]['icon']['score'],.94)

    def test_frame_translation_and_scale_do_not_use_fixed_coordinates(self):
        source_h,source_w=self.image.shape[:2]
        for scale in (.75,1.5):
            with self.subTest(scale=scale):
                resized=cv2.resize(self.image,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
                image=cv2.copyMakeBorder(resized,31,19,47,23,cv2.BORDER_CONSTANT,value=(180,180,180))
                h,w=image.shape[:2];texts=deepcopy(self.fixture['texts'])
                for text in texts:
                    text['box']=[[(x*source_w*scale+47)/w,(y*source_h*scale+31)/h] for x,y in text['box']]
                result=self.read(image=image,texts=texts)
                self.assertEqual(result['ids'],['rogue_6_from_relic_6'])
                self.assertTrue(result['complete'])

    def test_account_or_wrong_selected_operator_never_receives_buff(self):
        account=deepcopy(self.fixture['selected']);account['scope']='account'
        self.assertIsNone(self.read(member=account))
        wrong={'id':'char_101_sora','name':'空','scope':'run'}
        self.assertIsNone(self.read(member=wrong))

    def test_missing_owned_statement_or_roster_anchors_is_not_a_popup(self):
        for label in ('此干员已拥有以下1个收藏品增益','收起','收藏品增益'):
            with self.subTest(label=label):
                texts=[t for t in deepcopy(self.fixture['texts']) if t['text']!=label]
                self.assertIsNone(self.read(texts=texts))

    def test_missing_or_changed_description_does_not_confirm(self):
        texts=deepcopy(self.fixture['texts'])
        for t in texts:
            if '获得2技力' in t['text']:t['text']=t['text'].replace('2技力','3技力')
        result=self.read(texts=texts)
        self.assertEqual(result['ids'],[])
        self.assertFalse(result['complete'])
        self.assertIn('description_incomplete_or_conflicting',result['issues'])

    def test_effect_sign_decimal_percentage_and_units_are_not_formatting(self):
        self.assertNotEqual(_canonical('攻击速度-50'),_canonical('攻击速度50'))
        self.assertNotEqual(_canonical('技力+0.8/秒'),_canonical('技力+08/秒'))
        self.assertNotEqual(_canonical('攻击力+120%'),_canonical('攻击力+120'))
        self.assertEqual(_canonical('【医疗】（不消耗希望）'),_canonical('[医疗](不消耗希望)'))

    def test_covering_artwork_cannot_be_replaced_by_name_and_description(self):
        result=self.read();image=self.image.copy()
        points=result['entries'][0]['icon']['box'];h,w=image.shape[:2]
        x0=min(p[0] for p in points);x1=max(p[0] for p in points)
        y0=min(p[1] for p in points);y1=max(p[1] for p in points)
        image[round(y0*h):round(y1*h),round(x0*w):round(x1*w)]=0
        result=self.read(image=image)
        self.assertEqual(result['ids'],[])
        self.assertFalse(result['complete'])
        self.assertIn('icon_unconfirmed',result['issues'])

    def test_visible_count_does_not_claim_hidden_rows_are_complete(self):
        texts=deepcopy(self.fixture['texts'])
        for t in texts:
            if t['text']=='此干员已拥有以下1个收藏品增益':t['text']='此干员已拥有以下2个收藏品增益'
        result=self.read(texts=texts)
        self.assertEqual(result['ids'],['rogue_6_from_relic_6'])
        self.assertFalse(result['complete'])
        self.assertIn('visible_count_incomplete',result['issues'])

    def test_unknown_body_or_zero_without_real_layout_does_not_clear_memory(self):
        texts=deepcopy(self.fixture['texts'])
        header=next(t for t in texts if t['text']=='此干员已拥有以下1个收藏品增益')
        # This contradictory header is a guard test, not a labeled real sample.
        header['text']='此干员已拥有以下0个收藏品增益'
        result=self.read(texts=texts)
        self.assertFalse(result['complete'])
        self.assertIn('zero_layout_unverified',result['issues'])

    def test_public_other_page_negative_images_never_bind(self):
        from rapidocr_onnxruntime import RapidOCR
        engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
        files=['bili-novell-api-1.jpg','taptap-critique-4.jpg','BV1PGKC61EQF-related-first.jpg']
        for name in files:
            with self.subTest(name=name):
                image=cv2.imdecode(np.fromfile(RESEARCH/'source'/name,dtype=np.uint8),1)
                raw,_=engine(image);h,w=image.shape[:2]
                texts=[{'text':t.replace(' ',''),'confidence':float(s),
                    'box':[[float(x)/w,float(y)/h] for x,y in box]} for box,t,s in raw or []]
                self.assertIsNone(self.read(image=image,texts=texts))


if __name__=='__main__':unittest.main()
