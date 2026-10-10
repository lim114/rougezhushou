"""Capability-based report: an absent mechanism has no section or placeholder.

These presentation metrics consume the public numeric estimate. DP rules are
explicit per skill: a blackboard 'cost' is not necessarily generated DP.
"""
import math
import re
from .catalog import catalog
from .operator_engine import selected_talents


def metric(key,label,value,unit=''):
    return {'key':key,'label':label,'value':value,'unit':unit}


def section(key,title,metrics=(),notes=()):
    return {'id':key,'title':title,'metrics':list(metrics),'notes':list(notes)}


def relic_protection_section(protection,unit=None):
    if not protection:return None
    rows=[];notes=[]
    for p in protection:
        if p['kind']=='barrier_on_deploy_ratio':
            rows.append(metric('barrier_'+p['relic_id'],p['name']+' · 单次部署屏障参考',p['value'],'伤害吸收量'))
        elif p['kind']=='evasion_chance':
            label={'physical':'物理闪避','magic':'法术闪避'}[p['damage_type']]
            rows.append(metric('evasion_'+p['relic_id']+'_'+p['damage_type'],p['name']+' · '+label,p['value']*100,'%'))
        elif p['kind']=='shield_layers':
            rows.append(metric('shield_'+p['relic_id'],p['name']+' · 部署初始护盾',p['value'],'层'))
    if any(p['kind']=='barrier_on_deploy_ratio' for p in protection):
        notes.extend(['按当前常态最大生命推导单个来源的部署屏障容量；未自动读取部署瞬间生命快照。',
            '不同屏障来源分别展示，不推定叠加、覆盖率或实际承伤总量；屏障不计入治疗HPS。'])
    if any(p['kind']=='evasion_chance' for p in protection):
        notes.append('逐来源、逐伤害类型展示闪避概率；未合成为技能/天赋/藏品综合闪避，也不将概率折算为实际减伤。真实伤害不套用这三件藏品。')
    if any(p['kind']=='shield_layers' for p in protection):
        notes.append('护盾按层抵挡符合规则的伤害事件，不等于百分比生命屏障，也不能把一层当作一次完整多段攻击；此处为部署初始层数。')
    return section('relic_protection'+('_'+unit['id'] if unit else ''),
        (unit['name']+' · ' if unit else '')+'藏品防护',rows,notes)


def river_reference_sections(reference):
    """Render held-relic facts without scheduling extra combat damage."""
    branches=reference['branches'];blocks=[]
    for key in ('dark','fire','sanity','water'):
        branch=branches[key];name=branch['name']
        rows=[metric('burst_factor',name+'瞬时爆发倍率',branch['burst_damage_scale'],'倍')]
        notes={
            'dark':['该次凋亡爆发结束后，额外减攻结束。',
                    '其他相同减攻效果同时存在时，不能默认将倍率重复相乘。'],
            'fire':['该次灼燃爆发结束后，额外法抗减算结束。',
                    '与其他减法抗效果的组合需分别核对，不能默认全部累加。'],
            'sanity':['该次神经爆发结束后，本次追加持续伤害结束。',
                      '不默认重复叠加额外持续伤害。'],
            'water':['十次伤害结束后防御减算继续；侵蚀爆发结束不会移除它。',
                     '每次已确认产生的效果分别计算减防，未知次数不默认叠加。']}[key]
        if key=='dark':
            rows.append(metric('enemy_attack_factor','爆发期目标攻击最终倍率',
                               branch['modifiers']['enemy_atk_final_scaler'],'倍'))
        elif key=='fire':
            rows.append(metric('enemy_mr_addition','爆发期目标额外法抗变化',
                               branch['modifiers']['enemy_mr_addition']))
        else:
            dtype='元素' if key=='sanity' else '物理'
            rows.extend([metric('pulse_raw','单跳原始'+dtype+'伤害',branch['raw_pulse_damage']),
                         metric('period','追加伤害间隔参考',branch['period_seconds'],'秒')])
            if key=='sanity':
                rows.append(metric('first_wait','创建后首个完整等待间隔',branch['period_seconds'],'秒'))
                notes.append('每一次追加触发都需目标仍有神经爆发麻痹；状态未确认时保留未知，不按爆发次数默认生成追加伤害。')
            else:
                rows.extend([metric('maximum_pulses','每次效果最大追加伤害次数',branch['maximum_trigger_count'],'次'),
                             metric('enemy_def_addition','每次持续效果额外防御变化',branch['modifiers']['enemy_def_addition'])])
                notes.append('首跳不等待完整间隔，在下一次可执行的目标更新触发；是否在爆发当帧触发尚未确认。第十跳包含在十次伤害内。')
                notes.append('每次目标更新最多执行一次，不追赶补跳；0.03秒是原始间隔参数，不保证实际每0.03秒造成伤害。')
            notes.append('这里展示目标减伤和伤害修饰前的原始量，未排程追加伤害，也未将其加入当前总伤或每秒伤害。')
        blocks.append(section('river_'+key,'河谷祭祈 · '+name+'机制资料',rows,notes))
    blocks.append(section('river_limits','河谷祭祈 · 已知边界与待确认',notes=[
        '以上是已核对的四元素效果资料，不能作为常驻干员属性加成。',
        '爆发产生、伤害触发和爆发结束的先后，以及每跳目标是否满足条件，无法由培养或藏品页面确定。实际追加跳数与完整总伤仍未知。',
        '没有默认目标处于麻痹，也不默认追加伤害在爆发当帧开始。',
        '未发现河谷能独立加快元素爆发冷却的依据，本应用不另加冷却加速。',
        '客户端热更新版本是否改变这些效果尚未核验。所有输出只作局外参考，不采集实战站位或要求补填战斗事件。',
        '来源：'+reference['source']['topic_url']]))
    return blocks


def has_damage(op,number):
    if op=='kaltsit':return number==2
    if op=='silverash':return number!=1
    if op in ('char_151_myrtle','char_298_susuro','char_196_sunbr'):return False
    if op=='char_2025_shu':return number==3
    if op=='char_4202_haruka':return number in (2,3)
    return True


def has_healing(op,number):
    return op in ('kaltsit','char_196_sunbr','char_2025_shu','char_298_susuro','char_1037_amiya3','char_4202_haruka') or (op=='char_151_myrtle' and number==2) or (op=='char_1044_hsgma2' and number==2)


def fee_section(scenario,bb,skill):
    op=scenario['operator'];number=scenario['skill']
    immediate=gradual=0;unplaced_shadow=False
    if op=='char_151_myrtle':gradual=bb['value']
    elif op=='char_4228_closur':
        if number==1:
            casts=scenario.get('closure_prior_casts',0)
            if isinstance(casts,bool) or not isinstance(casts,(int,float)) or not math.isfinite(casts) or int(casts)!=casts or not 0<=casts<=1000:
                raise ValueError('已使用技能次数需要为0–1000的有限整数。')
            gradual=min(bb['cost_add_max'],bb['cost']+casts*bb['cost_per_add'])
        elif number==2:immediate=bb['cost'];gradual=bb['cost_period']
        else:gradual=bb['cost_period']
    elif op=='char_4087_ines':
        counts=skill['hit_counts']
        if number==1:immediate=bb['cost']*counts.get('淬影突袭物理攻击',0)
        elif number==2:gradual=bb['cost']*counts.get('暗夜无明递增攻速攻击',0)
        else:
            shadow_count=counts.get('收回影哨',0)
            unplaced_shadow=shadow_count is None
            immediate=0 if unplaced_shadow else bb['cost']*shadow_count
            gradual=bb['cost']*counts.get('技能攻击',0)
    elif op=='silverash' and number==1:immediate=bb['cost']
    elif op=='silverash' and number==3:
        immediate=bb['svash2_s_3[start_cost].cost']
        gradual=24*bb['svash2_s_3[cost].cost']
    else:
        if not any(r['kind']=='skill_start_dp' for r in scenario.get('_relic_rules',[])):return None
    immediate+=sum(r['value'] for r in scenario.get('_relic_rules',[]) if r['kind']=='skill_start_dp')
    known_total=immediate+gradual;total=None if unplaced_shadow else known_total
    duration=skill['duration_seconds'];cycle=skill['cycle_seconds']
    rows=[metric('per_cast','单次技能回费',total,'费')]
    if unplaced_shadow:
        rows += [metric('known_subtotal','已排程本体/开启回费参考小计',known_total,'费'),
                 metric('shadow_per_hit','影哨每个路径伤害事件回费参数',bb['cost'],'费')]
    if immediate:rows.append(metric('immediate','下次攻击回费条件参考' if op=='char_4087_ines' and number==1 else '开启时立即回费',immediate,'费'))
    if gradual:rows.append(metric('gradual','持续回费合计',gradual,'费'))
    if duration:rows.append(metric('active_rate','技能内平均回费',total/duration if total is not None else None,'费/秒'))
    if cycle:
        rows.append(metric('cycle_rate','本轮周期平均回费',total/cycle if total is not None else None,'费/秒'))
    elif skill.get('mode')!='deployment':
        rows.append(metric('cycle_rate','本轮周期平均回费',None,'费/秒'))
    notes=['主动技能产生的费用，未包含系统自然回费；不等于扣除部署费用后的净收益。','费用总量以完整技能为准，短观察窗口不替代它。']
    if op=='char_4228_closur' and number==1:
        notes.append('本次回费按部署后此前的技能次数情景计算（尚未自动读取），达到上限后不再成长。')
        rows.append(metric('mature_per_cast','成长完成后单次回费',bb['cost_add_max'],'费'))
        rows.append(metric('mature_cycle_rate','成长完成后周期平均',bb['cost_add_max']/cycle if cycle else None,'费/秒'))
    if op=='char_4087_ines':
        notes.append('按当前单目标持续供靶的有效攻击/伤害事件估算；持续法术跳数不当作额外回费。其他敌人的影哨路径命中未默认加入。')
        if unplaced_shadow:notes.append('影哨路径碰撞尚未定位；每个伤害事件回费只列参数，未确认开启时回费或完整技能回费。')
        if number==3 and scenario.get('ines_first_deployment'):
            notes.append('首次部署只放影哨后离场，此次没有伤害回费；免部署费是费用免除，不是产生费用。')
    return section('dp','费用收益',rows,notes)


def readable_description(description,values):
    def substitute(match):
        key,style=match.group(1),match.group(2)
        if key not in values:return '未确认'
        value=values[key]
        return f'{value*100:g}%' if style and '%' in style else f'{value:g}'
    text=re.sub(r'\{([^}:]+)(?::([^}]+))?\}',substitute,description or '')
    return re.sub(r'<[^>]+>','',text).replace('\\n','\n').strip()


