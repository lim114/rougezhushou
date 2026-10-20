"""Lake reference stages and separately inspected documented random outcomes."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-cave-334';DATA='rouge/data/current-cave.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='fbf906e36958485bcb89321ebc0981af8e6eca30026f8e84bf74e3cad4d7237d'
UNAVAILABLE='洞中宝的分支资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-table.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_cave_334_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_cave_334_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='cave',source_request=None):
    if type(event_id)is not str or event_id!='cave':return None
    ref=packet()
    if ref is None:return None
    d=ref['data']
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}or type(source_request['category'])is not str or type(source_request['key'])is not str:return None
        category,key=source_request['category'],source_request['key']
        if category not in('scenes','choices')or key not in d['originals'][category]:return None
    return {**ref,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),'source_request':deepcopy(source_request),'actual_outcome':None,'actual_probability':None,'actual_variant':None,'actual_stage':None,'actual_max_attempts':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    r=reference()
    if r is None or key not in r['data']['originals'][category]:return None
    if category=='scenes':
        parents=[sid for sid,s in r['scenes'].items()if key in s['original_scene_ids']];cid=None
    else:
        matches=[c for c in r['choices'].values()if key in c['variant_ids']]
        if len(matches)!=1:return None
        cid=matches[0]['id'];parents=matches[0]['scene_ids']
    return {'event_id':'cave','scene_id':parents[0]if len(parents)==1 else None,'choice_id':cid,'possible_scene_ids':parents,'phase_needed':len(parents)>1,'source_request':{'category':category,'key':key}}

def scene_label(result,sid):return result['scenes'].get(sid,{}).get('label','请选择查阅阶段')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and cid in s['choice_ids']and sid in c['scene_ids']):return None
    row=deepcopy(c);request=result['source_request'];selected=request['key']if request and request['category']=='choices'and request['key']in c['variant_ids']else None
    row['source_variant_id']=selected
    if selected is not None:row['next_scene_id']=c['variant_next_scene_ids'][selected]
    alternatives=c['record_next_scene_ids'];doc=c['documented_next_scene_id'];order=([doc]if doc is not None else[])+[x for x in alternatives if x!=doc]
    row['reference_followups']=[{'scene_id':x,'basis':'documented_followup'if x==doc else'exact_current_record_alternative','actual_outcome':None}for x in order]if selected is None and len(alternatives)>1 else[]
    row['listed_condition_match']=None;return row

def phase_prompt(result,cid=None):
    req=result.get('source_request');target=locate(req['category'],req['key'])if req else None;parents=target['possible_scene_ids']if target else result['choices'].get(cid,{}).get('scene_ids',[])
    return '【相同文字出现在两个文献阶段】\n请先选择要查阅的阶段：\n'+'\n'.join(scene_label(result,s)for s in parents)+'\n原始记录已保留，但不能靠文字或编号认定本局处于哪一步。'

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return phase_prompt(result,cid)
    s=result['scenes'][sid];c=choice_reference(result,sid,cid);lines=['【正在查阅】洞中宝',scene_label(result,sid),'','【当前对话】',version._plain(s['description'])]
    if result['source_request']:lines+=['','【资料定位】保留了从版本页打开的原始记录；它不等于本局实际阶段或选择。']
    if c:
        lines+=['','【查看的选项】'+c['title'],'【原文写明】',version._plain(c['description'])]
        if c['documented_outcomes']:lines+=['','【文献列出的四类结果】',*[scene_label(result,o['scene_id']).removeprefix('文献结果：')for o in c['documented_outcomes']],'四类结果分别查阅，不会同时发生，不默认其中一种，也不提供概率。','文献把继续探索写回随机组；原记录另有直接结束的后续，不能据此假定无限继续或推算最多次数。']
        if c['reward_reference']:
            reward=c['reward_reference'];lines+=['','【本分支的明确奖励】'+str(reward['quantity'])+('件'if reward['kind']=='收藏品'else'')+reward['kind'],'这是本次选项说明，不与其它结果相加，不表示本局已经领取。']
            if reward['kind']=='收藏品':lines+=['具体收藏品名单、稀有度和实际发放条件仍未知。']
        if c['reference_followups']:lines+=['','【同文案的原记录有不同后续】','完整文献写的是听到低鸣；当前原记录还列有直接结束的版本。','下面分别打开资料，不替本局选择，也不把同名记录合成保证继续的流程。']
        if c['source_variant_id'] is not None:lines+=['','【这份原记录的明确后续】',scene_label(result,c['next_scene_id'])if c['next_scene_id']else'没有指定唯一后续。','仅定位这份原件，不证明其本局出现条件或归属阶段。']
        elif c['next_scene_id']:lines+=['','【明确的资料后续】',scene_label(result,c['next_scene_id'])]
        if c['battle_hint_without_exact_stage']:lines+=['','【战斗资料尚缺对应】','原文只写遭遇一场艰难的战斗，原记录也只有战斗提示。','尚未核实具体关卡、普通或紧急版本及固定地图；不凭“艰难”认定紧急，也不误开另一关。']
    elif s['choice_ids']:lines+=['','请选择本段文献中的选项；不表示本局全部可选。']
    else:lines+=['','本表未列专属后续选项，不自动接回探索或其它作战。']
    lines+=['','【范围与未知】','同文对话合读时仍保留全部原件及其不同后续。文献中的拿到源石锭后低鸣、空手后低鸣分别阅读，不推断服务器的真实阶段或次数。','完整出现资格、各阶段实际候选、随机脚本、最大次数、具体奖励池与战斗身份仍未核验。','本页只查资料，不执行探索、领取或作战，不改本局、地图、资源和计算，不提供路线推荐或生成概率。']
    return '\n'.join(lines)

def catalogue_binding(record):
    if type(record)is not dict or record.get('id')!='community_group_017':return None
    from .current_node_readers import same
    from . import node_catalog
    try:
        r=reference()
        if r is None:return None
        row=r['data']['catalogue_binding']
        if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
        if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
        if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
        return {**deepcopy(row),'legacy_event_id':record['id'],'title':'洞中宝','reader':'cave334','current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),'current_source_identity':json.loads(json.dumps(r['source_identity'])),'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None
