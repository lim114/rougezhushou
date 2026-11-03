"""Lake reference stages and separately inspected documented random outcomes."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-unattended-shop-330';DATA='rouge/data/current-unattended-shop.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='7b213a9f5c632426b597b1fdfda62108d10e7ce6f362faae002000fa2692ba47'
UNAVAILABLE='无人商店资料暂时无法核对，旧对话、选项和后续入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_unattended_shop_330_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_unattended_shop_330_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='shop',gold=None,has_fossil=None,requested_original_id=None):
    if type(event_id)is not str or event_id!='shop':return None
    if gold is not None and(type(gold)is not int or gold<0):raise ValueError('源石锭应为非负整数或未知。')
    if has_fossil is not None and type(has_fossil)is not bool:raise ValueError('四叶草化石持有应为是、否或未知。')
    ref=packet()
    if ref is None:return None
    d=ref['data']
    if requested_original_id is not None and(type(requested_original_id)is not str or requested_original_id not in d['originals']['choices']):return None
    return {**ref,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),'declared_gold':gold,'declared_has_fossil':has_fossil,'requested_original_id':requested_original_id,'actual_variant':None,'actual_upgrade':None,'actual_reward_pool':None,'condition_is_local_reference_only':True}


def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    if not((category=='scenes'and key.startswith('scene_ro6_wish_'))or(category=='choices'and key.startswith('choice_ro6_wish_'))):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'event_id':'shop','scene_id':key,'choice_id':None,'original_choice_id':None}
    if category=='choices':
        rows=[c for c in r['choices'].values()if key in c['variant_ids']]
        if len(rows)==1:return {'event_id':'shop','scene_id':rows[0]['scene_id'],'choice_id':rows[0]['id'],'original_choice_id':key}
    return None


def scene_label(result,sid):return result['scenes'].get(sid,{}).get('label','请选择查阅对话')


def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and cid in s['choice_ids']and c['scene_id']==sid):return None
    row=deepcopy(c);cost=c['gold_cost_reference'];row['listed_condition_match']=(None if result['declared_gold']is None else result['declared_gold']>=cost)if cost is not None else result['declared_has_fossil']if c['required_relic_id']else None;return row


def followup_allowed(result,sid,cid,destination):
    c=choice_reference(result,sid,cid)
    return bool(c and c['listed_condition_match']is not False and destination in c['next_scene_ids'])


def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不表示本局已经到达。'
    c=choice_reference(result,sid,cid);o=result['data']['originals'];lines=['【正在查阅】无人商店',scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description']),'','【相同文字的记录】'+str(len(c['variant_ids']))+'份','全部保留供核对，不能当成多次选择、多次扣费或多次领取；本局使用哪份仍未确认。']
        if result['requested_original_id']in c['variant_ids']:lines+=['你是从一份指定原始记录进入本页；这只定位资料，不确认本局采用该记录。']
        if c['reward_quantity_reference']is not None:lines+=['','【明确的领取数量】1件收藏品','这里只确认原文件数，具体奖励与完整候选池未知。搬两个小桶也不是领取2件。']
        if c['required_relic_id']:
            held={None:'未确认',True:'按本页对照：持有',False:'按本页对照：未持有'}[result['declared_has_fossil']];item=o['items'][c['required_relic_id']];lines+=['','【这项的前提】四叶草化石：'+held,'原文要求持有，未写交出或消耗；这里不会扣除。','','【四叶草化石的作用资料】',version._plain(item['usage']),'增加可选项不等于增加领取件数；本项仍只按原文列1件，不据此推算奖励池。']
        if c['gold_cost_reference']is not None:
            lines+=['','【本次代价】4源石锭','只按一次文案列费用，不按重复记录累计成8源石锭。']
            if result['declared_gold']is None:lines+=['本页源石锭未填写，是否够支付未知，仍可查阅文献后续。']
            elif c['listed_condition_match']:lines+=['本页数量够支付4源石锭，但完整可选条件仍未知。']
            else:lines+=['本页数量不足4源石锭，保留说明，暂不跟随后续。']
            lines+=['','【换档说明与未知】','原文说换一批更高级的收藏品；不是当场又获得1件，也不能据此确定稀有度、候选数量、完整池或可换次数。','当前保留两份开桶后续记录，文字完全相同。分别查阅，不指定先后、档次或本局实际采用的记录。']
        if c['listed_condition_match']is False:lines+=['','【本页对照不符】仅限制这一选项的后续查阅，其它选项资料保留；不判整个事件不存在。']
        if c['next_scene_id']:lines+=['','【明确共同的后续对话】',scene_label(result,c['next_scene_id']),'只继续查资料，不执行游戏选择。']
    elif sid!=result['event']['entry_scene_id']:lines+=['','这段后续没有已证的专属选项，不把最初四项再接回来，也不当可重复领取或继续换档。']
    else:lines+=['','请选择文献列出的选项；不表示本局全部可选。']
    lines+=['','【范围与未知】','这是固定版本资料查阅。完整出现资格、换档脚本、重复记录的实际归属和奖励池仍待核验。','本页条件只用于对照，不修改源石锭、持有记录或本局数值，不提供路线建议或概率。']
    return '\n'.join(lines)
