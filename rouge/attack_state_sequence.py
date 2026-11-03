"""Declared AttackState entry/continuation gates for source-bound animations.

The sequence contains caller declarations, not inferred FSM transitions or RNG
draws. Its accumulator sums requested segment waits; it is not a combat clock.
"""
from copy import deepcopy
import math

from .animation_reference import choices, descriptor, label, three_part_profile
from .three_part_wait import fixed_wait_ticks


SOURCE = 'research/p2-three-part-wait-current/first-attack-rules.json'
SCOPES = {'kaltsit': ('normal', '1'), 'silverash': ('normal',)}
NAMES = {'kaltsit': '凯尔希', 'silverash': '凛御银灰'}
PARTS = ('begin', 'oneshot', 'end')


def sequence_choices(operator, scope):
    if type(operator) is not str or operator not in SCOPES:
        raise ValueError('状态序列仅支持已有三段原件的凯尔希和凛御银灰。')
    if type(scope) is not str or scope not in SCOPES[operator]:
        raise ValueError('状态序列需要该干员已证的普通攻击或凯尔希技能1作用域。')
    selected = [r for r in choices(operator, 1, normal=scope == 'normal')
                if r.get('static_action_binding', {}).get('three_part_reference')]
    if not selected:
        raise ValueError('当前固定资料没有完整三段候选，不能继承旧来源状态。')
    return selected


def _seconds(value, name, *, positive=False):
    if type(value) not in (int, float):
        raise ValueError(name + '需要有限数值秒数，不能使用布尔值或文本。')
    try:
        number = float(value)
    except (ValueError, OverflowError):
        raise ValueError(name + '需要范围内有限秒数。') from None
    if not math.isfinite(number) or not 0 <= number <= 3600 or positive and number == 0:
        raise ValueError(name + '需要范围内有限' + ('正' if positive else '非负') + '秒数。')
    return number


def _segments(plan, profile, delta):
    rows = []
    for part in PARTS:
        configured = plan[part] is not None
        played = configured and (part != 'begin' or not plan['only_begin_when_first_attack']
                                  or profile['first_attack_condition'])
        duration = profile['scaled_segment_seconds'][part]
        rows.append({'segment': part, 'animation': plan[part]['animation'] if configured else None,
            'configured': configured, 'played_under_declared_gate': played,
            'source_duration_seconds': profile['source_segment_seconds'][part],
            'scaled_duration_seconds': duration,
            'requested_wait_ticks': fixed_wait_ticks(duration, delta) if played else 0})
    return rows


