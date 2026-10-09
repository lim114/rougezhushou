"""Standard reports expose existing observation fields, never new game output.

Public-producer tests below use calculate_damage without mocks or injected
internal rules. The separate formatter-boundary tests use explicit synthetic
records only to check presentation and unknown preservation, not game results.
"""
from copy import deepcopy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import current_output_breakdown_sections, format_report


def request(operator,skill=1,mode='frames',**extra):
    return {'operator':operator,'skill':skill,'elite':2,'level':1,
        'skill_rank':10,'potential':1,'trust':0,'base_attack':1000,
        'enemy_defense':0,'enemy_resistance':0,'timing_mode':mode,**extra}


def blocks(result):
    return {block['id']:block for block in result['report']['sections']
            if block['id'].startswith('output_breakdown_')}


def values(block):
    return {row['key']:row['value'] for row in block['metrics']}


class CurrentOutputBreakdownPublicTests(unittest.TestCase):
    def assertComponentFields(self,result):
        """Every displayed scalar comes from the returned current observation."""
        all_rows={row['key']:row for block in blocks(result).values() for row in block['metrics']}
        for index,component in enumerate(result['components']):
            prefix='component_'+str(index)+'_'
            self.assertEqual(all_rows[prefix+'count']['value'],component['hits'])
            self.assertEqual(all_rows[prefix+'per_hit']['value'],component['per_hit'])
            self.assertEqual(all_rows[prefix+'total']['value'],component['total'])
            if 'actual_total' in component:
                self.assertEqual(all_rows[prefix+'actual_total']['value'],component['actual_total'])
        return all_rows

    def test_standard_and_technical_show_real_ordinary_current_components(self):
        for mode in ('frames','continuous'):
            with self.subTest(mode=mode):
                result=calculate_damage(request('char_4107_vrdant',2,mode,window_seconds=10))
                self.assertGreater(result['components'][0]['hits'],0)
                self.assertComponentFields(result)
                for technical in (False,True):
                    text=format_report(result,technical=technical)
                    self.assertIn('当前情景输出分项 · 伤害',text)
                    self.assertIn('技能攻击 · 单次量字段',text)
                    self.assertIn('法术伤害',text)
                    self.assertIn('分项模型总量',text)
                self.assertEqual(format_estimate(result),format_report(result))

    def test_window_detail_is_not_replaced_by_full_skill_hit_counts(self):
        for mode in ('frames','continuous'):
            short=calculate_damage(request('char_4107_vrdant',2,mode,window_seconds=2))
            longer=calculate_damage(request('char_4107_vrdant',2,mode,window_seconds=10))
            self.assertComponentFields(short)
            self.assertComponentFields(longer)
            self.assertLess(short['components'][0]['hits'],longer['components'][0]['hits'])
            self.assertEqual(short['estimate']['skill']['hit_counts'],longer['estimate']['skill']['hit_counts'])
            self.assertIn('该窗口字段，不是完整施放或本轮周期',format_report(short))

    def test_probability_source_retains_expectation_label_and_raw_share(self):
        result=calculate_damage(request('char_1041_angel2',1,window_seconds=3))
        index=next(i for i,c in enumerate(result['components']) if c['name']=='火力电台期望轰炸')
        component=result['components'][index]
        self.assertGreater(component['hits'],0)
        rows=self.assertComponentFields(result)
        self.assertIn('期望次数/份额',rows['component_'+str(index)+'_count']['label'])
        self.assertIn('不证明实际攻击次数',format_report(result))

    def test_unknown_coordinate_keeps_overall_unknown_and_separate_condition_reference(self):
        for mode in ('frames','continuous'):
            result=calculate_damage(request('char_1041_angel2',3,mode,window_seconds=10))
            self.assertIsNone(result['total_damage'])
            index=next(i for i,c in enumerate(result['components']) if c['name']=='投递坐标轰炸')
            self.assertIsNone(result['components'][index]['actual_total'])
            self.assertGreater(result['components'][index]['total'],0)
            rows=self.assertComponentFields(result)
            self.assertIn('条件总量参考',rows['component_'+str(index)+'_total']['label'])
            self.assertIsNone(rows['component_'+str(index)+'_actual_total']['value'])
            text=format_report(result)
            self.assertIn('整体伤害仍未知',text)
            self.assertIn('实际总量未知',text)
            self.assertIsNone(result['total_damage'])

    def test_medical_amiya_damage_healing_and_regeneration_have_separate_groups(self):
        for mode in ('frames','continuous'):
            result=calculate_damage(request('char_1037_amiya3',2,mode,window_seconds=10))
            detail=blocks(result)
            self.assertEqual(set(detail),{'output_breakdown_damage','output_breakdown_healing',
                'output_breakdown_regeneration'})
            self.assertComponentFields(result)
            self.assertIsNone(result['total_damage'])
            self.assertIsNone(result['total_healing'])
            text=format_report(result)
            self.assertIn('整体治疗仍未知',text)
            self.assertIn('独立生命回复不并入伤害或直接治疗',text)
            self.assertIn('潜在治疗不等于有效受疗',text)

    def test_existing_legacy_healing_fields_keep_capped_public_total(self):
        for mode in ('frames','continuous'):
            result=calculate_damage(request('kaltsit',1,mode,window_seconds=10,healing_targets=2))
            self.assertNotIn('components',result)
            rows=values(blocks(result)['output_breakdown_healing'])
            self.assertEqual(rows['component_0_count'],result['hits'])
            self.assertEqual(rows['component_0_per_hit'],result['per_heal'])
            self.assertEqual(rows['component_0_total'],result['total_healing'])
            self.assertEqual(result['total_healing'],result['estimate']['skill']['window_healing'])
            self.assertIn('不生成事件、额外目标次数或类型',format_report(result))

    def test_real_temporary_attack_events_show_amount_range_without_phase_range(self):
        result=calculate_damage(request('mechanist',3,window_seconds=20,
            relic_ids=['rogue_6_relic_legacy_61'],
            timing={'windup_frames':6,'recovery_frames':0,'projectile_travel_seconds':0}))
        component=next(c for c in result['components'] if c['name']=='轰击')
        self.assertGreater(len(component['event_amounts']),1)
        self.assertLess(min(component['event_amounts']),max(component['event_amounts']))
        index=result['components'].index(component);prefix='component_'+str(index)+'_'
        rows=self.assertComponentFields(result)
        self.assertEqual(rows[prefix+'event_mean']['value'],sum(component['event_amounts'])/len(component['event_amounts']))
        self.assertEqual(rows[prefix+'event_min']['value'],min(component['event_amounts']))
        self.assertEqual(rows[prefix+'event_max']['value'],max(component['event_amounts']))
        self.assertNotIn('range',rows[prefix+'event_min'])
        self.assertNotIn('range',rows[prefix+'event_max'])
        self.assertIn('已给逐事件量均值',format_report(result))

    def test_buildup_is_not_placed_in_life_damage_details(self):
        result=calculate_damage(request('char_1042_phatm2',3,window_seconds=10))
        self.assertComponentFields(result)
        detail=blocks(result)
        self.assertIn('output_breakdown_buildup',detail)
        buildup_indexes=[i for i,c in enumerate(result['components']) if c['damage_type']=='buildup']
        damage_rows=values(detail['output_breakdown_damage'])
        for index in buildup_indexes:
            self.assertNotIn('component_'+str(index)+'_total',damage_rows)
        self.assertIn('损伤积累不是敌人生命伤害',format_report(result))

    def test_formatting_preserves_caller_and_complete_returned_graph(self):
        caller=request('char_1037_amiya3',2,window_seconds=10)
        before=deepcopy(caller);result=calculate_damage(caller);saved=deepcopy(result)
        self.assertEqual(caller,before)
        for technical in (False,True):format_report(result,technical=technical)
        format_estimate(result);current_output_breakdown_sections(result)
        self.assertEqual(result,saved)
        self.assertEqual(caller,before)


