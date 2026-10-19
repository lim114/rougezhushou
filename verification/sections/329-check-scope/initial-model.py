"""Whole documented encounters, no inventory writes or assumed variant."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-resource-events-329';DATA='rouge/data/current-resource-events.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='95ff122d570ee7ec57f27c1d22cf9242f3b405c3f7b2c205742a56c8f779d792'
UNAVAILABLE='遭遇事件完整对话暂时无法核对，旧对话和选项已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_resource_events_329_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_resource_events_329_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

GOLD_EVENTS=('货从口出','敲动杠杆')

def reference(event_id,gold=None):
    if type(event_id)is not str:return None
    if gold is not None and(type(gold)is not int or gold<0):raise ValueError('源石锭对照请选择未知或非负整数。')
    if gold is not None and event_id not in GOLD_EVENTS:raise ValueError('本页固定费用对照只用于货从口出和敲动杠杆。')
    ref=packet()
    if ref is None or event_id not in ref['data']['events']:return None
    d=ref['data'];e=d['events'][event_id]
    return {**ref,'event':deepcopy(e),'scenes':{k:deepcopy(d['scenes'][k])for k in e['scene_ids']},'choices':{k:deepcopy(d['choices'][k])for k in e['choice_ids']},'declared_gold':gold,'condition_is_local_reference_only':True}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    if not key.startswith('scene_ro6_'if category=='scenes'else'choice_ro6_'):return None
    ref=packet()
    if ref is None:return None
    d=ref['data']
    if category=='scenes'and key in d['scenes']:return {'event_id':d['scenes'][key]['event_id'],'scene_id':key,'choice_id':None}
    if category=='choices':
        matches=[c for c in d['choices'].values()if key in c['variant_ids']]
        if len(matches)==1:return {'event_id':matches[0]['event_id'],'scene_id':matches[0]['scene_id'],'choice_id':matches[0]['id']}
    return None

def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · '+result['event']['title']
    choices=[c for c in result['choices'].values()if c['next_scene_id']==sid]
    return '选择“'+choices[0]['title']+'”后的对话'if len(choices)==1 else'文献中的后续对话'

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and cid in s['choice_ids']and c['scene_id']==sid):return None
    row=deepcopy(c);cost=c['gold_cost_reference'];gold=result['declared_gold'];row['listed_condition_match']=gold>=cost if gold is not None and cost is not None else None;return row


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不表示本局已经走到这一步。'
    o=result['data']['originals'];c=choice_reference(result,sid,cid);lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['gold_cost_reference']is not None:
            lines+=['','【本次代价】'+str(c['gold_cost_reference'])+'源石锭']
            if result['declared_gold']is None:lines+=['本页未填写源石锭，支付能力尚未确认；仍可继续查阅文献后续。']
            elif c['listed_condition_match']:lines+=['按本页填写的'+str(result['declared_gold'])+'源石锭，只确认足够支付这笔固定费用；不代表本局全部条件满足。']
            else:lines+=['按本页填写的'+str(result['declared_gold'])+'源石锭，不足以支付这笔固定费用；保留说明，暂不跟随后续。']
        if c['resource_reward_reference']:
            r=c['resource_reward_reference'];lines+=['','【明确的资源说明】'+str(r['quantity'])+r['resource'],'这是原文的本次变化，不是已经结算后的本局数值；上限不等于当前目标生命值，护盾也不混算成生命值。']
        if c['random_reward_reference']:
            r=c['random_reward_reference'];lines+=['','【明确的随机奖励说明】'+str(r['quantity'])+'件'+r['kind'],'只确认数量与类别，具体候选名单、稀有度和实际发放未知；不同类别不混用，也不把多选项奖励相加。']
        if c['named_reward_item_id']:
            item=o['items'][c['named_reward_item_id']];lines+=['','【具名奖励】'+item['name'],'选项没有独立写明件数，不补成1件，也不表示已领取。','','【该物品的作用资料】',version._plain(item.get('usage'))or'原表未写明。','作用说明供查阅，未据此自动获得或纳入本局数值。']
        if c['half_life_cost_reference']:lines+=['','【生命代价仍需核对】原文为一半目标生命值','奇数时的取整、最低剩余值和当前实际扣除尚未核验；不能从其它事件搬用保留1点的规则，也不预测扣后数值。']
        if c['all_gold_cost_reference']:lines+=['','【源石锭代价仍需核对】原文为全部源石锭','不把全部换算成固定费用；零源石锭时是否出现或可选、其它加成及实际扣除仍未知。']
        if c['next_scene_id']:lines+=['','【文献明确的后续】',scene_label(result,c['next_scene_id']),'这里只继续查阅对话，不执行游戏选择或支付。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本阶段资料列出的选项；不表示本局全部可选。']
    else:lines+=['','资料未列本段的专属后续选项，不自动连接其它事件。']
    lines+=['','【范围与未知】','注明版本的事件资料，不是本局已经选择的结果。完整出现资格、随机奖励池、实际发放及后续游戏调整仍需核对。','本页填写的源石锭仅用于阅读对照，不修改本局资源、持有记录或计算，也不提供路线推荐。']
    return '\n'.join(lines)
