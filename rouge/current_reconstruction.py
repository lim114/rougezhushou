"""Documentary reconstruction phases are not hidden server transitions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-reconstruction-344';DATA='rouge/data/current-reconstruction.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='9213c6351845a0fa0f929e5de9414f74a2d632fd674aaf3c24fe8aebd8e32432'
UNAVAILABLE='回滚文明的完整资料暂时无法核对，旧对话、交换/领取入口与图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json','rouge/data/relic-icon-receipt.json','research/p3-future-region-effects-300/prts-main-433770.html'}
        if m['schema']!='current_reconstruction_344_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_reconstruction_344_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def raw_role(v):
    return {'复原藏品':'choose_relic','复原零件':'choose_part','继续赞助它':'unknown_exchange','接过藏品':'claim_relic','接过零件':'claim_part','复原“文明”':'restore','等待结果':'claim_civil','离开':'leave','远离这个疯子':'leave','有点可疑':'decline'}.get(v['title'],'unknown')

def reference(event_id='reconstruction',naturals=None,source_request=None):
    if type(event_id)is not str or event_id!='reconstruction'or(naturals is not None and(type(naturals)is not int or naturals<0)):return None
    p=packet()
    if p is None:return None
    d=p['data'];event=deepcopy(d['event']);scenes=deepcopy(d['scenes']);choices=deepcopy(d['choices']);original=None
    if source_request is not None:
        if type(source_request)is not dict or set(source_request)!={'category','key'}or type(source_request['category'])is not str or type(source_request['key'])is not str:return None
        category,key=source_request['category'],source_request['key']
        if category not in('scenes','choices')or key not in d['originals'][category]:return None
        original=deepcopy(d['originals'][category][key])
        if category=='scenes':scenes['source-scene']={'id':'source-scene','label':'从原对话打开 · 后续未确认','description':original['description'],'source_scene_ids':[key],'choice_ids':[]}
        else:
            v=original;role=raw_role(v);next_id=v['nextSceneId']
            if next_id:scenes['source-next']={'id':'source-next','label':'原选项明确指定的后续对话','description':d['originals']['scenes'][next_id]['description'],'source_scene_ids':[next_id],'choice_ids':[]}
            scenes['source-choice']={'id':'source-choice','label':'从原选项打开 · 前置未确认','description':None,'source_scene_ids':[],'choice_ids':['source-choice']}
            choices['source-choice']={'id':'source-choice','title':v['title'],'description':v['description'],'scene_id':'source-choice','next_scene_id':'source-next'if next_id else None,'stage_ids':[],'role':role,'phase':None,'variant_ids':[key],'source_only':True,'natural_cost_reference':2 if role=='restore'else None,'reward_quantity_reference':1 if role in('claim_relic','claim_part')else None,'actual_variant':None,'actual_received':None,'document_next_is_original_next':next_id is not None}
        event['scene_ids']+=list(k for k in scenes if k not in d['scenes']);event['choice_ids']+=list(k for k in choices if k not in d['choices'])
    return {**p,'event':event,'scenes':scenes,'choices':choices,'declared_naturals_reference':naturals,'source_request':deepcopy(source_request),'requested_original':original,
            'requested_choice_association':d['original_choice_association'].get(source_request['key'])if source_request and source_request['category']=='choices'else None,
            'actual_inventory':None,'actual_consumed':None,'actual_received':None,'actual_choice':None,'actual_variant':None,'actual_reward_pool':None,'actual_remaining_exchanges':None,'actual_first_type':None}

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
    c=deepcopy(c);count=result['declared_naturals_reference'];c['listed_condition_match']=None if c['natural_cost_reference']is None or count is None else count>=c['natural_cost_reference']
    return c

def catalogue_allowed(result,sid,cid):
    c=choice_reference(result,sid,cid);return bool(c and c['role']in('choose_relic','continue_relic'))

def shows_reward(result,sid,cid):
    c=choice_reference(result,sid,cid);return bool(c and c['role']=='claim_civil')

def player_text(result,sid,cid=None):
    lines=['【正在查阅】回滚文明','分别查阅交出物品、领取结果和是否继续；不代表本局已经交换、支付或领取。',
           '','【出现与交换条件参考】文献排除第Ⅰ、Ⅵ层；完整出现资格仍需核对。',
           '“声带”允许交换零件；“手掌”使交换次数增加1次，且再次交换须与首次同为收藏品或同为零件。',
           '实际科技、首次类型和剩余次数未知；本页展示全部文献分支，不代表本次全都可选。']
    s=result['scenes'].get(sid)
    if s is None:return '\n'.join(lines+['','请选择要查阅的位置。'])
    lines+=['','【查阅位置】'+scene_label(result,sid)]
    if s['description']:lines+=['','【对话原文】',version._plain(s['description'])]
    if sid.startswith('source-'):
        lines+=['','【原始条目范围】只显示本次打开的完整原件；同文案或相邻编号不证明前置、首次/再次交换及实际选项组合。']
        if sid in('source-scene','source-next'):lines+=['此原对话没有已证明的后续菜单，不借其它同文案记录拼接。']
        if result['requested_choice_association']=='full_literal_sacrifice_candidate':lines+=['交换候选与文献全文相符，但原件没有指定下一段；不据此确定游戏中的分支归属或实际转换结果。']
    c=choice_reference(result,sid,cid)
    if c:
        role=c['role'];lines+=['','【查阅选项】'+c['title'],version._plain(c['description'])]
        if role in('choose_relic','continue_relic','choose_part','continue_part','unknown_exchange'):
            lines+=['','【交出与换入】这是提供物品的阶段，不等于已经得到新物品。','实际交出成员、消耗时点及换入候选仍未知；相同文案的多份记录不表示一次得到多件。']
            if role in('choose_relic','continue_relic'):lines+=['可另开当前收藏品“能否交出”目录；该目录不是奖励池，也不表示本局持有。']
            if role in('choose_part','continue_part'):lines+=['零件与收藏品是两类交换物；零件里的自然物、加工品、概念体不能替代首次交换类型。']
            if role.startswith('continue_'):lines+=['本段是文献中的再次交换；须核对“手掌”与首次类型，不视为可以无限循环。']
            if role=='unknown_exchange':lines+=['这份“继续赞助”原件未说明之前交换的是收藏品还是零件；不按编号指定类型，也不开放仅限藏品的目录入口。']
        elif role in('claim_relic','claim_part'):
            label='收藏品'if role=='claim_relic'else'零件';lines+=['','【单次领取参考】本选项原文为获得1件'+label+'；不按候选记录份数倍增。','领取与再次交出是不同阶段；不把首次和再次的奖励合并成一次两件。','具体领取物及完整池未知；稀有度影响候选，不代表同稀有度的所有物品均能换到。']
        elif role=='restore':
            count=result['declared_naturals_reference'];match=c['listed_condition_match']
            lines+=['','【明确代价】随机2件自然物；不是任意2件零件，也不指定丢弃成员或顺序。',
                    '【仅本页自然物件数对照】'+('尚未确认。'if count is None else str(count)+'件。'),
                    '只核对这条明确代价，完整资格与实际库存仍未知。'if match is not False else'少于2件，不打开本条后续；其它资料仍可独立查阅。']
        elif role=='claim_civil':
            item=next(iter(result['data']['originals']['items'].values()));lines+=['','【具名领取参考】'+item['name'],version._plain(item['usage']),
                    '这是复原“文明”后的领取说明，不再次消耗2件自然物；原文没有独立给出领取件数。',
                    '不自动记为已持有、已削弱敌人或已解锁后续结局，也不按其它领取选项的1件补数量。']
        else:lines+=['','【结束参考】只查阅对应离开或停止交换的对话，不附加其它分支奖励。']
        if c['source_only']:lines+=['','保留该原件明确后续；没有指定后续的交换项不借文献顺序补成原件跳转。']
        else:lines+=['','【文献分支范围】按完整表的菜单与分支分别阅读；同文候选不等于本次实际选项。',
                      '原交换项没有指定下一段，这里的按钮只沿文献翻页，不表示已恢复游戏实际转换流程。'if not c['document_next_is_original_next']else'原件明确后续与这段文献相符，但不自动选定本次实际变体。']
        if c['next_scene_id']:lines+=['','【可翻阅的资料后续】'+scene_label(result,c['next_scene_id']),'仅翻阅，不交出、不领取、不操作游戏。']
    elif s['choice_ids']:lines+=['','请选择本段的一条分支；收藏品、零件、复原文明与离开各自独立。']
    else:lines+=['','本段没有已证明的进一步选项，不自动返回或拼接其它同文原件。']
    lines+=['','【仍未知】实际交出物、换入池、科技及次数、本局领取、动态阶段与服务器完整资格。',
            '不修改本局、资源、地图或预计数值；不操作游戏，不给路线建议、排序与概率。']
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
    if type(record) is not dict or record.get('id')!='community_group_025':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'回滚文明','reader':'reconstruction344',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
