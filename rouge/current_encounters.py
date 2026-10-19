"""Whole documented encounters, no inventory writes or assumed variant."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-encounters-327';DATA='rouge/data/current-encounters.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='ca42039335caa0c8414d271f4c4eadb494a08d8065ee205fdb27dcfe8ab2ebfe'
UNAVAILABLE='遭遇事件完整对话暂时无法核对，旧对话和选项已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_encounters_327_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_encounters_327_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id,has_controller=None):
    if type(event_id)is not str:return None
    if has_controller is not None and type(has_controller)is not bool:raise ValueError('笼控器持有状态应为是、否或未知。')
    if event_id!='黑诞'and has_controller is not None:raise ValueError('笼控器对照仅适用于黑诞。')
    ref=packet()
    if ref is None or event_id not in ref['data']['events']:return None
    d=ref['data'];e=d['events'][event_id]
    return {**ref,'event':deepcopy(e),'scenes':{k:deepcopy(d['scenes'][k])for k in e['scene_ids']},'choices':{k:deepcopy(d['choices'][k])for k in e['choice_ids']},'declared_has_controller':has_controller,'condition_is_local_reference_only':True}

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
    row=deepcopy(c);row['listed_condition_match']=result['declared_has_controller']if c['required_item_id']else None;return row

def battle_target(result,sid,cid):
    c=choice_reference(result,sid,cid)
    if c is None or not c['has_documented_battle_link']or c['listed_condition_match']is False:return None
    from .current_event_battles import locate as battle_locate
    targets=[battle_locate('choices',key)for key in c['variant_ids']]
    valid=[t for t in targets if t is not None]
    return deepcopy(valid[0])if len(valid)==1 else None

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不表示本局已经走到这一步。'
    d=result['data'];o=d['originals'];c=choice_reference(result,sid,cid);lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if len(c['variant_ids'])>1:lines+=['','【同文案的不同记录】','游戏资料有4份同文案记录，均指向这一段后续对话，其它记录内容有差别。全部保留，不能指定本局使用哪一份，也不当作4次选择或4次扣除。']
        if c['required_item_id']:
            declared={None:'尚未确认',True:'按本页对照：持有',False:'按本页对照：未持有'}[result['declared_has_controller']];lines+=['','【这个选项的前提】持有笼控器：'+declared,'原文写的是持有，不自动扣除笼控器；完整出现条件与实际消耗仍未完全核验。']
            if c['listed_condition_match']is False:lines+=['当前对照不满足该项条件，仍可阅读，后续按钮不可用；不因此排除本事件的战斗或逃离选项。']
            else:lines+=['这只是本页条件对照，不是自动确认本局可选，也不修改持有记录。']
        if c['item_id']:
            item=o['items'][c['item_id']]
            if item['type']=='RELIC':lines+=['','【具名获得】'+item['name'],version._plain(item['usage']),'具体领取件数与实际发放仍未知；这里只提供作用资料，不发放或套用加成。']
        if '一半' in c['description']and'源石锭'in c['description']:lines+=['','【代价仍需核对】','原文为消耗一半源石锭。奇数时怎样取整、实际扣除顺序尚未核验，不给出猜测金额，也不扣本局资源。']
        if '至少保留1目标生命值'in c['description']:lines+=['','【生命代价】','原文要求扣除3点目标生命值，至少保留1点。实际扣除和其它效果的关系未完整核验，不将它理解成无条件扣满3点，也不改当前生命记录。']
        if c['next_scene_id']:lines+=['','【明确的后续对话】',scene_label(result,c['next_scene_id']),'下方按钮只继续阅读文献，不在游戏中选择。']
        if c['has_documented_battle_link']:lines+=['','【具名作战】','可打开对应的作战选项与配置资料，再手动选择固定地图。文献未限定版本时保留同名配置；明确紧急时排除普通配置，不默认本局版本。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段文献列出的选项；不表示本局全部可选。']
    else:lines+=['','文献未列本段的专属后续选项，不自动连接其它确认或作战。']
    lines+=['','【范围与未知】','这里按注明版本的资料整理对话和选项，同文案记录也保留差异；已知顺序不保证本局实际可选。','完整出现前置、实际使用哪份记录、领取结果及全部奖励池仍待核对。这里用于局外查阅，不会在游戏中替你选择。']
    return '\n'.join(lines)
