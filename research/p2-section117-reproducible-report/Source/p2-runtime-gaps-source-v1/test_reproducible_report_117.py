"""Real producer visibility; synthetic formatter boundaries are explicitly marked.

Source candidate only until Root actually executes. New report tables copy
existing fields and do not establish native client events or unknown mechanics.
"""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import (format_report, event_clock_reference_sections,
                             reproducible_context_sections)
from tests.test_token_full_cast_tail_111 import scenario as token_scenario, TOKEN


def values(block):
    return {row['key']:row['value'] for row in block['metrics']}


def section(result,identity):
    return next(block for block in result['report']['sections'] if block['id']==identity)


def new_sections(result):
    return [block for block in result['report']['sections'] if block['id']=='calculation_context'
            or block['id'].startswith(('event_clock_','output_domain_'))]


class ReproducibleReport117Tests(unittest.TestCase):
    def calculate(self,args):
        before=copy.deepcopy(args)
        result=calculate_damage(args)
        self.assertEqual(args,before)
        graph=copy.deepcopy(result)
        ordinary=format_report(result)
        technical=format_report(result,technical=True)
        self.assertEqual(format_estimate(result),ordinary)
        self.assertIsInstance(technical,str)
        self.assertEqual(result,graph)
        return result

    def clocks(self,result,key='streams'):
        return [block for block in new_sections(result) if block['id'].startswith('event_clock_'+key+'_')]

    def assert_clock_fields(self,result,key='streams'):
        streams=result['timing'].get(key,[])
        blocks=self.clocks(result,key)
        self.assertEqual(len(blocks),len(streams))
        for index,(stream,block) in enumerate(zip(streams,blocks,strict=True)):
            self.assertEqual(block['id'],'event_clock_'+key+'_'+str(index))
            actual=values(block)
            for field in ('start_frames','release_frames','impact_frames','times_seconds',
                          'emitted_impact_frames','emitted_times_seconds'):
                expected=stream.get(field)
                self.assertEqual(actual[field+'_count'],len(expected) if expected is not None else None)
                self.assertEqual(actual[field+'_first'],expected[0] if expected else None)
                self.assertEqual(actual[field+'_last'],expected[-1] if expected else None)

    def test_fixed_impact_boundary_release_and_impact_records_stay_distinct(self):
        args={'operator':'mechanist','skill':3,'base_attack':1000,
              'timing':{'windup_frames':6,'recovery_frames':9}}
        edge=self.calculate({**args,'window_seconds':1})
        after=self.calculate({**args,'window_seconds':31/30})
        self.assertEqual(values(self.clocks(edge)[0])['release_frames_count'],1)
        self.assertEqual(values(self.clocks(edge)[0])['impact_frames_count'],0)
        self.assertIsNone(values(self.clocks(edge)[0])['impact_frames_first'])
        self.assertEqual(values(self.clocks(after)[0])['impact_frames_first'],30)
        for result in (edge,after):self.assert_clock_fields(result)

    def test_token_tail_owner_and_recharge_have_separate_records(self):
        result=self.calculate(token_scenario())
        self.assert_clock_fields(result)
        self.assert_clock_fields(result,'recharge_streams')
        token_index=next(i for i,s in enumerate(result['timing']['streams']) if s['unit']==TOKEN)
        block=self.clocks(result)[token_index]
        self.assertIn('触手',block['title'])
        actual=values(block)
        self.assertEqual(actual['impact_frames_count'],16)
        self.assertEqual(actual['emitted_impact_frames_count'],24)
        self.assertGreater(actual['emitted_times_seconds_last'],result['estimate']['skill']['duration_seconds'])

    def test_zero_summons_does_not_promote_representative_stream_to_presence(self):
        result=self.calculate(token_scenario(count=0))
        self.assertEqual(next(c for c in result['components'] if c['name']=='触手')['hits'],0)
        token_index=next(i for i,s in enumerate(result['timing']['streams']) if s['unit']==TOKEN)
        block=self.clocks(result)[token_index]
        self.assertGreater(values(block)['release_frames_count'],0)
        self.assertIn('多只或零只', '\n'.join(block['notes']))

    def test_same_owner_enemy_and_friendly_streams_are_not_merged(self):
        result=self.calculate({'operator':'char_2025_shu','skill':3,'window_seconds':5,
            'healing_targets':1,'timing':{'windup_frames':0,'recovery_frames':0}})
        self.assertGreaterEqual(len(result['timing']['streams']),2)
        self.assert_clock_fields(result)
        scopes=[values(block)['target_scope'] for block in self.clocks(result)]
        self.assertIn('敌方获取参考',scopes)
        self.assertIn('友方获取参考',scopes)
        self.assertEqual(len({block['id'] for block in self.clocks(result)}),len(scopes))

    def test_disappearance_keeps_release_reference_without_late_impact(self):
        result=self.calculate({'operator':'mechanist','skill':3,'window_seconds':2,
            'timing':{'windup_frames':6,'recovery_frames':9,'target_disappears_seconds':.3}})
        actual=values(self.clocks(result)[0])
        self.assertGreater(actual['release_frames_count'],0)
        self.assertEqual(actual['emitted_impact_frames_count'],0)
        self.assert_clock_fields(result)

    def test_empty_enemy_lifetime_keeps_friendly_potential_healing(self):
        result=self.calculate({'operator':'char_298_susuro','skill':1,'window_seconds':10,
            'timing':{'target_disappears_seconds':0}})
        self.assertGreater(result['total_healing'],0)
        self.assertEqual(values(self.clocks(result)[0])['target_scope'],'友方获取参考')
        self.assertIn('敌方供靶不等于友方受疗资格','\n'.join(section(result,'calculation_context')['notes']))

    def test_phase_unknowns_remain_unknown_beside_acquisition_reference(self):
        result=self.calculate({'operator':'char_206_gnosis','skill':1,'window_seconds':5})
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['gnosis_s1_reference']['relative_hit_times_seconds'])
        compared=values(section(result,'output_domain_damage'))
        for key in ('cast_total','phase_total','cycle_total','cycle_seconds'):
            self.assertIsNone(compared[key])
        self.assert_clock_fields(result)

    def test_unplaced_shield_breaks_are_not_given_new_collision_events(self):
        result=self.calculate({'operator':'mechanist','skill':2,'shield_break_count':2,
            'skill_duration_seconds':20})
        self.assertIsNone(result['shield_break_reference']['actual_collision_times_seconds'])
        self.assertFalse(result['timing']['resource_and_damage_shared_clock'])
        self.assertIn('未绑定','\n'.join(note for block in self.clocks(result) for note in block['notes']))
        self.assertIsNone(values(section(result,'output_domain_damage'))['cast_total'])

    def test_continuous_reference_has_no_invented_frame_stream_sections(self):
        result=self.calculate({'operator':'char_002_amiya','skill':1,'window_seconds':10,
            'timing_mode':'continuous','timing':{'target_disappears_seconds':.1}})
        self.assertEqual(self.clocks(result),[])
        self.assertEqual(self.clocks(result,'recharge_streams'),[])
        self.assertIsNone(result['total_damage'])
        self.assertIn('连续模式保持既有参数参考','\n'.join(section(result,'calculation_context')['notes']))

    def test_finite_ammo_window_cast_phase_and_cycle_copy_the_existing_domains(self):
        result=self.calculate({'operator':'mechanist','skill':1,'window_seconds':60})
        skill=result['estimate']['skill'];actual=values(section(result,'output_domain_damage'))
        self.assertEqual(actual['window_seconds'],60)
        self.assertEqual(actual['window_total'],result['total_damage'])
        self.assertEqual(actual['cast_total'],skill['total_damage'])
        self.assertEqual(actual['phase_total'],skill['phase_damage'])
        self.assertEqual(actual['cycle_total'],skill['cycle_damage'])
        self.assertEqual(actual['cycle_average'],skill['cycle_dps'])

    def test_known_partial_damage_is_listed_without_filling_whole_unknowns(self):
        result=self.calculate({'operator':'char_1042_phatm2','skill':3,'window_seconds':2})
        actual=values(section(result,'output_domain_damage'))
        self.assertIsNone(actual['window_total'])
        self.assertIsNone(actual['cast_total'])
        for key in ('window_damage','total_damage','phase_damage','cycle_damage'):
            self.assertEqual(actual['known_'+key],result['known_damage_subtotals'][key])

    def test_known_partial_healing_is_listed_without_filling_whole_unknowns(self):
        result=self.calculate({'operator':'char_2025_shu','skill':1,'window_seconds':5,
            'healing_targets':1})
        actual=values(section(result,'output_domain_healing'))
        self.assertIsNone(actual['window_total'])
        self.assertIsNone(actual['cast_total'])
        self.assertIsNone(result['next_attack_healing_reference']['actual_acquisition_times_seconds'])
        for key in ('window_healing','total_healing','phase_healing','cycle_healing'):
            self.assertEqual(actual['known_'+key],result['known_healing_subtotals'][key])

    def test_target_resolution_summary_does_not_reuse_overwritten_manual_inputs(self):
        result=self.calculate({'operator':'mechanist','skill':1,'enemy_defense':999,
            'enemy_resistance':99,'target_enemy':{'stage_id':'ro6_n_1_2',
              'enemy_id':'enemy_1093_ccsbr','level':0},'run_config':{'difficulty':{'value':0}}})
        stats=result['run_resolution']['enemy']['stats'];actual=values(section(result,'calculation_context'))
        self.assertEqual(actual['enemy_defense'],stats['def'])
        self.assertEqual(actual['enemy_resistance'],stats['magicResistance'])
        self.assertEqual(actual['target_source'],'所选关卡敌人资料及已接入修正')

    def test_declared_empty_positive_initial_and_independent_conditions_are_visible(self):
        args=token_scenario(unit_extra={'target_windows':[[28,30]]},
                            window=30)
        args['timing'].update(target_windows=[],initial_target_windows=[[0,3]],
                              movement_windows=[[2,3]],interrupt_windows=[])
        result=self.calculate(args)
        notes='\n'.join(section(result,'calculation_context')['notes'])
        for expected in ('敌方可获取区间：明确为空','初动敌方可获取区间：[0, 3)',
                         '移动区间：[2, 3)','打断区间：明确为空','触手声明 · 敌方可获取区间：[28, 30)'):
            self.assertIn(expected,notes)

    def test_raw_numeric_string_declaration_renders_without_new_type_error(self):
        args={'operator':'mechanist','skill':1,'window_seconds':'0'}
        result=self.calculate(args)
        # Formatter-only direct rebuild uses the public raw declaration, as can
        # existing envelope branches; no project calculator re-execution here.
        blocks=reproducible_context_sections(args,result)
        current=copy.deepcopy(result)
        current['report']['sections']=[blocks[0]]
        self.assertIn('声明的观察窗口：0 秒',format_report(current))
        self.assertEqual(values(blocks[0])['window'],0)

    def test_formatter_only_missing_empty_and_repeated_event_arrays_are_distinct(self):
        args={'operator':'char_002_amiya','skill':1}
        result={'timing':{'mode':'frames','streams':[{'unit':args['operator'],
            'target_scope':'enemy','release_frames':[0,0,3],'times_seconds':[],
            'emitted_times_seconds':None}], 'recharge_streams':[]}}
        before=copy.deepcopy(result)
        actual=values(event_clock_reference_sections(args,result)[0])
        self.assertEqual(actual['release_frames_count'],3)
        self.assertEqual(actual['release_frames_first'],0)
        self.assertEqual(actual['release_frames_last'],3)
        self.assertEqual(actual['times_seconds_count'],0)
        self.assertIsNone(actual['times_seconds_first'])
        self.assertIsNone(actual['impact_frames_count'])
        self.assertIsNone(actual['emitted_times_seconds_count'])
        self.assertEqual(result,before)

    def test_output_capability_does_not_add_healing_domain_to_flag_skill_one(self):
        result=self.calculate({'operator':'char_151_myrtle','skill':1})
        identities={block['id'] for block in new_sections(result)}
        self.assertNotIn('output_domain_healing',identities)
        self.assertNotIn('潜在治疗口径对照',format_report(result))


if __name__=='__main__':unittest.main()
