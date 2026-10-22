"""Dance rounds and outcomes are documentary references, never actual inventory or server state."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-shadow-346';DATA='rouge/data/current-shadow.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='a5c1105cd272f096041b0668c0e58a74760fd2b393348a25f031924d0bb3656f'
UNAVAILABLE='被歌颂的影子资料暂时无法核对，旧对话、结果和图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json','rouge/data/relic-icon-receipt.json'}
        if m['schema']!='current_shadow_346_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_shadow_346_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='shadow',source_request=None):
    if type(event_id)is not str or event_id!='shadow':return None
    p=packet()
    if p is None:return None
    d=p['data'];event=deepcopy(d['event']);scenes=deepcopy(d['scenes']);choices=deepcopy(d['choices']);original=None
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}or type(source_request['category'])is not str or type(source_request['key'])is not str:return None
        category,key=source_request['category'],source_request['key']
        if category not in('scenes','choices')or key not in d['originals'][category]:return None
        original=deepcopy(d['originals'][category][key])
        if category=='scenes':scenes['source-scene']={'id':'source-scene','label':'原对话全文 · 菜单归属未确认','description':original['description'],'source_scene_ids':[key],'choice_ids':[],'scope':'original'}
        else:
            nxt=original['nextSceneId']
            if nxt:scenes['source-next']={'id':'source-next','label':'原选项明确指定的后续对话','description':d['originals']['scenes'][nxt]['description'],'source_scene_ids':[nxt],'choice_ids':[],'scope':'original'}
            scenes['source-choice']={'id':'source-choice','label':'原选项全文 · 前置未确认','description':None,'source_scene_ids':[],'choice_ids':['source-choice'],'scope':'original'}
            choices['source-choice']={'id':'source-choice','scene_id':'source-choice','title':original['title'],'description':original['description'],'next_scene_id':'source-next'if nxt else None,'variant_ids':[key],'stage_ids':[],'presentation':'option_reference','actual_game_button':None,'scope':'original','actual_received':None}
        event['scene_ids']+=list(k for k in scenes if k not in d['scenes']);event['choice_ids']+=list(k for k in choices if k not in d['choices'])
    return {**p,'event':event,'scenes':scenes,'choices':choices,'source_request':deepcopy(source_request),'requested_original':original,'actual_inventory':None,'actual_received':None,'actual_result':None,'actual_choice':None,'actual_transition':None,'actual_pool':None,'actual_life':None,'actual_round':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    if category=='relics'and key=='rogue_6_relic_artifact_4':return {'scene_id':'node-17','choice_id':'node-17:option:0'}if packet()else None
    if category not in('scenes','choices'):return None
    p=packet()
    if p is None or key not in p['data']['originals'][category]:return None
    return {'source_request':{'category':category,'key':key}}

def scene_label(result,sid):return result['scenes'].get(sid,{}).get('label','请选择查阅位置')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    return deepcopy(c)if s and c and cid in s['choice_ids']and c['scene_id']==sid else None

def shows_reward(result,sid,cid):
    c=choice_reference(result,sid,cid)
    return bool(c and any(result['data']['originals']['choices'][key]['displayData']['itemId']=='rogue_6_relic_artifact_4'for key in c['variant_ids']))

def player_text(result,sid,cid=None):
    lines=['【正在查阅】被歌颂的影子','每一圈的代价、随机结果和领取分开查看；不是本局已经发生的记录，不把不同结果相加。']
    s=result['scenes'].get(sid)
    if s is None:return '\n'.join(lines+['','请选择查阅位置。'])
    lines+=['','【查阅位置】'+scene_label(result,sid)]
    if s['description']:lines+=['','【对话原文】',version._plain(s['description'])]
    if s['scope']=='results':lines+=['','【随机结果参考】下面是文献列出的不同结果，只能逐项查阅，不能自行选择游戏随机结果，也不代表完整实际奖励池。']
    if s['scope']=='original':
        lines+=['','【这份原文能确认什么】只显示准确的原始条目；相同文字、相邻编号不证明它属于哪一圈或哪种结果。']
        if sid!='source-choice':lines+=['没有已核验的本段专属菜单，不自动连接领取、下一圈或重复分支。']
    elif s['scope']=='documented'and len(s['source_scene_ids'])>1:lines+=['','【同文提示】多份原对话全文相同，本页按文献位置区分，不能据此唯一确定服务器实际条目。']
    if sid in('node-27','node-26','node-25','node-24','node-21'):
        lines+=['','【资料区别】文献在回复生命结果复用了“谢谢你”的叙述；原件另有狗群安静下来的对话。不能仅凭文字或编号把两者强绑为同一条。回复数值按本次按钮原文查阅。']
    c=choice_reference(result,sid,cid)
    if c:
        outcome=c['presentation']=='outcome_reference'
        lines+=['','【'+('结果参考'if outcome else'查看的选项')+'】'+c['title'],version._plain(c['description'])]
        if c['title']=='加入它们':
            lines+=['','【本次代价】'+version._plain(c['description']),'每次加入分别消耗，不把领取奖励当作再次扣费；本局生命、能否承担和致命扣费规则未核对，不保证本次可选。']
            if s['scope']=='original'and c['next_scene_id']is None:lines+=['此原项没有明确下一段，不根据相同消耗猜随机结果或所属圈数。']
        if c['next_scene_id']and c['next_scene_id'].endswith(':results'):lines+=['','下方只打开本阶段文献结果目录，不代表已触发或已抽到任何结果。']
        if c['title']in('收下','休息好了'):lines+=['','【本次领取或回复】'+version._plain(c['description']),'这是这一项写明的效果，不与其它随机结果相加；随机自然物、加工品和收藏品不擅自补出具体物品名单。']
        if shows_reward(result,sid,cid):
            item=result['data']['originals']['items']['rogue_6_relic_artifact_4'];lines+=['','【犬植浆】',version._plain(item['usage']),'按原选项的物品编号对应名称和图片，不按社区清单序号套效果；不是获得6源石锭或揭露商店视野。此处不推定领取件数、光环实际层数或自动套入战斗数值。']
        if c['next_scene_id']:lines+=['','【可继续查阅】'+scene_label(result,c['next_scene_id']),'只翻阅资料，不在游戏中选择或领取。']
    elif s['choice_ids']:lines+=['','请选择本段资料列出的选项或结果参考；不表示本局同时可选或已发生。']
    else:lines+=['','本段未列出已证明的进一步菜单，不自动拼接下一步。']
    if sid in('node-15','node-15:results','node-16')or(c and c['variant_ids']==['choice_ro6_normal4_27']):
        lines+=['','【第八圈后的返回】文献与行动力领取原项都指向“我们继续跳舞吧！”的位置。再次加入仍写明消耗3目标生命值；不能由此认定无限次数、无代价收益或本局实际循环已成立。']
    lines+=['','【仍需核对】完整出现条件、随机结果范围与选择、实际父情景、生命不足处理、重复/停止脚本及本局实际领取。','仅局外资料，不改本局记忆或计算数值，不操作游戏；不推荐路线，不排序，不提供生成概率。']
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
    if type(record) is not dict or record.get('id')!='community_group_010':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'被歌颂的影子','reader':'shadow346',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
