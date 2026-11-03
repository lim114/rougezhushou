"""Peace guardian references: no inverse from a one-way movement condition."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-peace-343';DATA='rouge/data/current-peace.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='1e8e1b2368d3b58f0ae3d236263b158806be8e0a2ce935aad794e6ae23598633'
EXCEPTION_FILES={'rouge/data/peace-guardian-results.json','research/p3-peace-guardian-results-291/prts-events-427904.html','research/p3-peace-guardian-results-291/prts-events-440271.html','research/p3-peace-guardian-results-291/original-records.json'}
UNAVAILABLE='和平守卫者的完整资料暂时无法核对，旧对话、移动说明及图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json','rouge/data/relic-icon-receipt.json',*EXCEPTION_FILES}
        if m['schema']!='current_peace_343_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_peace_343_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='peace',completed=None):
    if type(event_id)is not str or event_id!='peace'or(completed is not None and type(completed)is not bool):return None
    p=packet()
    if p is None:return None
    d=p['data']
    return {**p,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),
            'declared_completed_reference':completed,'actual_current_floor_completion':None,'actual_target_node':None,
            'actual_moved':None,'actual_marked':None,'actual_battle_won':None,'actual_received':None,'actual_attack_speed_stacks':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'scene_id':key,'choice_id':None}
    if category=='choices'and key in r['choices']:return {'scene_id':r['choices'][key]['scene_id'],'choice_id':key}
    return None

def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · 和平守卫者'
    role=next((c['role']for c in result['choices'].values()if c['next_scene_id']==sid),None)
    return {'join':'接取悬赏后的对话','leave':'离开后的对话'}.get(role,'请选择要查阅的对话')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and c['scene_id']==sid and cid in s['choice_ids']):return None
    c=deepcopy(c);c['documented_no_move_reference']=True if c['role']=='move'and result['declared_completed_reference']is True else None
    return c

def shows_reward(result,sid,cid=None):
    c=choice_reference(result,sid,cid)
    return sid==result['data']['joined_scene_id']or bool(c and c['role']=='join')

def player_text(result,sid,cid=None):
    lines=['【正在查阅】和平守卫者','固定版本的事件资料；查阅不代表已经接悬赏、移动、标记或作战。']
    if sid not in result['scenes']:return '\n'.join(lines+['','请选择要查阅的对话。'])
    lines+=['','【当前对话】'+scene_label(result,sid),version._plain(result['data']['originals']['scenes'][sid]['description'])]
    c=choice_reference(result,sid,cid)
    if c:
        role=c['role'];lines+=['','【查阅选项】'+c['title'],version._plain(c['description'])]
        if role=='join':lines+=['','【接取悬赏的结果参考】获得厄运火杆；实际领取件数与是否持有仍未知。','接取悬赏之后，资料另列“立即前往”与“仅标记”两种选择；获得收藏品不等于已经前往或获胜。']
        elif role=='leave':lines+=['','【离开】本分支没有列出厄运火杆、标记、移动或作战奖励，不附加另一支的结果。']
        elif role=='move':
            lines+=['','【移动参考】文献写明前往最近的“居民”据点；当前原件没有给出具体节点或战斗地图。','【本层已完成时的例外】'+result['data']['movement_exception_reference']['condition_text'],'这是单向条件：已完成则不移动；未完成并不保证一定移动。']
            done=result['declared_completed_reference']
            lines+=['','【仅本页条件对照】'+('尚未确认本层是否完成；不代入本局。'if done is None else'假设本层已完成：按该文献例外，不移动；这不是本局实际状态。'if done else'假设本层未完成：仍不能据此保证移动或指定目的地。')]
            lines+=['实际目标、最近的判定、移动执行及是否进入作战仍未知；本页不会替玩家选择路线。']
        elif role=='mark':lines+=['','【仅作标记】资料说明暂不前往；标记不表示已移动、进入作战或取得胜利。','原件未给出准确目标节点和战斗地图；本页不伪造位置、开启作战或改写本局地图。']
        if c['next_scene_id']:lines+=['','【可翻阅的后续】'+scene_label(result,c['next_scene_id']),'按钮只翻阅资料，不执行接取、发放或移动。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择一条资料分支；后续结果分开阅读，不作为本局已经发生的事实。']
    else:lines+=['','完整资料未列出更多后续；不自动接回悬赏或补出作战。']
    if shows_reward(result,sid,cid):
        item=next(iter(result['data']['originals']['items'].values()))
        lines+=['','【悬赏收藏品】'+item['name']+'（当前固定版本说明，不代表已持有）',version._plain(item['usage']),
                '【生效时点】敌人生命减少限定于与“居民”作战；永久攻速奖励还要求作战胜利。',
                '接取悬赏、立即前往或仅作标记，都不能直接记为已获胜并增加10攻速；+10也不是+10%。',
                '请以实际作战结果确认生效情况和累计胜利次数；仅查阅本页不会改变预计数值。']
    lines+=['','【仍需核对】当前服务器完整资格、本层完成状态、实际目标、移动/标记与作战结果、实际领取和累计层数。',
            '本页条件仅供对照，不写回本局；不操作游戏，不给路线建议、排序或概率。']
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
    if type(record) is not dict or record.get('id')!='community_group_019':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'和平守卫者','reader':'peace343',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
