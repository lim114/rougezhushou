import copy
import unittest
from unittest.mock import patch
import numpy as np
from rouge.operator_name_recheck import recheck_run_names


def record(text,score=.99,x=.2,y=.2):
    return {'text':text,'confidence':score,'box':[[x,y],[x+.2,y],[x+.2,y+.05],[x,y+.05]]}


class NameRecheck055Tests(unittest.TestCase):
    def setUp(self):
        self.image=np.zeros((100,200,3),dtype=np.uint8)
        self.texts=[record('技能',y=.5),record('分支+',x=.5,y=.5),record('收藏品增益',y=.1),record('司霆惊垫',.874)]
        self.names={'司霆惊蛰':{'char'},'凯尔希思衡托':{'other'}}

    def recheck(self,raw):
        with patch('rouge.operator_name_recheck.identity_index',return_value=self.names):
            return recheck_run_names(self.image,self.texts,lambda image,**kwargs:(raw,0))

    def test_near_spelling_only_locates_work_without_supplying_identity(self):
        self.assertEqual(self.recheck([['司霆惊垫',.999]]),self.texts)

    def test_exact_current_pixel_reread_is_required_at_strict_confidence(self):
        out=self.recheck([['司霆惊蛰',.98]])
        self.assertEqual(out[-1]['text'],'司霆惊蛰')
        self.assertTrue(out[-1]['name_recheck']['exact_identity_verified'])
        self.assertEqual(out[-1]['box'],self.texts[-1]['box'])

    def test_low_confidence_ambiguous_or_unrelated_results_do_not_replace(self):
        for raw in ([['司霆惊蛰',.94]],[['司霆惊蛰',.98],['司霆惊蛰',.99]],[['未知干员',.99]]):
            self.assertEqual(self.recheck(raw),self.texts)

    def test_results_do_not_mutate_source_text_geometry(self):
        before=copy.deepcopy(self.texts);out=self.recheck([['司霆惊蛰',.98]])
        out[-1]['box'][0][0]=.99
        self.assertEqual(self.texts,before)

    def test_absent_strong_roster_controls_make_no_ocr_call(self):
        called=[]
        result=recheck_run_names(self.image,[self.texts[-1]],lambda *a,**k:called.append(1))
        self.assertFalse(called);self.assertEqual(result,[self.texts[-1]])

    def test_high_confidence_exact_name_does_not_spend_another_ocr_call(self):
        self.texts[-1]=record('司霆惊蛰',.99)
        called=[]
        with patch('rouge.operator_name_recheck.identity_index',return_value=self.names):
            out=recheck_run_names(self.image,self.texts,lambda *a,**k:called.append(1))
        self.assertFalse(called);self.assertEqual(out,self.texts)

    def test_owner_threshold_needs_a_strong_exact_name_at_another_current_location(self):
        self.texts.append(record('司霆惊蛰',.98,x=.6,y=.3))
        out=self.recheck([['司霆惊蛰',.9219]])
        self.assertEqual(out[-2]['text'],'司霆惊蛰')
        self.assertIn('corroborating_evidence',out[-2]['name_recheck'])

    def test_overlapping_duplicate_name_is_not_independent_corroboration(self):
        self.texts.append(record('司霆惊蛰',.98,x=.2,y=.2))
        self.assertEqual(self.recheck([['司霆惊蛰',.9219]]),self.texts)


if __name__=='__main__':unittest.main()
