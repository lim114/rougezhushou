"""Documented sand events, local condition comparison, no live eligibility claim."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-sand-325';DATA='rouge/data/current-sand-reference.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='30ee5abd60d71a7ebb02ef2176efe7ab220dbede58bd30a8ba966549172a85ff'
UNAVAILABLE='线人与好奇心与死的资料暂时无法核对，旧选项和关联入口已清除；恢复后请重新选择。'
LABELS={'scene_ro6_bomb1_enter':'最初对话 · 线人','scene_ro6_bomb1_1':'说明梅兰德身份后的对话','scene_ro6_bomb1_2':'独立探险家的对话','scene_ro6_bomb1_3':'联合政府身份的对话','scene_ro6_end1_enter':'最初对话 · 好奇心与死','scene_ro6_end1_1':'花费源石锭修正位置后的对话','scene_ro6_end1_2':'查看戏法后的对话'}
DEFAULT_CONTEXT={'scope':'current','floor':None,'node_type':'unknown','cleared_reboot':None,'has_alpha':None,'has_beta':None,'target_marked':None,'gold':None}

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-tables.html',PACK+'/ending-section-433770.html','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json'}
        if m['schema']!='current_sand_325_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_sand_325_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_received':None,'actual_marked':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def context(values=None):
    if values is not None and type(values)is not dict:raise ValueError('请使用本页支持的条件。')
    out=deepcopy(DEFAULT_CONTEXT)
    if values:
        if set(values)-set(out):raise ValueError('存在未支持的条件。')
        out.update(values)
    if out['scope']not in('current','history')or out['node_type']not in('unknown','不期而遇','命运所指','other'):raise ValueError('查看范围或节点类型未支持。')
    if out['floor']is not None and(type(out['floor'])is not int or out['floor']not in range(1,7)):raise ValueError('层数应为1至6或未知。')
    if out['gold']is not None and(type(out['gold'])is not int or out['gold']<0):raise ValueError('源石锭应为非负整数或未知。')
    for key in('cleared_reboot','has_alpha','has_beta','target_marked'):
        if out[key]is not None and type(out[key])is not bool:raise ValueError('状态应为是、否或未知。')
    return out

def reference(event_id='informer',values=None):
    if type(event_id)is not str or event_id not in('informer','curiosity'):return None
    c=context(values);r=packet()
    if r is None:return None
    d=r['data'];event=next(e for e in d['events']if e['id']==event_id)
    return {**r,'event':deepcopy(event),'scenes':{k:deepcopy(d['scenes'][k])for k in event['scene_ids']},'choices':{k:deepcopy(d['choices'][k])for k in event['choice_ids']},'context':c,'context_is_local_reference_only':True}

def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    if not((category=='scenes'and key in LABELS)or(category=='choices'and key in('choice_ro6_bomb1_1','choice_ro6_bomb1_2','choice_ro6_bomb1_3','choice_ro6_end1_1','choice_ro6_end1_2'))or(category=='relics'and key in('rogue_6_relic_final_1','rogue_6_relic_final_2'))):return None
    r=packet()
    if r is None:return None
    d=r['data'];cid=key if category=='choices'else'choice_ro6_bomb1_1'if category=='relics'and key=='rogue_6_relic_final_1'else None
    sid=d['choices'][cid]['scene_id']if cid else key if category=='scenes'else'scene_ro6_end1_enter'
    return {'event_id':d['scenes'][sid]['event_id'],'scene_id':sid,'choice_id':cid}

def scene_label(result,sid):return LABELS.get(sid,'请选择对话')

def _all(rows):return False if any(x['matches']is False for x in rows)else None if not rows or any(x['matches']is None for x in rows)else True
def _any(a,b):return True if a is True or b is True else False if a is False and b is False else None

def condition_checks(result,cid=None):
    c=result['context'];event=result['event']['id'];rows=[]
    def add(text,value):rows.append({'label':text,'matches':value})
    add('处于第二至第四层'if event=='informer'else'处于第五层',None if c['floor']is None else c['floor']in((2,3,4)if event=='informer'else(5,)))
    add('节点是不期而遇'if event=='informer'else'节点是命运所指',None if c['node_type']=='unknown'else c['node_type']==('不期而遇'if event=='informer'else'命运所指'))
    if event=='curiosity':
        add('已完成强制重启，解锁相关选项和收藏品',c['cleared_reboot']);add('至少持有沙盘α、沙盘β中的一种',_any(c['has_alpha'],c['has_beta']))
    if cid=='choice_ro6_bomb1_1':add('已完成强制重启，解锁相关选项和收藏品',c['cleared_reboot'])
    if cid=='choice_ro6_end1_1':
        add('窥视箱中尚未被标记',None if c['target_marked']is None else not c['target_marked']);add('至少有50源石锭',None if c['gold']is None else c['gold']>=50)
    return rows

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and cid in s['choice_ids']and c['scene_id']==sid):return None
    out=deepcopy(c);out['documented_checks']=condition_checks(result,cid)
    ctx=result['context'];conflict=result['event']['id']=='curiosity'and ctx['has_alpha']is True and ctx['has_beta']is True and ctx['target_marked']is False
    matched=_all(out['documented_checks'])
    out['listed_condition_match']=None if ctx['scope']=='history'else False if matched is False else None if conflict else matched
    out['contradictory_marker_declaration']=conflict;out['actual_eligible']=None;return out

def player_text(result,sid,cid=None):
    if sid not in result['scenes']:return '请选择文献情景；这里不表示本局已经到达。'
    d=result['data'];o=d['originals'];c=choice_reference(result,sid,cid);ctx=result['context'];lines=['【正在查阅】'+result['event']['title'],scene_label(result,sid),'','【当前对话】',version._plain(o['scenes'][sid]['description'])]
    if c:
        original=o['choices'][cid];lines+=['','【查看的选项】'+original['title'],'【原文写明】',version._plain(original['description'])]
        reward=c['reward']
        if reward:
            if reward['item_id']:lines+=['','【具名获得】沙盘α',version._plain(o['items'][reward['item_id']]['usage']),'本选项没有明确写领取件数，不自动补成1件；不改本局持有或部署费用。']
            else:lines+=['','【随机获得】1件'+reward.get('quality','')+reward['kind'],'可获得的具体名单、实际发放方式尚未核验，不能指定成某件藏品或零件。']
        if c['cost_gold']==50:lines+=['','【标记与代价】','文献说明：尚未标记窥视箱中时，可支付50源石锭标出目标。这是寻找目标的标记选项，不是再获得一件收藏品，也不会立即开始作战。']
        if c['next_scene_id']:lines+=['','【明确的后续对话】',scene_label(result,c['next_scene_id'])]
    checks=condition_checks(result,cid if c else None);lines+=['','【文献条件对照 · 仅本页】']
    for row in checks:lines+=[{True:'已知符合：',False:'已知不符：',None:'尚未确认：'}[row['matches']]+row['label']]
    if ctx['scope']=='history':lines+=['按历史资料查阅；当前持有、层数或源石锭不用于否定过去已经看见的事件。']
    elif _all(checks)is False:lines+=['至少一项文献条件不符，不将它作为本局可用分支；仍可阅读，后续按钮不可用。']
    else:lines+=['即使列出条件都符合，也只能说明符合已记载条件，不能证明服务器完整资格或本局实际可选。']
    if result['event']['id']=='curiosity':
        lines+=['','【目标怎样区分】','文献记载：在相关第五层生成情形中，三个命运所指为两个好奇心与死、一个窥视箱中，不能仅凭相同外观区分；这不是当前所有第五层的无条件规则。','同时持有沙盘α和沙盘β时，窥视箱中会有“谜题与谜底”标记。仅持有一种不等于已经标记；先核对实际标记，不推算生成概率。']
        if ctx['has_alpha']is True and ctx['has_beta']is True and ctx['target_marked']is False:lines+=['你声明同时持有两种沙盘，却又声明目标未标记，与文献规则不一致；不会自动改写任一信息。']
    else:lines+=['','【另一件沙盘】沙盘β',version._plain(o['items']['rogue_6_relic_final_2']['usage']),'文献提到其可在第一至第三层诡意行商以1源石锭出售；不保证商店有货，不把随机商店库存当本局事实。']
    if not result['scenes'][sid]['choice_ids']:lines+=['','文献未列本段的专属后续选择，不自动连接别处的确认或战斗。']
    lines+=['','【相关资料】窥视箱中','下方入口只打开该事件的条件与作战资料，不是当前选项立即跳转，也不会在游戏中移动。','','【范围与未知】','使用注明版本的文献与当前固定国服记录；完整出现前置、随机池与实际发放仍未完整核验。当前条件不写入本局，不执行扣费、领奖或数值修正，不提供路线建议。']
    return '\n'.join(lines)