def mechanism_sections(scenario,result,source,profile):
    op=scenario['operator'];number=scenario['skill'];bb=source['values']
    stats=result['estimate']['base_stats'];components=result.get('components',[])
    blocks=[]
    text=readable_description(source['description'],bb)
    clauses=[c.strip() for c in re.split('[；\n]',text) if c.strip()]
    protection=[c for c in clauses if any(word in c for word in ('屏障','护盾','闪避','庇护','减伤','伤害减免','伤害抗性','防御力','生命上限'))]
    if protection:
        rows=[]
        if op=='mechanist' and number==2:
            rows=[metric('body_barrier','本体每层屏障耐久',stats['hp']*bb['hp_ratio'],'伤害吸收量'),
                metric('barrier_ratio','屏障相对各自生命上限',bb['hp_ratio']*100,'%')]
        elif op=='silverash' and number==1:
            rows=[metric('recipient_barrier','指定干员部署后屏障',stats['hp']*bb['svash2_s_1[deck].shield'],'伤害吸收量')]
        elif op=='char_4228_closur' and number==1:
            rows=[metric('shield_layers','援军护盾层数',bb['shield_cnt'],'层')]
        shields=any(word in text for word in ('屏障','护盾'))
        title='屏障与防护' if shields else '生存与防护'
        note='护盾/屏障是防护，不计入直接治疗；未推定实战吸收总量或有效覆盖率。' if shields else '防护效果来自当前技能资料，未推定实战承伤与有效覆盖率。'
        blocks.append(section('protection',title,rows,protection+[note]))
    controls=[c for c in clauses if any(word in c for word in ('眩晕','晕眩','停顿','迟钝','束缚','寒冷','冻结','战栗','浮空','失重','隐匿','脆弱','虚弱','沉默'))]
    if controls:blocks.append(section('control','控制与状态',notes=controls+['这里是当前等级技能资料，实际控制时长/覆盖率取决于免疫、命中和时序，尚未统一模拟。']))
    talents,_=selected_talents(profile,scenario)
    descriptions=[readable_description(t.get('description'),t['values']) for t in talents if t.get('description')]
    summon_words=('触手','援军','结构性原理','魂灵之影','浮游单元','协同丹增')
    summoned=[c for c in components if any(word in c['name'] for word in summon_words)]
    source_summons=[c for c in clauses+descriptions if any(word in c for word in summon_words)]
    if summoned or source_summons or op in ('char_328_cammou','char_1038_whitw2') or (op=='silverash' and number==3 and scenario.get('cooperative')):
        rows=[metric('summon_damage','当前情景召唤/协同分项伤害',None if any(
            'actual_total' in c and c['actual_total'] is None for c in summoned) else sum(c['total'] for c in summoned))] if summoned else []
        if op=='char_110_deepcl':
            from .summons import token_concurrent_limit
            rows[0:0]=[metric('summon_count','参与测算触手数（局外假设）',scenario.get('summon_count',1),'个'),
                metric('concurrent_limit','触手同时在场上限',token_concurrent_limit(profile,scenario,'token_10001_deepcl_tentac'),'个')]
        blocks.append(section('summons','召唤与协同',rows,source_summons+['召唤/协同伤害如已计入总伤，不再重复相加；没有独立模型或已确认触发的数据不会补成确定输出。']))
    regeneration=[c for c in components if c.get('damage_type')=='regeneration' and c.get('per_hit',0)>0]
    if regeneration or (op=='char_110_deepcl' and number==1):
        if op=='char_110_deepcl':
            factor=result.get('relic_regeneration_multiplier',1)
            rows=[metric('per_token_rate','每只触手生命回复速度',bb['hp_recovery_per_sec']*factor,'生命/秒'),
                metric('all_tokens_rate','所选触手合计回复速度',bb['hp_recovery_per_sec']*factor*scenario.get('summon_count',1),'生命/秒')]
        elif any('nominal_duration_reference_seconds' in c for c in regeneration):
            rows=[metric('nominal_regeneration','名义持续参数下生命回复条件参考',sum(c['total'] for c in regeneration),'生命'),
                metric('window_regeneration','实际情景生命回复总量',
                    None if any(c.get('actual_total',0) is None for c in regeneration) else sum(c['total'] for c in regeneration),'生命')]
        else:rows=[metric('window_regeneration','当前情景生命回复总量',sum(c['total'] for c in regeneration),'生命')]
        notes=['生命回复独立于直接治疗 HPS，不扣当前生命已满导致的无效回复。']
        if op=='char_110_deepcl' and number==1:
            notes.append('以上为所选触手持续在场且技能回复持续覆盖时的速度参考，包含本次采用的生命回复效果倍率；实际在场、回复首跳和结束尚未核验，实际回复总量未知。')
        blocks.append(section('regeneration','生命回复',rows,notes))
    elementary=[c for c in components if c.get('damage_type') in ('elemental','buildup')]
    if elementary:
        buildup=op=='char_1042_phatm2' or (op=='char_4204_mantra' and number in (1,2))
        rows=[];notes=[]
        if buildup:
            binding_unknown=any(result.get(key,{}).get('affected_damage_phases',{}).get('window',False)
                for key in ('neural_s1_reference','neural_incoming_reference'))
            rows=[metric('potential_buildup','潜在损伤积累',None if binding_unknown else sum(c['total'] for c in elementary if c['damage_type']=='buildup'),'损伤值'),
                metric('bursts','当前情景损伤爆发次数',None if
                    any(result.get(key,{}).get('affected_damage_phases',{}).get('window') for key in
                        ('neural_incoming_reference','neural_s1_reference','neural_skill_reference','neural_bait_reference')) else
                    sum(c['hits'] for c in elementary if c['name']=='神经损伤爆发'),'次')]
            notes.append('潜在积累未扣除爆发冷却暂停；不是敌人生命伤害。')
        partial=bool(result.get('known_damage_subtotals'))
        rows.append(metric('elemental_damage','已建模元素伤害小计' if partial else '当前情景元素伤害',
            sum(c['total'] for c in elementary if c['damage_type']=='elemental')))
        partial_note=('目标普通攻击次数没有事件时刻，未生成堕梦损伤事件或实际爆发序列；法伤小计独立保留。'
                      if result.get('neural_incoming_reference') else
                      '束缚倍率首次生效与刷新尚未核验；法伤小计不含未知的神经爆发，损伤基础参考没有套用束缚倍率。'
                      if result.get('neural_s1_reference') else
                      '已计小计不含未排程的持续损伤及受其影响而未知的神经爆发；当前积累仅列直接来源。'
                      if result.get('neural_skill_reference') else
                      '诱饵持续效果与受其影响的神经爆发未排程；当前积累与元素小计仅列已排程的本体来源。'
                      if result.get('neural_bait_reference') else
                      '元素伤害已在已建模伤害小计中计入；不含未排程的河谷持续伤害。')
        blocks.append(section('elemental','元素机制',rows,notes+[
            partial_note if partial else
            '元素伤害已在总伤中计入，不再相加。']))
    ammo=bb.get('attack@trigger_time',bb.get('trigger_time'))
    if source['duration_type']=='AMMO' and ammo is not None:
        blocks.append(section('ammo','弹药机制',[metric('ammo','完整技能弹药/触发数',ammo,'次')],
            ['这是触发资源数量，不自动等于命中次数；破屏、布子或多连击的实际消耗规则以当前技能资料为准。']))
    if descriptions:blocks.append(section('talents','当前已解锁天赋资料',notes=descriptions+['仅列当前身份/培养/模组适用的资料；已量化范围与未覆盖项见估算状态。']))
    blocks.append(section('mechanics','技能机制（当前等级资料）',notes=[text]))
    return blocks


def current_output_breakdown_sections(result):
    """Show existing observation fields without rebuilding totals or clocks."""
    components=result.get('components')
    legacy='components' not in result
    if legacy:
        components=[]
        if 'hits' in result and 'per_hit' in result and 'total_damage' in result:
            components.append({'name':'既有技能伤害字段',
                'damage_type':result.get('damage_type','damage_reference'),
                'hits':result['hits'],'per_hit':result['per_hit'],'total':result['total_damage']})
        if 'hits' in result and 'per_heal' in result and 'total_healing' in result:
            components.append({'name':'既有技能治疗字段','damage_type':'healing',
                'hits':result['hits'],'per_hit':result['per_heal'],'total':result['total_healing']})
    if not components:return []
    categories={'damage':('伤害','伤害'), 'healing':('潜在治疗','治疗'),
        'regeneration':('独立生命回复','生命'), 'buildup':('潜在损伤积累','损伤积累'),
        'other':('其他输出字段','')}
    labels={'physical':'物理伤害','magic':'法术伤害','true':'真实伤害',
        'elemental':'元素伤害','weakness':'择优伤害（物理/法术）',
        'damage_reference':'伤害（原结果未单列类型）',
        'healing':'潜在治疗','regeneration':'独立生命回复','buildup':'潜在损伤积累'}
    grouped={key:[] for key in categories}
    group_notes={key:[] for key in categories}
    for index,component in enumerate(components):
        dtype=component.get('damage_type')
        group=(dtype if dtype in ('healing','regeneration','buildup') else
               'damage' if dtype in ('physical','magic','true','elemental','weakness','damage_reference') else 'other')
        rows=grouped[group];notes=group_notes[group];unit=categories[group][1]
        name=component.get('name') or '未命名分项'
        prefix='component_'+str(index)+'_'
        rows.append(metric(prefix+'type',name+' · 类型',labels.get(dtype,dtype if dtype is not None else None)))
        count_label='期望次数/份额' if '期望' in name else '模型次数/份额'
        rows.append(metric(prefix+'count',name+' · '+count_label,component.get('hits')))
        amounts=component.get('event_amounts')
        complete_amounts=(isinstance(amounts,list) and bool(amounts) and all(
            isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
            for value in amounts))
        variable_amounts=complete_amounts and min(amounts)!=max(amounts)
        per_label='单次量字段（事件量可变）' if variable_amounts else '单次量字段'
        rows.append(metric(prefix+'per_hit',name+' · '+per_label,component.get('per_hit'),unit))
        if variable_amounts:
            rows.extend([metric(prefix+'event_mean',name+' · 已给逐事件量均值',sum(amounts)/len(amounts),unit),
                metric(prefix+'event_min',name+' · 已给逐事件量下限',min(amounts),unit),
                metric(prefix+'event_max',name+' · 已给逐事件量上限',max(amounts),unit)])
            notes.append(name+'：均值和范围仅取自已有逐事件量；单次量字段照原值保留，不代表每次相同。')
        elif isinstance(amounts,list) and any(value is None or not isinstance(value,(int,float))
                or isinstance(value,bool) or not math.isfinite(value) for value in amounts):
            notes.append(name+'：逐事件量含未知或不可用值，未生成均值和范围。')
        pending='actual_total' in component and component['actual_total'] is None
        rows.append(metric(prefix+'total',name+' · '+('条件总量参考' if pending else '分项模型总量'),
            component.get('total'),unit))
        if 'actual_total' in component:
            rows.append(metric(prefix+'actual_total',name+' · 实际总量字段',component['actual_total'],unit))
            if pending:notes.append(name+'：实际总量未知，条件总量不能补成已确认输出。')
    blocks=[]
    for key,(title,unit) in categories.items():
        rows=grouped[key]
        if not rows:continue
        notes=['这里列当前情景返回的分项；有观察窗口时是该窗口字段，不是完整施放或本轮周期。',
            '模型次数可表示命中、持续量或期望份额，不证明实际攻击次数；总量照原字段，不用单次量乘次数重算。',
            '召唤、回复及元素专项表可能已汇总这些来源；本表只展开，不再相加。']
        if legacy:notes.append('原结果未提供分项列表；这里只列已有技能字段，不生成事件、额外目标次数或类型。')
        if key=='damage' and result.get('total_damage') is None:
            notes.append('整体伤害仍未知；以下已有分项字段和条件参考不构成完整伤害总量。')
        if key=='healing':
            notes.append('潜在治疗不等于有效受疗；不反推受疗人数，也不包含独立生命回复。')
            if result.get('total_healing') is None:notes.append('整体治疗仍未知；以下已有分项字段和条件参考不构成完整治疗总量。')
        if key=='regeneration':notes.append('独立生命回复不并入伤害或直接治疗；是否实际生效继续按原情景和来源限制。')
        if key=='buildup':notes.append('损伤积累不是敌人生命伤害，也不自动等于爆发次数或爆发伤害。')
        blocks.append(section('output_breakdown_'+key,'当前情景输出分项 · '+title,rows,notes+group_notes[key]))
    return blocks


def chen_motion_reference_sections(scenario):
    """Expose original motion facts, keeping them outside numeric scheduling."""
    from .chen_motion_reference import chen_motion_reference
    reference=chen_motion_reference(scenario)
    if reference is None:return []
    blocks=[]
    for face in ('Front','Back'):
        motions=[r for r in reference['motions'] if r['orientation']==face]
        if not motions:continue
        rows=[];notes=[
            '这些是原版资源中的独立动作条目；排列便于查看，不代表实际执行顺序、循环次数或当前皮肤动作选择。',
            '每个事件的偏移以该动作资源自身起点为0；不是技能开启后的实际命中或碰撞时刻。',
            '原始秒数和浮点帧保留原值；30帧/秒归一化仅处理资源表示误差，不证明游戏帧取整或客户端相位。',
            '参考只改变资料展示，不排程多事件伤害，不替换攻击模板，也不将动作长度相加作为技能持续时间。']
        for index,motion in enumerate(motions):
            prefix='motion_'+str(index);duration=motion['duration'];label=motion['label']
            rows.extend([
                metric(prefix+'_duration',label+' · 资源时长',repr(duration['seconds']),'秒（原值）'),
                metric(prefix+'_raw_frames',label+' · 原始浮点帧',repr(duration['raw_frames_30hz']),'帧'),
                metric(prefix+'_strict_ceil',label+' · 严格向上取整帧',duration['strict_ceil_frames_30hz'],'帧'),
                metric(prefix+'_normalized',label+' · 归一化参考帧',duration['ceil_frames_30hz'],'帧'),
                metric(prefix+'_events',label+' · 命名事件数量',len(motion['events']),'个')])
            for event_index,event in enumerate(motion['events']):
                event_prefix=prefix+'_event_'+str(event_index)
                event_label=label+' · 第'+str(event_index+1)+'个命名事件'
                rows.extend([
                    metric(event_prefix+'_seconds',event_label+' · 原始偏移',repr(event['seconds']),'秒（动作内）'),
                    metric(event_prefix+'_raw_frames',event_label+' · 原始浮点帧',repr(event['raw_frames_30hz']),'帧'),
                    metric(event_prefix+'_strict_ceil',event_label+' · 严格向上取整帧',event['strict_ceil_frames_30hz'],'帧'),
                    metric(event_prefix+'_normalized',event_label+' · 归一化参考偏移',event['ceil_frames_30hz'],'帧')])
                notes.append(event_label+'名称：'+event['name']+'；原名不等于已核验的实际伤害绑定。')
            notes.append(label+'资源动作原名：'+motion['animation']+'；来源：'+motion['source']['url']+
                         '；资源SHA-256：'+motion['source']['sha256'])
        rows.extend([metric('actual_damage','实际命中时刻',None,'秒'),
                     metric('actual_end','实际技能结束时刻',None,'秒')])
        if reference['skill']==2:
            rows.extend([metric('slash_end','实际斩击结束时刻',None,'秒'),
                         metric('strengthening_start','实际强化起点',None,'秒')])
            notes.append('普攻动作仅列资源参照，未证明它用于斩击后强化；消失动作长度不等于斩击持续时间。')
        elif reference['skill']==3:
            rows.append(metric('wave_collision','实际剑气碰撞时刻',None,'秒'))
            notes.append('循环动作的三个命名事件不补齐剑气碰撞、开启交接、实际循环次数或结束时刻。')
        else:
            notes.append('循环动作的两个命名事件仅列原始偏移，未绑定实际两段伤害或开启、结束交接。')
        blocks.append(section('chen_motion_'+face.lower(),'陈 · 原版阶段资料 · '+
                              {'Front':'正面','Back':'背面'}[face],rows,notes))
    return blocks


