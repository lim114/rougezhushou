import unittest
import json
from pathlib import Path
import cv2
import numpy as np
from rouge.recognition import ScreenReader

ROOT = Path(__file__).resolve().parents[1]

class RecognitionTests(unittest.TestCase):
    def test_two_visible_occurrences_of_same_artwork_are_not_merged_into_one_slot(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard-closed.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        # A controlled replay of repeated artwork, as shared-art variants can
        # occupy separate slots. The unchanged badge must not prove completeness.
        image[1019:1107,570:658]=image[1019:1107,394:482].copy()
        run=ScreenReader().read(image)['run']
        occurrences=[r for r in run['relics']['icons'] if 'rogue_6_relic_fight_26' in r['candidates']]
        self.assertEqual(len(occurrences),2)
        self.assertEqual(len(run['relics']['icons']),4)

    def test_all_owned_cards_are_read_and_tactical_tools_are_separate_from_relics(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        # Hide only bar artwork: identification must also use the held panel's
        # exact names and descriptions, including cards beyond the leftmost one.
        image[1014:1120,300:1000]=0
        run=ScreenReader().read(image)['run']
        self.assertEqual(set(run['relics']['ids']),{'rogue_6_relic_cargo_1','rogue_6_relic_fight_26'})
        self.assertEqual(run['tactical_tools']['ids'],['rogue_6_active_tool_5'])

    def test_owned_non_square_vip_icon_is_not_distorted_by_template_resize(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-relic-multicard.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(set(observed['run']['relics']['ids']),
                         {'rogue_6_relic_cargo_1','rogue_6_relic_fight_26'})

    def test_map_resource_counters_distinguish_gold_parts_and_appraisal(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-map-closed.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        run=ScreenReader().read(image)['run']
        self.assertEqual(run['resources']['gold']['value'],10)
        self.assertEqual(run['resources']['parts_count']['value'],1)
        self.assertNotEqual(run['resources']['gold']['value'],6)  #总估价不是源石锭
        masked=image.copy();masked[45:120,1770:1855]=0
        self.assertNotIn('gold',ScreenReader().read(masked)['run']['resources'])

    def test_emergency_hire_marker_is_separate_from_elite_and_portrait(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-emergency-mechanist.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        run=ScreenReader().read(image)['run']
        members={m['id']:m for m in run['operators']}
        self.assertEqual(members['mechanist']['recruitment_kind'],'emergency_hire')
        self.assertEqual(members['char_2027_wang']['recruitment_kind'],'non_emergency')
        self.assertTrue(members['mechanist']['advanced'])
        self.assertTrue(members['char_2027_wang']['advanced'])
        self.assertFalse(members['char_151_myrtle']['advanced'])
        self.assertNotEqual(members['char_151_myrtle'].get('recruitment_kind'),'emergency_hire')
        self.assertNotEqual(members['char_133_mm'].get('recruitment_kind'),'emergency_hire')
        self.assertEqual(members['mechanist']['fields']['elite'],2)
        self.assertEqual(members['mechanist']['fields']['level'],90)
        self.assertEqual(members['mechanist']['skill_ranks'],{1:10,2:10,3:10})
        self.assertNotIn('potential',members['mechanist']['fields'])

    def test_owned_bar_identifies_relic_without_hovering_over_it(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-map-closed.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        relics=ScreenReader().read(image)['run']['relics']
        self.assertEqual(relics['ids'],['rogue_6_relic_legacy_52'])
        self.assertEqual(relics['count'],1)

    def test_run_roster_reads_members_without_reusing_account_levels(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-roster.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['page'],'run_roster')
        members=observed['run']['operators']
        self.assertEqual({m['name'] for m in members},{'机械师','望','桃金娘','梅'})
        self.assertEqual({m['name']:m['reference_level'] for m in members},
                         {'机械师':90,'望':80,'桃金娘':60,'梅':60})
        self.assertEqual({m['name']:m['fields']['elite'] for m in members},
                         {'机械师':2,'望':1,'桃金娘':1,'梅':1})
        self.assertTrue(all('trust' not in m['fields'] for m in members))

    def test_selected_run_operator_uses_current_panel_not_account_card(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/run-mechanist-selected.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['page'],'run_roster')
        self.assertEqual({m['name'] for m in observed['run']['operators']},{'机械师','真言','梅'})
        operator=next(m for m in observed['run']['operators'] if m['id']=='mechanist')
        self.assertEqual(operator['fields']['elite'],1)
        self.assertEqual(operator['fields']['level'],80)
        self.assertIsNone(operator['fields']['module_id'])
        self.assertEqual(operator['skill_ranks'],{1:7,2:7})
        self.assertNotIn('trust',operator['fields'])

    def test_owned_relic_tooltip_and_map_count_are_read_separately(self):
        def read(name):
            image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client'/name,dtype=np.uint8),cv2.IMREAD_COLOR)
            return ScreenReader().read(image)
        opened=read('run-relic-open.png')['run']
        self.assertEqual(opened['relics']['ids'],['rogue_6_relic_legacy_52'])
        self.assertIsNone(opened['relics']['count'])
        closed=read('run-map-closed.png')['run']
        self.assertEqual(closed['relics']['count'],1)
        self.assertEqual(closed['crew_count'],6)
        self.assertEqual(closed['relics']['ids'],['rogue_6_relic_legacy_52'])

    def test_module_page_identifies_its_owner_and_equipped_stage_without_inventing_training(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/module-mechanist.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['page'],'operator_module')
        operator=observed['operator']
        self.assertEqual(operator['id'],'mechanist')
        self.assertEqual(operator['fields']['module_id'],'uniequip_002_mcnist')
        self.assertEqual(operator['fields']['module_level'],3)
        self.assertNotIn('level',operator['fields'])
        self.assertIn('level',operator['missing_fields'])
        json.dumps(observed)

    def test_mechanist_overview_reads_equipped_module_and_mastery_two(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/operator-mechanist.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        operator=ScreenReader().read(image)['operator']
        self.assertEqual(operator['id'],'mechanist')
        self.assertEqual(operator['fields']['elite'],2)
        self.assertEqual(operator['fields']['level'],90)
        self.assertEqual(operator['fields']['potential'],6)
        self.assertEqual(operator['fields']['trust_display'],113)
        self.assertEqual(operator['fields']['module_id'],'uniequip_002_mcnist')
        self.assertEqual(operator['fields']['module_level'],3)
        self.assertEqual(operator['skill_ranks'],{1:10,2:9,3:10})
        self.assertTrue(operator['complete'])

    def test_silverash_alter_page_reads_identity_training_and_individual_masteries(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/operator-silverash.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['page'],'operator_detail')
        operator=observed['operator']
        self.assertEqual(operator['id'],'silverash')
        self.assertEqual(operator['fields']['level'],60)
        self.assertEqual(operator['fields']['elite'],2)
        self.assertEqual(operator['fields']['potential'],1)
        self.assertEqual(operator['fields']['trust_display'],200)
        self.assertEqual(operator['skill_ranks'],{1:7,2:7,3:10})
        self.assertEqual(operator['fields']['selected_skill'],3)
        # Regional refinement and subsequent frames must not consume the cached name index.
        again=ScreenReader().read(image)['operator']
        self.assertEqual(again['id'],'silverash')

    def test_animated_native_page_splits_adjacent_skill_sp_digits(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/operator-kaltsit-animated.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['operator']['fields']['level'],90)
        self.assertEqual(observed['operator']['skill_ranks'],{1:7,2:10,3:10})

    def test_native_operator_page_reads_training_and_matches_the_potential_icon(self):
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/operator-kaltsit.png',dtype=np.uint8),cv2.IMREAD_COLOR)
        observed=ScreenReader().read(image)
        self.assertEqual(observed['page'],'operator_detail')
        operator=observed['operator']
        self.assertEqual(operator['id'],'kaltsit')
        self.assertEqual(operator['fields']['level'],90)
        self.assertEqual(operator['fields']['elite'],2)
        self.assertEqual(operator['fields']['trust'],100)
        self.assertEqual(operator['fields']['trust_display'],200)
        self.assertEqual(operator['fields']['potential'],2)
        self.assertEqual(operator['skill_ranks'],{1:7,2:10,3:10})

    def test_native_selected_node_reveals_stage_without_filling_hidden_nodes(self):
        image = cv2.imdecode(np.fromfile(ROOT / 'samples/native-client/selected-battle-node.png', dtype=np.uint8), cv2.IMREAD_COLOR)
        observed = ScreenReader().read(image)
        self.assertEqual(observed['stage']['name'], '遗忘时间')
        self.assertEqual(observed['page'], 'node_detail')
        self.assertTrue(any(n['type'] == '未知的诡秘' for n in observed['nodes']))
        self.assertIsNone(observed['drop_estimate'])
        names = {e['name'] for v in observed['stage']['variants'] for e in v['preview']['possible_enemies']}
        self.assertIn('鸭爵',names)
