"""River relic lifecycle references under explicit offline owner-tick conditions.

No combat inputs, live sampling or permanent character attributes are added.
The rational clock is a conditional reference, never a reconstruction of the
game's fixed-point delta time, creation snapshot or same-frame event order.
"""
from copy import deepcopy
from fractions import Fraction
import math


RELIC_ID='rogue_6_relic_fight_22'
SOURCE={
    'scope':'installed_native_baseline_and_pinned_parameters',
    'game_data_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
    'topic_url':'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/roguelike_topic_table.json',
    'game_dll_sha256':'6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce',
    'metadata_sha256':'ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118',
    'contract':'p1-native-runtime-054/river-contract-055.json',
    'contract_sha256':'56b3328926d6b9ba1ddff4358764b45efb1c77121e1c1af7d1f3b4105e2af268',
    'proof_seal':'p1-native-runtime-054/river-recipient-proof-seal-055.json',
    'current_hotfix_equivalence_proven':False}

_BRANCHES={
    'dark':{'name':'凋亡','burst_damage_scale':2.5,
        'modifiers':{'enemy_atk_final_scaler':.7},'derived':True,
        'lifetime':'该次凋亡爆发结束时清除派生加成。',
        'override':'默认同键属性组；不将多个同键攻击减算盲目相乘。',
        'raw_pulse_damage':None,'damage_type':None,'period_seconds':None,
        'wait_first':None,'maximum_trigger_count':None},
    'fire':{'name':'灼燃','burst_damage_scale':3.8,
        'modifiers':{'enemy_mr_addition':-20},'derived':True,
        'lifetime':'该次灼燃爆发结束时清除额外法抗减算。',
        'override':'默认同键属性组；不将多个同键法抗减算盲目累加。',
        'raw_pulse_damage':None,'damage_type':None,'period_seconds':None,
        'wait_first':None,'maximum_trigger_count':None},
    'sanity':{'name':'神经','burst_damage_scale':2.,'modifiers':{},'derived':True,
        'lifetime':'该次神经爆发结束时清除派生持续伤害。',
        'override':'默认同键派生效果；不将未知实例数量当作额外叠加伤害。',
        'raw_pulse_damage':1000.,'damage_type':'elemental','period_seconds':1.,
        'wait_first':True,'maximum_trigger_count':None,
        'pulse_condition':'每一次触发时，目标必须仍有 palsy[stack]；不能以爆发次数替代此条件。'},
    'water':{'name':'侵蚀','burst_damage_scale':1.,
        'scale_reason':'原黑板没有 damage_scale，原生 DamageScale 默认读取 1。',
        'modifiers':{'enemy_def_addition':-120},'derived':False,
        'lifetime':'独立无限寿命子效果；十次伤害结束后防御减算继续，元素爆发结束不移除它。',
        'override':'禁覆盖，重复创建的子实例独立；每个有效实例各提供额外防御 -120。',
        'raw_pulse_damage':1500.,'damage_type':'physical','period_seconds':.03,
        'wait_first':False,'maximum_trigger_count':10,
        'pulse_condition':'下一次符合条件的目标 Tick 最多执行一次；仅当创建早于该 Tick 的效果快照才可能同帧首跳。'}}
_ALIASES={branch['name']:key for key,branch in _BRANCHES.items()}
_LIMITS=[
    '创建帧及同帧创建、目标 Tick、爆发结束顺序不能从培养或藏品画面唯一恢复。',
    '条件逐跳参考使用调用方明确给出的目标 dt；不是原生 Q32 时间或实际战斗帧轨迹。',
    '未核验目标麻痹状态时，神经追加伤害保留未知。',
    '无来源伤害仍会经过目标减伤、伤害修饰或取消；原始量不等于实际生命损失。',
    '六个完整模板没有冷却加速动作，不另加河谷独立冷却加速。',
    '不改变常驻干员面板，不新增战斗人工输入，不采集站位或操作游戏。']


def _element(value):
    if not isinstance(value,str):raise ValueError('请选择凋亡、灼燃、神经或侵蚀。')
    key=_ALIASES.get(value,value)
    if key not in _BRANCHES:raise ValueError('请选择凋亡、灼燃、神经或侵蚀。')
    return key


