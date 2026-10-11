"""Pinned skill parameters, qualified talents and manually counted outputs."""
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from .catalog import operator_attributes
from .healing_budget import _amount


@lru_cache(maxsize=1)
def supplemental_profiles():
    return json.loads((Path(__file__).parent/'data/supplemental-skills.json').read_text(encoding='utf-8'))


def defaults(operator='char_208_melan'):
    return dict(operator=operator,elite=1,level=55,trust=100,potential=1,skill_rank=7,
                enemy_defense=0,enemy_resistance=0,count=1,missing_hp=500)


def skill_reference(preview):
    if type(preview) is not dict or set(preview)!=set(defaults()):
        raise ValueError('需要operator、elite、level、trust、potential、skill_rank、enemy_defense、enemy_resistance、count、missing_hp。')
    data=supplemental_profiles(); identity=preview['operator']
    if type(identity) is not str or identity not in data['operators']: raise ValueError('干员未接入补充技能参考。')
    profile=data['operators'][identity]
    for key in ('elite','level','potential','skill_rank','count'):
        if type(preview[key]) is not int: raise ValueError(key+'需要整数。')
    if not 1<=preview['skill_rank']<=7: raise ValueError('技能参数等级需要1–7。')
    if not 0<=preview['count']<=1000: raise ValueError('声明次数需要0–1000。')
    trust=_amount(preview['trust'],'信赖',100)
    defense=_amount(preview['enemy_defense'],'敌人防御')
    resistance=_amount(preview['enemy_resistance'],'敌人抗性',100)
    missing_hp=_amount(preview['missing_hp'],'声明生命缺口')
    stats=operator_attributes(identity,preview['elite'],preview['level'],trust,preview['potential'])
    talents=[]; bonuses={}
    for slot in profile['talents'] or []:
        candidates=[t for t in slot['candidates'] if
            (int(t['unlockCondition']['phase'].split('_')[-1]),t['unlockCondition']['level']) <=
            (preview['elite'],preview['level']) and t['requiredPotentialRank']<=preview['potential']-1]
        if candidates:
            talent=max(candidates,key=lambda t:(int(t['unlockCondition']['phase'].split('_')[-1]),t['unlockCondition']['level'],t['requiredPotentialRank']))
            talents.append(deepcopy(talent))
            for item in talent['blackboard']: bonuses[item['key']]=bonuses.get(item['key'],0)+item['value']
    skill=profile['levels'][preview['skill_rank']-1]; bb={item['key']:item['value'] for item in skill['blackboard']}
    attack=stats['attack']*(1+bonuses.get('atk',0))
    hp=stats['hp']*(1+bonuses.get('max_hp',0))
    armor=stats['defense']*(1+bonuses.get('def',0))
    rows=[]
    def add(label,value,unit,countable=False):
        rows.append({'name':label,'value':value,'unit':unit,
                     'declared_total':value*preview['count'] if countable and value is not None else None,
                     'declared_total_applicable':countable})
    kind=profile['kind']
    if kind=='attack_boost':
        skill_attack=stats['attack']*(1+bonuses.get('atk',0)+bb['atk'])
        add('普通攻击力',attack,'攻击力'); add('技能期间攻击力',skill_attack,'攻击力')
        add('技能单次物理伤害',max(skill_attack-defense,skill_attack*.05),'物理伤害',True)
    elif kind=='dp':
        add('单次回费',bb['cost'],'部署费用',True)
        add('部署费用（含已解锁天赋）',stats['deployment_cost']+bonuses.get('cost',0),'部署费用')
    elif kind=='magic_strike':
        add('普通单次法术伤害',attack*(1-min(resistance,95)/100),'法术伤害',True)
        add('技能单次法术伤害',attack*bb['atk_scale']*(1-min(resistance,95)/100),'法术伤害',True)
    elif kind=='double_physical':
        normal=max(attack-defense,attack*.05)
        critical_attack=attack*bonuses.get('atk_scale',1)
        critical=max(critical_attack-defense,critical_attack*.05)
        probability=bonuses.get('prob',0)
        add('普通攻击未触发天赋',normal,'物理伤害',True)
        add('普通攻击触发天赋',critical if probability else None,'物理伤害',bool(probability))
        add('普通单次边际期望',normal*(1-probability)+critical*probability,'期望伤害',True)
        skill_attack=attack*bb['atk_scale']
        hit=max(skill_attack-defense,skill_attack*.05)
        add('二连射单击（未触发天赋）',hit,'物理伤害')
        add('二连射合计（未触发天赋）',hit*bb['times'],'物理伤害',True)
        add('二连射含天赋组合',None if probability else hit*bb['times'],'物理伤害',not bool(probability))
    elif kind=='defense_boost':
        add('普通防御力',armor,'防御力')
        add('技能期间防御力',stats['defense']*(1+bonuses.get('def',0)+bb['def']),'防御力')
    elif kind in ('self_heal','heal_boost'):
        if kind=='self_heal':
            if missing_hp>hp: raise ValueError('自身生命缺口不能超过计算的最大生命。')
            heal=hp*bb['heal_scale'];add('天赋后最大生命',hp,'最大生命')
        else:
            heal=stats['attack']*(1+bonuses.get('atk',0)+bb['atk'])
            add('普通单次治疗',attack,'治疗量')
        add('技能单次治疗',heal,'治疗量',True)
        potential_heal=heal*preview['count'];effective=min(potential_heal,missing_hp)
        add('声明次数有效治疗合计',effective,'治疗量')
        add('声明次数过量治疗合计',potential_heal-effective,'治疗量')
    else: raise ValueError('技能分项尚未实现。')
    return {'preview':deepcopy(preview),'operator_name':profile['name'],'rows':rows,
            'attributes':{'attack':attack,'hp':hp,'defense':armor},'talents':talents,
            'skill_parameter':deepcopy(skill),'source':deepcopy(data['source']),
            'actual_activation_verified':None,'cycle_output':None,
            'notes':['次数为手动声明，不生成技能或攻击时刻；持续时间、技力成本及初始技力仅为原表参数。',
                     '培养按单独预览条件计算；不写入账户或本局。未含藏品、科技、本局增益、目标获取及原生时序。',
                     '精零已培养高等级技能的实际可用性、当前热更新与实机面板仍待核验。',
                     '各行次数分别表示该分项的声明次数，不将普通攻击、技能和期望重复相加。',
                     '治疗合计面对单个声明生命缺口，期间没有新增损失；不推断友方获取、阈值、实际存活或复活资格。',
                     '暴击只计算普通单次分支与边际期望；二连射与天赋的组合层、共享/独立抽样未知，组合输出保留未知。不模拟随机序列或击杀概率。']}


def format_reference(result):
    skill=result['skill_parameter']
    lines=[result['operator_name']+' · 补充技能参考',
           '条件：'+json.dumps(result['preview'],ensure_ascii=False),
           f"原表：{skill['name']}；持续参数{skill['duration']:g}秒，技力成本{skill['spData']['spCost']:g}，初始技力{skill['spData']['initSp']:g}"]
    lines += [r['name']+'：'+('未知' if r['value'] is None else format(r['value'],'.8g'))+' '+r['unit']+(f"；声明次数合计{r['declared_total']:.8g}" if r['declared_total'] is not None else '') for r in result['rows']]
    lines += ['适用天赋：'+json.dumps(result['talents'],ensure_ascii=False),*result['notes'],
              '固定资料：'+json.dumps(result['source'],ensure_ascii=False)]
    return '\n'.join(lines)
