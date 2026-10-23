"""Version-separated current CN reference. Never mutates the baseline calculator."""
from copy import deepcopy
from hashlib import sha256,sha1
from pathlib import Path,PurePosixPath
import json,re

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-expansion-313'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='490e70a7576411df0474812ad449a7e7910cbb3e93d095f0bf633c1e67e135e2'
OLD_COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
NEW_COMMIT='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'
NOTICE=('资料基准：国服2026年10月16日“内容拓展·一”。本页提供关卡、事件、物品及探索设置的固定资料；'
        '是否在本局出现、能够选择或已经领取，须按对应条件确认。涉及计算时，以该项结果旁注明的适用范围为准。')
LEGACY_NOTICE='本页计算使用更新前的固定基准；关卡原图、敌人及事件请到“战斗预览”“节点事件”等对应栏目查看。新版本的数值计算和位置映射尚未完整适配。'
UNAVAILABLE='更新资料暂时无法核对，旧条目、后续入口与图片已清除。恢复后请重新选择。'
CATEGORIES=(('stages','关卡与变体'),('scenes','事件场景'),('choices','事件选项与去向'),
            ('relics','收藏品说明与改动'),('scrap','零件'),('squads','分队资料（含强化档位）'),
            ('difficulty','保密等级'),('regions','区域'),('endings','结局'),('initial','初始状态'))


def _file(name):
    if type(name)is not str:raise ValueError('Public source name required')
    rel=PurePosixPath(name)
    if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name or rel.as_posix()!=name:raise ValueError('Unsafe source path')
    path=ROOT.joinpath(*rel.parts)
    if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular public source required')
    for p in path.parents:
        if p==ROOT:break
        if p.is_symlink():raise ValueError('Linked source parent refused')
    return path


def packet():
    try:
        raw=_file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);objects={}
        if manifest['schema']!='expansion_313_source_manifest_v1' or manifest['baseline_commit']!=OLD_COMMIT or manifest['current_commit']!=NEW_COMMIT:return None
        expected={PACK+'/'+n for n in('baseline-topic.json','current-topic.json','sources.json','map-images.json')}
        if set(manifest['files'])!=expected:return None
        for name,pin in manifest['files'].items():
            raw=_file(name).read_bytes()
            if type(pin['bytes'])is not int or len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(raw)
        old=objects[PACK+'/baseline-topic.json'];new=objects[PACK+'/current-topic.json']
        if set(old)!=set(new)or set(new)!={'topics','details','modules','customizeData'}:return None
        return {'baseline':old,'current':new,'images':objects[PACK+'/map-images.json'],
                'source':objects[PACK+'/sources.json'],'source_identity':MANIFEST_SHA256,
                'actual_eligibility':None,'actual_rewards':None,'current_server_verified':False,
                'run_state_updated':False,'baseline_calculation_migrated':False,'position_mapping_verified':False}
    except(OSError,ValueError,KeyError,TypeError,AttributeError,UnicodeError,RecursionError):return None


def _tables(snapshot):
    d=snapshot['details'];scrap=snapshot['modules']['scrap'];items=d['items']
    relics={k:{'item':items.get(k),'effect':v}for k,v in d['relics'].items()}
    parts={k:{'item':items.get(k),'part':next((table[k]for table in
           (scrap['moveScrapData'],scrap['goodsScrapData'],scrap['passiveScrapData'])if k in table),None)}for k in scrap['scrapItemToType']}
    return {'stages':d['stages'],'scenes':d['choiceScenes'],'choices':d['choices'],'relics':relics,'scrap':parts,
            'squads':{k:{'item':items.get(k),'reference':v}for k,v in d['bandRef'].items()},
            'difficulty':{str(v['modeDifficulty'])+'|'+str(v['grade']):v for v in d['difficulties']},
            'regions':d['zones'],'endings':d['endings'],
            'initial':{json.dumps([v['modeId'],v['modeGrade'],v.get('predefinedId'),v.get('predefinedStyle')],ensure_ascii=True,separators=(',',':')):v for v in d['init']}}


def _plain(value):
    if value is None:return ''
    text=str(value).replace('\\n','\n').replace('\r\r\n','\n').replace('\r\n','\n')
    # Only formatting is stripped. Angle-bracket game names (e.g. <城防路障>) are content.
    text=re.sub(r'<@[^>]+>|</>|</?(?:color|size|b|i)(?:=[^>]*)?>','',text)
    return text.replace('\u00a0',' ')


def rows(category,*,changes_only=True,reference=None):
    if type(category)is not str or category not in dict(CATEGORIES)or type(changes_only)is not bool:return []
    reference=packet()if reference is None else reference
    if reference is None:return []
    old,new=_tables(reference['baseline'])[category],_tables(reference['current'])[category]
    result=[]
    for key,value in new.items():
        changed=key not in old or old[key]!=value
        item=value.get('item')or{}
        name=value.get('name')or value.get('title')or item.get('name')
        if category=='difficulty':name=(name or'保密等级')+'·'+str(value['grade'])
        if not name and category=='initial':name=('初始状态 · 常规等级'+str(value['modeGrade'])if value['modeId']=='NORMAL'else'初始状态 · 月度小队')
        name=_plain(name)or'未命名效果条目'
        label=name
        if category=='stages':label+=' · '+('紧急'if value['isElite']else'首领'if value['isBoss']else'普通')
        if category=='squads'and value['reference'].get('bandLevel'):label+=' · 强化档位'
        result.append({'id':key,'name':name,'label':label,'change':'added'if key not in old else'changed'if changed else'unchanged',
                       'value':deepcopy(value),'before':deepcopy(old.get(key)),'category':category})
    # Original order is retained; duplicate names are separate real source entries.
    totals={label:sum(r['label']==label for r in result)for label in {r['label']for r in result}}
    positions={}
    for row in result:
        label=row['label'];positions[label]=positions.get(label,0)+1
        if totals[label]>1:row['label']+=' · 资料'+str(positions[label])
    return [row for row in result if not changes_only or row['change']!='unchanged']


