"""Identity candidates must retain every independently recorded artwork family.

The verifier scores below are injected at the matcher seam.  They are not a
claim that the public sprites or a real client page have those scores.
"""
import copy
import unittest
from unittest.mock import patch

import numpy as np

from rouge.catalog import catalog, tactical_tools
from rouge.relic_recognition import (
    _match_bar, artwork_families, difficulty_families, reference_entries,
    resolve_difficulty_icons, resolve_owned_icons,
)
from rouge.run_recognition import read_owned_cards
from rouge.relics import mechanics


BASE = 'rogue_6_relic_legacy_22'
OTHER = 'rogue_6_relic_legacy_23'
TOOL = 'rogue_6_active_tool_1'


def competing_artwork(best=BASE, other=OTHER, *, gap=.01):
    """Two verified reference scores at one slot, outside any image fixture."""
    refs=[]
    for value,rid in ((20,best),(30,other)):
        pixels=np.full((2,2,3),value,np.uint8)
        mask=np.full((2,2),255,np.uint8)
        refs.append((rid,pixels,mask,pixels.astype(np.float32),
                     np.ones((2,2),np.float32),float(value**2*12)))
    def scores(image,template,*args,**kwargs):
        result=np.full((8,8),1.,np.float32)
        result[2,2]=.01 if int(template[0,0,0])==20 else .01+gap
        return result
    with patch('rouge.relic_recognition.prepared_templates',return_value=refs), \
         patch('rouge.relic_recognition.EnergyScreen.possible',return_value=True), \
         patch('rouge.relic_recognition.ProjectionScreen.possible',return_value=True), \
         patch('rouge.relic_recognition._can_match',return_value=True), \
         patch('rouge.relic_recognition.cv2.matchTemplate',side_effect=scores):
        return _match_bar(np.full((30,70,3),80,np.uint8),900,1600,0,0)


def held_card(rid):
    return {'id':rid,'candidates':[rid],'confirmed':True,
            'source':'held_name_and_usage'}


class ReferenceIdentityCatalogTests(unittest.TestCase):
    def test_reference_ids_are_unique_and_item_ids_are_disjoint(self):
        refs=reference_entries()
        self.assertEqual(len(refs),len({x['id'] for x in refs}))
        self.assertFalse(set(catalog()['relics'])&set(tactical_tools()))

    def test_every_catalog_identity_is_direct_or_recorded_equivalent(self):
        direct={x['id'] for x in reference_entries()}
        self.assertEqual(set(catalog()['relics'])-direct-set(artwork_families()),set())
        self.assertLessEqual(set(tactical_tools()),direct)

    def test_equivalent_families_and_pinned_grade_mapping_are_identical(self):
        families=artwork_families()
        grades=difficulty_families()
        self.assertEqual(set(families),set(grades))
        for rid,family in families.items():
            with self.subTest(rid=rid):
                self.assertEqual(set(family),{x['relicId'] for x in grades[rid][1]})

    def test_char_buff_parent_icon_links_are_original_reference_ids(self):
        direct={x['id'] for x in reference_entries()}
        for bid,buff in mechanics()['char_buffs'].items():
            with self.subTest(buff=bid):
                self.assertIn(buff['raw']['iconId'],direct)
                self.assertEqual(buff['raw']['iconId'],buff['relic_id'])

    def test_every_tactical_tool_has_an_exact_owned_text_identity(self):
        def text(value,y):
            return {'text':value,'confidence':.99,
                    'box':[[.20,y-.01],[.70,y-.01],[.70,y+.01],[.20,y+.01]]}
        held=text('收起',.90)
        for rid,item in tactical_tools().items():
            with self.subTest(tool=rid):
                cards=read_owned_cards([text(item['name'],.20),text(item['usage'],.35)],held)
                self.assertEqual(cards,[{'id':rid,'candidates':[rid],'confirmed':True,
                                       'source':'held_name_and_usage','title':item['name']}])


class CompetingFamilyIdentityTests(unittest.TestCase):
    def test_both_competing_families_remain_candidates(self):
        icons=competing_artwork()
        self.assertEqual(len(icons),1)
        self.assertFalse(icons[0]['confirmed'])
        self.assertEqual(set(icons[0]['candidates']),
                         set(artwork_families()[BASE])|set(artwork_families()[OTHER]))

    def test_runner_up_family_variant_can_be_confirmed_by_exact_owned_usage(self):
        wanted=OTHER+'_b'
        icons=competing_artwork()
        original=copy.deepcopy(icons)
        result=resolve_owned_icons(icons,[held_card(wanted)])
        self.assertEqual(icons,original)
        self.assertTrue(result[0]['confirmed'])
        self.assertEqual(result[0]['id'],wanted)
        self.assertTrue(result[0]['name_usage_confirmed'])

    def test_tool_best_candidate_does_not_hide_competing_relic_variants(self):
        icons=competing_artwork(TOOL,OTHER)
        self.assertEqual(set(icons[0]['candidates']),{TOOL}|set(artwork_families()[OTHER]))

    def test_grade_alone_cannot_decide_a_cross_family_ambiguity(self):
        icons=competing_artwork()
        result=resolve_difficulty_icons(icons,{'value':10})
        self.assertFalse(result[0]['confirmed'])
        self.assertEqual(result[0]['candidates'],icons[0]['candidates'])

    def test_distant_verified_runner_up_does_not_expand_candidates(self):
        icons=competing_artwork(gap=.08)
        self.assertEqual(set(icons[0]['candidates']),set(artwork_families()[BASE]))
        result=resolve_difficulty_icons(icons,{'value':10})
        self.assertTrue(result[0]['confirmed'])
        self.assertEqual(result[0]['id'],BASE+'_c')

    def test_exact_owned_best_family_variant_stays_authoritative(self):
        wanted=BASE+'_a'
        icons=resolve_owned_icons(competing_artwork(),[held_card(wanted)])
        result=resolve_difficulty_icons(icons,{'value':10})[0]
        self.assertEqual(result['id'],wanted)
        self.assertTrue(result['confirmed'])
        self.assertTrue(result['name_usage_confirmed'])


if __name__=='__main__':
    unittest.main()
