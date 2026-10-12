"""Source-bound three-part waits on the existing declared preview grid.

This accounts for waiting and a declared cancellation. It does not identify a
client tick phase, a currently selected FSM path, or an attack-event callback.
"""
from copy import deepcopy
import math
import struct


SOURCE='research/p2-three-part-wait-current/receipt.json'


def _f32(value):
    try:value=struct.unpack('<f',struct.pack('<f',value))[0]
    except (OverflowError,struct.error):raise ValueError('等待参考超出原生浮点范围。') from None
    if not math.isfinite(value):raise ValueError('等待参考需要有限浮点数。')
    return value


def fixed_wait_ticks(seconds,delta_seconds):
    """Float overload: max(1, nearest-even(float32(time / delta)))."""
    if isinstance(seconds,bool) or isinstance(delta_seconds,bool):
        raise ValueError('等待参考秒数不能为布尔值。')
    try:seconds=float(seconds);delta_seconds=float(delta_seconds)
    except (TypeError,ValueError,OverflowError):raise ValueError('等待参考需要有限秒数。') from None
    if not math.isfinite(seconds) or not -3600<=seconds<=3600:
        raise ValueError('等待参考时长需要范围内有限秒数。')
    if not math.isfinite(delta_seconds) or not 0<delta_seconds<=3600:
        raise ValueError('等待步长参考需要有限正秒数。')
    delta=_f32(delta_seconds)
    if delta<=0:raise ValueError('等待步长参考不足以表示正的原生浮点数。')
    ratio=_f32(_f32(seconds)/delta)
    count=max(1,round(ratio))
    if count>2147483647:raise ValueError('等待参考超出已核验的32位计数范围。')
    return count


def _intervals(value):
    rows=[]
    for pair in value:
        if (not isinstance(pair,(tuple,list)) or len(pair)!=2 or
                any(type(v) is not int or v<0 for v in pair) or pair[1]<=pair[0]):
            raise ValueError('等待窗口需要非负整数帧的有效区间。')
        rows.append(tuple(pair))
    return sorted(rows)


def _unblocked_after(frame,interrupts,movement):
    # A permitted preview restart is a candidate only. It does not imply that
    # the FSM exited, reentered, found a target, or selected this action again.
    while True:
        later=max((b for a,b in [*interrupts,*movement] if a<=frame<b),default=frame)
        if later==frame:return frame
        frame=later