def detail(category,key):
    if type(key)is not str:return None
    ref=packet()
    if ref is None:return None
    found=next((r for r in rows(category,changes_only=False,reference=ref)if r['id']==key),None)
    if found is None:return None
    d=ref['current']['details'];value=found['value'];lines=[found['name'],NOTICE]
    lines+=['','资料变化：'+{'added':'新增条目','changed':'原条目有改动','unchanged':'在本次对照范围内未改动'}[found['change']]]
    next_scene=None;award=None;image=None
    if category=='stages':
        lines+=['关卡说明：'+_plain(value.get('description'))]
        if value.get('eliteDesc'):lines+=['紧急说明：'+_plain(value['eliteDesc'])]
        lines+=['同名条目可能是不同关卡变体，不能借用另一条目的敌人、路线或掉落。',
                '原图仅供查看；当前尚未校准坐标。可打开本版本关卡预览，查看已接入的敌人、出怪和条件奖励；完整修正面板、全局时间轴与奖励池仍待核验。']
        image=ref['images']['images'].get(key)
    elif category=='scenes':
        lines+=['场景内容：'+_plain(value.get('description')),
                '本场景出现前的完整条件和可选选项列表尚未恢复；不能按名称或编号拼接选项。']
        incoming=[v['title']for v in d['choices'].values()if v.get('nextSceneId')==key]
        if incoming:lines+=['资料中写明后续抵达这里的选项：'+'；'.join(incoming),'这些是指向本场景的选项，不是本场景内的选项。']
    elif category=='choices':
        lines+=['选项说明：'+_plain(value.get('description')),'出现前条件、来自哪个前置场景和本局是否可选：仍待核对。']
        target=value.get('nextSceneId')
        if target in d['choiceScenes']:
            next_scene={'id':target,'title':d['choiceScenes'][target]['title']}
            lines+=['原资料写明的后续场景：'+next_scene['title']+'。可手动跳转阅读；不表示已经选中或抵达。']
        item_id=(value.get('displayData')or{}).get('itemId')
        if item_id in d['items']and value['displayData'].get('effectHintType')=='ITEM':
            award={'id':item_id,'name':d['items'][item_id]['name'],'usage':d['items'][item_id].get('usage')}
            lines+=['关联物品提示：'+award['name'],'用途：'+_plain(award['usage']),
                    '这是该选项的物品提示，不能仅凭提示认定已领取；实际成本和数量以选项原文及完整机制为准。']
        if (value.get('displayData')or{}).get('funcIconId')=='battle':lines+=['本选项提示作战，但尚未取得明确关卡绑定，不能随意跳转到同名或猜测关卡。']
    elif category in('relics','scrap','squads'):
        item=value.get('item')or{}
        lines+=['用途：'+_plain(item.get('usage')),'获取或解锁说明：'+(_plain(item.get('unlockCondDesc'))or'此条目未给出独立解锁说明。')]
        if category=='scrap'and value.get('part'):lines+=['零件说明：'+_plain(value['part'].get('scrapDesc'))]
        if category=='relics':lines+=['此分类保留来源中的完整效果条目，也包含分队等效果，条目数不等于可持有收藏品数量。']
        lines+=['本页为固定资料阅读，未自动确认本局持有、强化档位、触发次数或将此新效果加入计算。']
    elif category=='difficulty':
        lines+=['新增或调整规则：'+_plain(value.get('ruleDesc')),'解锁说明：'+_plain(value.get('unlockText')),
                '旧计算页尚未按本更新完成全量迁移；不能据此把该等级的完整敌人或干员结果标成已核验。']
    elif category=='initial':
        for field,name in (('initialHp','目标生命'),('initialGold','源石锭'),('initialPopulation','希望'),('initialSquadCapacity','可携带干员'),('initialShield','护盾')):
            if field in value:lines+=[name+'：'+str(value[field])]
        lines+=['这是所选模式与等级的初始资料，不是当前局数值；分队、科技和收藏品仍可影响实际初始状态。']
    else:
        lines+=[_plain(value.get('description')or value.get('desc'))]
        if value.get('endingDescription'):lines+=['区域结束文字：'+_plain(value['endingDescription'])]
        lines+=['区域和结局说明不证明地图模板、进入条件或本局进度已核验。']
    return {'row':found,'player_text':'\n'.join(lines),'source_identity':ref['source_identity'],
            'next_scene':next_scene,'item_hint':award,'image':deepcopy(image),'source':deepcopy(ref['source']),
            'actual_eligibility':None,'actual_reward':None,'actual_server_verified':False,'mutations_applied':False}


def image_bytes(info):
    if type(info)is not dict:return None
    try:
        name=info.get('file')
        if type(name)is not str or not name.endswith('.png')or not name.startswith(('rouge/data/battle-maps/','rouge/data/expansion-maps/')):return None
        raw=_file(info['file']).read_bytes()
        if len(raw)!=info['bytes']or sha256(raw).hexdigest()!=info['sha256']:return None
        if sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=info['git_blob_sha1']:return None
        return raw
    except(OSError,ValueError,KeyError,TypeError):return None