class CurrentOutputBreakdownFormatterBoundaryTests(unittest.TestCase):
    """Synthetic field contracts; none of these records prove game output."""
    def test_none_and_condition_total_are_preserved_without_fabricating_output(self):
        fixture={'total_damage':None,'total_healing':None,'components':[
            {'name':'未核来源','damage_type':'physical','hits':None,'per_hit':None,
             'total':42,'actual_total':None}]}
        before=deepcopy(fixture);block=current_output_breakdown_sections(fixture)[0];rows=values(block)
        self.assertIsNone(rows['component_0_count'])
        self.assertIsNone(rows['component_0_per_hit'])
        self.assertIsNone(rows['component_0_actual_total'])
        self.assertEqual(rows['component_0_total'],42)
        self.assertTrue(any('整体伤害仍未知' in note for note in block['notes']))
        self.assertEqual(fixture,before)

    def test_variable_event_amounts_do_not_replace_per_hit_or_recompute_total(self):
        fixture={'total_damage':999,'components':[{'name':'格式字段样本','damage_type':'physical',
            'hits':7.5,'per_hit':123,'event_amounts':[10,12],'total':999}]}
        block=current_output_breakdown_sections(fixture)[0];rows=values(block)
        self.assertEqual(rows['component_0_count'],7.5)
        self.assertEqual(rows['component_0_per_hit'],123)
        self.assertEqual(rows['component_0_total'],999)
        self.assertEqual(rows['component_0_event_mean'],11)
        self.assertEqual(rows['component_0_event_min'],10)
        self.assertEqual(rows['component_0_event_max'],12)
        self.assertTrue(all('range' not in row for row in block['metrics']))

    def test_partial_event_amounts_cannot_be_filtered_into_a_known_mean(self):
        fixture={'components':[{'name':'部分格式样本','damage_type':'physical','hits':2,
            'per_hit':None,'event_amounts':[100,None],'total':None}]}
        block=current_output_breakdown_sections(fixture)[0];rows=values(block)
        self.assertNotIn('component_0_event_mean',rows)
        self.assertNotIn('component_0_event_min',rows)
        self.assertNotIn('component_0_event_max',rows)
        self.assertIsNone(rows['component_0_total'])
        self.assertTrue(any('未生成均值和范围' in note for note in block['notes']))

    def test_legacy_total_is_not_rebuilt_from_fractional_count_times_per_hit(self):
        fixture={'hits':3.5,'per_hit':1.2,'total_damage':10,'total_healing':0}
        before=deepcopy(fixture);rows=values(current_output_breakdown_sections(fixture)[0])
        self.assertEqual(rows['component_0_count'],3.5)
        self.assertEqual(rows['component_0_per_hit'],1.2)
        self.assertEqual(rows['component_0_total'],10)
        self.assertEqual(fixture,before)

    def test_empty_components_and_utility_outputs_create_no_fabricated_rows(self):
        self.assertEqual(current_output_breakdown_sections({'components':[],
            'hits':3,'per_hit':5,'total_damage':15}),[])
        self.assertEqual(current_output_breakdown_sections({'total_damage':0,'total_healing':0}),[])

    def test_independent_reply_and_unknown_type_preserve_their_own_values(self):
        fixture={'total_damage':0,'total_healing':0,'components':[
            {'name':'格式回复样本','damage_type':'regeneration','hits':1.5,'per_hit':7,'total':10.5},
            {'name':'格式未知类型','damage_type':'opaque_source','hits':None,'per_hit':None,'total':None}]}
        detail={b['id']:b for b in current_output_breakdown_sections(fixture)}
        self.assertEqual(set(detail),{'output_breakdown_regeneration','output_breakdown_other'})
        self.assertEqual(values(detail['output_breakdown_other'])['component_1_type'],'opaque_source')
        self.assertEqual(values(detail['output_breakdown_regeneration'])['component_0_total'],10.5)