def project_wait_budget(parts,plan,*,fps,origin_frame,horizon_frames,
                        interrupt_windows=(),movement_windows=(),target_windows=None,
                        declaration_offset_frame=0,absolute_declared_windows=None):
    if (type(fps) is not int or not 1<=fps<=240 or
            type(origin_frame) is not int or origin_frame<0 or
            type(horizon_frames) is not int or not 0<=horizon_frames<=108000):
        raise ValueError('等待参考网格及窗口需要范围内整数。')
    interrupts=_intervals(interrupt_windows);movement=_intervals(movement_windows)
    if target_windows is not None:target_windows=_intervals(target_windows)
    delta=1/fps
    cases=[]
    for profile in parts['conditional_profiles']:
        first=profile['first_attack_condition'];cursor=origin_frame;segments=[]
        for part in ('begin','oneshot','end'):
            configured=plan[part] is not None
            present=configured and (part!='begin' or not plan['only_begin_when_first_attack'] or first)
            duration=profile['scaled_segment_seconds'][part]
            ticks=fixed_wait_ticks(duration,delta) if present else 0
            segments.append({'segment':part,'configured':configured,'played_in_this_condition':present,
                'animation':plan[part]['animation'] if configured else None,
                'scaled_duration_seconds':duration,'wait_ticks':ticks,
                'reference_start_frame':cursor,'reference_finish_frame':cursor+ticks})
            cursor+=ticks
        finish=cursor;total=finish-origin_frame
        # Interruption is an explicit model condition, not inferred from
        # movement, a target gap, a deployment, or the native state machine.
        cuts=[max(origin_frame,a) for a,b in interrupts if a<finish and b>origin_frame]
        cut=min(cuts) if cuts else None
        observed_cut=cut if cut is not None and cut<horizon_frames else None
        observed_until=max(origin_frame,min(horizon_frames,finish,
            observed_cut if observed_cut is not None else finish))
        for segment in segments:
            begin=segment['reference_start_frame'];end=segment['reference_finish_frame']
            spent=max(0,min(observed_until,end)-begin)
            segment['spent_wait_ticks']=spent
            segment['remaining_wait_ticks']=segment['wait_ticks']-spent
            if not segment['played_in_this_condition']:state='not_played'
            elif observed_cut is not None and begin<=observed_cut<end:state='declared_interruption'
            elif observed_until>=end:state='wait_exhausted'
            elif observed_until<=begin:state='not_reached'
            else:state='waiting_at_window_end'
            segment['reference_state']=state
        exhausted=observed_cut is None and horizon_frames>=finish
        resume=_unblocked_after(observed_cut,interrupts,movement) if observed_cut is not None else None
        cases.append({'first_attack_condition':first,'segments':segments,'total_wait_ticks':total,
            'spent_wait_ticks':sum(s['spent_wait_ticks'] for s in segments),
            'remaining_wait_ticks':sum(s['remaining_wait_ticks'] for s in segments),
            'discarded_wait_ticks_due_to_declared_interruption':(
                sum(s['remaining_wait_ticks'] for s in segments) if observed_cut is not None else 0),
            'pending_wait_ticks_at_window_end':(
                0 if observed_cut is not None else sum(s['remaining_wait_ticks'] for s in segments)),
            'reference_nominal_finish_frame':finish,
            'reference_waits_exhausted':exhausted,
            'reference_completion_inside_window':exhausted and finish<horizon_frames,
            'declared_interruption_frame':observed_cut,
            'reference_resume_candidate_frame':resume,
            'reference_resume_candidate_inside_window':resume is not None and resume<horizon_frames,
            'resume_is_restart_candidate_not_continuation':True,
            'restart_first_attack_gate_actual':None,
            'actual_start_frame':None,'actual_finish_frame':None,'actual_callback_frame':None})
    # The supplied target and movement rows remain visible in the same actual
    # calculation result. Neither removes a pending wait nor reopens the gate.
    return {'source':SOURCE,'grid_fps':fps,'grid_delta_seconds':delta,
        'grid_delta_is_existing_preview_parameter':True,'actual_delta_play_time_seconds':None,
        'reference_origin_frame':origin_frame,'reference_horizon_frames':horizon_frames,
        'declaration_offset_frame':declaration_offset_frame,
        'absolute_declared_windows':deepcopy(absolute_declared_windows),
        'local_window_rebase':'只将声明区间换算到本段：已结束的区间不纳入，跨本段起点的区间夹到0；原绝对声明保留。',
        'origin_is_existing_preview_anchor':True,'assumes_reference_chain_started_at_origin':True,
        'actual_target_acquisition_frame':None,
        'uses_preview_origin_not_emitted_attack_start':True,
        'interrupt_windows':deepcopy(interrupts),'movement_windows':deepcopy(movement),
        'target_windows':deepcopy(target_windows),
        'movement_or_target_gap_clears_wait':None,
        'actual_fsm_path':None,'actual_scheduler_route':None,'actual_resume_phase':None,
        'runtime_binding_verified':False,'conditional_budgets':cases,
        'profile_playback_kept_fixed_as_reference_condition':True,
        'actual_midchain_playback_change':None,
        'interruption_model_condition':'给定interrupt_windows明确作为本次参考链取消条件；移动/空窗不触发此条件。',
        'window_convention':'[开始帧,结束帧)；等待在窗口边界耗尽不等于窗口内已经发生回调。',
        'gate_rule':'AttackState.OnEnter传true，同状态连续_NextAttackOrExit传false；未从声明窗口推定实际路径。'}
