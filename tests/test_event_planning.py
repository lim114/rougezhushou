from copy import deepcopy
import json,unittest
from rouge import event_planning as p
from rouge import node_catalog as c

def event(title):return next(e for e in c.all_events(include_indirect=True)['rows'] if e['title']==title)
def context(title):
    e=event(title)
    return {'node_type':e['node_types'][0],'floor':e['floors'][0] if e['floors'] else None,'entry_mode':'content'}
def choice_by_title(title,option,ctx):
    e=event(title)
    for scene in c.event_details(e['id'])['rows']:
        result=p.choice_eligibility(e['id'],scene['key'],ctx)
        for row in result['rows']:
            if row['choice_title']==option:return row
    raise AssertionError('source fixture choice missing')

class EventPlanningTests(unittest.TestCase):
    def test_resource_cost_budget_is_separate_from_server_eligibility(self):
        e=event('货从口出');scene=c.event_details(e['id'])['rows'][0]
        result=p.choice_resources(e['id'],scene['key'],{'gold':3})
        row=next(r for r in result['rows'] if '消耗4源石锭' in r['description'])
        cost=next(r for r in row['resource_references'] if r['kind']=='nominal_cost')
        self.assertFalse(cost['nominal_budget_covers']);self.assertEqual(cost['quantity_reference'],4)
        self.assertFalse(row['budget_failure_is_server_exclusion']);self.assertIsNone(row['actual_new_resources'])
        with self.assertRaises(ValueError):p.choice_resources(e['id'],scene['key'],{'gold':3,'resources':{'gold':4}})

    def test_resource_fraction_and_minimum_hp_do_not_guess_payment(self):
        e=event('沉重的契约');scene=c.event_details(e['id'])['rows'][0]
        rows=p.choice_resources(e['id'],scene['key'],{'resources':{'hp':5}})['rows']
        fractional=next(r for row in rows for r in row['resource_references'] if r['kind']=='fraction_cost')
        self.assertEqual(fractional['fraction_arithmetic_reference'],2.5)
        self.assertIsNone(fractional['actual_integer_cost']);self.assertFalse(fractional['integer_rounding_verified'])
        e=event('黑诞');rows=p.choice_resources(e['id'],c.event_details(e['id'])['rows'][0]['key'],{'resources':{'hp':2}})['rows']
        guarded=next(r for row in rows for r in row['resource_references'] if r.get('minimum_retained_hp_reference'))
        self.assertEqual(guarded['minimum_retained_hp_reference'],1)
        self.assertIsNone(guarded['nominal_budget_covers']);self.assertFalse(guarded['special_payment_rule_verified'])

    def test_category_item_cost_incomplete_stock_and_nested_relic_effects(self):
        e=event('回滚文明');scene=c.event_details(e['id'])['rows'][0]
        r=p.choice_resources(e['id'],scene['key'],{'item_quantities':{'rogue_6_scrap_G_01':1}})
        cost=next(x for row in r['rows'] for x in row['resource_references'] if x['kind']=='category_item_cost')
        self.assertEqual(cost['quantity_reference'],2);self.assertIsNone(cost['nominal_budget_covers'])
        r=p.choice_resources(e['id'],scene['key'],{'item_quantities':{'rogue_6_scrap_G_01':1},'inventory_complete':True})
        cost=next(x for row in r['rows'] for x in row['resource_references'] if x['kind']=='category_item_cost')
        self.assertFalse(cost['nominal_budget_covers'])
        e=event('安眠一隅');r=p.choice_resources(e['id'],c.event_details(e['id'])['rows'][0]['key'])
        self.assertFalse(any(x.get('quantity_reference')==99 for row in r['rows'] for x in row['resource_references']))
        self.assertTrue(all(not row['nested_relic_effects_auto_applied'] for row in r['rows']))

    def test_final_equal_hope_reference_does_not_leak_to_boss_exit(self):
        r=p.final_ap_conversion(7);self.assertEqual(r['conversion_ratio_reference'],1)
        self.assertEqual(r['hope_gain_reference'],7);self.assertIsNone(r['actual_hope_gain'])
        self.assertEqual({row['id'] for row in r['original_choice_records']},
            {'choice_ro6_final1_1','choice_ro6_final1_3','choice_ro6_final1_5'})
        from rouge.exploration_planning import region_transition
        r=region_transition('main_region_advance',remaining_ap=7,exit_node_type='BATTLE_BOSS')
        self.assertIsNone(r['resources']['hope_conversion_ratio']);self.assertIsNone(r['resources']['hope_gain'])
        with self.assertRaises(ValueError):p.final_ap_conversion(True)

    def test_current_terminal_outcomes_require_pre_entry_snapshot(self):
        e=event('被歌颂的影子');scene=next(s for s in c.event_details(e['id'])['rows'] if '若在进入本事件前已拥有【犬植浆】' in s['description'])
        ctx={'item_quantities':{'rogue_6_relic_artifact_3':0,'rogue_6_relic_artifact_4':0},'inventory_complete':True}
        r=p.scene_outcomes(e['id'],scene['key'],ctx)
        self.assertTrue(all(x['status']=='unknown' for x in r['rows']))
        ctx['pre_entry_inventory_complete']=True
        r=p.scene_outcomes(e['id'],scene['key'],ctx)
        self.assertEqual([x['status'] for x in r['rows']],['matched','excluded'])
        self.assertIsNone(r['actual_final_reward']);self.assertTrue(r['current_document_rule_is_deterministic'])
        self.assertEqual(r['current_document_source']['revision'],'440271')
        self.assertFalse(r['current_document_source']['whole_html_downloaded'])

    def test_current_terminal_origin_unknown_and_complement_are_preserved(self):
        e=event('被歌颂的影子');scene=next(s for s in c.event_details(e['id'])['rows'] if '若在进入本事件前已拥有【犬植浆】' in s['description'])
        ctx={'pre_entry_inventory_complete':True,'pre_entry_item_quantities':{'rogue_6_relic_artifact_4':1}}
        self.assertTrue(all(x['status']=='unknown' for x in p.scene_outcomes(e['id'],scene['key'],ctx)['rows']))
        ctx['pre_entry_item_origins']={'rogue_6_relic_artifact_4':[e['id']]}
        self.assertEqual([x['status'] for x in p.scene_outcomes(e['id'],scene['key'],ctx)['rows']],['excluded','matched'])
        ctx['pre_entry_item_origins']={'rogue_6_relic_artifact_4':['other_source']};ctx['pre_entry_item_origins_complete']=True
        self.assertEqual([x['status'] for x in p.scene_outcomes(e['id'],scene['key'],ctx)['rows']],['matched','excluded'])
        ctx['pre_entry_item_quantities']['rogue_6_relic_artifact_3']=1
        self.assertEqual([x['status'] for x in p.scene_outcomes(e['id'],scene['key'],ctx)['rows']],['excluded','matched'])
        choices=p.choice_eligibility(e['id'],scene['key'])['rows']
        self.assertTrue(all(row['edition_warnings'] for row in choices))
        with self.assertRaises(ValueError):p.scene_outcomes(e['id'],scene['key'],{'pre_entry_inventory_complete':1})

    def test_qualification_predecessor_three_state_and_unknown_server(self):
        red,house=event('呼吸的红苔'),event('沉寂之屋');ctx=context('呼吸的红苔')
        self.assertEqual(p.event_eligibility(red['id'],ctx)['status'],'unknown')
        ctx['event_history']={house['id']:{'encountered':False}}
        self.assertEqual(p.event_eligibility(red['id'],ctx)['status'],'excluded')
        ctx['event_history'][house['id']]['encountered']=True
        r=p.event_eligibility(red['id'],ctx)
        self.assertEqual(r['status'],'matched');self.assertIsNone(r['actual_server_eligible'])
        self.assertFalse(r['all_server_conditions_known'])
        r=p.qualified_events({'node_type':'不期而遇','floor':1,'entry_mode':'natural'})
        self.assertFalse(r['matched']);self.assertTrue(r['unknown']);self.assertTrue(r['excluded'])
        self.assertEqual(sum(len(r[key]) for key in ('matched','unknown','excluded')),38)

    def test_special_entry_and_scope_never_confirms_generation(self):
        e=event('安眠一隅')
        self.assertEqual(p.event_eligibility(e['id'],{'entry_mode':'natural'})['status'],'excluded')
        r=p.event_eligibility(e['id'],{'entry_mode':'processed_item','movement_item_id':'rogue_6_scrap_M_07'})
        self.assertIsNone(r['actual_server_eligible'])
        self.assertTrue(next(ch for ch in r['checks'] if ch['key']=='special_movement_entry')['matches'])
        r=p.event_eligibility(e['id'],{'entry_mode':'processed_item','movement_item_id':'rogue_6_scrap_M_08'})
        self.assertEqual(r['status'],'unknown')  # The source documents M07, not an exclusive proof against every other route.
        e=event('桑尼的邀请');ctx=context('桑尼的邀请');ctx['floor']=6
        self.assertEqual(p.event_eligibility(e['id'],ctx)['status'],'excluded')
        ctx['special_region']=True
        self.assertEqual(p.event_eligibility(e['id'],ctx)['status'],'unknown')

    def test_owned_item_and_gold_strict_boundary(self):
        ctx=context('黑诞');self.assertEqual(choice_by_title('黑诞','掏出笼控器控制猎狗',ctx)['status'],'unknown')
        ctx['item_quantities']={'rogue_6_scrap_G_12':0}
        self.assertEqual(choice_by_title('黑诞','掏出笼控器控制猎狗',ctx)['status'],'excluded')
        ctx['item_quantities']['rogue_6_scrap_G_12']=1
        self.assertEqual(choice_by_title('黑诞','掏出笼控器控制猎狗',ctx)['status'],'matched')
        ctx=context('传奇团伙')
        for gold,expected in ((50,'excluded'),(51,'matched')):
            ctx['gold']=gold;row=choice_by_title('传奇团伙','扎穿货车车胎',ctx)
            self.assertEqual(row['status'],expected)
            self.assertEqual(row['parsed_special_requirements'][0]['comparison'],'>')

    def test_pair_or_visit_exclusion_distinguishes_encountered_and_visited(self):
        ctx=context('好奇心与死');ctx['inventory_complete']=True
        ctx['item_quantities']={'rogue_6_relic_final_1':1,'rogue_6_relic_final_2':1}
        self.assertEqual(choice_by_title('好奇心与死','修正结果，必须找到目标',ctx)['status'],'excluded')
        ctx['item_quantities']={};box=event('窥视箱中')['id']
        ctx['event_history']={box:{'encountered':True}}
        self.assertEqual(choice_by_title('好奇心与死','修正结果，必须找到目标',ctx)['status'],'unknown')
        ctx['event_history'][box]['visited']=False
        row=choice_by_title('好奇心与死','修正结果，必须找到目标',ctx)
        self.assertTrue(row['parsed_special_requirements'][0]['matches'])
        self.assertEqual(row['status'],'unknown')  # Source has no proved main-floor qualification.
        ctx['event_history'][box]['visited']=True
        self.assertEqual(choice_by_title('好奇心与死','修正结果，必须找到目标',ctx)['status'],'excluded')

    def test_exact_choice_page_links_and_source_coverage(self):
        data=p.reference_data();self.assertEqual(data['counts'],{'groups':38,'scenes':190,'choices':233,'battle_choices':11,'stage_page_anchors':14})
        e=event('思乡心切');rows=p.event_battle_links(e['id'])['rows'];self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['choice_title'],'强行驱赶')
        link=rows[0]['stage_page_links'][0]
        self.assertEqual(link['title'],'ISW-NO 陌生旅伴')
        self.assertEqual(link['fixed_level_groups'][0]['stage_records'][0]['stage_id'],'ro6_t_1')
        self.assertIsNone(rows[0]['actual_stage_id'])
        self.assertTrue(rows[0]['community_choice_to_page_verified'])
        with self.assertRaises(ValueError):p.event_battle_links(e['id'],choice_key='community_group_014:scene:1:choice:0')

    def test_emergency_filter_keeps_unproved_ordinary_variants(self):
        rows=p.event_battle_links(event('鸭托邦')['id'])['rows']
        emergency=next(r for r in rows if r['conditional_text']=='升级为紧急作战')['stage_page_links'][0]
        self.assertEqual(emergency['fixed_level_groups'][0]['stage_records'][0]['stage_id'],'ro6_e_t_3')
        self.assertEqual(emergency['excluded_by_explicit_difficulty'][0]['stage_id'],'ro6_t_3')
        self.assertEqual(next(r for r in rows if r['conditional_text']=='升级为紧急作战')['preview_stage_candidates'][0]['stage_id'],'ro6_e_t_3')
        ordinary=next(r for r in rows if r['conditional_text'] is None)['stage_page_links'][0]
        self.assertEqual({r['difficulty'] for group in ordinary['fixed_level_groups'] for r in group['stage_records']},{'NORMAL','FOUR_STAR'})
        self.assertTrue(all(r['source_difficulty_matches'] is None for group in ordinary['fixed_level_groups'] for r in group['stage_records']))

    def test_event_pursuit_aliases_and_generic_next_floor_pool(self):
        r=p.event_battle_links(event('黑诞')['id'])['rows'][0]
        self.assertEqual(len(r['stage_page_links']),3)
        self.assertEqual({s['stage_id'] for l in r['stage_page_links'] for g in l['fixed_level_groups'] for s in g['stage_records']},
                         {'ro6_t_13','ro6_c_5','ro6_t_14','ro6_c_6','ro6_t_15','ro6_c_7'})
        self.assertTrue(all(l['fixed_level_groups'][0]['same_level_aliases'] for l in r['stage_page_links']))
        e=event('洞中宝');r=p.event_battle_links(e['id'],context={'floor':2})['rows'][0]['generic_pool_requirement']
        self.assertEqual(r['next_main_floor_reference'],3);self.assertEqual(len(r['fixed_named_pool']),6)
        self.assertFalse(r['server_pool_complete'])
        r=p.event_battle_links(e['id'],context={'floor':2,'special_region':True})['rows'][0]['generic_pool_requirement']
        self.assertIsNone(r['next_main_floor_reference']);self.assertFalse(r['fixed_named_pool'])

    def test_context_is_preserved_and_invalid_declarations_rejected(self):
        e=event('桑尼的邀请');ctx=context('桑尼的邀请');old=deepcopy(ctx)
        p.event_eligibility(e['id'],ctx);self.assertEqual(ctx,old)
        for ctx in ({'gold':True},{'item_quantities':{'x':True}},{'inventory_complete':1},
                    {'event_history':{'unknown':{'visited':True}}},{'floor':True}):
            with self.assertRaises(ValueError):p.event_eligibility(e['id'],ctx)
        json.dumps(p.qualified_events(),allow_nan=False)

if __name__=='__main__':unittest.main()
