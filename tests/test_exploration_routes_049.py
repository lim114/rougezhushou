"""Observable offline route references, independent of sampling or real state."""
import copy
import unittest
from rouge.exploration_routes import route_reference
from rouge.map_reporting import format_route
from rouge.map_recognition import map_data


def graph():
    return {'status':'matched','zone_id':'zone_1','template_id':'test',
            'grid':{'rows':3,'cols':4},'current_node':'a','source':{'url':'https://example.org'},
            'nodes':[{'id':key,'row':row,'col':col,'center':[col/4,row/3],
                      'visible':True,'observed_type':label,'distance':col}
                     for key,row,col,label in [('a',1,0,'林间空地'),('b',0,1,'作战'),
                         ('c',2,1,'林间空地'),('d',2,2,'林间空地'),('e',1,3,'诡意行商')]],
            'edges':[['a','b'],['b','e'],['a','c'],['c','d'],['d','e']]}


class ExplorationRoutesTests(unittest.TestCase):
    def test_revealed_battle_does_not_prove_passage_and_clear_detour_is_separate(self):
        result=route_reference(graph(),'e')
        self.assertEqual(result['topology']['path'],['a','b','e'])
        self.assertEqual(result['topology']['unconfirmed_intermediate_nodes'],['b'])
        self.assertEqual(result['corridor']['path'],['a','c','d','e'])
        self.assertEqual(result['corridor']['base_walking_ap'],3)
        self.assertEqual(result['display_path'],result['corridor']['path'])
        self.assertFalse(result['entry_confirmed'])

    def test_past_visit_is_not_a_completion_marker(self):
        g=graph();g['nodes'][1].update(visited=True,remembered_type='作战')
        self.assertEqual(route_reference(g,'e')['corridor']['steps'],3)

    def test_unread_empty_tile_is_only_history_and_not_a_corridor(self):
        g=graph();g['nodes'][2].update(visible=False,remembered_type='林间空地')
        result=route_reference(g,'e')
        self.assertIsNone(result['corridor'])
        self.assertEqual(result['display_path'],['a','b','e'])

    def test_tunnel_is_a_documented_exception_but_creates_no_teleport_edge(self):
        g=graph();g['nodes'][1]['observed_type']='曲折密道'
        result=route_reference(g,'e')
        self.assertEqual(result['corridor']['path'],['a','b','e'])
        self.assertEqual(result['corridor']['base_walking_ap'],2)
        self.assertEqual(len(g['edges']),5)

    def test_unknown_type_prediction_or_remembered_tunnel_does_not_prove_passage(self):
        g=graph();g['nodes'][1].update(observed_type='未知的诡秘',remembered_type='曲折密道',
                                      prediction={'candidates':['曲折密道']})
        self.assertEqual(route_reference(g,'e')['corridor']['steps'],3)

    def test_unrevealed_destination_has_no_walking_consumption(self):
        g=graph();g['nodes'][-1].update(observed_type='未知的诡秘',remembered_type='诡意行商')
        result=route_reference(g,'e')
        self.assertFalse(result['target_revealed']);self.assertIsNone(result['corridor'])
        text=format_route(g,'e');self.assertIn('目标尚未在本帧明确揭示',text)
        self.assertNotIn('基础消耗',text.split('住民占领')[0])

    def test_historical_frame_has_no_current_route_even_if_old_marker_exists(self):
        result=route_reference(graph(),'e',historical=True)
        self.assertEqual(result['reason'],'historical_frame');self.assertEqual(result['display_path'],[])
        self.assertIn('历史参考',format_route(graph(),'e',historical=True))

    def test_missing_marker_never_falls_back_to_last_confirmed_position(self):
        g=graph();g.update(current_node=None,last_confirmed_current_node='a')
        result=route_reference(g,'e')
        self.assertEqual(result['reason'],'current_unconfirmed');self.assertIsNone(result['topology'])
        self.assertIn('不作为起点',format_route(g,'e'))

    def test_selected_current_node_is_not_free_reentry(self):
        result=route_reference(graph(),'a')
        self.assertEqual(result['status'],'same_position');self.assertIsNone(result['corridor'])
        self.assertIn('通常另耗1行动力',format_route(graph(),'a'))

    def test_disconnected_graph_has_no_fabricated_route(self):
        g=graph();g['edges']=[['a','c']]
        self.assertEqual(route_reference(g,'e')['reason'],'disconnected')

    def test_invalid_edges_and_duplicate_nodes_are_rejected(self):
        g=graph();g['edges'].append(['a','missing'])
        self.assertEqual(route_reference(g,'e')['reason'],'invalid_graph')
        g=graph();g['nodes'].append(copy.deepcopy(g['nodes'][0]))
        self.assertEqual(route_reference(g,'e')['reason'],'invalid_graph')

    def test_missing_selection_or_unmatched_layout_is_not_routed(self):
        self.assertEqual(route_reference(graph(),None)['reason'],'target_unconfirmed')
        g=graph();g['status']='ambiguous'
        self.assertEqual(route_reference(g,'e')['reason'],'layout_unconfirmed')

    def test_equally_short_paths_are_counted_without_probability_or_uniqueness(self):
        g=graph();g['edges'].append(['c','e']);g['nodes'][1]['observed_type']='林间空地'
        result=route_reference(g,'e')
        self.assertEqual(result['topology']['equal_shortest_paths'],2)
        self.assertEqual(result['corridor']['equal_shortest_paths'],2)
        text=format_route(g,'e');self.assertIn('同长拓扑路线 2 条',text)
        self.assertNotIn('%',text)

    def test_cycles_and_duplicate_edges_do_not_duplicate_paths(self):
        g=graph();g['edges'] += [['a','c'],['e','b'],['b','c']]
        result=route_reference(g,'e')
        self.assertEqual(result['topology']['steps'],2)
        self.assertEqual(result['topology']['equal_shortest_paths'],1)

    def test_longer_corridor_is_not_described_as_one_of_shortest_topology_paths(self):
        g=graph();g['nodes'].append({'id':'x','row':0,'col':2,'visible':True,'observed_type':'作战'})
        g['edges'] += [['a','x'],['x','e']]
        text=format_route(g,'e')
        self.assertIn('同长拓扑路线 2 条',text)
        self.assertIn('较长绕行路线',text)
        self.assertNotIn('其中一条',text)

    def test_input_order_does_not_change_reference_or_mutate_graph(self):
        g=graph();before=copy.deepcopy(g);expected=route_reference(g,'e')
        self.assertEqual(g,before)
        g['nodes'].reverse();g['edges'].reverse()
        self.assertEqual(route_reference(g,'e'),expected)

    def test_normal_report_has_positions_and_limits_without_raw_ids(self):
        text=format_route(graph(),'e')
        self.assertIn('上排 · 第2列',format_route(graph(),'b'))
        self.assertIn('当前行动力未完整读取',text)
        self.assertIn('连线尚未独立核验',text)
        self.assertIn('结局和难度收益未参与比较',text)
        self.assertNotIn('https://',text)
        self.assertIn('https://prts.wiki',format_route(graph(),'e',technical=True))
        self.assertLess(len(format_route(graph(),'e',compact=True)),150)

    def test_all_43_template_pairs_agree_with_independent_all_pairs_distance(self):
        for template in map_data()['templates']:
            nodes=copy.deepcopy(template['nodes']);keys=[n['id'] for n in nodes]
            index={key:i for i,key in enumerate(keys)};size=len(keys)
            distances=[[0 if i==j else float('inf') for j in range(size)] for i in range(size)]
            for a,b in template['edges']:distances[index[a]][index[b]]=distances[index[b]][index[a]]=1
            for k in range(size):
                for i in range(size):
                    for j in range(size):distances[i][j]=min(distances[i][j],distances[i][k]+distances[k][j])
            for n in nodes:n.update(visible=True,observed_type='林间空地')
            g={'status':'matched','nodes':nodes,'edges':template['edges']}
            for start in keys:
                g['current_node']=start
                for target in keys:
                    result=route_reference(g,target)
                    distance=distances[index[start]][index[target]]
                    if start==target:self.assertEqual(result['status'],'same_position')
                    elif distance==float('inf'):self.assertEqual(result['reason'],'disconnected')
                    else:
                        self.assertEqual(result['topology']['steps'],distance,(template['id'],start,target))
                        self.assertEqual(result['corridor']['base_walking_ap'],distance)


if __name__=='__main__':unittest.main()
