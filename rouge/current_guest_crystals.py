"""Exact guest-boss documentary conditions; no live/numeric battle model."""
from copy import deepcopy
from hashlib import sha256
import json
from . import current_battle_reference as battle
PACK = 'research/p3-current-guest-crystals-379'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '015433e4fc028b4d29c7e32750d064b7a129b808371ecf06571541a4709f449d'
ACTORS = {'enemy_7027_xbbtl': 'flying', 'enemy_7028_xbscp': 'ground'}
STAGES = ('ro6_t_16', 'ro6_c_9')
TITLE = '晶矿惊蝗 · 双晶兽的护盾与捕杀'
NOTICE = '查看这份关卡中准确首领的招式、条件与形态。文献与固定配置分别保留；不认定本局已触发、实际时刻或最终面板。'
UNAVAILABLE = '首领条件资料无法核对，旧选择、原文、图片与入口已清除；恢复后请手动重新选择。'
def _same(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return a.keys()==b.keys()and all(_same(a[k],b[k])for k in a)
    if type(a)in(list,tuple):return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
    return a==b
def packet():
    try:
        raw=battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        if manifest['schema']!='current_guest_crystals_379_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
        expected={PACK+'/'+name for name in ('crystal-fly-complete.html', 'crystal-ground-complete.html', 'http-source-records.json', 'reference-data.json', 'source-notes.json')}
        if set(manifest['files'])!=expected:return None
        objects={}
        for name,pin in manifest['files'].items():
            content=battle.version._file(name).read_bytes()
            if type(pin['bytes'])is not int or len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            objects[name]=content
        data=json.loads(objects[PACK+'/reference-data.json']);current=battle.packet()
        if current is None or data['schema']!='current_guest_crystals_379_v1'or tuple(data['bindings'])!=STAGES:return None
        source=current['inputs'];stages=current['version']['current']['details']['stages']
        if any(not _same(v,stages.get(k))for k,v in data['originals']['stages'].items()):return None
        for table in('levels','enemy_definitions','handbook'):
            if any(not _same(v,source[table].get(k))for k,v in data['originals'][table].items()):return None
        actual={}
        for sid,stage in stages.items():
            key='levels/'+stage['levelId'].lower()+'.json'
            rows=[{'key':str(i),'reference_index':i,'entity_id':row['id'],'level':row['level'],
                   'actor':ACTORS[row['id']],'raw_binding':row,'source_selector':'$.enemyDbRefs['+str(i)+']'}
                  for i,row in enumerate(source['levels'][key]['enemyDbRefs'])if row['id']in ACTORS]
            if rows:actual[sid]={'level_key':key,'rows':rows}
        if not _same(actual,data['bindings']):return None
        return{'data':data,'current':current,'source_identity':(MANIFEST_SHA256,current['identity']),
               'actual_present':None,'actual_form':None,'actual_skill_time':None,'actual_partner_retired':None,
               'actual_shield':None,'expected_stats':None,'current_server_verified':False,'numeric_model_added':False,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,AttributeError,UnicodeError,RecursionError):return None
def reference(stage_id,enemy_key=None):
    if type(stage_id)is not str or stage_id not in STAGES or(enemy_key is not None and type(enemy_key)is not str):return None
    result=packet()
    if result is None:return None
    current=battle.stage_reference(stage_id)
    if current is None or current['source_identity']!=result['current']['identity']or not _same(current['stage'],result['data']['originals']['stages'][stage_id])or not _same(current['level'],result['data']['originals']['levels'][current['level_key']]):return None
    rows=[]
    for binding in result['data']['bindings'][stage_id]['rows']:
        enemy=next((row for row in current['enemies']if row['key']==binding['key']),None)
        if enemy is None or enemy['id']!=binding['entity_id']or enemy['level']!=binding['level']or not _same(enemy['raw_binding'],binding['raw_binding']):return None
        row=deepcopy(binding);row['enemy']=deepcopy(enemy);row['has_stage_overwrite']=binding['raw_binding']['overwrittenData']is not None
        row['actual_effective_parameters']=None;rows.append(row)
    if enemy_key is not None and enemy_key not in{row['key']for row in rows}:return None
    return{'stage_id':stage_id,'stage_name':current['name'],'rows':rows,'selected_key':enemy_key,'data':result['data'],
           'source_identity':result['source_identity'],'battle_source_identity':current['source_identity'],'level_key':current['level_key'],
           'actual_present':None,'actual_form':None,'actual_skill_time':None,'actual_partner_retired':None,'actual_shield':None,
           'expected_stats':None,'current_server_verified':False,'numeric_model_added':False,'run_updated':False}
def target_available(stage_id,enemy_key):return type(enemy_key)is str and reference(stage_id,enemy_key)is not None
def entity(result,key):
    return next((deepcopy(row)for row in result['rows']if row['key']==key),None)if type(result)is dict and type(key)is str else None
def topics(result,key):
    row=entity(result,key)
    return[(t['key'],t['label'])for t in result['data']['profiles'][row['actor']]['topics']]if row else[]
def selected_card(result,key,topic):
    row=entity(result,key)
    if row is None or type(topic)is not str:return None
    profile=result['data']['profiles'][row['actor']]
    selected=next((t for t in profile['topics']if t['key']==topic),None)
    index=selected['card_by_level'].get(str(row['level']))if selected else None
    if type(index)is not int:return None
    return deepcopy(result['data']['materials'][row['actor']]['cards'][index])
def related_entities(result,key):
    if entity(result,key)is None:return[]
    return[{'enemy_key':r['key'],'name':r['enemy']['name'],'entity_id':r['entity_id'],'level':r['level']}for r in result['rows']if r['key']!=key]
def resolve_related(result,key,request):
    if type(result)is not dict or type(request)is not dict:return None
    fresh=reference(result.get('stage_id'),result.get('selected_key'))
    if fresh is None or not _same(fresh,result):return None
    target=next((r for r in related_entities(fresh,key)if _same(r,request)),None)
    return{'stage_id':fresh['stage_id'],'enemy_key':target['enemy_key'],'source_identity':fresh['source_identity'],'run_updated':False}if target else None
def player_scope_notes(result):
    return ['完整文献中的追踪、逃窜和缴械分别保留；其中“受到伤害时追踪伤害来源”明确属于生息演算通用规则，不把它直接套用于本关。本关其余相关行为尚未逐项核验，本页不认定已经生效。', '以上护盾层数、捕杀和模式条件，不代表本局已经触发或当前还有多少层；本页不显示实战站位或最终预测面板。', '通用文献不替代本关或当前阶段的完整脚本；实际触发与最终结果仍需核对。']

def player_topic_notes(result,key,topic):
    row=entity(result,key)
    if row is None:return[]
    source=deepcopy(result['data']['profiles'][row['actor']]['topic_text'].get(topic,[]))
    if row['actor']=='ground'and topic=='mode':
        source=['文献记载普攻附加基础数值为防御力-100的永久减益。原文另注：“该减益可无限叠加，叠加时仅以第一层的数值为基础进行翻倍”。不能按每次固定再减100推算当前防御；本页不计算叠加后的实际防御。' if line=='文献记载普通攻击附加永久减防；原说明写每层防御力-100，并带有特殊叠加备注，本页不把它算入玩家当前防御。' else line for line in source]
    return source

def technical_scope_notes(result,key,topic):
    row=entity(result,key)
    if row is None:return{}
    return{'original_limits':deepcopy(result['data']['limits']),
           'original_topic_text':deepcopy(result['data']['profiles'][row['actor']]['topic_text'].get(topic,[])),
           'original_enemy_database':deepcopy(result['data']['originals']['enemy_definitions'][row['entity_id']]),
           'interpretation_notes':['上方是供玩家阅读的适用说明；原模式边界和原文分别保留，不解释为当前状态。','默认减防说明以完整文献的基础数值和特殊叠加注释为准；original_topic_text中旧“每层防御力-100”摘要不作为线性叠加结论。']}

def player_text(result,key=None,topic=None):
    if result is None:return UNAVAILABLE
    row=entity(result,key);lines=['【'+result['stage_name']+' · '+TITLE+'】',NOTICE]
    if row is None:return'\n'.join(lines+['','请选择这份关卡中的准确首领；同名、等级与关卡覆盖分别保存。'])
    profile=result['data']['profiles'][row['actor']]
    summary=deepcopy(profile['summary'])
    if row['actor']=='ground':
        summary[1]='普通模式二连击；强化模式与捕杀后的玲珑模式均为四连击。'
        summary.append('半血条件有两种来源口径：图鉴写“低于50%”，完整文献写“不高于50%”；恰好50%的当前服务器判定尚未核验。')
    lines+=['','【先看这几点】',row['enemy']['name'],*summary,'','【图鉴原说明】',*row['enemy']['abilities']]
    if topic is not None:
        card=selected_card(result,key,topic)
        if card is None:return'\n'.join(lines+['','所选说明不属于这份准确引用，旧招式不显示。'])
        detail=next(t for t in profile['topics']if t['key']==topic)
        lines+=['','【'+detail['label']+'】',*player_topic_notes(result,key,topic)]
        # Full text remains in the separate source reader. The default page
        # never promotes RA-specific universal behaviours into the IS stage.
        lines+=['','完整原文与本关配置可在“准确来源与完整文献”中展开查看。']
    if row['has_stage_overwrite']:lines+=['','本关含独立覆盖；通用说明不能代替覆盖后的实际参数。']
    lines+=['','【适用边界】',*player_scope_notes(result),
      '当前生命、攻击、防御和法抗的最终预测值仍未知；不以数据库白值替代，也不根据文献判定本局已领取、已触发或已结算。']
    return'\n'.join(lines)
def map_target(result):
    if type(result)is not dict:return None
    fresh=reference(result.get('stage_id'),result.get('selected_key'))
    if fresh is None or not _same(fresh,result):return None
    from . import current_map_position as maps
    mapped=maps.stage_reference(fresh['stage_id'])
    if mapped is None or mapped.get('stage_id')!=fresh['stage_id']or mapped.get('current_level_key')!=fresh['level_key']or not _same(mapped['complete_current_geometry']['mapData'],fresh['data']['originals']['levels'][fresh['level_key']]['mapData']):return None
    return{'stage_id':fresh['stage_id'],'source_identity':fresh['source_identity'],'run_updated':False}
