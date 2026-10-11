import unittest
from copy import deepcopy
from rouge import node_catalog as c

class NodeCatalogTests(unittest.TestCase):
    def test_171(self):
        r=c.all_events();self.assertEqual(len(r['rows']),37)
        self.assertEqual(sum(e['title']=='三重身' for e in r['rows']),3)
        self.assertNotIn('安眠一隅',[e['title'] for e in r['rows']])
        self.assertEqual(len(c.all_events(include_indirect=True)['rows']),38)
        self.assertFalse(r['scope']['all_server_events_verified'])
        self.assertEqual(r['original_uncataloged'][0]['title'],'行动奖励')
    def test_171_category_coverage(self):
        r=c.all_events()
        for t in ('作战','紧急作战','险路恶敌','羽瞰点','诡意行商','林间空地'):
            self.assertIn(t,r['known_node_types'])
        self.assertFalse(r['scope']['all_original_scene_ids_classified'])
    def test_171_pinned_source_revision(self):
        r=c.all_events();source=r['sources']['cached_community_catalog']
        self.assertIn('oldid=427904',source['url']);self.assertEqual(source['revision'],'427904')
        self.assertEqual(r['scope']['parsed_source_revision'],'427904')
    def test_172(self):
        a=c.event_candidates('不期而遇',floor=1);b=c.event_candidates('不期而遇',floor=3)
        self.assertIn('桑尼的邀请',[e['title'] for e in a['rows']])
        self.assertNotIn('桑尼的邀请',[e['title'] for e in b['rows']])
        self.assertIn('桑尼的邀请',[e['title'] for e in c.event_candidates('不期而遇',floor=3,special_region=True)['rows']])
        self.assertTrue(c.event_candidates('先行一步',floor=6)['rows'])
        with self.assertRaises(ValueError):c.event_candidates(floor=True)
    def test_172_indirect_not_main_floor_filtered(self):
        r=c.event_candidates(floor=6,include_indirect=True)
        self.assertIn('安眠一隅',[e['title'] for e in r['rows']])
        with self.assertRaises(ValueError):c.event_candidates(special_region=1)
