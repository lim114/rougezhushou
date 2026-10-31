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

def enemy_preview(stage_id,enemy_id,level,run_config=None,*,difficulty_reference=None):
    stage=battle_data()['stages'][stage_id]
    matches=[e for e in stage['enemies'] if e['id']==enemy_id and e['level']==level]
    if len(matches)!=1:raise ValueError('敌人必须与本关卡的引用等级唯一匹配。')
    entry=copy.deepcopy(matches[0]);config=copy.deepcopy(run_config or {})
    from .enemy_skills import enemy_skill_reference
    entry['skill_reference']=enemy_skill_reference(stage_id,enemy_id,level)
    from .enemy_panel import enemy_panel_reference
    entry['fixed_panel_reference']=enemy_panel_reference(stage_id,enemy_id,level)
    entry['raw_reference_stats']=copy.deepcopy(entry['reference_stats'])
    entry['reference_stats']=copy.deepcopy(entry['fixed_panel_reference']['attributes'])
    entry['movement_reference']=movement_reference(stage,entry['reference_stats'].get('moveSpeed'))
    scenario={'target_enemy':{'stage_id':stage_id,'enemy_id':enemy_id,'level':level},'run_config':config}
    try:
        partial=entry['fixed_panel_reference']['construction_reference']['mode']=='stage_constructor' and any(
            entry['fixed_panel_reference']['attributes'].get(k) is None for k in ('maxHp','atk','def','magicResistance'))
        _,resolution=prepare_run(scenario,enemy_panel_only=partial,difficulty_reference=difficulty_reference)
        entry['environment']=resolution['enemy']
        entry['context_pending']=resolution['pending']
    except (ValueError,KeyError) as error:
        entry['environment']=None;entry['context_pending']=['本局环境无法确认：'+str(error)]
    if not entry['fixed_panel_reference']['compiled_database_result_available']:
        entry['context_pending'].append('固定敌人构造来源不可用；数据库精确等级或关卡独立覆盖缺失，完整预计面板未知。')
    entry['limits']=['扩展属性（攻速/移动/重量等）仅为引用基础值，未模拟敌人技能、阶段或动画。',
        '本预览不套用藏品；含藏品的目标参考请在伤害测试页查看。',
        '图鉴未列出的阶段、技能参数和隐藏触发条件仍需核验。']
    from .rare_reward_sources import enemy_reward_reference
    reward_reference=enemy_reward_reference(stage_id,enemy_id,level)
    if reward_reference:entry['conditional_reward_reference']=reward_reference
    from .auxiliary_enemy_mechanisms import reference_for
    auxiliary=reference_for(stage_id,enemy_id,level,entry['fixed_panel_reference'])
    if auxiliary:entry['auxiliary_mechanism_reference']=auxiliary
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
    if not technical:
        lines.append('适用范围：当前固定关卡与已确认的本局环境；不含藏品，也不跟踪战斗中的技能或阶段变化。')
        if not confirmed:lines.append('面板尚有条件未确认，未知不等于0；原因见下方“面板待确认”。')
    if env and not confirmed and entry['fixed_panel_reference']['construction_reference']['mode']=='stage_constructor':
        lines.extend(['','【已证环境分项】','以下仅含已绑定构造值和已证环境修正，未含待确认修正；不能当完整预计面板。'])
        for key,label in labels:lines.append(label+'已证分项：'+value_text(env['stats'].get(key)))
    if env and confirmed:
        if env['damage_factor']!=1:lines.append('预计承伤倍率：'+value_text(env['damage_factor']))
    lines.extend(('预计攻速：未知（技能/阶段/其他修正未核验）',
        '预计攻击间隔：未知（技能/阶段/动画未核验）',
        '预计有效移速：未知（未推算移动入场时间）'))
    movement=entry.get('movement_reference',{}).get('conditional_native_movement')
    if movement is not None:
        lines.extend(['','【移速条件分项】',
            '符文写入移速属性：'+value_text(movement.get('written_move_speed_attribute')),
            '无其他属性修正的条件移速：'+value_text(movement.get('conditional_speed_tiles_per_second'))+' 格/秒',
            '条件：符文实际写入、使用标准范围且无额外移动属性修正；不代表当前完整移速或入场时刻。'])
    if entry.get('fixed_panel_reference'):
        from .enemy_panel import enemy_panel_text
        lines.extend(['',enemy_panel_text(entry['fixed_panel_reference'],technical=technical)])
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
    if not technical:lines.append('以下为图鉴与已核验的条件资料；请与上方预计面板分开阅读，不代表所有机制已模拟。')
    lines.append(entry['description'] or entry['handbook_description'] or '未取得描述。')
    lines.extend('• '+text for text in entry['abilities'])
    reward=entry.get('conditional_reward_reference')
    if reward:
        outcome=reward['rule']['outcomes'][0];quantity=outcome['quantity']
        amount=f'{quantity}件收藏品' if quantity is not None else '数量未知'
        lines += ['','【宝藏条件参考】',
            f'本级别文档：击倒后战斗结算 {amount}；完整收藏品池未知。',
            f"本关固定生成引用 {reward['fixed_spawn_reference_count']}条；引用数不是实际出现或击倒数。",
            '实际出现、击倒、当前模式结算和已领取数量：未知；不合入预计面板或完整奖励总量。']
        if technical:lines.append('条件数量文档：'+reward['rule']['quantity_source']['url'])
    from .auxiliary_enemy_mechanisms import reference_text
    auxiliary=entry.get('auxiliary_mechanism_reference')
    if auxiliary:lines.append('\n'+reference_text(auxiliary,technical=technical))
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
        movement=entry['movement_reference']
        rune=movement.get('stage_move_speed_rune_reference')
        if rune:
            lines.extend(['关卡移速符文参数参考：'+value_text(rune['parameter']),
                '基础移速×关卡倍率小计：'+value_text(movement['base_times_stage_speed'])])
            component=movement.get('conditional_native_movement')
            if component is not None:
                lines.extend(['符文与关卡倍率合成的移速：未知；字段接收、乘法写入及读取层已绑定，实际执行资格/动态修正尚未核验；实际实例的原生目标、写入及叠加层尚未核验。',
                    '符文与关卡倍率条件合成移速：'+value_text(component.get('conditional_speed_tiles_per_second'))+' 格/秒',
                    '条件分项采用公开标准无上限分支；未写最大范围标志及选择器指针的原生分配基线未闭合。',
                    '原生条件分项数据：'+json.dumps(component,ensure_ascii=False)])
            else:lines.append('符文与关卡倍率合成的移速：未知；原生目标、写入及叠加层尚未核验。')
            if rune['source']:lines.append('关卡移速参数来源：'+rune['source']['url'])
        source=battle_data()['source']
        for key,label in (('enemy_database','敌人原始数据'),('handbook','中文图鉴')):
            if source.get(key,{}).get('url'):lines.append(label+'：'+source[key]['url'])
    else:
        # The detailed helpers retain their source terminology in technical
        # mode. Ordinary readers need the meaning and uncertainty instead.
        readable=[]
        for line in '\n'.join(lines).splitlines():
            if '项扩展字段已有明确来源，完整值仍未知' in line:
                line='部分额外属性已有资料可查，但不能直接当作本局完整数值；详细记录见技术资料。'
            elif line.startswith('基包配置分项：'):
                line='固定资料中记载了一些招式和机制；完整记录见技术资料，不能据此断定当前全部生效。'
            readable.append(line)
        lines=readable
        replacements={
            '该引用要求数据库精确等级而条目缺失；不能以别名或默认路径替代所选构造模式。':'缺少当前敌人等级的完整资料，不能套用其他等级或同名敌人的数值。',
            '原始等级定义与本关卡覆盖分别保留，未推定合并为当前实战技能；配置不等于实际首发、轮次或技能伤害。':'不同等级和本关的招式资料还未全部核对，不能据此确定实际发动时刻、次数或伤害。',
            '本关卡采用独立构造，不使用数据库等级定义；资源标识与关卡别名分开。':'本关使用专属敌人资料，不能直接套用普通图鉴等级。',
            '当前引用等级没有独立定义；低等级资料不能当作已确认的有效继承。':'没有当前敌人等级的独立资料，不能直接使用较低等级的数值。',
            '固定数据库缺少精确等级；默认/别名构建路径未核验，未借用较低等级技力配置。':'缺少该敌人等级的完整资料，技力数值保持未知，不借用较低等级数据。',
            '未见非空技力覆盖，构造空指针分配基线尚未闭合；完整技力配置保持未知，不借用数据库。':'本关专属技力资料不完整，完整技力数值保持未知，不借用普通图鉴数据。',
            '技力配置分项已按基包非空整记录规则解析；实际控制器、首次发动与完整回转仍未知。':'已有可参考的技力资料；实际首次发动和完整回转仍未知。',
            '默认或显式初始化来源已核验到基包条件分支；当前热更新和实际控制器仍未知。':'已核对资料中的初始设置；当前游戏中是否生效仍未知。',
            '未合并资料：':'资料中记载：',
            '条招式配置':'项招式资料','组技力配置':'项技力资料',
            '部分技能字段为空，不证明没有默认/隐藏技能。':'缺少部分招式资料，不代表敌人没有其他招式。',
            '未取得非空技能/技力配置；这不证明没有默认或隐藏技能。':'没有取得完整招式和技力资料，不能断定它没有其他能力。',
            '部分参数格式未确认，保留原文并等待核验。':'部分机制资料尚未核对，详细记录留在技术资料中。',
            '项未核验参数；原文可在技术资料中查看。':'项机制资料尚未确认；详细记录见技术资料。',
            '下列“是/否”仅来自明确字段；未定义项保持未知。':'只有明确记载的免疫状态才显示“是/否”；没有记录的保持未知。',
            '基包招式与机制参数：精确等级不可用；未借用旧等级或默认/别名构建结果。':'当前敌人等级的招式资料不完整；不套用其他等级或同名敌人的数据。',
            '基包招式与机制参数：存在未覆盖的来源格式，完整配置参考保持未知。':'部分招式资料暂时无法读取，完整效果保持未知。',
            '关卡独立构造的原招式覆写已保留；构造器未写空指针的分配基线仍未闭合，完整配置未知，未继承数据库条目。':'已保留本关专属招式资料；缺失部分不能用普通图鉴数据补齐，完整效果保持未知。',
            '此处解析的是固定配置；未推定合并为当前实战技能，当前热更新、控制器、实际发动与完整回转仍未知。':'这些是固定版本的招式资料；当前游戏实际采用哪些、发动时间和完整回转仍未知。',
            '招式构造基线仍未知；不借用数据库费用或宣称可施放。实际控制器和当前池未知。':'招式资料仍不完整；不能套用普通图鉴费用或断定可以发动，当前实际技力仍未知。',
            '技能技力数值门：来源或独立构造基线未闭合，不能借用数据库/默认共享池。':'敌人技力资料不完整，不能借用其他资料来判断招式能否发动。',
            '基础初始化点共享技力':'固定条件下的初始共享技力','基础初始化点技力':'固定条件下的初始技力',
            '这里只检视独立技力数值门；实际附着、其他可用门和首次发动时刻仍未知。':'以下只判断技力是否足够；其他发动条件和首次发动时刻仍未知。',
            '【固定预制体技能条件】':'【招式额外使用条件】',
            '这些是同身份基包组件分项；实际附着、完整可施放及所有发动时钟仍未知。':'以下条件来自该敌人的固定资料；是否实际生效、能否发动和发动时间仍未知。',
            '基础初始化计数0':'固定条件下从0次开始','初始化点':'初始时',
        }
        text='\n'.join(lines)
        for old,new in replacements.items():text=text.replace(old,new)
        return text
    return '\n'.join(lines)

