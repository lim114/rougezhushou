"""Fixed enemy skill/blackboard construction, separate from live controllers."""
from copy import deepcopy
from functools import lru_cache
import json,math
from pathlib import Path

@lru_cache(maxsize=1)
def construction_rules():
    return json.loads((Path(__file__).with_name('data')/'enemy-configuration-construction.json').read_text(encoding='utf8'))

def _board(value):
    if value is None:return True
    if not isinstance(value,list):return False
    for pair in value:
        if not isinstance(pair,dict) or set(pair)!={'key','value','valueStr'}:return False
        if not isinstance(pair['key'],str) or not pair['key']:return False
        if pair['valueStr'] is not None and not isinstance(pair['valueStr'],str):return False
        if type(pair['value']) not in (int,float) or not math.isfinite(pair['value']):return False
    return True

def _skills(value):
    if value is None:return True
    if not isinstance(value,list):return False
    for skill in value:
        if not isinstance(skill,dict) or set(skill)!={'prefabKey','priority','cooldown','initCooldown','spCost','blackboard'}:return False
        if not isinstance(skill['prefabKey'],str) or not skill['prefabKey']:return False
        if type(skill['priority']) is not int or type(skill['spCost']) is not int:return False
        if any(type(skill[k]) not in (int,float) or not math.isfinite(skill[k]) for k in ('cooldown','initCooldown')):return False
        if not _board(skill['blackboard']):return False
    return True

def _apply_board(current,delta):
    """Only the actual native helper reconstructs the incoming DataPair."""
    result=deepcopy(current)
    for pair in delta or []:
        result=[p for p in result if p['key']!=pair['key']]
        incoming=deepcopy(pair)
        if incoming['valueStr']:
            incoming['value']=0
        else:incoming['valueStr']=None
        result.append(incoming)
    return result

def compiled_configuration(reference):
    rules=construction_rules()
    result={'scope':rules['scope'],'state':'unavailable_exact_database_level',
        'configuration':None,'source_chain':[],
        'compiled_inheritance_resolved':False,
        'database_exact_level_available':reference['exact_requested_level_present'],
        'current_runtime_controller':None,'first_activation_seconds':None,
        'complete_cycle_seconds':None,'effective_skill_damage':None,
        'native_evidence':deepcopy(rules['native_evidence']),
        'limits':list(rules['limits'])}
    from .enemy_reference_construction import configuration_path
    path=configuration_path(reference);result['construction_reference']=path
    if not path['compiled_result_available']:return result
    if path['mode']=='stage_constructor':
        result.update(state='constructor_configuration_baseline_unknown',configuration=None,
            source_written_configuration=deepcopy(reference['stage_overrides']),
            source_chain=[{'origin':'stage_override','level':reference['requested_level'],
                'state':'constructor_pointer_baseline_unresolved_no_database_inheritance'}])
        return result
    skills=[];talents=None
    records=[('database_level',d['level'],d) for d in reference['definitions'] if d['level']<=reference['requested_level']]
    records.append(('stage_override',reference['requested_level'],reference['stage_overrides']))
    for origin,level,record in records:
        row={'origin':origin,'level':level,'skill_writes':[],
             'skills_state':'absent' if 'skills' not in record else 'null' if record['skills'] is None else 'list',
             'talents_state':'absent' if 'talentBlackboard' not in record else 'null' if record['talentBlackboard'] is None else 'list'}
        board=record.get('talentBlackboard');delta=record.get('skills')
        if not _board(board) or not _skills(delta):
            row['unsupported_source_shape']=True;result['source_chain'].append(row)
            result['state']='unsupported_source_shape';return result
        if board:
            if talents is None:talents=[]
            talents=_apply_board(talents,board)
        for skill in delta or []:
            previous=next((s for s in skills if s['prefabKey']==skill['prefabKey']),None)
            incoming=deepcopy(skill)
            merge=previous is not None and bool(skill['blackboard'])
            if merge:
                incoming['blackboard']=_apply_board(previous['blackboard'] or [],skill['blackboard'])
            skills=[s for s in skills if s['prefabKey']!=skill['prefabKey']]
            skills.append(incoming)
            row['skill_writes'].append({'prefab_key':skill['prefabKey'],
                'path':'clone_delta_merge_previous_board' if merge else 'whole_delta_record',
                'scalar_source':'incoming_delta_record','previous_match_found':previous is not None})
        result['source_chain'].append(row)
    result.update(state='compiled_configuration_available',compiled_inheritance_resolved=True,
                  configuration={'skills':deepcopy(skills) if skills else None,'talentBlackboard':deepcopy(talents)})
    return result

def construction_text(result,technical=False):
    if result['state']=='unavailable_exact_database_level':
        return '基包招式与机制参数：精确等级不可用；未借用旧等级或默认/别名构建结果。'
    if result['state']=='unsupported_source_shape':
        return '基包招式与机制参数：存在未覆盖的来源格式，完整配置参考保持未知。'
    if result['state']=='constructor_configuration_baseline_unknown':
        return '关卡独立构造的原招式覆写已保留；构造器未写空指针的分配基线仍未闭合，完整配置未知，未继承数据库条目。'
    config=result['configuration'];skills=config['skills'] or [];talents=config['talentBlackboard'] or []
    lines=[f'基包配置分项：{len(skills)}条招式、{len(talents)}项机制参数已按来源构建规则解析。',
        '此处解析的是固定配置；未推定合并为当前实战技能，当前热更新、控制器、实际发动与完整回转仍未知。']
    if not technical:return '\n'.join(lines)
    from .enemy_skills import definition_text,raw_text
    lines += ['', '【基包招式与黑板构建参考】',*definition_text(config),
        '构建来源链：'+raw_text(result['source_chain']),
        '解析后的完整配置参考：'+raw_text(config),
        *('• '+note for note in result['limits'])]
    return '\n'.join(lines)
