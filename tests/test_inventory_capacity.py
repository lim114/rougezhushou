import importlib.util,json,sys,unittest
from copy import deepcopy
from itertools import combinations
from pathlib import Path
from PySide6.QtWidgets import QApplication
from rouge.inventory_capacity import inventory_capacity_plan,public_capacity_payload
from rouge.inventory_capacity_view import InventoryCapacityPanel,render_capacity_result


class CapacityTests(unittest.TestCase):
    def payload(self):return public_capacity_payload()
    def test_overload_pursuit_and_same_item_distinct_instance_minimal_release(self):
        p=self.payload();r=inventory_capacity_plan(**p)
        self.assertTrue(r['initial']['declared_overloaded']);self.assertEqual(r['initial']['minimum_release_units'],2)
        self.assertEqual(r['initial']['documented_action_gate'],'blocked_by_declared_overload')
        self.assertFalse(r['initial']['pursuit_exempt_from_overload'])
        self.assertEqual(r['minimum_release']['minimum_discarded_instances'],1)
        self.assertEqual(r['minimum_release']['candidate_discard_sets'],[{'instance_ids':['b'],'released_units':2},{'instance_ids':['c'],'released_units':2}])
        self.assertFalse(r['proposals'][0]['after_discard']['declared_overloaded'])
        self.assertEqual(r['proposals'][1]['after_receive']['declared_occupied'],4)
        self.assertIsNone(r['initial']['actual_game_action_allowed']);self.assertFalse(r['inventory_updated'])
    def test_unknown_weights_completeness_capacity_never_default_one_slot_or_empty_inventory(self):
        for key,value in [('capacity',None),('inventory_complete',False),('inventory_complete',None)]:
            p=self.payload();p['snapshot'][key]=value;r=inventory_capacity_plan(**p)
            self.assertIsNone(r['initial']['declared_occupied'] if key!='capacity' else r['initial']['free_units'])
            self.assertIsNone(r['minimum_release']['minimum_discarded_instances'])
        p=self.payload();p['snapshot']['items'][0]['slot_units']=None
        r=inventory_capacity_plan(**p);self.assertIsNone(r['initial']['declared_overloaded'])
        p['snapshot']['capacity']=3;r=inventory_capacity_plan(**p)
        self.assertTrue(r['initial']['declared_overloaded']);self.assertIsNone(r['initial']['declared_occupied'])
    def test_zero_and_equal_capacity_are_exact_declarations_without_implying_eligibility(self):
        p=self.payload();p['snapshot']['capacity']=7;r=inventory_capacity_plan(**p)
        self.assertFalse(r['initial']['declared_overloaded']);self.assertEqual(r['initial']['free_units'],0)
        self.assertIsNone(r['initial']['actual_game_action_allowed'])
        p['snapshot']['items']=[];p['snapshot']['capacity']=0;p['protected_ids']=[];p['proposals']=[]
        self.assertFalse(inventory_capacity_plan(**p)['initial']['declared_overloaded'])
    def test_protection_impossibility_and_capped_enumeration_are_distinct(self):
        p=self.payload();p['protected_ids']=['a','b','c'];p['proposals']=[]
        r=inventory_capacity_plan(**p);self.assertEqual(r['minimum_release']['status'],'protected_instances_prevent_sufficient_release')
        p=self.payload();p['proposals']=[];r=inventory_capacity_plan(**p,max_candidates=1)
        self.assertEqual(r['minimum_release']['minimum_discarded_instances'],1)
        self.assertFalse(r['minimum_release']['complete_candidate_enumeration'])
        self.assertEqual(r['minimum_release']['truncated_reason'],'candidate_limit')
    def test_strict_instance_discard_receive_provenance_and_input_validation(self):
        cases=[]
        for mutate in [lambda p:p['snapshot'].update(capacity=True),lambda p:p['snapshot'].update(inventory_complete=1),lambda p:p['snapshot'].update(source=''),lambda p:p['snapshot']['items'][0].update(slot_units=-1),lambda p:p['snapshot']['items'][1].update(instance_id='a'),lambda p:p['proposals'][0].update(discard_ids=['missing']),lambda p:p['proposals'][0].update(discard_ids=['a']),lambda p:p['proposals'][1]['received_items'][0].update(instance_id='b')]:
            p=self.payload();mutate(p)
            with self.assertRaises(ValueError):inventory_capacity_plan(**p)
    def test_all_small_weight_sets_match_independent_exhaustive_oracle(self):
        import itertools
        checked=0
        for weights in itertools.product(range(4),repeat=4):
            items=[{'instance_id':str(i),'item_id':'same-original-id','source':'independent oracle declaration','slot_units':w} for i,w in enumerate(weights)]
            cap=3;s={'snapshot_id':'oracle','source':'finite generated arithmetic','capacity':cap,'inventory_complete':True,'items':items}
            r=inventory_capacity_plan(s,protected_ids=['0']);needed=max(0,sum(weights)-cap)
            feasible=[combo for k in range(4) for combo in combinations(range(1,4),k) if sum(weights[i] for i in combo)>=needed]
            expected=min(map(len,feasible)) if feasible else None
            self.assertEqual(r['minimum_release']['minimum_discarded_instances'],expected)
            if expected is not None:
                self.assertEqual({tuple(row['instance_ids']) for row in r['minimum_release']['candidate_discard_sets']},{tuple(str(i) for i in c) for c in feasible if len(c)==expected})
            checked+=1
        self.assertEqual(checked,256)
    def test_protection_type_and_visit_limit_are_strict(self):
        for value in [False,0,{},'']:
            p=self.payload();p['protected_ids']=value
            with self.assertRaises(ValueError):inventory_capacity_plan(**p)
        p=self.payload();p['proposals']=[]
        r=inventory_capacity_plan(**p,max_search_visits=1)
        self.assertEqual(r['minimum_release']['search_visits'],1)
        self.assertFalse(r['minimum_release']['complete_candidate_enumeration'])
    def test_source_and_inputs_survive_output_editing_and_html_is_escaped(self):
        p=self.payload();before=deepcopy(p);r=inventory_capacity_plan(**p);self.assertEqual(p,before)
        r['snapshot']['source']='changed';self.assertEqual(p,before)
        p['proposals'][0]['id']='<tag>&';text=render_capacity_result(inventory_capacity_plan(**p))
        self.assertIn('&lt;tag&gt;&amp;',text);self.assertNotIn('<tag>',text)


class CapacityViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def test_actual_example_run_edit_invalidation_host_refresh_and_source_reading(self):
        panel=InventoryCapacityPanel();panel.show();panel.run_button.click();self.qt.processEvents()
        self.assertTrue(panel.result_snapshot()['initial']['declared_overloaded'])
        self.assertIn('含追猎',panel.result_view.toPlainText());before=panel.editor.toPlainText()
        panel.set_context({'capacity':100,'items':[]});self.assertEqual(panel.editor.toPlainText(),before)
        panel.editor.setPlainText('{"snapshot":1,"snapshot":2}');panel.run_button.click()
        self.assertIn('重复声明键',panel.status.text())
        panel.editor.setPlainText('[]');self.assertIsNone(panel.result_snapshot());panel.run_button.click()
        self.assertIsNone(panel.result_snapshot());self.assertEqual(panel.result_view.toPlainText(),'')
        panel.load_example.click();panel.run_button.click();self.assertIsNotNone(panel.result_snapshot())
        panel.close();panel.deleteLater();self.qt.processEvents()