def reproducible_context_sections(scenario,result):
    """Display declared conditions and already resolved targets, without validation."""
    skill=result['estimate']['skill'];timing=scenario.get('timing',{})
    timing=timing if isinstance(timing,dict) else {}
    def scalar(value):
        return value if type(value) in (int,float,str) else None
    rows=[metric('timing_mode','计算时序口径',
        '30帧/秒事件参考' if result.get('timing',{}).get('mode')=='frames' else '连续供靶参数参考'),
        metric('window','本次采用的观察窗口',skill.get('window_seconds'),'秒')]
    if 'window_seconds' in scenario:
        raw=scalar(scenario['window_seconds'])
        rows.append(metric('declared_window','声明的观察窗口',str(raw)+' 秒' if raw is not None else None))
    enemy=result.get('run_resolution',{}).get('enemy')
    if isinstance(enemy,dict):
        stats=enemy.get('stats',{})
        rows.extend([metric('target_source','目标属性来源','所选关卡敌人资料及已接入修正'),
            metric('enemy_defense','目标防御参考',stats.get('def')),
            metric('enemy_resistance','目标法抗参考',stats.get('magicResistance'))])
    else:
        rows.extend([metric('target_source','目标属性来源','手动情景输入参考'),
            metric('enemy_defense','当前情景防御参考',scalar(scenario.get('enemy_defense',0))),
            metric('enemy_resistance','当前情景法抗参考',scalar(scenario.get('enemy_resistance',0)))])
    notes=['这里复述当前报告情景或已返回的目标资料；不改变输入、输出或时序，也不证明当前游戏面板。',
        '手动情景字段可能已经过既有预处理；本表不额外声称保留了修正前原输入或完整实际消费记录。' ,
        '目标生命参考不用于截断攻击；这些条件不提供实际击杀时间。']
    if scenario.get('timing_mode','frames')=='continuous':
        notes.append('连续模式保持既有参数参考；正供靶、移动和打断区间不在此转换为帧事件，也不据此推算空转。')
    def shown(value):
        if type(value) is int or type(value) is float and math.isfinite(value):
            try:return str(value)
            except (ValueError,OverflowError):return '未确认'
        if type(value) is str:return value
        return '未确认'
    def condition_lines(options,prefix):
        found=[]
        for key,label in (('target_windows','敌方可获取区间'),
                          ('movement_windows','移动区间'),('interrupt_windows','打断区间'),
                          ('initial_target_windows','初动敌方可获取区间'),
                          ('initial_movement_windows','初动移动区间'),
                          ('initial_interrupt_windows','初动打断区间')):
            if key not in options:continue
            value=options[key]
            if isinstance(value,list):
                if not value:text='明确为空'
                elif all(isinstance(pair,(list,tuple)) and len(pair)==2 for pair in value):
                    text='；'.join('['+shown(pair[0])+', '+shown(pair[1])+') 秒' for pair in value)
                else:text='未确认'
            else:text='未确认'
            found.append(prefix+label+'：'+text+'。')
        for key,label,unit in (('target_disappears_seconds','当前目标生命周期终点','秒'),
                ('projectile_travel_seconds','手动弹道延迟','秒'),
                ('windup_frames','前摇预览','帧'),('recovery_frames','后摇预览','帧'),
                ('start_delay_frames','起始延迟预览','帧'),
                ('post_skill_lock_frames','技能结束硬直预览','帧'),
                ('sp_lockout_extra_seconds','额外阻回预览','秒')):
            if key in options:found.append(prefix+label+'：'+shown(options[key])+' '+unit+'。')
        return found
    notes.extend(condition_lines(timing,'本体声明 · '))
    active_units={stream.get('unit') for key in ('streams','recharge_streams')
                  for stream in result.get('timing',{}).get(key,[]) if isinstance(stream,dict)}
    units=timing.get('units',{})
    if isinstance(units,dict):
        tokens=catalog()['operators'][scenario['operator']].get('tokens',{})
        for identity,options in units.items():
            if identity not in active_units or not isinstance(options,dict):continue
            name=tokens.get(identity,{}).get('name') or '独立单位'
            notes.extend(condition_lines(options,name+'声明 · '))
    if not any(key in timing for key in ('target_windows','target_disappears_seconds')):
        notes.append('未声明敌方供靶或消失限制；沿用当前计算原有的连续供靶参考，不表示已观察到该条件。')
    notes.append('敌方供靶不等于友方受疗资格；独立单位采用自己的已声明情景，未声明的获取/命中脚本继续未知。')
    return [section('calculation_context','本次计算条件',rows,notes)]


def event_clock_reference_sections(scenario,result):
    """Keep each stored stream and its fields separate; no clock reconstruction."""
    timing=result.get('timing',{})
    if timing.get('mode')!='frames':return []
    profile=catalog()['operators'][scenario['operator']]
    tokens=catalog()['operators'][scenario['operator']].get('tokens',{})
    blocks=[]
    def sequence(stream,key):
        value=stream.get(key)
        if not isinstance(value,list) or not all(isinstance(item,(int,float)) and
                not isinstance(item,bool) and math.isfinite(item) for item in value):return None
        return value
    for phase,key in (('当前情景','streams'),('本轮充能期','recharge_streams')):
        for index,stream in enumerate(timing.get(key,[])):
            identity=stream.get('unit')
            name=(profile['name']+'本体' if identity==scenario['operator'] else
                  tokens.get(identity,{}).get('name') or '独立单位')
            scope={'enemy':'敌方获取参考','friendly':'友方获取参考'}.get(stream.get('target_scope'),'获取来源未确认')
            rows=[metric('target_scope','获取来源',scope)]
            for field,label,unit in (
                    ('start_frames','攻击起始记录','帧'),('release_frames','出手记录','帧'),
                    ('impact_frames','窗口内命中帧记录','帧'),
                    ('times_seconds','输出时间参考记录','秒'),
                    ('emitted_impact_frames','已释放的潜在命中帧记录','帧'),
                    ('emitted_times_seconds','已释放的潜在命中时间记录','秒')):
                values=sequence(stream,field)
                rows.extend([metric(field+'_count',label+'数',len(values) if values is not None else None,'条'),
                    metric(field+'_first',label+'首项',values[0] if values else None,unit),
                    metric(field+'_last',label+'末项',values[-1] if values else None,unit)])
            notes=['各条记录照既有序列保留；同单位的多条流和同帧多事件不合并、不去重，也不换算成实际攻击次数。',
                '一条召唤物时序可供多只或零只单位的条件计算使用；记录数不证明真实在场数量或分项命中次数。',
                '已释放的潜在命中记录可晚于观察窗口；不自动加入窗口、技能阶段或本轮周期输出。',
                '输出时间与窗口内命中帧分别取自现有字段；部分完整施放路径的输出时间含尾段，不能据此改写窗口边界。',
                '缺失记录保持未知，明确空序列保留零条；首末项未知不伪造零秒事件。',
                '时刻为各自阶段的相对参考，不是游戏实测；本轮充能期不与当前情景合并成稳态时间线。']
            if timing.get('phase_clock_unbound') or timing.get('parameter_clock_only') or timing.get('resource_and_damage_shared_clock') is False:
                notes.append('当前技能阶段、获取/命中或资源时钟有未绑定部分；以下只展示已有局外/参数参考，实际时间和完整周期仍未知。')
            if stream.get('known_animation') is False:
                notes.append('前后摇资料未齐；保留原计算的延迟首击参考，不补成原生动画绑定。')
            elif stream.get('known_animation') is not True:
                notes.append('动作参数资格未确认；数值记录不证明动画资料齐全或原生绑定。')
            blocks.append(section('event_clock_'+key+'_'+str(index),phase+' · '+name+' · 时序记录 '+str(index+1),rows,notes))
    return blocks


def output_domain_comparison_sections(scenario,result):
    """Expose existing phase/domain totals; never subtract phases or add sources."""
    op=scenario['operator'];number=scenario['skill'];skill=result['estimate']['skill'];blocks=[]
    for kind,enabled,total,phase,window,cycle,average,unit in (
            ('damage',has_damage(op,number),'total_damage','phase_damage','window_damage','cycle_damage','cycle_dps','伤害'),
            ('healing',has_healing(op,number),'total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','治疗')):
        if not enabled:continue
        label='伤害' if kind=='damage' else '潜在治疗'
        window_value=skill.get(window,result.get('total_damage') if kind=='damage' else None)
        rows=[metric('window_seconds','观察窗口长度',skill.get('window_seconds'),'秒'),
            metric('window_total','观察窗口'+label,window_value,unit),
            metric('cast_total','完整本次施放'+label,skill.get(total),unit),
            metric('duration_seconds','技能阶段长度',skill.get('duration_seconds'),'秒'),
            metric('phase_total','技能阶段'+label,skill.get(phase),unit),
            metric('recharge_seconds','本轮结束后充能长度',skill.get('recharge_seconds'),'秒'),
            metric('cycle_seconds','本轮周期长度',skill.get('cycle_seconds'),'秒'),
            metric('cycle_total','本轮周期'+label,skill.get(cycle),unit),
            metric('cycle_average','本轮周期平均'+label,skill.get(average),unit+'/秒')]
        subtotal=result.get('known_'+kind+'_subtotals')
        if isinstance(subtotal,dict):
            for key,suffix in ((window,'观察窗口'),(total,'完整施放'),(phase,'技能阶段'),(cycle,'本轮周期')):
                if key in subtotal:rows.append(metric('known_'+key,suffix+'已计部分',subtotal[key],unit))
        notes=['各项直接读取既有结果，未知仍未知；本表不重新结算、相加或由差值反推充能期输出。',
            '完整施放按本次施放归属；技能阶段、观察窗口和本轮周期各有自己的截止边界。已释放尾段可使它们不同。',
            '本轮周期使用当前技能与结束后充能的既有计算；跨多轮稳态、残留和未绑定事件没有因此得到确认。',
            '已计部分只是受支持来源的小计，不能补成完整总量；独立生命回复、损伤积累和屏障仍采用各自口径。']
        if kind=='healing':notes.append('潜在治疗不扣过量治疗，不等于实际有效受疗。')
        blocks.append(section('output_domain_'+kind,label+'口径对照',rows,notes))
    return blocks