def reference(element=None):
    """Copy-safe user-visible facts; omit any invented absolute pulse schedule."""
    branches=_BRANCHES if element is None else {_element(element):_BRANCHES[_element(element)]}
    return {'relic_id':RELIC_ID,'name':'河谷祭祈','scope':'offline_conditional_reference',
        'branches':deepcopy(branches),'source':deepcopy(SOURCE),'limitations':_LIMITS[:],
        'permanent_panel_effect':False,'live_combat_inputs_added':False,
        'pulse_damage_is_before_target_mitigation':True,
        'maximum_triggers_per_owner_tick':1,'catch_up_loop':False,
        'native_fp_equivalence_proven':False,'absolute_creation_phase_known':False}


def _dt(value):
    if isinstance(value,bool) or not isinstance(value,(int,float,Fraction)):
        raise ValueError('局外条件时钟需要正的有限时间步长。')
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('时间步长需要有限数值。')
    value=Fraction(str(value)) if isinstance(value,float) else Fraction(value)
    if value<=0:raise ValueError('时间步长需要大于零；暂停和不执行目标 Tick 不应传入。')
    return value


class RiverInstance:
    """One explicitly created child in a supplied rational owner-tick scenario.

    Call break_finished before or after tick to express the established event
    order of that scenario. No order is silently chosen for actual gameplay.
    Different water objects retain their independent damage and DEF state.
    """
    def __init__(self,element):
        self.element=_element(element);self._branch=_BRANCHES[self.element]
        period=self._branch['period_seconds']
        self._period=Fraction(str(period)) if period is not None else None
        self._remaining=self._period if self._branch['wait_first'] else Fraction(0)
        self._count=self._branch['maximum_trigger_count']
        self._elapsed=Fraction(0);self._finished=False;self._attempts=0;self._events=[]

    def break_finished(self):
        if self._branch['derived']:self._finished=True

    def tick(self,dt,*,palsy=None):
        """Return at most one conditional pulse, with unknown damage kept null.

        Rational deadline comparison has no fabricated epsilon. This function
        is explicitly not the native fixed-point timer. A missing palsy fact
        never becomes a fabricated hit or zero HP loss.
        """
        dt=_dt(dt)
        if palsy is not None and type(palsy) is not bool:raise ValueError('麻痹存在性应为已知布尔值或未知。')
        self._elapsed+=dt
        if self._finished or self._period is None or self._count==0:return None
        self._remaining-=dt
        if self._remaining>0:return None
        self._remaining+=self._period;self._attempts+=1
        if self._count is not None:self._count-=1
        condition=palsy if self.element=='sanity' else True
        raw=None if condition is None else (self._branch['raw_pulse_damage'] if condition else 0.)
        event={'tick':self._attempts,'relative_seconds':float(self._elapsed),
            'relative_time_exact':str(self._elapsed),'condition_confirmed':condition,
            'event_kind':'conditional_trigger_attempt',
            'raw_damage':raw,'damage_type':self._branch['damage_type'],
            'damage_before_target_mitigation':True,'ignore_for_sp':True,
            'native_fp_equivalence_proven':False}
        self._events.append(event)
        return deepcopy(event)

    def snapshot(self):
        events=deepcopy(self._events);unknown=any(e['raw_damage'] is None for e in events)
        known=sum(e['raw_damage'] for e in events if e['raw_damage'] is not None)
        return {'element':self.element,'name':self._branch['name'],
            'elapsed_seconds':float(self._elapsed),'elapsed_exact':str(self._elapsed),
            'events':events,'trigger_attempts':self._attempts,'remaining_trigger_count':self._count,
            'pulse_actions_exhausted':self._count==0,'finished':self._finished,
            'active_modifiers':{} if self._finished else deepcopy(self._branch['modifiers']),
            'known_raw_damage_subtotal':known,'conditional_raw_damage_total':None if unknown else known,
            'actual_hp_loss':None,'condition_complete':not unknown,
            'condition_scope':'recorded_trigger_attempts_only',
            'clock':'explicit_rational_owner_dt_reference','native_fp_equivalence_proven':False,
            'limitations':_LIMITS[:],'source':deepcopy(SOURCE)}
