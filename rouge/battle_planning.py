"""Public fixed-stage planning queries, never live gameplay or RNG simulation."""
from copy import deepcopy
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from functools import lru_cache
import json
from pathlib import Path
from .battle_preview import battle_data, display_cell, enemy_preview
from .spawn_reference import local_sequence

ACTION_LABELS = {'SPAWN':'生成敌人', 'ACTIVATE_PREDEFINED':'激活预置实体',
    'EMPTY':'空动作', 'PREVIEW_CURSOR':'路线预览标记',
    'DISPLAY_ENEMY_INFO':'敌人资料显示', 'PLAY_OPERA':'演出配置'}
LIMITS = ['仅固定公开关卡配置；不操作游戏、不确认实际出场。',
          '不计算候选生成概率，不将所有候选数量相加为实际总数。',
          '局部偏移与配置顺序不是已验证的全局执行时钟。']

def _stage(stage_id):
    try: return battle_data()['stages'][stage_id]
    except (KeyError,TypeError): raise ValueError('没有找到固定战斗关卡。') from None

def _result(stage, **values):
    return {'stage_id':stage['id'], 'stage_name':stage['name'],
        'source':deepcopy(stage['level_source']), 'scope':'offline_fixed_configuration',
        'actual_gameplay_verified':False, 'limits':list(LIMITS), **values}

def action_catalog(stage_id):
    """All main-queue actions, including activation, empty and display actions."""
    stage=_stage(stage_id); rows=[]
    for w in stage['waves']:
        for f in w['fragments']:
            for ordinal,raw in enumerate(f['actions'],1):
                a=deepcopy(raw['action']); typ=a.get('actionType')
                rows.append({'id':raw['id'], 'wave':w['index'], 'fragment':f['index'],
                    'queue_id':f"w{w['index']}.f{f['index']}", 'action_ordinal':ordinal,
                    'type':typ, 'type_label':ACTION_LABELS.get(typ,'未核验动作类型'),
                    'wave_pre_delay_parameter':w['pre_delay'],
                    'wave_post_delay_parameter':w['post_delay'],
                    'wave_max_wait_parameter':w['max_time_waiting_for_next_wave'],
                    'fragment_pre_delay_parameter':f['pre_delay'], 'action':a,
                    'scheduler_fields':{k:a.get(k) for k in ('managedByScheduler','blockFragment',
                        'dontBlockWave','forceBlockWaveInBranch')},
                    'absolute_seconds':None,
                    'source_selector':f"$.waves[{w['index']-1}].fragments[{f['index']-1}].actions[{ordinal-1}]"})
    return _result(stage,actions=rows,action_types=sorted(set(r['type'] for r in rows)))

def predefined_activations(stage_id):
    """Bind activation keys to exact public object aliases, not routeIndex."""
    stage=_stage(stage_id); rows=[]; objects=stage['predefined_objects']
    for row in action_catalog(stage_id)['actions']:
        if row['type']!='ACTIVATE_PREDEFINED': continue
        key=row['action'].get('key'); matches=[o for o in objects if o.get('alias')==key] if key else []
        refs=[]
        for obj in matches:
            refs.append({'alias':obj.get('alias'), 'instance':deepcopy(obj.get('inst')),
                'display_cell':display_cell(obj.get('position'),len(stage['map']),len(stage['map'][0])),
                'direction_parameter':obj.get('direction'), 'hidden_parameter':obj.get('hidden'),
                'skill_index_parameter':obj.get('skillIndex'),
                'skill_rank_parameter':obj.get('mainSkillLvl'), 'actual_activation_seconds':None})
        rows.append({'action_id':row['id'], 'queue_id':row['queue_id'], 'key':key,
            'binding_status':'empty_key' if not key else 'exact_alias' if len(matches)==1 else
                'ambiguous_alias' if matches else 'unresolved_alias', 'objects':refs,
            'random_group':row['action'].get('randomSpawnGroupKey'),
            'source_selector':row['source_selector'], 'actual_active':None})
    return _result(stage,activations=rows,unreferenced_objects=[deepcopy(o) for o in objects
        if not any(r['key']==o.get('alias') for r in rows)],
        binding_rule='alias equality; activation routeIndex is not a spatial lookup')

