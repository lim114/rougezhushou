"""Current-run settings from observed labels, never from menu choices or presets."""
import json,re
from copy import deepcopy
from pathlib import Path
from functools import lru_cache
from .operator_recognition import center
from .anchors import units

@lru_cache(maxsize=1)
def config_data():
    return json.loads((Path(__file__).with_name('data')/'run-config.json').read_text(encoding='utf-8'))

def difficulty_value(record):
    if not isinstance(record,dict) or record.get('modeDifficulty','NORMAL')!='NORMAL':return None
    grade=record.get('value')
    return grade if type(grade) is int and str(grade) in config_data()['difficulties'] else None


def confirmed_config(run_context):
    """Only a caller's current-run snapshot may avoid a new badge search."""
    if not isinstance(run_context,dict) or not isinstance(run_context.get('run_id'),str) or not run_context['run_id']:return {}
    records=run_context.get('config',{});result={}
    if not isinstance(records,dict):return result
    difficulty=records.get('difficulty')
    if difficulty_value(difficulty) is not None and difficulty.get('captured_at') is not None:
        result['difficulty']=deepcopy(difficulty)
    squad=records.get('squad')
    if isinstance(squad,dict) and squad.get('captured_at') is not None:
        known=config_data()['squads'].get(squad.get('id'))
        if known and known['name']==squad.get('name'):result['squad']=deepcopy(squad)
    for record in result.values():
        # The value survives a resize; geometry belongs to its original frame.
        record.pop('badge',None)
        record['reused_from_run']=run_context['run_id']
    return result


def read_config(image,texts,held,*,engine=None,known_config=None):
    data=config_data();result={}
    known=known_config or {}
    zones=[t for t in texts if t['confidence']>=.95
        and any(z['name']==t['text'] for z in data['zones'].values())]
    if len(zones)==1:
        ids=[key for key,z in data['zones'].items() if z['name']==zones[0]['text']]
        # Hidden-zone artwork names are shared; keep candidates, not a fabricated ID.
        if len(ids)==1 or set(ids)=={'zone_4','zone_4_1'}:
            result['zone']={'id':ids[0],'name':zones[0]['text'],'candidates':ids,'source':'地图顶部完整区域名'}
        elif all(key.startswith('zone_portal_') for key in ids):
            result['zone']={'id':None,'name':zones[0]['text'],'candidates':ids,'hidden':True,
                'source':'地图顶部黑潭名称；具体黑潭变体未确认'}
    label=next((t for t in texts if t['text']=='保密等级' and t['confidence']>=.95),None)
    candidates=[]
    if label:
        x,y=center(label);ux,uy=units(image,label,35.2)
        candidates=[t for t in texts if t['confidence']>=.95 and re.fullmatch(r'\d{1,2}',t['text'])
                    and .025*ux<center(t)[0]-x<.16*ux and abs(center(t)[1]-y)<.065*uy
                    and t['text'] in data['difficulties']]
    if len(candidates)==1:
        result['difficulty']={'value':int(candidates[0]['text']),'source':'本局信息面板保密等级标签及相邻数字'}
    names={s['name'] for s in data['squads'].values()}
    titles=[t for t in texts if t['confidence']>=.95 and t['text'] in names]
    # A settings tooltip has one current squad, unlike a multi-choice menu.
    if len(titles)==1 and label:
        title=titles[0];x,y=center(title);ux,uy=units(image,title,35.2)
        divider=next((t for t in texts if t['text']=='DIFFICULTY' and t['confidence']>=.9),label)
        bottom=min(p[1] for p in divider['box'])
        description=''.join(t['text'] for t in sorted(texts,key=lambda t:(round(center(t)[1],2),center(t)[0]))
            if t['confidence']>=.9 and y+.015*uy<center(t)[1]<bottom
            and min(p[0] for p in title['box'])-.03*ux<min(p[0] for p in t['box'])<x+.35*ux)
        def plain(value):
            return re.sub(r'[\s，,。；;：:“”"（）()【】]','',re.sub(r'<[^>]*>','',value))
        options={key:s for key,s in data['squads'].items() if s['name']==title['text']}
        matched=[(key,s) for key,s in options.items() if plain(s['usage'])==plain(description)]
        if len(matched)==1:
            key,s=matched[0]
            result['squad']={'id':key,'name':s['name'],'level':s['bandLevel'],'usage':s['usage'],
                'source':'本局分队提示的完整名称及效果','effect_verified':True}
        else:
            bases={s['normalBandId'] for s in options.values()}
            if len(bases)==1:
                result['squad']={'id':next(iter(bases)),'name':title['text'],'level':None,
                    'source':'本局分队提示名称；强化阶段/效果未完整确认','effect_verified':False}
    if ('squad' not in result and 'squad' not in known) or ('difficulty' not in result and 'difficulty' not in known):
        from .run_badges import find_squad_badge,read_badge_grade
        badge=find_squad_badge(image,held)
        if badge:
            if 'squad' not in result and 'squad' not in known:
                result['squad']={'id':badge['id'],'name':badge['name'],'level':None,
                    'source':'探索界面分队图标；基础与强化共用图案，效果未确认','effect_verified':False,
                    'badge':badge}
            if 'difficulty' not in result and 'difficulty' not in known:
                grade=read_badge_grade(image,badge,texts,engine)
                if grade is not None:
                    result['difficulty']={'value':grade,'source':'动态定位分队图标旁的保密等级徽标数字',
                        'badge':{'box':badge['box']}}
    return result