def build_report(scenario,result):
    op=scenario['operator'];number=scenario['skill'];p=catalog()['operators'][op]
    if op=='char_110_deepcl' and type(scenario.get('summon_count')) is str:
        # Combat.plan already validated this finite, nonnegative integer string.
        scenario={**scenario,'summon_count':int(float(scenario['summon_count']))}
    source=p['skills'][number-1]['levels'][scenario.get('skill_rank',10)-1]
    bb=source['values'];estimate=result['estimate'];skill=estimate['skill']
    sections=[]
    for reference in result.get('token_duration_references',[]):
        state=reference['state']
        notes=['当前培养尚未解锁结构性原理。' if state=='locked' else
               '当前持续参数为无限；这不保证持续存活，仍可能死亡或撤退。' if state=='unlimited' else
               '显示部署后持续参数，实际在场时间尚未确认。',
               '无限仅适用于【沉沦者的黑流树海】、精二60级及以上的二/三阶模组；一阶仍用基础持续参数。',
               '实际部署完成、退场和存活时长未知；本参考不改变技能伤害或回转。']
        sections.append(section('token_duration_'+reference['token_id'],reference['token_name']+' · 持续参数参考',[
            metric('duration','部署后持续参数',reference['duration_seconds'],'秒')],notes))
    mei_module=result.get('mei_airborne_module_reference')
    if mei_module:
        sections.append(section('mei_airborne_module','梅 MAR-X · 空中条件参数参考',[
            metric('unlock_elite','模组解锁精英阶段',mei_module['unlock_elite']),
            metric('unlock_level','模组解锁等级',mei_module['unlock_level']),
            metric('module_level','当前模组等级',mei_module['module_level']),
            metric('attack_scale','空中条件攻击倍率原参数',mei_module['attack_scale_parameter']*100,'%'),
            metric('target_airborne','当前目标空中条件',mei_module['actual_target_is_airborne']),
            metric('conditional_damage','该特性实际条件伤害',mei_module['actual_conditional_damage'])],
            [readable_description(mei_module['trait_description'],{'atk_scale':mei_module['attack_scale_parameter']}),
             '仅列当前已解锁新手侦探礼包的原表条件参数；本次未确认目标是否为空中单位。',
             '空中条件、真实模组附着以及与技能或其他加成的组合层尚未核验；110%参数未计入当前伤害数值。',
             '现有伤害、攻击时钟与培养数值保持；本参考不表示该条件模组机制已完整覆盖。',
             result['complete_definition']]))
    mode=skill.get('mode','ammo' if source['duration_type']=='AMMO' else 'instant' if source['duration']<=0 else 'timed')
    sections.append(section('timing','技能时序',[
        metric('initial','预计初动',skill['initial_seconds'],'秒'),
        metric('duration','持续时间',skill['duration_seconds'],'秒'),
        metric('cycle','预计回转',skill['cycle_seconds'],'秒'),
        metric('recharge','结束后充能',skill['recharge_seconds'],'秒')]))
    shu_sp=result.get('shu_periodic_sp_reference')
    if shu_sp:
        sections.append(section('shu_periodic_sp','天有四时 · 周期技力待核验',[
            metric('interval','周期间隔原参数',shu_sp['interval_seconds_parameter'],'秒'),
            metric('sp','单次周期技力原参数',shu_sp['sp_per_pulse_parameter'],'技力'),
            metric('natural_rate','已计自然技力回复速度',skill['sp_recovery_per_second'],'技力/秒'),
            metric('first_tick','实际周期首跳',shu_sp['first_tick_seconds'],'秒')],
            ['四岁编队条件由当前情景声明；原天赋培养门槛和攻击力加成保持。',
             '4秒获得1点技力是周期原参数，不能当作每秒自然回复+0.25。',
             '周期首跳、计时起点、重置和阻回期间归属尚未核验；未排周期事件，完整初动、充能与回转保持未知。',
             '初始技力已足够时保留0秒就绪；敌方供靶或空观察窗口不取消这一独立友方技力来源。']))
    received=[r for r in result.get('relic_resolution',{}).get('rules',[]) if r['kind'] in ('received_sp','event_sp') and not r.get('token_only')]
    if received:
        from .sp_events import EVENT_TYPES
        outgoing=any(r['kind']=='event_sp' for r in received)
        rows=[metric('per_event_'+r['relic_id']+'_'+r['event_type'],EVENT_TYPES[r['event_type']]+' · 单次额外技力',r['value'],'技力') for r in received]
        notes=['按明确事件表合并到初动、充能、回转及本轮周期输出；未折算成固定每秒技力。',
            '只计本体已确认的回调与次数；不从出手数、命中段数或总伤猜测归属，不为召唤物直接继承。' if outgoing else
            '受到攻击不自动等于受到伤害；元素损伤指损伤积累，不是元素生命伤害。',
            '同一时间可以是多次独立事件，事件表保留次数；缺失阶段不填零。']
        for phase,reference in estimate.get('sp_events',{}).items():
            label='初动阶段' if phase=='initial' else '本轮周期'
            if reference['status']=='not_needed':notes.append(label+'技力已足够，不要求额外事件表。')
            else:rows.append(metric(phase+'_events',label+' · 明确事件数',reference['events_supplied'],'次'))
            if reference['ignored_blocked']:
                rows.append(metric(phase+'_blocked',label+' · 阻回期间丢弃',reference['ignored_blocked'],'次'))
            if outgoing:
                for kind,credit in reference.get('credited_by_type',{}).items():
                    rows.extend([metric(phase+'_'+kind+'_credited',label+' · '+EVENT_TYPES[kind]+'已计入',credit['events'],'次'),
                        metric(phase+'_'+kind+'_sp',label+' · '+EVENT_TYPES[kind]+'有效额外技力',credit['sp'],'技力')])
            if reference['status']=='missing':notes.append(label+'事件表未确认，对应充能结果未知。')
        sections.append(section('event_sp' if outgoing else 'received_sp',
            '事件技力（局外情景）' if outgoing else '受击技力（局外情景）',rows,notes))
    nonrepeat=mode in ('infinite','passive','switch','once','once_deploy','deployment','triggered_ammo')
    if nonrepeat and skill['cycle_seconds'] is None:
        sections[0]['metrics'][2]['reason']='不适用：'+('依赖实际布子与耗弹' if mode=='triggered_ammo' else '没有原地固定重复回转')
    if mode in ('infinite','switch','passive'):
        sections[0]['metrics'][1]['reason']='无限持续 / 常驻 / 切换状态，使用观察窗口'
    elif mode=='instant' and skill['duration_seconds']==0:
        sections[0]['metrics'][1]['reason']='瞬时触发'
    timing=result.get('timing',{})
    multi=next((s.get('multi_melee_reference') for s in timing.get('streams',[])
        if s.get('multi_melee_reference')),None)
    if multi:
        if skill['initial_seconds'] is None:
            sections[0]['metrics'][0]['reason']='初始技力不足；普攻充能与首次施放的观察相位尚未确认'
        for row in sections[0]['metrics'][1:]:
            row['reason']='实际结束、阻回与普攻恢复的观察相位尚未确认'
        sections.append(section('multi_melee','暗夜回声 · 两段动作参考',[
            metric('raw_interval','动画缩放使用的原始攻击周期',multi['raw_interval_seconds'],'秒'),
            metric('animation_scale','动画时间比例',multi['animation_scale']),
            metric('relative_wait','两段相对等待',multi['relative_wait_frames'],'帧'),
            metric('relative_wait_seconds','两段相对等待时间',
                multi['relative_wait_frames']/30 if multi['relative_wait_frames'] is not None else None,'秒')],
            [('原版技能与动作的对应关系来自安装资源；这里只使用原版动作锚点作局外参考，不代表当前皮肤或客户端精确首伤帧。'
              if multi['selected_motion']=='Skill_1' else
              '当前手动选择的是普通攻击动作预览；安装资源中的一技能实际动作是Skill_1，未将此预览动作声明为技能真实绑定。'),
             '段间等待按未取整攻击周期缩放，再以30Hz取最近偶数帧且至少等待1帧；没有固定0.01秒间隔。',
             '同次施放锁定同一目标；离开供靶范围不自动换人，目标消失后不继续计算对该目标的伤害。',
             '完整结束、解除阻回与普攻恢复的实际相位尚未核验，回转和周期伤害保持未知。']))
    if timing.get('mode')=='frames':
        rows=[metric('fps','模拟逻辑频率',timing['fps'],'帧/秒')]
        primary=next((s for s in timing.get('streams',[]) if s['unit']==op),None)
        if primary:
            rows.extend([metric('interval','当前攻击间隔',primary['interval_seconds'],'秒'),
                metric('interval_frames','当前攻击间隔帧数',primary['interval_frames'],'帧'),
                metric('windup','参考前摇',primary['windup_frames'],'帧'),
                metric('recovery','参考后摇',primary['recovery_frames'],'帧'),
                metric('first_release','原版锚点首个出手' if multi else '窗口首个出手',primary['release_frames'][0]/30 if primary['release_frames'] else None,'秒'),
                metric('first_impact','原版锚点首个命中' if multi else '窗口首个命中/治疗',primary['impact_frames'][0]/30 if primary['impact_frames'] else None,'秒')])
            if 'fixed_impact_delay_seconds' in primary:
                rows.append(metric('fixed_impact_delay','本体固定落地延迟',primary['fixed_impact_delay_seconds'],'秒'))
        reference_notes=[]
        for stream in [*timing.get('streams',[]),*timing.get('recharge_streams',[])]:
            original=stream.get('original_animation_reference')
            if original:
                if stream.get('multi_melee_reference'):
                    note=('使用已核验的原版技能动作参考：' if stream['multi_melee_reference']['automatic_original_reference'] else
                          '明确选用原版动画参考：')+original['reference_label']+'；仅局外参考，当前皮肤、热更新与实际出手相位未核验。'
                else:
                    note='明确选用原版动画参考：'+original['reference_label']+'；仅局外参考，实际技能、皮肤与动作选择未绑定。'
                if original['overridden_by_preview']:note+=' 当前前/后摇被时序测试值覆盖。'
                if note not in reference_notes:reference_notes.append(note)
        sections.append(section('execution','战斗时序参考',rows,[
            '前后摇与攻击冷却有重叠，不把它们全部再加到攻击间隔上。',
            '时序资料及模板绑定未完整校准；无前摇资料时保持延迟首击参考。',
            ('技能相对窗口保留帧参考；独立技力算例不包含四岁周期来源，完整初动、结束后充能与回转未知。' if shu_sp else '初动/回转已按模拟帧处理；额外阻回与结束硬直使用明确提供的时序情景。'),*reference_notes]))
    changed=[]
    base_speed=estimate['base_stats'].get('attack_speed_reference',estimate['base_stats']['attack_speed'])
    skill_speed=skill.get('skill_attack_speed_reference',skill['skill_attack_speed'])
    for key,label,value,base,unit in (
        ('skill_attack','技能期间攻击力',skill['skill_attack'],estimate['base_stats']['attack'],''),
        ('skill_speed','技能期间攻速',skill_speed,base_speed,'游戏数值单位')):
        if value!=base:changed.append(metric(key,label,value,unit))
    if skill_speed!=skill['skill_attack_speed']:
        changed.append(metric('skill_speed_timing','技能攻击间隔使用攻速',skill['skill_attack_speed'],'游戏数值单位'))
    if changed:sections.append(section('skill_stats','技能属性变化',changed))
    windowed=mode in ('infinite','switch','passive')
    if has_damage(op,number):
        rows=[]
        if not windowed:
            rows.append(metric('per_cast','单次技能总伤',skill['total_damage']))
            if skill['duration_seconds'] and skill['total_damage'] is not None:
                rows.append(metric('active_dps','技能阶段平均 DPS',skill.get('phase_damage',skill['total_damage'])/skill['duration_seconds'],'伤害/秒'))
        window_damage=skill.get('window_damage',result['total_damage'])
        if windowed or 'window_seconds' in scenario or skill['total_damage']!=window_damage:
            rows.append(metric('window_damage','情景伤害参考（含给定冲锋次数）' if result.get('charge_reference') else '观察窗口总伤',window_damage))
            if skill.get('window_seconds') is not None:
                rows.append(metric('window_seconds','伤害观察窗口',skill['window_seconds'],'秒'))
            if skill.get('window_seconds'):
                rows.append(metric('window_dps','情景平均伤害参考' if result.get('charge_reference') else '窗口平均 DPS',
                    window_damage/skill['window_seconds'] if window_damage is not None else None,'伤害/秒'))
        if not nonrepeat:
            rows.append(metric('cycle_dps','本轮周期 DPS',skill['cycle_dps'],'伤害/秒'))
        sections.append(section('damage','伤害输出',rows))
    drone=result.get('drone_trait_reference')
    if drone:
        params=drone['parameters']
        sections.append(section('drone_trait','浮游单元 · 模组特性参数',[
            metric('initial','初始攻击倍率参数',params['init_atk_scale']*100,'%'),
            metric('increment','每层增长参数',params['delta_atk_scale']*100,'%'),
            metric('maximum','基础倍率上限参数',params['max_atk_scale']*100,'%'),
            metric('stacks','最大层数参数',params['max_stack_cnt'],'层')],
            ['仅更新已有暖机参考的直接数据参数；实际独立单元时钟、重选目标重置与当前热更新仍未核验。']))
    amiya_continuous=result.get('amiya_continuous_reference')
    if amiya_continuous:
        clock=amiya_continuous['parameter_clock_reference']
        sections.append(section('amiya_continuous','术师阿米娅S1 · 受限连续时序参考',[
            metric('per_hit','单次攻击伤害条件参考',amiya_continuous['per_hit_damage_reference']),
            metric('window_reference','连续供靶窗口伤害参数参考',clock['window_damage']),
            metric('cast_reference','连续供靶单次伤害参数参考',clock['total_damage']),
            metric('recharge_reference','旧连续供靶充能参数参考',clock['recharge_seconds'],'秒'),
            metric('natural_reference','无攻击回技力的自然充能参数参考',amiya_continuous['natural_only_recharge_seconds_reference'],'秒'),
            metric('actual_recharge','实际结束后充能',None,'秒')],
            ['间隔算例中的合成时刻不证明实际首击、供靶获取、命中或回技力；有限正约束下的伤害及实际回转未知。',
             '空范围只排除当前敌人的数学来源；自然SP参数不证明没有其它游戏目标或来源。',
             '施放后的生命周期/范围不重写原施放前初动约定；旧数值只保留条件参数，未作minlife或均匀比例裁剪。']))
    terminal=result.get('gnosis_terminal_reference')
    if terminal:
        sections.append(section('gnosis_terminal','失温症 · 终结条件参考',[
            metric('nominal_end','技能持续参数',terminal['nominal_skill_end_seconds'],'秒'),
            metric('conditional_damage','冻结终结单次伤害条件参考',terminal['conditional_terminal_damage']),
            metric('actual_end','实际结束当帧',None,'帧')],
            ['目标在名义结束前消失时不生成终结来源；同帧消失顺序未核验时完整伤害未知。',
             '实际结束相位、冻结移除顺序及离开范围的后续适用性尚未核验。']))
    haruka=result.get('haruka_healing_reference')
    if haruka:
        rows=[metric('trait_base','当前特性治疗人数参数',haruka['selected_trait_target_limit_parameter'],'名'),
            metric('skill_add','当前技能增加人数参数',haruka['skill_target_add_parameter'],'名'),
            metric('combined','人数相加条件参考',haruka['conditional_target_limit_reference'],'名'),
            metric('modeled','独立来源支持的已建模人数范围',haruka['modeled_target_limit_reference'],'名'),
            metric('declared','声明满额潜在受疗人数',haruka['declared_healing_targets'],'名'),
            metric('actual_targets','实际同时受疗人数',None,'名')]
        if haruka['additional_conditional_targets']:
            external_window=result['external_event_reference']['window_reference']
            for i,c in enumerate(external_window['conditional_components']):
                if c['name'] not in ('护佑者额外目标治疗（组合待核验）','额外目标治疗衍生伤害（组合待核验）'):continue
                rows.append(metric('additional_'+str(i),'观察窗口'+c['name']+'条件总量',c['total'],
                    '治疗（最终受疗倍率前）' if c['damage_type']=='healing' else '伤害'))
        sections.append(section('haruka_healing','遥 · 满额潜在治疗参考',rows,[
            '普通治疗沿用既有动作参考和明确的特性人数参数；实际友方获取时刻、模组附着及当前客户端尚未核验。',
            '特性人数与当前技能增加人数保留独立来源；人数相加只列条件参数，超出已建模范围的份额及其派生伤害不并入已计小计。']))
    shield=result.get('shield_break_reference')
    if shield:
        rows=[metric('count','声明本次总破屏次数',shield['hits_requested'],'次'),
            metric('per_hit','破屏单次法伤条件参考',shield['per_hit_damage_reference']),
            metric('declared','给定总次数条件伤害参考',shield['declared_count_damage_reference']),
            metric('ammo','原表弹药数量参数',shield['nominal_ammunition_parameter'],'发'),
            metric('manual_duration','手动结束时间条件参数',shield['manual_duration_parameter_seconds'],'秒'),
            metric('break_times','实际破屏/爆炸时刻',None,'秒'),
            metric('actual_end','实际结束时刻',None,'秒')]
        sections.append(section('shield_break','协防术式 · 破屏条件来源待核验',rows,[
            '总次数不证明当前窗口内的事件数量；零观察窗口和当前敌人0秒生命周期不产生实际伤害。',
            '本体与结构性原理的破屏、耗弹与再次屏障顺序未闭合；普通攻击沿用既有手动结束参数参考，未并入未定位的爆炸来源。']))
    external=result.get('external_event_reference')
    if external:
        rows=[metric('source_'+str(i),c['name']+'条件总量',c['total'],
                     '治疗' if c['damage_type']=='healing' else '伤害')
              for i,c in enumerate(external['conditional_components'])]
        rows += [metric('parameter_'+str(i),label,value,unit)
                 for i,(label,value,unit) in enumerate(external['parameter_rows'])]
        rows.append(metric('events','实际事件时刻',None,'秒'))
        sections.append(section('external_events','独立条件来源 · 事件时钟待核验',rows,external['notes']))
    unbound=result.get('unbound_cast_reference')
    if unbound:
        rows=[metric('source_'+str(i),c['name']+'条件总量',c['total'],
                     '治疗' if c['damage_type']=='healing' else '伤害')
              for i,c in enumerate(unbound['conditional_components'])]
        rows += [metric('parameter_'+str(i),label,value,unit)
                 for i,(label,value,unit) in enumerate(unbound['parameter_rows'])]
        rows.append(metric('hits','实际命中时刻',None,'秒'))
        sections.append(section('unbound_cast','多段技能 · 实际时钟待核验',rows,
            unbound['notes']+['条件总量保留当前培养和情景倍率；未排程来源不代表观察窗口、完整阶段或本轮周期输出。',
             '本体供靶或打断区间不证明独立弹道/接触范围；零窗口或当前敌人0秒生命周期不产生对它的实际输出。']))
    amiya_phase=result.get('amiya_phase_reference')
    if amiya_phase:
        isolated=amiya_phase['isolated_attack_phase_reference']
        rows=[metric('duration','原表技能持续参数',amiya_phase['nominal_skill_duration_parameter_seconds'],'秒'),
            metric('attack','后续攻击力条件参考',amiya_phase['strengthened_attack_reference']),
            metric('hits','孤立攻击阶段次数参考',isolated['conditional_hits'],'次'),
            metric('damage','孤立攻击阶段伤害参考',isolated['conditional_damage']),
            metric('start','实际后续攻击阶段起点',None,'秒'),
            metric('end','实际技能结束时刻',None,'秒')]
        notes=['孤立阶段沿用既有攻击参数和情景；原表持续参数不证明开启或斩击结束后另有该段时长。',
            '孤立攻击的相对时刻不代表技能开启后的实际命中时刻，完整输出和结束保持未知。']
        if amiya_phase['kind']=='tactical_slashes':
            rows.append(metric('slash_end','实际斩击结束时刻',None,'秒'))
            title='影霄·绝影 · 斩击与后续参考'
            notes.append('立即寻找目标不证明十次同帧命中；声明击倒只保留既有后续加攻条件参考，不推算击倒先后。')
        else:
            rows[0:0]=[metric('opening_damage','立即开启单击伤害条件参考',amiya_phase['opening_damage_reference']),
                metric('opening_healing','开启伤害派生治疗条件参考',amiya_phase['opening_healing_reference'],'治疗')]
            title='慈悲愿景 · 开启与后续参考'
            notes.append('开启来源保留原描述立刻一次的既有参数算术，单击数额不代表实机命中证明；零观察窗口不计开启及派生治疗。')
            notes.append('开启伤害、命中加攻和派生治疗的实际链顺序未知；完整直接治疗随后续伤害保持未知。')
        sections.append(section('amiya_phase',title,rows,notes))
    sections.extend(chen_motion_reference_sections(scenario))
    chen_phase=result.get('chen_phase_reference')
    if chen_phase and chen_phase['kind']=='post_slash_strengthening':
        isolated=chen_phase['isolated_attack_phase_reference']
        sections.append(section('chen_strengthening','绝影 · 孤立强化阶段参考',[
            metric('duration','斩击后强化持续参数',chen_phase['strengthening_duration_parameter_seconds'],'秒'),
            metric('attack','强化攻击力参考',chen_phase['strengthened_attack_reference']),
            metric('hits','孤立强化阶段攻击次数参考',isolated['conditional_hits'],'次'),
            metric('damage','孤立强化阶段伤害参考',isolated['conditional_damage']),
            metric('slash_end','实际斩击结束时刻',None,'秒'),
            metric('start','实际强化起点',None,'秒')],
            ['孤立阶段沿用既有普通攻击参考；其相对时刻不代表技能开启后的绝对命中时刻。',
             '6秒参数不包括未绑定的斩击阶段，不能证明完整技能结束、结束后充能或本轮周期。']))
    if chen_phase and chen_phase['kind']=='swordwave':
        wave=chen_phase['conditional_components'][0]
        sections.append(section('chen_swordwave','天喟 · 剑气碰撞待核验',[
            metric('hp','声明目标当前生命',chen_phase['declared_current_hp'],'生命'),
            metric('ratio','当前生命伤害比例参数',chen_phase['hp_ratio_parameter']*100,'%'),
            metric('minimum','攻击力保底倍率参数',chen_phase['minimum_attack_scale_parameter'],'倍'),
            metric('damage','剑气单次伤害条件参考',wave['per_hit']),
            metric('body_duration','本体技能持续参数',chen_phase['body_duration_parameter_seconds'],'秒'),
            metric('collision','实际剑气碰撞时刻',None,'秒')],
            ['剑气取声明当前生命比例与攻击力保底的较大值；实际碰撞时生命、路径和独立时钟尚未绑定。',
             '已建模本体三连保留原有时钟小计；完整窗口、阶段和周期伤害不合入未排程剑气。',
             '本体供靶或打断区间不证明剑气路径覆盖；零窗口或当前目标0秒生命周期没有对它的实际输出。']))
    sbell=result.get('sbell_instant_reference')
    if sbell:
        sections.append(section('sbell_instant','铃音吹雪 · 立即来源与结束待核验',[
            metric('per_hit','立即伤害单次条件参考',sbell['per_hit_damage_reference']),
            metric('scale','立即伤害倍率参数',sbell['attack_scale_parameter'],'倍'),
            metric('charges','可充能次数参数',sbell['charge_count_parameter'],'次'),
            metric('end','实际技能结束时刻',None,'秒')],
            ['原描述立即伤害保留既有参数来源；零观察窗口没有伤害，正观察窗口不被0秒结束参考覆盖。',
             '原有结束/回转算术另存参数参考，实际结束、阻回和多充能链尚未绑定；经过伤害独立列条件来源。']))
    snow=result.get('snow_field_reference')
    if snow:
        sections.append(section('snow_field','积雪场地 · 覆盖与首跳待核验',[
            metric('per_tick','每次积雪跳伤条件参考',snow['per_tick_damage_reference']),
            metric('interval','跳伤间隔参数',snow['tick_interval_parameter_seconds'],'秒'),
            metric('coverage','声明积雪覆盖比例',snow['declared_coverage_fraction']*100,'%'),
            metric('ticks','实际积雪跳伤时刻',None,'秒')],
            ['目标条件：'+snow['target_condition_reference']+'。',
             '本体攻击范围不代表积雪场地范围；覆盖比例不确定首跳或覆盖区间。无限技能没有固定完整总伤，技能后雪的生命周期未知。']))
    next_heal=result.get('next_attack_healing_reference')
    if next_heal:
        sections.append(section('next_attack_healing','下次攻击治疗 · 获取与结束待核验',[
            metric('per_heal','单名友方治疗条件参考',next_heal['per_heal_reference'],'生命'),
            metric('recipients','单次治疗目标上限',next_heal['recipient_limit'],'名'),
            metric('charges','可充能次数参数',next_heal['charge_count_parameter'],'次'),
            metric('acquisition','实际友方治疗时刻',None,'秒')],
            ['友方条件：'+next_heal['recipient_condition_reference']+'；符合条件的受疗人数采用情景输入。',
             '敌方供靶区间不代表友方受疗资格；零窗口/零受疗目标不生成治疗。获取、阈值判断、结束和多充能链未核验。']))
    liftoff=result.get('aglna_liftoff_reference')
    if liftoff:
        sections.append(section('aglna_liftoff','重力自定义 · 起飞阶段待核验',[
            metric('chant','吟唱时长参数参考',liftoff['chant_duration_parameter_seconds'],'秒'),
            metric('duration_parameter','原始技能持续参数',liftoff['nominal_skill_duration_parameter_seconds'],'秒'),
            metric('conditional_damage','已有孤立攻击阶段条件伤害参考',liftoff['cast_attack_phase_reference']['conditional_damage']),
            metric('takeoff','实际起飞时刻',None,'秒')],
            ['观察窗口按给定长度保留，不因扣除后回加chant参数变长。',
             '保留旧攻击阶段参数参考，不将孤立阶段事件当作实际开启后的命中时刻；起飞、循环和结束绑定未知。']))
    manual_close=result.get('manual_close_reference')
    if manual_close:
        sections.append(section('manual_close','地狱变相 · 关闭尾段待核验',[
            metric('declared_terminal','指定尾段时长参考',manual_close['declared_terminal_seconds'],'秒'),
            metric('terminal_limit','原始尾段时长参数',manual_close['terminal_limit_parameter_seconds'],'秒'),
            metric('four_hit','单次四连伤害条件参考',manual_close['four_hit_attack_damage_reference']),
            metric('active_reference','未指定关闭时刻的原有技能来源参考',manual_close['active_body_damage_reference']),
            metric('close_time','实际主动关闭时刻',None,'秒')],
            ['尾段时长不等于关闭时刻，不从开启时刻重复排四连，也不扩长给定观察窗口。',
             '关闭决定前后阶段有效攻击，转换绑定及实际时钟未知；两阶段参数不能当作完整总伤。']))
    ines_dot=result.get('ines_dot_reference')
    if ines_dot:
        sections.append(section('ines_dot','淬影突袭 · 持续伤害待核验',[
            metric('per_second','每秒伤害条件参考',ines_dot['per_second_damage_reference']),
            metric('duration','持续时间参数',ines_dot['duration_parameter_seconds'],'秒'),
            metric('first_tick','实际首跳',None,'秒'),
            metric('ticks','实际跳数',None,'次')],
            ['下次攻击命中是持续伤害必要来源；无有效出手参考时不生成持续伤害。',
             '3秒和每秒伤害参数不证明首跳、刷新或边界，不生成3个假定跳伤；物理攻击参考小计保留。']))
    mei=result.get('mei_s1_reference')
    if mei:
        clock=mei['parameter_clock_reference']
        sections.append(section('mei_s1','麻痹弹 · 下次攻击与结束待核验',[
            metric('per_hit','单次物理伤害条件参考',mei['per_hit_damage_reference']),
            metric('sluggish','停顿持续参数',mei['sluggish_duration_parameter_seconds'],'秒'),
            metric('parameter_initial','常规动作算例初动',clock['initial_seconds'],'秒'),
            metric('parameter_cycle','常规动作算例回转',clock['cycle_seconds'],'秒'),
            metric('actual_end','实际技能结束',None,'秒')],
            ['观察窗口保持声明值；下次攻击可等待后续有效供靶，只保留一次出手参考。',
             '常规动作与手动时序的充能结果仅作参数算例；实际S1动作绑定、结束/阻回与完整周期未知。']))
    mizuki=result.get('mizuki_s1_reference')
    if mizuki:
        sections.append(section('mizuki_s1','唤醒 · 下次攻击与结束待核验',[
            metric('physical','单次物理伤害条件参考',mizuki['physical_per_hit_reference']),
            metric('arts','单次额外法术条件参考',mizuki['arts_per_hit_reference']),
            metric('actual_end','实际技能结束',None,'秒')],
            ['有效出手获取仅用已有常规参考；零窗口、无目标或全程打断不生成技能来源。',
             '下次攻击不当作开启瞬间命中；当前动作绑定、结束/阻回与完整周期未核验。']))
    mizuki_amb_y=result.get('mizuki_amb_y_reference')
    if mizuki_amb_y:
        sections.append(section('mizuki_amb_y','水月AMB-Y · 天赋与回复待核验',[
            metric('first_talent','原版第一天赋单次法术条件参考',mizuki_amb_y['original_first_talent']['per_hit_damage_reference']),
            metric('extra_recovery','模组实际额外回复',mizuki_amb_y['actual_extra_healing'])],
            ['原版第一天赋参数保留条件参考；隐藏能力是否附着及与原天赋并存未核验，完整伤害未知。',
             '每击杀回复描述只保留来源；实际额外回复与触发时钟未知，未排治疗事件。']))
    gnosis_module=result.get('gnosis_isw_a_reference')
    if gnosis_module:
        sections.append(section('gnosis_isw_a','灵知ISW-A · 天赋与持续法术待核验',[
            metric('dot_per_tick','每跳法术伤害条件参考',gnosis_module['per_tick_damage_reference']),
            metric('dot_scale','每跳攻击倍率参数',gnosis_module['dot_parameters']['atk_scale']*100,'%'),
            metric('dot_interval','持续法术间隔参数',gnosis_module['dot_parameters']['interval'],'秒'),
            metric('dot_count','实际持续法术跳数',gnosis_module['actual_tick_count'],'次')],
            [readable_description(gnosis_module['trait_description'],gnosis_module['dot_parameters']),
             '原版坚冰保留条件参考；模组能力与原天赋的实际并存、隐藏附着及增长/重置顺序未核验。',
             '自身在场及寒冷/冻结只列原描述条件；首跳、攻击快照、状态覆盖和技能后生命周期未知，未排持续法术事件。',
             '初始未寒冷不证明后续不会寒冷；普通攻击附加1秒寒冷参数不证明持续法术时钟。']))
    gnosis=result.get('gnosis_s1_reference')
    if gnosis:
        sections.append(section('gnosis_s1','高速思考 · 两段时间待核验',[
            metric('per_hit','每段伤害条件参考',gnosis['per_hit_damage_reference']),
            metric('two_hits','两段合计条件参考',gnosis['two_hit_damage_reference']),
            metric('gap','实际两段间隔',None,'秒')],
            ['没有有效出手参考时不生成两段伤害；两段的实际技能绑定、间隔和结束相位未核验。',
             '不把原版两事件默认当同刻命中，不从普通攻击结束推导完整周期。']))
    drone_lifecycle=result.get('drone_lifecycle_reference')
    if drone_lifecycle:
        sections.append(section('drone_aura','狼群光环 · 覆盖与跳伤待核验',[
            metric('per_tick','单次跳伤条件参考',drone_lifecycle['aura_per_tick_damage_reference']),
            metric('interval','每秒伤害描述间隔',drone_lifecycle['aura_interval_description_seconds'],'秒'),
            metric('first_tick','实际首跳',None,'秒'),
            metric('tick_count','实际跳伤次数',None,'次')],
            ['光环围绕全场追敌的浮游单元且不叠加；本体攻击范围没有目标不证明光环无覆盖。',
             '单元位置、首跳与边界未知时不按技能时长生成满覆盖跳伤；零窗口或目标立即消失不产生来源。']))
        if 'unbound_attack_times_parameter' in drone_lifecycle:
            sections.append(section('drone_arrival','特殊浮游单元 · 独立攻击待核验',[
                metric('initial','初始倍率单次伤害条件参考',drone_lifecycle['drone_initial_per_hit_reference']),
                metric('unbound_parameter','attack@times原始参数（含义未绑定）',drone_lifecycle['unbound_attack_times_parameter']),
                metric('arrival','实际到达时间',None,'秒'),
                metric('hits','同目标实际命中计数',None,'次')],
                ['S3单元全场追敌，不能用本体范围或被抑制的本体事件生成独立命中与暖机。',
                 '到达、重选目标、暖机及技能结束返回后的连续性未核验；本体攻击参考小计保留。']))
    summon_routes=result.get('wisdel_summon_qualification_reference')
    if summon_routes:
        talent=summon_routes['talent_route'];route=summon_routes['skill_route']
        status=lambda path:'已达原表培养门槛' if path['cultivation_qualified'] else '未达原表培养门槛'
        level_source=route['selected_level_source']
        skill_text=(readable_description(level_source['description'],level_source['values']) if level_source else
                    '…'.join(route['original_common_fragments']))
        sections.append(section('wisdel_summon_qualification','魂灵之影 · 本体召唤途径培养资料',[
            metric('talent_qualification',talent['name']+' · 精二1级门槛',status(talent)),
            metric('s3_qualification','第三技能 · 精二1级门槛',status(route)),
            metric('s3_selected','当前是否选中第三技能','是' if route['currently_selected'] else '否')],
            ['第二天赋原文：'+readable_description(talent['description'],{}),
             ('当前第三技能原文：' if level_source else '第三技能各级原文共通部分（省略数量）：')+skill_text,
             '以上仅列固定原表第二天赋与第三技能两条本体途径的培养资格，不表示实际召唤、当前存在或已完成施放。',
             '魂灵数量与施放次数仍是窗口来源声明，未确定其来源归属；本资料不涵盖模组或藏品可能附着的全部途径。',
             '实际来源、存活和施放时钟仍待核验；未改变指定次数的条件参考。']))
    wisdel=result.get('wisdel_secondary_reference')
    if wisdel:
        sections.append(section('wisdel_secondary','好礼与余震 · 次生事件待核验',[
            metric('probability','单次判定概率描述参数',wisdel['described_single_check_probability']*100,'%'),
            metric('explosion','单次残影爆炸条件参考',wisdel['explosion_per_hit_reference']),
            metric('expected_count','实际爆炸期望次数',None,'次'),
            metric('secondary_clock','余震命中时间',None,'秒')]+([
                metric('ghost_count','指定魂灵之影施放次数参考',wisdel['ghost_casts_requested'],'次'),
                metric('ghost_per_cast','魂灵之影单次条件伤害',wisdel['ghost_per_cast_damage_reference']),
                metric('ghost_declared_damage','指定次数条件伤害参考',wisdel['ghost_declared_count_damage_reference']),
                metric('ghost_times','魂灵之影施放时刻',None,'秒')] if wisdel.get('ghost_casts_requested') else []),
            ['没有有效出手参考时不生成技能来源；出手参考不证明余震或残影实际命中。',
             '随机独立性、残影刷新/消耗顺序未核验，不套用多次独立判定公式；S1完整结束与周期未知。',
             '指定魂灵施放次数只列窗口条件参考，不证明完整施放或周期归属，不在两个阶段重复计入。']))
    charge=result.get('charge_reference')
    if charge:
        sections.append(section('charge_reference','结构性原理 · 冲锋次数参考',[
            metric('hits','指定情景命中次数',charge['hits_requested'],'次'),
            metric('per_hit','每次冲锋伤害参考',charge['per_hit_damage']),
            metric('declared_damage','给定次数伤害参考',charge['declared_count_damage']),
            metric('collision','冲锋碰撞时刻',None,'秒')],
            ['次数参考不证明碰撞时间或完整施放次数；技能阶段和周期总伤未知。',
             '本体0.8秒落地延迟不用于冲锋。']))
    incoming=result.get('neural_incoming_reference')
    if incoming:
        sections.append(section('neural_incoming','堕梦 · 目标攻击时间待确认',[
            metric('attacks','指定目标普通攻击次数',incoming['attacks_requested'],'次'),
            metric('buildup','每次普通攻击损伤参数',incoming['buildup_per_attack'],'损伤值'),
            metric('first_attack','目标首个普通攻击时刻',None,'秒')],
            ['次数不确定攻击时刻，不按技能时长或观察窗口均匀分配。',
             '缺少事件时刻时，损伤积累、爆发序列和受影响的完整总伤未知；保留已排程法伤小计。']))
    binding=result.get('neural_s1_reference')
    if binding:
        sections.append(section('neural_s1','暗夜回声 · 束缚倍率待核验',[
            metric('direct_ratio','附带损伤攻击力比例',binding['direct_buildup_ratio']*100,'%'),
            metric('direct_raw','单段未计束缚倍率的损伤基础参考',binding['direct_buildup_raw'],'损伤值'),
            metric('binding_multiplier','束缚期间神经损伤倍率参数',binding['binding_multiplier'],'倍'),
            metric('binding_duration','束缚持续时间参数',binding['binding_duration_seconds'],'秒')],
            ['倍率只作用于该次束缚期间；首次生效、黑板初始化与刷新顺序尚未核验。',
             '参数和未计倍率的基础参考不等于当前目标实际积累；受影响的爆发次数与完整总伤未知。',
             '已计法伤小计沿用原版两段动作参考，不包含未知的神经爆发。']))
    neural_skill=result.get('neural_skill_reference')
    if neural_skill:
        sections.append(section('neural_skill','空剧场 · 持续损伤待核验',[
            metric('buildup_ratio','持续神经损伤攻击力比例',neural_skill['periodic_buildup_ratio']*100,'%'),
            metric('buildup_raw','单次持续神经损伤原始参考',neural_skill['periodic_buildup_raw'],'损伤值'),
            metric('interval','持续神经损伤间隔',neural_skill['periodic_interval'],'秒'),
            metric('first_tick','持续神经损伤首跳时刻',None,'秒')],
            ['技能期间先造成神经损伤才有后续持续损伤；未命中不生成持续损伤。',
             '首跳、刷新与爆发后生命周期尚未查明；不根据攻击间隔猜首跳，不假设离开范围就终止。',
             '持续损伤会改变神经爆发序列，因此受影响的爆发次数与完整总伤未知，小计仅保留可确定法伤。']))
    neural_reference=result.get('neural_relic_reference')
    bait_reference=result.get('neural_bait_reference')
    if bait_reference:
        sections.append(section('neural_bait','本能的召唤 · 诱饵持续效果待核验',[
            metric('trigger_count','指定诱饵触发次数',bait_reference['triggers_requested'],'次'),
            metric('snapshot_attack','诱饵部署时攻击力快照',None),
            metric('duration','单次效果持续时间',bait_reference['duration_seconds'],'秒'),
            metric('interval','持续效果间隔',bait_reference['tick_interval_seconds'],'秒'),
            metric('arts_ratio','单次法伤攻击力比例',bait_reference['arts_attack_scale']*100,'%'),
            metric('buildup_ratio','单次神经损伤攻击力比例',bait_reference['buildup_attack_ratio']*100,'%'),
            metric('first_tick','持续效果首跳时刻',None,'秒')],
            ['效果使用诱饵部署时的攻击快照；退场触发，次数不能确定退场时刻。',
             '诱饵神经损伤不受损伤抵抗；持续效果首跳、刷新及叠加未核验。',
             '尚未排程诱饵效果，不使用固定25秒触发间隔；受影响的完整总伤与爆发次数未知。']))
    if neural_reference:
        sections.append(section('river_neural','河谷祭祈 · 神经爆发参考',[
            metric('instant_raw','单次瞬时爆发原始伤害',neural_reference['instant_raw_damage']),
            metric('instant_adjusted','单次瞬时爆发减伤后参考',neural_reference['instant_adjusted_damage']),
            metric('periodic_raw','冷却期额外持续伤害单次原始量',neural_reference['periodic_raw_damage']),
            metric('periodic_interval','额外持续伤害间隔',neural_reference['periodic_interval'],'秒'),
            metric('first_tick','额外持续伤害首跳时刻',None,'秒')],
            ['仅放大神经爆发的瞬时分项，不放大干员附带元素伤害或损伤积累。',
             '已确认产生效果后首跳等待1秒，效果在神经爆发结束时终止；实际首跳时刻和每跳麻痹条件尚未确认，未生成实际追加跳数或完整总量。',
             '四元素倍率、生命周期和条件逐跳规则见河谷机制资料；资料原始量不等于当前情景实际生命伤害。']))
    from .river_effects import RELIC_ID,reference as river_reference
    if any(record.get('id')==RELIC_ID for record in result.get('relic_resolution',{}).get('records',[])):
        lifecycle=(neural_reference or {}).get('lifecycle_reference') or river_reference()
        sections.extend(river_reference_sections(lifecycle))
    subtotals=result.get('known_damage_subtotals')
    if subtotals:
        generic_note='这些数值只包含已保留的本体来源参考，不含未核验的次生事件，不能当作完整输出。'
        river_note='这些数值不包含河谷祭祈未排程的额外持续伤害，不能当作完整总伤或完整 DPS。'
        subtotal_notes=['这些数值仅包含可确定法伤，不含持续损伤及受其影响的未知爆发，不能当作完整总伤或完整 DPS。'
            if neural_skill else '这些数值仅包含已排程的本体法伤，不含诱饵持续效果和受其影响的未知爆发，不能当作完整输出。'
            if bait_reference else generic_note
            if amiya_continuous or wisdel or mizuki or mizuki_amb_y or ines_dot or manual_close or liftoff or snow or unbound or external or chen_phase or result.get('drone_lifecycle_reference') or binding or incoming else
            river_note if neural_reference else generic_note]
        if binding:
            subtotal_notes.append('暗夜回声的束缚倍率首次生效与刷新顺序尚未核验；小计不含受其影响的未知神经爆发。')
        if incoming:
            subtotal_notes.append('堕梦的目标普通攻击次数没有事件时刻；小计不含受其影响的未知神经爆发。')
        if neural_reference and subtotal_notes[0]!=river_note:
            subtotal_notes.append(river_note)
        sections.append(section('known_damage_subtotals','已建模伤害小计',[
            metric('cast','单次技能已计伤害小计',subtotals['total_damage']),
            metric('window','观察窗口已计伤害小计',subtotals['window_damage']),
            metric('cycle','本轮周期已计伤害小计',subtotals['cycle_damage']),
            metric('cycle_dps','已计部分本轮周期 DPS',subtotals['cycle_dps'],'伤害/秒')],subtotal_notes))
    healing_subtotals=result.get('known_healing_subtotals')
    if healing_subtotals:
        sections.append(section('known_healing_subtotals','已建模治疗小计',[
            metric('cast','单次技能已计治疗小计',healing_subtotals['total_healing']),
            metric('window','观察窗口已计治疗小计',healing_subtotals['window_healing']),
            metric('cycle','本轮周期已计治疗小计',healing_subtotals['cycle_healing'])],
            ['只含已保留的本体治疗参考，不含未定位的独立治疗来源，不能当作完整治疗。']))
    if has_healing(op,number):
        rows=[];window_healing=skill['window_healing']
        if not windowed:
            rows.append(metric('per_cast','单次技能总治疗',skill['total_healing']))
            if skill['duration_seconds'] and skill['total_healing'] is not None:
                rows.append(metric('active_hps','技能阶段平均 HPS',skill.get('phase_healing',skill['total_healing'])/skill['duration_seconds'],'治疗/秒'))
        if windowed or 'window_seconds' in scenario or window_healing!=skill['total_healing']:
            rows.append(metric('window_healing','观察窗口治疗',window_healing))
            if skill.get('window_seconds') is not None:
                rows.append(metric('window_seconds','治疗观察窗口',skill['window_seconds'],'秒'))
            if skill.get('window_seconds'):
                rows.append(metric('window_hps','窗口平均 HPS',window_healing/skill['window_seconds'] if window_healing is not None else None,'治疗/秒'))
        if not nonrepeat:rows.append(metric('hps','本轮周期 HPS',skill['cycle_hps'],'治疗/秒'))
        sections.append(section('healing','治疗输出',rows,['满额潜在治疗，未扣过量治疗；生命回复和屏障单独列出。']))
    fee=fee_section(scenario,bb,skill)
    if fee:sections.insert(1,fee)
    if op=='silverash' and number in (1,2):
        discount=bb['svash2_s_1[deck].cost'] if number==1 else bb['cost']
        sections.append(section('deployment_cost','部署费用调整',[
            metric('ally_discount','指定待部署干员减费上限',discount,'费')],
            ['减少另一名干员部署费用，不直接增加当前费用；实际节省取决于被选中的干员及其费用下限。']))
    if op=='char_4228_closur' and number==2:
        sections.append(section('deployment_cost','部署费用调整',[
            metric('rebate_ratio','有效部署返费比例',bb['cost_return']*100,'%'),
            metric('actual_rebate','实际额外返费',None,'费')],
            ['仅技能期间战术点效果范围内的有效部署生效；需要本局部署事件及其实际费用，不默认额外收益。部署返费与技能固定回费分别核算。']))
    if op=='char_151_myrtle':
        sections.append(section('flag','执旗手机制',[metric('skill_block','技能期间阻挡数',0)],['技能期间停止攻击；二技能另有治疗。' if number==2 else '技能期间停止攻击。']))
    sections.extend(mechanism_sections(scenario,result,source,p))
    if result.get('relic_regeneration_rate'):
        sections.append(section('relic_regeneration','藏品生命回复',[
            metric('rate','本体藏品生命回复速度',result['relic_regeneration_rate'],'生命/秒')],
            ['潜在生命回复，未扣满血造成的无效回复；不合并为直接治疗 HPS。']))
    features=result.get('relic_features',[])
    refill=[r for r in result.get('relic_resolution',{}).get('rules',[]) if r['kind']=='ammo_refill']
    if refill:
        rows=[];notes=[]
        for r in refill:
            a=r['ammo_parameters'];name=next(v['name'] for v in result['relic_resolution']['records'] if v['id']==r['relic_id'])
            rows.extend([
                metric('ammo_max_'+r['relic_id'],name+' · 当前已建模最大弹药',a['maximum'],'发'),
                metric('ammo_threshold_'+r['relic_id'],name+' · 正剩余弹药触发阈值',a['threshold'],'发'),
                metric('ammo_refill_'+r['relic_id'],name+' · 单次补充额度',a['refill_count'],'发')])
            if not a['can_trigger_before_empty']:
                notes.append('阈值为0且要求剩余弹药大于0：本技能不能触发补弹，不增加总伤或持续时间。')
            if r.get('ammo_polling_pending'):notes.append('耗尽前检查窗口不足，完整技能输出和周期未知；补充额度不是实际已补回数量。')
            if a.get('partial_packet_reference'):
                counts=result['estimate']['skill'].get('hit_counts',{})
                unresolved=result['relic_resolution'].get('ammo_refill_unresolved') or r.get('ammo_polling_pending') or r.get('ammo_order_pending')
                rows.extend([
                    metric('ammo_full_cast_hits','单次技能预测攻击命中',None if unresolved else counts.get('技能攻击'),'次'),
                    metric('ammo_full_cast_recoveries','单次技能预测天赋回复次数',None if unresolved else counts.get('火力电台本体生命回复'),'次')])
                notes.extend(['当前技能不足5发的最后一包仍完成五连击，天赋按5次消耗处理；不按余弹比例裁减。',
                    '次数为完整技能参考，不表示观察窗口内已经完成；轮询未确认时次数也保持未知。',
                    '末包机制资料：'+a['partial_packet_reference']['source_url']])
            notes.extend(['先作单精度浮点乘法，再将阈值向下取整、补充量向上取整；10发的30%为3发，50发的30%为16发。',
                '0.1秒检查相位/同帧回调未实机校准；此处为普通耗弹局外参考，每次开启至多一次。',
                '来源：'+a['template_url'],'原生算术证明：'+a['native_parameter_proof_sha256']])
        reference=result.get('ammo_refill_reference',{})
        if len(reference.get('cases',[]))>1:
            notes.append('两本书共享同一弹药计数器的恢复额度；两种合法处理顺序均已核算。当前确定次数不表示触发时刻或获取先后已读取。')
        sections.append(section('ammo_refill_reference','藏品补弹参考',rows,notes))
    protection=relic_protection_section(result.get('relic_protection',[]))
    if protection:sections.append(protection)
    deployment=result.get('deployment_reference',{})
    finite_speed=result.get('deployment_buff_reference')
    if finite_speed:
        sections.append(section('deployment_attack_speed','部署限时攻速',[
            metric('snapshot_age','当前属性参考时刻',finite_speed['snapshot_age_seconds'],'部署后秒'),
            metric('permanent_speed','限时结束后的攻速',finite_speed['permanent_attack_speed'],'游戏数值单位'),
            *[metric('speed_'+s['id'],catalog()['relics'][s['id']]['name']+' · 前10秒额外攻速',s['attack_speed_addition'],'游戏数值单位')
              for s in finite_speed['spans']]],[
            '两种疗养卡可同时生效；每次部署重新获得10秒，技能开启不会刷新。',
            '初动、单次技能和本轮周期按同一部署时钟计算；到期时攻击前后摇的中途变速仍采用明确的开始帧参考。']))
    if any(r['kind']=='deployment_cost_add' and not r.get('token_only') for r in features) and not deployment.get('cost'):
        sections.append(section('relic_deployment','藏品部署费用',[
            metric('cost','本体首次部署费用参考',result['deployment_cost'],'费')],
            ['来自培养档案与藏品的部署费用加减；未包含重复部署涨费、环境限制和费用返还。']))
    cost=deployment.get('cost')
    if cost:
        notes=['培养费用与符文先计算并作半值取偶；重部署倍率与卡片倍率分别向下取整，最后加减费用并限制至0–99。',
            '显示首次部署的局外预计值；未观测本局实际扣费、部署次数或外部技能减费。']
        if cost['excluded_script_discounts'] or cost['missing_conditions']:
            notes.append('存在脚本减费或缺失费用条件：显示的单项符文参考未计入这些部分，复合费用保持未知。')
        sections.append(section('relic_deployment_reference','藏品部署费用参考',[
            metric('cultivation_cost','培养档案费用',cost['cultivation_cost'],'费'),
            metric('rune_addition','已确认藏品符文加减',cost['rune_addition'],'费'),
            metric('rune_factor','藏品符文费用倍率',cost['rune_factor']),
            metric('rune_reference','符文取整后费用',cost.get('attributes_cost'),'费'),
            metric('combined_reference','首次部署预计费用',cost['combined_reference'],'费')],notes))
    first=deployment.get('first_deployment_cost')
    if first:
        notes=['先完成符文费用取整，再乘首次卡片倍率并向下取整；已确认的他缚与铁卫可以组合。',
            '卡片在本次成功部署扣费后消耗。本工具只估算首次部署，未观测本局是否已经消耗。']
        if first['excluded_discount_sources']:notes.append('同时存在其他费用来源或未确认条件：复合费用保持未知，不假定折扣的先后次序。')
        sections.append(section('first_deployment_reference','首次部署费用参考',[
            metric('cultivation_cost','培养档案费用',first['cultivation_cost'],'费'),
            metric('card_factor','首次部署卡片倍率',first['card_factor']),
            metric('combined_reference','首次部署预计费用',first['combined_reference'],'费')],notes))
    for loss in deployment.get('hp_loss',[]):
        notes=['使用本体常态最大生命与明确给出的本次事件前生命比例；不改生命上限，不扣屏障。',
            '本次部署未触发时仅计算一次当前生命损失；已触发标记下本次额外损失为0。重算不推进状态，退场后新部署需新的明确情景。',
            '局外独立理论值；不自动读取当前生命或真实触发帧，不将事件后的生命比例自动套给低血量增益，不混入技能伤害/HPS。']
        if loss['loss_unused'] is not None:notes.append('本次部署触发状态：'+('尚未损血' if loss['loss_unused'] else '已经损血，不重复扣除'))
        sections.append(section('relic_deployment_loss','他缚 · 部署损血参考',[
            metric('max_hp','常态最大生命参考',loss['max_hp_reference']),
            metric('before','本次事件前当前生命参考',loss['hp_before_loss']),
            metric('ratio','单次当前生命损失比例',loss['loss_ratio']*100,'%'),
            metric('lost','本次额外生命损失',loss['lost_hp']),
            metric('after','本次事件后当前生命参考',loss['hp_after_loss'])],notes))
    if any(r['kind']=='token_deploy_slot_free' for r in features):
        sections.append(section('relic_tokens','藏品召唤物规则',notes=[
            '符合召唤物选择器的单位不占部署人数；不扩大召唤物自身在场数量上限。']))
    for token in result.get('relic_token_stats',[]):
        protection=relic_protection_section(token.get('protection',[]),token)
        if protection:sections.append(protection)
        sources='及'.join(token.get('modifier_sources',['藏品']))
        module=token.get('module_reference')
        cost_module=token.get('module_cost_reference')
        notes=['使用独立召唤物档案与适用的'+sources+'；不继承召唤师信赖或职业加成，'+
               ('已覆盖深海色SUM-Y的费用、持有/在场上限及生命叠加；未覆盖其他召唤物模组。' if module else
                '已覆盖望TRP-X的棋子固定费用修正；额外部署数、特殊天赋与实际在场数量仍未核验。' if cost_module else
                '未覆盖召唤物模组与特殊天赋修正。')]
        sections.append(section('relic_token_'+token['id'],token['name']+' · '+sources+'属性参考',[
            metric('hp','生命',token['hp']),metric('attack','攻击',token['attack']),
            metric('defense','防御',token['defense']),metric('speed','攻速',token['attack_speed'],'游戏数值单位'),
            metric('cost','部署费用',token['deployment_cost'],'费')],
            notes))
        if module:
            sections[-1]['metrics'].extend([
                metric('module_stage','装备模组阶段',module['module_level'],'级'),
                metric('held_limit','触手持有上限',module['held_limit'],'个'),
                metric('concurrent_limit','触手同时在场上限',module['concurrent_limit'],'个'),
                metric('model_count','参与测算触手数（局外假设）',scenario.get('summon_count',1),'个'),
                metric('module_hp_pct','模组单项生命提升',module['hp_pct']*100,'%')])
            sections[-1]['notes'].append('同时在场上限来自触手自己的数量限制；所选数量仍受关卡可用部署位、地块和当前库存约束。持有上限不会自动作为在场数量，不推断真实站位或数量。')
            if module['hp_composition_verified'] and module['hp_pct']:
                sections[-1]['notes'].append('生命先计入适用的藏品和分队加成并取整，再计入模组天赋；模组与其他普通生命百分比加成相加。百分比生命回复使用此处的预计生命。')
            if module['hp_composition_pending']:
                sections[-1]['metrics'].extend([
                    metric('module_only_hp','仅模组的生命参考',module['module_only_hp']),
                    metric('other_sources_only_hp','不含模组的其他来源生命参考',module['other_sources_only_hp'])])
                sections[-1]['notes'].append('模组与藏品/分队生命的叠加层尚未核验：复合生命及依赖该生命的回复未知；上述两个单项不可自行相加或相乘。已确认伤害与固定生命回复不受影响。')
        if cost_module:
            sections[-1]['metrics'].extend([
                metric('module_stage','装备模组阶段',cost_module['module_level'],'级'),
                metric('module_cost_add','模组棋子费用修正',cost_module['cost_add'],'费')])
            sections[-1]['notes'].append('仅修正已解锁模组对应棋子的培养费用参考；不扩大棋子数量、不推断库存、地块或真实部署。')
        if 'regeneration_rate' in token:
            sections[-1]['metrics'].append(metric('regeneration_rate','藏品常态生命回复',token['regeneration_rate'],'生命/秒'))
    incoming=[r for r in features if r['kind']=='incoming_element_resistance']
    if incoming:
        sections.append(section('relic_element_resistance','藏品元素防护',[
            metric('resistance','受到的元素损伤减免',incoming[0]['value']*100,'%')],
            ['影响我方受到的元素损伤积累，不减敌方元素生命伤害；实际承受总量尚未模拟。']))
    control=[r for r in features if r['kind']=='status_duration_delta']
    if control and any(s['id']=='control' for s in sections):
        sections.append(section('relic_control','藏品状态时长参考',[
            metric('factor','敌人状态时长调整系数',1+control[0]['value'])],
            ['仅报告黑板的状态时长调整；免疫、基础抗性和具体控制命中时序仍需核对。']))
    enemy=result.get('relic_resolution',{}).get('enemy_effects',{})
    if enemy.get('hp_factors'):
        sections.append(section('relic_enemy','藏品敌方生命修正',[
            metric('hp_factor','目标生命缩放系数',math.prod(enemy['hp_factors']))],
            ['供关卡敌人生命估计使用；当前单目标供靶计算没有按血量死亡截断，不能据此宣称击杀时间。']))
    if enemy.get('hp_composition_pending'):
        sections.append(section('relic_enemy_unresolved','居民生命组合待核验',[
            metric('hp_factor','厄运火杆与其他生命藏品的复合倍率',None)],
            ['当前敌方生命参考保留已接入来源，未额外乘0.6；不由文字减益擅自推断叠乘或加算。']))
    resolution=result.get('relic_resolution',{})
    if resolution.get('records'):
        labels={'applied':'已计算支持部分','bound':'已确认绑定当前干员；效果见个人强化条目','incomplete':'条件缺失或机制未覆盖','inapplicable':'当前干员不适用','non_output':'无干员输出加成','reference_only':'战斗相关效果仅作资料'}
        evidence=section('relic_evidence','藏品核验',notes=[
            r['name']+'：'+labels[r['status']]+('；领取干员：'+catalog()['operators'][r['recipient']]['name'] if r.get('recipient') else '')+
            ('；缺 '+ '、'.join(r['missing_conditions']) if r['missing_conditions'] else '')
            for r in resolution['records']])
        sections.append(evidence)
        references=[r for r in resolution['records'] if r.get('reference_effects') or r.get('reference_pending')]
        if references:
            sections.append(section('relic_combat_reference','藏品效果资料',notes=[
                r['name']+'：'+r.get('reference_usage','') for r in references]+[
                '涉及击倒、受击、实时生命/屏障或站位的部分只保留资料，不计入局外数值，也不要求战斗事件输入。',
                '同件藏品的稳定加成如适用仍单独计算；资料中的战斗收益未包含在所显示的输出中。']))
        used={e[k] for r in resolution['records'] for e in r['applied'] for k in ('condition','recipient_condition') if e.get(k) in resolution.get('context',{})}
        labels={'gold':'源石锭','parts_count':'零件数','current_hp_ratio':'当前生命比例',
            'adjacent_allies':'相邻我方单位','deployed_casters':'实际在场术师','skill_cast_stacks':'已确认技能叠层',
            'altar_stacks':'圆石祭坛实际层数','chitin_recipient':'当前干员刺刃受益标记',
            'battle_start_shields':'开战时对局护盾值','blocked_enemies':'本体情景阻挡敌人数','probe_stacks':'探测先锋实际层数'}
        labels.update(empty_slots='零件箱空栏数',grudge_stacks='仇名录实际击杀叠层',deployed_seconds='在场秒数',
            near_protection_point='目标点周围八格标记',enemy_first_damage_unused='对该目标首伤未触发标记',
            entered_zone_count='累计进入新区域数',active_other_aura_sources='犬植浆生效的其他光环数',
            mercenary_recipient='佣兵饰物实际受益标记',mercenary_stacks='佣兵饰物总层数（含初始层）',
            fire_rod_stacks='厄运火杆实际层数',deployment_hp_ratio='本次部署事件前生命比例',
            deployment_loss_unused='本次部署损血尚未触发标记')
        if used:evidence['notes'].append('条件参考：'+'、'.join(labels.get(k,k)+'='+str(resolution['context'][k]) for k in sorted(used))+'；'+resolution['context_source']+'。')
        for record in resolution['records']:
            caps={e['condition']:e['maximum'] for e in record['applied'] if e.get('condition') and 'maximum' in e}
            for key,cap in caps.items():
                if resolution.get('context',{}).get(key,0)>cap:
                    evidence['notes'].append(record['name']+'：提供的'+labels.get(key,key)+'超过计数上限，按'+str(int(cap))+'计入加成。')
    environment=result.get('run_resolution',{})
    enemy=environment.get('enemy')
    if enemy:
        names={'maxHp':'预计生命值','atk':'预计攻击力','def':'预计防御','magicResistance':'预计法抗'}
        spawn=enemy.get('spawn_hp')
        if spawn:names['maxHp']='已接入生命来源参考（未含随机出生加成）'
        rows=[metric(key,label,enemy['stats'][key]) for key,label in names.items()]
        weight_changed=any('massLevel' in step.get('deltas',{}) for step in enemy['steps'])
        if weight_changed:
            names['massLevel']='预计重量'
            rows.append(metric('massLevel',names['massLevel'],enemy['stats']['massLevel'],'重量等级'))
        rows.append(metric('damage_factor','难度承伤独立倍率',enemy['damage_factor']))
        for dtype,factor in enemy.get('type_factors',{}).items():
            rows.append(metric('intrinsic_'+dtype,('物理' if dtype=='physical' else '法术')+'自身承伤倍率',factor))
        notes=[enemy['stage_name']+' · '+enemy['stage_difficulty']+' · '+enemy['name']+' · '+(enemy['level_type'] or '类别未确认')]
        for step in enemy['steps']:
            values='、'.join(names.get(k,k)+'×'+f'{v:.6g}' for k,v in step.get('factors',{}).items())
            values=values or '、'.join(names.get(k,k)+f'{v:+.6g}' for k,v in step.get('deltas',{}).items())
            values=values or '、'.join(('物理' if k=='physical' else '法术')+'承伤×'+str(v) for k,v in step.get('type_factors',{}).items())
            notes.append(step['label']+'：'+(values or '承伤×'+str(step['damage_factor'])))
            if step.get('evidence'):
                notes.append(step['evidence']['source_note']+' 来源：'+step['evidence']['source_url'])
        notes+=enemy['pending']+['敌人技能、阶段与动态环境尚未模拟；候选不代表必定出场。']
        if weight_changed:notes.append('重量允许为负；此处不据此计算位移距离、控制时长或额外伤害。')
        sections.append(section('enemy_environment','关卡目标与环境修正',rows,notes))
        if spawn:
            rows=[metric('untriggered_max_hp','未触发的生命参考',spawn['untriggered_max_hp']),
                metric('triggered_max_hp','触发的生命参考',spawn['triggered_max_hp']),
                metric('probability','单个敌人出生触发概率',spawn['probabilities']['triggered']*100,'%')]
            notes=['未观测当前出生分支；两种生命值是局外预览，不将概率加权生命当作实际数值。',
                '3%为单个敌人的来源概率，不推定各敌人之间独立，也不据此推算整关至少一次触发概率。',
                '生命分支不改变防御/法抗或持续供靶伤害与回转；不推算实际死亡和击杀时间。']
            if spawn.get('verified_final_hp_sources'):
                notes.append('已核对的最终生命倍率：'+
                    '、'.join(catalog()['relics'][rid]['name'] for rid in spawn['verified_final_hp_sources'])+
                    '；按已确认计数计算，并在咖啡直接乘算层之后相乘。计数获取、重置与敌人动态阶段仍未自动核验。')
            if spawn['excluded_hp_sources']:
                rows.append(metric('single_item_triggered_max_hp','单件猎犬咖啡强化生命参考（隔离其他生命藏品）',spawn['single_item_triggered_max_hp']))
                notes.append('随机出生生命与其他生命藏品的组合尚未核验：'+
                    '、'.join(catalog()['relics'][rid]['name'] for rid in spawn['excluded_hp_sources'])+'；复合触发生命值保持未知。')
            sections.append(section('enemy_spawn_hp','猎犬咖啡出生生命分支',rows,notes))
    if environment.get('squad') or environment.get('difficulty'):
        notes=list(environment.get('notes',[]))+list(environment.get('pending',[]))
        difficulty=environment.get('difficulty')
        if difficulty:
            source=difficulty.get('source','明确提供的计算情景')
            if not isinstance(source,str):source='未确认（来源字段不是文本）'
            notes.insert(0,'本局保密等级：'+str(difficulty['value'])+'；来源：'+source)
        labels={'attack_pct':'分队攻击加成','hp_pct':'分队生命加成','defense_pct':'分队防御加成'}
        rows=[metric(r['kind'],labels[r['kind']],r['value']*100,'%') for r in environment.get('applied',[]) if r['kind'] in labels]
        sections.append(section('run_environment','本局配置与修正',rows,notes))
    squad_reference=environment.get('squad_unlock_reference')
    if squad_reference:
        notes=['档案解锁条件：'+squad_reference['unlock_condition_reference']]
        technology=squad_reference['technology_node_reference']
        if technology:
            notes.append('对应科技资料：'+technology['name'])
            gate=technology['gate_reference']
            if gate:notes.append('科技生效门槛资料：'+gate['enable_description_reference'])
        notes.append('这里只列条件资料；账户解锁与条件实际激活未知，不据此切换分队版本或追加效果。当前明确确认的本局效果按原情景计算。')
        sections.append(section('squad_unlock_reference','强化分队 · 条件资料',[
            metric('account_unlock','账户解锁状态',None),
            metric('activation','解锁条件实际激活',None)],notes))
    sections.extend(current_output_breakdown_sections(result))
    sections.extend(reproducible_context_sections(scenario,result))
    sections.extend(event_clock_reference_sections(scenario,result))
    sections.extend(output_domain_comparison_sections(scenario,result))
    report={'schema_version':2,'operator':{'id':op,'name':p['name'],'profession':p['profession']},
        'skill_number':number,'skill_rank':scenario.get('skill_rank',10),'mode':mode,'sections':sections}
    from .module_source_reference import selected_module_reference, module_source_notes, REFERENCE_KEY, SECTION_ID
    reference=selected_module_reference(p,scenario,result,sections)
    if reference:
        report[REFERENCE_KEY]=reference
        sections.append(section(SECTION_ID,'所选模组 · 原件资料与覆盖边界',
            notes=module_source_notes(reference,sections,readable_description)))
    return report


