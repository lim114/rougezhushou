"""Pinned original motions, explicitly selected as offline timing references."""
from functools import lru_cache
from copy import deepcopy
import json
from pathlib import Path
import re
import math
import struct


@lru_cache(maxsize=1)
def references():
    return json.loads((Path(__file__).with_name('data')/'original-animation-references.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def static_bindings():
    return json.loads((Path(__file__).with_name('data')/'native-static-action-bindings.json').read_text(encoding='utf-8'))


def _valid_three_part(match, records):
    plan = match.get('three_part_reference')
    if plan is None:return True
    if (plan.get('behaviour_type') != 'Torappu.Battle.Abilities.ThreePartOneshotAnimation' or
            type(plan.get('only_begin_when_first_attack')) is not bool or
            plan.get('first_attack_gate_actual') is not None):return False
    for part in ('begin','oneshot','end'):
        segment = plan.get(part)
        if segment is None:
            if part == 'oneshot':return False
            continue
        original = records.get(segment.get('reference_id'))
        if (original is None or segment.get('native_loop') is not False or
                segment.get('native_speed') != 1.0 or
                segment.get('orientation') != match['orientation'] or
                original['orientation'] != segment.get('orientation') or
                segment.get('animation') != original['animation'] or
                segment.get('source_sha256') != original['source']['sha256'] or
                segment.get('duration_seconds') != original['duration']['seconds']):return False
    if (plan['oneshot']['reference_id'] != match['reference_id'] or
            plan.get('source_on_attack_seconds') != match['source_on_attack_seconds']):return False
    return all(type(plan.get(k)) in (int,float) and math.isfinite(plan[k])
               for k in ('min_animation_scale','max_animation_scale'))


def _bound_choices(operator, skill, normal):
    source = static_bindings()
    scope = 'normal' if normal else str(skill)
    binding = source['operators'].get(operator, {}).get(scope)
    if binding is None:return None
    by_id = {r['reference_id']:r for r in binding['records']}
    selected = []
    records = references()['operators'].get(operator, {}).get('records', [])
    original_by_id = {r['id']:r for r in records}
    for record in records:
        match = by_id.get(record['id'])
        # A changed skeleton or source/config mismatch must not inherit this
        # static proof. Keep the ordinary unknown default when no row matches.
        if (not match or not match['static_selection_verified'] or
                match['native_animation_loop'] is not False or
                match['skeleton_sha256'] != record['source']['sha256'] or
                match['animation'] != record['animation'] or
                match['orientation'] != record['orientation']):continue
        if not _valid_three_part(match, original_by_id):continue
        attacks = [e for e in record['events'] if e['name'] == 'OnAttack']
        if (len(attacks) != 1 or not 0 < attacks[0]['seconds'] < record['duration']['seconds'] or
                attacks[0]['seconds'] != match['source_on_attack_seconds'] or
                record['duration']['seconds'] != match['source_animation_duration_seconds']):continue
        # Reuse the disclosed 048 representation normalization only for this
        # explicitly chosen animation-segment preview. These are not callback
        # frames, and no activation/end/tick phase is derived from them.
        windup = attacks[0]['representation_normalized_frames_30hz']
        duration = record['duration']['representation_normalized_frames_30hz']
        if type(windup) is not int or type(duration) is not int or not 0 < windup < duration:continue
        chosen = deepcopy(record)
        chosen['preview'] = {'windup_frames':windup,
            'recovery_frames':duration-windup, 'animation_frames':duration}
        chosen.update(static_action_binding=deepcopy(match), bound_scope=scope,
            mode_indices=list(binding['mode_indices']),
            selection_source_evidence=binding.get('three_part_source_evidence',source['source_evidence']),
            selectable_as_static_bound_segment_reference=True,
            actual_callback_frames=None, runtime_binding_verified=False)
        selected.append(chosen)
    return selected


def choices(operator,skill=None,*,normal=False):
    bound=_bound_choices(operator,skill,normal)
    if bound is not None:return bound
    records=references()['operators'].get(operator,{}).get('records',[])
    selected=[]
    for record in records:
        if not record['selectable_as_conventional_reference']:continue
        name=record['animation']
        number=re.match(r'^Skill_?(\d+)(?:_|$)',name)
        ordinary=name.startswith('Attack')
        if (normal and ordinary) or (not normal and (ordinary or number and int(number[1])==skill)):
            selected.append(record)
    return selected


def label(record):
    face={'Front':'正面','Back':'背面'}[record['orientation']]
    if record.get('static_action_binding'):
        scope=record['bound_scope'];down=' · 向下动作' if 'Down' in record['animation'] else ''
        action='普通攻击' if scope=='normal' else '技能'+scope+'动作'
        preview=record['preview']
        if record['static_action_binding'].get('three_part_reference'):
            variant = ' · 候选'+record['animation'].removeprefix('Attack_') if record['bound_scope']=='normal' and record['static_action_binding']['three_part_reference']['selection']['method']=='Random' else ''
            return f"{face} · {action}{down}{variant} · 主体事件参考{preview['windup_frames']}帧 / 首击未知"
        return f"{face} · {action}{down} · 原件事件参考{preview['windup_frames']}帧 / 动画参考{preview['animation_frames']}帧"
    motion=record['animation']
    number=re.match(r'^Skill_?(\d+)(?:_|$)',motion)
    if motion.startswith('Attack'):
        suffix=motion.removeprefix('Attack').strip('_')
        suffix={'Down':'向下动作'}.get(suffix,suffix)
        action='普通攻击'+(' '+suffix if suffix else '')
    elif number:
        suffix=motion[number.end():]
        action=f'技能{number[1]}动作'+({'Attack':' · 攻击','Combat':' · 攻击'}.get(suffix,' · 动作变体' if suffix else ''))
    else:action='攻击动作参考'
    preview=record['preview']
    return f"{face} · {action} · 出手{preview['windup_frames']}帧 / 动画{preview['animation_frames']}帧"


def descriptor(operator,skill,options,*,normal=False):
    field='normal_animation_reference' if normal else 'animation_reference'
    identity=options.get(field)
    if identity is None:return None
    record=next((r for r in choices(operator,skill,normal=normal) if r['id']==identity),None)
    if record is None:raise ValueError('原版动画参考与当前干员/技能不符，或该动作不适合常规逐击参考。')
    result={**record['preview'],'animation':record['animation'],'source':record['source']['url'],
        'reference_id':identity,'reference_label':label(record),
        'original_orientation':record['orientation'],'skin':'original',
        'runtime_binding_verified':False,'source_sha256':record['source']['sha256']}
    if record.get('static_action_binding'):
        result.update(static_selection_verified=True, mode_indices=record['mode_indices'],
            static_action_binding=deepcopy(record['static_action_binding']),
            selection_source_evidence=record['selection_source_evidence'],
            frame_numbers_are_animation_segment_reference=True,
            actual_callback_frames=None, actual_activation_phase_seconds=None, actual_end_seconds=None)
    if record.get('static_action_binding',{}).get('three_part_reference'):
        result['three_part_reference'] = deepcopy(record['static_action_binding']['three_part_reference'])
        result['body_event_is_not_first_release'] = True
    return result


def three_part_profile(data, cooldown_seconds):
    """Conditional animation durations only; no scheduler origin or callback clock."""
    plan = data.get('three_part_reference')
    if plan is None:return None
    if isinstance(cooldown_seconds,bool):raise ValueError('三段参考周期需要有限正秒数。')
    try:cooldown = float(cooldown_seconds)
    except (ValueError,TypeError,OverflowError):raise ValueError('三段参考周期需要有限正秒数。') from None
    if not math.isfinite(cooldown) or not 0 < cooldown <= 3600:
        raise ValueError('三段参考周期需要有限正秒数。')
    def f32(value):
        try:result=struct.unpack('<f',struct.pack('<f',value))[0]
        except (OverflowError,struct.error):raise ValueError('三段参考数值超出原生浮点范围。') from None
        if not math.isfinite(result):raise ValueError('三段参考数值超出原生浮点范围。')
        return result
    profiles=[]
    for first_attack in (True,False):
        durations={part:(plan[part]['duration_seconds'] if plan[part] is not None else 0.0)
                   for part in ('begin','oneshot','end')}
        if plan['only_begin_when_first_attack'] and not first_attack:durations['begin']=0.0
        total=f32(f32(durations['end']+durations['begin'])+durations['oneshot'])
        scale=f32(f32(cooldown)/total)
        minimum=plan['min_animation_scale'];maximum=plan['max_animation_scale']
        if minimum >= 0:scale=max(scale,minimum)
        if maximum >= 0:scale=min(scale,maximum)
        if scale <= 0:raise ValueError('三段参考周期不足以表示正的原生浮点缩放。')
        speed=f32(1.0/scale)
        scaled={part:f32(raw/speed) for part,raw in durations.items()}
        profiles.append({'first_attack_condition':first_attack,'source_segment_seconds':durations,
            'source_chain_seconds':total,'duration_scale':scale,'playback_speed':speed,
            'scaled_segment_seconds':scaled,
            'animation_only_chain_seconds':sum(scaled.values()),
            'animation_only_on_attack_offset_seconds':scaled['begin']+f32(plan['source_on_attack_seconds']/speed),
            'actual_chain_start_seconds':None,'actual_callback_seconds':None,'actual_end_seconds':None})
    return {'source':'research/p2-three-part-static-current/receipt.json',
        'cooldown_reference_seconds':cooldown,'first_attack_gate_actual':None,
        'selection':deepcopy(plan['selection']),'conditional_profiles':profiles,
        'ability_end_animation_key':plan['ability_end_animation_key'],
        'actual_callback_frames':None,'runtime_binding_verified':False,
        'scope':'动画段时长与事件偏移参考；未计调度恢复相位、实际启动、打断及弹道，不能作为首击/结束时钟。'}
