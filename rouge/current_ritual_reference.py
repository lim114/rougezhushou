"""Current documented ritual and material sources; never applies combat effects."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
from . import expansion_reference as version

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-ritual-324'; DATA='rouge/data/current-ritual-reference.json'; MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='fc672ee514b62fa43dc57475652801898dc52230a684e30386b1bc622bb13534'
UNAVAILABLE='调谐仪式与材料来源暂时无法核对，旧对话和关联入口已清除；恢复后请重新选择。'
MATERIALS=('rogue_6_relic_final_4','rogue_6_relic_final_6','rogue_6_relic_final_5','rogue_6_relic_cargo_13')
LABELS={'scene_ro6_end3_enter':'最初对话 · 调谐仪式','scene_ro6_end3_1':'第一步 · 保护危朽（高台部署地块）','scene_ro6_end3_2':'不依靠外物后的对话','scene_ro6_end3_3':'第二步 · 避免待部署区被封锁','scene_ro6_end3_4':'第三步 · 降低灾厄之口伤害','scene_ro6_end3_5':'仪式结束后的对话','scene_ro6_chimera2_enter':'最初对话 · 泪之聚落','scene_ro6_chimera2_1':'倾囊资助后的对话','scene_ro6_chimera2_2':'婉拒后的对话'}

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html',PACK+'/ending-section-433770.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_ritual_324_manifest_v1' or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_ritual_324_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_consumed':None,'actual_weakened':None,'run_updated':False,'calculation_applied':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='ritual'):
    if type(event_id)is not str or event_id not in('ritual','tears'):return None
    ref=packet()
    if ref is None:return None
    data=ref['data'];event=next(e for e in data['events']if e['id']==event_id)
    return {**ref,'event':deepcopy(event),'scenes':{k:deepcopy(data['scenes'][k])for k in event['scene_ids']},'choices':{k:deepcopy(data['choices'][k])for k in event['choice_ids']}}

def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    candidate=(category=='scenes'and key in LABELS)or(category=='choices'and(key.startswith('choice_ro6_end3_')or key in('choice_ro6_chimera2_1','choice_ro6_chimera2_2')))or(category=='relics'and key in MATERIALS)
    if not candidate:return None
    ref=packet()
    if ref is None:return None
    d=ref['data'];sid=None;cid=None
    if category=='scenes'and key in d['scenes']:sid=key
    elif category=='choices'and key in d['choices']:cid=key;sid=d['choices'][key]['scene_id']
    elif category=='relics':
        if key==MATERIALS[-1]:sid=next(e['entry_scene_id']for e in d['events']if e['id']=='ritual')
        else:
            hits=[v for v in d['choices'].values()if v['offered_item_id']==key]
            if len(hits)==1:cid=hits[0]['id'];sid=hits[0]['scene_id']
    if sid is None:return None
    return {'event_id':d['scenes'][sid]['event_id'],'scene_id':sid,'choice_id':cid}

def scene_label(result,sid):return LABELS.get(sid,'请选择对话')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    return deepcopy(c)if s and c and cid in s['choice_ids']and c['scene_id']==sid else None

def acquisition_reference(result,sid,cid):
    c=choice_reference(result,sid,cid)
    return deepcopy(result['data']['acquisitions'].get(c['offered_item_id']))if c else None

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择要查阅的对话；这里不表示本局已进行到这一步。'
    d=result['data'];c=choice_reference(result,sid,cid);original=d['originals']
    lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(original['scenes'][sid]['description'])]
    if c:
        o=original['choices'][cid];lines+=['','【查看的选项】'+o['title'],'【原文写明】',version._plain(o['description'])]
        iid=c['offered_item_id']
        if iid:
            effect=original['items'][c['effect_item_id']];alt=original['choices'][c['alternative_choice_id']]
            lines+=['','【削弱什么】',version._plain(effect['usage']),'保护危朽只明确适用于首次灾厄之口；降低伤害不等于伤害归零，也没有在这里补上减伤百分比。'if c['effect_item_id']!='rogue_6_relic_final_6'else'这里指灾厄之口不再封锁待部署区，不是取消首领的全部能力。','','【另一种交付方式】'+alt['title'],version._plain(alt['description']),'同一项削弱有两种交付方式，不重复相加。原文未明确交付件数，不默认每次消耗1件；也不能认定一把源私钥能完成全部三步。']
            source=acquisition_reference(result,sid,cid)
            lines+=['','【材料从哪里来】',source['description']if source else'源私钥的完整获取条件与本局持有尚未核对；本页不替你选定三种用途。']
        if result['event']['id']=='tears'and cid=='choice_ro6_chimera2_1':lines+=['','【代价与获得】','原文写明消耗全部源石锭，关联击坠“神明”。具体领取件数及本局是否符合条件仍未知，不自动扣除资源。']
        if c['next_scene_id']:lines+=['','【明确的后续对话】',scene_label(result,c['next_scene_id']),'下方按钮只继续查阅，不会在游戏中选择。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择本段文献列出的选项；不表示本局全部可选。']
    else:lines+=['','文献没有明确列出本段的专属后续选项，不自动连接别处的确认或作战。']
    if result['event']['id']=='ritual':lines+=['','【相关首领】畸症','可查固定地图、敌人及出怪资料；这不是交付后的即时作战入口，预览尚未套用上述削弱。']
    lines+=['','【范围与未知】','依据当前固定国服资料与注明修订的文献。完整出现前置、实际领取、交付数量和服务器资格仍未完全核验。','只提供节点资料，不推荐路线，不操作游戏，不改本局记忆或现有数值计算。']
    return '\n'.join(lines)
