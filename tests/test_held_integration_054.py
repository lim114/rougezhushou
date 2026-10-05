"""Held-page evidence, counter binding and same-run reuse boundaries."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

from rouge.held_cards import read_held_cards
from rouge.run_recognition import expanded_held_page,read_held_counters,read_run
from rouge.run_state import RunState
from rouge.viewport import map_evidence

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'.cache/research/p1-held-cards-054/fixtures.json'
IMAGE=ROOT/'.cache/research/p1-counter-images-054/source/taptap-hydra-100.jpg'


class HeldIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures=json.loads(DATA.read_text(encoding='utf-8'))
        cls.image=cv2.imdecode(np.fromfile(IMAGE,np.uint8),cv2.IMREAD_COLOR)

    def texts(self):return copy.deepcopy(self.fixtures['training_multirow']['texts'])

    def parts(self,texts):
        held=next(t for t in texts if t['text']=='收起')
        anchors={t['text']:t for t in texts if t['confidence']>=.9}
        return anchors,held,read_held_cards(texts,held)

    def read(self,texts,resources=None,image=None):
        # Keep image/held parser/counter/resource code real. Old icon matching
        # and config are covered elsewhere; isolate them from these new seams.
        with patch('rouge.run_recognition.match_held_icons',return_value=[]), \
             patch('rouge.run_recognition.read_config',return_value={}):
            if resources is None:
                return read_run(self.image if image is None else image,texts,lambda *a,**k:([],0))
            with patch('rouge.run_recognition.read_resources',return_value=resources):
                return read_run(self.image if image is None else image,texts,lambda *a,**k:([],0))

    def test_expanded_real_multirow_hidden_hud_is_held_evidence(self):
        texts=self.texts()
        self.assertFalse(any(t['text']=='目标生命值' for t in texts))
        result=self.read(texts)
        self.assertEqual(result['page'],'run_map')
        self.assertEqual(len(result['relics']['cards']),11)
        self.assertIsNone(result['relics']['count'])
        self.assertEqual(result['resources']['parts_count']['value'],15)
        self.assertEqual(result['resources']['parts_count']['capacity'],18)
        self.assertEqual(result['resources']['parts_count']['counter_crosscheck']['value'],15)
        self.assertNotIn('char_buff_ids',result)

    def test_original_three_card_holdout_unchanged(self):
        original=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard.png',np.uint8),cv2.IMREAD_COLOR)
        result=self.read(self.fixtures['holdout_three_cards']['texts'],image=original)
        self.assertEqual({c['id'] for c in result['relics']['cards']},{
            'rogue_6_active_tool_5','rogue_6_relic_fight_26','rogue_6_relic_cargo_1'})
        self.assertEqual(result['relics']['counters'],[])

    def test_each_footer_control_is_required(self):
        for name in ('零件箱','干员','编队'):
            with self.subTest(name=name):
                texts=[t for t in self.texts() if t['text']!=name]
                self.assertFalse(expanded_held_page(*self.parts(texts)))
                self.assertIsNone(self.read(texts))

    def test_reward_shop_or_summary_without_close_control_cannot_bind(self):
        for replacement in ('获得','购买','收藏品','统计'):
            texts=self.texts()
            next(t for t in texts if t['text']=='收起')['text']=replacement
            result=self.read(texts)
            self.assertIsNone(result)

    def test_footer_alone_never_proves_ownership(self):
        anchors,held,_=self.parts(self.texts())
        self.assertFalse(expanded_held_page(anchors,held,[]))
        self.assertFalse(expanded_held_page(anchors,held,[{'confirmed':False}]))

    def test_oversized_or_displaced_labels_cannot_expand_gate(self):
        for huge in (False,True):
            texts=self.texts();control=next(t for t in texts if t['text']=='零件箱')
            if huge:control['box']=[[x,.6 if i<2 else .99] for i,(x,y) in enumerate(control['box'])]
            else:control['box']=[[x,y-.25] for x,y in control['box']]
            self.assertFalse(expanded_held_page(*self.parts(texts)))

    def test_gate_translates_and_scales_with_observed_typography(self):
        texts=self.texts()
        for t in texts:t['box']=[[x*.65+.12,y*.7+.05] for x,y in t['box']]
        self.assertTrue(expanded_held_page(*self.parts(texts)))

    def test_non_map_roster_does_not_leak_held_card_candidates(self):
        def label(name,x):return {'text':name,'confidence':.99,
            'box':[[x,.9],[x+.05,.9],[x+.05,.93],[x,.93]]}
        texts=[label('收起',.05),label('技能',.3),label('分支+',.5)]
        with patch('rouge.run_recognition.read_owned_cards',return_value=[{'confirmed':True,'id':'fake'}]), \
             patch('rouge.run_recognition.match_held_icons',return_value=[]), \
             patch('rouge.run_recognition.read_roster',return_value=[]), \
             patch('rouge.run_recognition.read_selected_member',return_value=None):
            result=read_run(self.image,texts,lambda *a,**k:([],0))
        self.assertEqual(result['page'],'run_roster')
        self.assertEqual(result['relics']['cards'],[])
        self.assertEqual(result['relics']['counters'],[])

    def test_real_counter_binds_only_to_complete_card(self):
        texts=self.texts();_,held,_=self.parts(texts)
        result=read_held_counters(self.image,texts,held)
        self.assertEqual([(r['id'],r['value']) for r in result],[('rogue_6_relic_cargo_2',15)])
        for t in texts:
            if t['text']=='悲伤的红':t['text']='悲伤的'
        self.assertEqual(read_held_counters(self.image,texts,held),[])

    def test_conflicting_counter_does_not_update_current_parts(self):
        result=self.read(self.texts(),{'parts_count':{'value':16,'capacity':18,'source':'fixture'}})
        self.assertNotIn('parts_count',result['resources'])
        self.assertTrue(any('冲突' in s for s in result['limitations']))

    def test_counter_alone_does_not_invent_resource_capacity_or_uncapped_value(self):
        result=self.read(self.texts(),{})
        self.assertEqual(len(result['relics']['counters']),1)
        self.assertEqual(result['resources'],{})

    def test_empty_or_conflicting_read_preserves_same_run_last_confirmed_parts(self):
        with tempfile.TemporaryDirectory() as folder:
            run=RunState(Path(folder)/'run.json')
            first=self.read(self.texts());at=run.state['started_at']+1
            self.assertTrue(run.apply(first,captured_at=at))
            identity=run.state['id'];before=copy.deepcopy(run.state['resources']['parts_count'])
            run.apply(self.read(self.texts(),{}),captured_at=at+1)
            run.apply(self.read(self.texts(),{'parts_count':{'value':16}}),captured_at=at+2)
            self.assertEqual(run.state['id'],identity)
            self.assertEqual(run.state['resources']['parts_count'],before)

    def test_duplicate_marker_candidates_for_one_card_remain_unbound(self):
        texts=self.texts();_,held,_=self.parts(texts)
        from rouge.counter_badges import read_counter_badges
        badges=read_counter_badges(self.image,texts)
        with patch('rouge.run_recognition.read_counter_badges',return_value=badges+copy.deepcopy(badges)):
            self.assertEqual(read_held_counters(self.image,texts,held),[])

    def test_evidence_polygons_remap_once_including_marker(self):
        texts=self.texts();_,held,_=self.parts(texts)
        counter=read_held_counters(self.image,texts,held)[0]
        original=copy.deepcopy(counter)
        view={'source_size':[4000,2000],'content_rect':[200,100,3368,1540]}
        map_evidence(counter,view)
        for path in ('box','marker'):
            old=original['box'] if path=='box' else original['marker']['box']
            new=counter['box'] if path=='box' else counter['marker']['box']
            for (x,y),(a,b) in zip(old,new):
                self.assertAlmostEqual(a,(200+x*3168)/4000)
                self.assertAlmostEqual(b,(100+y*1440)/2000)


if __name__=='__main__':unittest.main()
