"""Read-only battle references. Raw scheduling fields do not imply a global clock."""
import copy,json,math
from functools import lru_cache
from pathlib import Path
from .run_modifiers import prepare_run
from .spawn_reference import movement_reference,sequence_text

DATA=Path(__file__).with_name('data')

@lru_cache(maxsize=1)
def battle_data():
    return json.loads((DATA/'battle-previews.json').read_text(encoding='utf-8'))

def display_cell(position,rows,cols):
    if not isinstance(position,dict):return None
    r=position.get('row');c=position.get('col')
    if any(isinstance(x,bool) or not isinstance(x,int) for x in (r,c)):return None
    if not (0<=r<rows and 0<=c<cols):return None
    return {'row':rows-1-r,'col':c}

def route_reference(stage,index):
    routes=stage['routes'];rows=len(stage['map']);cols=len(stage['map'][0])
    if isinstance(index,bool) or not isinstance(index,int) or not 0<=index<len(routes):
        return {'start':None,'end':None,'points':[],'checkpoints':[],'pending':['基础路线引用缺失或越界。']}
    route=routes[index];start=display_cell(route.get('startPosition'),rows,cols)
    if route.get('motionMode') not in ('WALK','FLY'):
        return {'start':None,'end':None,'points':[],'checkpoints':[],
            'pending':['路线移动类型未定义，不能将序列化占位坐标当出生格。']}
    end=display_cell(route.get('endPosition'),rows,cols)
    points=[];checkpoints=[];pending=[]
    if start:points.append({'kind':'start',**start})
    for cp in route.get('checkpoints') or []:
        # WAIT positions can be serialized placeholders; only spatial types map.
        cell=display_cell(cp.get('position'),rows,cols) if cp['type'] in ('MOVE','APPEAR_AT_POS') else None
        checkpoints.append({'type':cp['type'],'time':cp.get('time'),'cell':cell})
        if cell:points.append({'kind':cp['type'],**cell})
    if end:points.append({'kind':'end',**end})
    if not start or not end:pending.append('路线存在地图外端点；不裁剪为地图内出生格。')
    offset=route.get('spawnOffset') or {};random_range=route.get('spawnRandomRange') or {}
    if any(v for d in (offset,random_range) for v in d.values()):pending.append('存在出生偏移/随机范围，图上标记仅为名义格。')
    if any(c['type'] in ('DISAPPEAR','APPEAR_AT_POS') for c in checkpoints):
        pending.append('包含消失/再出现检查点；不连接为连续寻路轨迹。')
    return {'start':start,'end':end,'points':points,'checkpoints':checkpoints,
        'motion':route.get('motionMode'),'offset':copy.deepcopy(offset),
        'random_range':copy.deepcopy(random_range),'pending':pending,
        'path_is_actual':False,'continuous_reference':not any(c['type'] in ('DISAPPEAR','APPEAR_AT_POS') for c in checkpoints)}

def hidden_group_reference(stage,group):
    if not group:return {'group':None,'enabled_by_stage_rune':False,'status':'no_hidden_group'}
    rules=[r for r in stage['runes'] if r['key']=='level_hidden_group_enable' and
        any(b.get('key')=='key' and b.get('valueStr')==group for b in r.get('blackboard') or [])]
    enabled=any(r.get('difficultyMask') in (stage['difficulty'],'ALL') for r in rules)
    return {'group':group,'enabled_by_stage_rune':enabled,
        'status':'stage_rune_enabled' if enabled else 'activation_unknown'}

