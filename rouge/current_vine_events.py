"""Whole documented encounters, no inventory writes or assumed variant."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-vine-events-333';DATA='rouge/data/current-vine-events.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='dcea619fb2148ed11f258c93daf924e531633e7eb0e18b8164842e0a049a48cf'
UNAVAILABLE='遭遇事件完整对话暂时无法核对，旧对话和选项已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_vine_events_333_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_vine_events_333_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

GOLD_EVENTS=('沉寂之屋',)
CATALOGUE_IDS=('community_group_007','community_group_009')

def reference(event_id,gold=None,controller=None,seeds=None):
    if type(event_id)is not str:return None
    if gold is not None and(type(gold)is not int or gold<0):raise ValueError('源石锭请选择未知或非负整数。')
    if seeds is not None and(type(seeds)is not int or seeds<0):raise ValueError('种子请选择未知或非负整数。')
    if controller is not None and type(controller)is not bool:raise ValueError('笼控器请选择尚未确认、持有或未持有。')
    if event_id!='沉寂之屋'and gold is not None:raise ValueError('源石锭对照只用于沉寂之屋。')
    if event_id!='呼吸的红苔'and(controller is not None or seeds is not None):raise ValueError('持有与种子对照只用于呼吸的红苔。')
    ref=packet()
    if ref is None or event_id not in ref['data']['events']:return None
    d=ref['data'];e=d['events'][event_id]
    return {**ref,'event':deepcopy(e),'scenes':{k:deepcopy(d['scenes'][k])for k in e['scene_ids']},'choices':{k:deepcopy(d['choices'][k])for k in e['choice_ids']},'declared_gold':gold,'declared_controller':controller,'declared_seeds':seeds,'actual_future_region':None,'condition_is_local_reference_only':True}

def catalogue_binding(record):
    if type(record)is not dict or record.get('id')not in CATALOGUE_IDS:return None
    from .current_node_readers import same
    from . import node_catalog
    try:
        p=packet()
        if p is None:return None
        row=p['data']['catalogue_bindings'].get(record['id'])
        if row is None or any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
        if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
        if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
        r=reference(row['current_event_id'])
        if r is None:return None
        return {**deepcopy(row),'legacy_event_id':record['id'],'title':row['current_event_id'],'reader':'vine333','current_event':deepcopy(r['event']),'current_original_scenes':{k:deepcopy(v)for k,v in p['data']['originals']['scenes'].items()if v['title']==row['current_event_id']},'current_source_identity':json.loads(json.dumps(r['source_identity'])),'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,'actual_node_version_confirmed':False,'mapping_mode':'event_reference_only','actual_same_game_version':None,'actual_scene':None,'actual_choice':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

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
    row=deepcopy(c);matches=[]
    if c['gold_cost_reference']is not None:matches.append(None if result['declared_gold']is None else result['declared_gold']>=c['gold_cost_reference'])
    if c['required_item_id']is not None:matches.append(result['declared_controller'])
    if c['seed_cost_reference']is not None:matches.append(None if result['declared_seeds']is None else result['declared_seeds']>=c['seed_cost_reference'])
    row['listed_condition_match']=False if False in matches else None if not matches or None in matches else True
    return row


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不代表本局已经走到这一步。'
    o=result['data']['originals'];c=choice_reference(result,sid,cid);lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['gold_cost_reference']is not None:lines+=['','【本次源石锭代价】8源石锭','只对照本页填写的余额；足够支付不代表本局全部条件满足。']
        if c['target_life_cost_reference']is not None:lines+=['','【目标生命值代价】2目标生命值','这是本局目标生命值，不是干员生命。原文没有写至少保留1点，不套用黑诞的保底规则；余额不足时的可选条件和实际扣除仍未知。']
        if c['named_part_item_id']:
            item=o['items'][c['named_part_item_id']];lines+=['','【可获得的具名零件】'+item['name'],'笼控器属于零件，不是收藏品。原文没有独立写明件数，不自动补成1件。','作用资料：'+version._plain(item.get('usage')),'只查阅获取说明，不写入本局库存，也不把两种取得方法相加。']
        if c['required_item_id']is not None:lines+=['','【本选项的持有条件】笼控器','本页只核对是否持有；持有不等于已经消耗，不从文案推断它会被扣除。','只有本分支要求笼控器，种子分支与离开分支不继承这个要求。']
        if c['seed_cost_reference']is not None:lines+=['','【本次种子变化】种下1枚种子','这是使用种子，不是获得1枚种子，也不是领取1件随机零件。','本分支不要求笼控器；种子数量仅用于本页对照，不改本局记录。']
        if c['resource_reward_reference']:
            r=c['resource_reward_reference'];lines+=['','【选择时的直接变化】'+str(r['quantity'])+r['resource'],'仅本分支原文明确记载，不与种子分支相加，不表示本局已领取。']
        if c['future_region_reference']:lines+=['','【下一区域的影响】希望的沃土','原文写明在下一区域生成；不是当前地图新增节点，也不是现在全队获得属性加成。','区域的实际生成、覆盖哪些节点、所用阶段、属性与战后奖励仍需另核对，不在这里增加伤害或发放零件。','笼控器与种子是两条独立选项，不能当作连续两次生效。']
        if c['listed_condition_match']is False:lines+=['','【本页条件对照】已填写的条件不满足本选项；保留说明，暂不跟随后续。']
        elif c['listed_condition_match']is True:lines+=['','【本页条件对照】只确认已列的持有或数量条件相符；完整出现资格仍未知。']
        elif c['gold_cost_reference']is not None or c['required_item_id']is not None or c['seed_cost_reference']is not None:lines+=['','【本页条件对照】尚未填写或确认；仍可查阅文献后续，不代表游戏中可选。']
        if c['next_scene_id']:lines+=['','【文献后续】',scene_label(result,c['next_scene_id']),'这里只继续读对话，不执行游戏选择、扣费、种植或领取。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段资料列出的选项；不表示本局全部可选。']
    else:lines+=['','本表未列本段的专属后续，不自动接入其它事件。']
    lines+=['','【范围与未知】','使用注明版本的完整事件表及固定国服记录；实际出现资格、原选项与发放方式、件数和当前服务器变化仍待核验。','本页填写的条件仅用于查阅，不修改本局资源、库存、地图或数值计算，不提供路线推荐或概率。']
    return '\n'.join(lines)
