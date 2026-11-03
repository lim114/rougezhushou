"""Source-bound ownership gates and scoped absence, using public fixtures only."""
from copy import deepcopy
import json,unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import choice_held_requirements as held,event_planning as p,node_catalog as c
from rouge.node_catalog_view import NodeCatalogPanel,event_details_text
from tests.test_event_planning import event,context
from tests import test_event_run_context as context_tests
from rouge.event_run_context import observed_event_context

ROOT=Path(__file__).resolve().parents[1]
CONTROLLER='rogue_6_scrap_G_12';FOSSIL='rogue_6_relic_legacy_113'

def declared_context(title):
    ctx=context(title)
    if title=='呼吸的红苔':ctx['event_history']={event('沉寂之屋')['id']:{'encountered':True}}
    return ctx

def source_rows(title,ctx):
    e=event(title)
    return [row for scene in c.event_details(e['id'])['rows'] for row in p.choice_eligibility(e['id'],scene['key'],ctx)['rows']
        if any(check.get('description_condition_reference') for check in row['parsed_special_requirements'])]

class ChoiceHeldRequirementsTests(unittest.TestCase):
    def test_regenerate_every_current_choice_identity_and_original_owned_record(self):
        from scripts.build_choice_held_reference import build
        data=held.reference_data();self.assertEqual(build(ROOT),data)
        self.assertEqual(data['counts'],{'groups':38,'scenes':190,'choices':233,'top_level_owned_positions':5})
        self.assertEqual(len(data['original_choices']),6)
        self.assertEqual({r['required_item_id'] for r in data['community_choices'].values()},{CONTROLLER,FOSSIL})
        self.assertTrue(data['sources']['current_event_document']['whole_html_downloaded'])
        self.assertEqual(data['sources']['current_event_document']['revision'],'440271')
        for row in data['community_choices'].values():
            self.assertFalse(row['source_scene_link_verified'])
            self.assertTrue(row['primary_source_records'])
            self.assertTrue(all(not ref['next_scene_used_to_infer_source'] for ref in row['primary_source_records']))

    def test_all_five_public_owned_positions_use_presence_tristate_and_keep_options(self):
        count=0
        for title,identity in (('黑诞',CONTROLLER),('呼吸的红苔',CONTROLLER),('愈创之心',CONTROLLER),('无人商店',FOSSIL)):
            ctx=declared_context(title)
            for presence in (None,False,True):
                ctx['item_presence']={identity:presence};rows=source_rows(title,ctx)
                self.assertEqual(len(rows),2 if title=='无人商店' else 1)
                for row in rows:
                    check=next(check for check in row['parsed_special_requirements'] if check.get('description_condition_reference'))
                    self.assertIs(check['matches'],presence)
                    self.assertIsNone(check['actual_consumed']);self.assertFalse(check['holding_is_consumption'])
                    self.assertIsNone(row['actual_selectable']);self.assertFalse(row['full_server_conditions_known'])
                    if presence is False:self.assertEqual(row['status'],'excluded')
                    elif presence is None:self.assertEqual(row['status'],'unknown')
                    else:self.assertNotEqual(row['status'],'excluded')
                e=event(title);s=c.event_details(e['id'])['rows'][0]
                self.assertEqual(len(p.choice_eligibility(e['id'],s['key'],ctx)['rows']),len(s['choices']))
            count+=len(source_rows(title,ctx))
        self.assertEqual(count,5)

    def test_black_existing_conditional_is_enriched_once_without_duplicate_gate(self):
        row=source_rows('黑诞',declared_context('黑诞'))[0]
        gates=[check for check in row['parsed_special_requirements'] if check['key']=='required_owned_item']
        self.assertEqual(len(gates),1);self.assertEqual(gates[0]['source_text'],'仅在持有笼控器时出现')
        self.assertEqual(gates[0]['description_condition_reference']['required_item_id'],CONTROLLER)

    def test_red_predecessor_still_independent_from_owned_choice(self):
        e=event('呼吸的红苔');ctx=declared_context('呼吸的红苔');ctx['item_presence']={CONTROLLER:False}
        self.assertEqual(p.event_eligibility(e['id'],ctx)['status'],'matched')
        self.assertEqual(source_rows('呼吸的红苔',ctx)[0]['status'],'excluded')
        ctx['item_presence'][CONTROLLER]=True;ctx.pop('event_history')
        self.assertEqual(source_rows('呼吸的红苔',ctx)[0]['status'],'unknown')

    def test_two_unknown_entry_original_choices_expose_gate_without_recovering_entry(self):
        for identity in ('choice_ro6_normal3_1','choice_ro6_normal5_4'):
            for presence,expected in ((None,'unknown'),(False,'excluded'),(True,'matched')):
                r=p.original_entry_qualification(identity,{'item_presence':{CONTROLLER:presence}})
                self.assertEqual(r['documented_choice_requirements_status'],expected)
                self.assertEqual(r['status'],'excluded' if presence is False else 'unknown')
                self.assertFalse(r['source_scene_link_verified']);self.assertIsNone(r['reference'])
                self.assertIsNone(r['reachable_from_entry']);self.assertIsNone(r['actual_server_eligible'])
                self.assertFalse(r['natural_node_generation_verified'])
        rows=c.original_references()['rows']
        self.assertEqual(sum(r['record_type']=='scene' and not r['source_scene_link_verified'] for r in rows),25)
        self.assertEqual(sum(r['record_type']=='choice' and not r['source_scene_link_verified'] for r in rows),57)

    def test_red_reward_item_and_heart_lose_style_do_not_become_ownership_or_payment(self):
        data=held.reference_data()['original_choices']
        self.assertEqual(data['choice_ro6_normal3_1']['raw_record']['displayData']['itemId'],'rogue_6_gold')
        heart=data['choice_ro6_normal5_4'];self.assertIn('<@ro6.lose>',heart['description'])
        self.assertEqual(heart['required_item_id'],CONTROLLER);self.assertIsNone(heart['actual_consumed'])
        e=event('愈创之心');ctx=declared_context('愈创之心');ctx['item_presence']={CONTROLLER:True}
        result=p.choice_resources(e['id'],c.event_details(e['id'])['rows'][0]['key'],ctx)
        row=next(r for r in result['rows'] if r['choice_title']=='检测此地有无危险')
        self.assertEqual([(r['kind'],r['resource'],r['quantity_reference']) for r in row['resource_references']],
            [('nominal_gain_or_recovery','ap',5)])
        self.assertIsNone(row['actual_new_resources'])

    def test_nested_sandbox_effect_not_promoted_to_choice_gate(self):
        ctx=declared_context('线人');ctx['inventory_complete']=True
        e=event('线人');rows=p.choice_eligibility(e['id'],c.event_details(e['id'])['rows'][0]['key'],ctx)['rows']
        self.assertTrue(all(not row['parsed_special_requirements'] for row in rows))

    def test_runtime_complete_relics_never_prove_scrap_absence_or_count_budget(self):
        run=context_tests.EventRunContextTests().fixture({},True);before=deepcopy(run.state);ctx=observed_event_context(run)
        self.assertTrue(ctx['inventory_complete']);self.assertNotIn(CONTROLLER,ctx['inventory_complete_item_ids'])
        self.assertIn(FOSSIL,ctx['inventory_complete_item_ids'])
        self.assertIsNone(p._owned(p._context(ctx),CONTROLLER));self.assertFalse(p._owned(p._context(ctx),FOSSIL))
        self.assertEqual(run.state,before);self.assertNotIn('item_quantities',ctx)
        heart=declared_context('愈创之心')|ctx
        self.assertEqual(source_rows('愈创之心',heart)[0]['status'],'unknown')
        for title in ('回滚文明','愈创之心'):
            e=event(title);rows=p.choice_resources(e['id'],c.event_details(e['id'])['rows'][0]['key'],ctx)['rows']
            costs=[ref for row in rows for ref in row['resource_references'] if ref['kind']=='category_item_cost']
            self.assertTrue(costs);self.assertTrue(all(ref['nominal_budget_covers'] is None for ref in costs))
            self.assertTrue(all(not ref['inventory_complete_declared'] for ref in costs))

    def test_manual_global_complete_compatibility_and_narrow_scope(self):
        self.assertFalse(p._owned(p._context({'inventory_complete':True}),CONTROLLER))
        self.assertIsNone(p._owned(p._context({'inventory_complete':True,'inventory_complete_item_ids':[FOSSIL]}),CONTROLLER))
        self.assertFalse(p._owned(p._context({'inventory_complete':True,'inventory_complete_item_ids':[CONTROLLER]}),CONTROLLER))
        for value in (None,'RELIC',{},[CONTROLLER,CONTROLLER],[True]):
            with self.subTest(value=value),self.assertRaises(ValueError):
                p._context({'inventory_complete_item_ids':value})

    def test_membership_completeness_does_not_supply_missing_positive_quantities(self):
        e=event('回滚文明');scene=c.event_details(e['id'])['rows'][0]
        ctx={'inventory_complete':True,'item_presence':{'rogue_6_scrap_G_01':True}}
        rows=p.choice_resources(e['id'],scene['key'],ctx)['rows']
        cost=next(ref for row in rows for ref in row['resource_references'] if ref['kind']=='category_item_cost')
        self.assertEqual(cost['known_owned_subtotal'],0);self.assertIsNone(cost['nominal_budget_covers'])
        ctx['item_quantities']={'rogue_6_scrap_G_01':2}
        cost=next(ref for row in p.choice_resources(e['id'],scene['key'],ctx)['rows'] for ref in row['resource_references'] if ref['kind']=='category_item_cost')
        self.assertTrue(cost['nominal_budget_covers']);self.assertEqual(cost['known_owned_subtotal'],2)

    def test_source_guard_and_deepcopy_preserve_catalog_context(self):
        e=event('愈创之心');scene=c.event_details(e['id'])['rows'][0];choice=next(ch for ch in scene['choices'] if ch['title']=='检测此地有无危险')
        modified=deepcopy(choice);modified['description']+='未证'
        with self.assertRaises(ValueError):held.choice_reference(e['id'],modified)
        ctx=declared_context('愈创之心');before=deepcopy(ctx);result=source_rows('愈创之心',ctx)[0]
        result['parsed_special_requirements'][0]['description_condition_reference']['required_item_name']='modified'
        self.assertEqual(ctx,before);self.assertEqual(source_rows('愈创之心',ctx)[0]['parsed_special_requirements'][0]['required_item_name'],'笼控器')
        json.dumps(p.choice_eligibility(e['id'],scene['key'],ctx),allow_nan=False)

class ChoiceHeldViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=NodeCatalogPanel();self.panel.resize(900,700);self.panel.show();self.qt.processEvents()
        self.addCleanup(self.panel.close)
    def select_event(self,title):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries) if e['kind']=='event' and e['title']==title))
        self.qt.processEvents();return self.panel.detail.toPlainText()
    def select_original(self,identity):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries) if e['kind']=='original'
            and e['record']['record']['record_id']==identity));self.qt.processEvents();return self.panel.detail.toPlainText()

    def test_node_details_show_owned_gate_source_and_reward_without_consumption(self):
        self.panel.set_map_context(None,runtime_context={'item_presence':{CONTROLLER:False,FOSSIL:False}})
        for title in ('呼吸的红苔','愈创之心','无人商店'):
            text=self.select_event(title)
            self.assertIn('条件核对：不符；持有',text);self.assertIn('持有门原ID：',text)
            self.assertIn('固定427904与较新440271已对照',text)
            self.assertIn('仅判断持有，不认定消耗或实际可选',text)
        self.assertIn('获得1件收藏品',text)

    def test_unknown_origin_details_keep_source_unknown_and_no_map_jump(self):
        self.panel.set_map_context(None,runtime_context={'item_presence':{CONTROLLER:False}})
        text=self.select_original('choice_ro6_normal5_4')
        self.assertIn('来源入口仍未知',text);self.assertIn('原选项已列持有条件：已列条件不符',text)
        self.assertIn('当前服务器资格与完整可达链：未知',text);self.assertFalse(self.panel.map_jump.isEnabled())
        self.assertIn('scene_ro6_normal5_4',text);self.assertIn('<@ro6.lose>',text)

    def test_production_complete_scope_visible_as_scrap_unknown(self):
        ctx=observed_event_context(context_tests.EventRunContextTests().fixture({},True))
        self.panel.set_map_context(None,runtime_context=ctx);text=self.select_event('愈创之心')
        self.assertIn('条件核对：未知；持有零件笼控器',text)
        self.assertIn('有关零件数量不完整',text)

    def test_changed_and_unchanged_context_preserve_selection_reading_scroll_folding(self):
        self.panel.set_map_context(None,runtime_context={'item_presence':{CONTROLLER:False}})
        self.select_event('愈创之心');key=self.panel.detail_key;group_states=self.panel.list.expanded_groups()
        cursor=self.panel.detail.textCursor();cursor.setPosition(0);cursor.setPosition(4,QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor);selection=self.panel.detail.textCursor().selectedText()
        self.panel.detail.verticalScrollBar().setValue(140);scroll=self.panel.detail.verticalScrollBar().value()
        for ctx in ({'item_presence':{CONTROLLER:False}},{'item_presence':{CONTROLLER:True}}):
            self.panel.set_map_context(None,runtime_context=ctx);self.qt.processEvents()
            self.assertEqual(self.panel.detail_key,key);self.assertEqual(self.panel.detail.textCursor().selectedText(),selection)
            self.assertEqual(self.panel.detail.verticalScrollBar().value(),scroll);self.assertEqual(self.panel.list.expanded_groups(),group_states)
        self.assertIn('条件核对：相符；持有零件笼控器',self.panel.detail.toPlainText())

if __name__=='__main__':unittest.main()
