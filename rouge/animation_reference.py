"""Pinned original motions, explicitly selected as offline timing references."""
from functools import lru_cache
from copy import deepcopy
import json
from pathlib import Path
import re


@lru_cache(maxsize=1)
def references():
    return json.loads((Path(__file__).with_name('data')/'original-animation-references.json').read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def static_bindings():
    return json.loads((Path(__file__).with_name('data')/'native-static-action-bindings.json').read_text(encoding='utf-8'))


def _bound_choices(operator, skill, normal):
    source = static_bindings()
    scope = 'normal' if normal else str(skill)
    binding = source['operators'].get(operator, {}).get(scope)
    if binding is None:return None
    by_id = {r['reference_id']:r for r in binding['records']}
    selected = []
    for record in references()['operators'].get(operator, {}).get('records', []):
        match = by_id.get(record['id'])
        # A changed skeleton or source/config mismatch must not inherit this
        # static proof. Keep the ordinary unknown default when no row matches.
        if (not match or not match['static_selection_verified'] or
                match['native_animation_loop'] is not False or
                match['skeleton_sha256'] != record['source']['sha256'] or
                match['animation'] != record['animation'] or
                match['orientation'] != record['orientation']):continue
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
            selection_source_evidence=source['source_evidence'],
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
    return result
