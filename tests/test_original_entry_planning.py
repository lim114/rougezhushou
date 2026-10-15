"""Direct special-entry proofs and three-state declarations, using public fixtures."""
from collections import Counter
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as c,event_planning as p
from rouge.node_catalog_view import NodeCatalogPanel


def startup_context():return {'phase':'run_start','exploration_mode':'NORMAL','previous_regions_completed':2}


class OriginalEntryPlanningTests(unittest.TestCase):
    def test_all_six_hidden_choices_have_literal_primary_scene_pair(self):
        data=c._original_entries();rows=data['startup']['legacy_choices'];self.assertEqual(len(rows),6)
        self.assertEqual(len({r['legacy_id'] for r in rows}),6)
        self.assertEqual(len({r['legacy_item']['name'] for r in rows}),1)
        for row in rows:
            board={b['key']:b['valueStr'] for b in row['force_add_choice_buff']['blackboard']}
            self.assertEqual(row['force_add_choice_buff']['key'],'force_add_choice')
            self.assertEqual(board,{'choice_id':row['choice']['id'],'scene_ids':'scene_ro6_startbuff_enter'})
            result=p.original_entry_qualification(row['choice']['id'])
            self.assertTrue(result['source_scene_link_verified']);self.assertEqual(result['status'],'unknown')
            self.assertIsNone(result['actual_server_eligible'])

    def test_legacy_condition_tristate_never_borrows_current_held_items(self):
        key='choice_ro6_startbuff_7';legacy='rogue_6_legacy_04';ctx=startup_context()
        ctx.update(item_quantities={legacy:1},inventory_complete=True,item_presence={legacy:True})
        self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'unknown')
        ctx['inherited_legacy_presence']={legacy:True};before=deepcopy(ctx)
        result=p.original_entry_qualification(key,ctx);self.assertEqual(result['status'],'matched');self.assertEqual(ctx,before)
        self.assertIsNone(result['actual_selectable']);self.assertEqual(result['documented_extra_blue_display_count'],1)
        ctx['inherited_legacy_presence'][legacy]=False
        self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'excluded')
        ctx.pop('inherited_legacy_presence');ctx['inherited_legacy_complete']=True
        self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'excluded')

    def test_completed_regions_phase_and_mode_do_not_become_current_generation(self):
        ctx=startup_context();ctx['inherited_legacy_ids']=['rogue_6_legacy_04'];key='choice_ro6_startbuff_7'
        ctx['previous_regions_completed']=1;self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'excluded')
        ctx['previous_regions_completed']=2;self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'matched')
        ctx['phase']='map_node';self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'excluded')
        ctx['phase']='run_start';ctx['exploration_mode']='MONTH_TEAM'
        self.assertEqual(p.original_entry_qualification(key,ctx)['status'],'excluded')
        self.assertNotIn('行动奖励',[e['title'] for e in c.all_events(include_indirect=True)['rows']])

    def test_regular_six_pool_is_not_displayed_set_or_direct_source_scene(self):
        for row in c._original_entries()['startup']['regular_choices']:
            result=p.original_entry_qualification(row['id'],startup_context())
            self.assertEqual(result['status'],'matched');self.assertFalse(result['source_scene_link_verified'])
            self.assertEqual(result['documented_regular_candidate_count'],6)
            self.assertEqual(result['documented_regular_display_count'],3)
            self.assertIsNone(result['actual_displayed_choice_ids']);self.assertFalse(result['all_twelve_choices_displayed'])

    def test_portal_nineteen_exact_descriptions_and_color_aliases_are_preserved(self):
        data=c._original_entries()['portal'];counts=Counter()
        for variant in data['variants']:
            for scene in variant['original_scenes']:
                self.assertEqual(scene['description'],data['common_prefix']+variant['explicit_clause'])
                self.assertEqual(c._original()['scenes'][scene['id']]['description'],scene['description'])
                counts[variant['fog_color']]+=1
        self.assertEqual(dict(counts),{'red':8,'blue':3,'green':3,'gold':2,'orange':2,'purple':1})
        result=p.original_entry_variants(data['event_id'],{'fog_color':'red'})
        self.assertEqual(len(result['rows']),19)
        self.assertEqual(sum(r['documented_identity_matches'] is True for r in result['rows']),8)
        self.assertEqual(sum(r['status']=='excluded' for r in result['rows']),11)
        self.assertTrue(all(r['actual_original_scene_selected'] is None for r in result['rows']))
        self.assertFalse(result['original_id_suffix_used_as_evidence'])
        details=c.event_details(data['event_id']);self.assertEqual(len(details['original_entry_variants']),19)
        self.assertEqual(len(details['unlinked_original_scenes']),13)

    def test_exact_scene_declaration_retains_one_identity_without_picking_by_color(self):
        data=c._original_entries()['portal'];key=data['variants'][1]['original_scenes'][0]['id']
        result=p.original_entry_variants(data['event_id'],{'original_scene_id':key})
        self.assertEqual(sum(r['documented_identity_matches'] is True for r in result['rows']),1)
        self.assertIsNone(result['actual_original_scene_selected'])
        raw=p.original_entry_qualification('choice_ro6_portal1a_6')
        self.assertFalse(raw['source_scene_link_verified']);self.assertEqual(raw['status'],'unknown')
        self.assertEqual(raw['record']['nextSceneId'],'scene_ro6_portal1a_3')
        self.assertIsNone(raw['reachable_from_entry'])

    def test_invalid_startup_snapshot_is_rejected_without_mutation(self):
        for ctx in ({'previous_regions_completed':True},{'inherited_legacy_ids':['襁褓羽蛇']},
            {'inherited_legacy_complete':1},{'original_scene_id':{}},
            {'inherited_legacy_ids':['rogue_6_legacy_04'],'inherited_legacy_presence':{'rogue_6_legacy_04':False}}):
            with self.subTest(context=ctx),self.assertRaises(ValueError):p.original_entry_qualification('choice_ro6_startbuff_7',ctx)


class OriginalEntryViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):self.panel=NodeCatalogPanel();self.addCleanup(self.panel.close)
    def select_record(self,key):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries)
            if e['kind']=='original' and e['record']['record']['record_id']==key))
        return self.panel.detail.toPlainText()

    def test_special_details_show_proof_and_unknown_then_declared_conditions(self):
        text=self.select_record('choice_ro6_startbuff_7')
        self.assertIn('force_add_choice',text);self.assertIn('资格未确认',text)
        self.assertIn('6项中随机展示3项',text);self.assertIn('当前持有',text)
        ctx=startup_context();ctx['inherited_legacy_presence']={'rogue_6_legacy_04':True}
        self.panel.set_map_context(None,runtime_context=ctx);text=self.select_record('choice_ro6_startbuff_7')
        self.assertIn('特殊入口资料：已列条件相符',text);self.assertIn('实际当前展示/进入/服务器资格：未知',text)
        self.assertFalse(self.panel.map_jump.isEnabled())

    def test_original_portal_preview_requires_exact_declared_scene_id(self):
        scene='scene_ro6_portal5a_enter'
        graph={'zone_id':'zone_1','template_id':'public','grid':{'rows':3,'cols':3},'edges':[],
            'nodes':[{'id':'a','row':1,'col':1,'observed_type':'误入奇境','content':{'kind':'event','title':'溯源'}},
                     {'id':'b','row':0,'col':2,'observed_type':'误入奇境','content':{'kind':'event','title':'溯源','original_scene_id':scene}}]}
        self.panel.set_map_context(graph,epoch=123);text=self.select_record(scene)
        self.assertIn('蓝雾',text);self.assertIn('逐字相等',text)
        entry=next(e for e in self.panel.entries if e['kind']=='original' and e['record']['record']['record_id']==scene)
        self.assertEqual(entry['record']['record']['record_id'],scene)
        self.assertIn(scene,text)
        self.assertNotIn(scene,entry['title'])
        self.assertEqual(self.panel.map_location.count(),1)
        calls=[];self.panel.mapNodeSelected.connect(lambda key,binding:calls.append((key,binding)))
        self.panel.map_jump.click();self.assertEqual(len(calls),1);self.assertEqual(calls[0][0],'b');self.assertEqual(calls[0][1]['epoch'],123)
        self.assertIn('声明原场景ID',self.panel.map_location.currentText())

    def test_same_frame_unique_read_contract_maps_without_manual_original_id(self):
        scene='scene_ro6_portal5a_enter'
        graph={'zone_id':'zone_1','template_id':'public','grid':{'rows':3,'cols':3},'edges':[],
            'nodes':[{'id':'a','row':1,'col':1,'observed_type':'误入奇境','content':{'kind':'event','title':'溯源',
                'source':'same_frame_selected_node','identity_status':'visible_scene','scene_candidates':[scene]}}]}
        self.panel.set_map_context(graph,epoch='public-run');self.select_record(scene)
        self.assertEqual(self.panel.map_location.count(),1)
        self.assertIn('同帧唯一原场景候选',self.panel.map_location.currentText())
        for candidates,source in (([scene,'scene_ro6_portal5b_enter'],'same_frame_selected_node'),([scene],'unbound_popup')):
            graph['nodes'][0]['content'].update(scene_candidates=candidates,source=source)
            self.panel.set_map_context(graph,epoch='public-run');self.select_record(scene)
            self.assertEqual(self.panel.map_location.count(),0)

    def test_conflicting_declared_and_observed_scene_never_maps_to_either(self):
        scene='scene_ro6_portal5a_enter';other='scene_ro6_portal5b_enter'
        graph={'zone_id':'zone_1','template_id':'public','grid':{'rows':3,'cols':3},'edges':[],
            'nodes':[{'id':'a','row':1,'col':1,'observed_type':'误入奇境','content':{'kind':'event','title':'溯源',
                'source':'same_frame_selected_node','identity_status':'visible_scene','scene_candidates':[scene],
                'original_scene_id':other}}]}
        self.panel.set_map_context(graph,epoch='public-run')
        for record in (scene,other):
            self.select_record(record);self.assertFalse(self.panel.map_jump.isEnabled())


if __name__=='__main__':unittest.main()
