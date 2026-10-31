"""Current-run identities and confirmed settings at public recognition/state seams."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock,patch

import numpy as np

from rouge.damage import calculate_damage
from rouge.recognition import ScreenReader
from rouge.relic_recognition import resolve_difficulty_icons,resolve_owned_icons
from rouge.run_config import config_data,confirmed_config,read_config
from rouge.run_state import RunState

BASE='rogue_6_relic_legacy_24'


def icon(base=BASE):
    return {'id':base,'candidates':[base,base+'_a',base+'_b',base+'_c'],
            'confirmed':False,'score':.97,'center':[.2,.9]}


def bar(rows,count=None,ids=None):
    return {'relics':{'icons':copy.deepcopy(rows),'ids':ids or [],'count':count,'source':'held_bar'}}


def grade(value):
    return {'config':{'difficulty':{'value':value,'source':'本局等级标签'}}}


def text(value,x,y):
    return {'text':value,'confidence':.99,'box':[[x-.02,y-.01],[x+.02,y-.01],[x+.02,y+.01],[x-.02,y+.01]]}


class GradeSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.file=Path(self.tmp.name)/'run.json';self.run=RunState(self.file)
        self.at=self.run.state['started_at']+1

    def apply(self,observation,step=0):
        return self.run.apply(observation,self.at+step)

    def test_all_thirteen_groups_resolve_every_grade_and_keep_original_candidates(self):
        groups=config_data()['difficulty_upgrade_relic_groups']
        self.assertEqual(len(groups),13)
        for group in groups.values():
            rows=group['relicData'];base=rows[0]['relicId']
            for value in range(16):
                with self.subTest(base=base,grade=value):
                    out=resolve_difficulty_icons([icon(base)],{'value':value})[0]
                    selected=max((t for t in rows if t['equivalentGrade']<=value),key=lambda t:t['equivalentGrade'])
                    self.assertEqual(out['id'],selected['relicId']);self.assertTrue(out['confirmed'])
                    self.assertEqual(out['difficulty_tier'],selected['equivalentGrade'])
                    self.assertEqual(out['candidates'],icon(base)['candidates'])

    def test_grade_derived_identity_can_be_corrected_without_mutating_caller(self):
        previous=resolve_difficulty_icons([icon()],{'value':10});saved=copy.deepcopy(previous)
        changed=resolve_difficulty_icons(previous,{'value':3})
        self.assertEqual(changed[0]['id'],BASE+'_a');self.assertEqual(previous,saved)

    def test_exact_owned_effect_wins_and_grade_conflict_is_explicit(self):
        card={'id':BASE+'_a','candidates':[BASE+'_a'],'confirmed':True,'source':'held_name_and_usage'}
        owned=resolve_owned_icons([icon()],[card])
        changed=resolve_difficulty_icons(owned,{'value':10})[0]
        self.assertEqual(changed['id'],BASE+'_a');self.assertEqual(changed['tier_label'],'半结构化')
        self.assertEqual(changed['difficulty_conflict']['expected_id'],BASE+'_c')

    def test_invalid_grade_and_cross_family_ambiguity_do_not_guess(self):
        for value in (None,True,False,'10',10.0,-1,16):
            self.assertFalse(resolve_difficulty_icons([icon()],{'value':value})[0]['confirmed'])
        mixed=icon();mixed['candidates'].append('rogue_6_relic_legacy_23')
        self.assertFalse(resolve_difficulty_icons([mixed],{'value':10})[0]['confirmed'])
        self.assertFalse(resolve_difficulty_icons([icon()],{'value':10,'modeDifficulty':'MONTH_TEAM'})[0]['confirmed'])

    def test_late_grade_resolves_saved_bar_without_new_icons_or_screenshot(self):
        self.apply(bar([icon()],1));signature=copy.deepcopy(self.run.state['bar_signature'])
        self.apply(grade(10),1)
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_c']);self.assertTrue(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.state['bar_signature'],signature)
        self.assertEqual(self.run.state['relics'][BASE+'_c']['captured_at'],self.at)

    def test_grade_downgrade_replaces_old_tier_and_retains_history(self):
        self.apply({**bar([icon()],1),**grade(10)});history=copy.deepcopy(self.run.state['history'])
        self.apply(grade(3),1)
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_a'])
        self.assertFalse(self.run.state['relics'][BASE+'_c']['held'])
        self.assertEqual(self.run.state['history'][:len(history)],history)
        self.assertTrue(self.run.inventory_status()['complete'])

    def test_stale_ids_derived_by_reader_are_not_added_with_corrected_id(self):
        old=resolve_difficulty_icons([icon()],{'value':10})
        self.apply({**bar(old,1,[BASE+'_c']),**grade(3)})
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_a']);self.assertTrue(self.run.inventory_status()['complete'])

    def test_pending_candidates_survive_restart_until_grade_is_seen(self):
        self.apply(bar([icon()],1));self.run=RunState(self.file)
        self.apply(grade(6),1)
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_b'])

    def test_manual_reset_prevents_old_candidates_returning(self):
        self.apply(bar([icon()],1));previous_id=self.run.state['id'];self.run.reset()
        self.at=self.run.state['started_at']+1;self.apply(grade(10))
        self.assertNotEqual(self.run.state['id'],previous_id);self.assertEqual(self.run.held_relic_ids(),[])
        self.assertIsNone(self.run.state['relic_icon_memory'])

    def test_count_change_without_icons_invalidates_old_bar_and_survives_restart(self):
        self.apply(bar([icon()],1));self.apply(bar([],0),1)
        self.run=RunState(self.file);self.apply(grade(10),2)
        self.assertEqual(self.run.held_relic_ids(),[]);self.assertTrue(self.run.inventory_status()['complete'])

    def test_changed_positive_count_does_not_claim_old_bar_is_complete(self):
        self.apply(bar([icon()],1));self.apply(bar([],2),1);self.apply(grade(10),2)
        self.assertEqual(self.run.held_relic_ids(),[]);self.assertFalse(self.run.inventory_status()['complete'])

    def test_partial_recheck_keeps_other_known_slots_and_corrects_both_tiers(self):
        other='rogue_6_relic_legacy_23'
        self.apply({**bar([icon(),icon(other)],2),**grade(10)})
        self.apply({**bar([icon()],None),**grade(3)},1)
        self.assertEqual(self.run.held_relic_ids(),sorted([BASE+'_a',other+'_a']))
        self.assertTrue(self.run.inventory_status()['complete'])

    def test_new_artwork_partial_bar_does_not_replay_prior_full_bar(self):
        self.apply(bar([icon()],1));self.apply(bar([icon('rogue_6_relic_legacy_23')],2),1)
        self.apply(grade(10),2)
        self.assertEqual(self.run.held_relic_ids(),['rogue_6_relic_legacy_23_c'])
        self.assertFalse(self.run.inventory_status()['complete'])

    def test_legacy_full_signature_migrates_without_resetting_history(self):
        self.apply(bar([icon()],1));saved=json.loads(self.file.read_text(encoding='utf-8'))
        saved.pop('relic_icon_memory');self.file.write_text(json.dumps(saved),encoding='utf-8')
        self.run=RunState(self.file);history=copy.deepcopy(self.run.state['history']);self.apply(grade(9),1)
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_c']);self.assertTrue(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.state['history'][:len(history)],history)

    def test_repeated_same_grade_does_not_emit_duplicate_inventory_changes(self):
        self.apply({**bar([icon()],1),**grade(10)});history=copy.deepcopy(self.run.state['history'])
        self.apply(grade(10),1);self.apply(grade(10),2)
        self.assertEqual(self.run.state['history'],history)

    def test_stale_capture_cannot_change_grade_or_candidates(self):
        self.apply({**bar([icon()],1),**grade(10)});saved=copy.deepcopy(self.run.state)
        self.assertFalse(self.run.apply(grade(3),self.at-1));self.assertEqual(self.run.state,saved)

    def test_current_tier_is_used_once_by_damage_calculation(self):
        self.apply({**bar([icon()],1),**grade(10)});self.apply(grade(3),1)
        scenario={'operator':'mechanist','skill':1}
        current=calculate_damage({**scenario,'relic_ids':self.run.held_relic_ids()})
        expected=calculate_damage({**scenario,'relic_ids':[BASE+'_a']})
        self.assertEqual(current['estimate'],expected['estimate'])

    def test_exact_usage_survives_later_icon_only_page_and_conflict_is_visible(self):
        observed=bar([icon()],1,[BASE+'_a'])
        observed['relics']['cards']=[{'id':BASE+'_a','candidates':[BASE+'_a'],'confirmed':True,'source':'held_name_and_usage'}]
        self.apply(observed);self.apply({**bar([icon()],1),**grade(10)},1)
        self.assertEqual(self.run.held_relic_ids(),[BASE+'_a']);self.assertIn('变体依据冲突',self.run.summary())


class ConfirmedSettingsReuseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.run=RunState(Path(self.tmp.name)/'run.json');self.at=self.run.state['started_at']+1
        self.run.apply({'config':{'difficulty':{'value':10,'source':'label'},
            'squad':{'id':'rogue_6_band_20','name':'多边贸易分队','level':1,'effect_verified':True,'source':'effect'}}},self.at)
        self.image=np.zeros((100,180,3),np.uint8);self.held=text('收藏品',.1,.9)

    def test_confirmed_squad_and_grade_skip_badge_search(self):
        known=confirmed_config(self.run.recognition_context())
        with patch('rouge.run_badges.find_squad_badge') as find:
            self.assertEqual(read_config(self.image,[],self.held,known_config=known),{})
            find.assert_not_called()

    def test_unknown_grade_is_still_read_without_downgrading_known_squad(self):
        context=self.run.recognition_context();context['config'].pop('difficulty')
        badge={'id':'rogue_6_band_19','name':'多边贸易分队','box':[]}
        with patch('rouge.run_badges.find_squad_badge',return_value=badge) as find,patch('rouge.run_badges.read_badge_grade',return_value=6) as read:
            result=read_config(self.image,[],self.held,known_config=confirmed_config(context))
            self.assertEqual(result['difficulty']['value'],6);self.assertNotIn('squad',result)
            find.assert_called_once();read.assert_called_once()

    def test_explicit_current_label_can_correct_a_reused_grade(self):
        with patch('rouge.run_badges.find_squad_badge') as find:
            result=read_config(self.image,[text('保密等级',.2,.3),text('3',.27,.3)],self.held,
                known_config=confirmed_config(self.run.recognition_context()))
            self.assertEqual(result['difficulty']['value'],3);find.assert_not_called()

    def test_presets_without_run_evidence_are_not_reused(self):
        self.assertEqual(confirmed_config({'config':{'difficulty':{'value':10}}}),{})
        self.assertEqual(confirmed_config({'run_id':'x','config':{'difficulty':{'value':10}}}),{})

    def test_context_is_detached_and_reused_records_keep_original_timestamp(self):
        context=self.run.recognition_context();known=confirmed_config(context)
        context['config']['difficulty']['value']=0
        self.run.apply({'config':known},self.at+1)
        self.assertEqual(self.run.state['config']['difficulty']['value'],10)
        self.assertEqual(self.run.state['config']['difficulty']['captured_at'],self.at)
        self.run.reset();self.run.apply({'config':known},self.run.state['started_at']+1)
        self.assertEqual(self.run.state['config'],{})

    def test_exact_frame_cache_is_scoped_by_run_and_meaningful_settings(self):
        reader=ScreenReader();reader._read=Mock(return_value={'observed_at':0,'performance':{}})
        context=self.run.recognition_context();reader.read(self.image,run_context=context)
        second=reader.read(self.image.copy(),run_context=context)
        self.assertEqual(second['performance']['reuse'],'exact_frame')
        context['config']['difficulty']['captured_at']+=1
        self.assertEqual(reader.read(self.image,run_context=context)['performance']['reuse'],'exact_frame')
        context['config']['difficulty']['value']=3
        self.assertEqual(reader.read(self.image,run_context=context)['performance']['reuse'],'none')
        context['run_id']='another-run'
        self.assertEqual(reader.read(self.image,run_context=context)['performance']['reuse'],'none')
        self.assertEqual(reader._read.call_count,3)


if __name__=='__main__':unittest.main()
