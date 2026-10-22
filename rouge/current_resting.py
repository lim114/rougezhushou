"""Resting references keep source conflicts, outcomes and actual run state separate."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-resting-345';DATA='rouge/data/current-resting.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='418e6be9505e2a699802b922387c3ce132bc05fb021e63f2248578eb22de1b1a'
OLD_FILES={'rouge/data/resting-corner-results.json','research/p3-resting-results-293/prts-events-427904.html','research/p3-resting-results-293/prts-events-440271.html'}
UNAVAILABLE='安眠一隅的完整资料暂时无法核对，旧结果、对照入口与图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json','rouge/data/relic-icon-receipt.json',*OLD_FILES}
        if m['schema']!='current_resting_345_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_resting_345_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='resting',source_request=None):
    if type(event_id)is not str or event_id!='resting':return None
    p=packet()
    if p is None:return None
    d=p['data'];event=deepcopy(d['event']);scenes=deepcopy(d['scenes']);choices=deepcopy(d['choices']);original=None
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}or type(source_request['category'])is not str or type(source_request['key'])is not str:return None
        category,key=source_request['category'],source_request['key']
        if category not in('scenes','choices')or key not in d['originals'][category]:return None
        original=deepcopy(d['originals'][category][key])
        if category=='scenes':scenes['source-scene']={'id':'source-scene','label':'从原对话打开 · 后续未确认','description':original['description'],'source_scene_ids':[key],'choice_ids':[],'scope':'original'}
        else:
            v=original;reward=d['original_reward_references'][key];role='named_item'if '源私钥'in v['description']else'gold99'if reward and reward['kind']=='gold'else'resource'if reward else'look'if v['title']=='四处看看'else'touch';next_id=v['nextSceneId']
            if next_id:scenes['source-next']={'id':'source-next','label':'原选项明确指定的后续对话','description':d['originals']['scenes'][next_id]['description'],'source_scene_ids':[next_id],'choice_ids':[],'scope':'original'}
            scenes['source-choice']={'id':'source-choice','label':'从原选项打开 · 前置未确认','description':None,'source_scene_ids':[],'choice_ids':['source-choice'],'scope':'original'}
            choices['source-choice']={'id':'source-choice','scene_id':'source-choice','title':v['title'],'original_title':v['title'],'description':v['description'],'role':role,'next_scene_id':'source-next'if next_id else None,'variant_ids':[key],'scope':'original','source_only':True,'stage_ids':[],'presentation':'option_reference','reward_reference':deepcopy(reward),'explicit_next_conflict':role=='gold99','conflicting_original_id':key if role=='gold99'else None,'actual_result':None,'actual_received':None}
        event['scene_ids']+=list(k for k in scenes if k not in d['scenes']);event['choice_ids']+=list(k for k in choices if k not in d['choices'])
    return {**p,'event':event,'scenes':scenes,'choices':choices,'source_request':deepcopy(source_request),'requested_original':original,
            'requested_choice_association':d['original_choice_association'].get(source_request['key'])if source_request and source_request['category']=='choices'else None,
            'actual_inventory':None,'actual_received':None,'actual_result':None,'actual_choice':None,'actual_transition':None,'actual_eligible':None,'actual_pool':None,'actual_left':None,'actual_gold_total':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    p=packet()
    if p is None or key not in p['data']['originals'][category]:return None
    return {'source_request':{'category':category,'key':key}}

def scene_label(result,sid):return result['scenes'].get(sid,{}).get('label','请选择要查阅的位置')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not s or not c or cid not in s['choice_ids']:return None
    return deepcopy(c)

def conflicting_original_target(result,sid,cid):
    c=choice_reference(result,sid,cid)
    if not c or c['source_only']or not c['explicit_next_conflict']or not c['conflicting_original_id']:return None
    return locate('choices',c['conflicting_original_id'])

def shows_reward(result,sid,cid):
    c=choice_reference(result,sid,cid);return bool(c and c['role']=='named_item')

def reward_label(ref):
    if ref is None:return None
    return str(ref['quantity'])+{'hope':'希望','shield':'护盾','gold':'源石锭','precious_processed_part':'件珍贵的加工品'}[ref['kind']]

def player_text(result,sid,cid=None):
    lines=['【正在查阅】安眠一隅','分开查阅不同情况的结果；不代表本局已经进入、出现或领取，不把不同情况奖励相加。']
    s=result['scenes'].get(sid)
    if s is None:return '\n'.join(lines+['','请选择要查阅的位置。'])
    lines+=['','【查阅位置】'+scene_label(result,sid)]
    if s['description']:lines+=['','【对话原文】',version._plain(s['description'])]
    if sid.startswith('source-'):
        lines+=['','【原始条目范围】只显示这份完整原件；相同文字或相邻编号不证明它属于小狗、捕梦网或松鼠的哪一步。']
        if sid in('source-scene','source-next'):lines+=['只读该段明确对话，不猜后续菜单，也不据此认定可以重复领取。']
        if result['requested_choice_association']=='full_literal_random_candidate':lines+=['这份随机候选没有指定下一段；不按编号选择结果或套用别的情况。']
    if sid in('outcomes:first','outcomes:dog','outcomes:net','outcomes:squirrel'):
        lines+=['','【结果参考，非游戏菜单】下面是资料列出的后续，只供逐项查阅，不代表玩家可自行选中结果，也不声称完整实际范围。']
    if sid in('doc:12','outcomes:net'):
        lines+=['','【数量注释尚不一致】旧PRTS在捕梦网后的“触碰图案”写随机2种，但只列动物泥偶1项；BWIKI这组也只列该项。','不能据此认定只有1项或补出第2项；“安静观察”是另外列出的领取选项，不擅自拿来凑随机结果数。']
    if sid in('doc:16','outcomes:squirrel'):
        lines+=['','【来源分组不同】BWIKI松鼠后列果园和豹子2项；旧PRTS的注释写2项，却另列动物泥偶而成为3项。','果园、豹子按BWIKI分别查阅；旧PRTS动物泥偶单列为归属未证候选，不当成本局已证实可出现结果。']
    c=choice_reference(result,sid,cid)
    scope=c['scope']if c else s['scope']
    if scope=='legacy_unresolved':lines+=['','【仅旧资料另列，当前归属未证】此条来自旧PRTS松鼠后的额外动物泥偶；BWIKI当前分组未列。','只保留完整文字供核对，不证明当前服务器或本局可达。']
    if c:
        role=c['role'];is_result=c['presentation']=='outcome_reference'
        lines+=['','【'+('结果参考'if is_result else'查阅选项')+'】'+c['title'],version._plain(c['description'])]
        if is_result:lines+=['这是文献后续参考，不是新增游戏按钮，不等于已经发生或领取。']
        elif role=='named_item':
            item=next(iter(result['data']['originals']['items'].values()));lines+=['','【具名收藏品参考】'+item['name'],version._plain(item['usage']),
                '原选项只写出物品名称，没有给出物品编号；这里按当前唯一同名收藏品显示资料，不代表已领取、已持有或已计入资源。']
        elif role in('look','touch'):lines+=['','【继续查阅】各情况和结果按资料分组；原随机候选未给下一段，不恢复随机选择规则或完整结果池。']
        elif role in('resource','gold99'):
            lines+=['','【本次按钮的奖励参考】'+reward_label(c['reward_reference']),
                    '只解释这一按钮；其它情况、前后不同领取步骤及同文记录不在此重复合计。']
            if c['reward_reference']['kind']=='precious_processed_part':lines+=['这是1件珍贵加工品；具体物品及完整候选池仍未知，不与自然物或概念体混作同类。']
        if role in('named_item','gold99'):
            lines+=['','【两处99源石锭的关系未证实】源私钥的物品说明与事件领取项都写了99源石锭。','尚未核验是否同一次发放或不同阶段，不能相加成198，也不能据返回场景推断可反复领取。']
        if c['explicit_next_conflict']:
            lines+=['','【后续冲突必须分开看】BWIKI把99源石锭后写成离开；当前原选项却明确指向进入后的病床对话。',
                    '不能认定哪一边就是实际结束方式；实际父情景、返回/离开过程、重复与领取仍未知。']
            if c['source_only']:lines+=['本页后续按钮按原选项指向病床，只阅读原文，不补后续菜单或重复领奖。']
            else:lines+=['本页后续仅翻阅文献写出的离开；另有“对照99源石锭原项”入口，可查看它明确的病床后续。']
        if c['next_scene_id']:lines+=['','【可翻阅的资料后续】'+scene_label(result,c['next_scene_id']),'只翻阅，不进入游戏、不确认结果或发放。']
    elif s['choice_ids']:lines+=['','请选择一条资料选项或结果参考；不表示本次同时可选或已全部发生。']
    else:lines+=['','本段未列出已证明的进一步菜单，不自动返回或拼接其它结果。']
    lines+=['','【仍需核对】两处数量注释、实际结果范围/归属、99发放与后续关系、当前资格和本局领取。',
            '仅局外查阅，不修改本局、库存、地图或预计数值；不操作游戏，不给路线建议、排序或概率。']
    return '\n'.join(lines)

def icon_bytes():
    p=packet()
    if p is None:return None
    try:
        r=p['data']['icon_reference'];name=r['file'];rel=PurePosixPath(name)
        if not name.startswith('rouge/data/relic-icons/')or '..'in rel.parts or rel.is_absolute()or'\\'in name or':'in name:return None
        path=ROOT/name
        if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
        for parent in path.parents:
            if parent==ROOT:break
            if parent.is_symlink():return None
        raw=path.read_bytes()
        return raw if len(raw)==r['bytes']and sha256(raw).hexdigest()==r['sha256']and raw.startswith(b'\x89PNG\r\n\x1a\n')else None
    except(OSError,KeyError,TypeError,ValueError):return None

def catalogue_binding(record):
    if type(record) is not dict or record.get('id')!='community_group_023':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'安眠一隅','reader':'resting345',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
