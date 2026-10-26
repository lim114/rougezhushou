"""Exact guest-boss documentary conditions; no live/numeric battle model."""
from copy import deepcopy
from hashlib import sha256
import json
from . import current_battle_reference as battle
PACK = 'research/p3-current-guest-material-380'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '9d65a3e8a4bfbe18619e0e07d0709b9b0e8ff5b18e8ec369bfbb4341393f542c'
ACTORS = {'enemy_1532_minima': 'material'}
STAGES = ('ro6_n_5_2', 'ro6_n_5_2_dlc1', 'ro6_e_5_2', 'ro6_e_5_2_dlc1')
TITLE = '“物欲拮抗者” · 指令、屏障与斯第奇'
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
        if manifest['schema']!='current_guest_material_380_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
        expected={PACK+'/'+name for name in ('http-source-records.json', 'material-opponent-complete.html', 'reference-data.json', 'source-notes.json')}
        if set(manifest['files'])!=expected:return None
        objects={}
        for name,pin in manifest['files'].items():
            content=battle.version._file(name).read_bytes()
            if type(pin['bytes'])is not int or len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            objects[name]=content
        data=json.loads(objects[PACK+'/reference-data.json']);current=battle.packet()
        if current is None or data['schema']!='current_guest_material_380_v1'or tuple(data['bindings'])!=STAGES:return None
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
    return ['这里只采用本关对应的机制资料；同名敌人其它配置的招式和冷却不能直接套用。', '屏障、技能准备、命中延迟、影响地块和波次释放各有条件；本页不读取战斗或实际站位，也不推算开场后的准确时刻。', '通用文献不替代本关或当前阶段的完整脚本；实际触发、持续和最终结果仍需核对。']

def player_topic_notes(result,key,topic):
    row=entity(result,key)
    if row is None:return[]
    source=deepcopy(result['data']['profiles'][row['actor']]['topic_text'].get(topic,[]))
    if row['actor']=='material'and topic=='shield':
        source=[('本关对应资料的屏障技能，首次准备和再次就绪均为80秒；同名敌人的另一组资料列有40秒，不能套用到本关。'if'数据库级别0'in line else'资料中还有尚未解释的屏障参数；不能用它们替代文献所记的屏障值，也不能据此推算本局实际剩余屏障。'if'dynamic'in line else line)for line in source]
    return source

def technical_scope_notes(result,key,topic):
    row=entity(result,key)
    if row is None:return{}
    return{'original_limits':deepcopy(result['data']['limits']),
           'original_topic_text':deepcopy(result['data']['profiles'][row['actor']]['topic_text'].get(topic,[])),
           'original_enemy_database':deepcopy(result['data']['originals']['enemy_definitions'][row['entity_id']]),
           'interpretation_notes':['原始dynamic=3333参数与文献9999屏障分别保留；本节不解释它们的换算，不以原参数替代文献或最终屏障。', '原数据库级别只用于准确取资料，不代表普通/精英/领袖分类。']}

def player_text(result,key=None,topic=None):
    if result is None:return UNAVAILABLE
    row=entity(result,key);lines=['【'+result['stage_name']+' · '+TITLE+'】',NOTICE]
    if row is None:return'\n'.join(lines+['','请选择这份关卡中的准确首领；同名、等级与关卡覆盖分别保存。'])
    profile=result['data']['profiles'][row['actor']]
    lines+=['','【先看这几点】',row['enemy']['name'],*profile['summary'],'','【图鉴原说明】',*row['enemy']['abilities']]
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
