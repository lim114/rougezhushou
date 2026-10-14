from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time
import unittest

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import exploration_planning as p
from rouge.node_arrival import arrival_reference,arrival_source,arrival_data
from scripts.build_node_arrival_reference import build
from rouge.offline_tools_view import OfflineToolsPanel,exploration_presets,render_offline_result

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    return deepcopy(next(r['payload'] for r in exploration_presets('itinerary') if r['id']=='light-chain'))


class NodeArrivalPlanningTests(unittest.TestCase):
    def test_first_and_received_declarations_are_required_not_history_or_visit(self):
        node=fixture()['graph']['nodes'][1]
        self.assertEqual(arrival_reference(node,['LIGHT'])['node_arrival_ap_reference'],1)
        for state in ({},{'first_entry':True},{'reward_received':False},{'first_entry':False,'reward_received':False}):
            changed=deepcopy(node);changed['light_arrival_declaration']=state
            changed.update(visited=True,remembered_type='羽瞰点')
            self.assertIsNone(arrival_reference(changed,['LIGHT'])['node_arrival_ap_reference'])
        node.pop('light_arrival_declaration');node.update(visited=True,remembered_type='羽瞰点')
        self.assertIsNone(arrival_reference(node,[])['node_arrival_ap_reference'])
        self.assertIsNone(arrival_reference(node,['LIGHT'])['first_entry_declared'])

    def test_already_received_and_conflicting_declarations_never_repeat_plus_one(self):
        node=fixture()['graph']['nodes'][1]
        node['light_arrival_declaration']={'first_entry':False,'reward_received':True}
        result=arrival_reference(node,['LIGHT'])
        self.assertEqual(result['first_component_remaining_ap_reference'],0)
        self.assertIsNone(result['node_arrival_ap_reference'])
        self.assertIn('重复到达',result['reason'])
        node['light_arrival_declaration']['first_entry']=True
        result=arrival_reference(node,['LIGHT'])
        self.assertTrue(result['declaration_conflict']);self.assertIsNone(result['node_arrival_ap_reference'])

    def test_visibility_parameters_have_exact_technology_gate_and_no_geometry(self):
        node=fixture()['graph']['nodes'][1]
        cases=[(2,True,False,[4],[12]),(3,True,True,[12],[24]),(15,False,False,[4],[12]),
               (3,None,None,[4,12],[12,24]),(None,True,None,[4,12],[12,24]),(None,False,False,[4],[12])]
        for difficulty,split,boost,spawn,arrival in cases:
            result=arrival_reference(node,['LIGHT'],difficulty=difficulty,split_unlocked=split)
            self.assertIs(result['vision_boost_condition_matches'],boost)
            self.assertEqual(result['spawn_surrounding_count_candidates'],spawn)
            self.assertEqual(result['arrival_surrounding_count_candidates'],arrival)
            self.assertIsNone(result['range_geometry']);self.assertIsNone(result['actual_revealed_nodes'])

    def test_occupied_light_grant_and_budget_do_not_borrow_future_return(self):
        payload=next(r['payload'] for r in exploration_presets('options') if r['id']=='fresh-light-occupied')
        result=p.movement_options(**payload)
        walking=next(r for r in result['options'] if r['id']=='walking')
        self.assertTrue(walking['node_arrival_reference']['occupied_light_source_exception'])
        self.assertEqual(walking['nominal_ap_after_combined_grants_reference'],2)
        spring=next(r for r in result['options'] if r['id']=='spring')
        self.assertEqual((spring['item_ap_grant_reference'],spring['node_arrival_reference']['node_arrival_ap_reference']),(3,1))
        self.assertEqual(spring['nominal_ap_after_combined_grants_reference'],6)
        result=p.movement_options(payload['graph'],'light',action_points=0)
        self.assertFalse(result['options'][0]['base_cost_affordable'])
        self.assertIsNone(result['options'][0]['nominal_ap_after_combined_grants_reference'])
        self.assertIsNone(result['minimum_base_ap_cost_reference'])

    def test_positive_ap_chain_separates_item_and_node_grants_and_only_updates_scratch(self):
        payload=fixture();before=deepcopy(payload);result=p.itinerary(**payload)
        self.assertEqual(payload,before)
        self.assertEqual((result['known_base_ap_cost_sum'],result['known_stated_ap_grant_sum'],result['known_node_arrival_ap_grant_sum']),(2,0,1))
        self.assertEqual(result['nominal_final_ap'],1);self.assertIsNone(result['stopped_reason'])
        self.assertEqual(result['node_arrival_reference_state'][0]['light_arrival_declaration'],{'first_entry':False,'reward_received':True})
        self.assertEqual(result['node_arrival_reference_state_scope'],'conditional_plan_only')
        self.assertIsNone(result['actual_final_ap']);self.assertIsNone(result['actual_final_inventory'])

    def test_payment_zero_preserves_return_reference_and_independent_tail_not_actual_stop(self):
        payload=fixture();payload['action_points']=1;result=p.itinerary(**payload)
        self.assertEqual(result['steps'][0]['nominal_ap_after_payment'],0)
        self.assertEqual(result['steps'][0]['nominal_ap_after_stated_grant'],1)
        self.assertEqual(result['stopped_reason'],'zero_ap_callback_order_unverified')
        tail=result['steps'][1]
        self.assertEqual(tail['declared_step'],payload['steps'][1])
        self.assertEqual(tail['assumed_start_from_declared_plan'],'light')
        self.assertEqual(tail['independent_declared_option_reference']['base_ap_cost'],1)
        self.assertIsNone(tail['independent_declared_option_reference']['base_cost_affordable'])
        self.assertIsNone(tail['actual_continuation']);self.assertFalse(result['complete_declared_conditions'])

    def test_zero_ap_item_grant_does_not_justify_continuing_with_invented_callback_order(self):
        payload=fixture();payload['action_points']=0
        payload['inventory']=[{'instance_id':'spring','item_id':'rogue_6_scrap_M_12','remaining_uses':1}]
        payload['steps'][0]['mode']='spring'
        result=p.itinerary(**payload)
        self.assertEqual(result['steps'][0]['base_ap_cost'],0)
        self.assertEqual(result['steps'][0]['stated_ap_grant'],3)
        self.assertEqual(result['steps'][0]['nominal_ap_after_stated_grant'],4)
        self.assertEqual(result['steps'][1]['status'],'not_evaluated_after_stop')
        self.assertEqual(result['stopped_reason'],'zero_ap_callback_order_unverified')
        self.assertIsNone(result['actual_final_ap'])

    def test_unknown_light_state_and_repeat_plan_stop_dependency_without_double_count(self):
        payload=fixture();payload['graph']['nodes'][1].pop('light_arrival_declaration')
        result=p.itinerary(**payload)
        self.assertEqual(result['stopped_reason'],'node_arrival_ap_condition_unknown')
        self.assertEqual(result['steps'][0]['unknown_ap_components'],['node_arrival'])
        self.assertIsNone(result['steps'][0]['nominal_ap_after_stated_grant'])
        self.assertIsNone(result['nominal_final_ap']);self.assertEqual(result['steps'][1]['status'],'not_evaluated_after_stop')
        payload=next(r['payload'] for r in exploration_presets('itinerary') if r['id']=='light-revisit')
        result=p.itinerary(**payload)
        self.assertEqual(result['known_node_arrival_ap_grant_sum'],1)
        third=result['steps'][2]['node_arrival_reference']
        self.assertEqual(third['first_component_remaining_ap_reference'],0)
        self.assertIsNone(third['node_arrival_ap_reference']);self.assertEqual(result['steps'][3]['status'],'not_evaluated_after_stop')

    def test_current_original_type_is_required_and_inputs_are_strict(self):
        node=fixture()['graph']['nodes'][1]
        self.assertIsNone(arrival_reference(node,[])['node_arrival_ap_reference'])
        self.assertEqual(arrival_reference(node,['BATTLE_NORMAL'])['node_arrival_ap_reference'],0)
        for state in (False,{'first_entry':1},{'reward_received':'yes'},{'count':1}):
            changed=deepcopy(node);changed['light_arrival_declaration']=state
            with self.assertRaises(ValueError):arrival_reference(changed,['LIGHT'])
        for kwargs in ({'difficulty':True},{'difficulty':16},{'split_unlocked':1}):
            with self.assertRaises(ValueError):arrival_reference(node,['LIGHT'],**kwargs)

    def test_source_body_and_original_type_are_exact_and_copies_do_not_change_source(self):
        source=arrival_source();path=ROOT/source['community_file']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),source['community_sha256'])
        self.assertEqual(p.reference_data()['node_types']['LIGHT']['name'],'羽瞰点')
        self.assertEqual(source['community_license'],'CC BY-NC-SA 4.0')
        self.assertEqual(build(),arrival_data())
        self.assertEqual(source['original_node_type_field'],'$.details.rogue_6.nodeTypeData.LIGHT')
        before=deepcopy(source);result=arrival_reference(fixture()['graph']['nodes'][1],['LIGHT'])
        result['source']['facts'].clear();self.assertEqual(arrival_source(),before)
        self.assertIn('Zero-AP exhaustion callback order versus item or LIGHT grants.',source['unverified'])


class NodeArrivalPlanningViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):self.panel=OfflineToolsPanel(include_historical_route_diagnostics=True);self.panel.resize(1100,760);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()
    def finish(self):
        until=time.monotonic()+8
        while self.panel._workers and time.monotonic()<until:self.app.processEvents();time.sleep(.005)
        self.assertFalse(self.panel._workers);self.assertIsNotNone(self.panel.result_snapshot(),self.panel.status.text())

    def test_all_six_new_presets_run_and_show_bound_reward_or_unknown_and_tail(self):
        count=0
        for command in ('options','itinerary'):
            self.panel.select_query('exploration',command)
            for preset in exploration_presets(command):
                if not preset['id'].startswith(('fresh-light','light-')):continue
                self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id']))
                self.panel.load_example.click();before=self.panel.editor.toPlainText()
                self.panel.run_button.click();self.finish();text=self.panel.result_view.toPlainText()
                self.assertEqual(self.panel.editor.toPlainText(),before)
                self.assertIn('首次',text);self.assertIn('4/12/24只是已列数量',text)
                self.assertIn('领取',text);self.assertFalse(self.panel._result_links)
                if preset['id'] in ('light-zero-tail','light-revisit'):
                    self.assertIn('尾链独立声明参考',text);self.assertIn('不表示已经续行或必然结束',text)
                if preset['id']=='light-state-unknown':self.assertIn('参考：未知',text)
                count+=1
        self.assertEqual(count,6)

    def test_source_refresh_preserves_input_reward_declarations_result_and_reading(self):
        self.panel.select_query('exploration','itinerary')
        self.panel.preset.setCurrentIndex(self.panel.preset.findData('light-zero-tail'));self.panel.load_example.click()
        self.panel.run_button.click();self.finish()
        cursor=self.panel.result_view.textCursor();cursor.setPosition(7);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor)
        self.panel.result_view.setTextCursor(cursor);self.panel.result_view.verticalScrollBar().setValue(17)
        before=(self.panel.editor.toPlainText(),self.panel.result_snapshot(),self.panel.result_view.toHtml(),
                cursor.selectedText(),self.panel.result_view.verticalScrollBar().value(),self.panel.preset.currentData())
        self.panel.set_graph(fixture()['graph'],epoch=234,historical=False);self.app.processEvents()
        after=(self.panel.editor.toPlainText(),self.panel.result_snapshot(),self.panel.result_view.toHtml(),
               self.panel.result_view.textCursor().selectedText(),self.panel.result_view.verticalScrollBar().value(),self.panel.preset.currentData())
        self.assertEqual(before,after)


if __name__=='__main__':unittest.main()
