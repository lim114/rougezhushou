"""Extract fixed reward-device declarations; no selection or settlement simulation."""
import argparse, hashlib, json
from pathlib import Path

ENTITIES={'trap_321_shnbox':'sktok_shnbox','trap_322_shrbox':'sktok_shrbox',
          'trap_323_shsbox':'sktok_shsbox','trap_320_shtlbx':'sktok_shtlbx'}
MOVING='enemy_2152_shezlc'

def checked(path,receipt):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=receipt['sha256']:raise ValueError('Fixed source hash differs: '+str(path))
    return json.loads(raw)

def queues(level):
    for wi,w in enumerate(level.get('waves') or []):
        for fi,f in enumerate(w.get('fragments') or []):
            yield f'$.waves[{wi}].fragments[{fi}]',f.get('actions') or []
    for key,b in (level.get('branches') or {}).items():
        for pi,p in enumerate(b.get('phases') or []):
            yield '$.branches['+json.dumps(key)+f'].phases[{pi}]',p.get('actions') or []

def extract_level(level,receipt):
    declarations=[];aliases={};all_aliases={}
    for container in ('predefines','hardPredefines'):
        for field in ('characterInsts','tokenInsts'):
            for i,obj in enumerate((level.get(container) or {}).get(field) or []):
                alias=obj.get('alias');entity=(obj.get('inst') or {}).get('characterKey')
                if alias:all_aliases.setdefault(alias,[]).append(entity)
                if entity not in ENTITIES:continue
                path=f'$.{container}.{field}[{i}]'
                board=[b for b in obj.get('overrideSkillBlackboard') or [] if b.get('key')=='branch_id']
                branch=board[0].get('valueStr') if len(board)==1 else None
                row={'id':path,'entity_id':entity,'alias':alias,'container':container,'raw':obj,
                     'source_selector':path,'explicit_branch_id':branch,
                     'branch_configuration_exists':branch in (level.get('branches') or {}) if branch else None}
                declarations.append(row)
                if alias:aliases.setdefault(alias,[]).append(path)
    actions=[];groups=[]
    for queue,raw_actions in queues(level):
        scoped=[]
        for i,a in enumerate(raw_actions):
            kind=a.get('actionType');key=a.get('key')
            refs=aliases.get(key,[]) if kind=='ACTIVATE_PREDEFINED' else []
            known=bool(refs) or (kind=='SPAWN' and key==MOVING)
            scoped.append({'id':queue+f'.actions[{i}]','queue_id':queue,
                          'source_selector':queue+f'.actions[{i}]','raw':a,
                          'definition_ids':refs,'known_reward_reference':known,
                          'all_alias_entities':all_aliases.get(key,[]) if kind=='ACTIVATE_PREDEFINED' else []})
        wanted={r['raw'].get('randomSpawnGroupKey') for r in scoped if r['known_reward_reference'] and r['raw'].get('randomSpawnGroupKey')}
        actions.extend(r for r in scoped if r['known_reward_reference'])
        for key in sorted(wanted):
            groups.append({'queue_id':queue,'group_key':key,
                           'members':[r for r in scoped if r['raw'].get('randomSpawnGroupKey')==key]})
    enemy_refs=[{'source_selector':f'$.enemyDbRefs[{i}]','raw':r}
                for i,r in enumerate(level.get('enemyDbRefs') or []) if r.get('id')==MOVING]
    # An enemy DB reference declares an available identity, not an initial spawn.
    initial=[{'source_selector':f'$.enemies[{i}]','raw':r}
             for i,r in enumerate(level.get('enemies') or [])
             if isinstance(r,dict) and (r.get('id')==MOVING or r.get('enemyId')==MOVING)]
    return {'source':receipt,'declarations':declarations,'actions':actions,'random_groups':groups,
            'moving_enemy_refs':enemy_refs,'initial_records':initial,
            'inspected_containers':['predefines.characterInsts','predefines.tokenInsts',
                'hardPredefines.characterInsts','hardPredefines.tokenInsts','waves.fragments.actions',
                'branches.phases.actions','enemies','enemyDbRefs'],
            'full_runtime_spawn_coverage':False}

