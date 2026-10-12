"""Compiled EnemyDatabase SP-field replacement, separate from runtime skill clocks."""
from copy import deepcopy
from functools import lru_cache
import json,math
from pathlib import Path

@lru_cache(maxsize=1)
def inheritance_rules():
    return json.loads((Path(__file__).with_name('data')/'enemy-sp-inheritance-reference.json').read_text(encoding='utf8'))

def compiled_sp_reference(reference):
    rules=inheritance_rules()
    result={'scope':rules['scope'],'state':'unavailable_exact_database_level',
        'configuration':None,'applied_source':None,'source_chain':[],
        'compiled_rule_verified':True,'database_exact_level_available':reference['exact_requested_level_present'],
        'initialization_reference':{'state':'unavailable_compiled_configuration','path':None,'scalar_assignment_reference':None,
            'scope':rules['rules']['initialization']['scope'],'current_hooks_bound':False,
            'required_conditions':['当前各初始化入口、构造后置和上限读取热更新钩子均未接管。',
                '仅限已证基包路径，实际控制器、技能附着和时钟仍未核验。']},
        'current_runtime_controller':None,'first_activation_seconds':None,'complete_cycle_seconds':None,
        'native_evidence':deepcopy(rules['native_evidence']),
        'limits':['只解析固定来源中的基包技力配置整记录继承，不合并技能或天赋黑板。',
            'null不覆盖前项；非null技力配置整体替换，不按字段拼接。',
            '已证无热更新钩子的默认/显式初始化来源；实际默认控制器、触发、首次发动、技能回转、关卡别名构建和当前热更新仍待核验。']}
    if not result['database_exact_level_available']:return result
    records=[('database_level',d['level'],d) for d in reference['definitions'] if d['level']<=reference['requested_level']]
    records.append(('stage_override',reference['requested_level'],reference['stage_overrides']))
    configuration=None;source=None
    for origin,level,record in records:
        value=record.get('spData')
        row={'origin':origin,'level':level,'state':'absent' if 'spData' not in record else 'null' if value is None else 'whole_record_write'}
        if value is not None:
            if not _valid_configuration(value):
                result.update(state='unsupported_source_shape',configuration=None,applied_source=None)
                row['state']='unsupported_source_shape';result['source_chain'].append(row)
                return result
            configuration=deepcopy(value);source={'origin':origin,'level':level}
        result['source_chain'].append(row)
    result.update(state='compiled_configuration_available' if configuration is not None else 'no_explicit_sp_configuration',
        configuration=configuration,applied_source=source)
    initialization=result['initialization_reference'];rule=rules['rules']['initialization']
    if configuration is None:
        initialization.update(state='conditional_baseline_available',path='shared_default',
            scalar_assignment_reference=deepcopy(rule['default_scalar_assignments']))
    elif configuration['spType'] not in rule['sp_types']:
        initialization.update(state='unsupported_sp_type')
    else:
        scalars={target:configuration[source] for source,target in rule['explicit_field_mapping'].items()}
        scalars.update(maxChargeTime=rule['explicit_max_charge_time'],maxSp=configuration['maxSp'])
        initialization.update(state='conditional_baseline_available',path='explicit_record_conversion',
            scalar_assignment_reference=scalars)
    return result

def _valid_configuration(value):
    if not isinstance(value,dict) or set(value)!={'spType','maxSp','initSp','increment'}:return False
    return isinstance(value['spType'],str) and bool(value['spType']) and type(value['maxSp']) is int and type(value['initSp']) is int and type(value['increment']) in (int,float) and math.isfinite(value['increment'])
