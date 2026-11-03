from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import unittest,json
from rouge import current_route_itinerary as model,current_battle_reference as battle
from scripts.build_current_route_itinerary_375 import build
ROOT=Path(__file__).resolve().parents[1]
class CurrentRouteItinerary375Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.current=battle.packet();assert cls.current;cls.stage=battle.stage_reference('ro6_n_1_3');assert cls.stage
    def test_complete9440_routes40695_checkpoints59575_steps_source_rebuild(self):
        blobs,counts=build();self.assertEqual(counts,{'base':8773,'checkpoints':40695,'main_bound_spawn_records':7042,'route_unassigned_spawn_records':654,'extra':667,'stages':184,'routes':9440,'steps':59575})
        for n,raw in blobs.items():self.assertEqual((ROOT/n).read_bytes(),raw)
    def test_all_original_route_selectors_and_counts_preserve_order_and_duplicates(self):
        inventory=model.packet()['inventory'];total=0
        for sid,entry in inventory['stages'].items():
            level=self.current['inputs']['levels'][entry['level_key']];expected=[(f'$.{field}[{i}]',scope,len(raw.get('checkpoints')or[]))for scope,field in(('base','routes'),('extra','extraRoutes'))for i,raw in enumerate(level.get(field)or[])];self.assertEqual([(r['key'],r['scope'],r['checkpoint_count'])for r in entry['routes']],expected);total+=len(expected)
        self.assertEqual(total,9440)
    def test_complete_checkpoint_types_preserve_five_original_kinds(self):
        types=model.packet()['inventory']['checkpoint_types'];self.assertEqual(types,{'MOVE':29090,'WAIT_FOR_SECONDS':6341,'DISAPPEAR':2519,'APPEAR_AT_POS':2521,'WAIT_CURRENT_FRAGMENT_TIME':224})
    def test_each_checkpoint_remains_between_start_and_end_in_original_order(self):
        r=model._derive(self.stage,'test-source')
        for route in r['entries']:
            self.assertEqual(route['steps'][0]['kind'],'START');self.assertEqual(route['steps'][-1]['kind'],'END');self.assertEqual([s['raw']for s in route['steps'][1:-1]],route['raw'].get('checkpoints')or[]);self.assertEqual([s['key']for s in route['steps']],list(map(str,range(len(route['steps'])))))
    def test_wait_and_disappear_coordinates_never_become_map_positions(self):
        r=model._derive(self.stage,'test-source');steps=[s for route in r['entries']for s in route['steps']if s['kind']in('WAIT_FOR_SECONDS','WAIT_CURRENT_FRAGMENT_TIME','DISAPPEAR')];self.assertTrue(steps);self.assertTrue(all(s['cell']is None and not s['spatial_reference_permitted']for s in steps))
    def test_only_explicit_main_spawns_bind_base_route_not_activate_or_preview(self):
        r=model._derive(self.stage,'test-source')
        for route in r['entries']:
            for a in route['actions']:self.assertEqual(route['scope'],'base');self.assertEqual(a['raw']['actionType'],'SPAWN');self.assertEqual(a['queue']['kind'],'main');self.assertEqual(a['raw']['routeIndex'],route['ordinal']-1)
    def test_extra_routes_keep_original_steps_without_guessing_branch_selection(self):
        r=model.stage_reference('ro6_n_1_1');rows=model.routes(r,scope='extra');self.assertTrue(rows);self.assertTrue(all(not row['actions']for row in rows));self.assertIn('没有按相同编号借用',model.player_text(r,rows[0]))
    def test_unassigned_spawns_partition_all_direct_records_without_losing_branch(self):
        r=model._derive(self.stage,'test-source');bound=[a['key']for route in r['entries']for a in route['actions']];unbound=[a['action']['key']for a in r['unassigned_actions']];expected=[a['key']for a in self.stage['actions']if a['raw']['actionType']=='SPAWN'];self.assertEqual(set(bound).intersection(unbound),set());self.assertCountEqual(bound+unbound,expected);self.assertTrue(all(a['actual_route']is None for a in r['unassigned_actions']))
    def test_unassigned_action_has_valid_original_jump_but_no_route_assignment(self):
        r=model.stage_reference('ro6_n_1_1');self.assertTrue(r['unassigned_actions']);a=r['unassigned_actions'][0]['action'];selected=model.resolve(r,action_key=a['key']);self.assertIsNotNone(selected);self.assertIsNone(selected['route']);self.assertIsNone(selected['actual_route']);self.assertIn('没有把它归到任何',model.player_text(r,action=a,unassigned=True))
    def test_defined_motion_only_and_nonspatial_placeholder_is_not_birth_cell(self):
        fake=deepcopy(self.stage);fake['level']['routes'][0]['motionMode']='NONE';r=model._derive(fake,'test');route=r['entries'][0];self.assertTrue(all(s['cell']is None for s in route['steps']));self.assertIn('未取得明确移动方式',model.player_text(r,route))
    def test_wrong_scope_action_cannot_be_borrowed_by_extra_route(self):
        r=model.stage_reference('ro6_n_1_1');base=next(route for route in r['entries']if route['actions']);extra=next(route for route in r['entries']if route['scope']=='extra');self.assertIsNone(model.resolve(r,extra['key'],action_key=base['actions'][0]['key']))
    def test_corrupted_source_and_forged_same_name_route_fail_closed(self):
        r=model.stage_reference('ro6_n_1_3');route=r['entries'][0];bad=deepcopy(r);bad['entries'][0]['raw']['motionMode']='FLY';self.assertIsNone(model.resolve(bad,route['key']))
        with patch.object(model,'packet',return_value=None):self.assertIsNone(model.stage_reference('ro6_n_1_3'))
    def test_valid_exact_step_position_and_wait_refusal(self):
        r=model.stage_reference('ro6_n_1_3');route=next(a for a in r['entries']if a['key']=='$.routes[10]');spatial=next(s for s in route['steps']if s['spatial_reference_permitted']);wait=next(s for s in route['steps']if s['kind']=='DISAPPEAR');p=model.position_reference(r,route['key'],spatial['key']);self.assertIsNotNone(p);self.assertEqual(p['step']['source_selector'],spatial['source_selector']);self.assertIsNone(p['actual_path']);self.assertIsNone(model.position_reference(r,route['key'],wait['key']));self.assertIsNone(model.position_reference(r,route['key'],None))
    def test_wait_fragment_parameter_is_seconds_not_global_time_or_clock_sum(self):
        r=model.stage_reference('ro6_n_1_4');route=next(a for a in r['entries']if a['key']=='$.routes[10]');step=next(s for s in route['steps']if s['kind']=='WAIT_CURRENT_FRAGMENT_TIME');text=model.player_text(r,route,step);self.assertIn('15秒',text);self.assertIn('不能与路程耗时或其它等待直接相加',text);self.assertIsNone(r['absolute_time']);self.assertIsNone(r['actual_path'])
    def test_filters_keep_chinese_enemy_search_and_actual_values_unknown(self):
        r=model.stage_reference('ro6_n_1_1');self.assertTrue(model.routes(r,'猎犬proto','base'));self.assertEqual(model.routes(r,scope='guess'),[]);self.assertEqual(model.routes(r,query=None),[]);self.assertFalse(r['run_updated']);self.assertFalse(r['actual_server_verified']);self.assertIsNone(model.stage_reference(None));self.assertIsNone(model.stage_reference('missing'))