def spawn_rows(stage_id,wave=None,enemy_id=None,include_branches=True):
    stage=battle_data()['stages'].get(stage_id)
    if not stage:return []
    result=[]
    for w in stage['waves']:
        if wave is not None and w['index']!=wave:continue
        for f in w['fragments']:
            for raw in f['actions']:
                a=raw['action']
                if a['actionType']!='SPAWN' or (enemy_id and a['key']!=enemy_id):continue
                result.append({'id':raw['id'],'wave':w['index'],'fragment':f['index'],
                    'wave_pre_delay':w['pre_delay'],'wave_post_delay':w['post_delay'],
                    'wave_max_wait':w['max_time_waiting_for_next_wave'],'fragment_pre_delay':f['pre_delay'],
                    'action':copy.deepcopy(a),'route':route_reference(stage,a.get('routeIndex')),
                    'hidden':hidden_group_reference(stage,a.get('hiddenGroup')),
                    'absolute_time':None,'probability':None,'branch':None})
    if include_branches and wave is None:
        for raw in stage['branch_spawns']:
            a=raw['action']
            if enemy_id and a['key']!=enemy_id:continue
            result.append({**copy.deepcopy(raw),'wave':None,'fragment':None,
                'route':{'start':None,'end':None,'points':[],'checkpoints':[],
                    'pending':['条件分支缺少运行时useExtraRoute选择字段；不能按routeIndex借用基础或额外路线定位。']},
                'hidden':hidden_group_reference(stage,a.get('hiddenGroup')),
                'absolute_time':None,'probability':None})
    return result

def enemy_preview(stage_id,enemy_id,level,run_config=None):
    stage=battle_data()['stages'][stage_id]
    matches=[e for e in stage['enemies'] if e['id']==enemy_id and e['level']==level]
    if len(matches)!=1:raise ValueError('敌人必须与本关卡的引用等级唯一匹配。')
    entry=copy.deepcopy(matches[0]);config=copy.deepcopy(run_config or {})
    from .enemy_skills import enemy_skill_reference
    entry['skill_reference']=enemy_skill_reference(stage_id,enemy_id,level)
    entry['movement_reference']=movement_reference(stage,entry['reference_stats'].get('moveSpeed'))
    scenario={'target_enemy':{'stage_id':stage_id,'enemy_id':enemy_id,'level':level},'run_config':config}
    try:
        _,resolution=prepare_run(scenario)
        entry['environment']=resolution['enemy']
        entry['context_pending']=resolution['pending']
    except (ValueError,KeyError) as error:
        entry['environment']=None;entry['context_pending']=['本局环境无法确认：'+str(error)]
    entry['limits']=['扩展属性（攻速/移动/重量等）仅为引用基础值，未模拟敌人技能、阶段或动画。',
        '本预览不套用藏品；含藏品的目标参考请在伤害测试页查看。',
        '图鉴未列出的阶段、技能参数和隐藏触发条件仍需核验。']
    return entry

def value_text(value):
    if value is None:return '未知'
    if isinstance(value,bool):return '是（明确字段）' if value else '否（明确字段）'
    if isinstance(value,(int,float)) and math.isfinite(value):return f'{value:g}'
    return str(value)

