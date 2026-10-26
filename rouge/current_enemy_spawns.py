"""Reverse exact fixed enemy references to their direct SPAWN declarations.

This is a structural relation. It never chooses a random member, executes a
branch, decides a database level, or converts waits to a global clock.
"""
from copy import deepcopy
from . import current_battle_reference as battle

NOTICE='查看这个敌人在本关资料中对应的直接出怪条目。随机候选和条件分支仍需满足条件；没有直接记录不表示它不会出现。'
UNAVAILABLE='敌人与出怪条目的对应资料无法核对，旧内容和跳转已清除；资料恢复后请重新选择。'
PACK='research/p3-current-enemy-spawns-371'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='0536025c7c3e37d498f3fca43461378bdd561b4d6ea7fc2db8277b91f20f4332'
def evidence():
    import json
    from hashlib import sha256
    try:
        raw=battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        if manifest['schema']!='current_enemy_spawns_371_manifest_v1' or set(manifest['files'])!={PACK+'/scope-inventory.json',PACK+'/source-notes.json'}:return None
        objects={}
        for name,pin in manifest['files'].items():
            body=battle.version._file(name).read_bytes()
            if type(pin['bytes'])is not int or len(body)!=pin['bytes']or sha256(body).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(body)
        return objects[PACK+'/scope-inventory.json']
    except(OSError,ValueError,TypeError,KeyError):return None

KINDS=((None,'总览（全部对应条目）'),('main','主波次'),('branch','条件分支'))

def _same(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return a.keys()==b.keys() and all(_same(a[k],b[k])for k in a)
    if type(a)in(list,tuple):return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
    return a==b

def _derive(current,enemy_key):
    enemy=next((e for e in current['enemies']if e['key']==enemy_key),None)
    if enemy is None:return None
    entries=[]
    for action in current['actions']:
        raw=action['raw']
        if raw.get('actionType')!='SPAWN' or raw.get('key')!=enemy['id']:continue
        candidates=action['enemy_candidates']
        if not any(e['key']==enemy_key and _same(e['raw_binding'],enemy['raw_binding'])for e in candidates):
            raise ValueError('Exact candidate binding missing')
        entries.append({'key':action['key'],'label':battle.action_label(action),'action':deepcopy(action),
            'reference_candidates':[{'enemy_key':e['key'],'database_level':e['level'],
                                     'raw_binding':deepcopy(e['raw_binding'])}for e in candidates],
            'exact_level_selected':len(candidates)==1,'actual_occurrence':None,'actual_count':None,
            'absolute_time':None,'actual_position':None})
    return {'stage_id':current['id'],'stage_name':current['name'],'enemy_key':enemy_key,
            'enemy':deepcopy(enemy),'entries':entries,'level_key':current['level_key'],
            'original_level_source':deepcopy(current['source']),
            'battle_source_identity':current['source_identity'],
            'source_identity':(MANIFEST_SHA256,current['source_identity']),
            'actual_occurrence':None,'actual_count':None,'absolute_time':None,'actual_path':None,
            'expected_stats':None,'actual_server_verified':False,'run_updated':False}

def stage_reference(stage_id,enemy_key):
    if type(stage_id)is not str or type(enemy_key)is not str:return None
    current=battle.stage_reference(stage_id)
    scope=evidence()
    if current is None or scope is None or scope['source_identity']!=current['source_identity']or stage_id not in scope['stages']:return None
    declared=scope['stages'][stage_id]
    if declared['level_key']!=current['level_key']or declared['original_source']!=current['source']:return None
    try:return _derive(current,enemy_key)
    except(KeyError,TypeError,ValueError,IndexError):return None

def rows(result,kind=None):
    if type(result)is not dict or kind not in dict(KINDS):return []
    return [deepcopy(e)for e in result['entries']if kind is None or e['action']['queue']['kind']==kind]

def resolve_action(result,key):
    if type(result)is not dict or type(key)is not str:return None
    fresh=stage_reference(result.get('stage_id'),result.get('enemy_key'))
    if fresh is None or not _same(fresh,result):return None
    row=next((r for r in fresh['entries']if r['key']==key),None)
    if row is None:return None
    return {'stage_id':fresh['stage_id'],'enemy_key':fresh['enemy_key'],'action_key':key,
            'row':deepcopy(row),'source_identity':deepcopy(fresh['source_identity']),'run_updated':False}

def position_reference(result,key):
    selected=resolve_action(result,key)
    if selected is None:return None
    from . import current_action_positions
    position=current_action_positions.reference(result['stage_id'],key)
    if position is None or position['battle_source_identity']!=result['battle_source_identity']:return None
    return position

def player_text(result,entry=None):
    lines=[result['enemy']['name']+' · '+result['stage_name'],'',
           '【对应的出怪记录】',f"本关资料中找到{len(result['entries'])}条直接出怪记录；这是条目数，不是实际出场数量。",
           '主波次与条件分支分别列出。每条的随机组、隐藏组和等待条件要单独查看，不能相加为本关必出的敌人数。']
    if not result['entries']:
        lines+=['未找到直接出怪记录。这类实体仍可能由技能、装置或其它脚本生成，不能据此排除。']
    if entry is not None:
        lines+=['', '【所选条目】',*battle.action_text(entry['action']).splitlines()]
        if not entry['exact_level_selected']:
            lines+=['这一出怪名称关联多个精确引用；它们全都保留。当前条目未证明实际采用哪份等级或独立配置。']
        else:lines+=['本条名称在此固定关卡资料中只对应这一份引用；这不证明本局实际生成或当前最终面板。']
    lines+=['','【适用范围】','没有计算开场后的准确时刻、实际出现次数或概率；动态生成来源和当前服务器执行仍未完整核对。',
            '可以跳转到本条出怪条件及已有地图参考；地图未校准的格子不会画到原图，也不会连接成实际路线。']
    return '\n'.join(lines)
