from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge.player_parts import part_rows,box_status
from rouge.player_tools import tool_rows

class PartAndToolTests(unittest.TestCase):
    def test_three_exact_game_categories_cover_every_fixed_part_once(self):
        rows=part_rows();self.assertEqual(len(rows),44)
        self.assertEqual({r['kind_name']for r in rows},{'加工品','自然物','概念体'})
        split=[row for kind in('MOVE','GOODS','PASSIVE')for row in part_rows(kind=kind)]
        self.assertEqual({r['id']for r in split},{r['id']for r in rows});self.assertEqual(len(split),len(rows))

    def test_count_does_not_fabricate_members_or_remaining_uses(self):
        text=box_status({'resources':{'parts_count':{'value':2}}});self.assertIn('2件',text);self.assertIn('具体成员与剩余使用次数未完整读取',text)
        for value in(True,None,'2',2.0,-1):self.assertIn('尚未读到',box_status({'resources':{'parts_count':{'value':value}}}))
        self.assertIn('零件0件',box_status({'resources':{'parts_count':{'value':0}}}))

    def test_part_search_and_source_failure_never_use_old_catalogue(self):
        rows=part_rows('轮');self.assertTrue(rows);self.assertTrue(all('轮'in(r['name']+r['usage'])for r in rows))
        with patch('rouge.player_parts.source.packet',return_value=None):self.assertIsNone(part_rows())

    def test_tactical_tools_are_not_relics_and_unconfirmed_is_not_owned(self):
        known=tool_rows({},held_only=False);self.assertTrue(known)
        identity=known[0]['id'];other=known[1]['id'];state={'tactical_tools':{identity:{'held':True},other:{'held':'true'}}};before=deepcopy(state)
        self.assertEqual([r['id']for r in tool_rows(state)],[identity]);self.assertEqual(state,before)
        state['tactical_tools'][identity]['held']=False;self.assertEqual(tool_rows(state),[])
        with patch('rouge.player_tools.expansion_reference.packet',return_value=None):self.assertIsNone(tool_rows(state))

if __name__=='__main__':unittest.main()
