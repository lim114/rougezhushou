import unittest
from copy import deepcopy
from rouge.player_map_find import coverage,rows
from rouge.player_map_acceptance import fixtures
class Coverage(unittest.TestCase):
 def test_disjoint_coverage_never_counts_candidates_as_confirmed(self):
  gs,*_=fixtures();g={r['zone_id']:r for r in gs};before=deepcopy(g);c=coverage(g);self.assertEqual(sum(c.values()),sum(len(r['nodes'])for r in gs));self.assertEqual(c['read'],2);self.assertGreater(c['unknown'],0);self.assertEqual(g,before)
 def test_filter_only_changes_result_membership(self):
  gs,*_=fixtures();g={r['zone_id']:r for r in gs};allrows=rows(g);groups=[rows(g,evidence=e)for e in('read','fixed','unknown')];self.assertEqual(set(r['key']for r in allrows),set(r['key']for group in groups for r in group));self.assertTrue(all(r['evidence']=='unknown'for r in groups[-1]));self.assertEqual(coverage({}),{'read':0,'fixed':0,'unknown':0})
 def test_passed_node_keeps_direct_bound_remembered_title_searchable(self):
  gs,*_=fixtures();n=next(n for n in gs[0]['nodes']if n.get('remembered_type'));n['remembered_content']={'source':'same_frame_selected_node','title':'历史直接绑定标题'};self.assertEqual(rows({gs[0]['zone_id']:gs[0]},'历史直接绑定标题')[0]['key'][-1],n['id'])
if __name__=='__main__':unittest.main()
