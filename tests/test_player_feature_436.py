import unittest
from types import SimpleNamespace
from rouge.player_source_map import targets

class SourceMap(unittest.TestCase):
 def test_requires_enum_and_exact_name_not_event_label(self):
  index=SimpleNamespace(pools=lambda v,i:[{'id':'pool','nodeBindings':[{'nodeType':'BATTLE_NORMAL','nodeName':'作战'},{'nodeType':'source','nodeName':'不期而遇'},{'nodeType':'BATTLE_NORMAL','nodeName':'错误名称'},None]}])
  self.assertEqual(targets(index,'base','item','pool'),['作战']);self.assertEqual(targets(index,'base','item','other'),[])
 def test_public_entries_with_no_enum_are_not_guessed(self):
  self.assertEqual(targets(None,'base','item','pool'),[])

if __name__=='__main__':unittest.main()
