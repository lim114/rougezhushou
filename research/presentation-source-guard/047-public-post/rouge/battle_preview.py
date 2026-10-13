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

ATTACK_WAY_LABELS={'MELEE':'近战','RANGED':'远程','ALL':'近战与远程','NONE':'不攻击'}
MOTION_LABELS={'WALK':'地面','FLY':'飞行'}
DAMAGE_TYPE_LABELS={'PHYSIC':'物理','MAGIC':'法术','REAL':'真实','NONE':'无',
    'NO_DAMAGE':'不造成伤害','HEAL':'治疗'}
CHECKPOINT_LABELS={'MOVE':'移动至指定位置','WAIT_FOR_SECONDS':'原地等待',
    'WAIT_CURRENT_FRAGMENT_TIME':'等待当前片段计时至指定时点',
    'DISAPPEAR':'消失','APPEAR_AT_POS':'在指定位置出现'}

def enemy_text(entry,technical=False):
    labels=(('maxHp','生命值'),('atk','攻击力'),('def','防御'),('magicResistance','法抗'))
    lines=[entry['name'],'','【预计面板】']
    env=entry['environment']
    confirmed=env and not entry['context_pending']
    for key,label in labels:lines.append('预计'+label+'：'+value_text(env['stats'].get(key) if confirmed else None))
    if env and confirmed:
        if env['damage_factor']!=1:lines.append('预计承伤倍率：'+value_text(env['damage_factor']))
    lines.extend(('预计攻速：未知（技能/阶段/其他修正未核验）',
        '预计攻击间隔：未知（技能/阶段/动画未核验）',
        '预计有效移速：未知（未推算移动入场时间）'))
    if entry['context_pending']:
        pending=[s for s in entry['context_pending'] if not s.startswith('关卡脚本修正待核验：')]
        scripts=len(entry['context_pending'])-len(pending)
        if scripts:pending.insert(0,f'有{scripts}项关卡脚本修正待核验，原始字段可在技术资料中查看。')
        lines.extend(['','【面板待确认】',*('• '+s for s in pending)])
    elif env and env['steps']:
        lines.extend(['','本局环境修正：',*('• '+step['label'] for step in env['steps'])])
    lines.extend(['','【作战特征】',
        '攻击方式：'+ATTACK_WAY_LABELS.get(entry.get('attack_way'),'未知（分类未核验）')+
        '；移动方式：'+MOTION_LABELS.get(entry.get('motion'),'未知（分类未核验）')])
    lines.append('图鉴伤害类型：'+(' / '.join(DAMAGE_TYPE_LABELS.get(x,'未知（类型未核验）')
        for x in entry['damage_types']) or '未知'))
    lines.append('以上方式为图鉴分类；具体阶段和行为见机制资料。')
    lines.extend(['','【机制资料】'])
    lines.append(entry['description'] or entry['handbook_description'] or '未取得描述。')
    lines.extend('• '+text for text in entry['abilities'])
    from .enemy_skills import enemy_skill_text
    lines.append('\n'+enemy_skill_text(entry['skill_reference'],technical=technical))
    immunity_names={'stunImmune':'眩晕','silenceImmune':'沉默','sleepImmune':'沉睡',
        'frozenImmune':'冻结','levitateImmune':'浮空','disarmedCombatImmune':'缴械',
        'fearedImmune':'恐惧','palsyImmune':'麻痹','attractImmune':'吸引',
        'teleportImmune':'传送','groundBoundImmune':'束缚'}
    lines.extend(['','【异常免疫】','下列“是/否”仅来自明确字段；未定义项保持未知。'])
    immune=[immunity_names.get(k,'未核验免疫类型')+'：'+('未知' if v is None else '是' if v is True else '否' if v is False else '未知')
        for k,v in entry['immunity_reference'].items()]
    for start in range(0,len(immune),3):lines.append('；'.join(immune[start:start+3]))
    lines.extend(['','【预测范围】',
        '预计面板只覆盖已核验的本局环境；不代表所有敌人技能或阶段均已模拟。',
        '含藏品的目标预测结果请在伤害测试页查看。'])
    if technical:
        lines.extend(['','【敌人技术资料】',
            f"原始敌人标识：{entry['id']}；本关卡引用等级：{entry['level']}",
            '原始攻击方式：'+value_text(entry.get('attack_way'))+'；原始移动方式：'+value_text(entry.get('motion')),
            '原始伤害类型：'+json.dumps(entry['damage_types'],ensure_ascii=False),
            '免疫引用字段：'+json.dumps(entry['immunity_reference'],ensure_ascii=False),
            '环境待确认原文：'+json.dumps(entry['context_pending'],ensure_ascii=False)])
        source=battle_data()['source']
        for key,label in (('enemy_database','敌人原始数据'),('handbook','中文图鉴')):
            if source.get(key,{}).get('url'):lines.append(label+'：'+source[key]['url'])
    return '\n'.join(lines)