def build(cache,observation):
    cache=Path(cache);receipt=json.loads((cache/'receipt.json').read_text(encoding='utf8'))
    lr=json.loads((cache/'level-receipt.json').read_text(encoding='utf8'))
    if receipt['commit']!=lr['commit']:raise ValueError('Mixed game revisions.')
    files=receipt['files'];topic=checked(cache/'roguelike_topic_table.json',files['roguelike_topic_table'])['details']['rogue_6']
    chars=checked(cache/'character_table.json',files['character_table']);skills=checked(cache/'skill_table.json',files['skill_table'])
    rules={}
    for entity,skill in ENTITIES.items():
        if not any(row['skillId']==skill for row in chars[entity]['skills']):raise ValueError('Device skill identity mismatch.')
        level=skills[skill]['levels'][0];text=level['description']
        rule={'entity_id':entity,'name':chars[entity]['name'],'skill_id':skill,'primary_description':text,
              'identity_source':{**files['character_table'],'source_selector':'$.'+entity},
              'quantity_source':{**files['skill_table'],'source_selector':'$.'+skill+'.levels[0].description'},
              'outcomes':[],'actual_reward':None}
        if entity=='trap_320_shtlbx':
            if text!='消耗50点部署费用开启，战斗后获得1个零件':raise ValueError('Opening rule text changed.')
            rule['outcomes']=[{'condition':'opened','condition_label':'成功开启并完成战斗后的原文参考',
                'resource':'random_scrap','quantity':1,'cost_resource':'deployment_points','cost_quantity':50,
                'complete_item_pool_known':False}]
        else:
            amount={'trap_321_shnbox':2,'trap_322_shrbox':5,'trap_323_shsbox':10}[entity]
            if f'击破额外获得{amount}源石锭' not in text:raise ValueError('Destruction reward text changed.')
            label='装置被击毁后的结算参考' if entity!='trap_323_shsbox' else '箱型装置受击召出恶笼草；击倒召出实体后的结算参考'
            rule['outcomes']=[{'condition':'defeated','condition_label':label,'resource':'gold','quantity':amount}]
        rules[entity]=rule
    rules[MOVING]={'entity_id':MOVING,'name':'恶笼草（移动敌人）','documented_level':0,
        'outcomes':[{'condition':'defeated','condition_label':'级别0移动恶笼草被击倒后结算','resource':'gold','quantity':10},
                    {'condition':'reached_route_end','condition_label':'级别0移动恶笼草到达路径终点后结算','resource':'gold','quantity':-10}],
        'quantity_source':observation['moving_enemy'],'actual_reward':None,
        'other_level_quantities':None,'complete_effective_level_binding_known':False}
    levels={};stages={}
    for stage_id,stage in topic['stages'].items():
        key=stage['levelId'].lower()+'.json';source=lr['files'][key]
        if key not in levels:levels[key]=extract_level(checked(cache/'levels'/key,source),source)
        stages[stage_id]={'name':stage['name'],'difficulty':stage['difficulty'],'level_key':key}
    return {'schema_version':1,'commit':receipt['commit'],'rules':rules,'stages':stages,'levels':levels,
        'online_observation':observation,'license_note':'游戏文本版权归鹰角及关联公司。PRTS其它内容声明CC BY-NC-SA 4.0；原数据全库许可未另行核实。',
        'limits':['仅固定声明，不证明当前宝箱出现、开启、击倒或结算。','候选、相同位置和不同来源不相加为实际总奖励。',
            '箱型装置退场和移动恶笼草击倒不是同一实体的重复奖励。','敌人资料引用不证明初始生成；动态脚本及完整结算池仍未知。']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--observation',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=build(a.cache,json.loads(Path(a.observation).read_text(encoding='utf8')))
    Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