def format_report(result,*,technical=False):
    estimate=result['estimate'];report=result['report'];stats=estimate['base_stats'];training=estimate['training']
    def number(value):
        if value is None:return '未知（需要条件或尚未建模）'
        if isinstance(value,str):return value
        return f'{value:,.2f}'.rstrip('0').rstrip('.')
    sources=[]
    def phrase(text):
        text=str(text)
        replacements={'DPS/HPS':'每秒伤害 / 每秒治疗','DPS':'每秒伤害','HPS':'每秒治疗',
            '30Hz':'30帧/秒',
            'timing.sp_events.initial':'初动阶段事件表','timing.sp_events.cycle':'本轮周期事件表',
            'projectile_delay_time':'档案弹道延迟参数','attack@interval':'档案连击间隔参数'}
        for key,value in replacements.items():text=text.replace(key,value)
        text=re.sub(r' (?=每秒伤害|每秒治疗)','',text)
        # Enum labels are presentation only; the numeric source and debug JSON stay intact.
        text=re.sub(r'\b(?:NORMAL|ELITE|BOSS|FOUR_STAR)\b',lambda m:{
            'NORMAL':'普通','ELITE':'精英','BOSS':'领袖','FOUR_STAR':'紧急'}[m.group()],text)
        if technical:return text
        # Translate this verified condition only; unknown script keys stay opaque.
        text=re.sub(r'(?<![\w:.\[\]@])emergency_hire(?![\w:.\[\]@])','应急招募来源',text)
        for url in re.findall(r'https?://[^\s；，。<>）]+',text):
            if url not in sources:sources.append(url)
        text=re.sub(r'\s*原生算术证明[:：]\s*[0-9a-f]{64}','',text)
        text=re.sub(r'\s*(?:来源|定点资料)[:：]\s*https?://[^\s；，。<>）]+','',text)
        text=re.sub(r'https?://[^\s；，。<>）]+','（来源见技术资料）',text)
        # An opaque script key has no proven mechanism name. Keep the gap, not
        # an invented translation; original warning strings remain in debug.
        text=re.sub(r'\b[A-Za-z][A-Za-z0-9_]*_[A-Za-z0-9_]+(?::[A-Za-z0-9_@\[\].-]+)?(?![A-Za-z0-9_])',
                    '未核验配置（原文见技术资料）',text)
        text=re.sub(r'(未核验配置（原文见技术资料）[、；]){2,}',
                    '多项未核验配置（原文见技术资料）、',text)
        return text.strip()
    def render(row):
        value=row['value'];unit=row['unit']
        if row.get('range'):
            bounds=row['range']
            return phrase(row['label'])+f'：{bounds["lower"]:.2f}–{bounds["upper"]:.2f} '+unit+'（相位范围）'
        if row.get('reason'):return phrase(row['label']+'：'+row['reason'])
        shown=f'{value:.2f}' if value is not None and unit=='秒' else number(value)
        return phrase(row['label']+'：'+shown+(' '+unit if value is not None and unit else ''))
    professions={'pioneer':'先锋','warrior':'近卫','tank':'重装','sniper':'狙击','caster':'术师','medic':'医疗','support':'辅助','special':'特种'}
    modes={'infinite':'无限持续','passive':'常驻被动','switch':'切换模式','once':'整场限用一次',
        'once_deploy':'结束后退场','deployment':'部署触发，无原地回转','triggered_ammo':'布子弹药',
        'ammo':'攻击弹药','next_attack':'强化/替代下次攻击','instant':'瞬时触发','timed':'有限持续'}
    rank=report['skill_rank'];rank_text=f'{rank}级' if rank<=7 else f'7级 · 专精{rank-7}'
    lines=[report['operator']['name']+' · '+professions.get(report['operator']['profession'],'职业未确认'),
        '计算状态：'+('支持范围内估算' if estimate['complete'] else '不完整（见待确认与适用范围）'),
        '', '【培养信息】',f"精英 {training['elite']} · 等级 {training['level']} · 潜能 {training['potential']} · 信赖加成进度 {training['trust']}%",
        '', '【预计属性】','含已支持的天赋和藏品；不是未修正基础值。',
        f"生命值：{number(stats['hp'])}    攻击力：{number(stats['attack'])}",
        f"防御：{number(stats['defense'])}    法抗：{number(stats['resistance'])}",
        f"再部署时间：{stats['redeploy_seconds']:.2f} 秒    阻挡数：{number(stats['block_count'])}",
        f"攻速：{number(stats.get('attack_speed_reference',stats['attack_speed']))}（游戏数值单位，基础 100）"+
        (f"；攻击间隔使用攻速 {number(stats['attack_speed'])}（10–600 范围，面板攻速保留实际值）" if stats.get('attack_speed_reference',stats['attack_speed'])!=stats['attack_speed'] else ''),
        '', '【当前技能】',f"{estimate['skill']['name']} · {rank_text} · {modes.get(report['mode'],'技能模式未确认')}"]
    enemy=result.get('run_resolution',{}).get('enemy',{})
    if enemy.get('enemy_id')=='enemy_2148_shorbb':
        lines.insert(1,'输出口径：固定行动模式与统一来源列的测试情景。' if enemy.get('type_factors') else
            '输出口径：源阶方阶段/来源列未确认，以下是未套用自身减伤的参考，不能当作实际伤害。')
    explanations=[]
    for block in report['sections']:
        notes=list(dict.fromkeys(phrase(note) for note in block['notes']))
        notes=[note for note in notes if note]
        if block['metrics']:
            lines.extend(['','【'+phrase(block['title'])+'】',*[render(row) for row in block['metrics']]])
            if notes:explanations.append((phrase(block['title']),notes))
        elif notes:lines.extend(['','【'+phrase(block['title'])+'】',*['• '+note for note in notes]])
    if explanations:
        lines.extend(['','【计算说明】'])
        for title,notes in explanations:lines.extend([title+'：',*['• '+note for note in notes]])
    notes=[]
    for note in estimate['notes']:
        if note.startswith('周期 DPS/HPS 包含'):note='周期平均指标包含技能与结束后充能阶段；各指标仅在相应能力存在时显示。'
        if not has_healing(report['operator']['id'],report['skill_number']):
            note=note.replace('单目标持续存活、供靶/满额受疗情景','单目标持续存活、供靶情景')
        notes.append(phrase(note))
    lines.extend(['','【待确认与适用范围】','情景范围：'+phrase(estimate['scenario_scope']),
        *['• '+note for note in dict.fromkeys(notes) if note],
        *['• '+phrase(warning) for warning in dict.fromkeys(estimate['warnings'])]])
    if not technical and sources:lines.append('资料引用已保留；勾选“显示技术资料”可查看完整来源。')
    if technical:
        lines.extend(['','【技术资料】','干员标识：'+report['operator']['id'],
            '技能序号：'+str(report['skill_number'])+'；内部等级：'+str(rank),
            '模式字段：'+report['mode'],
            '显示用语：每秒伤害＝DPS；每秒治疗＝HPS；普通/精英/领袖＝NORMAL/ELITE/BOSS；紧急关卡＝FOUR_STAR。',
            '档案字段：弹道延迟＝projectile_delay_time；连击间隔＝attack@interval。字段存在不代表完成实机校准。',
            '完整计算输入和原始指标可在“结构化计算数据（调试）”查看。'])
    if technical and report.get('selected_module_source_reference'):
        from .module_source_reference import technical_source_trace
        lines.extend(['',technical_source_trace(report['selected_module_source_reference'])])
    return '\n'.join(lines)
