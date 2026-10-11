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
    def test_173(self):
        n={'id':'n1','observed_type':'林间空地','remembered_type':'不期而遇'};old=deepcopy(n)
        r=c.node_events(n,floor=1);self.assertFalse(r['rows']);self.assertTrue(r['history_candidates']);self.assertEqual(n,old)
        r=c.node_events({'id':'n2','observed_type':'未知的诡秘','prediction':{'candidates':['不期而遇','失与得']}})
        self.assertIn('回滚文明',[e['title'] for e in r['rows']]);self.assertIn('桑尼的邀请',[e['title'] for e in r['rows']])
        self.assertEqual(len({e['id'] for e in r['rows']}),len(r['rows']))
    def test_173_unknown_includes_battles_functions_and_keeps_history(self):
        r=c.node_events({'observed_type':'未知的诡秘'})
        for t in ('作战','紧急作战','险路恶敌','羽瞰点','诡意行商'):
            self.assertIn(t,r['type_candidates'])
        r=c.node_events({'observed_type':'林间空地','remembered_type':'不期而遇'},floor=6)
        self.assertIn('桑尼的邀请',[e['title'] for e in r['history_candidates']])
        for n in ({'observed_type':3},{'prediction':['不期而遇']},{'content':[]}):
            with self.assertRaises(ValueError):c.node_events(n)
    def test_174(self):
        e=next(e for e in c.all_events()['rows'] if e['title']=='桑尼的邀请');r=c.event_details(e['id'])
        self.assertEqual(r['rows'][0]['game_scene_ids'],['scene_ro6_res1_enter'])
        self.assertIn('云兽玩偶',r['rows'][0]['description'])
        ids=[e['id'] for e in c.all_events()['rows'] if e['title']=='三重身'];self.assertEqual(len(set(ids)),3)
        with self.assertRaises(ValueError):c.event_details('三重身')
    def test_174_all_unmapped_original_records_queryable(self):
        r=c.original_references();self.assertEqual(len(r['rows']),108)
        self.assertEqual(len(c.original_references(record_type='scene')['rows']),45)
        self.assertEqual(len(c.original_references(record_type='choice')['rows']),63)
        for row in r['rows']:
            single=c.original_references(record_id=row['record_id'])['rows']
            self.assertEqual(len(single),1);self.assertFalse(single[0]['source_scene_link_verified'])
        x=c.original_references(title='行动奖励')['rows'];self.assertEqual(len(x),1)
        self.assertFalse(c.original_references()['natural_node_entry_verified'])
    def test_175(self):
        e=next(e for e in c.all_events()['rows'] if e['title']=='桑尼的邀请');r=c.choice_graph(e['id'])
        x=next(x for x in r['rows'] if x['title']=='帮它梳理绒毛')
        self.assertTrue(x['from'].endswith(':0'));self.assertTrue(x['to'].endswith(':1'))
        self.assertIsNone(x['server_option_available'])
        self.assertTrue(all(not x['game_exit_verified'] for x in r['unresolved']))
    def test_175_all_subchoices_preserved(self):
        e=next(e for e in c.all_events(include_indirect=True)['rows'] if e['title']=='安眠一隅')
        r=c.choice_graph(e['id']);sub=[x for x in r['rows'] if x['subchoice']]
        self.assertEqual(len(sub),9)
        valid={s['key'] for s in c.event_details(e['id'])['rows']}
        self.assertTrue(all(x['from'] in valid and x['to'] in valid for x in sub))
        self.assertTrue(all(x['branch_probability'] is None for x in sub))
