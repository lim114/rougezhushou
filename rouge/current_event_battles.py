"""Current named battle links: source references, never actual stage selection."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-event-battles-326';DATA='rouge/data/current-event-battles.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='52e2d2dc858ad16062f9d45d02b27fc548729d8163cee7e5460cd86984579755'
UNAVAILABLE='事件与作战的对应资料暂时无法核对，旧选项和地图入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_event_battles_326_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
        values={}
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            path=ROOT.joinpath(*rel.parts)
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in path.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            content=path.read_bytes()
            if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            values[name]=content
        data=json.loads(values[DATA]);current=version.packet()
        if current is None or data['schema']!='current_event_battles_326_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id=None,stage_id=None):
    if event_id is not None and type(event_id)is not str:return None
    if stage_id is not None and type(stage_id)is not str:return None
    if event_id is not None and stage_id is not None:return None
    ref=packet()
    if ref is None:return None
    d=ref['data']
    if event_id is not None and event_id not in d['events']:return None
    if stage_id is not None and not any(stage_id in c['stage_ids']for c in d['choices'].values()):return None
    rows=[deepcopy(c)for c in d['choices'].values()if(event_id is None or c['event_id']==event_id)and(stage_id is None or stage_id in c['stage_ids'])]
    return {**ref,'rows':rows,'event_id':event_id,'stage_id':stage_id,'actual_stage_id':None,'parent_scene_id':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    if category=='choices'and not key.startswith('choice_ro6_'):return None
    if category=='scenes'and not key.startswith('scene_ro6_'):return None
    ref=packet()
    if ref is None:return None
    d=ref['data']
    if category=='choices'and key in d['choices']:return {'event_id':d['choices'][key]['event_id'],'choice_id':key,'source_scene_id':None}
    if category=='scenes':
        for e in d['events'].values():
            if key in e['related_scene_ids']:return {'event_id':e['id'],'choice_id':None,'source_scene_id':key}
    return None

def choice(result,cid):
    if type(cid)is not str:return None
    return next((deepcopy(c)for c in result['rows']if c['id']==cid),None)

def stage_rows(result,cid):
    c=choice(result,cid)
    if c is None:return []
    ids=[s for s in c['stage_ids']if result['stage_id']is None or s==result['stage_id']]
    return [{'id':s,'name':result['data']['originals']['stages'][s]['name'],'emergency':bool(result['data']['originals']['stages'][s]['isElite']),'actual_stage_id':None}for s in ids]

def stage_label(result,cid,sid):
    rows=stage_rows(result,cid)
    if sid not in{v['id']for v in rows}:return '未核对的配置'
    row=next(v for v in rows if v['id']==sid);same=[v for v in rows if v['name']==row['name']and v['emergency']==row['emergency']]
    suffix=' · 同名配置'+str(same.index(row)+1)if len(same)>1 else''
    return row['name']+' · '+('紧急作战'if row['emergency']else'非紧急配置')+suffix

def player_text(result,cid=None):
    c=choice(result,cid)
    if c is None:return '请选择文献中的作战选项。这里只列具名作战链接，不是该事件的完整选项或本局可选清单；从情景进入只打开同名事件总览，不证明父子关系。'
    lines=['【来源事件】'+c['event_id'],'【文献中的选项】'+c['title'],version._plain(c['description']),'','【原表写明的作战】']
    for page in c['pages']:
        lines+=[page['name']+(' · 明确注明紧急作战'if page['explicit_emergency']else' · 未在本格限定普通或紧急版本')]
        if len(page['admitted_stage_ids'])>1:lines+=['有多份同名配置供核对，不自动指定本局会使用哪一份。']
        if page['unbound_stage_ids']:lines+=['同名记录指向不同关卡文件，当前没有足够依据绑定具体配置，地图入口保留未知。']
    if len(c['pages'])>1:lines+=['原表列出多个作战名称；它们是文献候选，不表示一次连续进入，也不提供概率。']
    if c['excluded_stage_ids']:lines+=['','【已排除的误配】','该格明确注明紧急作战，因此不提供同名普通配置的入口。']
    if len(c['document_cells'])>1:lines+=['','【重复记载】','完整原表在两处写到同一选项，均保留来源；不当作两次战斗或两份奖励。']
    if result['stage_id']is not None:lines+=['','【从固定关卡反查】','当前只列文献中能对应这份配置的选项；不是本局实际入口，也不是作战的所有可能来源。']
    lines+=['','【怎样查图】','先选择下方具体配置，再打开固定预览。地图页可查敌人、出怪和奖励条件；未确认的实际版本不会被自动选中。','','【仍需区分】','文献未写紧急版本时，不因“特殊战斗”的表述排除紧急；“艰难”也不自动等于紧急。完整出现前置、实际父情景、服务器选择与奖励发放仍未知。','这里只读当前固定国服资料，不操作游戏，不扣费领奖，不改本局或旧计算，不推荐路线。']
    return '\n'.join(lines)

SUPPORTED_STAGES=frozenset(['ro6_c_5', 'ro6_c_6', 'ro6_c_7', 'ro6_duel_1', 'ro6_duel_2', 'ro6_e_t_3', 'ro6_e_t_4', 'ro6_e_t_5', 'ro6_s_1', 'ro6_t_1', 'ro6_t_13', 'ro6_t_14', 'ro6_t_15', 'ro6_t_2', 'ro6_t_3', 'ro6_t_4', 'ro6_t_5'])

def stage_has_reference(stage_id):
    return type(stage_id)is str and stage_id in SUPPORTED_STAGES and reference(stage_id=stage_id)is not None
