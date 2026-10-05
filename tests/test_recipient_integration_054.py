"""Real popup through run parsing, persistent merge and capture coordinates."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from rouge.run_recognition import read_run
from rouge.run_state import RunState
from rouge.viewport import map_evidence

ROOT=Path(__file__).resolve().parents[1]
RESEARCH=ROOT/'.cache/research/p1-recipient-training-054'


class RecipientIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((RESEARCH/'novell-ocr-fixture.json').read_text(encoding='utf-8'))
        path=RESEARCH/cls.fixture['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==cls.fixture['sha256']
        cls.image=cv2.imdecode(np.fromfile(path,np.uint8),cv2.IMREAD_COLOR)

    def read(self,texts=None):
        # Actual member identity/roster/popup readers stay live. Isolate the
        # unrelated held-strip icon scan and extra unread skill text only.
        with patch('rouge.run_recognition.match_held_icons',return_value=[]):
            return read_run(self.image,copy.deepcopy(self.fixture['texts']) if texts is None else texts,
                            lambda *a,**kw:([],0))

    def selected(self,result):
        return next(m for m in result['operators'] if m['id']==result['selected_operator'])

    def test_real_run_reader_binds_only_selected_member(self):
        result=self.read();member=self.selected(result)
        self.assertEqual(result['page'],'run_roster')
        self.assertEqual(result['selected_operator'],'char_4173_nowell')
        self.assertEqual(member['char_buff_ids'],['rogue_6_from_relic_6'])
        self.assertIs(member['char_buffs_complete'],True)
        self.assertEqual(member['recipient_buffs']['entries'][0]['name'],'医者-新典训')
        self.assertTrue(all('char_buff_ids' not in m for m in result['operators'] if m is not member))
        # The popup proves a recipient; it does not invent cultivation values.
        self.assertNotIn('potential',member['fields'])
        self.assertNotIn('trust',member['fields'])

    def test_full_binding_is_persisted_without_resetting_current_run(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');identity=run.state['id'];at=run.state['started_at']+1
            self.assertTrue(run.apply(self.read(),captured_at=at))
            record=run.state['operators']['char_4173_nowell']
            self.assertEqual(record['char_buff_ids'],['rogue_6_from_relic_6'])
            self.assertIs(record['char_buffs_complete'],True)
            self.assertEqual(run.state['id'],identity)
            restored=RunState(Path(directory)/'run.json')
            self.assertEqual(restored.state['id'],identity)
            self.assertEqual(restored.state['operators']['char_4173_nowell']['char_buff_ids'],record['char_buff_ids'])

    def test_partial_popup_and_unverified_zero_do_not_clear_known_buff(self):
        for change in ('description','zero'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as directory:
                run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
                run.apply(self.read(),captured_at=at);identity=run.state['id']
                texts=copy.deepcopy(self.fixture['texts'])
                for text in texts:
                    if change=='description' and '获得2技力' in text['text']:
                        text['text']=text['text'].replace('2技力','3技力')
                    if change=='zero' and text['text']=='此干员已拥有以下1个收藏品增益':
                        text['text']='此干员已拥有以下0个收藏品增益'
                result=self.read(texts);member=self.selected(result)
                self.assertIs(member['char_buffs_complete'],False)
                run.apply(result,captured_at=at+1)
                self.assertEqual(run.state['operators'][member['id']]['char_buff_ids'],['rogue_6_from_relic_6'])
                self.assertEqual(run.state['id'],identity)

    def test_page_without_popup_reuses_known_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');at=run.state['started_at']+1
            run.apply(self.read(),captured_at=at)
            texts=[copy.deepcopy(t) for t in self.fixture['texts'] if t['text']!='收藏品增益']
            result=self.read(texts)
            self.assertNotIn('char_buff_ids',self.selected(result))
            run.apply(result,captured_at=at+1)
            record=run.state['operators']['char_4173_nowell']
            self.assertEqual(record['char_buff_ids'],['rogue_6_from_relic_6'])
            self.assertIs(record['char_buffs_complete'],True)

    def test_all_popup_polygons_remap_once_without_mutating_ocr(self):
        texts=copy.deepcopy(self.fixture['texts']);before=copy.deepcopy(texts)
        result=self.read(texts)
        member=self.selected(result);old=copy.deepcopy(member['recipient_buffs'])
        # Remap together with the OCR list exactly as ScreenReader does.
        observation={'run':result,'texts':texts}
        map_evidence(observation,{'source_size':[1600,900],'content_rect':[80,90,1360,666]})
        mapped=member['recipient_buffs']
        def polygons(value):
            found=[]
            if isinstance(value,dict):
                for key,item in value.items():
                    if key=='box':found.append(item)
                    else:found.extend(polygons(item))
            elif isinstance(value,list):
                for item in value:found.extend(polygons(item))
            return found
        original,actual=polygons(old),polygons(mapped)
        self.assertGreaterEqual(len(original),6)
        self.assertEqual(len(original),len(actual))
        for a,b in zip(original,actual):
            for (x,y),(px,py) in zip(a,b):
                self.assertAlmostEqual(px,(80+x*1280)/1600)
                self.assertAlmostEqual(py,(90+y*576)/900)
        # OCR was changed only by its own single normal viewport mapping.
        for old_text,new_text in zip(before,texts):
            for (x,y),(px,py) in zip(old_text['box'],new_text['box']):
                self.assertAlmostEqual(px,(80+x*1280)/1600)
                self.assertAlmostEqual(py,(90+y*576)/900)


if __name__=='__main__':unittest.main()
