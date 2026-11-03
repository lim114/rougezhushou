"""Conditional gates from an exact fixed prefab, never actual controller state."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json,math
from .deployment import _fp,_Q32
from .enemy_skill_resources import _as_float

SOURCE='research/p3-enemy-prefab-skill-gates-current/receipt.json'
SCOPE='gated_baseline_skill_starts'

@lru_cache(maxsize=1)
def prefab_data():return json.loads((Path(__file__).with_name('data')/'enemy-prefab-skill-gates.json').read_text(encoding='utf-8'))

def _int32(value):return type(value) is int and -(1<<31)<=value<(1<<31)
def _normalized(value):
    # Both native assignment sides call current-culture ToLower, not invariant.
    # Only fixed ASCII names without capital I use this stable subset; do not
    # turn Python Unicode lower/casefold into the unknown native culture.
    if not isinstance(value,str) or not value or not value.isascii() or 'I' in value:return None
    return value.lower()

def prefab_key_reference(stage_id,enemy_id,level,reference):
    from .enemy_panel import panel_data
    binding=panel_data()['bindings'].get(stage_id,{}).get(enemy_id+'@'+str(level),{})
    path=reference.get('construction_reference') or {};key=None;known=False;chain=[]
    if not path.get('compiled_result_available'):return {'key':None,'known':False,'chain':[]}
    if path['mode']=='database':
        records=prefab_data()['database_prefab_keys'].get(enemy_id,{})
        for n,row in sorted(records.items(),key=lambda p:int(p[0])):
            if int(n)>level:continue
            if type(row.get('defined')) is not bool:return {'key':None,'known':False,'chain':chain}
            if row['defined']:key=deepcopy(row.get('value'));known=True
            chain.append({'origin':'database_level','level':int(n),'prefab_key_defined':row['defined'],
                'value':deepcopy(row.get('value'))})
    writes=binding.get('identity_overrides') or {}
    if 'prefabKey' in writes:
        key=deepcopy(writes['prefabKey']);known=True
        chain.append({'origin':'stage_override','prefab_key_defined':True,'value':key})
    return {'key':key,'known':known,'chain':chain,'alias_used_as_prefab_key':False,
        'actual_resource_load_verified':False,'current_hotfix_equivalence_proven':False}

def _plan(value):
    if value is None:return None
    if not isinstance(value,dict) or set(value)-{'scope','requests','starting_counts','starting_sp','starting_sp_raw'}:
        raise ValueError('预制体技能预算需要受支持的声明；不接受实际时钟或回复输入。')
    if value.get('scope')!=SCOPE:raise ValueError('需要明确声明基础技能启动被接受且其他门已满足的条件。')
    requests=value.get('requests');counts=value.get('starting_counts',{})
    def valid_request(item):
        return (isinstance(item,str) and bool(item)) or (isinstance(item,dict) and
            set(item)=={'skill','ability_start_success'} and isinstance(item['skill'],str) and bool(item['skill']) and
            type(item['ability_start_success']) is bool)
    if not isinstance(requests,list) or len(requests)>256 or any(not valid_request(k) for k in requests):
        raise ValueError('技能启动请求需要至多256个明确招式标识。')
    if not isinstance(counts,dict) or any(not isinstance(k,str) or not k or not _int32(v) or v<0 for k,v in counts.items()):
        raise ValueError('声明的启动次数需为非负有符号32位整数。')
    if 'starting_sp' in value and 'starting_sp_raw' in value:raise ValueError('声明技力与FP原值不能同时输入。')
    result=deepcopy(value)
    if 'starting_sp_raw' in result:
        if type(result['starting_sp_raw']) is not int or not -(1<<63)<=result['starting_sp_raw']<(1<<63):
            raise ValueError('声明FP技力需为有符号64位整数。')
    elif 'starting_sp' in result:
        number=result['starting_sp']
        try:valid=type(number) in (int,float) and math.isfinite(number)
        except OverflowError:valid=False
        if not valid:raise ValueError('声明技力需要有限数值。')
        result['starting_sp_raw']=_fp(number)
    return result

def prefab_skill_reference(stage_id,enemy_id,level,reference,prefab_gate_plan=None):
    plan=_plan(prefab_gate_plan);identity=prefab_key_reference(stage_id,enemy_id,level,reference)
    result={'state':'unavailable_fixed_prefab','scope':'conditional_exact_prefab_baseline_skill_gates',
        'prefab_key_reference':identity,'skills':[],'declared_start_budget':None,'declaration':deepcopy(plan),
        'native_evidence':SOURCE,'actual_attachment_verified':False,'actual_current_controller_verified':False,
        'current_hotfix_equivalence_proven':False,'full_availability':None,
        'actual_cast_count':None,'first_activation_seconds':None,'complete_cycle_seconds':None,
        'conditions':['基础资源请求使用已绑定的prefabKey，不使用关卡别名。',
            '当前实际使用的是所列同身份预制体和基础EnemySkill入口，无脚本、子类或热更新覆盖。',
            '声明预算只在其他门、目标、冷却、能力启动和技力请求都按声明成功时更新共享池与启动计数；不推算实际施放。']}
    if not identity['known'] or not isinstance(identity['key'],str):return result
    prefab=prefab_data()['prefabs'].get(identity['key'])
    if prefab is None:return result
    result['prefab_source']=deepcopy({k:v for k,v in prefab.items() if k!='skills'})
    config=reference.get('compiled_configuration') or {}
    if config.get('state')!='compiled_configuration_available':
        result['state']='unavailable_source_skill_configuration';return result
    rows=config['configuration'].get('skills') or [];by_name={}
    normalized_source_keys=[_normalized(row.get('prefabKey')) for row in rows]
    known_source_keys=[key for key in normalized_source_keys if key is not None]
    if len(set(known_source_keys))!=len(known_source_keys):
        # The native assignment dictionary collapses normalized identities;
        # do not give one physical component two independent usage counters.
        result['state']='ambiguous_assignment_source_keys';return result
    for row in prefab['skills']:
        normalized=_normalized(row['key'])
        if normalized is not None:by_name.setdefault(normalized,[]).append(row)
    source_resources=reference.get('initial_skill_resources') or {}
    resource_rows={r['prefab_key']:r for r in source_resources.get('skills',[])}
    skills=[];by_key={}
    for data in rows:
        key=data.get('prefabKey');matches=by_name.get(_normalized(key),[])
        if len(matches)!=1:
            skills.append({'key':key,'state':'unbound_component_or_name_culture','full_availability':None});continue
        component=deepcopy(matches[0]);maximum=component['max_trigger_time'];override=component['initial_cooldown_override']
        if not _int32(maximum) or not _int32(override):
            skills.append({'key':key,'state':'unsupported_prefab_integer','full_availability':None});continue
        period_value=override if override>=0 else data.get('initCooldown')
        try:period_raw=max(0,_fp(period_value));period=_as_float(period_raw)
        except ValueError:period_raw=None;period=None
        row={'key':key,'state':'conditional_prefab_gates_available','component':component,
            'name_match':'both_native_sides_current_culture_ToLower_supported_ASCII_subset',
            'initial_trigger_count_reference':0,'current_trigger_count':None,
            'maximum_trigger_time_reference':maximum,'unlimited_by_this_counter':maximum<0,
            'initial_count_gate_pass':maximum<0 or 0<maximum,
            'initial_cooldown_override_reference':override,
            'initial_cooldown_branch':'prefab_nonnegative_override' if override>=0 else 'source_data_negative_override',
            'initial_cooldown_period_fp_raw':period_raw,'initial_cooldown_period_reference':period,
            'autonomous_target_reference':False if component['trigger_class']=='Torappu.Battle.NeverTrigger' else None,
            'actual_manual_or_scripted_trigger':None,'full_availability':None,
            'actual_cast_count':None,'first_activation_seconds':None,'complete_cycle_seconds':None,
            'sp_numeric_reference':deepcopy(resource_rows.get(key))}
        skills.append(row);by_key[key]=row
    result.update(state='conditional_prefab_gates_available',skills=skills)
    if plan is None:return result
    pool=source_resources.get('initial_pool')
    request_keys=[r if isinstance(r,str) else r['skill'] for r in plan['requests']]
    if pool is None or any(k not in by_key for k in [*request_keys,*plan.get('starting_counts',{})]):
        raise ValueError('启动预算需明确已绑定的技能组件、技能费用和共享池；不能填默认值。')
    current=plan.get('starting_sp_raw',pool['initial_sp_raw']);capacity=pool['capacity_sp_raw']
    if current>capacity:raise ValueError('声明技力超出已绑定共享池容量。')
    counts={key:plan.get('starting_counts',{}).get(key,0) for key in by_key};events=[]
    for i,item in enumerate(plan['requests'],1):
        key=item if isinstance(item,str) else item['skill']
        ability_success=True if isinstance(item,str) else item['ability_start_success']
        row=by_key[key];resource=row['sp_numeric_reference']
        if resource is None:raise ValueError('该技能费用尚未闭合，不能用预制体名字补齐费用。')
        count=counts[key];maximum=row['maximum_trigger_time_reference'];count_gate=maximum<0 or count<maximum
        sp_gate=current>=resource['cost_fp_raw'];gates_pass=count_gate and sp_gate;before=current
        accepted=gates_pass and ability_success
        if gates_pass and resource['source_sp_cost']>0:current=min(capacity,max(0,current-resource['cost_fp_raw']))
        if accepted:
            if count==(1<<31)-1:raise ValueError('声明次数触及原生计数溢出，预算未覆盖此范围。')
            counts[key]+=1
        events.append({'ordinal':i,'key':key,'count_gate_pass':count_gate,'sp_numeric_gate_pass':sp_gate,
            'conditional_start_accepted':accepted,'before_count':count,'after_count':counts[key],
            'declared_ability_start_success':ability_success,
            'conditional_positive_sp_request_before_ability_result':gates_pass and resource['source_sp_cost']>0,
            'immediate_refund_in_baseline_failure_branch':False,
            'before_sp_raw':before,'after_sp_raw':current,'after_sp_reference':_as_float(current),
            'actual_cast_succeeded':None})
    result['declared_start_budget']={'scope':SCOPE,'events':events,'remaining_sp_raw':current,
        'remaining_sp_reference':_as_float(current),'ending_count_references':counts,
        'shared_pool':True,'actual_cast_count':None,'actual_accepted_starts':None,'actual_time_seconds':None,
        'recovery_or_timing_added':False,'all_other_gates_assumed_ready_only_as_explicit_declaration':True}
    return result

def prefab_skill_text(result,technical=False):
    if result['state']!='conditional_prefab_gates_available':
        return ('预制体具体技能门：未闭合；不使用别名/名字相似或数据库ID代替资源标识。' if technical else '')
    if not result['skills']:return ''
    lines=['【固定预制体技能条件】','这些是同身份基包组件分项；实际附着、完整可施放及所有发动时钟仍未知。']
    for i,row in enumerate(result['skills'],1):
        if row['state']!='conditional_prefab_gates_available':lines.append(f'招式{i}：具体组件或名称映射未知。');continue
        limit='此计数门不设上限' if row['unlimited_by_this_counter'] else '启动次数上限 '+str(row['maximum_trigger_time_reference'])
        gate='次数门通过' if row['initial_count_gate_pass'] else '次数门不通过'
        lines.append(f'招式{i}：{limit}；基础初始化计数0，{gate}。')
        if row['autonomous_target_reference'] is False:
            lines.append('自动目标分支不提供目标；其他能力或脚本是否调用仍未知，不等于不能施放。')
    budget=result['declared_start_budget']
    if budget is not None:
        lines.append('【声明的启动预算】共享技力与各招式计数分别跟踪，假定其他门就绪；实际施放未知。')
        for e in budget['events']:
            lines.append(f"第{e['ordinal']}项："+('条件启动接受' if e['conditional_start_accepted'] else '条件门不通过')+
                f"；次数门 {'通过' if e['count_gate_pass'] else '不通过'}；技力门 {'通过' if e['sp_numeric_gate_pass'] else '不通过'}；余技力 {e['after_sp_reference']:g}。")
            if e['conditional_positive_sp_request_before_ability_result'] and not e['declared_ability_start_success']:
                lines.append('声明能力启动失败：先前的基础扣费请求保留，本分支不立即返还；启动计数不增加。')
    if technical:
        lines.extend(['资源标识来源：'+str(result['prefab_key_reference']),'组件、具体初始冷却与触发器：'+str(result['skills']),
            '初始冷却是组件分支参考，不等于出生/首次发动时刻；实际热更新、模式和控制器未知。','来源：'+SOURCE])
    return '\n'.join(lines)