def spawn_text(row,stage_id,technical=False):
    a=row['action'];route=row['route'];cell=route['start']
    names={entry['id']:entry['name'] for entry in battle_data()['stages'][stage_id]['enemies']}
    lines=['【出场条目】',names.get(a.get('key'),'敌人名称未确认'),('第'+str(row['wave'])+'波 · 第'+str(row['fragment'])+'片段' if row['wave'] else
        '条件分支 · 第'+str(row['phase'])+'阶段'),
        '出生位置：'+(f"格图自上第{cell['row']+1}行、第{cell['col']+1}列" if cell else '未知/未映射'),
        '绝对出场时刻：未知（调度起点、阻塞及脚本条件未核验）']
    if not technical:
        anchor='本分支阶段' if row.get('branch') else '本片段'
        lines.append('时间口径：+'+'秒数从'+anchor+'的出场计划启动时计时，启动前的等待另列；不是开战倒计时，也不是从首只敌人出现计时。')
    lines.extend(['','【出场条件】','本条目生成数量：'+value_text(a.get('count'))])
    if not technical:lines.append('数量仅在本条出场计划实际启用时适用；资料条目数不是实际敌人数。')
    if row.get('branch'):lines.append('此条目属于条件分支；触发时刻和阶段选择仍待核验。')
    if a.get('hiddenGroup'):
        lines.append('隐藏组：'+('本关卡变体符文声明启用' if row['hidden']['enabled_by_stage_rune'] else '启用条件待核验'))
    if a.get('randomSpawnGroupKey') or a.get('randomSpawnGroupPackKey'):
        if technical:lines.append('此条目属于随机候选；原始权重：'+value_text(a.get('weight'))+'（非概率）。')
        else:lines.append('随机候选：本条目不保证出现；候选不能相加为实际敌人数，也不提供生成概率。')
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
    text='\n'.join(lines)
    if not technical:
        replacements={
            '调度起点、阻塞及脚本条件未核验':'出场计划的开始时间和等待条件尚未确认',
            '本波本片段动作队列开始':'本段出场计划启动',
            '所选分支阶段动作队列开始':'本阶段出场计划启动',
            '局部生成计划':'出场时间差',
            '锚点已在片段/阶段开始前延迟之后；不重复加此前延迟，不跨片段使用同一个0秒。':'计时起点位于本段/本阶段开始前的等待之后；不要重复加此前等待，不同段也不能共用同一个0秒。',
            '名义偏移不是开局绝对时刻；帧执行、生成回调和可见入场延迟尚未校准。':'出场时间差不是开战后的实际时刻；画面上真正出现的时间仍未确认。',
            '此条目含条件或随机候选；序列仅在该条目实际启用/入选时适用。':'本条计划含额外条件或随机候选；只有本条计划实际生效时，这些时间差才适用。',
            '以下是配置参数，不直接相加为全局时间。':'下面是出场前可能发生的等待，不能直接相加当作开战倒计时。',
            '本波开始前延迟':'本波开始前等待','本波清场后的延迟':'本波清场后等待',
            '本片段开始前延迟':'本段开始前等待','分支阶段开始前延迟':'本阶段开始前等待',
            '无上限（原始配置为负一）':'无上限',
            '秒（配置；实际清场等待仍未知）':'秒（资料设定；实际清场等待仍未知）',
            '本条目首次生成前延迟':'本条计划首次出场前等待',
            '同条目相邻生成间隔':'本条计划相邻两次出场间隔',
            '以下是路线配置参考，不推算移动到达时刻。':'下面是资料中记载的途经位置和等待；不估算实际到达时刻。',
            '等待当前片段计时至指定时点':'等待本段计时到指定时刻',
            '（配置）':'（资料设定）',
            '条目生成数量缺失/无效，不推定为1。':'出场数量未确认，不能当作1。',
            '条目延迟/间隔缺失或无效，不推定为0。':'出场等待或间隔未确认，不能当作0。',
            '生成偏移超出有限数值范围。':'出场时间差超出可显示范围。',
            '本条目生成数量为0，无计划生成项。':'本条计划出场数量为0，没有安排出场。',
            '条件分支缺少基础/额外路线选择信息，不能借用其他路线定位。':'本额外计划尚未确认使用哪条路径，不能借用其他路径标出出生位置。',
            '路线存在地图外端点；不裁剪为地图内出生格。':'路径起点或终点不在地图格内；位置保留未知，不挪到地图边缘。',
            '存在出生偏移/随机范围，图上标记仅为名义格。':'出生位置有偏移或随机范围，图上点仅作位置参考。',
            '包含消失/再出现检查点；不连接为连续寻路轨迹。':'路径有消失或重新出现，不把两端连成连续行走路线。',
            '路线移动类型未定义，不能将序列化占位坐标当出生格。':'移动方式尚未确认，不能使用占位坐标标出生位置。',
        }
        for old,new in replacements.items():text=text.replace(old,new)
    return text
