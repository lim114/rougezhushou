"""Last-confirmed presence and quantity-independent event conditions."""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from rouge.event_run_context import observed_event_context
from rouge import event_planning as p
from tests.test_event_planning import event,context


class EventRunContextTests(unittest.TestCase):
    def fixture(self,records,complete=False):
        state={'id':'public-run','started_at':100,'last_read':120,
               'relics':deepcopy(records),'tactical_tools':{}}
        return SimpleNamespace(state=state,calculation_resources=lambda:{'gold':{'value':51,'captured_at':119}},
            inventory_status=lambda:{'complete':complete,'recognized':sum(r.get('held') is True for r in records.values()),
                'recognized_tools':0,'confirmed_at':119})

    def test_presence_answers_ownership_without_fabricating_item_count(self):
        identity=p._named_item('沙盘α')
        run=self.fixture({identity:{'held':True,'captured_at':110,'source':'held_name_usage'}})
        before=deepcopy(run.state);result=observed_event_context(run)
        self.assertEqual(result['item_presence'],{identity:True})
        self.assertNotIn('item_quantities',result);self.assertNotIn('event_history',result)
        self.assertNotIn('pre_entry_item_quantities',result);self.assertEqual(run.state,before)
        self.assertEqual(result['gold'],51);self.assertTrue(p._owned(p._context(result),identity))
        result['item_presence'][identity]=False
        self.assertTrue(run.state['relics'][identity]['held'])

    def test_unqualified_flags_times_and_source_never_prove_presence_or_completeness(self):
        identity=p._named_item('沙盘α')
        for raw in ({'held':1,'captured_at':110,'source':'held'},
                    {'captured_at':110,'source':'held'},
                    {'held':True,'captured_at':99,'source':'held'},
                    {'held':True,'captured_at':121,'source':'held'},
                    {'held':True,'captured_at':110,'source':''}):
            with self.subTest(raw=raw):
                result=observed_event_context(self.fixture({identity:raw},complete=True))
                self.assertEqual(result['item_presence'],{})
                # A malformed/missing positive cannot establish a full inventory.
                self.assertFalse(result['inventory_complete'])
                self.assertIsNone(p._owned(p._context(result),identity))

    def test_complete_last_confirmed_inventory_proves_absence_but_never_pre_entry(self):
        alpha,beta=p._named_item('沙盘α'),p._named_item('沙盘β')
        result=observed_event_context(self.fixture({alpha:{'held':True,'captured_at':110,'source':'held'}},True))
        self.assertTrue(result['inventory_complete']);self.assertFalse(p._owned(p._context(result),beta))
        self.assertIsNone(p._pre_owned(p._context(result),beta))
        result=observed_event_context(self.fixture({alpha:{'held':False,'captured_at':110,'source':'held'}}))
        self.assertFalse(p._owned(p._context(result),alpha))

    def test_presence_schema_and_quantity_conflicts_are_rejected(self):
        for value in (1,'yes',{},[]):
            with self.subTest(value=value),self.assertRaises(ValueError):p.qualified_events({'item_presence':{'a':value}})
        for presence,count in ((True,0),(False,1)):
            with self.assertRaises(ValueError):p.qualified_events({'item_presence':{'a':presence},'item_quantities':{'a':count}})
        for presence,count in ((True,2),(False,0),(None,0)):
            p.qualified_events({'item_presence':{'a':presence},'item_quantities':{'a':count}})

    def test_known_sandbox_pair_excludes_option_but_unknown_history_does_not_invent_entry(self):
        ctx=context('好奇心与死');ctx['item_presence']={p._named_item('沙盘α'):True,p._named_item('沙盘β'):True}
        rows=[];e=event('好奇心与死')
        for scene in p.catalog.event_details(e['id'])['rows']:
            rows += p.choice_eligibility(e['id'],scene['key'],ctx)['rows']
        row=next(r for r in rows if '同时持有' in (r['conditional_text'] or ''))
        self.assertEqual(row['status'],'excluded');self.assertIsNone(row['actual_selectable'])
        ctx['item_presence'][p._named_item('沙盘β')]=None
        rows=[r for s in p.catalog.event_details(e['id'])['rows'] for r in p.choice_eligibility(e['id'],s['key'],ctx)['rows']]
        self.assertEqual(next(r for r in rows if '同时持有' in (r['conditional_text'] or ''))['status'],'unknown')


if __name__=='__main__':unittest.main()
