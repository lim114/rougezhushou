"""Actual multi-buff held popup, with masked tabs and strict current context."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.recipient_recognition import read_owned_popup_member,read_recipient_buffs
from rouge.recognition_cache import CachedOCR,ExactImageCache
from rouge.run_recognition import read_run
from rouge.run_state import RunState

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.cache/research/p1-live-recipient-055'
EPOCH='1791131176463664300'


class OwnedPopupContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image=cv2.imdecode(np.fromfile(DEST/f'cached-pair-{EPOCH}-0.png',np.uint8),1)
        cls.observation=json.loads((DEST/f'cached-pair-{EPOCH}-0-observation.json').read_text(encoding='utf-8'))
        cls.texts=cls.observation['texts']
        cls.engine=CachedOCR(RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2))

    @staticmethod
    def forbidden(*args,**kwargs):
        raise AssertionError('unattributed context must not trigger local description OCR')

    def test_real_popup_retains_exact_owner_without_inventing_covered_training_fields(self):
        self.assertEqual(self.observation['page'],'unknown')
        self.assertIsNone(self.observation['run'])
        self.assertFalse(any(t['text'] in ('技能','分支+') for t in self.texts))
        member=read_owned_popup_member(self.image,self.texts)
        self.assertEqual(member['id'],'char_151_myrtle')
        self.assertEqual(member['name'],'桃金娘')
        self.assertEqual(member['scope'],'run')
        self.assertEqual(member['fields'],{})
        self.assertEqual(member['skill_ranks'],{})
        self.assertIn('level',member['missing_fields'])

    def test_both_actual_names_icons_full_descriptions_and_count_confirm_snack_and_new_training(self):
        member=read_owned_popup_member(self.image,self.texts)
        result=read_recipient_buffs(self.image,self.texts,member,engine=self.engine)
        self.assertEqual(result['operator_id'],'char_151_myrtle')
        self.assertEqual(set(result['ids']),{'rogue_6_from_relic_1','rogue_6_from_relic_13'})
        self.assertEqual(result['count'],2)
        self.assertTrue(result['complete'])
        self.assertEqual(result['issues'],[])
        self.assertTrue(all(e['icon']['score']>=.94 for e in result['entries']))

    def test_missing_current_owner_card_header_button_or_any_footer_cannot_attribute_popup(self):
        for label in ('收藏品增益','收藏品','收起','编队'):
            with self.subTest(label=label):
                texts=[t for t in self.texts if t['text']!=label]
                self.assertIsNone(read_owned_popup_member(self.image,texts))
        for predicate in (lambda t:'此干员已拥有以下' in t['text'],
                          lambda t:t['text']=='桃金娘' and sum(p[0] for p in t['box'])/4<.5,
                          lambda t:t['text']=='桃金娘' and sum(p[0] for p in t['box'])/4>.5):
            self.assertIsNone(read_owned_popup_member(self.image,[t for t in self.texts if not predicate(t)]))

    def test_conflicting_or_low_confidence_names_and_multiple_independent_cards_are_rejected(self):
        for change in ({'text':'古米'},{'confidence':.949}):
            texts=deepcopy(self.texts)
            next(t for t in texts if t['text']=='桃金娘' and t['box'][0][0]<.5).update(change)
            self.assertIsNone(read_owned_popup_member(self.image,texts))
        texts=deepcopy(self.texts)
        card=deepcopy(next(t for t in texts if t['text']=='桃金娘' and t['box'][0][0]>.5))
        card['box']=[[x,y-.12] for x,y in card['box']]
        texts.append(card)
        self.assertIsNone(read_owned_popup_member(self.image,texts))

    def test_bad_footer_geometry_or_font_and_missing_dynamic_dark_container_are_rejected(self):
        for change in ('position','font'):
            texts=deepcopy(self.texts)
            footer=next(t for t in texts if t['text']=='编队')
            if change=='position':footer['box']=[[x,y-.25] for x,y in footer['box']]
            else:
                cy=sum(p[1] for p in footer['box'])/4
                footer['box']=[[x,cy+(y-cy)*3] for x,y in footer['box']]
            self.assertIsNone(read_owned_popup_member(self.image,texts))
        self.assertIsNone(read_owned_popup_member(np.full_like(self.image,255),self.texts))

    def test_no_single_tab_missing_or_one_buff_layout_is_rescued_by_new_multi_popup_route(self):
        for label in ('技能','分支+'):
            texts=deepcopy(self.texts)
            texts.append({**deepcopy(texts[0]),'text':label,'confidence':.99})
            self.assertIsNone(read_owned_popup_member(self.image,texts))
        texts=deepcopy(self.texts)
        header=next(t for t in texts if '此干员已拥有以下' in t['text'])
        for count in ('1','0'):
            header['text']=header['text'].replace('以下2个',f'以下{count}个')
            self.assertIsNone(read_owned_popup_member(self.image,texts))
            header['text']=header['text'].replace(f'以下{count}个','以下2个')
        texts=[t for t in self.texts if t['text']!='零食盒']
        self.assertIsNone(read_owned_popup_member(self.image,texts))

    def test_wrong_caller_scope_or_owner_does_not_run_description_ocr(self):
        member=read_owned_popup_member(self.image,self.texts)
        for bad in ({**member,'scope':'account'},
                    {**member,'id':'kaltsit','name':'凯尔希·思衡托'}):
            self.assertIsNone(read_recipient_buffs(self.image,self.texts,bad,engine=self.forbidden))

    def test_partial_header_count_never_claims_complete_or_clears_unseen_buff_list(self):
        texts=deepcopy(self.texts)
        header=next(t for t in texts if '此干员已拥有以下' in t['text'])
        header['text']=header['text'].replace('以下2个','以下3个')
        member=read_owned_popup_member(self.image,texts)
        result=read_recipient_buffs(self.image,texts,member,engine=self.engine)
        self.assertEqual(set(result['ids']),{'rogue_6_from_relic_1','rogue_6_from_relic_13'})
        self.assertFalse(result['complete'])
        self.assertIn('visible_count_incomplete',result['issues'])

    def test_source_ocr_is_not_mutated_and_geometry_is_owned_by_result(self):
        texts=deepcopy(self.texts); before=deepcopy(texts)
        member=read_owned_popup_member(self.image,texts)
        member['sources']['owned_popup_context']['owner']['box'][0][0]=.5
        self.assertEqual(texts,before)

    def test_dynamic_scale_translation_preserves_actual_context_and_complete_buff_list(self):
        oh,ow=self.image.shape[:2]
        for scale in (.75,1.25):
            with self.subTest(scale=scale):
                resized=cv2.resize(self.image,None,fx=scale,fy=scale,
                                   interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_LINEAR)
                image=cv2.copyMakeBorder(resized,37,19,53,21,cv2.BORDER_CONSTANT,value=(180,180,180))
                h,w=image.shape[:2];texts=deepcopy(self.texts)
                for t in texts:t['box']=[[(x*ow*scale+53)/w,(y*oh*scale+37)/h] for x,y in t['box']]
                member=read_owned_popup_member(image,texts)
                self.assertEqual(member['id'],'char_151_myrtle')
                result=read_recipient_buffs(image,texts,member,engine=self.engine)
                self.assertTrue(result['complete'])

    def test_temporary_state_saves_both_observed_buffs_and_preserves_unobserved_fixture(self):
        member=read_owned_popup_member(self.image,self.texts)
        result=read_recipient_buffs(self.image,self.texts,member,engine=self.engine)
        member.update(char_buff_ids=result['ids'],char_buffs_complete=result['complete'],recipient_buffs=result)
        with tempfile.TemporaryDirectory(prefix='rouge-owned-popup-unit-055-') as temporary:
            path=Path(temporary)/'run.json';state=RunState(path)
            state.apply({'operators':[{'id':'kaltsit','name':'凯尔希·思衡托','scope':'run','fields':{},
                                       'char_buff_ids':['rogue_6_from_relic_6'],'char_buffs_complete':True}]},time.time())
            self.assertTrue(state.apply({'operators':[member]},time.time()))
            state.save();restored=RunState(path)
            self.assertEqual(set(restored.state['operators']['char_151_myrtle']['char_buff_ids']),
                             {'rogue_6_from_relic_1','rogue_6_from_relic_13'})
            self.assertTrue(restored.state['operators']['char_151_myrtle']['char_buffs_complete'])
            self.assertEqual(restored.state['operators']['kaltsit']['char_buff_ids'],['rogue_6_from_relic_6'])

    @classmethod
    def pipeline(cls):
        if not hasattr(cls,'full_run'):
            cls.full_run=read_run(cls.image,cls.texts,cls.engine,
                                 icon_cache=ExactImageCache(max_bytes=2*1024*1024,max_entries=8))
        return deepcopy(cls.full_run)

    def test_formal_run_fallback_reads_only_owner_and_keeps_obscured_fields_unknown(self):
        run=self.pipeline()
        self.assertEqual(run['page'],'run_roster')
        self.assertEqual(run['selected_operator'],'char_151_myrtle')
        self.assertEqual([m['id'] for m in run['operators']],['char_151_myrtle'])
        member=run['operators'][0]
        self.assertEqual(member['fields'],{})
        self.assertEqual(member['skill_ranks'],{})
        self.assertEqual(set(member['char_buff_ids']),{'rogue_6_from_relic_1','rogue_6_from_relic_13'})
        self.assertTrue(member['char_buffs_complete'])

    def test_formal_run_merge_preserves_previous_owner_training_skills_and_other_members(self):
        run=self.pipeline()
        training={'level':20,'elite':2,'potential':6,'trust':100,'module_id':None,
                  'module_level':0,'selected_skill':2}
        fixture={'operators':[{'id':'char_151_myrtle','name':'桃金娘','scope':'run','fields':training,
                              'skill_ranks':{'1':10,'2':10},'char_buff_ids':['rogue_6_from_relic_1'],
                              'char_buffs_complete':True},
                             {'id':'kaltsit','name':'凯尔希·思衡托','scope':'run','fields':{'level':90,'elite':2},
                              'char_buff_ids':['rogue_6_from_relic_6'],'char_buffs_complete':True}]}
        with tempfile.TemporaryDirectory(prefix='rouge-owned-popup-pipeline-unit-055-') as temporary:
            path=Path(temporary)/'run.json';state=RunState(path)
            self.assertTrue(state.apply(fixture,time.time()))
            self.assertTrue(state.apply(run,time.time()))
            state.save();restored=RunState(path)
            member=restored.state['operators']['char_151_myrtle']
            self.assertEqual(member['fields'],training)
            self.assertEqual(member['skill_ranks'],{'1':10,'2':10})
            self.assertEqual(set(member['char_buff_ids']),{'rogue_6_from_relic_1','rogue_6_from_relic_13'})
            self.assertTrue(member['char_buffs_complete'])
            old=restored.state['operators']['kaltsit']
            self.assertEqual(old['fields'],{'level':90,'elite':2})
            self.assertEqual(old['char_buff_ids'],['rogue_6_from_relic_6'])
            self.assertTrue(old['present'])


if __name__=='__main__':unittest.main()
