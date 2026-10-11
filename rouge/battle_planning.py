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