def spawn_text(row,stage_id,technical=False):
    a=row['action'];route=row['route'];cell=route['start']
    lines=['【出场条目】',('第'+str(row['wave'])+'波 · 第'+str(row['fragment'])+'片段' if row['wave'] else
        '条件分支 · 第'+str(row['phase'])+'阶段'),
        '出生位置：'+(f"格图自上第{cell['row']+1}行、第{cell['col']+1}列" if cell else '未知/未映射'),
        '绝对出场时刻：未知（调度起点、阻塞及脚本条件未核验）']
    lines.extend(['','【出场条件】','本条目生成数量：'+value_text(a.get('count'))])
    if row.get('branch'):lines.append('此条目属于条件分支；触发时刻和阶段选择仍待核验。')
    if a.get('hiddenGroup'):
        lines.append('隐藏组：'+('本关卡变体符文声明启用' if row['hidden']['enabled_by_stage_rune'] else '启用条件待核验'))
    if a.get('randomSpawnGroupKey') or a.get('randomSpawnGroupPackKey'):
        lines.append('此条目属于随机候选；原始权重：'+value_text(a.get('weight'))+'（非概率）。')
    lines.append('资料条目不保证实际出场；生成数量不跨随机候选相加。')
    lines.extend(['','【局部时间计划】',sequence_text(row)])
    lines.extend(['','【调度参考】','以下是配置参数，不直接相加为全局时间。'])
    if row['wave']:
        lines.extend(label+'：'+value_text(row.get(key))+'秒' for key,label in
            (('wave_pre_delay','本波开始前延迟'),('wave_post_delay','本波清场后的延迟'),
             ('fragment_pre_delay','本片段开始前延迟')))
        max_wait=row.get('wave_max_wait')
        lines.append('本波清场等待上限：'+('无上限（原始配置为负一）' if max_wait==-1 else
            value_text(max_wait)+'秒（配置；实际清场等待仍未知）'))
    else:lines.append('分支阶段开始前延迟：'+value_text(row.get('phase_pre_delay'))+'秒')
    lines.extend(['本条目首次生成前延迟：'+value_text(a.get('preDelay'))+'秒',
        '同条目相邻生成间隔：'+value_text(a.get('interval'))+'秒'])
    if route.get('checkpoints'):
        lines.extend(['','【路线检查点】','以下是路线配置参考，不推算移动到达时刻。'])
        for cp in route['checkpoints']:
            c=cp['cell'];typ=cp['type'];label=CHECKPOINT_LABELS.get(typ,'未知检查点类型')
            if typ in ('WAIT_FOR_SECONDS','WAIT_CURRENT_FRAGMENT_TIME'):
                lines.append('• '+label+'：'+value_text(cp['time'])+'秒（配置）')
            else:
                location=f"第{c['row']+1}行、第{c['col']+1}列" if c else ('非空间检查点' if typ=='DISAPPEAR' else '未映射到空间格')
                lines.append('• '+label+'：'+location)
    if route['pending']:
        lines.extend(['','【位置待确认】',*(s.replace('条件分支缺少运行时useExtraRoute选择字段；不能按routeIndex借用基础或额外路线定位。',
            '条件分支缺少基础/额外路线选择信息，不能借用其他路线定位。') for s in route['pending'])])
    if technical:
        lines.extend(['','【出场技术资料】','关卡标识：'+stage_id+'；条目标识：'+str(row.get('id')),
            '原始分支标识：'+value_text(row.get('branch')),
            '波/片段/分支阶段引用参数：'+json.dumps({key:row.get(key) for key in
                ('wave_pre_delay','wave_post_delay','wave_max_wait','fragment_pre_delay','phase_pre_delay')},ensure_ascii=False),
            '原始生成动作：'+json.dumps(a,ensure_ascii=False),
            '路线引用结构（显示行列；非完整原始路径）：'+json.dumps(route,ensure_ascii=False),
            '来源：'+battle_data()['stages'][stage_id]['level_source']['url']])
        reference=battle_data()['source'].get('scheduling_reference')
        if reference:lines.append('局部调度资料：'+reference['url'])
    return '\n'.join(lines)