def project_attack_state_sequence(payload):
    """Bind each declared state step to its exact source animation candidate."""
    if type(payload) is not dict or set(payload) - {'operator', 'scope', 'grid_fps', 'steps'}:
        raise ValueError('状态序列需要operator、scope、steps，可选grid_fps。')
    if not {'operator', 'scope', 'steps'} <= set(payload):
        raise ValueError('状态序列需要operator、scope、steps。')
    operator, scope = payload['operator'], payload['scope']
    available = {r['id']: r for r in sequence_choices(operator, scope)}
    fps = payload.get('grid_fps', 30)
    if type(fps) is not int or not 1 <= fps <= 240:
        raise ValueError('参考网格需要1–240整数帧率；它不是实测游戏步长。')
    steps = payload['steps']
    if type(steps) is not list or not 1 <= len(steps) <= 64:
        raise ValueError('状态序列需要1–64条声明。')
    rows, cursor, all_entry_ticks, entry_ordinal, previous = [], 0, 0, None, None
    for ordinal, step in enumerate(steps, 1):
        required = {'state', 'reference_id', 'cooldown_seconds'}
        optional = {'movement_gap_seconds', 'target_gap_seconds'}
        if type(step) is not dict or not required <= set(step) or set(step) - required - optional:
            raise ValueError('每步需要state、reference_id、cooldown_seconds；可选移动和目标空档秒数。')
        state, identity = step['state'], step['reference_id']
        if type(state) is not str or state not in ('entry', 'continue'):
            raise ValueError('state需要entry（进入攻击状态）或continue（同状态继续）。')
        if type(identity) is not str or identity not in available:
            raise ValueError('候选与声明干员/作用域不符，或没有完整三段原件绑定。')
        cooldown = _seconds(step['cooldown_seconds'], '参考攻击周期', positive=True)
        movement = _seconds(step.get('movement_gap_seconds', 0), '声明移动空档')
        target = _seconds(step.get('target_gap_seconds', 0), '声明目标空档')
        first = state == 'entry'
        if first:
            entry_ordinal = ordinal
        key = 'normal_animation_reference' if scope == 'normal' else 'animation_reference'
        selected = descriptor(operator, 1, {key: identity}, normal=scope == 'normal')
        plan = selected['three_part_reference']
        parts = three_part_profile(selected, cooldown)
        profile = next(r for r in parts['conditional_profiles'] if r['first_attack_condition'] == first)
        segments = _segments(plan, profile, 1 / fps)
        count = sum(r['requested_wait_ticks'] for r in segments)
        hypothetical = sum(r['requested_wait_ticks'] for r in
                           _segments(plan, parts['conditional_profiles'][0], 1 / fps))
        rows.append({'ordinal': ordinal, 'declared_state': state, 'reference_id': identity,
            'reference_label': label(available[identity]), 'animation': selected['animation'],
            'orientation': selected['original_orientation'], 'mode_indices': selected['mode_indices'],
            'declared_entry_ordinal': entry_ordinal, 'prior_entry_not_declared': entry_ordinal is None,
            'first_attack_bool_under_declared_path': first,
            'bool_source': 'AttackState.OnEnter -> _StartAttack(true)' if first else
                           'AttackState._NextAttackOrExit -> _StartAttack(false)',
            'candidate_changed': previous is not None and previous != identity,
            'candidate_change_reopens_first_gate': False,
            'declared_movement_gap_seconds': movement, 'declared_target_gap_seconds': target,
            'gaps_used_to_infer_state_or_schedule': False,
            'cooldown_reference_seconds': cooldown, 'duration_scale': profile['duration_scale'],
            'playback_speed': profile['playback_speed'], 'segments': segments,
            'requested_wait_ticks': count, 'requested_wait_seconds_reference': count / fps,
            'cumulative_requested_wait_ticks_before': cursor,
            'cumulative_requested_wait_ticks_after': cursor + count,
            'all_entry_comparison_wait_ticks': hypothetical,
            'declared_minus_all_entry_wait_ticks': count - hypothetical,
            'animation_only_on_attack_offset_seconds_reference': profile['animation_only_on_attack_offset_seconds'],
            'random_selection': deepcopy(plan['selection']), 'actual_first_attack_bool': None,
            'actual_start_seconds': None, 'actual_callback_seconds': None, 'actual_end_seconds': None})
        cursor += count
        all_entry_ticks += hypothetical
        previous = identity
    return {'scope': 'declared_attack_state_sequence_segment_waits', 'operator': operator,
        'operator_name': NAMES[operator], 'attack_scope': scope, 'grid_fps': fps,
        'grid_delta_seconds_reference': 1 / fps, 'declared_sequence': deepcopy(payload), 'rows': rows,
        'entry_count': sum(r['declared_state'] == 'entry' for r in rows),
        'continuation_count': sum(r['declared_state'] == 'continue' for r in rows),
        'requested_wait_ticks_total': cursor, 'requested_wait_seconds_total_reference': cursor / fps,
        'all_entry_comparison_wait_ticks_total': all_entry_ticks,
        'declared_minus_all_entry_wait_ticks_total': cursor - all_entry_ticks,
        'accumulator_is_sum_of_requested_segment_waits_only': True,
        'actual_fsm_path': None, 'actual_random_draws': None, 'actual_elapsed_sequence_seconds': None,
        'actual_first_callback_seconds': None, 'actual_last_end_seconds': None,
        'actual_cycle_seconds': None, 'runtime_binding_verified': False,
        'current_hotfix_equivalence_proven': False,
        'source': {'state_gate': SOURCE, 'animation_segments': 'research/p2-three-part-static-current/receipt.json',
                   'float_waits': 'research/p2-three-part-wait-current/receipt.json'},
        'notes': ['entry/continue和每步动作候选都是调用方声明；没有从本局、目标空窗、移动或候选变化推断原生状态。',
            'entry通过原件路径传true；同状态continue传false。银灰随机组转发该布尔值，换候选不会自行重开开始段门。',
            '首次声明可以是continue，此时更早的进入状态来源未知；显式entry才建立新的声明状态组。',
            '累计值只相加各段请求的等待分项；未包含实际起点、冷却空转、段间调度相位或声明空档，不是整串攻击耗时。',
            '每步按其明确攻击周期独立缩放；此处未推定动作中途攻速变化或实际相邻攻击周期。',
            '所有步骤当entry的比较仅用于解释门条件造成的数值差；它不是另一条实际游戏路径。',
            '30Hz为默认局外参考网格；实际步长、原生路径、随机抽取、首击、结束和完整循环均未知。']}


def public_sequence_payload(operator='kaltsit', scope=None):
    scope = ('1' if operator == 'kaltsit' else 'normal') if scope is None else scope
    available = sequence_choices(operator, scope)
    front = [r for r in available if r['orientation'] == 'Front']
    selected = sorted(front, key=lambda r: r['animation'])
    first = selected[0]
    second = selected[1] if len(selected) > 1 else first
    return {'operator': operator, 'scope': scope, 'grid_fps': 30,
        'steps': [{'state': 'entry', 'reference_id': first['id'], 'cooldown_seconds': 2.55},
            {'state': 'continue', 'reference_id': second['id'], 'cooldown_seconds': 2.55,
             'movement_gap_seconds': .2, 'target_gap_seconds': .4},
            {'state': 'entry', 'reference_id': second['id'], 'cooldown_seconds': 2.55}]}


def format_attack_state_sequence(result):
    lines = [result['operator_name'] + ' · 攻击状态声明序列',
        '普通攻击' if result['attack_scope'] == 'normal' else '技能' + result['attack_scope'],
        f"参考网格{result['grid_fps']}Hz；累计请求等待{result['requested_wait_ticks_total']}步 / "
        f"{result['requested_wait_seconds_total_reference']:.8g}参考秒（等待分项之和）"]
    for row in result['rows']:
        gate = 'true' if row['first_attack_bool_under_declared_path'] else 'false'
        group = str(row['declared_entry_ordinal']) if row['declared_entry_ordinal'] is not None else '更早进入未声明'
        lines.append(f"第{row['ordinal']}步：{row['declared_state']}；{row['reference_label']}；firstAttack={gate}；进入组={group}")
        lines.append('开始/主体/结束请求等待：' + '/'.join(str(s['requested_wait_ticks']) for s in row['segments']) +
            f"；本步{row['requested_wait_ticks']}步；累计{row['cumulative_requested_wait_ticks_after']}步；"
            f"相对每步均entry的比较差{row['declared_minus_all_entry_wait_ticks']:+d}步")
        lines.append(f"声明移动空档{row['declared_movement_gap_seconds']:g}秒、目标空档{row['declared_target_gap_seconds']:g}秒；不据此重开门或安排攻击。")
    lines.extend(['实际首击/末段结束/整串攻击耗时/完整循环：未知。', *result['notes']])
    return '\n'.join(lines)
