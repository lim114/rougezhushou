import unittest
from copy import deepcopy
from rouge.player_context import recent_content
class Context(unittest.TestCase):
 def test_no_claim_when_missing(self):self.assertEqual(recent_content({}),'')
 def test_retained_content_not_overwritten(self):
  state={'last_node_content':{'title':'遗忘时间','location':None}};before=deepcopy(state)
  self.assertEqual(recent_content(state),'遗忘时间');self.assertEqual(state,before)
 def test_invalid_title(self):self.assertEqual(recent_content({'last_node_content':{'title':None}}),'')
