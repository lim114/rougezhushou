"""Separate known burst damage from unresolved elemental damage timelines."""


def exclude_unplaced_neural_source(result,reference):
    """An unresolved neural source changes burst state; retain direct subtotals."""
    skill=result['estimate']['skill'];affected=reference['affected_damage_phases']
    excluded=reference['excluded_burst_damage']
    existing=result.get('known_damage_subtotals')
    if existing is not None:
        # Several unresolved sources can affect the same burst sequence.
        # The first finisher already excluded it; never subtract it twice.
        subtotals=dict(existing)
    else:
        subtotals={key:skill.get(key) for key in
            ('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps')}
        subtotals['window_damage']=skill.get('window_damage',result['total_damage'])
        for key,phase in (('total_damage','cast'),('phase_damage','phase'),
                          ('window_damage','window'),('cycle_damage','cycle')):
            if subtotals[key] is not None:
                subtotals[key]=max(0,subtotals[key]-excluded[phase])
    cycle=skill['cycle_seconds'];window=skill['window_seconds']
    subtotals['cycle_dps']=subtotals['cycle_damage']/cycle if cycle else None
    subtotals['window_dps']=subtotals['window_damage']/window if window else None
    result['known_damage_subtotals']=subtotals
    for phase,keys in {'cast':('total_damage','phase_damage'),
                       'window':('window_damage','window_dps'),
                       'cycle':('cycle_damage','cycle_dps')}.items():
        if affected[phase]:
            for key in keys:skill[key]=None
    if affected['window']:
        result['total_damage']=None
        result['components']=[c for c in result['components'] if c['name']!='神经损伤爆发']
    if affected['cast']:skill['hit_counts'].pop('神经损伤爆发',None)
    river=result.get('neural_relic_reference')
    if river:
        for phase in ('cast','window','cycle'):
            if affected[phase]:river[phase+'_burst_times']=None
        river['burst_schedule_status']='unknown_due_to_secondary_buildup'
    result['complete']=False;result['estimate']['complete']=False
    result['complete_definition']='当前情景包含尚未核验的持续效果和爆发时间线；基础属性与已知分项独立展示。'
    result['estimate']['notes']=[
        '本轮周期法伤包含技能与充能期的已排程命中；神经爆发序列受未核验持续损伤影响而未知。'
        if n.startswith('周期神经损伤连续结算') else n for n in result['estimate']['notes']]


def finish_neural_skill(result):
    reference=result.get('neural_skill_reference')
    if not reference:return
    exclude_unplaced_neural_source(result,reference)
    result['complete_definition']='当前技能包含尚未核验的持续损伤和爆发时间线；基础属性与已知分项独立展示。'
    result['estimate']['notes'].append(
        '空剧场持续损伤要求技能期间先造成神经损伤。首跳、刷新与爆发后生命周期未核验，'
        '未排程该损伤或把直接损伤单独计算的爆发次数当作实际结果；'
        '受影响总伤/DPS未知，小计只保留可确定法伤。离开范围不被擅自当作状态终止。')


def finish_neural_reference(result):
    incoming=result.get('neural_incoming_reference')
    if incoming:
        exclude_unplaced_neural_source(result,incoming)
        result['estimate']['notes'].append(
            '堕梦的目标普通攻击次数没有提供事件时刻；不按技能或观察窗口时长均匀分配。'
            '实际损伤积累、爆发序列及受影响的完整总伤未知，小计保留已排程的本体法伤。')
    binding=result.get('neural_s1_reference')
    if binding:
        exclude_unplaced_neural_source(result,binding)
        for component in result['components']:
            if component['damage_type']=='buildup':
                component['name']='未计束缚倍率的损伤基础参考（不是生命伤害）'
                component['binding_multiplier_applied']=False
                if binding['affected_damage_phases']['window']:
                    component['actual_total']=None
        result['complete_definition']='暗夜回声束缚倍率的首次生效与刷新尚未核验；法伤小计和未计束缚倍率的损伤基础参考独立展示。'
        result['estimate']['notes'].append(
            '暗夜回声束缚模板的神经损伤倍率已查明，但首次附着、黑板初始化与刷新顺序尚未闭合。'
            '不将该倍率直接套在两段攻击上；受影响的损伤积累、爆发次数和完整总伤未知，'
            '小计仅保留原版动作参考下的已排程法伤。')
        river=result.get('neural_relic_reference')
        if river:river['burst_schedule_status']='unknown_due_to_s1_binding'
    finish_neural_skill(result)
    bait=result.get('neural_bait_reference')
    if bait and any(bait['affected_damage_phases'].values()):
        exclude_unplaced_neural_source(result,bait)
        result['estimate']['notes'].append(
            '本能的召唤：诱饵按部署时攻击力快照，在退场后触发持续效果；缺少快照与事件时刻时，'
            '诱饵法伤、神经损伤及受影响的实际爆发/完整总伤未知。不用次数推算触发间隔，'
            '诱饵损伤不受损伤抵抗，不能沿用本体损伤的抵抗缩放。小计仅保留已排程的本体法伤。')
    reference=result.get('neural_relic_reference')
    if not reference:
        return
    from .river_effects import RELIC_ID,reference as river_reference
    if reference.get('relic_id')==RELIC_ID:
        reference['lifecycle_reference']=river_reference()
    sources=(incoming,binding,result.get('neural_skill_reference'),bait)
    secondary={phase:any((source or {}).get('affected_damage_phases',{}).get(phase,False)
        for source in sources) for phase in ('cast','window','cycle')}
    affected={phase:bool(reference[phase+'_burst_times'] or reference['preexisting_break_assumed'] or secondary.get(phase))
              for phase in ('cast','window','cycle')}
    reference['periodic_damage_possible']=any(affected.values())
    reference['affected_damage_phases']=affected
    if not any(affected.values()):
        return
    # The native relative first tick/lifetime is known, but has not yet been
    # integrated into this schedule. Do not treat unscheduled extra damage as
    # zero or infer absolute events from the interval alone.
    skill=result['estimate']['skill']
    keys=('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps')
    subtotals=result.get('known_damage_subtotals')
    if subtotals is None:
        subtotals={key:skill.get(key) for key in keys}
        subtotals['window_damage']=skill.get('window_damage',result['total_damage'])
    result['known_damage_subtotals']=subtotals
    phase_keys={'cast':('total_damage','phase_damage'),
                'window':('window_damage','window_dps'),'cycle':('cycle_damage','cycle_dps')}
    for phase,fields in phase_keys.items():
        if affected[phase]:
            for key in fields:
                skill[key]=None
    if affected['window']:
        result['total_damage']=None
    result['complete']=False
    result['estimate']['complete']=False
    result['estimate']['notes'].append(
        '河谷祭祈已计神经瞬时爆发翻倍；额外持续伤害尚未排程。完整总伤与伤害效率未知，'
        '另列已建模伤害小计，不把小计当作完整输出。初动、回转和治疗不因此清空。')
