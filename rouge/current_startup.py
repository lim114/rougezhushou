"""Current action support pool, with explicit inherited sources kept separate."""
from pathlib import Path, PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import expansion_reference as version
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-startup-350';DATA='rouge/data/current-startup.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='a51932ca6907a2b5c089822f09d22f83a4f7af496bf7728c459ba5c38ce1e164';SCENE='scene_ro6_startbuff_enter'
UNAVAILABLE='行动奖励的当前资料暂时无法核对，旧选项与图片已清除；恢复后请重新选择。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);d=json.loads((ROOT/DATA).read_bytes())
        expected={DATA,PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','rouge/data/original-entry-reference.json',*['rouge/data/relic-icons/rogue_6_start_'+str(i)+'.png'for i in range(1,7)]}
        if m['schema']!='current_startup_350_manifest_v1'or m['game_commit']!=version.NEW_COMMIT or set(m['files'])!=expected:return None
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            if any(a.is_symlink()for a in p.parents if a!=ROOT and ROOT in a.parents):return None
            b=p.read_bytes()
            if len(b)!=pin['bytes']or sha256(b).hexdigest()!=pin['sha256']:return None
        v=version.packet()
        if v is None or d['schema']!='current_startup_350_v1'or d['game_commit']!=version.NEW_COMMIT:return None
        cur=v['current']['details']
        for table,key in(('choices','choices'),('scenes','choiceScenes'),('items','items'),('relics','relics')):
            if any(cur[key].get(k)!=r for k,r in d['originals'][table].items()):return None
        if len(d['choices'])!=12 or len(d['regular_ids'])!=6 or len(d['inherited_ids'])!=6:return None
        for cid,row in d['choices'].items():
            if row['id']!=cid or row['scene_id']!=SCENE or row['original']!=cur['choices'][cid]:return None
            if row['kind']=='inherited':
                buffs=cur['relics'][row['legacy_id']]['buffs']
                if row['force_add_choice_buff']not in buffs or row['original']['isHiddenChoice']is not True:return None
                board={b['key']:b['valueStr']for b in row['force_add_choice_buff']['blackboard']}
                if board!={'choice_id':cid,'scene_ids':SCENE}:return None
        return {'data':d,'source_identity':(MANIFEST_SHA256,v['source_identity']),'actual_eligible':None,'actual_received':None,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError):return None

def reference(event_id='startup',previous_regions=None,mode=None,gold=None,inherited=None,group='all'):
    if event_id!='startup'or group not in('all','regular','inherited'):return None
    if any(v is not None and(type(v)is not int or v<0)for v in(previous_regions,gold)):return None
    if mode not in(None,'NORMAL','OTHER')or inherited not in(None,'none',*[f'choice_ro6_startbuff_{n}'for n in range(7,13)]):return None
    p=packet()
    if p is None:return None
    d=p['data'];ids=d['event']['choice_ids']if group=='all'else d[group+'_ids'];scenes=deepcopy(d['scenes']);scenes[SCENE]['choice_ids']=list(ids)
    return {**p,'event':deepcopy(d['event']),'scenes':scenes,'choices':deepcopy(d['choices']),
            'declared':{'previous_regions':previous_regions,'mode':mode,'gold':gold,'inherited':inherited,'group':group},
            'actual_displayed_choice_ids':None,'actual_original_parent_script_restored':False}

def locate(category,key):
    if type(category)is not str or type(key)is not str:return None
    p=packet()
    if p is None:return None
    if category=='scenes'and key==SCENE:return {'event_id':'startup','scene_id':SCENE,'choice_id':None}
    if category=='choices'and key in p['data']['choices']:return {'event_id':'startup','scene_id':SCENE,'choice_id':key}
    if category=='relics':
        ids=[cid for cid,row in p['data']['choices'].items()if row['kind']=='inherited'and row['item_id']==key]
        if len(ids)==1:return {'event_id':'startup','scene_id':SCENE,'choice_id':ids[0]}
    return None

def scene_label(result,sid):return '开始探索前 · 行动奖励'if sid==SCENE else'请选择查阅位置'

def choice_reference(result,sid,cid):
    if sid!=SCENE or type(cid)is not str or cid not in result['scenes'][SCENE]['choice_ids']:return None
    row=deepcopy(result['choices'][cid]);v=result['declared'];checks=[{'label':'上一局已通过至少两个区域','matches':None if v['previous_regions']is None else v['previous_regions']>=2}]
    checks.append({'label':'常规行动资料范围','matches':True if v['mode']=='NORMAL'else None})
    if row['kind']=='inherited':
        checks[-1]['matches']=None if v['mode']is None else v['mode']=='NORMAL'
        checks.append({'label':'上一局明确继承了这一项额外支援','matches':None if v['inherited']is None else v['inherited']==cid})
    if cid=='choice_ro6_startbuff_3':checks.append({'label':'足够支付6源石锭','matches':None if v['gold']is None else v['gold']>=6})
    row['checks']=checks;row['listed_condition_match']=False if any(c['matches']is False for c in checks)else None if any(c['matches']is None for c in checks)else True
    row['actual_eligible']=None;row['actual_received']=None;return row

def player_text(result,sid,cid=None):
    if sid!=SCENE:return '请选择开始探索时的行动奖励。这里不列为普通地图自然事件。'
    lines=['【行动奖励 · 当前固定版本】','这是开始探索前的支援资料，不是普通探索节点。上一局通过的区域数不是本局层数或最高抵达层号。',
           '常规候选库有6项，文献说明每次展示其中3项；继承带来的额外蓝色支援另有1项。这里的资料目录不等于本次游戏菜单，也不把12项合并领取。', '',version._plain(result['data']['originals']['scenes'][SCENE]['description'])]
    row=choice_reference(result,sid,cid)
    if row:
        original=row['original'];lines+=['','【查看的支援】'+original['title'],'【代价与效果原文】',version._plain(original['description']),'','【本页条件对照】']
        lines += [c['label']+'：'+('未知'if c['matches']is None else'相符'if c['matches']else'不符')for c in row['checks']]
        if row['kind']=='inherited':
            lines+=['','【继承来源】六种额外支援的原继承记录同名，但明确指向不同选项，按准确对应分别保留。',
                    '当前持有的襁褓生灵不能证明上一局继承了哪一项；需要独立的继承记录。这里只对照说明，不把增益代入本局。']
        else:lines+=['','【候选范围】这六项与旧文献的完整原选项记录一致；常规项没有直接场景指针，仍只作为文献候选，实际抽取与菜单未知。']
        if cid=='choice_ro6_startbuff_4':lines+=['退行补偿消耗的是2目标生命上限，不是当前生命值；最低上限、可选底限与实际扣除仍未知。']
        if cid=='choice_ro6_startbuff_6':lines+=['巢寄生减少零件箱容量；是否存在最低容量限制尚未核验，不把容量不足时的行为补成已知。']
        if cid=='choice_ro6_startbuff_12':lines+=['三个随机收藏品写明在进入血色空脉时获得；不在开局提前计入库存，也不补具体奖励池。']
        if cid=='choice_ro6_startbuff_10':lines+=['各区域成长、重复获得与丢失后的实际数值仍需另外核验；这里不新增攻击或生命的计算假设。']
    else:lines+=['','选择一条支援，查看它自己的代价与效果。不同选项不合计收益，也不推荐选择。']
    lines+=['','【范围与未知】固定国服10月16日资料；已列条件相符仍不保证实际可选。完整获取池、实际抽取、隐藏资格、扣除/领取与当前服务器执行仍未知。',
            '仅局外查阅，不操作游戏、不扣资源、不改本局记忆或计算，不推荐路线、不提供生成概率。']
    return '\n'.join(lines)
