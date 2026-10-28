import unittest
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from rouge import player_map_reference as m

class MapReferenceTests(unittest.TestCase):
 def test_observation_overrides_template_and_prediction(self):
  n={'observed_type':'林间空地','template_type':'作战','prediction':{'candidates':['诡意行商']}}
  self.assertEqual(m.candidate_types(n),('林间空地',));self.assertEqual(m.type_match(n,'诡意行商'),'excluded')
 def test_passed_type_is_history_not_new_candidate(self):
  n={'observed_type':'林间空地','remembered_type':'诡意行商'}
  self.assertEqual(m.type_match(n,'诡意行商'),'history');self.assertIsNone(m.overlay_rows({'nodes':[{'id':'a',**n}]},'诡意行商')['a']['frequency'])
 def test_fixed_node_does_not_get_a_probability(self):
  n={'id':'a','template_type':'羽瞰点','distance':2}
  row=m.overlay_rows({'zone_id':'zone_1','nodes':[n]},'羽瞰点')['a']
  self.assertEqual(row['match'],'template');self.assertIsNone(row['frequency'])
 def test_uncertain_without_candidates_stays_unconfirmed(self):
  self.assertEqual(m.candidate_types({'observed_type':'未知的诡秘'}),())
  self.assertEqual(m.type_match({},'诡意行商'),'unconfirmed')
 def test_single_candidate_remains_candidate(self):
  self.assertEqual(m.type_match({'prediction':{'candidates':['诡意行商']}},'诡意行商'),'candidate')
 def test_deduplicate_candidates_without_reordering(self):
  self.assertEqual(m.candidate_types({'prediction':{'candidates':['不期而遇','诡意行商','不期而遇']}}),('不期而遇','诡意行商'))
 def test_candidate_filter_does_not_renormalize_historical_counts(self):
  n={'id':'a','distance':2,'observed_type':'未知的诡秘','prediction':{'candidates':['诡意行商']}}
  graph={'zone_id':'zone_1','nodes':[n]};before=deepcopy(graph)
  row=m.overlay_rows(graph,'诡意行商')['a']['frequency'];self.assertIsNotNone(row)
  original=next(r for r in m.historical_rows('zone_1',2)if r['name']=='诡意行商')
  self.assertEqual(row,original);self.assertLess(row['frequency'],1);self.assertEqual(graph,before)
 def test_known_observation_has_no_redundant_rate(self):
  graph={'zone_id':'zone_1','nodes':[{'id':'a','distance':2,'observed_type':'诡意行商'}]}
  self.assertEqual(m.overlay_rows(graph,'诡意行商')['a'],{'match':'observed','frequency':None})
 def test_other_types_are_excluded_from_highlight(self):
  self.assertEqual(m.type_match({'prediction':{'candidates':['作战']}},'诡意行商'),'excluded')
 def test_unknown_sixth_or_special_region_not_first_floor_fallback(self):
  for zone in('zone_6','treehole','zone_4_extra',None):self.assertEqual(m.historical_rows(zone,2),())
 def test_no_sample_is_unknown(self):self.assertIsNone(m.historical_frequency({'zone_id':'zone_1'},{'distance':100},'诡意行商'))
 def test_boolean_distance_is_not_integer_sample_after_cache_hit(self):
  m.historical_rows('zone_1',1);self.assertEqual(m.historical_rows('zone_1',True),())
 def test_artwork_all_exact_bytes_and_no_missing_files(self):
  manifest=m.event_art_manifest();self.assertEqual(len(manifest['sources']),25)
  for row in manifest['sources'].values():self.assertEqual(sha256((Path(__file__).resolve().parents[1]/row['file']).read_bytes()).hexdigest(),row['sha256'])
 def test_unknown_event_does_not_borrow_an_image(self):self.assertIsNone(m.event_picture('made-up-event'))
 def test_exact_event_mapping_has_real_images(self):
  from rouge.node_catalog import _data
  paths=[m.event_picture(row['id'])for row in _data()['events']]
  self.assertTrue(any(path and path.is_file()for path in paths))
 def test_no_candidate_dossier_is_not_global_directory(self):
  self.assertIsNone(m.node_dossier({'nodes':[{'id':'a','observed_type':'未知的诡秘'}]},'a',{}))
 def test_unrelated_fixed_battle_has_no_event_cards(self):
  g={'zone_id':'zone_1','nodes':[{'id':'a','row':0,'col':0,'template_type':'作战'}]};before=deepcopy(g)
  d=m.node_dossier(g,'a',{});self.assertEqual(d['rows'],[]);self.assertTrue(d['battle_rows']);self.assertEqual(g,before)
