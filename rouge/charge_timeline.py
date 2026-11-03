"""Compare explicit collision declarations without deriving a native clock."""
from copy import deepcopy
import json
import math

from .damage import calculate_damage


def _seconds(values, label, limit):
    if not isinstance(values, list) or len(values) > limit:
        raise ValueError(f'{label}需要最多{limit}项的JSON列表。')
    parsed = []
    for value in values:
        if type(value) not in (int, float):
            raise ValueError(label + '需要有限非负JSON数值，不能使用布尔值或文本。')
        try:
            seconds = float(value)
        except OverflowError:
            raise ValueError(label + '需要0–3600秒内的有限数值。') from None
        if not math.isfinite(seconds) or not 0 <= seconds <= 3600:
            raise ValueError(label + '需要0–3600秒内的有限数值。')
        parsed.append(seconds)
    return parsed


def compare_charge_windows(scenario, hit_times_seconds, windows_seconds):
    """Keep original bombardment calculations and add supplied collisions only.

    Supplied times refer to successful hits on the selected target, relative to
    skill activation. They use exact seconds, even when the existing owner
    timeline uses reference frames. Equal times retain their multiplicity.
    No declaration proves a complete cast, native snapshot or token presence.
    """
    if scenario.get('operator') != 'mechanist' or type(scenario.get('skill')) is not int or scenario['skill'] != 3:
        raise ValueError('冲锋时刻对照仅适用于机械师三技能。')
    times = sorted(_seconds(hit_times_seconds, '冲锋命中时刻', 100))
    windows = _seconds(windows_seconds, '观察窗口', 12)
    if not windows:
        raise ValueError('至少需要一个观察窗口。')
    base = deepcopy(scenario)
    base.pop('window_seconds', None)
    base['charge_count'] = 0
    reference = calculate_damage(base)
    duration = reference['estimate']['skill']['duration_seconds']
    if duration is None or any(window > duration for window in windows):
        raise ValueError('观察窗口不能超过当前技能的参数持续时间；技能后的独立生命周期仍未知。')
    charge = next(c for c in reference['components'] if c['name'] == '结构性原理冲锋')
    per_hit = charge['per_hit']
    if per_hit is None:
        raise ValueError('冲锋单包仍未知；先明确已选模组参考的目标阻挡身份。')
    rows = []
    for window in windows:
        modeled = calculate_damage({**deepcopy(base), 'window_seconds': window})
        included = [time for time in times if time < window]
        charge_damage = per_hit * len(included)
        module_reference=modeled.get('mechanist_module_reference')
        bombard_damage=(module_reference['modeled_window_damage_reference'] if module_reference else modeled['total_damage'])
        subtotal = None if bombard_damage is None else bombard_damage + charge_damage
        rows.append({'window_seconds': window, 'hit_times_seconds': included,
            'charge_hits': len(included), 'bombard_damage': bombard_damage,
            'charge_damage': charge_damage, 'conditional_damage_subtotal': subtotal,
            'conditional_dps': subtotal / window if subtotal is not None and window else None,
            'warnings': deepcopy(modeled['warnings']),
            'modeled_parts_complete': modeled['complete']})
    return {'scope': 'manual_collision_times_same_conditions',
        'scenario': deepcopy(scenario), 'skill_duration_parameter_seconds': duration,
        'training': deepcopy(reference['estimate']['training']),
        'calculation_notes': deepcopy(reference['estimate']['notes']),
        'per_hit_damage_reference': per_hit, 'hit_times_seconds': times,
        'events': [{'at_seconds': time, 'damage_reference': per_hit,
                    'cumulative_charge_damage_reference': per_hit * (i + 1)}
                   for i, time in enumerate(times)],
        'windows': rows, 'full_cast_damage': None, 'cycle_damage': None,
        'native_collision_clock_verified': False,
        'notes': [
            '冲锋时刻是用户声明的局外条件；0秒为技能开启。只填写命中当前目标的事件，同一时刻可有多次命中。',
            '冲锋按原始秒数计入[0,观察窗口)；恰好位于窗口结束的事件不计入。[]仅表示此情景未声明命中。',
            '每次冲锋沿用现有技能攻击与减伤参数的固定参考；已明确选用静态模组参考时另按声明阻挡身份调整。真实采样时刻、短时属性变化、实际附着与当前热更新仍需核验。',
            '本体供靶、移动、中断和弹道参数只影响既有轰击；不能用本体0.8秒落地延迟定位独立冲锋。',
            '仅比较当前技能参数持续范围内的已计部分，不外推充能期。给定事件不证明召唤物实际在场、完整施放次数或周期归属。',
            '晚于技能参数持续时间的声明只保留在事件表，不据此推定技能后召唤物仍存活。',
            '本对照取打开时的计算条件；独立事件替代原次数与观察窗口输入，不改写原计算、账号或本局。']}


def format_charge_windows(result):
    def number(value):
        return '未知' if value is None else format(value, '.8g')
    scenario = result['scenario']
    lines = ['机械师三技能 · 冲锋时刻与观察窗口对照（局外条件）',
             '计算条件：' + json.dumps(scenario, ensure_ascii=False, sort_keys=True),
             '声明命中时刻/秒：' + ', '.join(number(t) for t in result['hit_times_seconds']),
             '每次冲锋条件伤害：' + number(result['per_hit_damage_reference'])]
    for row in result['windows']:
        lines.append(f"{number(row['window_seconds'])}秒：冲锋{row['charge_hits']}次，"
            f"轰击已计{number(row['bombard_damage'])}，冲锋{number(row['charge_damage'])}，"
            f"条件小计{number(row['conditional_damage_subtotal'])}，每秒{number(row['conditional_dps'])}")
        lines.extend('待确认：' + warning for warning in row['warnings'])
    lines.extend(['完整施放总伤：未知；周期总伤：未知。', *result['notes'], *result['calculation_notes']])
    return '\n'.join(lines)