def candidate_groups(stage_id):
    """Queue-scoped group and package membership, without selecting a winner."""
    stage=_stage(stage_id); actions=action_catalog(stage_id)['actions']; grouped={}; packages={}
    for row in actions:
        a=row['action']; group=a.get('randomSpawnGroupKey'); pack=a.get('randomSpawnGroupPackKey')
        member={'action_id':row['id'],'type':row['type'],'type_label':row['type_label'],
            'key':a.get('key'),'weight_parameter':a.get('weight'),'count_parameter':a.get('count'),
            'hidden_group':a.get('hiddenGroup'),'empty_key':not bool(a.get('key')),
            'package_key':pack,'source_selector':row['source_selector']}
        if group: grouped.setdefault((row['queue_id'],group),[]).append(member)
        if pack: packages.setdefault((row['queue_id'],pack),[]).append({**member,'group_key':group})
    groups=[]
    for (queue,key),members in grouped.items():
        groups.append({'queue_id':queue,'group_key':key,'candidates':deepcopy(members),
            'actual_choice':None,'probabilities':None,
            'companion_packages':[{'package_key':p,'members':deepcopy(packages[(queue,p)])}
                for p in dict.fromkeys(m['package_key'] for m in members if m['package_key'])]})
    return _result(stage,groups=groups,packages=[{'queue_id':q,'package_key':p,'members':deepcopy(m)}
        for (q,p),m in packages.items()],
        grouping_rule='queue identity and raw key equality; no actual selection inferred')

def local_time_window(stage_id,start_seconds,end_seconds,*,limit=4096):
    """Query nominal action occurrences separately in each fragment anchor."""
    from .spawn_reference import finite_nonnegative
    import heapq
    if not finite_nonnegative(start_seconds) or not finite_nonnegative(end_seconds) or start_seconds>end_seconds:
        raise ValueError('局部时间窗需要有限、非负且有序的秒数。')
    if type(limit) is not int or not 1<=limit<=4096: raise ValueError('展示上限需要1–4096整数。')
    stage=_stage(stage_id); queues={}; start=Decimal(str(start_seconds)); end=Decimal(str(end_seconds))
    for row in action_catalog(stage_id)['actions']:
        queue=queues.setdefault(row['queue_id'],{'queue_id':row['queue_id'],'anchor':'fragment_action_queue_start',
            'occurrences':[],'matching_declared_occurrences':0,'pending':[],
            'fragment_pre_delay_parameter':row['fragment_pre_delay_parameter'],
            'absolute_start_seconds':None,'truncated':False,'_streams':[]})
        seq=local_sequence(row,limit=0)
        if seq['pending']:
            queue['pending'].append({'action_id':row['id'],'reasons':seq['pending']}); continue
        count=seq['count']
        if not count: continue
        a=row['action']; delay=Decimal(str(a['preDelay'])); interval=Decimal(str(a['interval']))
        if not interval: first=0; last=count-1 if start<=delay<=end else -1
        else:
            first=max(0,int(((start-delay)/interval).to_integral_value(rounding=ROUND_CEILING)))
            last=min(count-1,int(((end-delay)/interval).to_integral_value(rounding=ROUND_FLOOR)))
        matches=max(0,last-first+1); queue['matching_declared_occurrences']+=matches
        if matches: heapq.heappush(queue['_streams'],(delay+first*interval,row['action_ordinal'],first,last,interval,row))
    for queue in queues.values():
        streams=queue.pop('_streams'); queue['truncated']=queue['matching_declared_occurrences']>limit
        while streams and len(queue['occurrences'])<limit:
            offset,_,i,last,interval,row=heapq.heappop(streams);a=row['action']
            queue['occurrences'].append({'action_id':row['id'],'ordinal':i+1,'type':row['type'],
                'type_label':row['type_label'],'key':a.get('key'),'offset_seconds':float(offset),
                'configured_action_ordinal':row['action_ordinal'],
                'conditional':bool(a.get('hiddenGroup') or a.get('randomSpawnGroupKey') or a.get('randomSpawnGroupPackKey'))})
            if i<last: heapq.heappush(streams,(offset+interval,row['action_ordinal'],i+1,last,interval,row))
        queue['count_is_actual_enemy_total']=False
    return _result(stage,start_seconds=start_seconds,end_seconds=end_seconds,queues=list(queues.values()),
        sorting_rule='nominal offset then serialized action order; not a native same-frame proof')

