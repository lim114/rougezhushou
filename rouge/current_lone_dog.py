"""Lake reference stages and separately inspected documented random outcomes."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-lone-dog-335';DATA='rouge/data/current-lone-dog.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='4eb26af717f5187be1d69bbee0e2064c09a0629b53c888f784f43e00023b8c9c'
UNAVAILABLE='独活的完整资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_lone_dog_335_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_lone_dog_335_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='dog'):
    if type(event_id)is not str or event_id!='dog':return None
    ref=packet()
    if ref is None:return None
    d=ref['data'];return {**ref,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),'actual_moved':None,'actual_marked':None,'actual_recruited':None,'actual_received':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'event_id':'dog','scene_id':key,'choice_id':None}
    if category=='choices'and key in r['choices']:return {'event_id':'dog','scene_id':r['choices'][key]['scene_id'],'choice_id':key}
    return None

def scene_label(result,sid):
    return '最初对话 · 独活'if sid==result['event']['entry_scene_id']else'去看小狗后的对话与两种后续'if result['scenes'].get(sid,{}).get('choice_ids')else'小心为上后的对话'

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and c['scene_id']==sid and cid in s['choice_ids']):return None
    return {**deepcopy(c),'listed_condition_match':None}

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择查阅的对话，不代表本局已到达这一步。'
    c=choice_reference(result,sid,cid);o=result['data']['originals'];lines=['【正在查阅】独活',scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['role']=='approach':
            item=o['items'][c['item_id']];lines+=['','【具名奖励资料】'+item['name'],'原文没有独立写明件数，不补成1件；这里也不表示本局已经领取。','','【作用资料，尚未应用到本局】',version._plain(item['usage']),'只涉及应急助力节点的招募源石锭，以及应急干员的生命值、攻击力和防御力；不扩大到所有招募或全队，也不据此推断其它属性与叠加算法。','','【后续分开查阅】','文献在这段对话之后列出“跟随小狗”与“请小狗告知营地位置”两种选项；不把它们当同时发生。']
        elif c['role']=='move':lines+=['','【文献作用】前往应急助力','这是前往节点，不是只标记位置，也不等于已经招募干员。','原件没有下一段对话ID；目的地的具体节点、可达条件、移动代价与实际移动仍未知，不伪造坐标或游戏跳转。']
        elif c['role']=='mark':lines+=['','【文献作用】标记应急助力位置','这是标记位置，不是立即前往，也不代表已经进入、招募或取得奖励。','具体标记哪些节点、位置与当前显示状态仍未知，本页不会改动地图。']
        if c['next_scene_id']:lines+=['','【明确的资料后续】',scene_label(result,c['next_scene_id']),'按钮只继续查阅对话，不领取收藏品或执行游戏选项。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段文献列出的选项；不表示本局全部可选。']
    else:lines+=['','本表未列本段专属后续，不自动接入前往或标记。']
    lines+=['','【范围与未知】','这是注明版本的完整事件表与固定国服原件，完整出现资格、实际领取/件数、原选项归属与移动或标记执行仍未核验。','本页只作局外查阅，不操作游戏、不修改本局库存、招募、地图或计算，不提供路线建议及概率。']
    return '\n'.join(lines)

def catalogue_binding(record):
    if type(record)is not dict or record.get('id')!='community_group_020':return None
    from .current_node_readers import same
    from . import node_catalog
    try:
        r=reference()
        if r is None:return None
        row=r['data']['catalogue_binding']
        if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
        if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
        if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
        return {**deepcopy(row),'legacy_event_id':record['id'],'title':'独活','reader':'dog335','current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),'current_source_identity':json.loads(json.dumps(r['source_identity'])),'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None
