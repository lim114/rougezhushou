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
    def test_176(self):
        e=next(e for e in c.all_events()['rows'] if e['title']=='桑尼的邀请')
        r=c.event_paths(e['id']);self.assertGreaterEqual(len(r['rows']),2)
        self.assertTrue(any(x['scenes'][-1].endswith(':1') for x in r['rows']))
        one=c.event_paths(e['id'],max_paths=1);self.assertTrue(one['truncated'])
        self.assertFalse(one['game_execution_verified'])
    def test_176_no_navigation_depth_and_cycle_limits(self):
        from unittest.mock import patch
        e=next(e for e in c.all_events()['rows'] if e['title']=='黑诞')
        rows=c.event_paths(e['id'])['rows'];used={k for row in rows for k in row['choices']}
        self.assertIn(e['entry'][0]+':choice:1',used)
        e=next(e for e in c.all_events()['rows'] if e['title']=='被歌颂的影子')
        limited=c.event_paths(e['id'],max_steps=1)
        self.assertTrue(limited['truncated']);self.assertIn('max_steps',limited['truncation_reasons'])
        g={'rows':[{'from':'a','to':'a','choice_id':'x'+str(i)} for i in range(4)],'entries':['a'],'event':{},'unresolved':[]}
        with patch.object(c,'choice_graph',return_value=g):
            limited=c.event_paths('mock',max_paths=1)
        self.assertEqual(len(limited['rows']),1);self.assertTrue(limited['truncated'])
        e=next(e for e in c.all_events(include_indirect=True)['rows'] if e['title']=='安眠一隅')
        self.assertGreater(len({s for row in c.event_paths(e['id'])['rows'] for s in row['scenes']}),2)
    def test_177(self):
        e=next(e for e in c.all_events()['rows'] if e['title']=='桑尼的邀请');r=c.event_reward_options(e['id'])
        self.assertFalse(r['inventory_updated']);self.assertTrue(all(x['actual_claim_eligible'] is None for x in r['rows']))
        for e in c.all_events()['rows']:self.assertEqual(c.event_reward_options(e['id'])['event']['id'],e['id'])
        total=sum(bool(x['rewards']) for e in c.all_events()['rows'] for x in c.event_reward_options(e['id'])['rows'])
        self.assertGreater(total,0)
    def test_177_reward_title_guard_and_incomplete_pool(self):
        from unittest.mock import patch
        e=next(e for e in c.all_events()['rows'] if e['title']=='血衣之下')
        good=c.event_reward_options(e['id']);row=next(x for x in good['rows'] if x['rewards'])
        self.assertTrue(row['named_reward_found']);self.assertFalse(row['full_reward_pool_known'])
        self.assertTrue(row['unknown_reward_pool'])
        from rouge.node_rewards import _reference
        bad=deepcopy(_reference());cid=row['rewards'][0]['choice_id']
        bad['event_rewards'][cid]['choice_title']='不同选项'
        with patch('rouge.node_rewards._reference',return_value=bad):
            changed=next(x for x in c.event_reward_options(e['id'])['rows'] if x['choice_id']==row['choice_id'])
        self.assertFalse(changed['rewards']);self.assertTrue(changed['rejected_reward_links'])
    def test_178(self):
        r=c.battle_candidates('作战',floor=1);self.assertIn('遗忘时间',[x['title'] for x in r['rows']])
        self.assertTrue(all(x['categories']==['normal'] and x['natural_node_types']==['作战'] for x in r['rows']))
        self.assertFalse(c.battle_candidates('作战',floor=6)['rows'])
        self.assertEqual(len(c.battle_candidates('作战')['rows']),31)
        self.assertEqual(len(c.battle_candidates('紧急作战')['rows']),31)
        self.assertFalse(c.battle_candidates('险路尽头')['rows'])
        self.assertEqual(len(c.battle_candidates()['rows']),105)
    def test_178_contexts_never_mix_normal_events_pursuit(self):
        ordinary={r['id'] for r in c.battle_candidates('作战')['rows']}
        self.assertNotIn('ro6_t_1',ordinary);self.assertNotIn('ro6_c_1',ordinary)
        self.assertNotIn('ro6_t_6',ordinary);self.assertNotIn('ro6_t_8',ordinary)
        event=c.battle_candidates('不期而遇',context='content',floor=1)['rows']
        self.assertIn('ro6_t_1',{r['id'] for r in event})
        self.assertTrue(any('event' in r['categories'] and 'pursuit' in r['categories'] for r in event))
        self.assertFalse(c.battle_candidates('不期而遇',context='natural')['rows'])
        bosses={r['id'] for r in c.battle_candidates('险路恶敌')['rows']}
        self.assertIn('ro6_b_1',bosses);self.assertNotIn('ro6_b_1_b',bosses)
        self.assertEqual({r['id'] for r in c.battle_candidates('“居民”据点')['rows']},{'ro6_t_10','ro6_t_11'})
        self.assertEqual({r['id'] for r in c.battle_candidates('诡意行商',context='content')['rows']},{'ro6_t_6','ro6_t_7'})
        with self.assertRaises(ValueError):c.battle_candidates(context='invalid')
    def test_178_hidden_floor_not_reassigned_to_main_floor(self):
        r=c.battle_candidates('作战',floor=1)
        self.assertEqual(len(r['rows']),4)
        self.assertTrue(any(x['hidden_layer_reference'] for x in r['excluded']))
        hidden=c.battle_candidates('作战',floor=6,special_region=True)['rows']
        self.assertTrue(any(x['hidden_layer_reference'] for x in hidden))
    def test_178_resident_gate_uses_explicit_node_conditions(self):
        for floor in (1,6):
            r=c.battle_candidates('“居民”据点',floor=floor,difficulty=15)
            self.assertFalse(r['rows']);self.assertEqual(len(r['excluded']),2)
            self.assertFalse(r['known_requirement_checks']['known_floor_requirement_matches'])
        r=c.battle_candidates('“居民”据点',floor=2,difficulty=3)
        self.assertFalse(r['rows']);self.assertFalse(r['known_requirement_checks']['known_difficulty_requirement_matches'])
        r=c.battle_candidates('“居民”据点',floor=2)
        self.assertEqual(len(r['rows']),2);self.assertIsNone(r['known_requirement_checks']['known_difficulty_requirement_matches'])
        self.assertEqual(len(c.battle_candidates('“居民”据点',floor=2,difficulty=4)['rows']),2)
        with self.assertRaises(ValueError):c.battle_candidates(difficulty=True)
    def test_179(self):
        r=c.indirect_events(floor=1);self.assertEqual([e['title'] for e in r['rows']],['安眠一隅'])
        self.assertEqual(r['cross_run_support'][0]['title'],'行动奖励')
        self.assertIsNone(r['rows'][0]['current_eligibility']) if r['rows'][0]['current_eligibility'] is None else self.assertEqual(r['rows'][0]['current_eligibility'],'未知')
        self.assertNotIn('安眠一隅',[e['title'] for e in c.event_candidates()['rows']])
    def test_179_special_is_inspectable_not_natural(self):
        e=c.indirect_events()['rows'][0]
        self.assertEqual(len(c.event_details(e['id'])['rows']),12)
        self.assertFalse(c.indirect_events()['scope']['all_server_events_verified'])
    def test_180(self):
        r=c.search_events('绒毛');self.assertEqual([e['title'] for e in r['rows']],['桑尼的邀请'])
        self.assertEqual(r['rows'][0]['matches'][0]['scope'],'选择或条件')
        self.assertEqual(len(c.search_events('三重身')['rows']),3)
        self.assertFalse(c.search_events('不存在的词123')['rows'])
    def test_180_special_notes_subchoices_originals_searchable(self):
        self.assertEqual([e['title'] for e in c.search_events('安眠')['rows']],['安眠一隅'])
        r=c.search_events('动物泥偶')
        self.assertTrue(any(x['scope']=='来源子分支' for e in r['rows'] for x in e['matches']))
        self.assertTrue(c.search_events('行动奖励')['original_matches'])
        self.assertTrue(c.search_events('他缚')['rows'])
        self.assertFalse(c.search_events('安眠',include_indirect=False)['rows'])
