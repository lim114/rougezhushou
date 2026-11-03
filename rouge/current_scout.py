"""Current scout reading: no actual departure, return, resource or run mutation."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-scout-342';DATA='rouge/data/current-scout.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='bc6ef7f9eee129bd77625b3c79cce0652568b8213c82a0220d806880f3876103'
RETURN_FILES={'rouge/data/expedition-results.json','research/p3-expedition-results-297/source-manifest.json','research/p3-expedition-results-297/prts-events-427904.html','research/p3-expedition-results-297/prts-events-440271.html','research/p3-expedition-results-297/prts-main-433770.html','research/p3-expedition-results-297/original-records.json','research/p3-expedition-results-297/dom-bindings.json'}
UNAVAILABLE='未涉足之树的完整资料暂时无法核对，旧对话、归来说明和图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/source-receipt.json',PACK+'/documented-section.html',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/baseline-topic.json','rouge/data/node-catalog.json',*RETURN_FILES}
        if m['schema']!='current_scout_342_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
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
        if current is None or data['schema']!='current_scout_342_v1':return None
        for group,table in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('stages','stages')):
            if any(current['current']['details'][table].get(k)!=v for k,v in data['originals'][group].items()):return None
        if any(current['current']['details']['gameConst'].get(k)!=v for k,v in data['current_game_const'].items()):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),'actual_eligible':None,'actual_entered':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None

def reference(event_id='scout'):
    if type(event_id)is not str or event_id!='scout':return None
    p=packet()
    if p is None:return None
    d=p['data']
    return {**p,'event':deepcopy(d['event']),'scenes':deepcopy(d['scenes']),'choices':deepcopy(d['choices']),
            'actual_operator':None,'actual_returned':None,'actual_received':None,'actual_advanced':None,'actual_hope':None,'actual_return_clock':None,'actual_selectable':None}

def locate(category,key):
    if type(category)is not str or type(key)is not str or category not in('scenes','choices'):return None
    r=reference()
    if r is None:return None
    if category=='scenes'and key in r['scenes']:return {'scene_id':key,'choice_id':None}
    if category=='choices'and key in r['choices']:return {'scene_id':r['choices'][key]['scene_id'],'choice_id':key}
    return None

def scene_label(result,sid):
    if sid==result['event']['entry_scene_id']:return '最初对话 · 未涉足之树'
    role=next((c['role']for c in result['choices'].values()if c['next_scene_id']==sid),None)
    return {'inside':'探索内部后的对话','origin':'探索源头后的对话','rest':'休息后的对话'}.get(role,'请选择要查阅的对话')

def choice_reference(result,sid,cid):
    if type(sid)is not str or type(cid)is not str:return None
    s=result['scenes'].get(sid);c=result['choices'].get(cid)
    if not(s and c and c['scene_id']==sid and cid in s['choice_ids']):return None
    return deepcopy(c)

def shows_return_item(result,sid,cid=None):
    if sid not in result['scenes']:return False
    c=choice_reference(result,sid,cid)
    return bool(c and c['role']in('origin','confirm'))

def player_text(result,sid,cid=None):
    lines=['【正在查阅】未涉足之树','固定版本的事件与归来资料；本页不会派出干员，也不表示已经归来或领取。',
           '','【出现条件参考】先行一步的文献范围为第Ⅱ、Ⅲ、Ⅳ层；文献排除第Ⅰ、Ⅴ、Ⅵ层。',
           '“探索源头”的结局相关选项与收藏品，资料要求先完成结局“强制重启”。',
           '本页仍展示资料供查阅；不代表当前账户已解锁，也不代表同一次事件全部选项都可选。完整服务器资格仍需核对。']
    if sid not in result['scenes']:return '\n'.join(lines+['','请选择要查阅的对话。'])
    lines+=['','【当前对话】'+scene_label(result,sid),version._plain(result['data']['originals']['scenes'][sid]['description'])]
    c=choice_reference(result,sid,cid)
    if c:
        role=c['role'];lines+=['','【查阅选项】'+c['title'],version._plain(c['description'])]
        if role in('inside','origin'):
            lines+=['','【派出与归来】派出1名同伴；暂时不能编入队伍。','【当前版本的归来提示】'+result['data']['current_game_const']['expeditionSelectDescFormat'].replace('{0}','（所选干员）'),'社区资料表述为下一层开始时归来；进入特殊区域是否等同下一层、实际返回时刻及当前是否已返回仍未知。','本页不选择人选，不更改已招募队伍、培养或库存。']
            if role=='inside':lines+=['','【探索内部：归来参考】只说明会带回物资；完整奖励池、具体数量和培养变化仍未知。','不套用探索源头的2希望与怦然信标，也不因为进入电梯就跳转到某张战斗地图。']
        elif role=='rest':
            lines+=['','【当场结果参考】获得2希望；此分支不派出干员。','不附加探索源头归来时的另2希望、怦然信标或加工品；本局最终希望与上限仍未计算。']
        elif role=='confirm':
            lines+=['','【会合确认】这是探索源头后资料中的确认项，不是再次派出、再次休息或立即领奖。','原件没有下一段对话或战斗地图，不拼出额外后续。图标中的目标生命字段不证明会回复生命。']
        if role in('origin','confirm'):
            item=next(iter(result['data']['originals']['items'].values()))
            lines+=['','【探索源头：归来参考】干员不会被进阶，归来时带来2希望与收藏品“'+item['name']+'”。','归来奖励不与“休息”的当场2希望相加；收藏品实际领取件数和是否已持有仍未知。','【收藏品效果】'+version._plain(item['usage']),'这是当前固定版本物品说明，不表示已经改变队伍或敌人的预计面板。','【资料说明与按钮的区别】“通过此方式送出的干员不会被进阶……”是归来解释，不作为另一个可点击的事件选项。']
        if role in('inside','origin','confirm'):
            lines+=['','【长期科技“喙”】通用资料说明可在归来时额外获得随机加工品。','它与源头分支“仅获得”的关系尚未核验，不额外加算；是否点亮、实际成员与数量、完整池仍未知。']
        if c['next_scene_id']:lines+=['','【可翻阅的后续】'+scene_label(result,c['next_scene_id']),'按钮只翻阅资料，不执行游戏选择。']
    elif result['scenes'][sid]['choice_ids']:lines+=['','请选择一个分支查看；探索内部、探索源头和休息是不同选择，不累计成一份总奖励。']
    else:lines+=['','本表没有列出更多选项；不推断再次派出或自动领奖。']
    lines+=['','【仍需核对】当前服务器完整资格、实际人选、返回时刻、领取和完整奖励池。','仅局外查阅，不改本局、资源、地图或计算；不操作游戏，不提供路线建议与概率。']
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
    if type(record) is not dict or record.get('id')!='community_group_024':return None
    from .current_node_readers import same
    from . import node_catalog
    r=reference()
    if r is None:return None
    row=r['data']['catalogue_binding']
    if any(k not in record or not same(record[k],v)for k,v in row['expected_summary'].items()):return None
    if 'scenes'in record and not same(record['scenes'],row['expected_legacy_event']['scenes']):return None
    if not same(node_catalog._event(record['id']),row['expected_legacy_event']):return None
    return {**deepcopy(row),'legacy_event_id':record['id'],'title':'未涉足之树','reader':'scout342',
            'current_event':deepcopy(r['event']),'current_original_scenes':deepcopy(r['data']['originals']['scenes']),
            'current_source_identity':json.loads(json.dumps(r['source_identity'])),
            'source_identity':(MANIFEST_SHA256,json.loads(json.dumps(r['source_identity']))),'reference_only':True,
            'actual_node_version_confirmed':False,'actual_scene':None,'actual_choice':None,'run_updated':False}
