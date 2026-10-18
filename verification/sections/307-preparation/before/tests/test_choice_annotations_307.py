"""Necessary semantic/legacy boundaries, without game or private state."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch

from rouge import choice_annotations as model,event_planning,node_catalog
from rouge.player_node_information import node_information_text

KEY=('community_group_008','community_group_008:scene:0','community_group_008:scene:0:choice:1')


class ChoiceAnnotation307Tests(unittest.TestCase):
    def test_01_all_sixteen_exact_notes_are_four_requirements_twelve_results(self):
        data=model.source_data();self.assertIsNotNone(data)
        self.assertEqual(len(data['rows']),16)
        self.assertEqual(sum(r['role']=='preselection_requirement'for r in data['rows']),4)
        self.assertEqual(sum(r['role']=='selection_result'for r in data['rows']),12)
        self.assertEqual(len(model.NEW_RESULT_IDENTITIES),10)
        for row in data['rows']:
            key=tuple(row[k]for k in('event_id','scene_key','choice_key'))
            result=model.choice_reference(*key)
            self.assertEqual(result['reference'],row)
            self.assertEqual([s['revision']for s in row['source_refs']],['427904','440271'])
            self.assertTrue(all(s['field']=='choose.desc2'and s['source_text']==row['text']for s in row['source_refs']))
            self.assertIsNone(result['actual_result']);self.assertIsNone(result['actual_selectable'])

    def test_02_complete_legacy_190_scenes_233_choices_stay_equal_except_exact_metadata_and_ten_notes(self):
        scenes=choices=changed=0
        for event in node_catalog._data()['events']:
            for scene in event['scenes']:
                old=event_planning.choice_eligibility(event['id'],scene['key'])
                new=model.classified_choice_eligibility(event['id'],scene['key'])
                normalized=deepcopy(new);scenes+=1
                for row,prior in zip(normalized['rows'],old['rows']):
                    choices+=1;key=(event['id'],scene['key'],row['choice_key'])
                    if key in model.IDENTITIES:
                        self.assertTrue(row['annotation_source_valid'])
                        for field in('annotation_reference','annotation_role','annotation_source_valid'):row.pop(field)
                    else:self.assertNotIn('annotation_reference',row)
                    if key in model.NEW_RESULT_IDENTITIES:
                        self.assertIsNone(row['unparsed_condition_text'])
                        self.assertEqual(prior['unparsed_condition_text'],prior['conditional_text'])
                        row['unparsed_condition_text']=prior['unparsed_condition_text'];changed+=1
                self.assertEqual(normalized,old)
                self.assertEqual(event_planning.choice_eligibility(event['id'],scene['key']),old)
        self.assertEqual((scenes,choices,changed),(190,233,10))

    def test_03_resources_adapter_changes_only_nested_reading_metadata(self):
        old=event_planning.choice_resources(KEY[0],KEY[1],{'gold':51})
        result=model.classified_choice_resources(KEY[0],KEY[1],{'gold':51})
        for row,prior in zip(result['rows'],old['rows']):
            qualified=row['choice_eligibility']
            for field in('annotation_reference','annotation_role','annotation_source_valid'):qualified.pop(field)
            qualified['unparsed_condition_text']=prior['choice_eligibility']['unparsed_condition_text']
        self.assertEqual(result,old)

    def test_04_every_runtime_source_failure_clears_role_and_preserves_original_text_then_recovers(self):
        manifest=json.loads((model.ROOT/model.MANIFEST).read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory()as temporary:
            root=Path(temporary)
            for name in(model.MANIFEST,*manifest['runtime_files']):
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((model.ROOT/name).read_bytes())
            with patch.object(model,'ROOT',root):
                self.assertTrue(model.choice_reference(*KEY)['source_valid'])
                for name in(model.MANIFEST,*manifest['runtime_files']):
                    target=root/name;raw=target.read_bytes();target.write_bytes(raw+b' ')
                    try:
                        result=model.choice_reference(*KEY)
                        self.assertFalse(result['source_valid']);self.assertIsNone(result['role']);self.assertIsNone(result['reference'])
                        qualified=next(r for r in model.classified_choice_eligibility(*KEY[:2])['rows']if r['choice_key']==KEY[2])
                        self.assertEqual(qualified['unparsed_condition_text'],qualified['conditional_text'])
                        lines=model.reading_lines(result,qualified['conditional_text'])
                        self.assertTrue(lines[0].startswith('附注原文（类型待核对）：'))
                    finally:target.write_bytes(raw)
                    self.assertTrue(model.choice_reference(*KEY)['source_valid'])

    def test_05_full_bound_event_scene_choice_mutations_and_mutable_catalog_are_rejected(self):
        event=deepcopy(node_catalog._event(KEY[0]));scene=deepcopy(node_catalog._scene(*KEY[:2]));choice=deepcopy(scene['choices'][1])
        for name,value in(('event',event),('scene',scene),('choice',choice)):
            bad=deepcopy(value);bad['test_injected_field']=True
            result=model.choice_reference(*KEY,**{name:bad})
            self.assertFalse(result['source_valid']);self.assertIsNone(result['role'])
        changed=deepcopy(node_catalog._data());changed['events'][8]['scenes'][0]['description']+=' changed'
        with patch.object(node_catalog,'_data',return_value=changed):
            self.assertFalse(model.choice_reference(*KEY)['source_valid'])

    def test_06_no_io_for_unrelated_identity_and_one_source_read_per_scene(self):
        with patch.object(model,'_packet',side_effect=AssertionError('unrelated source read')):
            self.assertIsNone(model.choice_reference('community_group_008',KEY[1],KEY[2]+'wrong'))
            self.assertEqual(model.scene_references('community_group_000','community_group_000:scene:0'),{})
        with patch.object(model,'_packet',wraps=model._packet)as source:
            values=model.scene_references(*KEY[:2]);self.assertEqual(len(values),2);self.assertEqual(source.call_count,1)

    def test_07_returned_data_cannot_pollute_fresh_source_or_legacy(self):
        first=model.choice_reference(*KEY);first['reference']['catalog_choice']['title']='changed'
        first['reference']['source_refs'].clear()
        self.assertEqual(model.choice_reference(*KEY)['reference']['catalog_choice']['title'],'和猎狗战斗到底')
        result=model.classified_choice_eligibility(*KEY[:2]);result['rows'][0]['checks'].clear()
        self.assertTrue(event_planning.choice_eligibility(*KEY[:2])['rows'][0]['checks'])

    def test_08_true_requirements_keep_three_state_matching_and_no_actual_selection(self):
        for identity in model.IDENTITIES:
            reference=model.choice_reference(*identity)
            if reference['role']!='preselection_requirement':continue
            old=event_planning.choice_eligibility(*identity[:2])
            new=model.classified_choice_eligibility(*identity[:2])
            row=next(r for r in new['rows']if r['choice_key']==identity[2])
            prior=next(r for r in old['rows']if r['choice_key']==identity[2])
            self.assertEqual(row['parsed_special_requirements'],prior['parsed_special_requirements'])
            self.assertIsNone(row['actual_selectable'])
        eid='community_group_015';sid=eid+':scene:0';cid=sid+':choice:1'
        for gold,expected in((None,None),(50,False),(51,True)):
            row=next(r for r in model.classified_choice_eligibility(eid,sid,{'gold':gold})['rows']if r['choice_key']==cid)
            check=next(c for c in row['checks']if c['key']=='gold_strictly_greater')
            self.assertIs(check['matches'],expected)

    def test_09_old_recruitment_and_movement_source_failure_is_not_masked_by_roles(self):
        for identity,module,name in((model.IDENTITIES[7],event_planning.choice_recruitment_results,'choice_reference'),
                                     (model.IDENTITIES[8],event_planning.peace_guardian_results,'choice_result_reference')):
            unavailable={'status':'source_unavailable','source_valid':False,'annotation_role':None}
            with patch.object(module,name,return_value=unavailable):
                row=next(r for r in model.classified_choice_eligibility(*identity[:2])['rows']if r['choice_key']==identity[2])
                self.assertEqual(row['annotation_role'],'selection_result')
                self.assertEqual(row['unparsed_condition_text'],row['conditional_text'])

    def test_10_player_labels_keep_true_conditions_and_reward_count_conflicts(self):
        for identity in model.NEW_RESULT_IDENTITIES:
            reference=model.choice_reference(*identity)
            lines=model.reading_lines(reference,reference['reference']['text'])
            self.assertNotIn('出现前条件',lines[0]);self.assertIn('不作为选项出现条件','\n'.join(lines))
        for index,count in((11,1),(12,3)):
            reference=model.choice_reference(*model.IDENTITIES[index]);lines='\n'.join(model.reading_lines(reference,reference['reference']['text']))
            self.assertIn('数量不一致',lines);self.assertIn('明确列出'+str(count)+'种后续',lines)
        event=node_catalog._event('community_group_008')
        text=node_information_text({'kind':'event','record':event})
        self.assertIn('选择后可能的战斗（原文）',text);self.assertIn('条件原文：仅在持有笼控器时出现',text)
        self.assertNotIn('这段附加条件尚未完整解析',text)


if __name__=='__main__':unittest.main()
