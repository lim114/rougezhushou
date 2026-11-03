"""Pinned original motions, explicitly selected as offline timing references."""
from functools import lru_cache
import json
from pathlib import Path
import re


@lru_cache(maxsize=1)
def references():
    return json.loads((Path(__file__).with_name('data')/'original-animation-references.json').read_text(encoding='utf-8'))


def choices(operator,skill=None,*,normal=False):
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
    return {**record['preview'],'animation':record['animation'],'source':record['source']['url'],
        'reference_id':identity,'reference_label':label(record),
        'original_orientation':record['orientation'],'skin':'original',
        'runtime_binding_verified':False,'source_sha256':record['source']['sha256']}
