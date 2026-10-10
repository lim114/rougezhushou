"""Inspect Chen's pinned original motions without placing combat events.

Names, lengths and animation events are resource facts. They do not establish
which action runs, how often it loops, damage/collision timing or skill end.
The opt-in orientation only changes presentation; numeric selectors stay closed.
"""
from copy import deepcopy

from .animation_reference import references

OPERATOR = 'char_1050_chen3'
ACTIONS = {
    1: (('Skill_1_Begin', '开启动作条目'),
        ('Skill_1_Loop', '循环动作条目'), ('Skill_1_End', '结束动作条目')),
    2: (('Skill_2_Begin', '开启动作条目'),
        ('Skill_2_Disappear', '消失动作条目'), ('Attack', '普攻动作条目')),
    3: (('Skill_3_Begin', '开启动作条目'),
        ('Skill_3_Loop', '循环动作条目'), ('Skill_3_End', '结束动作条目')),
}


def chen_motion_reference(scenario):
    """Return a detached resource reference for an explicit Front/Back choice."""
    if scenario.get('operator') != OPERATOR:
        return None
    orientation = scenario.get('chen_motion_orientation')
    if orientation is None:
        return None
    if type(orientation) is not str or orientation not in ('Front', 'Back', 'both'):
        raise ValueError('陈原版阶段资料面向需要为Front、Back或both；留空不显示。')
    skill = scenario.get('skill')
    if type(skill) is not int or skill not in ACTIONS:
        raise ValueError('陈原版阶段资料仅适用于一、二、三技能。')
    catalog = references()
    source = catalog['operators'][OPERATOR]['records']
    faces = ('Front', 'Back') if orientation == 'both' else (orientation,)
    motions = []
    for face in faces:
        for name, label in ACTIONS[skill]:
            record = next(r for r in source
                          if r['orientation'] == face and r['animation'] == name)
            # Preserve every original representation and event in source order.
            motions.append({'label': label, **deepcopy(record)})
    return {
        'operator': OPERATOR, 'skill': skill, 'orientation': orientation,
        'source_commit': catalog['source_commit'], 'fps': catalog['fps'],
        'frame_normalization_tolerance': catalog['frame_normalization_tolerance'],
        'motions': motions, 'numeric_schedule_changed': False,
        'runtime_motion_selection_verified': False,
        'damage_event_binding_verified': False,
        'actual_damage_times_seconds': None, 'actual_skill_end_seconds': None,
        'actual_slash_end_seconds': None, 'actual_wave_collision_seconds': None,
        'phase_duration_sum_permitted': False,
    }