def enemy_entry_sources(stage_id,enemy_id,level):
    """Reverse-link a selected enemy reference to every configured entry source."""
    stage=_stage(stage_id)
    if type(level) is not int or level<0: raise ValueError('敌人引用等级需要非负整数。')
    refs=[e for e in stage['enemies'] if e['id']==enemy_id]
    selected=[e for e in refs if e['level']==level]
    if len(selected)!=1: raise ValueError('敌人及等级必须与关卡引用唯一匹配。')
    levels=sorted(set(e['level'] for e in refs)); sources=[]
    for row in action_catalog(stage_id)['actions']:
        if row['type']=='SPAWN' and row['action'].get('key')==enemy_id:
            sources.append({'kind':'main_queue','id':row['id'],'queue_id':row['queue_id'],
                'source_selector':row['source_selector'],'action':row['action'],
                'local_sequence':local_sequence(row,limit=16)})
    for row in stage['branch_spawns']:
        if row['action'].get('key')==enemy_id:
            sources.append({'kind':'conditional_branch','id':row['id'],'branch':row['branch'],
                'phase':row['phase'],'action':deepcopy(row['action']),
                'local_sequence':local_sequence(row,limit=16),'route_scope_verified':False})
    for index,record in enumerate(stage['initial_enemy_records']):
        # Preserve full records and match only explicit identity fields.
        if isinstance(record,dict) and (record.get('id')==enemy_id or record.get('enemyId')==enemy_id):
            sources.append({'kind':'initial_record','index':index,'raw':deepcopy(record),
                'actual_entry_seconds':None})
    return _result(stage,enemy_id=enemy_id,level=level,name=selected[0]['name'],
        referenced_levels=levels,action_level_binding_unique=len(levels)==1,
        entry_sources=sources,actual_enemy_count=None,
        limits=list(LIMITS)+['动作key不包含等级；多个引用等级时不得据此猜有效等级。'])

@lru_cache(maxsize=1)
def _branch_data():
    return json.loads((Path(__file__).with_name('data')/'battle-branches.json').read_text(encoding='utf-8'))

