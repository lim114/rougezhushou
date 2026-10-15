"""Bound initial shared-SP gate and explicitly declared accepted-request budget."""
from copy import deepcopy
import math
from .deployment import _fp,_single,_Q32

SOURCE='research/p3-enemy-skill-resource-gates-current/receipt.json'
SCOPE='gated_baseline_sp_requests'

def _int32(value):return type(value) is int and -(1<<31)<=value<(1<<31)
def _as_float(raw):return _single(_single(raw)*_single(1/_Q32))

def _plan(value):
    if value is None:return None
    if not isinstance(value,dict) or set(value)-{'scope','requests','starting_sp','starting_sp_raw'}:
        raise ValueError('敌人共享技力声明需为受支持对象，不能加入未核验回复/时钟。')
    if value.get('scope')!=SCOPE:
        raise ValueError('共享技力预算必须明确声明：基础路径接受的技力请求。')
    requests=value.get('requests')
    if not isinstance(requests,list) or len(requests)>256 or any(not isinstance(k,str) or not k for k in requests):
        raise ValueError('共享技力请求需为至多256个非空招式标识。')
    if 'starting_sp' in value and 'starting_sp_raw' in value:
        raise ValueError('声明技力与原生FP原值只能选择一项。')
    result=deepcopy(value)
    if 'starting_sp_raw' in result:
        raw=result['starting_sp_raw']
        if type(raw) is not int or not -(1<<63)<=raw<(1<<63):raise ValueError('声明FP技力需要有符号64位整数。')
    elif 'starting_sp' in result:
        number=result['starting_sp']
        try:valid=type(number) in (int,float) and math.isfinite(number)
        except OverflowError:valid=False
        if not valid:raise ValueError('声明技力需要有限数值。')
        try:raw=_fp(number)
        except ValueError:raise ValueError('声明技力超出原生FP范围。') from None
        result['starting_sp_raw']=raw
    return result

def initial_skill_resource_reference(reference,resource_plan=None):
    plan=_plan(resource_plan)
    result={'scope':'conditional_bound_shared_sp_initialization_and_numeric_gate','state':'unavailable_source',
        'initial_pool':None,'skills':[],'declared_request_budget':None,'declaration':deepcopy(plan),
        'native_evidence':SOURCE,'actual_controller_or_attachment_verified':False,
        'full_availability':None,'first_activation_seconds':None,'complete_cycle_seconds':None,
        'current_hotfix_equivalence_proven':False,
        'conditions':['使用已证基包数据及初始化分支，所列招式通过基础AssignData绑定到同一敌人实体。',
            '初始化点没有未证脚本、控制器或额外技力来源改动共享池、上限及技能费用。',
            '预算仅表示明确声明的请求按原费用被接受；不证明技能实际触发、冷却完成、动画结束或有可用目标。']}
    config=reference.get('compiled_configuration') or {};sp=reference.get('compiled_sp_reference') or {}
    init=sp.get('initialization_reference') or {}
    if init.get('state')!='conditional_baseline_available':return result
    scalars=init.get('scalar_assignment_reference') or {};maximum=scalars.get('maxSp');initial=scalars.get('initSp')
    if not _int32(maximum) or maximum<0 or not _int32(initial):
        result['state']='unsupported_source_pool';return result
    # Entity.Init min(init,max) occurs in signed integer space before float/FP;
    # it does not clamp this initialization to zero. Later setters clamp0..max.
    selected=min(initial,maximum)
    try:initial_raw=_fp(selected)
    except ValueError:result['state']='unsupported_native_pool_conversion';return result
    capacity_raw=maximum*_Q32
    if initial_raw>capacity_raw:
        result['state']='unsupported_initial_rounding_at_capacity';return result
    pool={'source_init_sp':initial,'source_max_sp':maximum,'initial_integer_after_upper_cap':selected,
        'initial_sp_raw':initial_raw,'initial_sp_reference':_as_float(initial_raw),
        'capacity_sp_raw':capacity_raw,'initial_lower_zero_clamp_applied':False,
        'origin':init.get('path'),'actual_current_sp':None,'actual_current_max_sp':None}
    if config.get('state')!='compiled_configuration_available':
        result.update(state='conditional_initial_pool_only_skill_baseline_unknown',initial_pool=pool)
        return result
    rows=config.get('configuration',{}).get('skills') or [];skills=[];by_key={}
    for row in rows:
        key=row.get('prefabKey');cost=row.get('spCost');cooldown=row.get('initCooldown')
        if not isinstance(key,str) or not key or key in by_key or not _int32(cost):
            result['state']='unsupported_source_skill';return result
        try:
            period_raw=max(0,_fp(cooldown));period=_as_float(period_raw);period_state='conditional_data_branch_available'
        except (ValueError,OverflowError):
            period=None;period_raw=None;period_state='unsupported_native_cooldown_conversion'
        item={'prefab_key':key,'source_sp_cost':cost,'cost_fp_raw':cost*_Q32,
            'initial_sp_numeric_gate_pass':initial_raw>=cost*_Q32,
            'gate_comparator':'signed_FP_GE_exact_without_epsilon',
            'positive_cost_request_sp_delta':-cost if cost>0 else 0,
            'nonpositive_cost_request_is_no_op':cost<=0,
            'default_constructor_init_cooldown_override':-1,
            'source_init_cooldown_period_reference':period,
            'source_init_cooldown_period_fp_raw':period_raw,
            'source_init_cooldown_reference_state':period_state,
            'cooldown_wait_first_period':True,'actual_prefab_init_cooldown_override':None,
            'override_rule':'prefab override >=0, including0, replaces source initial cooldown; actual override unknown',
            'full_availability':None,'actual_attachment_verified':False,'actual_cast_count':None}
        skills.append(item);by_key[key]=item
    result.update(state='conditional_initial_numeric_gates_available',initial_pool=pool,skills=skills)
    if plan is None:return result
    starting=plan.get('starting_sp_raw',initial_raw)
    if starting>capacity_raw:raise ValueError('声明技力超出已绑定基础共享池上限，不能借用未核验上限覆盖。')
    current=starting;events=[]
    for index,key in enumerate(plan['requests']):
        if key not in by_key:raise ValueError('预算请求必须精确绑定已解析的本敌人招式标识。')
        item=by_key[key];cost=item['source_sp_cost'];passed=current>=item['cost_fp_raw'];before=current
        if passed and cost>0:current=min(capacity_raw,max(0,current-cost*_Q32))
        events.append({'ordinal':index+1,'prefab_key':key,'cost':cost,'before_sp_raw':before,
            'sp_numeric_gate_pass':passed,'conditional_baseline_request_applied':passed and cost>0,
            'nonpositive_cost_emits_no_sp_request':cost<=0,
            'requested_delta':-cost if passed and cost>0 else 0,'after_sp_raw':current,
            'after_sp_reference':_as_float(current),'actual_cast_succeeded':None})
    result['declared_request_budget']={'scope':SCOPE,'starting_sp_raw':starting,
        'starting_sp_reference':_as_float(starting),'events':events,'remaining_sp_raw':current,
        'remaining_sp_reference':_as_float(current),'shared_pool':True,
        'actual_accepted_requests':None,'actual_cast_count':None,'actual_time_seconds':None,
        'no_regeneration_or_other_effects_added':True}
    return result

