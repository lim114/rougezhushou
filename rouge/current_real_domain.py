"""Read-only ideology/policy directory; declared conditions are not live effects."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-real-domain-357'
DATA = 'rouge/data/current-real-domain.json'
MANIFEST = PACK+'/runtime-manifest.json'
MANIFEST_SHA256 = '3da037d87d8d737fbd09665070ea39c7d76102185ebfde643d4605381f63c814'
HOPE = 'rogue_6_weather_8'
GAIN = 'rogue_6_subweather_4'
SQUADS = ('rogue_6_band_15', 'rogue_6_band_16', 'rogue_6_band_25')
IMMUNE_SQUADS = frozenset(SQUADS[1:])
LINKS = {
    'red_controller': ('vine', 'choices', 'choice_ro6_normal3_1', HOPE),
    'red_seed': ('vine', 'choices', 'choice_ro6_normal3_2', HOPE),
    'resting': ('resting', 'scenes', 'scene_ro6_surprise_enter', 'rogue_6_weather_10'),
}
UNAVAILABLE = '实托邦的来源暂时无法核对，旧理念、方针、条件说明和事件入口已清除；恢复后请重新选择。'
NOTICE = '这里只解释实托邦的条件与影响；未认定本局生成、覆盖节点或生效，不改干员、敌人、奖励和本局记录。'


def source_rows(snapshot, documented):
    weather = snapshot['modules']['weather']
    main, sub = weather['mainWeatherData'], weather['subWeatherData']
    if set(main) != {f'rogue_6_weather_{i}_{suffix}' for i in range(1, 11) for suffix in ('a','b','c')} or set(sub) != {f'rogue_6_subweather_{i}' for i in range(1,5)}:
        raise ValueError('Complete30 ideology and4 policy records required')
    rows = []
    for kind, table in (('idea',main), ('policy',sub)):
        for identity, raw in table.items():
            if raw['id'] != identity or raw['type'] not in documented:
                raise ValueError('Exact type and documented name required')
            doc = documented[raw['type']]
            if doc['name'] != raw['name'] or not doc['complete_table']:
                raise ValueError('Complete exact documented table required')
            stage = raw['level'] if kind=='idea' else None
            text = doc['stages'][str(stage)] if kind=='idea' else doc['function']
            if raw['type']=='rogue_6_weather_5':
                # The community explicitly adds emergency-support shops. Both
                # independent texts remain visible; never rewrite the original.
                if text.replace('应急助力、','') != raw['functionDesc']:
                    raise ValueError('Only the documented storage supplement is admitted')
            elif text != raw['functionDesc']:
                raise ValueError('Exact original/documented description differs')
            rows.append({'id':identity,'kind':kind,'type':raw['type'],'name':raw['name'],
                         'level':stage,'level_name':raw.get('levelName'),
                         'original':deepcopy(raw),'documented':deepcopy(doc),
                         'actual_active':None,'actual_affected_nodes':None})
    return rows


def _read(name):
    if type(name)is not str:raise ValueError('Public relative source required')
    relative=PurePosixPath(name)
    if relative.is_absolute()or'..'in relative.parts or'\\'in name or':'in name or relative.as_posix()!=name:raise ValueError('Unsafe source')
    path=ROOT.joinpath(*relative.parts)
    if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Linked source refused')
    for parent in path.parents:
        if parent==ROOT:break
        if parent.is_symlink():raise ValueError('Linked source parent refused')
    return path.read_bytes()


def packet():
    try:
        raw=_read(MANIFEST)
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        expected={DATA,PACK+'/source-notes.json',PACK+'/database-page.html',PACK+'/main-page.html',
                  PACK+'/database-download.json',PACK+'/main-download.json',
                  PACK+'/documented-real-domain.html',PACK+'/documented-domain-overview.html',
                  'research/p3-expansion-313/current-topic.json',
                  'rouge/data/current-vine-events.json','rouge/data/current-resting.json',
                  'research/p3-current-vine-events-333/runtime-manifest.json',
                  'research/p3-current-resting-345/runtime-manifest.json'}
        if manifest['schema']!='current_real_domain_357_manifest_v1'or manifest['game_commit']!=version.NEW_COMMIT or set(manifest['files'])!=expected:return None
        content={}
        for name,pin in manifest['files'].items():
            data=_read(name)
            if type(pin['bytes'])is not int or len(data)!=pin['bytes']or sha256(data).hexdigest()!=pin['sha256']:return None
            content[name]=data
        data=json.loads(content[DATA]);current=version.packet()
        if current is None or data['schema']!='current_real_domain_357_v1'or data['game_commit']!=version.NEW_COMMIT:return None
        snapshot=current['current'];details=snapshot['details']
        if data['rows']!=source_rows(snapshot,data['documented']):return None
        if data['difficulties']!={str(row['grade']):row for row in details['difficulties']if row['modeDifficulty']=='NORMAL'}:return None
        if data['squads']!={key:{'item':details['items'][key],'relic':details['relics'][key]}for key in SQUADS}:return None
        from . import current_vine_events as vine,current_resting as resting
        providers={'vine':vine,'resting':resting}
        for key,(provider,category,identity,type_id)in LINKS.items():
            original_table='choices'if category=='choices'else'choiceScenes';link=data['links'][key];module=providers[provider];p=module.packet()
            if p is None or link['target']!=module.locate(category,identity):return None
            if link['source_identity']!=json.loads(json.dumps(p['source_identity'])):return None
            if link['source_category']!=category or link['source_id']!=identity or link['type']!=type_id or link['original']!=details[original_table][identity]:return None
        if set(data['links'])!=set(LINKS):return None
        return {'data':data,'source_identity':(MANIFEST_SHA256,current['source_identity']),
                'actual_weather':None,'actual_phase':None,'actual_combination':None,
                'actual_affected_nodes':None,'actual_received':None,'actual_eligible':None,
                'calculation_applied':False,'run_updated':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None


def _context(mode,difficulty,floor,affected,action,squad,paired):
    if mode not in(None,'NORMAL','OTHER'):raise ValueError('Unsupported mode')
    if difficulty is not None and(type(difficulty)is not int or not 0<=difficulty<=16):raise ValueError('Unsupported difficulty')
    if floor is not None and(type(floor)is not int or not 1<=floor<=6):raise ValueError('Unsupported main layer')
    if affected is not None and type(affected)is not bool:raise ValueError('Unknown node coverage must remain unknown')
    if action not in(None,'enter','pass','both'):raise ValueError('Unsupported reading action')
    if squad is not None and(type(squad)is not str or squad not in SQUADS):raise ValueError('Exact squad record required')
    paired_ids={f'rogue_6_weather_{i}'for i in range(1,11)}|{f'rogue_6_subweather_{i}'for i in range(1,5)}
    if paired is not None and(type(paired)is not str or paired not in paired_ids):raise ValueError('Exact paired type required')
    return {'mode':mode,'difficulty':difficulty,'floor':floor,'affected':affected,'action':action,'squad':squad,'paired':paired}


def comparison(row,context):
    """Listed documentary prerequisites only, never return actual activation."""
    if row is None:return {'facts':[],'status':'unknown','ordinary_phase':None,'actual_applied':None}
    phase=None
    if context['mode']=='NORMAL'and context['difficulty']is not None and context['difficulty']>=2:
        phase=1 if context['difficulty']<6 else 2 if context['difficulty']<12 else 3
    facts=[]
    def add(name,matched,meaning):facts.append({'name':name,'matched':matched,'meaning':meaning})
    grade=context['difficulty'];minimum=2 if row['kind']=='idea'else 6
    natural_match=None if context['mode']!='NORMAL'or grade is None else grade>=minimum
    if row['id']==GAIN and grade is not None and grade<6:natural_match=None
    add('常规自然生成难度',natural_match,
        '只对照常规自然生成门槛；事件强制来源、已存在状态和其它模式另核。')
    if row['kind']=='idea':
        add('普通档位',None if phase is None else row['level']==phase,'早期为保密2至5，中期6至11，晚期12至16；不据此替换手选原项。')
    add('节点是否受影响',context['affected'],'只采用本页声明，不读取或修改实际地图。')
    action=context['action']
    action_match=None if action is None else action in('enter','both')if row['kind']=='idea'else True if action in('pass','both')else None
    add('进入与经过分别核对',action_match,
        '理念在节点内生效；方针看途经结算。两者可以同时声明；只确认进入，不自动证明经过结算已经执行。')
    if row['type']=='rogue_6_weather_1':
        add('不是第一主层',None if context['floor']is None else context['floor']!=1,'社区文献注明黑流地脉不会生成在第Ⅰ层；特殊区域不能按名字套主层。')
    if row['type']==HOPE:
        add('仅配增益方针',None if context['paired']is None else context['paired']==GAIN,'资料不支持希望的沃土与其它方针组合。')
    if row['kind']=='policy':
        paired=context['paired']
        if row['id']==GAIN:
            match=None if paired is None else paired==HOPE
            add('仅配希望的沃土',match,'增益与希望的沃土互相限定，不用任意组合补齐。')
        else:
            match=False if paired==HOPE else None
            add('组合记录',match,'已知希望的沃土只配增益；其它理念的全部方针组合没有因此得到证明。')
        squad=context['squad']
        add('文明开化方针例外',None if squad is None else True if row['id']==GAIN else squad not in IMMUNE_SQUADS,
            '强化档位对消耗类方针有免疫原文；社区另注明增益可影响这种免疫档位。不是账户已解锁或已激活的证明。')
    status='not_matched'if any(f['matched']is False for f in facts)else'unknown'if any(f['matched']is None for f in facts)else'listed_matched'
    return {'facts':facts,'status':status,'ordinary_phase':phase,'actual_applied':None}


def reference(row_id=None,*,kind=None,type_id=None,query='',mode=None,difficulty=None,floor=None,affected=None,action=None,squad=None,paired=None):
    if row_id is not None and type(row_id)is not str:return None
    if kind not in(None,'idea','policy')or type(query)is not str:return None
    try:context=_context(mode,difficulty,floor,affected,action,squad,paired)
    except(ValueError,TypeError):return None
    p=packet()
    if p is None:return None
    if type_id is not None and(type(type_id)is not str or type_id not in p['data']['documented']):return None
    rows=[deepcopy(row)for row in p['data']['rows']if(kind is None or row['kind']==kind)and(type_id is None or row['type']==type_id)and(not query.strip()or query.strip()in row['name'])]
    selected=next((row for row in rows if row['id']==row_id),None)
    if row_id is not None and selected is None:return None
    if selected and paired is not None:
        required='rogue_6_weather_'if selected['kind']=='policy'else'rogue_6_subweather_'
        if not paired.startswith(required):return None
    return {**p,'rows':rows,'selected':selected,'context':context,'comparison':comparison(selected,context),
            'filters':{'kind':kind,'type_id':type_id,'query':query},
            'related_origins':[deepcopy(link)for link in p['data']['links'].values()if selected and link['type']==selected['type']]}


def locate(category,identity):
    if type(category)is not str or type(identity)is not str:return None
    packet_value=packet()
    if packet_value is None:return None
    for key,(_,cat,source,type_id)in LINKS.items():
        if (category,identity)==(cat,source):return {'kind':'idea','type_id':type_id,'origin_key':key,'source_category':cat,'source_id':source}
    if(category,identity)==('scenes','scene_ro6_normal3_enter'):
        return {'kind':'idea','type_id':HOPE,'origin_key':None,'source_category':category,'source_id':identity}
    return None


def destination(key):
    if type(key)is not str or key not in LINKS:return None
    p=packet()
    return deepcopy(p['data']['links'][key])if p else None


def player_text(result):
    lines=['【实托邦：理念与方针】',NOTICE,'','理念是节点内的核心影响；方针是途经受影响节点时的附加影响。两者分别看，不能把进入与路过算成同一件事。',
           '资料收录10种理念的30份早/中/晚期原项和4种方针；是可查目录，不代表同局全部存在或任意组合。']
    row=result['selected']
    if row is None:return '\n'.join(lines+['','请选择一条理念或方针；所有本页条件默认未知。'])
    raw=row['original'];doc=row['documented']
    lines+=['','【'+row['name']+(' · '+row['level_name']if row['kind']=='idea'else' · 方针')+'】',
            '【游戏原说明】',version._plain(raw['functionDesc'])]
    if row['kind']=='idea':
        lines+=['','【同一理念的三档对照】']
        for level in(1,2,3):
            r=next(v for v in result['data']['rows']if v['type']==row['type']and v['level']==level)
            lines+=[r['level_name']+'：'+version._plain(r['original']['functionDesc'])]
    if doc['notes']:
        lines+=['','【社区补充与例外】']+doc['notes']
    if row['type']=='rogue_6_weather_5':lines+=['社区补充把应急助力列入商品栏位减少范围；游戏原说明仅写两类行商。两份原文分别保留，不把补文伪装成原字段。']
    if row['type']==HOPE:lines+=['请分别核对早期、中期、晚期效果，以及同处节点所配的方针。','下一区域效果不是当前立即获得；零件具体种类、数量及实际领取仍未知。']
    if row['type']=='rogue_6_weather_10':lines+=['安眠一隅只是文献提到的相关事件；没有足够依据指定哪条实际选项或保证触发。模型变黑不等于不可选中、隐匿或无敌。']
    if row['type']=='rogue_6_weather_9':lines+=['不能把“无法自然揭示”解释成一切揭示失效，也不能把已进入的重复节点重新改成未知。']
    if row['kind']=='policy':lines+=['生命和护盾是探索资源，不是干员生命；增益改变自然物估价，不是当场增加源石锭。']
    result_names={'not_matched':'已列条件有不符；仍可阅读原文，不认定本局会生效。','unknown':'条件尚未完整确认，实际效果仍未知。','listed_matched':'本页已列条件相符；完整服务器条件与实际生效仍未知。'}
    lines+=['','【本页条件对照】',result_names[result['comparison']['status']]]
    for fact in result['comparison']['facts']:
        mark='未知'if fact['matched']is None else'相符'if fact['matched']else'不符'
        lines+=[fact['name']+'：'+mark+'。'+fact['meaning']]
    lines+=['','【怎样理解这里的条件】','保密等级只选出常规资料档位参照，不证明地图已生成该理念。受影响节点、当前阶段、途经/进入和分队都是本页人工对照，不填入本局。',
            '对战斗、商店、节点信息与奖励的完整实际结果，仍需各自条件和脚本；本页不叠入属性、伤害或奖励总量。',
            '相关事件按钮打开准确原文供查阅，具体触发、完整资格与已领取均未知。','采用国服2026年10月16日固定资料，社区补充说明另列；本页只供查阅，不操作游戏或改变本局，不提供路线推荐或出现概率。']
    return '\n'.join(lines)
