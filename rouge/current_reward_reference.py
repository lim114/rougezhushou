"""Current exact reward declarations and conditional quantities; no grants."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import current_battle_reference as battle
from . import moving_reward_reference as moving

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-rewards-315'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='8125b3f78a849d68a569cb466e4d0561b289155f66788aa3ff02695275a4e831'
DEVICES={'trap_320_shtlbx':'sktok_shtlbx','trap_321_shnbox':'sktok_shnbox','trap_322_shrbox':'sktok_shrbox','trap_323_shsbox':'sktok_shsbox','trap_327_shchst':'sktok_shchst'}
MOVING='enemy_2152_shezlc'
UNAVAILABLE='本版本的奖励资料无法核对，旧奖励与入口已清除；恢复后请重新选择。'
NOTICE='这里列出可能的奖励来源和达成条件，不保证出现，也不表示已经领取。不同候选、装置和派生实体不能相加为本关实际总奖励。'


def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        if manifest['schema']!='current_rewards_315_v1' or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
        objects={}
        for name,pin in manifest['files'].items():
            relative=PurePosixPath(name)
            if relative.is_absolute()or'..'in relative.parts or'\\'in name or':'in name:return None
            path=ROOT.joinpath(*relative.parts)
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            raw=path.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(raw)if name.endswith('.json')else None
        current=battle.packet()
        if current is None:return None
        return {'current':current,'selected':objects[PACK+'/selected-originals.json'],'sources':objects[PACK+'/source-selection.json'],
            'documentation_scope':objects[PACK+'/documentation-scope.json'],'rare_docs':objects['research/p3-rare-rewards/documented-outcomes.json'],
            'source_identity':MANIFEST_SHA256,'actual_total':None,'complete_reward_pool_known':False}
    except(OSError,ValueError,TypeError,KeyError,UnicodeError,RecursionError):return None


def device_rule(entity,raw,ref):
    char=ref['selected']['characters'][entity];skill_id=DEVICES[entity];skill=ref['selected']['skills'][skill_id]['levels'][0]
    selected=raw.get('skillIndex')==0 and type(raw.get('skillIndex'))is int and raw.get('mainSkillLvl')==1 and type(raw.get('mainSkillLvl'))is int
    selected=selected and len(char['skills'])==1 and char['skills'][0]['skillId']==skill_id
    overrides=raw.get('overrideSkillBlackboard')or[]
    quantity_qualified=selected and not raw.get('overrideTalents')and not raw.get('uniEquipIds')and not raw.get('tmplId')and all(x.get('key')=='branch_id'for x in overrides)
    outcomes=[]
    if entity=='trap_320_shtlbx':outcomes=[{'condition':'成功开启并完成战斗后','resource':'随机零件','minimum':1,'maximum':1,'cost_resource':'部署费用','cost':50}]
    elif entity=='trap_327_shchst':outcomes=[{'condition':'击破后部署干员偷取商店物品','resource':'商店物品','minimum':1,'maximum':2,'restriction':'参与偷取的干员无法再部署；实际商品与成功偷取数量未知。'}]
    else:
        n={'trap_321_shnbox':2,'trap_322_shrbox':5,'trap_323_shsbox':10}[entity]
        outcomes=[{'condition':'达成击破条件后的奖励参考','resource':'源石锭','minimum':n,'maximum':n}]
    if not quantity_qualified:
        for outcome in outcomes:outcome.update(minimum=None,maximum=None,cost=None)
    board=overrides if any(x.get('key')=='branch_id'for x in overrides)else skill.get('blackboard')or[]
    branch_ids=[x.get('valueStr')for x in board if x.get('key')=='branch_id']
    return {'entity_id':entity,'name':char['name'],'skill_id':skill_id,'skill_name':skill['name'],'original_description':skill['description'],
        'fixed_skill_selection_qualified':selected,'quantity_qualified':quantity_qualified,'outcomes':outcomes,
        'branch_id':branch_ids[0]if len(branch_ids)==1 and branch_ids[0]else None,
        'source_scope':'current_game_skill_text','actual_received':None,'complete_pool_known':False}


def enemy_rule(entity,refs,ref):
    if entity==MOVING:
        result=moving.moving_reward_rule([{'raw':r}for r in refs]);outcomes=[]
        for row in result['outcomes']:
            outcomes.append({'condition':'该移动敌人被击倒后战斗结算'if row['condition']=='defeated'else'该移动敌人抵达自身终点后战斗结算','resource':'源石锭','minimum':row['quantity'],'maximum':row['quantity']})
        return {'entity_id':entity,'name':'恶笼草（移动敌人）','outcomes':outcomes,'source_scope':'pinned_community_document','quantity_source':result['quantity_source'],'reference_qualification':result['reference_qualification'],'actual_received':None,'complete_pool_known':False,'mutually_exclusive_outcomes':True,'current_server_execution_verified':False}
    docs=ref['rare_docs'].get(entity);levels=sorted({r['level']for r in refs if type(r.get('level'))is int})
    qualified=bool(refs)and all(r.get('id')==entity and r.get('useDb')is True and type(r.get('level'))is int and r['level']in(0,1,2)and'overwrittenData'in r and r['overwrittenData']is None for r in refs)
    values=[docs['documented_reward_by_level'].get(str(n))for n in levels]if docs and qualified else[]
    quantity=values[0]if values and values[0]is not None and all(x==values[0]for x in values)else None
    definitions=ref['current']['inputs']['enemy_definitions'].get(entity,[]);names=[v['enemyData'].get('name',{}).get('m_value')for v in definitions if v['enemyData'].get('name',{}).get('m_defined')is True]
    return {'entity_id':entity,'name':names[0]if names else'稀有敌人（独立名称未绑定）','outcomes':[{'condition':'该敌人被击倒后，战斗结算时','resource':'随机收藏品','minimum':quantity,'maximum':quantity}],
        'source_scope':'pinned_community_document','quantity_source':deepcopy(docs),'referenced_levels':levels,'fixed_refs_qualified':qualified,'actual_received':None,'complete_pool_known':False,'current_server_execution_verified':False}


def stage_rewards(stage_id):
    ref=packet()
    if ref is None:return None
    stages=ref['current']['version']['current']['details']['stages']
    if type(stage_id)is not str or stage_id not in stages:return None
    stage=stages[stage_id];level_key='levels/'+stage['levelId'].lower()+'.json';level=ref['current']['inputs']['levels'].get(level_key)
    if level is None:return None
    rows=[];aliases={};actions=[];groups={};branch_actions={}
    enemies=battle.enemy_records(level,ref['current']);enemy_names={}
    for enemy in enemies:enemy_names.setdefault(enemy['id'],[]).append(enemy['name'])
    mimic_ids=ref['current']['version']['current']['details']['gameConst']['mimicEnemyIds'];wanted=set(mimic_ids)|{MOVING}
    for container in('predefines','hardPredefines'):
        for field in('characterInsts','tokenInsts'):
            for index,raw in enumerate((level.get(container)or{}).get(field)or[]):
                selector=f'$.{container}.{field}[{index}]';entity=(raw.get('inst')or{}).get('characterKey');alias=raw.get('alias')
                if alias:aliases.setdefault(alias,[]).append({'entity_id':entity,'selector':selector})
                if entity in DEVICES:rows.append({'id':selector,'kind':'device','entity_id':entity,'raw':deepcopy(raw),'name':ref['selected']['characters'][entity]['name'],'alias':alias,'rule':device_rule(entity,raw,ref),'source_selector':selector,'activation_references':[],'source_action_keys':[],'actual_reward':None,'position_on_original':None})
    for queue in battle.queues(level):
        scope={k:v for k,v in queue.items()if k!='actions'}
        for index,raw in enumerate(queue['actions']):
            key=str(len(actions));a={'key':key,'raw':deepcopy(raw),'queue':deepcopy(scope),'source_selector':queue['source_selector']+f'.actions[{index}]','action_index':index+1}
            entity=raw.get('key');names=list(dict.fromkeys(enemy_names.get(entity,[])))if raw.get('actionType')=='SPAWN'else[]
            if entity==MOVING:names=['恶笼草（移动敌人）']
            if raw.get('actionType')=='ACTIVATE_PREDEFINED':
                names=[ref['selected']['characters'][v['entity_id']]['name']for v in aliases.get(entity,[])if v['entity_id']in DEVICES]
            a['name']=' / '.join(names)if names else'空条目（未指定目标）'if not entity else'其他目标（名称尚未绑定）'
            actions.append(a)
            if queue['kind']=='branch':branch_actions.setdefault(queue['branch'],[]).append(a)
            group=(queue['source_selector'],raw.get('randomSpawnGroupKey'),raw.get('randomSpawnGroupPackKey'))
            if group[1]or group[2]:groups.setdefault(group,[]).append(a)
            if raw.get('actionType')=='SPAWN'and raw.get('key')in wanted:
                entity=raw['key'];refs=[r for r in level['enemyDbRefs']if r.get('id')==entity];rule=enemy_rule(entity,refs,ref)
                rows.append({'id':a['source_selector'],'kind':'moving'if entity==MOVING else'rare','entity_id':entity,'name':rule['name'],'raw':deepcopy(raw),'source_selector':a['source_selector'],'source_action_keys':[key],'activation_references':[],'rule':rule,'actual_reward':None,'position_on_original':None})
    for row in rows:
        if row['kind']=='device':
            bindings=aliases.get(row['alias'],[])if row['alias']else[];row['alias_bindings']=deepcopy(bindings);row['alias_unique']=len(bindings)==1 and bindings[0]['selector']==row['id']
            row['activation_references']=[deepcopy(a)for a in actions if a['raw'].get('actionType')=='ACTIVATE_PREDEFINED'and row['alias']and a['raw'].get('key')==row['alias']]
            if row['alias_unique']:row['source_action_keys']=[a['key']for a in row['activation_references']]
            branch=row['rule']['branch_id'];row['explicit_branch_exists']=branch in(level.get('branches')or{})if branch else None
            row['linked_branch_actions']=deepcopy(branch_actions.get(branch,[]))if branch else[]
        else:row['alias_unique']=None
        candidates=[e['portrait']for e in enemies if e['id']==row['entity_id']]
        row['portrait']=deepcopy(candidates[0])if candidates and candidates[0]is not None and all(p==candidates[0]for p in candidates)else None
        source_keys=set(row['source_action_keys']);row['candidate_groups']=[]
        for group,members in groups.items():
            if source_keys.intersection(m['key']for m in members):row['candidate_groups'].append({'queue_selector':group[0],'group_key':group[1],'pack_key':group[2],'members':deepcopy(members)})
        row['source_actions']=[deepcopy(a)for a in actions if a['key']in source_keys]
    return {'stage_id':stage_id,'stage_name':stage['name'],'level_key':level_key,'source_identity':ref['source_identity'],'battle_source_identity':ref['current']['identity'],
        'rows':rows,'current_mimic_catalog_ids':list(mimic_ids),'unreferenced_mimic_catalog_ids':[x for x in mimic_ids if not any(r['entity_id']==x for r in rows)],
        'source':deepcopy(ref['current']['selection']['original_sources'][level_key]),'documentation_scope':deepcopy(ref['documentation_scope']),
        'all_actual_rewards':None,'complete_reward_pool_known':False,'actual_current_server_verified':False,'mutated_run':False,
        'inspected_containers':['predefines.characterInsts','predefines.tokenInsts','hardPredefines.characterInsts','hardPredefines.tokenInsts','waves.fragments.actions','branches.phases.actions','enemyDbRefs'],
        'raw_null_capsule_fields_mean_unknown_not_empty':stage['capsulePool']is None and stage['redCapsulePool']is None}


def summary_text(result):
    return '\n'.join([result['stage_name']+' · 奖励与条件',NOTICE,'',f"本关固定资料列出{len(result['rows'])}条奖励来源，不等于实际目标或奖励的数量。",
        '宝箱与装置、移动恶笼草、稀有敌人分别查看。选择一项后可继续查看对应的出现条件。',
        '完整结算奖励与可掉落物品清单：未知。关卡奖励池字段为空，不能解释为不会掉落。',
        '这是固定版本资料；实际出现、击倒、开启、偷取和领取均未确认，不改动本局资源。'])


def row_text(row):
    rule=row['rule'];lines=[row['name'],'','【达成什么条件，能得到什么】']
    for outcome in rule['outcomes']:
        lo,hi=outcome['minimum'],outcome['maximum']
        if lo is None or hi is None:amount='数量未知，'
        elif outcome['resource']=='源石锭':amount=f'{lo:+d}'if lo==hi else f'{lo}–{hi}'
        else:amount=(str(lo)if lo==hi else f'{lo}–{hi}')+('件'if outcome['resource']=='随机收藏品'else'个')
        lines.append(outcome['condition']+'：'+amount+outcome['resource']+'。')
        if outcome.get('cost')is not None:lines.append('开启需消耗'+str(outcome['cost'])+'点部署费用；不是源石锭或探索行动力。')
        if outcome.get('restriction'):lines.append(outcome['restriction'])
    if row['kind']=='device':
        lines+=['','【技能说明】',rule['skill_name']+'：'+battle.plain(rule['original_description'])]
        if not rule['quantity_qualified']:lines+=['本关技能选择或覆盖参数尚未匹配，以上完整数量不能据原说明代入。']
        lines+=['','【是否会出现】','预置声明和对应出现条件只是来源记录；是否激活、能否领取仍需实际条件。']
        if row['alias']and not row['alias_unique']:lines+=['同一标记对应多个预置对象，无法唯一对应出现条件；已禁用直接跳转，不能任选一个。']
        if row.get('linked_branch_actions'):lines+=['原件明确关联了额外分支；是否触发、实际生成次数和时刻仍未确认。']
    else:
        lines+=['','【数量适用范围】','数量来自固定版本的社区敌人文献；当前关卡的精确身份、等级与覆盖条件单独核对，不能当作当前服务器已执行。']
    if row['candidate_groups']:
        lines+=['','【同组候选】']
        for i,group in enumerate(row['candidate_groups']):lines+=['候选组'+str(i+1)+'：'+'；'.join(str(j+1)+'. '+m['name']for j,m in enumerate(group['members']))+'。']
        lines+=['以上保留同组全部条目，含空条目；候选不是同时出现的证明，也不提供生成概率。']
    if row['kind']=='moving':lines+=['击倒获得与抵达终点损失是同一个目标的互斥结果，不能两项相加。']
    if row['entity_id']=='trap_323_shsbox':lines+=['箱型装置和关联分支中的移动恶笼草分别记录；不能把同一条奖励链的两处10源石锭各算一次。']
    lines+=['','【尚未确认】','本关实际奖励总量、完整收藏品/零件/商店物品池、原图上的位置：未知。']
    return '\n'.join(lines)
