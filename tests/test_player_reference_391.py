import unittest
from copy import deepcopy
from rouge import public_archive as m
from scripts import update_cloud_index as ci
class PublicReferenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.data=m.load()
 def test_distinct_version_memberships(self):
  self.assertEqual(set(self.data['versions']),{'base','dlc1'});self.assertNotEqual(len(self.data['versions']['base']),len(self.data['versions']['dlc1']))
 def test_search_by_member_or_effect(self):
  rows=m.pool_rows(self.data,'dlc1','报废轮子');self.assertTrue(rows);self.assertTrue(all(any(self.data['items'].get(i,{}).get('name')=='报废轮子'for i in r['collectibles'])for r in rows))
 def test_observed_numerator_denominator(self):
  rows=self.data['versions']['dlc1'];pool=next(r for r in rows if r.get('observedDistribution',{}).get('interpretation')=='observedFrequencyOnly')
  d=pool['observedDistribution'];members=m.members(self.data,pool,d);self.assertTrue(any(r['rate']is not None for r in members))
  for row in members:
   if row['rate']is not None:self.assertEqual(row['rate'],row['count']/row['total'])
 def test_summary_and_overlapping_sources_not_added(self):
  pool=next(r for r in self.data['versions']['base']if len(m.distributions(r))>1);copy=deepcopy(pool)
  rows=m.distributions(pool);self.assertEqual(pool,copy);self.assertEqual(rows[0][0],'summary');self.assertGreater(len(rows),1)
 def test_game_formatting_not_exposed_in_effects(self):
  pool=next(r for r in self.data['versions']['dlc1']if'rogue_6_scrap_M_01'in r['collectibles'])
  rows=m.members(self.data,pool);self.assertTrue(any('报废轮子'==r['name']for r in rows));self.assertTrue(all('<color='not in r['effect']for r in rows))
 def test_stratified_or_missing_statistics_unknown(self):
  pool=self.data['versions']['dlc1'][0]
  self.assertTrue(all(r['rate']is None for r in m.members(self.data,pool)))
  self.assertTrue(all(r['rate']is None for r in m.members(self.data,pool,{'interpretation':'stratifiedObservations'})))
 def test_bad_reported_ratio_unknown(self):
  pool={'collectibles':['a']};d={'interpretation':'observedFrequencyOnly','totalOccurrenceCount':10,'members':[{'itemId':'a','occurrenceCount':2,'occurrenceRate':.7}]}
  self.assertIsNone(m.members({'items':{}},pool,d)[0]['rate'])
 def test_treehole_entrance_not_assumed(self):
  self.assertEqual(m.event_rows(self.data,1,True),[]);self.assertTrue(m.event_rows(self.data,3,True))
 def test_floor_specific_events_and_conditional_requirements(self):
  a=m.event_rows(self.data,1);b=m.event_rows(self.data,3);self.assertNotEqual({r['id']for r in a},{r['id']for r in b})
  self.assertTrue(any('仅在'in r['condition']for r in a));self.assertTrue(all(r['actual_eligible']is None for r in a+b))
 def test_unknown_version_not_replaced_by_default(self):self.assertEqual(m.pool_rows(self.data,'dlc2'),[])
 def test_duplicates_rejected(self):
  d=deepcopy(self.data);d['versions']['base'].append(d['versions']['base'][0])
  with self.assertRaises(ValueError):m.validate(d)

class MapPresentationTests(unittest.TestCase):
 def test_single_candidate_not_revealed(self):
  from rouge.player_map import node_style
  self.assertEqual(node_style({'prediction':{'candidates':['诡意行商']}}),(None,'类型未确认','unknown'))
 def test_passed_node_keeps_original_record(self):
  from rouge.player_map import node_style
  self.assertEqual(node_style({'observed_type':'林间空地','remembered_type':'不期而遇'}),('林间空地','原为不期而遇','history'))
 def test_fixed_icon_distinguished_from_observation(self):
  from rouge.player_map import node_style
  self.assertEqual(node_style({'template_type':'羽瞰点'})[2],'template')
 def test_map_art_pins_and_sprite_rectangles(self):
  from rouge.player_map import ART,art_manifest,ICONS
  from hashlib import sha256
  data=art_manifest()
  for row in data['sources']:self.assertEqual(sha256((ART/row['file'].split('/')[-1]).read_bytes()).hexdigest(),row['sha256'])
  self.assertTrue(set(ICONS.values())<=set(data['sprites']))
  for row in data['sprites'].values():
   self.assertGreater(row['width'],0);self.assertLessEqual(row['x']+row['width'],row['atlasWidth']);self.assertLessEqual(row['y']+row['height'],row['atlasHeight'])

 def test_fixed_battle_does_not_list_unrelated_events(self):
  from rouge.player_map import dossier_graph
  from rouge.node_catalog import node_dossier
  g={'nodes':[{'id':'a','row':0,'col':0,'template_type':'作战'}]};copy=deepcopy(g)
  query=dossier_graph(g);d=node_dossier(query,'a',floor=1)
  self.assertEqual(g,copy);self.assertEqual(d['type_candidates'],['作战']);self.assertEqual(d['rows'],[]);self.assertTrue(d['battle_rows'])
  self.assertNotIn('observed_type',query['nodes'][0])
 def test_observed_change_overrides_original_template(self):
  from rouge.player_map import dossier_graph
  g={'nodes':[{'observed_type':'林间空地','template_type':'作战'}]}
  self.assertNotIn('prediction',dossier_graph(g)['nodes'][0])
