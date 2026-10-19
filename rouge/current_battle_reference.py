"""Current pinned level references, kept separate from legacy predictions."""
from copy import deepcopy
from hashlib import sha256
import json,math,re
from . import expansion_reference as version

ROOT=version.ROOT
PACK='research/p3-current-battle-314'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='5afaa89bda5cee08b90d0db4f536d70a742755d93f073cfd55257f5fd2fbfc13'
TIERS={'NORMAL':'普通','ELITE':'精英','BOSS':'领袖'}
NOTICE='国服10月16日更新资料。这里只说明固定关卡中的候选与条件，不读取战斗、不操作游戏；当前难度、分队与敌人技能的完整数值修正仍待迁移。'
UNAVAILABLE='当前版本的关卡资料无法核对，旧内容已清除；资料恢复后请重新选择。'


def plain(value):
    return re.sub(r'<\$[^>]+>','',version._plain(value))


def packet():
    try:
        manifest_raw=(ROOT/MANIFEST).read_bytes()
        if sha256(manifest_raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(manifest_raw)
        expected={PACK+'/'+s for s in('source-inputs.json','source-selection.json','enemy-images.json')}
        if manifest['schema']!='current_battle_314_v1' or set(manifest['files'])!=expected:return None
        if manifest['game_commit']!=version.NEW_COMMIT:return None
        objects={}
        for name,pin in manifest['files'].items():
            p=ROOT/name
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(raw)
        base=version.packet()
        if base is None:return None
        return {'inputs':objects[PACK+'/source-inputs.json'],'selection':objects[PACK+'/source-selection.json'],
                'portraits':objects[PACK+'/enemy-images.json'],'version':base,'identity':MANIFEST_SHA256,
                'numeric_environment_migrated':False,'map_projection_verified':False,'actual_server_verified':False}
    except(OSError,ValueError,TypeError,KeyError,UnicodeError,RecursionError):return None


def _writes(target,source):
    """Only explicit defined wrappers write identity/metadata, never placeholder values."""
    for k,v in source.items():
        if isinstance(v,dict)and type(v.get('m_defined'))is bool and 'm_value'in v:
            if v['m_defined']:target[k]=deepcopy(v['m_value'])


def enemy_records(level,ref):
    results=[];data=ref['inputs']
    for index,binding in enumerate(level['enemyDbRefs']):
        identity={};versions=data['enemy_definitions'].get(binding['id'],[])
        exact=any(v['level']==binding['level']for v in versions)
        if binding['useDb']is True:
            for row in sorted(versions,key=lambda v:v['level']):
                if row['level']<=binding['level']:_writes(identity,row['enemyData'])
        _writes(identity,binding.get('overwrittenData')or{})
        handbook=data['handbook'].get(binding['id'])if binding['useDb']is True else None
        handbook=handbook or{}
        name=identity.get('name')or handbook.get('name')or'未命名关联实体'
        tier=identity.get('levelType')or handbook.get('enemyLevel')
        prefab=identity.get('prefabKey')
        portrait=ref['portraits']['images'].get(prefab)if prefab else None
        # An image named exactly as the reference is independently identifiable,
        # but a same-name handbook enemy or stripped suffix is never substituted.
        if portrait is None:portrait=ref['portraits']['images'].get(binding['id'])
        results.append({'key':str(index),'reference_index':index,'id':binding['id'],'level':binding['level'],
            'name':plain(name),'tier':tier if tier in TIERS else None,'prefab_key':prefab,
            'portrait':deepcopy(portrait),'description':plain(identity.get('description')or handbook.get('description')),
            'abilities':[plain(a['text'])for a in handbook.get('abilityList')or[]if a.get('text')],
            'handbook_applied':bool(handbook),'exact_database_level_present':exact,'use_db':binding['useDb'],
            'raw_binding':deepcopy(binding),'expected_stats':None,'actual_count':None})
    return results


def queues(level):
    for wi,w in enumerate(level['waves']):
        for fi,f in enumerate(w['fragments']):
            yield {'kind':'main','wave':wi+1,'fragment':fi+1,'branch':None,'phase':None,
                   'wave_pre_delay':w.get('preDelay'),'wave_post_delay':w.get('postDelay'),
                   'fragment_pre_delay':f.get('preDelay'),'wave_wait_limit':w.get('maxTimeWaitingForNextWave'),
                   'source_selector':f'$.waves[{wi}].fragments[{fi}]','actions':f.get('actions')or[]}
    for bi,(key,b)in enumerate((level.get('branches')or{}).items()):
        for pi,p in enumerate(b.get('phases')or[]):
            yield {'kind':'branch','wave':None,'fragment':None,'branch':key,'branch_index':bi+1,'phase':pi+1,
                   'phase_pre_delay':p.get('preDelay'),
                   'source_selector':'$.branches['+json.dumps(key)+f'].phases[{pi}]','actions':p.get('actions')or[]}


def stage_reference(stage_id):
    ref=packet()
    if ref is None:return None
    stages=ref['version']['current']['details']['stages']
    if type(stage_id)is not str or stage_id not in stages:return None
    stage=stages[stage_id];key='levels/'+stage['levelId'].lower()+'.json'
    level=ref['inputs']['levels'].get(key)
    if level is None:return None
    enemies=enemy_records(level,ref);all_queues=list(queues(level));actions=[]
    aliases={}
    for c in('predefines','hardPredefines'):
        for field in('characterInsts','tokenInsts'):
            for i,row in enumerate((level.get(c)or{}).get(field)or[]):
                if row.get('alias'):aliases.setdefault(row['alias'],[]).append({'source_selector':f'$.{c}.{field}[{i}]','raw':deepcopy(row)})
    for queue in all_queues:
        for i,raw in enumerate(queue['actions']):
            matches=[e for e in enemies if e['id']==raw.get('key')]if raw.get('actionType')=='SPAWN'else[]
            actions.append({'key':str(len(actions)),'queue':{k:v for k,v in queue.items()if k!='actions'},
                'action_index':i+1,'source_selector':queue['source_selector']+f'.actions[{i}]','raw':deepcopy(raw),
                'enemy_candidates':deepcopy(matches),'predefined_candidates':deepcopy(aliases.get(raw.get('key'),[]))if raw.get('actionType')=='ACTIVATE_PREDEFINED'else[],
                'absolute_time':None,'actual_occurrence':None,'position_on_original':None,'probability':None})
    return {'id':stage_id,'name':stage['name'],'stage':deepcopy(stage),'level_key':key,
        'level':deepcopy(level),'enemies':enemies,'actions':actions,'source_identity':ref['identity'],
        'image':deepcopy(ref['version']['images']['images'].get(stage_id)),
        'source':deepcopy(ref['selection']['original_sources'][key]),'numeric_environment_migrated':False,
        'map_projection_verified':False,'actual_server_verified':False}


def number(value):
    return format(value,'g')if type(value)in(int,float)and math.isfinite(value)else'未知'


def summary_text(result):
    s=result['stage'];level=result['level'];options=level.get('options')or{}
    lines=[s['name']+' · '+('紧急作战'if s['isElite']else'领袖作战'if s['isBoss']else'普通作战'),NOTICE,'',
        '【关卡特点】',version._plain(s.get('description'))]
    if s.get('eliteDesc'):lines+=['紧急变化：'+version._plain(s['eliteDesc'])]
    lines+=['','【关卡原始设置】','可同时部署：'+number(options.get('characterLimit')),
        '开场部署费用：'+number(options.get('initialCost')),'部署费用上限：'+number(options.get('maxCost')),
        '说明：这是关卡设置，不代表当前局的希望、目标生命或最终可部署人数。','',
        '【查看范围】',f"列出{len(result['enemies'])}条敌人/实体引用，含随机候选与关联实体，不能相加为实际敌人数。",
        '主波次、条件分支、隐藏组和预置装置分别保留；图鉴没有列出，不等于关卡没有该实体。',
        '固定原图可以查看；出怪位置在原图上的校准尚未完成，不显示猜测标记。',
        '完整出怪时刻、奖励池、当前保密等级与技能修正后的敌人面板：仍待核对。']
    return '\n'.join(lines)


def enemy_text(enemy):
    lines=[enemy['name']+' · '+TIERS.get(enemy['tier'],'类别未确认'),'','【预计面板】',
        '生命值、攻击力、防御、法抗：未知。当前版本的关卡、保密等级和技能修正尚未完整迁移，不以白值替代。',
        '','【介绍与机制】',enemy['description']or'此精确引用未取得独立介绍。']
    lines+=enemy['abilities']or['此精确引用未取得独立图鉴能力；不能借用同名或派生单位的机制。']
    if not enemy['use_db']:lines+=['本关采用独立配置，未借用数据库图鉴机制。']
    lines+=['','【适用提醒】','这是关卡候选引用，不证明每次都会出现；同一名字不同引用等级保留为不同资料。',
        '图鉴说明不覆盖全部关卡脚本、当前阶段和本局数值。']
    return '\n'.join(lines)


def action_label(action):
    q=action['queue'];prefix=(f"第{q['wave']}波 · 第{q['fragment']}组"if q['kind']=='main'else f"条件分支{q['branch_index']} · 第{q['phase']}段")
    raw=action['raw'];kind=raw.get('actionType')
    names=list(dict.fromkeys(e['name']for e in action['enemy_candidates']))
    title=' / '.join(names)if names else{'ACTIVATE_PREDEFINED':'预置装置或单位','EMPTY':'等待条目','PREVIEW_CURSOR':'路线提示','PLAY_OPERA':'剧情演出','DISPLAY_ENEMY_INFO':'敌人介绍提示'}.get(kind,'关联实体（未取得明确名称）')
    return prefix+' · '+str(action['action_index'])+' · '+title


def action_text(action):
    raw=action['raw'];q=action['queue'];lines=[action_label(action),'',
        '【何时出现】','开场后的准确时刻：未知。这里的等待参数不能直接相加当作实际出怪时刻。']
    if q['kind']=='branch':lines+=['这是条件分支；原始分支名称不证明触发条件、触发次数或实际已发生。','本段配置等待：'+number(q.get('phase_pre_delay'))+' 秒']
    else:lines+=['本波配置等待：'+number(q.get('wave_pre_delay'))+' 秒','本组配置等待：'+number(q.get('fragment_pre_delay'))+' 秒']
    lines+=['本条配置等待：'+number(raw.get('preDelay'))+' 秒','同条目配置间隔：'+number(raw.get('interval'))+' 秒',
        '同条目配置数量：'+number(raw.get('count'))+'（可能是候选，不能直接累计）']
    if raw.get('blockFragment'):lines+=['本条要求阻塞当前组；实际等待结束仍依赖调度与清场条件。']
    if raw.get('hiddenGroup'):lines+=['隐藏组候选：是否启用仍需对应条件；不是必出单位。']
    if raw.get('randomSpawnGroupKey')or raw.get('randomSpawnGroupPackKey'):lines+=['随机组候选：不能把同组所有条目一起相加；这里不提供生成概率。']
    lines+=['','【位置与入口】','原图上的出怪位置：尚未校准。路线编号只作为完整原值保留，不套用旧关卡坐标。']
    if action['predefined_candidates']:lines+=['已找到本关中精确别名对应的预置声明；声明不等于实际生成、击破、开启或领取奖励。']
    if len(action['enemy_candidates'])>1:lines+=['同一引用名称对应多个候选等级，尚未证明实际选择，不能任选一个等级的面板。']
    return '\n'.join(lines)


def picture_bytes(info):
    if type(info)is not dict:return None
    file=info.get('file')
    if type(file)is not str or not file.startswith(('rouge/data/portraits/','rouge/data/current-enemies/')):return None
    try:
        path=version._file(file);raw=path.read_bytes()
        from hashlib import sha1
        if len(raw)!=info['bytes']or sha256(raw).hexdigest()!=info['sha256']or sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=info['git_blob_sha1']:return None
        return raw
    except(OSError,ValueError,TypeError,KeyError):return None
