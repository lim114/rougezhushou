"""Source-checked portal choices; declared reading conditions never update a run."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-portal-341';DATA='rouge/data/current-portal.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='fc2af323976b78d9cc5cef04de48f6957809f97f88b5d3c444bf1cac8b7c27f5'
UNAVAILABLE='溯源的完整资料暂时无法核对，旧对话和结果入口已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json'}
        if m['schema']!='current_portal_341_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_portal_341_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='portal', processed_parts=None, source_request=None):
    if type(event_id)is not str or event_id!='portal':return None
    if processed_parts is not None and(type(processed_parts)is not int or processed_parts<0):return None
    p=packet()
    if p is None:return None
    d=p['data'];scenes=deepcopy(d['scenes']);choices=deepcopy(d['choices']);event=deepcopy(d['event']);original=None
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}:return None
        cat,key=source_request['category'],source_request['key']
        if type(cat)is not str or type(key)is not str or cat not in('scenes','choices')or key not in d['originals'][cat]:return None
        original=deepcopy(d['originals'][cat][key])
        if cat=='scenes':scenes['source-scene']={'id':'source-scene','label':'从原始对话打开的资料','description':original['description'],'choice_ids':[],'source_scene_ids':[key]}
        else:
            v=original;role='pay'if v['type']=='SCRAP_PAY_SHOW'else'teleport'if v['type']=='TELEPORT'else'no_engine'if v['description']=='没有可用的加工品'else'leave'
            if v['nextSceneId']:
                sid=v['nextSceneId'];target=d['originals']['scenes'][sid];scenes['source-next']={'id':'source-next','label':'原选项明确指定的后续对话','description':target['description'],'choice_ids':[],'source_scene_ids':[sid]}
            scenes['source-choice']={'id':'source-choice','label':'从原选项打开 · 前置未知','description':None,'choice_ids':['source-choice'],'source_scene_ids':[]}
            choices['source-choice']={'id':'source-choice','title':v['title'],'description':v['description'],'role':role,'variant_ids':[key],
                                     'next_scene_id':'source-next'if v['nextSceneId']else None,'stage_ids':[],
                                     'inventory_rule':'has'if role=='pay'else'none'if role=='no_engine'else None,'source_only':True,'actual_variant':None,'actual_eligible':None}
        event['scene_ids']+=list(k for k in scenes if k not in d['scenes']);event['choice_ids']+=list(k for k in choices if k not in d['choices'])
    return {**p,'event':event,'scenes':scenes,'choices':choices,'declared_processed_parts':processed_parts,'source_request':deepcopy(source_request),
            'requested_original':original,'requested_choice_association':d['original_choice_association'].get(source_request['key'])if source_request and source_request['category']=='choices'else None,'actual_inventory':None,'actual_consumed':None,'actual_teleported':None,'actual_destination':None,'actual_variant':None}

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
    c=deepcopy(c);count=result['declared_processed_parts'];rule=c['inventory_rule']
    c['listed_condition_match']=None if count is None or rule is None else count>=1 if rule=='has'else count==0
    return c

def player_text(result,sid,cid=None):
    lines=['【正在查阅】溯源','固定版本资料参考；不代表本局已经出现该雾色、支付加工品或进入特殊区域。']
    s=result['scenes'].get(sid)
    if s is None or sid=='overview':return '\n'.join(lines+['','请从上方选择红、蓝、绿、金、橙或紫雾资料；颜色均写出中文，不只靠颜色区分。','加工品与自然物、概念体不同；本页件数只对照加工品，不代入零件总数。','本页不判断哪种雾色在本局出现，也不提供路线建议或生成概率。'])
    lines+=['','【查阅位置】'+scene_label(result,sid)]
    if s['description']:lines+=['','【对话原文】',version._plain(s['description'])]
    if sid.startswith('source-'):
        lines+=['','【原始条目范围】保留本次打开的完整原件。',
                '文字相同或编号接近，不能说明进入前会看到哪些选项、实际雾色或对应哪条游戏分支；这里不把其它原件的选项接到本段对话。']
        if sid in('source-next','source-scene'):lines+=['只显示这份明确的原对话，不补猜它的后续选项。']
    elif sid=='fog:绿雾':lines+=['','【原文歧义】两个离开对话标签都列了绿雾；两份均保留，实际选择依据未知，不默认其一。']
    if sid=='source-choice'and result.get('requested_choice_association')=='full_literal_teleport_candidate':lines+=['','【同文确认候选】此原件只有与文献一致的完整文字，尚未证明其属于溯源在游戏中的具体分支；不据此拼前置或传送目的地。']
    c=choice_reference(result,sid,cid)
    if c:
        role=c['role'];lines+=['','【查阅选项】'+c['title'],version._plain(c['description'])]
        if role=='pay':lines+=['','【单次代价】1件加工品。','三条是分开的选项，不一起消耗3件，也不能仅凭第一/二/三个按钮确定具体候选加工品。','本页不指定丢弃哪件、不扣实际库存、不添加奖励；消费的实际阶段及候选成员仍未知。']
        elif role=='teleport':lines+=['','【进入黑潭】这是传送提示，原件没有下一段场景或具体地图。','不把确认当作再次支付1件加工品，不凭雾色或编号造目的地、行动力和原图跳转。']
        elif role=='no_engine':lines+=['','【没有加工品】此条对应无可用加工品的说明。','红雾还记有另一种标题写法，未给出概率；不把两个标题当成两个奖励或两次触发。']
        else:lines+=['','【离开】只查看离开对话，不执行传送。']
        if c['inventory_rule']:
            value=result['declared_processed_parts'];match=c['listed_condition_match']
            lines+=['','【仅本页加工品对照】'+('件数未确认。'if value is None else str(value)+'件。'),
                    '只核对已列条件，完整服务器资格仍未知。'if match is not False else'与本条已列条件不符，暂不打开它的后续；其它资料仍可独立查阅。']
        if c.get('source_only'):lines+=['','本原件未证明之前的对话；条件只按该条明确代价或“没有加工品”原文对照，不借用整张表的菜单门槛。']
        else:lines+=['','有加工品/无加工品的分组来自完整表格的合并单元格；不是从选项编号猜入口。','同文案原件仍全部保留，仅作文献内容对应，不据此确定游戏中实际会出现哪种选项。']
        if c['next_scene_id']:lines+=['','【明确的资料后续】'+scene_label(result,c['next_scene_id']),'只翻阅本段后续，不移动、不支付、不触发游戏。']
    elif s['choice_ids']:lines+=['','请选择本段资料中的独立选项；不表示它们在本局同时出现或可选。']
    else:lines+=['','本段没有已证明的进一步选项，不自动返回或拼接其它同文案原件。']
    lines+=['','【范围与未知】已核对固定版本记录及完整事件资料；游戏中实际出现哪组选项、可消耗哪些加工品、何时消费或传送、目的地地图及本局状态仍未知。',
            '仅局外查阅，不操作游戏，不修改本局记忆、资源、地图或计算，不推荐或排序路线，不提供节点概率。']
    return '\n'.join(lines)

def catalogue_binding(record):
    if type(record)is not dict or record.get('id')!='community_group_027':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'溯源','reader':'portal341','current_event':deepcopy(r['event']),
            'current_original_scenes':deepcopy(r['data']['originals']['scenes']),'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,'actual_node_version_confirmed':False,
            'actual_scene':None,'actual_choice':None,'run_updated':False,'legacy_initial_scene_remains_unbound':True}
