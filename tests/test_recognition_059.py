"""A visual popup hint needs a currently attributable owned run observation."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
import unittest
from unittest.mock import patch
import cv2
import numpy as np

from rouge.recognition import specialized_observation_valid
from rouge.recipient_recognition import (reconfirm_owned_popup_footer,read_owned_popup_member,
                                         _retain_stronger_current_lines,_canonical)
from rouge.viewport import prepare_frame

ROOT=Path(__file__).resolve().parents[1]

class OwnedPopupSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        receipt=json.loads((ROOT/'HYBRID_0.58_VERIFICATION.json').read_text(encoding='utf-8'))
        for name,sha in receipt['replay_receipts'].items():
            path=ROOT/name
            assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
            value=json.loads(path.read_text(encoding='utf-8'))
            if value['case']=='kaltsit_owned:native':
                cls.original=value['outputs']['current']['frames'][0]['observation']
                break
        else:raise AssertionError('No sealed actual owned popup')

    def current(self):return deepcopy(self.original)
    def member(self,record):
        return next(m for m in record['run']['operators'] if m['id']==record['run']['selected_operator'])

    def test_actual_current_owned_popup_validates_family_without_changing_facts(self):
        record=self.current();before=deepcopy(record)
        self.assertTrue(specialized_observation_valid(record,'run_owned_popup'))
        self.assertEqual(record,before)

    def test_attributable_partial_body_confirms_page_but_keeps_unknown_buffs(self):
        record=self.current();member=self.member(record)
        member['char_buff_ids']=[];member['char_buffs_complete']=False
        member['recipient_buffs'].update(ids=[],entries=[],complete=False,status='partial',
            issues=['description_incomplete_or_conflicting','visible_count_incomplete'])
        before=deepcopy(record)
        self.assertTrue(specialized_observation_valid(record,'run_owned_popup'))
        self.assertEqual(record,before)

    def test_account_node_and_non_roster_conflicts_reject_hint(self):
        for changes in ({'operator':{'scope':'operator_profile'}},{'node_content':{'kind':'event'}},
                        {'page':'unknown'},{'run':None}):
            record=self.current();record.update(changes)
            with self.subTest(changes=changes):
                self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))

    def test_ordinary_roster_or_missing_current_popup_evidence_reject_hint(self):
        for missing in ('recipient_buffs','scope'):
            record=self.current();self.member(record).pop(missing)
            with self.subTest(missing=missing):
                self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))
        record=self.current();record['run']['page']='run_map'
        self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))

    def test_owner_and_selection_must_match_current_popup(self):
        for key,value in (('operator_id','silverash'),('operator_name','凛御银灰'),
                          ('source','reward_offer'),('count',None),('count',0),('count',True)):
            record=self.current();self.member(record)['recipient_buffs'][key]=value
            with self.subTest(key=key,value=value):
                self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))
        record=self.current();self.member(record)['scope']='account'
        self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))
        record=self.current();record['run']['selected_operator']='absent-owner'
        self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))

    def test_missing_current_header_or_container_cannot_confirm_popup(self):
        for key in ('header_evidence','popup_evidence'):
            record=self.current();self.member(record)['recipient_buffs'].pop(key)
            with self.subTest(key=key):
                self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))
            for evidence in ({},{'box':[]},None):
                record=self.current();self.member(record)['recipient_buffs'][key]=evidence
                with self.subTest(key=key,evidence=evidence):
                    self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))

    def test_duplicate_owner_rows_cannot_arbitrarily_select_one(self):
        record=self.current();record['run']['operators'].append(deepcopy(self.member(record)))
        self.assertFalse(specialized_observation_valid(record,'run_owned_popup'))

class OwnedPopupFooterTests(unittest.TestCase):
    """Use the sealed failing frame and its actual one-crop REC result."""
    @classmethod
    def setUpClass(cls):
        probe_path=ROOT/'.cache/research/hybrid-059/epoch2-current/footer-current-rec-probe-1791183933046002600/receipt.json'
        cls.probe=json.loads(probe_path.read_text(encoding='utf-8'))
        for record in (cls.probe['source_frame'],cls.probe['source_worker_row'],cls.probe['crop_file']):
            path=ROOT/record.get('path',record.get('file'))
            assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],path
        frame=cls.probe['source_frame'];encoded=np.fromfile(ROOT/frame['file'],dtype=np.uint8)
        cls.image,viewport=prepare_frame(cv2.imdecode(encoded,cv2.IMREAD_COLOR),frame['client_rect'])
        assert list(cls.image.shape)==cls.probe['prepared_shape']
        row=json.loads((ROOT/cls.probe['source_worker_row']['path']).read_text(encoding='utf-8'))
        raw=row['outputs']['baseline']['frames'][0]['actual_raw_ocr']
        h,w=cls.image.shape[:2]
        cls.texts=[{'text':text.replace(' ',''),'confidence':float(score),
                    'box':[[float(x)/w,float(y)/h] for x,y in box]} for box,text,score in raw]

    def engine(self,output=None,error=None):
        calls=[]
        def read(crop,**kwargs):
            calls.append((crop.copy(),kwargs))
            if error:raise error
            return deepcopy(self.probe['raw_output'] if output is None else output),None
        return read,calls

    def test_only_same_frame_footer_is_reconfirmed_with_actual_rec_output(self):
        before=deepcopy(self.texts);engine,calls=self.engine()
        self.assertIsNone(read_owned_popup_member(self.image,self.texts))
        result=reconfirm_owned_popup_footer(self.image,self.texts,engine)
        self.assertEqual(self.texts,before);self.assertEqual(len(calls),1)
        crop,kwargs=calls[0]
        self.assertEqual(kwargs,{'use_det':False,'use_cls':False})
        self.assertEqual(list(crop.shape),self.probe['crop_shape'])
        self.assertEqual(hashlib.sha256(crop.tobytes()).hexdigest(),self.probe['crop_pixels_sha256'])
        changed=[(old,new) for old,new in zip(before,result) if old!=new]
        self.assertEqual(len(changed),1)
        old,new=changed[0];self.assertEqual(old['text'],'收藏品')
        self.assertEqual(new['confidence'],self.probe['raw_output'][0][1])
        left,top,right,bottom=self.probe['crop_bounds_ltrb'];h,w=self.image.shape[:2]
        self.assertEqual(new['footer_recheck']['box'],[[left/w,top/h],[right/w,top/h],
                                                      [right/w,bottom/h],[left/w,bottom/h]])
        stripped=deepcopy(new);stripped.pop('footer_recheck');stripped['confidence']=old['confidence']
        self.assertEqual(stripped,old)
        member=read_owned_popup_member(self.image,result)
        self.assertEqual((member['id'],member['name'],member['scope']),('char_151_myrtle','桃金娘','run'))
        self.assertEqual(member['fields'],{});self.assertEqual(member['skill_ranks'],{})
        self.assertEqual(member['sources']['owned_popup_context']['footer']['收藏品']['footer_recheck'],new['footer_recheck'])

    def test_recognizer_failure_wrong_text_and_invalid_scores_preserve_unknown(self):
        results=[[['收藏品',.9499]],[['收藏品',float('nan')]],[['收藏品',float('inf')]],
                 [['收藏品',True]],[['收藏品',1.01]],[['收藏品','0.99']],[['藏品',.999]],
                 [['收藏品',.999],['收藏品',.999]],[],[['收藏品']],{'text':'收藏品'}]
        for raw in results:
            engine,calls=self.engine(raw)
            with self.subTest(raw=raw):
                result=reconfirm_owned_popup_footer(self.image,self.texts,engine)
                self.assertIs(result,self.texts);self.assertEqual(len(calls),1)
                self.assertIsNone(read_owned_popup_member(self.image,result))
        engine,calls=self.engine(error=RuntimeError('unavailable'))
        self.assertIs(reconfirm_owned_popup_footer(self.image,self.texts,engine),self.texts)
        self.assertEqual(len(calls),1)

    def test_complete_or_ambiguous_context_never_requests_footer_recognition(self):
        complete=deepcopy(self.texts)
        next(t for t in complete if t['text']=='收藏品')['confidence']=.99
        duplicate=deepcopy(self.texts)
        duplicate.append(deepcopy(next(t for t in duplicate if t['text']=='收藏品')))
        two_weak=deepcopy(self.texts)
        next(t for t in two_weak if t['text']=='编队')['confidence']=.94
        unknown_titles=[t for t in self.texts if t['text']!='零食盒']
        missing_peer=[t for t in self.texts if t['text']!='收起']
        duplicate_header=deepcopy(self.texts)
        duplicate_header.append(deepcopy(next(t for t in self.texts if '此干员' in t['text'])))
        skill_page=deepcopy(self.texts)+[{'text':'技能','confidence':.99,'box':[[0,0],[.1,0],[.1,.1],[0,.1]]}]
        for texts in (complete,duplicate,two_weak,unknown_titles,missing_peer,duplicate_header,skill_page):
            engine,calls=self.engine()
            result=reconfirm_owned_popup_footer(self.image,texts,engine)
            self.assertIs(result,texts);self.assertFalse(calls)

    def test_reconfirmation_cannot_replace_independent_owner_and_card_checks(self):
        texts=deepcopy(self.texts)
        copies=[t for t in texts if t['text']=='桃金娘']
        self.assertEqual(len(copies),2)
        copies[1]['text']='凛御银灰'
        engine,calls=self.engine();result=reconfirm_owned_popup_footer(self.image,texts,engine)
        self.assertEqual(len(calls),1)
        self.assertIsNone(read_owned_popup_member(self.image,result))
        self.assertEqual(texts[0],self.texts[0])

    def test_already_strong_footers_skip_full_image_container_discovery(self):
        texts=deepcopy(self.texts)
        next(t for t in texts if t['text']=='收藏品')['confidence']=.99
        engine,calls=self.engine()
        with patch('rouge.recipient_recognition._popup_region',side_effect=AssertionError('unnecessary full-image pass')):
            self.assertIs(reconfirm_owned_popup_footer(self.image,texts,engine),texts)
        self.assertFalse(calls)

    def test_invalid_current_weak_box_cannot_request_an_unrelated_crop(self):
        texts=deepcopy(self.texts)
        next(t for t in texts if t['text']=='收藏品')['box'][0][0]=-.1
        engine,calls=self.engine()
        self.assertIs(reconfirm_owned_popup_footer(self.image,texts,engine),texts)
        self.assertFalse(calls)

class CurrentDescriptionLineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'.cache/research/hybrid-059/epoch3-current/existing-description-reconfirm-1791186974924856300/receipt.json'
        cls.proof=json.loads(path.read_text(encoding='utf-8'))
        assert cls.proof['existing_strategy_only'] and cls.proof['source_stable']
        assert cls.proof['canonical_equal'] is False
        cls.original=[line['original'] for line in cls.proof['lines']]
        cls.local=cls.proof['function_result']
        for line in cls.proof['lines']:
            crop=ROOT/line['crop']['path']
            assert hashlib.sha256(crop.read_bytes()).hexdigest()==line['crop']['sha256']

    def test_actual_complete_lines_match_prose_without_extra_rec_or_catalog_characters(self):
        before=deepcopy((self.original,self.local))
        result=_retain_stronger_current_lines(self.original,self.local)
        self.assertEqual((self.original,self.local),before)
        self.assertEqual(result['texts'][0]['text'],self.original[0]['text'])
        self.assertEqual(result['texts'][0]['confidence'],self.original[0]['confidence'])
        for index in (1,2):self.assertEqual(result['texts'][index],self.local['texts'][index])
        self.assertEqual(_canonical(''.join(t['text'] for t in result['texts'])),self.proof['pinned_canonical'])
        self.assertEqual(result['local_ocr_calls'],3)
        self.assertEqual([c['source'] for c in result['line_choices']],
                         ['current_full_ocr','current_local_otsu_rec','current_local_otsu_rec'])

    def test_unaligned_or_weak_originals_cannot_supply_the_required_prose(self):
        moved=deepcopy(self.local);moved['texts'][0]['box'][0][0]+=.01
        self.assertIsNone(_retain_stronger_current_lines(self.original,moved))
        self.assertIsNone(_retain_stronger_current_lines(self.original[:-1],self.local))
        unknown_source=deepcopy(self.local);unknown_source['texts'][0]['source']='old_frame'
        self.assertIsNone(_retain_stronger_current_lines(self.original,unknown_source))
        for score in (.949,float('nan'),True,1.01):
            original=deepcopy(self.original);original[0]['confidence']=score
            with self.subTest(score=score):
                self.assertIsNone(_retain_stronger_current_lines(original,self.local))
        wrong=deepcopy(self.original);wrong[0]['text']='此行含未知效果'
        result=_retain_stronger_current_lines(wrong,self.local)
        self.assertNotEqual(_canonical(''.join(t['text'] for t in result['texts'])),self.proof['pinned_canonical'])

if __name__=='__main__':unittest.main()
