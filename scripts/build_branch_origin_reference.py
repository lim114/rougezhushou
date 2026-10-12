"""Explicit branch-parameter and object-alias references; no script inference."""
import argparse,hashlib,json
from pathlib import Path

EXPECTED_COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'

def checked(path,receipt):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Fixed source digest differs: '+str(path))
    return json.loads(raw)

def extract(level,chars):
    branches=level.get('branches') or {};result={key:{'origins':[],'activations':[]} for key in branches};objects=[]
    for container in ('predefines','hardPredefines'):
        for field in ('characterInsts','tokenInsts'):
            for i,obj in enumerate((level.get(container) or {}).get(field) or []):
                path=f'$.{container}.{field}[{i}]';inst=obj.get('inst') or {};entity=inst.get('characterKey')
                source={'id':path,'kind':'predefined','entity_id':entity,'name':(chars.get(entity) or {}).get('name'),
                    'instance_level':inst.get('level'),'skill_level':obj.get('mainSkillLvl'),
                    'position':obj.get('position'),'alias':obj.get('alias'),'container':container,
                    'source_selector':path,'raw':obj}
                objects.append(source)
                for bi,entry in enumerate(obj.get('overrideSkillBlackboard') or []):
                    if entry.get('key','').rsplit('.',1)[-1].rsplit('@',1)[-1]!='branch_id' or entry.get('valueStr') not in branches:continue
                    result[entry['valueStr']]['origins'].append({**source,
                        'branch_parameter':entry,'parameter_selector':path+f'.overrideSkillBlackboard[{bi}]',
                        'related_parameters':obj.get('overrideSkillBlackboard') or [],'field_reference_verified':True})
    for i,ref in enumerate(level.get('enemyDbRefs') or []):
        raw=ref.get('overwrittenData') or {};path=f'$.enemyDbRefs[{i}]';name=raw.get('name') or {}
        source={'id':path,'kind':'enemy_reference','entity_id':ref.get('id'),
            'name':name.get('m_value') if name.get('m_defined') is True else None,
            'instance_level':ref.get('level'),'skill_level':None,'position':None,
            'source_selector':path,'raw_use_db':ref.get('useDb')}
        for field in ('talentBlackboard','skills'):
            boards=[(path+'.overwrittenData.talentBlackboard',raw.get('talentBlackboard') or [])] if field=='talentBlackboard' else [
                (path+f'.overwrittenData.skills[{j}].blackboard',skill.get('blackboard') or []) for j,skill in enumerate(raw.get('skills') or [])]
            for board_path,board in boards:
                for bi,entry in enumerate(board):
                    if entry.get('key','').rsplit('.',1)[-1].rsplit('@',1)[-1]!='branch_id' or entry.get('valueStr') not in branches:continue
                    result[entry['valueStr']]['origins'].append({**source,
                        'branch_parameter':entry,'parameter_selector':board_path+f'[{bi}]',
                        'related_parameters':board,'field_reference_verified':True})
    for key,branch in branches.items():
        for pi,phase in enumerate(branch.get('phases') or []):
            for ai,action in enumerate(phase.get('actions') or []):
                if action.get('actionType')!='ACTIVATE_PREDEFINED':continue
                alias=action.get('key');matches=[o for o in objects if alias and o['alias']==alias]
                result[key]['activations'].append({'action_id':f'branch:{key}.p{pi+1}.a{ai+1}',
                    'source_selector':'$.branches['+json.dumps(key)+f'].phases[{pi}].actions[{ai}]',
                    'alias':alias,'objects':matches,
                    'binding_status':'exact_alias' if len(matches)==1 else 'ambiguous_alias' if matches else 'unresolved_alias'})
    return result

def build(cache,observation):
    cache=Path(cache);r=json.loads((cache/'receipt.json').read_text(encoding='utf8'));lr=json.loads((cache/'level-receipt.json').read_text(encoding='utf8'))
    if r['commit']!=lr['commit']:raise ValueError('Mixed fixed game versions.')
    if r['commit']!=EXPECTED_COMMIT:raise ValueError('New source revision needs independent review.')
    chars=checked(cache/'character_table.json',r['files']['character_table'])
    stages=checked(cache/'roguelike_topic_table.json',r['files']['roguelike_topic_table'])['details']['rogue_6']['stages']
    levels={};index={}
    for sid,s in stages.items():
        key=s['levelId'].lower()+'.json';source=lr['files'][key]
        if key not in levels:
            raw=checked(cache/'levels'/key,source);levels[key]={'source':source,'branches':extract(raw,chars)}
        index[sid]={'level_key':key,'name':s['name']}
    return {'schema_version':1,'commit':r['commit'],'stages':index,'levels':levels,'observation':observation,
        'name_source':r['files']['character_table'],'topic_source':r['files']['roguelike_topic_table'],
        'limits':['同值branch_id与唯一alias仅证明配置引用，不证明实际触发。',
                  '不根据参数名Killed、summon或数值推断回调、阶段或绝对时钟。',
                  '敌人资料引用不证明已创建，原件字段不完整时保留来源未知。',
                  '预置来源位置与激活对象位置是资料坐标；SPAWN的路线数组和实际出生位置仍未知。']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--observation',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    data=build(a.cache,json.loads(Path(a.observation).read_text(encoding='utf8')))
    Path(a.output).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