def skill_resource_text(result,technical=False):
    if result['state']=='conditional_initial_pool_only_skill_baseline_unknown':
        pool=result['initial_pool']
        return ('【技力池条件分项】\n基础初始化点技力：'+f"{pool['initial_sp_reference']:g}"+' / '+str(pool['source_max_sp'])+
            '\n招式构造基线仍未知；不借用数据库费用或宣称可施放。实际控制器和当前池未知。')
    if result['state']!='conditional_initial_numeric_gates_available':
        return '技能技力数值门：来源或独立构造基线未闭合，不能借用数据库/默认共享池。'
    pool=result['initial_pool'];rows=result['skills']
    if not rows and result['declared_request_budget'] is None:return ''
    lines=['【技能技力条件分项】',
        '基础初始化点共享技力：'+f"{pool['initial_sp_reference']:g}"+' / '+str(pool['source_max_sp']),
        '这里只检视独立技力数值门；实际附着、其他可用门和首次发动时刻仍未知。']
    for i,row in enumerate(rows,1):
        gate='达到费用' if row['initial_sp_numeric_gate_pass'] else '费用不足'
        delta='无' if row['nonpositive_cost_request_is_no_op'] else str(-row['positive_cost_request_sp_delta'])
        lines.append(f"招式 {i} · 费用 {row['source_sp_cost']}：初始化点{gate}；请求扣除：{delta}；完整可施放未知。")
    budget=result['declared_request_budget']
    if budget is not None:
        lines += ['【声明的共享技力请求预算】','请求之间共用一个池，未加入回复、时间或实际施放。']
        for row in budget['events']:
            lines.append(f"第{row['ordinal']}项："+('技力数值门通过' if row['sp_numeric_gate_pass'] else '技力数值门不通过')+
                f"；余技力 {row['after_sp_reference']:g}；实际施放未知。")
    if technical:
        lines += ['原招式费用及冷却初始化分支：'+str(rows),
            '预制体初始冷却覆盖非负（包括0）时替代原字段；实际覆盖未知，不由初始冷却0推出生即施放。',
            '技力数值GE门是有符号FP精确比较，不复用生命比率的容差比较。',
            '来源：'+SOURCE]
    return '\n'.join(lines)
