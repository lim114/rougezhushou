"""Source-checked memory-tree choices; declared reading conditions never update a run."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-memory-tree-336';DATA='rouge/data/current-memory-tree.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='7c35934af863024fa0312f834863a786010471e56fb5c05a84221ae70002db20'
UNAVAILABLE='愈创之心的完整资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_memory_tree_336_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_memory_tree_336_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='memorytree',action_points=None,processed_parts=None,source_key=None,controller=None):
    if type(event_id)is not str or event_id!='memorytree':return None
    if any(v is not None and(type(v)is not int or v<0)for v in(action_points,processed_parts)):return None
    if any(v is not None and type(v)is not bool for v in(source_key,controller)):return None
    ref=packet()
    if ref is None:return None
    d=ref['data'];return {**ref,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),'declared':{'action_points':action_points,'processed_parts':processed_parts,'source_key':source_key,'controller':controller},'actual_consumed':None,'actual_received':None,'actual_new_region':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'event_id':'memorytree','scene_id':key,'choice_id':None}
    if category=='choices'and key in r['choices']:return {'event_id':'memorytree','scene_id':r['choices'][key]['scene_id'],'choice_id':key}
    return None

def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · 愈创之心'
    for c in result['choices'].values():
        if c['next_scene_id']==sid:return c['title']+'后的对话'
    return '请选择查阅的对话'


def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    scene=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(scene and c and c['scene_id']==sid and cid in scene['choice_ids']):return None
    v=result['declared'];role=c['role']
    match=(None if v['action_points']is None else v['action_points']>=3)if role=='action_cost'else(None if v['processed_parts']is None else v['processed_parts']>=2)if role=='random_parts'else v['source_key']if role=='key_cost'else v['controller']if role=='controller_held'else True
    return {**deepcopy(c),'listed_condition_match':match}


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择查阅的对话，不代表本局已经到达。'
    original=result['data']['originals'];c=choice_reference(result,sid,cid)
    lines=['【正在查阅】愈创之心',scene_label(result,sid),'','【当前对话】',version._plain(original['scenes'][sid]['description'])]
    if c:
        role=c['role'];lines+=['','【查看的选项】'+c['title'],version._plain(c['description'])]
        if role=='action_cost':lines+=['','【本分支代价】3行动力','只对照本页填写的行动力；不扣除本局行动力，不和其它选项合并支付。']
        elif role=='random_parts':lines+=['','【本分支代价】随机2件加工品','加工品与自然物、概念体不是同一类别。文献写明随机消耗；不能指定消耗哪两件，也不能仅凭零件总数确定加工品足够。']
        elif role=='key_cost':lines+=['','【本分支代价】消耗源私钥','原文没有独立写明件数，不补成1件。源私钥原本的99源石锭说明，不是本事件消费它后再发放的奖励。']
        elif role=='controller_held':lines+=['','【本分支要求】持有笼控器','这是持有条件，不是消耗笼控器。笼控器属于零件，不是收藏品。','【本分支收益】增加5行动力（文献值）','不再加上另一选项的1行动力；行动力上限与实际恢复后的数值仍需核对。']
        else:lines+=['','【本分支收益】增加1行动力（文献值）','不加上笼控器分支的5行动力，不把没有列出的代价当成服务器完整资格。']
        match=c['listed_condition_match'];lines+=['','【仅本页条件对照】',('尚未确认；仍可继续查阅资料，不代表游戏中一定可选。'if match is None else'不满足本分支已列条件；其它分支不受影响，可从上方直接查看后续对话。'if match is False else'满足本分支已列条件；完整资格与游戏实际选项仍未知。')]
        if c['reward_item_id']:
            item=original['items'][c['reward_item_id']];lines+=['','【具名奖励资料】'+item['name'],'原文没有独立写明领取件数；不补成1件，也不表示已经领取。',version._plain(item['usage']),'','【追忆的适用范围】','PRTS资料说明：仅在第四层取得；之后进入下一区域时，会进入另一张第四层地图，随后追忆失效。进入误入奇境不会触发。','资料列出新第四层可生成的实托邦理念为美丽新大地与希望的沃土；这不是当前地图、固定目的地或路线建议。','这段说明只限定追忆的获取与作用，不能据此认定本事件所有其它选项也只在第四层出现。']
        lines+=['','【明确的资料后续】',scene_label(result,c['next_scene_id']),'按钮只翻阅后续对话，不支付、不领取、不触发区域转换。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段文献列出的选项；五条分支不代表本局五条都可选。']
    else:lines+=['','本表未列这段对话之后的进一步选项；不自动领取或跳转地图。']
    lines+=['','【资料状态与未知】','原页面仍有“调查中”标记；完整五选项表与固定国服原件已逐项核对，不代表隐藏选项或服务器脚本已经全部恢复。','本局实际持有、消耗、领取、随机成员、区域触发及当前游戏版本仍未核验。本页条件仅作阅读对照，不写回本局或数值计算。']
    return chr(10).join(lines)


def catalogue_binding(record):
    if type(record)is not dict or record.get('id')!='community_group_011':return None
    from .current_node_readers import same
    from . import node_catalog
    try:
        r=reference()
        if r is None:return None
        row=r['data']['catalogue_binding']
        if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
        if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
        if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
        return {**deepcopy(row),'legacy_event_id':record['id'],'title':'愈创之心','reader':'memory336','current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),'current_source_identity':json.loads(json.dumps(r['source_identity'])),'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None
