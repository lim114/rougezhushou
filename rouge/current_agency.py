"""Source-checked agency choices; declared reading conditions never update a run."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-agency-340';DATA='rouge/data/current-agency.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='391b90aa19dcd1eacd965b9b8b089418aa55508e0b56a7eb003f12afda661cd1'
UNAVAILABLE='临时中介所的完整资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json','rouge/data/profession-icons.json'}
        if m['schema']!='current_agency_340_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_agency_340_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

OFFER_LABELS = ('先锋或近卫','重装或辅助','医疗或狙击','术师或特种')

def reference(event_id='agency', offer=None):
    if type(event_id) is not str or event_id != 'agency': return None
    if offer is not None and (type(offer) is not str or offer not in OFFER_LABELS): return None
    p=packet()
    if p is None:return None
    d=p['data']
    return {**p,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),
            'declared_offer_reference':offer,'actual_profession_offer':None,'actual_received':None,'actual_recruited':None,
            'actual_cultivation':None,'actual_hope':None,'actual_cost':None}

def locate(category,key):
    if type(category) is not str or type(key) is not str or category not in ('scenes','choices'):return None
    r=reference()
    if r is None:return None
    if category=='scenes' and key in r['scenes']:return {'scene_id':key,'choice_id':None}
    if category=='choices' and key in r['choices']:return {'scene_id':r['choices'][key]['scene_id'],'choice_id':key}
    return None

def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · 临时中介所'
    role=next((c['role']for c in result['choices'].values()if c['next_scene_id']==sid),None)
    return {'promoted':'可靠中介招募后的对话','temporary_six':'六星临时招募后的对话','leave':'离开后的对话'}.get(role,'请选择要查阅的对话')

def choice_reference(result,sid,cid):
    if type(sid) is not str or type(cid) is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and c['scene_id']==sid and cid in s['choice_ids']):return None
    c=deepcopy(c);c['listed_condition_match']=None if c['role']!='promoted' or result['declared_offer_reference'] is None else '或'.join(c['profession_pair'])==result['declared_offer_reference']
    return c

def player_text(result,sid,cid=None):
    lines=['【正在查阅】临时中介所','本页只读固定资料，不代表本局已经出现该职业组、取得希望或招募干员。']
    if sid not in result['scenes']:return '\n'.join(lines+['','请选择要查阅的对话。'])
    lines+=['','【当前对话】'+scene_label(result,sid),version._plain(result['data']['originals']['scenes'][sid]['description'])]
    c=choice_reference(result,sid,cid)
    if c:
        role=c['role'];lines+=['','【查阅选项】'+c['title'],version._plain(c['description'])]
        if role=='promoted':
            lines+=['','【职业与人数】'+'或'.join(c['profession_pair'])+' · 招募1名 · 5星及以下',
                    '“或”表示从该职业范围招募一名，不是两个职业各招一名。',
                    '【希望】本分支原文：获得2希望。',
                    '四种职业组是替代结果，不累计成8希望或4名干员；本页也不计算本局最终希望或希望上限。',
                    '【直升是什么意思】首次招募时即获得已进阶效果。',
                    '直升不等于本页已知具体等级、精英阶段、技能、模组、潜能或信赖；这些培养信息仍需实际确认。',
                    '【本次职业组】文献把该选项标为随机，但没有给出权重或当前实际组合；四组资料不表示本次四组全部可选。']
            offer=result['declared_offer_reference'];match=c['listed_condition_match']
            lines+=['','【仅本页职业组对照】'+('尚未确认；不代入本局。' if offer is None else offer+'。')]
            if match is False:lines+=['本页对照组与当前查阅的组合不同，暂不打开本组合的后续；这不是服务器实际可选性的判定。']
            elif match is True:lines+=['与当前查阅组合一致；只说明本页资料相符，完整出现资格仍未知。']
            lines+=['【招募费用与候选】原文没有给出可靠分支的完整费用和可招名单；不能把获得2希望视为免费招募或已付费用。']
        elif role=='temporary_six':
            lines+=['','【随机结果】1名6星临时招募干员；未指定职业或姓名。',
                    '不从可靠中介的四种职业组继承职业，也不额外加上那个分支的2希望。',
                    '【临时招募说明】主题通用资料说明临时招募不消耗希望；这是通用规则参考，不是已恢复本事件的实际发放与结算过程。',
                    '“临时招募”与只参加一次作战的“应急雇佣”是不同机制，不能因为“临时”二字就判定打完一场必定离队。',
                    '实际干员、培养、可选范围、发放时点及本事件完整结算仍未知。']
        else:lines+=['','【离开】仅查阅离开后的对话；不招募、不取得另一分支的2希望。']
        lines+=['','【明确的文献后续】'+scene_label(result,c['next_scene_id']),'按钮只翻阅对话，不执行选择或发放。']
    elif result['scenes'][sid]['choice_ids']:
        lines+=['','【可查阅的分支】可靠中介有四种职业组资料，另有随机六星临时招募及离开。',
                '请选择一条阅读；职业组是替代结果，不表示六条都能在本局同时选择。']
    else:lines+=['','本表没有列出后续选项；不自动返回初始菜单或反复招募。']
    lines+=['','【范围与未知】固定国服完整原件和文献已核对，不代表当前服务器完整脚本。',
            '当前实际职业组、完整资格、领取、培养、候选池与费用结算仍未知；本页职业对照只供查阅，不写回本局、计算或库存，不提供路线建议与概率。']
    return '\n'.join(lines)

def icon_bytes(label):
    """An unavailable ornament never invalidates the verified event text."""
    if type(label) is not str:return None
    p=packet()
    if p is None:return None
    r=p['data']['profession_icons'].get(label)
    if r is None:return None
    try:
        name='rouge/data/'+r['file']
        if not name.startswith('rouge/data/profession-icons/') or '..'in PurePosixPath(name).parts:return None
        path=ROOT/name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):return None
        for parent in path.parents:
            if parent==ROOT:break
            if parent.is_symlink():return None
        raw=path.read_bytes()
        if len(raw)!=r['bytes'] or sha256(raw).hexdigest()!=r['sha256'] or not raw.startswith(b'\x89PNG\r\n\x1a\n'):return None
        return raw
    except(OSError,KeyError,TypeError,ValueError):return None

def catalogue_binding(record):
    if type(record) is not dict or record.get('id')!='community_group_018':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'临时中介所','reader':'agency340',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
