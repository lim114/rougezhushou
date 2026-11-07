"""Explain explicit current enemy declarations without guessing live state."""

IMMUNITIES = {
    'stunImmune': '晕眩', 'silenceImmune': '沉默', 'sleepImmune': '沉睡',
    'frozenImmune': '冻结', 'levitateImmune': '浮空',
    'disarmedCombatImmune': '战栗', 'fearedImmune': '恐惧',
    'palsyImmune': '麻痹', 'attractImmune': '诱导',
    'teleportImmune': '传送', 'groundBoundImmune': '缚地',
}
FIELDS = ('motion', 'applyWay', 'lifePointReduce', 'notCountInTotal')
CORE_ATTRIBUTES = ('maxHp', 'atk', 'def', 'magicResistance')
MOTION = {'WALK': '地面行动', 'FLY': '飞行行动'}
ATTACK = {'MELEE': '近战', 'RANGED': '远程', 'ALL': '近战与远程',
          'NONE': '未配置普通攻击途径；仍可能有技能或特殊行为'}
DAMAGE = {'PHYSIC': '物理伤害', 'MAGIC': '法术伤害', 'HEAL': '治疗',
          'NO_DAMAGE': '图鉴未列常规伤害', 'TRUE': '真实伤害'}


def binding_sources(binding, reference):
    definitions = reference['inputs']['enemy_definitions'].get(binding['id'], [])
    level = binding['level']
    inherited = []
    handbook = {}
    if binding['useDb'] is True:
        inherited = sorted((row for row in definitions if row['level'] <= level),
                           key=lambda row: row['level'])
        exact = bool(inherited) and inherited[-1]['level'] == level
        handbook = reference['inputs']['handbook'].get(binding['id']) or {}
    else:
        exact = any(row['level'] == level for row in definitions)
    return exact, inherited, handbook


def declarations(binding, reference):
    return declarations_from_sources(binding, *binding_sources(binding, reference))


def declarations_from_sources(binding, exact, inherited, handbook):
    """Traits require an exact database level before applying inherited writes."""
    sources = [(f"数据库等级{row['level']}", row['enemyData']) for row in inherited] if exact else []
    sources.append(('本关明确覆盖', binding.get('overwrittenData') or {}))
    values, provenance, core = {}, {}, {}
    for label, data in sources:
        attributes = data.get('attributes') or {}
        for key in CORE_ATTRIBUTES:
            wrapper = attributes.get(key)
            if wrapper is not None and wrapper['m_defined'] is True:
                core[key] = wrapper['m_value']
        for key in (*FIELDS, *IMMUNITIES):
            immunity = key in IMMUNITIES
            container = attributes if immunity else data
            wrapper = container.get(key)
            if (not isinstance(wrapper, dict) or wrapper.get('m_defined') is not True
                    or 'm_value' not in wrapper):
                continue
            value = wrapper['m_value']
            valid = (type(value) is bool if immunity or key == 'notCountInTotal'
                     else type(value) is int and value >= 0 if key == 'lifePointReduce'
                     else type(value) is str)
            if valid:
                values[key] = value
                provenance[key] = {'source': label, 'path':
                                   ('attributes.' if immunity else '') + key}
    # A handbook entry describes its database identity, never an independent constructor.
    raw_damage = handbook.get('damageType') if exact else None
    damage = list(raw_damage) if isinstance(raw_damage, list) and all(
        type(value) is str for value in raw_damage) else None
    return {'values': values, 'provenance': provenance, 'handbook_damage_types': damage,
            'explicit_core_attributes': core,
            'database_level_available': exact if binding['useDb'] is True else None,
            'current_immunity_or_blockability_proven': False,
            'final_life_loss_or_total_count_proven': False}


def player_lines(traits):
    if not traits:
        return []
    values = traits['values']
    lines = ['', '【行动与攻击方式】',
             '行动方式：' + MOTION.get(values.get('motion'), '未取得明确设置'),
             '普通攻击途径：' + ATTACK.get(values.get('applyWay'), '未取得明确设置')]
    damage = traits['handbook_damage_types']
    if damage:
        lines.append('图鉴攻击类型：' + '、'.join(DAMAGE.get(v, '类型尚未核对') for v in damage))
    lines.append('地面或飞行是资料中的行动方式，不能单凭它判断当前能否阻挡；变形、浮空及技能效果请结合下方机制。')
    if 'lifePointReduce' in values:
        lines += ['', '【漏敌与敌人数】', '抵达终点的原设置：扣除' + str(values['lifePointReduce']) + '点目标生命。',
                  '这是抵达自身路径终点的配置，不代表被击倒时的效果；本局保护、特殊退场和其它修正后的实际扣点仍需核对。']
    count = values.get('notCountInTotal')
    if type(count) is bool:
        lines.append('敌人数统计原设置：' + ('不计入' if count else '计入') + '总数；不据此推算本关实际总敌人数。')
    positive, negative = [], []
    for key, name in IMMUNITIES.items():
        setting = values.get(key)
        if setting is True:
            positive.append(name)
        elif setting is False:
            negative.append(name)
    if positive or negative:
        lines += ['', '【控制效果的原始设置】']
        if positive:
            lines.append('明确设有免疫：' + '、'.join(positive) + '。')
        if negative:
            lines.append('明确未设置这项免疫：' + '、'.join(negative) + '。')
        lines.append('这里只说明固定配置；未设置免疫不等于当前一定能控制，阶段、技能及其它效果仍可能阻止控制。')
    if traits['database_level_available'] is False:
        lines.append('此精确等级的数据库记录未取得，只显示本关明确覆盖的设置，不借用其它等级。')
    return lines
