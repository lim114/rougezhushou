import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from rouge.animation_reference import choices,descriptor,three_part_profile
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.three_part_wait import fixed_wait_ticks,project_wait_budget
from rouge.timing import AttackTimeline


class ThreePartWaitBudgetCurrentTests(unittest.TestCase):
    def ref(self):
        return next(r['id'] for r in choices('kaltsit',1)
                    if r['animation']=='Attack_Loop' and r['orientation']=='Front')

    def stream(self,seconds=3,interval=2.5,**timing):
        timeline=AttackTimeline({'operator':'kaltsit','skill':1,
            'timing':{'animation_reference':self.ref(),**timing}})
        result=timeline.attacks(seconds,interval)
        return result,result['three_part_reference']['wait_budget']

    def test_float_nearest_even_clamp_and_float32_boundary_are_not_ceil(self):
        self.assertEqual([fixed_wait_ticks(v,1) for v in [0,-.1,.1,1.49,1.5,2.5,3.5]],
                         [1,1,1,1,2,2,4])
        # The installed float path divides in single precision. 0.25 / the
        # preview's single-precision 1/30 lies just below 7.5, not at 8 ticks.
        self.assertEqual(fixed_wait_ticks(.25,1/30),7)
        self.assertEqual(fixed_wait_ticks(2.25,1/30),68)
        self.assertEqual(fixed_wait_ticks(.01,1/30),1)

    def test_invalid_duration_and_delta_do_not_create_wait_counts(self):
        for time,delta in [(True,1),(1,False),(None,1),(1,None),(float('inf'),1),
                           (1,float('nan')),(3601,1),(1,0),(1,-1),(1,1e-320)]:
            with self.subTest(time=time,delta=delta),self.assertRaises(ValueError):fixed_wait_ticks(time,delta)

    def test_each_segment_quantizes_independently_and_two_gates_remain_separate(self):
        _,budget=self.stream(interval=2.55)
        first,again=budget['conditional_budgets']
        self.assertEqual([s['wait_ticks'] for s in first['segments']],[8,69,0])
        self.assertEqual(first['total_wait_ticks'],77)
        self.assertEqual([s['wait_ticks'] for s in again['segments']],[0,76,0])
        self.assertEqual(again['total_wait_ticks'],76)
        self.assertNotEqual(first['total_wait_ticks'],fixed_wait_ticks(2.55,1/30))
        self.assertIsNone(first['restart_first_attack_gate_actual'])
        self.assertIsNone(again['restart_first_attack_gate_actual'])

    def test_skipped_empty_segments_are_not_called_zero_duration_waits(self):
        _,budget=self.stream()
        first,again=budget['conditional_budgets']
        self.assertEqual(first['segments'][0]['wait_ticks'],7)
        self.assertFalse(again['segments'][0]['played_in_this_condition'])
        self.assertEqual(again['segments'][0]['wait_ticks'],0)
        self.assertFalse(first['segments'][2]['configured'])
        self.assertEqual(first['segments'][2]['wait_ticks'],0)
        self.assertEqual(fixed_wait_ticks(0,1/30),1)

    def test_window_budget_consumes_then_preserves_remaining_waiting(self):
        _,budget=self.stream(seconds=.5)
        for case in budget['conditional_budgets']:
            self.assertEqual(case['total_wait_ticks'],75)
            self.assertEqual(case['spent_wait_ticks'],15)
            self.assertEqual(case['remaining_wait_ticks'],60)
            self.assertFalse(case['reference_waits_exhausted'])
        first=budget['conditional_budgets'][0]
        self.assertEqual(first['segments'][0]['reference_state'],'wait_exhausted')
        self.assertEqual(first['segments'][1]['reference_state'],'waiting_at_window_end')

    def test_half_open_window_completion_at_boundary_is_not_callback_inside_window(self):
        _,at=self.stream(seconds=2.5)
        for case in at['conditional_budgets']:
            self.assertTrue(case['reference_waits_exhausted'])
            self.assertFalse(case['reference_completion_inside_window'])
            self.assertEqual(case['remaining_wait_ticks'],0)
            self.assertIsNone(case['actual_callback_frame'])
            self.assertIsNone(case['actual_finish_frame'])
        _,after=self.stream(seconds=2.5+1/30)
        self.assertTrue(all(c['reference_completion_inside_window'] for c in after['conditional_budgets']))

    def test_declared_interrupt_cancels_budget_and_resume_candidate_respects_windows(self):
        _,budget=self.stream(interrupt_windows=[[.5,.8],[.7,.9]],movement_windows=[[.8,1]])
        for case in budget['conditional_budgets']:
            self.assertEqual(case['declared_interruption_frame'],15)
            self.assertEqual(case['spent_wait_ticks'],15)
            self.assertEqual(case['remaining_wait_ticks'],60)
            self.assertEqual(case['discarded_wait_ticks_due_to_declared_interruption'],60)
            self.assertEqual(case['pending_wait_ticks_at_window_end'],0)
            self.assertTrue(case['resume_is_restart_candidate_not_continuation'])
            self.assertEqual(case['reference_resume_candidate_frame'],30)
            self.assertTrue(case['reference_resume_candidate_inside_window'])
            self.assertFalse(case['reference_waits_exhausted'])
            self.assertIsNone(case['restart_first_attack_gate_actual'])
        self.assertEqual(budget['conditional_budgets'][0]['segments'][1]['reference_state'],'declared_interruption')

    def test_initial_declared_interrupt_preserves_whole_chain_budget(self):
        _,budget=self.stream(interrupt_windows=[[0,.2]])
        for case in budget['conditional_budgets']:
            self.assertEqual(case['declared_interruption_frame'],0)
            self.assertEqual(case['spent_wait_ticks'],0)
            self.assertEqual(case['remaining_wait_ticks'],75)
            self.assertEqual(case['reference_resume_candidate_frame'],6)

    def test_interrupt_start_at_completion_or_horizon_does_not_cancel_earlier(self):
        _,done=self.stream(interrupt_windows=[[2.5,2.6]])
        self.assertTrue(all(c['declared_interruption_frame'] is None and c['reference_waits_exhausted']
                            for c in done['conditional_budgets']))
        _,cut_after=self.stream(seconds=.5,interrupt_windows=[[.5,.8]])
        self.assertTrue(all(c['declared_interruption_frame'] is None and c['spent_wait_ticks']==15
                            for c in cut_after['conditional_budgets']))

    def test_movement_and_target_gap_do_not_clear_waits_or_reopen_gate(self):
        _,plain=self.stream()
        _,declared=self.stream(movement_windows=[[.2,.8]],target_windows=[[0,.2],[1,2]])
        self.assertEqual(plain['conditional_budgets'],declared['conditional_budgets'])
        self.assertEqual(declared['movement_windows'],[(6,24)])
        self.assertEqual(declared['target_windows'],[(0,6),(30,60)])
        self.assertIsNone(declared['movement_or_target_gap_clears_wait'])
        self.assertIsNone(declared['actual_fsm_path'])
        self.assertIn('OnEnter传true',declared['gate_rule'])

    def offset_stream(self,**timing):
        ref=next(r['id'] for r in choices('kaltsit',1,normal=True) if r['orientation']=='Front')
        source={'operator':'kaltsit','skill':1,'timing':{'normal_animation_reference':ref,**timing}}
        before=copy.deepcopy(source)
        stream=AttackTimeline(source,normal=True,offset=2).attacks(3,2.5)
        self.assertEqual(source,before)
        return stream['three_part_reference']['wait_budget']

    def test_recharge_offset_discards_past_local_windows_without_losing_declarations(self):
        b=self.offset_stream(movement_windows=[[0,1]],interrupt_windows=[[.5,1]],target_windows=[[0,1],[2,3]])
        self.assertEqual(b['declaration_offset_frame'],60)
        self.assertEqual(b['movement_windows'],[]);self.assertEqual(b['interrupt_windows'],[])
        self.assertEqual(b['target_windows'],[(0,30)])
        self.assertEqual(b['absolute_declared_windows']['interrupt_windows'],[(15,30)])
        self.assertTrue(all(c['declared_interruption_frame'] is None for c in b['conditional_budgets']))

    def test_recharge_offset_clips_cross_origin_declared_interrupt_only_in_local_budget(self):
        b=self.offset_stream(interrupt_windows=[[1,2.5]],movement_windows=[[2.5,3]])
        self.assertEqual(b['interrupt_windows'],[(0,15)]);self.assertEqual(b['movement_windows'],[(15,30)])
        self.assertEqual(b['absolute_declared_windows']['interrupt_windows'],[(30,75)])
        self.assertTrue(all(c['declared_interruption_frame']==0 and c['reference_resume_candidate_frame']==30
                            and c['pending_wait_ticks_at_window_end']==0 for c in b['conditional_budgets']))

    def test_recharge_offset_keeps_future_windows_on_the_relative_grid(self):
        b=self.offset_stream(interrupt_windows=[[3,4]])
        self.assertEqual(b['interrupt_windows'],[(30,60)])
        self.assertEqual(b['absolute_declared_windows']['interrupt_windows'],[(90,120)])
        self.assertTrue(all(c['declared_interruption_frame']==30 and c['spent_wait_ticks']==30
                            and c['reference_resume_candidate_frame']==60 for c in b['conditional_budgets']))

    def test_empty_target_and_future_origin_do_not_invent_actual_chain(self):
        stream,budget=self.stream(target_windows=[])
        self.assertEqual(stream['start_frames'],[])
        self.assertTrue(budget['assumes_reference_chain_started_at_origin'])
        self.assertIsNone(budget['actual_target_acquisition_frame'])
        self.assertIsNone(budget['actual_fsm_path'])
        _,later=self.stream(seconds=1,start_delay_frames=90)
        self.assertEqual(later['reference_origin_frame'],90)
        self.assertTrue(all(c['spent_wait_ticks']==0 and c['remaining_wait_ticks']==75
                            for c in later['conditional_budgets']))

    def test_actual_delta_route_phase_and_first_release_stay_unknown(self):
        stream,budget=self.stream()
        self.assertEqual(budget['grid_fps'],30)
        self.assertTrue(budget['grid_delta_is_existing_preview_parameter'])
        for key in ('actual_delta_play_time_seconds','actual_scheduler_route','actual_resume_phase'):
            self.assertIsNone(budget[key])
        self.assertFalse(budget['runtime_binding_verified'])
        self.assertFalse(stream['known_animation'])
        self.assertIsNone(stream['actual_first_release_seconds'])
        self.assertTrue(budget['profile_playback_kept_fixed_as_reference_condition'])
        self.assertIsNone(budget['actual_midchain_playback_change'])

    def test_actual_calculation_and_report_consume_existing_declarations(self):
        scenario={'operator':'kaltsit','skill':1,'timing':{'animation_reference':self.ref(),
            'interrupt_windows':[[.5,.8]],'movement_windows':[[.8,1]],'target_windows':[[0,.3],[2,3]]}}
        before=copy.deepcopy(scenario);result=calculate_damage(scenario)
        budget=result['timing']['streams'][0]['three_part_reference']['wait_budget']
        self.assertEqual(budget['conditional_budgets'][0]['declared_interruption_frame'],15)
        report=next(s for s in result['report']['sections'] if s['id'].startswith('three_part_wait_'))
        labels={m['label'] for m in report['metrics']}
        for condition in ('开始段门成立','开始段门不成立'):
            self.assertIn(condition+'：窗口末未执行预算',labels)
            self.assertIn(condition+'：声明中断后的重新开始候选',labels)
        text=format_estimate(result)
        for phrase in ('三段等待与声明窗口预算','现有预览网格参数','不重开firstAttack门','实际取得目标/开始仍未知','取消等待并不证明原动画或伤害事件已停止'):
            self.assertIn(phrase,text)
        self.assertEqual(scenario,before)

    def test_default_without_reference_never_calls_budget_or_changes_numbers(self):
        for scenario in [{'operator':'kaltsit','skill':1},{'operator':'silverash','skill':3},
                         {'operator':'mechanist','skill':2,'shield_break_count':2}]:
            before=calculate_damage(scenario)
            with patch('rouge.three_part_wait.project_wait_budget',side_effect=AssertionError('must not auto select')):
                self.assertEqual(calculate_damage(scenario),before)

    def test_normal_recharge_reference_is_scoped_and_continuous_mode_does_not_fake_frame_waits(self):
        ref=next(r['id'] for r in choices('silverash',3,normal=True) if r['animation']=='Attack_A')
        result=calculate_damage({'operator':'silverash','skill':3,'timing':{'normal_animation_reference':ref}})
        self.assertNotIn('three_part_reference',result['timing']['streams'][0])
        self.assertTrue(any(s.get('three_part_reference',{}).get('wait_budget')
                            for s in result['timing']['recharge_streams']))
        result=calculate_damage({'operator':'kaltsit','skill':1,'timing_mode':'continuous',
            'timing':{'animation_reference':self.ref()}})
        self.assertNotIn('wait_budget',result['timing']['streams'][0]['three_part_reference'])

    def test_budget_copies_inputs_and_does_not_modify_conditional_duration_profiles(self):
        data=descriptor('kaltsit',1,{'animation_reference':self.ref()})
        parts=three_part_profile(data,2.5);before=copy.deepcopy(parts)
        windows=[[15,24]]
        budget=project_wait_budget(parts,data['three_part_reference'],fps=30,origin_frame=0,
            horizon_frames=90,interrupt_windows=windows)
        budget['interrupt_windows'].clear();budget['conditional_budgets'][0]['segments'].clear()
        self.assertEqual(parts,before);self.assertEqual(windows,[[15,24]])

    def test_current_native_wait_and_first_gate_rules_are_exact_and_bounded(self):
        root=Path(__file__).resolve().parents[1]/'research/p2-three-part-wait-current'
        native=json.loads((root/'native-proof.json').read_text(encoding='utf-8'))
        exact=next(r for r in native['method_records'] if r['method'].get('metadata_method_index')==64149)
        self.assertEqual(exact['method']['Address'],0x180661350)
        self.assertEqual(exact['method']['declaring_type'],'Torappu.Battle.AsyncUtil+<WaitForFixedSeconds>d__0')
        self.assertEqual(exact['instruction_count'],63)
        self.assertTrue(all(not r['limits'] and r['cfg_bounded_traversal_finished'] for r in native['method_records']))
        ids={r['method'].get('metadata_method_index') for r in native['method_records']}
        self.assertTrue({64127,64149,64245,76192,76195,76196,76200,91665}<=ids)
        meta=json.loads((root/'selected-metadata.json').read_text(encoding='utf-8'))
        yields=next(t for t in meta['selected'] if t['name']=='Torappu.Battle.Yields')
        fixed=next(f for f in yields['fields'] if f['offset']==0)
        self.assertEqual((fixed['name'],fixed['type']),('sharedWaitForFixedUpdate','UnityEngine.WaitForFixedUpdate'))
        receipt=json.loads((root/'receipt.json').read_text(encoding='utf-8'))
        self.assertIn('FP overload64132/64179',receipt['different_overload_boundary'])
        self.assertFalse(native['current_hotfix_equivalence_proven'])


if __name__=='__main__':unittest.main()
