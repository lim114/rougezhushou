"""Exact source cards and manual scene reading, with no Qt or real-run state."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from rouge import resting_corner_results as model

ROOT=Path(__file__).resolve().parents[1]
EVENT='community_group_023'
CHOICES=[EVENT+suffix for suffix in (':scene:1:choice:0',':scene:6:choice:0',':scene:9:choice:1',':scene:11:choice:0')]


class RestingCornerResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/model.MANIFEST).read_text(encoding='utf-8'))

    def cards(self):return model.resting_result_cards(EVENT)

    def clone(self,target):
        for relative in [model.MANIFEST,*self.manifest['files']]:
            path=target/relative;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes((ROOT/relative).read_bytes())

    def test_four_exact_choices_and_three_same_titles_remain_independent(self):
        result=self.cards();self.assertEqual(result['status'],'documented_reference')
        self.assertEqual([card['choice_key'] for card in result['cards']],CHOICES)
        self.assertEqual([card['scene_number'] for card in result['cards']],[2,7,10,12])
        self.assertEqual([card['choice_title'] for card in result['cards']],['四处看看','触碰图案','触碰图案','触碰图案'])

    def test_documented_and_listed_counts_preserve_both_conflicts(self):
        cards=self.cards()['cards']
        self.assertEqual([(r['documented_count'],r['listed_branch_count'],r['count_matches']) for r in cards],
            [(3,3,True),(2,2,True),(2,1,False),(2,3,False)])
        self.assertEqual([r['conflict_notice'] for r in cards[:2]],['',''])
        self.assertIn('原注写2种，这里只列出1项',cards[2]['conflict_notice'])
        self.assertIn('原注写2种，这里只列出3项',cards[3]['conflict_notice'])

    def test_nine_local_branches_keep_literal_targets_without_pool_repair(self):
        cards=self.cards()['cards']
        self.assertEqual([[b['label'] for b in c['branches']] for c in cards],
            [['小狗','捕梦网','松鼠'],['果园','竞速比赛'],['动物泥偶'],['果园','竞速比赛','动物泥偶']])
        self.assertEqual([[b['target_scene_key'] for b in c['branches']] for c in cards],
            [[EVENT+':scene:2',EVENT+':scene:4',EVENT+':scene:5'],[EVENT+':scene:7',EVENT+':scene:3'],
             [EVENT+':scene:10'],[EVENT+':scene:7',EVENT+':scene:3',EVENT+':scene:10']])
        self.assertEqual(sum(len(c['branches']) for c in cards),9)

    def test_future_button_numbers_are_separate_alternatives_not_immediate_sum(self):
        cards=self.cards()['cards']
        self.assertEqual([[b['future_buttons'][0]['quantity_reference'] for b in c['branches']] for c in cards],
            [[20,15,1],[15,1],[99],[15,1,99]])
        self.assertEqual([[b['future_buttons'][0]['resource'] for b in c['branches']] for c in cards],
            [['hope','shield',None],['shield',None],['gold'],['shield',None,'gold']])
        for card in cards:
            self.assertIsNone(card['actual_reward']);self.assertNotIn('total_reward',card)
            for branch in card['branches']:
                self.assertIsNone(branch['actual_reward'])
                self.assertIsNone(branch['future_buttons'][0]['actual_granted'])

    def test_precious_processed_item_keeps_quality_text_and_unknown_pool(self):
        rows=[b['future_buttons'][0] for c in self.cards()['cards'] for b in c['branches'] if b['future_buttons'][0]['category_text']]
        self.assertEqual(len(rows),3)
        for row in rows:
            self.assertEqual(row['quantity_reference'],1);self.assertEqual(row['category_text'],'珍贵的加工品')
            self.assertIsNone(row['item_pool']);self.assertNotIn('rarity',row)
        self.assertEqual({row['choice_key'] for row in rows},{EVENT+':scene:3:choice:0',EVENT+':scene:5:choice:0'})

    def test_ninety_nine_gold_keeps_empty_original_ids_and_mismatch(self):
        card=self.cards()['cards'][2];button=card['branches'][0]['future_buttons'][0]
        self.assertEqual((button['quantity_reference'],button['resource']),(99,'gold'))
        self.assertEqual(button['game_choice_ids'],[]);self.assertEqual(button['game_match_basis'],'destination_mismatch')
        self.assertEqual(button['original_content_reference_ids'],[]);self.assertTrue(button['original_relation_mismatch'])
        self.assertFalse(button['original_entry_relation_verified'])
        scene=model.resting_result_scene(EVENT,card['choice_key'],card['branches'][0]['branch_id'])['scene']
        self.assertEqual(scene['choices'][0]['game_choice_ids'],[])
        self.assertEqual(scene['choices'][0]['destination_keys'],[EVENT+':scene:8'])

    def test_same_amounts_from_distinct_buttons_keep_their_complete_identities(self):
        cards=self.cards()['cards']
        shield=[b['future_buttons'][0] for c in cards for b in c['branches'] if b['future_buttons'][0]['resource']=='shield']
        self.assertEqual({tuple(row['game_choice_ids']) for row in shield},
            {('choice_ro6_surprise_3',),('choice_ro6_surprise_7',)})
        self.assertEqual({row['choice_key'] for row in shield},{EVENT+':scene:4:choice:0',EVENT+':scene:7:choice:0'})

    def test_six_target_scene_readings_return_exact_full_original_community_choices(self):
        data=model.source_data();expected={scene['key']:scene for scene in data['expected_event']['scenes']}
        seen=set()
        for card in self.cards()['cards']:
            for branch in card['branches']:
                result=model.resting_result_scene(EVENT,card['choice_key'],branch['branch_id'])
                self.assertEqual(result['status'],'documented_reference');self.assertTrue(result['source_valid'])
                scene=result['scene'];fixed=expected[branch['target_scene_key']]
                self.assertEqual(scene['key'],fixed['key']);self.assertEqual(scene['description'],fixed['description'])
                self.assertEqual(scene['choices'],fixed['choices']);self.assertEqual(scene['game_scene_ids'],fixed['game_scene_ids'])
                seen.add(scene['key'])
        self.assertEqual(seen,{EVENT+':scene:'+str(i) for i in (2,3,4,5,7,10)})

    def test_branch_from_another_card_is_rejected_even_with_the_same_destination(self):
        cards=self.cards()['cards'];from_other=cards[3]['branches'][0]
        self.assertEqual(cards[1]['branches'][0]['target_scene_key'],from_other['target_scene_key'])
        with self.assertRaises(ValueError):model.resting_result_scene(EVENT,cards[1]['choice_key'],from_other['branch_id'])

    def test_wrong_unknown_branch_never_falls_back_to_first_or_similar_name(self):
        for key in ('果园',CHOICES[1]+':sub:9',EVENT+':scene:7',CHOICES[1]+':main:0'):
            with self.subTest(key=key),self.assertRaises(ValueError):model.resting_result_scene(EVENT,CHOICES[1],key)

    def test_wrong_event_or_typed_subclass_skips_source_reads(self):
        class Text(str):pass
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Should not read source')):
            for value in ('other',False,23,{},None,Text(EVENT)):
                self.assertIsNone(model.resting_result_cards(value))
                self.assertIsNone(model.resting_result_scene(value,CHOICES[0],CHOICES[0]+':sub:0'))

    def test_invalid_choice_or_branch_types_are_not_coerced_or_localized_by_title(self):
        class Text(str):pass
        with patch.object(model,'_validated_packet',side_effect=AssertionError('Should validate identity first')):
            for choice in ('触碰图案',EVENT+':scene:9:choice:0',False,Text(CHOICES[1])):
                with self.subTest(choice=choice),self.assertRaises(ValueError):model.resting_result_scene(EVENT,choice,'anything')
            for branch in (False,1,{},Text(CHOICES[0]+':sub:0')):
                with self.subTest(branch=branch),self.assertRaises(ValueError):model.resting_result_scene(EVENT,CHOICES[0],branch)

    def test_all_actual_results_and_full_pool_or_server_claims_stay_unknown(self):
        result=self.cards()
        self.assertFalse(result['full_actual_pool_known']);self.assertFalse(result['current_server_verified'])
        for key in ('actual_transition','actual_selected_branch','actual_reward','actual_selectable'):self.assertIsNone(result[key])
        for card in result['cards']:
            self.assertFalse(card['source_scene_link_verified']);self.assertFalse(card['full_actual_pool_known'])
            for key in ('actual_selected_branch','actual_reward','actual_selectable'):self.assertIsNone(card[key])
            for branch in card['branches']:self.assertIsNone(branch['actual_transition'])

    def test_result_and_scene_nested_mutation_do_not_pollute_following_reads(self):
        cards=self.cards();cards['cards'][0]['branches'][0]['future_buttons'][0]['quantity_reference']=999
        cards['sources']['community_documents'][0]['revision']='changed'
        scene=model.resting_result_scene(EVENT,CHOICES[0],CHOICES[0]+':sub:0')
        scene['scene']['choices'][0]['game_choice_ids'].append('changed')
        again=self.cards();self.assertEqual(again['cards'][0]['branches'][0]['future_buttons'][0]['quantity_reference'],20)
        self.assertEqual(again['sources']['community_documents'][0]['revision'],'427904')
        self.assertEqual(model.resting_result_scene(EVENT,CHOICES[0],CHOICES[0]+':sub:0')['scene']['choices'][0]['game_choice_ids'],['choice_ro6_surprise_2'])

    def test_source_data_returns_an_independent_snapshot(self):
        data=model.source_data();before=deepcopy(data)
        data['cards'].clear();data['scenes'].clear();data['expected_event']['title']='changed'
        self.assertEqual(model.source_data(),before)

    def test_warm_call_rehashes_every_pinned_file_and_rejects_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);self.clone(target)
            with patch.object(model,'ROOT',target):
                self.assertEqual(self.cards()['status'],'documented_reference')
                for relative in self.manifest['files']:
                    with self.subTest(relative=relative):
                        path=target/relative;before=path.read_bytes();path.write_bytes(before+b' ')
                        result=self.cards();self.assertEqual(result['status'],'unknown');self.assertEqual(result['cards'],[])
                        scene=model.resting_result_scene(EVENT,CHOICES[0],CHOICES[0]+':sub:0')
                        self.assertEqual(scene['status'],'unknown');self.assertIsNone(scene['scene'])
                        path.write_bytes(before);self.assertEqual(self.cards()['status'],'documented_reference')

    def test_missing_current_catalog_does_not_reuse_a_warm_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);self.clone(target)
            with patch.object(model,'ROOT',target):
                self.assertTrue(self.cards()['source_valid'])
                (target/'rouge/data/node-catalog.json').unlink()
                self.assertIsNone(model.source_data())
                self.assertEqual(self.cards()['status'],'unknown')

    def test_manifest_tamper_cannot_replace_the_fixed_packet_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory);self.clone(target)
            with patch.object(model,'ROOT',target):
                self.assertTrue(self.cards()['source_valid'])
                path=target/model.MANIFEST;manifest=json.loads(path.read_text(encoding='utf-8'))
                manifest['files'].pop('rouge/data/node-catalog.json');path.write_text(json.dumps(manifest),encoding='utf-8')
                self.assertEqual(self.cards()['status'],'unknown')

    def test_runtime_does_not_read_full_game_table_or_write_any_file(self):
        read=Path.read_bytes;reads=[]
        def observed(path):reads.append(str(path));return read(path)
        with patch.object(Path,'read_bytes',observed),patch.object(Path,'write_bytes',side_effect=AssertionError('Read only')):
            self.assertTrue(self.cards()['source_valid'])
            self.assertTrue(model.resting_result_scene(EVENT,CHOICES[0],CHOICES[0]+':sub:0')['source_valid'])
        self.assertTrue(any(path.endswith('node-catalog.json') for path in reads))
        self.assertFalse(any(path.endswith('roguelike_topic_table.json') for path in reads))

    def test_public_apis_offer_no_data_source_or_evaluator_override(self):
        with self.assertRaises(TypeError):model.resting_result_cards(EVENT,data={})
        with self.assertRaises(TypeError):model.resting_result_cards(EVENT,source={})
        with self.assertRaises(TypeError):model.resting_result_scene(EVENT,CHOICES[0],CHOICES[0]+':sub:0',evaluator=lambda:True)

    def test_selected_originals_preserve_null_random_targets_and_gold_conflict(self):
        path=ROOT/'research/p3-resting-results-293/original-records.json';original=json.loads(path.read_text(encoding='utf-8'))['records']
        self.assertEqual((len(original['choices']),len(original['choiceScenes'])),(12,12))
        for suffix in (5,6,9,11):
            row=original['choices']['choice_ro6_surprise_'+str(suffix)]
            self.assertEqual(row['type'],'NEXT_PROB');self.assertIsNone(row['nextSceneId'])
        self.assertEqual(original['choices']['choice_ro6_surprise_12']['nextSceneId'],'scene_ro6_surprise_1')
        self.assertEqual(model.source_data()['expected_event']['scenes'][10]['choices'][0]['game_choice_ids'],[])

    def test_source_readback_preserves_the_known_punctuation_difference_without_origin_claim(self):
        path=ROOT/'research/p3-resting-results-293/extraction.json'
        rows=json.loads(path.read_text(encoding='utf-8'))['original_scene_candidate_comparisons']
        differences=[row for row in rows if not row['normalized_full_text_equal']]
        self.assertEqual(len(differences),1)
        self.assertEqual((differences[0]['community_scene_key'],differences[0]['original_scene_id']),
            (EVENT+':scene:2','scene_ro6_surprise_2'))
        self.assertIn('蝴蝶......',differences[0]['original_description'])
        self.assertIn('蝴蝶……',differences[0]['community_description'])
        self.assertTrue(differences[0]['known_punctuation_variant'])
        self.assertTrue(all(row['source_scene_entry_verified'] is False for row in rows))


if __name__=='__main__':unittest.main()