def branch_phase_catalog(stage_id,branch_id=None):
    """Complete original phases, including empty phases and non-SPAWN actions."""
    stage=_stage(stage_id); reference=_branch_data()['stages'].get(stage_id)
    if reference is None or reference['source']!=stage['level_source']:
        raise ValueError('分支原件与关卡来源不匹配。')
    branches=reference['branches']
    if branch_id is not None and branch_id not in branches: raise ValueError('关卡没有该条件分支。')
    result=[]
    for key,branch in branches.items():
        if branch_id is not None and key!=branch_id: continue
        phases=[]
        for ordinal,phase in enumerate(branch.get('phases') or [],1):
            actions=[]
            for ai,a in enumerate(phase.get('actions') or [],1):
                row={'branch':key,'action':a}; seq=local_sequence(row,limit=16)
                actions.append({'id':f'branch:{key}.p{ordinal}.a{ai}',
                    'type_label':ACTION_LABELS.get(a.get('actionType'),'未核验动作类型'),
                    'action':deepcopy(a),'local_sequence':seq,
                    'route_scope_verified':False,
                    'source_selector':f'$.branches[{json.dumps(key)}].phases[{ordinal-1}].actions[{ai-1}]'})
            phases.append({'phase':ordinal,'pre_delay_parameter':phase.get('preDelay'),
                'actions':actions,'empty_configuration':not bool(actions),'actual_activation_seconds':None})
        result.append({'branch_id':key,'phases':phases,'phase_count':len(phases),
            'trigger_mechanism':None,'phase_selection':None,'raw_nonphase_fields':deepcopy(
                {k:v for k,v in branch.items() if k!='phases'})})
    return _result(stage,branches=result,limits=list(LIMITS)+[
        '完整阶段目录不证明当前触发、游标推进、回绕或随机选阶段规则。',
        'routeIndex缺少运行时基础/额外路线选择，分支位置保持未知。'])

def route_segments(stage_id,route_index):
    """Separate serialized spatial segments at disappearance/reappearance."""
    stage=_stage(stage_id)
    if type(route_index) is not int or not 0<=route_index<len(stage['routes']):
        raise ValueError('基础路线引用需要有效整数。')
    route=stage['routes'][route_index]; rows=len(stage['map']); cols=len(stage['map'][0])
    supported=route.get('motionMode') in ('WALK','FLY'); segments=[]; current=[]; waits=[]; transitions=[]; pending=[]
    def cell(pos): return display_cell(pos,rows,cols) if supported else None
    start=cell(route.get('startPosition')); end=cell(route.get('endPosition'))
    if start: current.append({'kind':'start','cell':start})
    for index,cp in enumerate(route.get('checkpoints') or []):
        typ=cp.get('type'); entry={'checkpoint_index':index,'type':typ,'time_parameter':cp.get('time')}
        if typ=='DISAPPEAR':
            if current: segments.append(current); current=[]
            transitions.append({**entry,'display_cell':None,'kind':'disappear'})
        elif typ=='APPEAR_AT_POS':
            if current: segments.append(current); current=[]
            c=cell(cp.get('position')); transitions.append({**entry,'display_cell':c,'kind':'appear'})
            if c: current.append({'kind':'appear','cell':c,'checkpoint_index':index})
            else: pending.append({'checkpoint_index':index,'reason':'再出现位置无法映射。'})
        elif typ=='MOVE':
            c=cell(cp.get('position'))
            if c: current.append({'kind':'move','cell':c,'checkpoint_index':index})
            else: pending.append({'checkpoint_index':index,'reason':'移动检查点超出地图或移动类型未确认。'})
        elif typ in ('WAIT_FOR_SECONDS','WAIT_CURRENT_FRAGMENT_TIME'):
            waits.append({**entry,'display_cell':None,'anchor':'elapsed_fragment_time' if typ=='WAIT_CURRENT_FRAGMENT_TIME' else 'arrival_local_wait',
                'arrival_seconds':None})
        else: pending.append({'checkpoint_index':index,'reason':'未核验检查点类型：'+str(typ)})
    if end: current.append({'kind':'end','cell':end})
    if current: segments.append(current)
    return _result(stage,route_index=route_index,motion=route.get('motionMode'),
        segments=segments,transitions=transitions,waits=waits,pending=pending,
        spawn_offset_parameter=deepcopy(route.get('spawnOffset')),
        spawn_random_range_parameter=deepcopy(route.get('spawnRandomRange')),
        actual_path=None,arrival_seconds=None,projection_plane='serialized nominal grid cells',
        limits=list(LIMITS)+['不连接消失前与再出现后的轨迹；等待的占位坐标不映射为地图位置。',
            '分段折线是配置参考，不证明寻路、三维脚点、出生偏移或地形可通行性。'])
