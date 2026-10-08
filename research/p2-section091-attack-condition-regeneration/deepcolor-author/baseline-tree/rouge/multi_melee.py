"""Bounded original-motion reference for Phantom alter's two-hit S1.

The installed prefab and native coroutine establish a relative wait, not a
current-client absolute damage frame or SP unblock phase. Keep that boundary
visible and do not reuse a conventional next-attack end frame.
"""
import math
import struct

from .animation_reference import choices, descriptor
from .attribute_limits import effective_attack_speed
from .timing import FPS, cadence, finite, frame_time

OPERATOR = 'char_1042_phatm2'
TRIGGER_DELTA = 0.4000000059604645


def float32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def relative_wait(interval, animation_seconds=1.6):
    """Float32 animation compression then float-wait ties-to-even rounding."""
    interval = finite(interval, '攻击间隔', 3600)
    animation_seconds = finite(animation_seconds, '动画时长', 3600)
    if not animation_seconds:
        raise ValueError('多段攻击参考需要非零动画时长。')
    scale = min(float32(1), max(float32(.1),
        float32(float32(interval) / float32(animation_seconds))))
    seconds = float32(TRIGGER_DELTA * scale)
    frames = max(1, round(float32(seconds / float32(1 / FPS))))
    return scale, seconds, frames


def wine_s1(timeline, interval, speed, attribute_speed, hits, window=None):
    """Schedule one locked cast under an explicitly disclosed resource anchor.

    Acquisition / movement are offline scenario inputs. Disappearance cancels
    damage to that target; merely leaving attack range does not retarget the
    second spell. This does not infer current game positions or actions.
    """
    if timeline.s['operator'] != OPERATOR or timeline.s['skill'] != 1 or timeline.normal:
        raise ValueError('此多段参考仅适用于酒神一技能。')
    if hits != 2:
        raise ValueError('原始酒神一技能两段配置与当前技能数据不符。')
    options = timeline.options
    selected = descriptor(OPERATOR, 1, options)
    if selected is None:
        records = [r for r in choices(OPERATOR, 1) if r['animation'] == 'Skill_1']
        record = next(r for r in records if r['orientation'] == 'Front')
        assert all(r['preview'] == record['preview'] for r in records)
        selected = descriptor(OPERATOR, 1, {'animation_reference': record['id']})
    raw_windup = options.get('windup_frames', selected['windup_frames'])
    animation = selected['animation_frames'] / FPS
    deployment = [r for r in timeline.s.get('_relic_rules', [])
        if r['kind'] == 'deployment_attack_speed']
    begin = math.ceil(finite(options.get('start_delay_frames', 0), '起始延迟帧'))
    horizon = frame_time(3600 if window is None else window)
    start = begin
    while start < horizon and (not timeline.selectable(start) or timeline.unavailable(start)):
        start += 1
    if start >= horizon:
        starts = []; releases = []; emitted = []; scale = None; gap = None; wait = None
        raw_interval = interval
    else:
        age = (start + timeline.deployment_offset) / FPS
        bonus = sum(r['value'] for r in deployment if age < r['duration'])
        current_speed = effective_attack_speed(attribute_speed + bonus)
        raw_interval = interval * speed / current_speed
        scale, wait, gap = relative_wait(raw_interval, animation)
        windup = (math.ceil(finite(raw_windup, '前摇帧')) if 'windup_frames' in options else
            math.ceil(finite(raw_windup, '前摇帧') * scale - 1e-9))
        # These are resource-anchor reference frames. The coroutine/animator
        # entry phase is not proven; never quietly add one universal frame.
        starts = [start]
        releases = [start + windup, start + windup + gap]
        # No sourced interrupt/cancel/resume state machine is implemented for
        # this replacement cast. Do not silently ignore a supplied cut or
        # reuse the conventional windup retry rule for a special ability.
        provisional_end = max(start + frame_time(raw_interval), releases[-1]) + 1
        if any(a < provisional_end and b > start for a, b in timeline.blocked):
            raise ValueError('暗夜回声施放中的移动/打断机制尚未核验，不能为该情景生成确定的两段输出。')
        emitted = [f for f in releases if timeline.selectable_lifetime(f)]
    impacts = [f for f in emitted if f < horizon]
    stream = {
        'unit': OPERATOR, 'known_animation': True, 'exact_binding': False,
        'reference_binding': True, 'animation': selected['animation'],
        'windup_frames': (releases[0] - starts[0]) if releases else None,
        'recovery_frames': None, 'interval_frames': cadence(raw_interval),
        'interval_seconds': cadence(raw_interval) / FPS,
        'start_frames': starts, 'release_frames': releases,
        'impact_frames': impacts, 'times_seconds': [f / FPS for f in impacts],
        'emitted_impact_frames': emitted, 'emitted_times_seconds': [f / FPS for f in emitted],
        'emitted_release_frames': emitted, 'hit_release_frames': impacts,
        'interval_frames_by_attack': [cadence(raw_interval)] if starts else [],
        'temporary_attack_speed': bool(deployment), 'resume_frame': 0,
        'source': selected['source'],
        'original_animation_reference': {k: selected[k] for k in (
            'reference_id', 'reference_label', 'original_orientation', 'skin',
            'source_sha256', 'runtime_binding_verified')},
        'multi_melee_reference': {
            'source_prefab': 'skchr_phatm2_1.prefab', 'source_animation': 'Skill_1',
            'selected_motion': selected['animation'],
            'automatic_original_reference': 'animation_reference' not in options,
            'raw_interval_seconds': raw_interval, 'animation_scale': scale,
            'relative_wait_seconds_float32': wait, 'relative_wait_frames': gap,
            'first_damage_phase_verified': False, 'cast_end_verified': False,
            'sp_unblock_phase_verified': False, 'normal_resume_verified': False,
            'current_hotfix_equivalence_proven': False,
            'anchor': '原版动作出手事件的局外参考；不是当前客户端精确首伤帧',
        },
    }
    stream['original_animation_reference']['overridden_by_preview'] = 'windup_frames' in options
    timeline.streams.append(stream)
    timeline.notes.append('暗夜回声采用原版动作锚点与原生两段相对等待；段间按未取整攻击周期缩放、float32等待取最近偶数帧。当前首伤相位、完整结束、阻回与普攻恢复尚未验证，回转及周期输出未知。')
    return stream