def enemy_text(entry):
    labels=(('maxHp','生命值'),('atk','攻击力'),('def','防御'),('magicResistance','法抗'))
    lines=[f"{entry['name']} · {entry['id']} · 引用等级 {entry['level']}",
        '预计面板（本局环境；藏品目标结果见伤害测试）：']
    env=entry['environment']
    confirmed=env and not entry['context_pending']
    for key,label in labels:lines.append('预计'+label+'：'+value_text(env['stats'].get(key) if confirmed else None))
    if env and confirmed:
        lines.extend(step['label'] for step in env['steps'])
        if env['damage_factor']!=1:lines.append('预计承伤倍率：'+value_text(env['damage_factor']))
    lines.extend(('预计攻速：未知（技能/阶段/其他修正未核验）',
        '预计攻击间隔：未知（技能/阶段/动画未核验）',
        '预计有效移速：未知（未推算移动入场时间）'))
    lines.extend('\n待确认：'+s for s in entry['context_pending'])
    lines.append('\n攻击方式：'+value_text(entry.get('attack_way'))+'；移动方式：'+value_text(entry.get('motion')))
    types={'PHYSIC':'物理','MAGIC':'法术','REAL':'真实','NONE':'无','NO_DAMAGE':'不造成伤害','HEAL':'治疗'}
    lines.append('图鉴伤害类型：'+(' / '.join(types.get(x,x) for x in entry['damage_types']) or '未知'))
    lines.append('\n机制资料：')
    lines.append(entry['description'] or entry['handbook_description'] or '未取得描述。')
    lines.extend('• '+text for text in entry['abilities'])
    from .enemy_skills import enemy_skill_text
    lines.append('\n'+enemy_skill_text(entry['skill_reference']))
    immunity_names={'stunImmune':'眩晕','silenceImmune':'沉默','sleepImmune':'沉睡',
        'frozenImmune':'冻结','levitateImmune':'浮空','disarmedCombatImmune':'缴械',
        'fearedImmune':'恐惧','palsyImmune':'麻痹','attractImmune':'吸引',
        'teleportImmune':'传送','groundBoundImmune':'束缚'}
    lines.append('\n免疫字段（未定义保持未知）：')
    lines.extend(immunity_names[k]+'：'+value_text(v) for k,v in entry['immunity_reference'].items())
    lines.extend(('\n以上预计面板只覆盖已核验的本局环境；不代表敌人所有技能或阶段均已模拟。',
                  '含藏品的目标预测结果请在伤害测试页查看。'))
    return '\n'.join(lines)

def spawn_text(row,stage_id):
    a=row['action'];route=row['route'];cell=route['start']
    lines=[('第'+str(row['wave'])+'波，第'+str(row['fragment'])+'片段' if row['wave'] else
        '条件分支 '+row['branch']+'，阶段'+str(row['phase'])),
        '出生位置：'+(f"格图自上第{cell['row']+1}行、第{cell['col']+1}列" if cell else '未知/未映射'),
        '绝对出场时刻：未知（调度起点、阻塞及脚本条件未核验）',
        '调度参数参考；以下不直接相加为全局时间：']
    if row['wave']:
        lines.extend('波 '+name+'：'+value_text(row.get(key)) for name,key in
            (('preDelay','wave_pre_delay'),('postDelay','wave_post_delay'),
             ('maxTimeWaitingForNextWave','wave_max_wait')))
        lines.append('片段 preDelay：'+value_text(row['fragment_pre_delay']))
    else:lines.append('分支阶段 preDelay：'+value_text(row['phase_pre_delay']))
    lines.extend('条目 '+k+'：'+value_text(a.get(k)) for k in
        ('preDelay','interval','count','managedByScheduler','blockFragment','dontBlockWave','forceBlockWaveInBranch'))
    if a.get('hiddenGroup'):
        lines.append('隐藏组：'+a['hiddenGroup']+'；'+('本变体符文声明启用' if row['hidden']['enabled_by_stage_rune'] else '启用条件待核验'))
    if a.get('randomSpawnGroupKey') or a.get('randomSpawnGroupPackKey'):
        lines.extend(('随机候选组：'+str(a.get('randomSpawnGroupKey')),
            '随机候选包：'+str(a.get('randomSpawnGroupPackKey')),
            '原始权重：'+value_text(a.get('weight'))+'（非概率）'))
    lines.append('资料条目不保证实际出场，count不跨随机候选相加。')
    lines.append('\n'+sequence_text(row))
    if route.get('checkpoints'):
        lines.append('\n路线检查点参考（不推算移动到达时刻）：')
        for cp in route['checkpoints']:
            c=cp['cell']
            lines.append(cp['type']+'：'+(f"第{c['row']+1}行、第{c['col']+1}列" if c else '非空间点')+'；time='+value_text(cp['time']))
    lines.extend(route['pending'])
    lines.append('\n来源：'+battle_data()['stages'][stage_id]['level_source']['url'])
    reference=battle_data()['source'].get('scheduling_reference')
    if reference:lines.append('局部调度资料：'+reference['url'])
    return '\n'.join(lines)
