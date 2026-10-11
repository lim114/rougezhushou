"""Fixed public source queries, never server eligibility or game operations."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json,re

NOTICE='固定资料候选与原文引用；未知资格仍保留，不表示必然出现，不提供生成概率。'
@lru_cache(maxsize=1)
def _data():
    return json.loads((Path(__file__).with_name('data')/'node-catalog.json').read_text(encoding='utf-8'))
@lru_cache(maxsize=1)
def _original():
    return json.loads((Path(__file__).with_name('data')/'node-events.json').read_text(encoding='utf-8'))
def _text(value,label,optional=False):
    if optional and value is None:return
    if not isinstance(value,str) or not value.strip():raise ValueError(label+'需要非空文字。')
def _floor(floor,special_region=False):
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):raise ValueError('主层需要1–6的整数。')
    if type(special_region) is not bool:raise ValueError('special_region需要布尔值。')
def _event(event_id):
    _text(event_id,'事件引用')
    e=next((e for e in _data()['events'] if e['id']==event_id),None)
    if e is None:raise ValueError('事件引用不存在；同名事件需要选择各自资料分组。')
    return e
def _scene(event_id,scene_key):
    _text(scene_key,'场景引用')
    s=next((s for s in _event(event_id)['scenes'] if s['key']==scene_key),None)
    if s is None:raise ValueError('场景不属于所选事件。')
    return s
def _result(rows,**extra):
    return {'rows':rows,'sources':deepcopy(_data()['sources']),
            'scope':deepcopy(_data()['completeness']),'notice':NOTICE,**extra}
def _summary(e):
    return {k:deepcopy(e[k]) for k in ('id','title','node_types','floors','natural','natural_reason','entry')}
def _all_node_types():
    return list(dict.fromkeys([v['name'] for v in _data()['node_types'].values()]+
                             [t for e in _data()['events'] for t in e['node_types']]))
def all_events(node_type=None,include_indirect=False):
    _text(node_type,'节点类型',True)
    if type(include_indirect) is not bool:raise ValueError('include_indirect需要布尔值。')
    rows=[_summary(e) for e in _data()['events'] if (include_indirect or e['natural'] is not False)
          and (node_type is None or node_type in e['node_types'])]
    return _result(rows,node_type=node_type,indirect_included=include_indirect,
                   original_uncataloged=deepcopy(_data()['uncataloged_original_titles']),
                   known_node_types=_all_node_types())
COMMANDS={'events':all_events}
def event_candidates(node_type=None,floor=None,special_region=False,include_indirect=False):
    _floor(floor,special_region)
    rows=[];excluded=[]
    for e in all_events(node_type,include_indirect)['rows']:
        natural_context=e['natural'] is not False
        if floor is not None and not special_region and natural_context and e['floors'] and floor not in e['floors']:
            excluded.append({**e,'reason':'固定社区目录的主层范围不包含所选层'});continue
        e['floor_status']='目录主层条件相符' if floor is not None and not special_region and natural_context and e['floors'] else '层数或特殊区域资格未知'
        e['server_eligibility']='未知';rows.append(e)
    return _result(rows,excluded=excluded,floor=floor,special_region=special_region,
                   indirect_included=include_indirect)
COMMANDS['candidates']=event_candidates
def _validate_node(node):
    if not isinstance(node,dict):raise ValueError('节点需要对象。')
    for key in ('observed_type','remembered_type'):_text(node.get(key),key,True)
    prediction=node.get('prediction')
    if prediction is not None and not isinstance(prediction,dict):raise ValueError('类型预测需要对象。')
    types=(prediction or {}).get('candidates')
    if types is not None and (not isinstance(types,list) or any(not isinstance(t,str) or not t for t in types)):
        raise ValueError('类型候选需要非空文字列表。')
    for key in ('content','remembered_content'):
        value=node.get(key)
        if value is not None and not isinstance(value,dict):raise ValueError(key+'需要对象。')
    history=node.get('content_history')
    if history is not None and (not isinstance(history,list) or any(not isinstance(v,dict) for v in history)):
        raise ValueError('历史内容需要对象列表。')
def node_events(node,floor=None,special_region=False):
    _validate_node(node);_floor(floor,special_region)
    observed=node.get('observed_type');remembered=node.get('remembered_type')
    # A current floor filter cannot discard the identity of an earlier read.
    history=all_events(remembered,include_indirect=True)['rows'] if remembered and remembered!=observed else []
    if observed in ('林间空地','曲折密道'):
        return _result([],history_candidates=history,type_candidates=[observed],node_id=node.get('id'),
                       state='当前通行节点；历史内容仅作过去参考')
    if observed and not observed.startswith('未知'):
        types=[observed];basis='当前已读类型'
    else:
        types=(node.get('prediction') or {}).get('candidates') or []
        if not types:types=_all_node_types()
        basis='模板类型候选' if (node.get('prediction') or {}).get('candidates') else '类型未确认，全部已证节点类别联合'
    by_id={}
    for t in types:
        for e in event_candidates(t,floor,special_region)['rows']:by_id[e['id']]=e
    return _result(list(by_id.values()),history_candidates=history,type_candidates=deepcopy(types),
                   remembered_type=remembered,node_id=node.get('id'),type_basis=basis)
COMMANDS['node']=node_events
def original_references(query='',title=None,record_type='all',record_id=None):
    if not isinstance(query,str) or len(query)>120:raise ValueError('检索词需要0–120字。')
    _text(title,'标题',True);_text(record_id,'原表引用',True)
    if record_type not in ('all','scene','choice'):raise ValueError('原表类别需要all、scene或choice。')
    rows=[];needle=query.strip().casefold()
    for kind,field,idkey in (('scene','unmapped_original_scenes','scene_id'),('choice','unmapped_original_choices','choice_id')):
        if record_type not in ('all',kind):continue
        for raw in _data()[field]:
            if record_id is not None and raw[idkey]!=record_id:continue
            if title is not None and raw['title']!=title:continue
            text=json.dumps(raw,ensure_ascii=False).casefold()
            if needle and needle not in text:continue
            rows.append({'record_type':kind,'record_id':raw[idkey],**deepcopy(raw),
                         'source_scene_link_verified':False,'reachable_from_entry':None})
    if record_id is not None and not rows:raise ValueError('引用不在未分类原表记录中。')
    return _result(rows,query=query,title=title,record_type=record_type,
                   next_scene_is_destination_reference_only=True,
                   natural_node_entry_verified=False)
def event_details(event_id):
    e=deepcopy(_event(event_id));represented={i for s in e['scenes'] for i in s['game_scene_ids']}
    unlinked=[{'id':i,**deepcopy(s),'reachable_from_entry':None} for i,s in _original()['scenes'].items()
              if s['title']==e['title'] and i not in represented]
    return _result(e['scenes'],event=_summary(e),unlinked_original_scenes=unlinked,
                   unclassified_original_query={'command':'original','input':{'query':e['title']}},
                   server_scene_reachability_verified=False)
COMMANDS.update(detail=event_details,original=original_references)
def _choice_navigation(event,choice):
    keys={s['key'] for s in event['scenes']};branches=[]
    for i,target in enumerate(choice['destination_keys']):
        branches.append({'branch_id':choice['key']+':main:'+str(i),'to':target,'subchoice':None})
    for i,sub in enumerate(choice.get('subchoices',[])):
        # The parser already maps group-local scene array indices to scene keys.
        branches.append({'branch_id':choice['key']+':sub:'+str(i),
                         'to':sub.get('community_destination_scene_id'),'subchoice':deepcopy(sub)})
    if not branches:branches=[{'branch_id':choice['key']+':unknown','to':None,'subchoice':None}]
    if any(b['to'] is not None and b['to'] not in keys for b in branches):
        raise ValueError('来源导航边指向组外，拒绝跨事件拼接。')
    return branches
def choice_graph(event_id):
    e=_event(event_id);edges=[];unresolved=[]
    for s in e['scenes']:
        for ch in s['choices']:
            for b in _choice_navigation(e,ch):
                row={'from':s['key'],'scene':s['key'],'choice_id':ch['key'],'choice':ch['key'],
                     'title':ch['title'],'role':ch['presentation_role'],'game_choice_ids':deepcopy(ch['game_choice_ids']),
                     'branch_id':b['branch_id'],'subchoice':b['subchoice'],
                     'evidence':'固定社区页面局部导航','server_option_available':None,
                     'game_exit_verified':False,'branch_probability':None}
                if b['to'] is None:
                    unresolved.append({**row,'status':ch['destination_status']})
                else:edges.append({**row,'to':b['to']})
    return _result(edges,event=_summary(e),entries=deepcopy(e['entry']),unresolved=unresolved,
                   community_navigation_only=True)
COMMANDS['graph']=choice_graph
def event_paths(event_id,max_steps=40,max_paths=128):
    if type(max_steps) is not int or not 1<=max_steps<=100 or type(max_paths) is not int or not 1<=max_paths<=4096:
        raise ValueError('路径限制需要有效整数。')
    g=choice_graph(event_id);adj={};stops={};rows=[];truncated=False;reasons=set()
    for edge in g['rows']:adj.setdefault(edge['from'],[]).append(edge)
    for stop in g['unresolved']:stops.setdefault(stop['scene'],[]).append(stop)
    stack=[('visit',key,[key],[],[],None) for key in reversed(g['entries'])]
    while stack:
        if len(rows)>=max_paths:truncated=True;reasons.add('max_paths');break
        mode,key,path,choices,navigation,status=stack.pop()
        if mode=='emit':
            rows.append({'scenes':path,'choices':choices,'navigation':navigation,'status':status});continue
        out=adj.get(key,[]);unknown=stops.get(key,[])
        if len(choices)>=max_steps and (out or unknown):
            rows.append({'scenes':path,'choices':choices,'navigation':navigation,'status':'达到展示深度'})
            truncated=True;reasons.add('max_steps');continue
        if not out and not unknown:
            rows.append({'scenes':path,'choices':choices,'navigation':navigation,'status':'导航末端，游戏结束未知'});continue
        pending=[]
        for edge in out:
            target=edge['to'];nav=navigation+[deepcopy(edge)]
            pending.append(('emit' if target in path else 'visit',target,path+[target],choices+[edge['choice_id']],nav,
                            '循环导航；后续未枚举' if target in path else None))
        for stop in unknown:
            pending.append(('emit',key,path,choices+[stop['choice_id']],navigation+[deepcopy(stop)],
                            '选择后续导航未知，游戏结束未知'))
        stack.extend(reversed(pending))
    return _result(rows,event=g['event'],truncated=truncated,truncation_reasons=sorted(reasons),
                   game_execution_verified=False,cycles_are_navigation_references=True,
                   limits={'max_steps':max_steps,'max_paths':max_paths})
COMMANDS['paths']=event_paths
def event_reward_options(event_id):
    from .node_rewards import _reference
    e=_event(event_id);rewards=_reference()['event_rewards'];rows=[]
    norm=lambda text:re.sub(r'[\W_]+','',text or '')
    for s in e['scenes']:
        for ch in s['choices']:
            candidates=[];rejected=[]
            for cid in ch['game_choice_ids']:
                reward=rewards.get(cid)
                if not reward:continue
                if reward['event_title']==e['title'] and norm(reward['choice_title'])==norm(ch['title']):
                    candidates.append({'choice_id':cid,**deepcopy(reward)})
                else:rejected.append({'choice_id':cid,'reason':'事件标题或选项标题不一致'})
            rows.append({'scene':s['key'],'choice_id':ch['key'],'choice_title':ch['title'],
                         'role':ch['presentation_role'],'rewards':candidates,'rejected_reward_links':rejected,
                         'named_reward_found':bool(candidates),'full_reward_pool_known':False,
                         'unknown_reward_pool':True,'actual_claim_eligible':None,
                         'source_scene_link_verified':False})
    return _result(rows,event=_summary(e),inventory_updated=False,
                   named_grant_only=True,full_reward_pool_known=False)
COMMANDS['rewards']=event_reward_options
@lru_cache(maxsize=1)
def _battle_pools():
    return json.loads((Path(__file__).with_name('data')/'battle-node-pools.json').read_text(encoding='utf-8'))
def _difficulty(difficulty):
    if difficulty is not None and (type(difficulty) is not int or difficulty not in _data()['valid_difficulties']):
        raise ValueError('保密等级需要固定资料中的普通模式整数或留空。')
def _node_requirement_checks(node_type,floor=None,difficulty=None,special_region=False):
    _floor(floor,special_region);_difficulty(difficulty)
    rules={'“居民”据点':{'excluded_main_floors':[1,6],'minimum_difficulty':4},
           '曲折密道':{'excluded_main_floors':[1,2,6]},'应急助力':{'excluded_main_floors':[1,6]}}
    rule=rules.get(node_type,{})
    reference=next((f for f in _battle_pools()['node_functions'] if f['node_type']==node_type),None)
    return {'excluded_main_floors':deepcopy(rule.get('excluded_main_floors',[])),
            'minimum_difficulty':rule.get('minimum_difficulty'),
            'known_floor_requirement_matches':None if not rule.get('excluded_main_floors') or floor is None or special_region else floor not in rule['excluded_main_floors'],
            'known_difficulty_requirement_matches':None if rule.get('minimum_difficulty') is None or difficulty is None else difficulty>=rule['minimum_difficulty'],
            'condition_sources':deepcopy(reference['references']) if rule and reference else [],
            'full_server_eligibility_verified':False}
def battle_candidates(node_type=None,floor=None,context='natural',special_region=False,difficulty=None):
    from .catalog import catalog
    _text(node_type,'节点类型',True);_floor(floor,special_region)
    if context not in ('natural','content','all'):raise ValueError('战斗来源需要natural、content或all。')
    pool=_battle_pools();rows=[];excluded=[]
    checks=_node_requirement_checks(node_type,floor,difficulty,special_region)
    if node_type is not None and node_type not in _all_node_types():raise ValueError('节点类型不在已证目录中。')
    meta=json.loads((Path(__file__).with_name('data')/'view-catalog.json').read_text(encoding='utf-8'))['stages']
    for sid,p in pool['stages'].items():
        membership=p['natural_node_types'] if context=='natural' else p['content_node_types'] if context=='content' else list(dict.fromkeys(p['natural_node_types']+p['content_node_types']))
        if node_type is not None and node_type not in membership:continue
        # An unfiltered query is the complete fixed stage directory, not a node pool.
        s=catalog()['stages'][sid];m=meta.get(sid,{})
        r={'id':sid,'title':s['name'],'difficulty':s['difficulty'],'boss_parameter':s['isBoss'],
           'floor':m.get('floor'),'floor_label':m.get('label'),'floors':deepcopy(p['floors']),
           'categories':deepcopy(p['categories']),'natural_node_types':deepcopy(p['natural_node_types']),
           'content_node_types':deepcopy(p['content_node_types']),'source_references':deepcopy(p['source_references']),
           'settlement_context_references':deepcopy(p['settlement_context_references']),
           'known_requirement_checks':deepcopy(checks),'context':context,'natural_pool_reference':bool(p['natural_node_types']),
           'node_applicability':'来源具名池引用；服务器资格未知','description':s['description'],
           'actual_occurrence':None,'server_eligibility':'未知','hidden_layer_reference':p['hidden_layer_reference']}
        if checks['known_floor_requirement_matches'] is False or checks['known_difficulty_requirement_matches'] is False:
            excluded.append({**r,'exclusion_reason':'已核对的节点主层或保密等级门槛不符'});continue
        # Generic displayed floors on pursuit/special variants cannot filter content contexts.
        apply_floor=node_type is not None and context in ('natural','all') and not special_region and bool(p['natural_node_types'])
        if floor is not None and apply_floor and p['hidden_layer_reference']:
            excluded.append({**r,'exclusion_reason':'固定目录标记为隐藏层，不能当作所选主层'});continue
        if floor is not None and apply_floor and p['floors'] and floor not in p['floors']:
            excluded.append({**r,'exclusion_reason':'具名自然节点池的固定目录主层不符'});continue
        rows.append(r)
    return _result(rows,excluded=excluded,node_type=node_type,floor=floor,context=context,special_region=special_region,difficulty=difficulty,known_requirement_checks=checks,
                   stage_source=deepcopy(catalog()['source']),pool_sources=deepcopy(pool['sources']),
                   pool_limits=deepcopy(pool['limitations']),unfiltered_is_directory=node_type is None)
COMMANDS['battles']=battle_candidates
def indirect_events(floor=None):
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):raise ValueError('主层需要1–6。')
    rows=[]
    for e in _data()['events']:
        if e['natural'] is not False:continue
        item=_summary(e);item['current_eligibility']='未知'
        item['floor_reference_matches']=None if floor is None or not e['floors'] else floor in e['floors']
        item['entry_source']='特殊传送，不能作为自然生成候选';rows.append(item)
    support=deepcopy(_data()['uncataloged_original_titles'])
    return _result(rows,cross_run_support=support,floor=floor)
COMMANDS['indirect']=indirect_events
def search_events(query,node_type=None,floor=None,include_indirect=True):
    if not isinstance(query,str) or not query.strip() or len(query)>120:raise ValueError('请输入1–120字检索词。')
    needle=query.strip().casefold();rows=[]
    for summary in event_candidates(node_type,floor,include_indirect=include_indirect)['rows']:
        e=_event(summary['id']);matches=[]
        if needle in e['title'].casefold():matches.append({'scope':'事件名','text':e['title']})
        for s in e['scenes']:
            for scope,text in [('场景正文',s['description'])]+[('场景补充说明',t) for t in s['edesc_texts']]:
                if needle in text.casefold():matches.append({'scope':scope,'scene':s['key'],'text':text})
            for ch in s['choices']:
                text=' '.join([ch.get('title') or '',ch.get('description') or '',ch.get('conditional') or ''])
                if needle in text.casefold():matches.append({'scope':'选择或条件','scene':s['key'],'choice':ch['key'],'text':text})
                for i,sub in enumerate(ch.get('subchoices',[])):
                    text=sub.get('raw') or ''
                    if needle in text.casefold():matches.append({'scope':'来源子分支','scene':s['key'],'choice':ch['key'],'subchoice_index':i,'text':text})
        for row in event_reward_options(e['id'])['rows']:
            for reward in row['rewards']:
                name=reward.get('reward',{}).get('name') or ''
                if needle in name.casefold():matches.append({'scope':'已证具名奖励','scene':row['scene'],'choice':row['choice_id'],'text':name})
        if matches:rows.append({**summary,'matches':matches})
    return _result(rows,query=query,original_matches=original_references(query=query)['rows'],
                   indirect_included=include_indirect,original_matches_have_unclassified_context=True)
COMMANDS['search']=search_events
def scene_choices(event_id,scene_key):
    e=_event(event_id);s=_scene(event_id,scene_key);original=_original()['choices'];rows=[]
    for ch in s['choices']:
        raw=[{'id':cid,**deepcopy(original[cid])} for cid in ch['game_choice_ids'] if cid in original]
        navigation=_choice_navigation(e,ch)
        rows.append({'id':ch['key'],'title':ch['title'],'description':ch['description'],
            'conditional_text':ch['conditional'],'role':ch['presentation_role'],'source_type':ch['source_type'],
            'button_identity_status':'多个原表候选' if len(raw)>1 else '单个原表候选' if raw else '仅社区展示',
            'original_candidates':raw,'next_scenes':list(dict.fromkeys(b['to'] for b in navigation if b['to'])),
            'subchoices':deepcopy(ch.get('subchoices',[])),'navigation':navigation,
            'actual_selectable':None,'visible_button_proven':False})
    return _result(rows,scene={'key':s['key'],'description':s['description'],'edesc_texts':deepcopy(s['edesc_texts'])},event=_summary(e))
COMMANDS['choices']=scene_choices
