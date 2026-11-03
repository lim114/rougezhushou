"""Lake reference stages and separately inspected documented random outcomes."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-lake-328';DATA='rouge/data/current-lake.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='2057f6b545ce98cdb77465139f76fdfc8fc60f73e422ce431a53bfc98b1cbeee'
UNAVAILABLE='湖中仙女的分阶段资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_lake_328_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_lake_328_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='lake'):
    if type(event_id)is not str or event_id!='lake':return None
    ref=packet()
    if ref is None:return None
    d=ref['data'];return {**ref,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),'actual_outcome':None,'actual_probability':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    if not((category=='scenes'and key.startswith('scene_ro6_bat5_'))or(category=='choices'and key.startswith('choice_ro6_bat5_'))):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'event_id':'lake','scene_id':key,'choice_id':None,'phase_needed':False}
    if category=='choices'and key in r['choices']:
        parents=r['choices'][key]['scene_ids'];return {'event_id':'lake','scene_id':parents[0]if len(parents)==1 else None,'choice_id':key,'phase_needed':len(parents)>1}
    return None

def scene_label(result,sid):return result['scenes'].get(sid,{}).get('label','请选择查阅阶段')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and cid in s['choice_ids']and sid in c['scene_ids']):return None
    return {**deepcopy(c),'scene_id':sid}

def battle_target(result,sid,cid):
    c=choice_reference(result,sid,cid)
    if c is None or not c['has_documented_battle_link']:return None
    from .current_event_battles import locate as locate_battle
    return locate_battle('choices',cid)

def phase_prompt(result,cid):
    c=result['choices'].get(cid)
    if c is None:return '请选择要查阅的阶段；这里不表示本局已到达。'
    return '【同一选项出现在多个阶段】'+c['title']+'\n请先从上方选择对话阶段：\n'+'\n'.join(scene_label(result,s)for s in c['scene_ids'])+'\n不会默认第一次遇见，也不会修改本局进度。'

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的阶段；这里不表示本局已到达。'
    c=choice_reference(result,sid,cid);o=result['data']['originals'];lines=['【正在查阅】湖中仙女',scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['gold_cost_reference']is not None:lines+=['','【本次代价】1源石锭','只说明这一次选择的原文代价，不自动累计本局投入，也不判断当前是否可付或实际扣除。']
        if c['mapping_basis']=='explicit_repeat_note_plus_unique_current_nextSceneId':lines+=['','【重复环节单独查看】','原表把重复投入合写在一条说明中，这里按磁石和破表的对话分开查阅，不把它们当成同一次选择。']
        if c['documented_outcomes']:lines+=['','【文献记载的两种结果】',*[scene_label(result,x['scene_id'])for x in c['documented_outcomes']],'这两种结果分别查阅，不会同时发生；这里不替你确定本局结果，也不编造概率。请使用“查看文献结果”按钮查看各自后续。']
        if c['reward_reference']:lines+=['','【明确的奖励说明】1件珍贵收藏品','具体名单、实际发放条件和是否已领取仍未知，不把两种随机结果都计入奖励。']
        if c['next_scene_id']:lines+=['','【明确的后续对话】',scene_label(result,c['next_scene_id']),'下方只继续查资料，不会在游戏中选择。']
        if c['has_documented_battle_link']:lines+=['','【作战资料】','打开对应选项的固定地图配置，再手动选择查阅。文献明确紧急时排除普通配置，未限定版本的记录仍需核对实际版本。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本阶段资料列出的选项；不表示本局全部可选。']
    else:lines+=['','资料未列本段的专属后续选择，不自动接入其它战斗或确认。']
    lines+=['','【范围与未知】','这是注明版本的事件资料查阅。重复阶段与两个结果分开显示，已知顺序不保证本局实际可选。','完整出现条件、实际随机结果、奖励池和发放仍待核验；这里只作局外查阅，不改本局进度或代替游戏选择。']
    return '\n'.join(lines)
