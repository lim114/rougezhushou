"""Current complete player output permits only source-supported note edits."""
from copy import deepcopy
import re,unittest
from rouge import node_catalog,choice_annotations
from rouge.player_node_information import node_information_text,_plain
from tests.player_presentation_legacy_307 import legacy_node_information_text

NEW_TEN=((8,0,1),(14,2,0),(15,2,0),(16,8,0),(17,6,0),(23,1,0),(23,6,0),(23,9,1),(23,11,0),(31,0,1))
OLD_WARNING='这段附加条件尚未完整解析；保留原文，不当作已满足。'
RESULT_NOTICE='这是选择后的结果说明，不作为选项出现条件；实际结果仍未知。'


def expected_note_edit(text,event,scene_key,choice_key,reference):
    """Literal edit inside one complete, independently addressed old choice block."""
    scene_index=next(i for i,s in enumerate(event['scenes']) if s['key']==scene_key)
    scene=event['scenes'][scene_index]
    choice_index=next(i for i,c in enumerate(scene['choices']) if c['key']==choice_key)
    def heading(i):
        choice=scene['choices'][i]
        label='选项' if choice['presentation_role']=='display_option_reference' else '说明参考（是否为实际按钮未确认）'
        return f'{label} {i+1}：'+_plain(choice['title'])
    start_token=f'【场景 {scene_index+1}】\n';assert text.count(start_token)==1
    start=text.index(start_token)
    next_token=f'【场景 {scene_index+2}】\n'
    end=text.index(next_token,start+len(start_token)) if scene_index+1<len(event['scenes']) else len(text)
    section=text[start:end]
    header=heading(choice_index)+'\n';assert section.count(header)==1
    block_start=section.index(header)
    block_end=section.index(heading(choice_index+1)+'\n',block_start+len(header)) if choice_index+1<len(scene['choices']) else len(section)
    old_block=section[block_start:block_end]
    old_line='条件原文：'+_plain(reference['text'])
    assert old_block.count(old_line)==1 and old_block.count(OLD_WARNING)==1
    # These exact additions are approved player wording, not a call to the
    # current rendering helper or a snapshot generated from its output.
    replacement='\n'.join(_plain(x) for x in
        [reference['label']+'（原文）：'+reference['text'],RESULT_NOTICE,*reference['limits']])
    new_block=old_block.replace(old_line,replacement,1)
    if OLD_WARNING+'\n' in new_block:new_block=new_block.replace(OLD_WARNING+'\n','',1)
    else:
        assert new_block.endswith('\n'+OLD_WARNING)
        new_block=new_block[:-len('\n'+OLD_WARNING)]
    updated=section[:block_start]+new_block+section[block_end:]
    return text[:start]+updated+text[end:]


class AnnotationPresentationPairs307(unittest.TestCase):
    def test_all_38_events_default_and_natural_have_only_exact_ten_approved_note_edits(self):
        data=choice_annotations.source_data();self.assertIsNotNone(data)
        actual_targets=tuple((int(eid.rsplit('_',1)[1]),int(sid.rsplit(':',1)[1]),int(cid.rsplit(':',1)[1]))
            for eid,sid,cid in choice_annotations.NEW_RESULT_IDENTITIES)
        self.assertEqual(actual_targets,NEW_TEN)
        notes={tuple(r[k] for k in ('event_id','scene_key','choice_key')):r for r in data['rows']}
        events=node_catalog._data()['events'];self.assertEqual(len(events),38)
        pairs=0;changed=set()
        for event in events:
            eid=event['id'];entry={'kind':'event','record':deepcopy(event)}
            for context in ({},{'floor':3,'entry_mode':'natural','node_type':event['node_types'][0] if event['node_types'] else None}):
                with self.subTest(event=eid,context=context):
                    before_entry=deepcopy(entry);before_context=deepcopy(context)
                    old=legacy_node_information_text(entry,context=context)
                    current=node_information_text(entry,context=context)
                    expected=old
                    for key in choice_annotations.NEW_RESULT_IDENTITIES:
                        if key[0]==eid:expected=expected_note_edit(expected,event,key[1],key[2],notes[key])
                    self.assertEqual(current,expected)
                    self.assertEqual(entry,before_entry);self.assertEqual(context,before_context)
                    if current!=old:changed.add(eid)
                    pairs+=1
        self.assertEqual(pairs,76)
        self.assertEqual(changed,{f'community_group_{g:03d}' for g in (8,14,15,16,17,23,31)})


if __name__=='__main__':unittest.main()
