"""Exact current Elbert/Firebrand documentary workflow; no effective damage or timing."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path,PurePosixPath
import json
from . import current_battle_reference as battle

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-elbert-366'
DATA='rouge/data/current-elbert-reference.json'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='8de7978ce8c573218973116f89179a936abb97371df990b454b41eaf0a9ea4f6'
STAGES=('ro6_b_3','ro6_b_3_dlc1','ro6_b_3_b','ro6_b_3_b_dlc1')
ELBERT='enemy_2143_shwksc';HERETIC='enemy_2144_shwks2';FIRE='enemy_2154_shdfb'
PROFILES={ELBERT:'elbert',HERETIC:'heretic',FIRE:'firebrand'}
CARDS={'boss':(('overview','先看机制全貌'),('summon','火种从哪里来'),('blink','闪现的条件与保护'),('staff','退场法杖')),
       'fire':(('overview','先看机制全貌'),('collision','碰撞与爆炸'),('configuration','本关独立配置与文献默认'))}
NOTICE='本页说明所选固定关卡中的首领与火种机制，供战斗前查阅；不读取实况，不操作游戏，不计算实际伤害或完整出怪时刻。'
UNAVAILABLE='埃尔伯特与火种的资料暂时无法核对，旧说明、图片和关联入口已清除；恢复后请重新选择。'


def _undefined_override(value):
    """The reviewed normal stage has wrappers, all explicitly undefined.

    False wrapper values are placeholders, not a second identity or stat record.
    This accepts that exact empty declaration shape only; it does not merge an
    unreviewed true override or infer a false wrapper's m_value.
    """
    if value is None:return True
    if type(value)is not dict:return False
    for key,item in value.items():
        if key=='attributes':
            if type(item)is not dict or not item or any(type(v)is not dict or set(v)!={'m_defined','m_value'}or v['m_defined']is not False for v in item.values()):return False
        elif key in('talentBlackboard','skills','spData'):
            if item is not None:return False
        elif type(item)is not dict or set(item)!={'m_defined','m_value'}or item['m_defined']is not False:return False
    return bool(value)


def source_rows(snapshot,inputs):
    stages=snapshot['details']['stages'];result={}
    for sid in STAGES:
        stage=stages[sid];key='levels/'+stage['levelId'].lower()+'.json';level=inputs['levels'][key]
        rows=[]
        for index,raw in enumerate(level['enemyDbRefs']):
            eid=raw['id']
            if eid not in PROFILES:continue
            if type(raw['level'])is not int or raw['level']!=0 or type(raw['useDb'])is not bool:
                raise ValueError('Exact grade0 current binding required')
            definitions=inputs['enemy_definitions'][eid]
            exact=[r for r in definitions if r['level']==raw['level']]
            if len(exact)!=1:raise ValueError('Exact full database declaration required')
            if raw['useDb']is True and _undefined_override(raw['overwrittenData']):
                constructor='database';declared=exact[0]['enemyData']
            elif raw['useDb']is False and type(raw['overwrittenData'])is dict:
                constructor='independent';declared=raw['overwrittenData']
            else:raise ValueError('Unreviewed constructor/override combination')
            prefab=declared.get('prefabKey')or{};name=declared.get('name')or{}
            if prefab.get('m_defined')is not True or prefab.get('m_value')!=eid or name.get('m_defined')is not True:
                raise ValueError('Explicit identity wrappers required; no placeholder fallback')
            rows.append({'key':str(index),'enemy_id':eid,'level':raw['level'],'name':name['m_value'],
                         'kind':'fire'if eid==FIRE else'boss','profile':PROFILES[eid],
                         'raw_binding':deepcopy(raw),'source_selector':f'$.enemyDbRefs[{index}]',
                         'database_definitions':deepcopy(definitions),'handbook':deepcopy(inputs['handbook'][eid]),
                         'constructor':constructor,'declared_configuration':deepcopy(declared),
                         'override_status':'none'if raw['overwrittenData']is None else'undefined_wrappers'if constructor=='database'else'independent_full',
                         'document_default_configuration_equal':constructor=='database'and declared==exact[0]['enemyData'],
                         'actual_present':None,'actual_phase':None,'actual_configuration_applied':None})
        if len(rows)!=2 or len({r['enemy_id']for r in rows} & {ELBERT,HERETIC})!=1 or sum(r['enemy_id']==FIRE for r in rows)!=1:
            raise ValueError('One exact boss and independent Firebrand reference per stage required')
        result[sid]={'stage':deepcopy(stage),'level_key':key,'complete_level':deepcopy(level),'entities':rows}
    return result


def _read_public(name):
    if type(name)is not str:raise ValueError('Public relative source required')
    rel=PurePosixPath(name)
    if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name or rel.as_posix()!=name:raise ValueError('Unsafe source')
    path=ROOT.joinpath(*rel.parts)
    if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Linked source refused')
    for parent in path.parents:
        if parent==ROOT:break
        if parent.is_symlink():raise ValueError('Linked source parent refused')
    return path.read_bytes()


def packet():
    try:
        raw=_read_public(MANIFEST)
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        expected={DATA,PACK+'/source-notes.json',PACK+'/complete-cards.json',
                  'research/p3-expansion-313/current-topic.json','research/p3-current-battle-314/source-inputs.json',
                  'research/p3-current-battle-314/source-selection.json','research/p3-current-battle-314/runtime-manifest.json'}
        expected.update(PACK+'/'+name+suffix for name in PROFILES.values()for suffix in('-page.html','-download.json'))
        if manifest['schema']!='current_elbert_366_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT or set(manifest['files'])!=expected:return None
        values={}
        for name,pin in manifest['files'].items():
            content=_read_public(name)
            if type(pin['bytes'])is not int or len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
            values[name]=content
        current=battle.packet();data=json.loads(values[DATA])
        if current is None or data['schema']!='current_elbert_366_v1'or data['game_commit']!=battle.version.NEW_COMMIT:return None
        if data['stages']!=source_rows(current['version']['current'],current['inputs']):return None
        if data['battle_identity']!=current['identity']:return None
        portraits={sid:{row['key']:deepcopy(row['portrait'])for row in battle.enemy_records(stage['complete_level'],current)}for sid,stage in data['stages'].items()}
        return{'data':data,'source_identity':(MANIFEST_SHA256,current['identity']),
               'battle_source_identity':current['identity'],'portraits':portraits,
               'actual_present':None,'actual_phase':None,'actual_target':None,'actual_blink':None,
               'actual_fire_direction':None,'actual_staff_position':None,'actual_damage':None,
               'actual_clock':None,'actual_received_buff':None,'current_server_verified':False,
               'run_updated':False,'numerical_model_applied':False}
    except(OSError,ValueError,KeyError,TypeError,AttributeError,UnicodeError,RecursionError):return None


def reference(stage_id,enemy_key=None,card=None):
    if type(stage_id)is not str or stage_id not in STAGES:return None
    if enemy_key is not None and type(enemy_key)is not str:return None
    if card is not None and type(card)is not str:return None
    result=packet()
    if result is None:return None
    stage=result['data']['stages'][stage_id];selected=next((r for r in stage['entities']if r['key']==enemy_key),None)
    if enemy_key is not None and selected is None:return None
    if card is not None and(selected is None or card not in dict(CARDS[selected['kind']])):return None
    return{**result,'stage_id':stage_id,'stage_name':stage['stage']['name'],'stage':deepcopy(stage),
           'entities':deepcopy(stage['entities']),'selected':deepcopy(selected),'card':card,
           'actual_source_entity':None}


def locate(stage_id,enemy_key):
    result=reference(stage_id,enemy_key)
    return{'stage_id':stage_id,'enemy_key':enemy_key}if result and result['selected']else None


def entity(result,enemy_key):
    if result is None or type(enemy_key)is not str:return None
    return next((row for row in result['entities']if row['key']==enemy_key),None)


def related_entities(result,enemy_key):
    row=entity(result,enemy_key)
    if row is None:return[]
    return[{'stage_id':result['stage_id'],'enemy_key':other['key'],
            'enemy_id':other['enemy_id'],'level':other['level'],'name':other['name']}
           for other in result['entities']if other['key']!=enemy_key]


def resolve_related(result,enemy_key,request):
    if result is None or type(request)is not dict or request not in related_entities(result,enemy_key):return None
    fresh=reference(result['stage_id'],enemy_key)
    if fresh is None or fresh['source_identity']!=result['source_identity']or fresh['stage']!=result['stage']:return None
    return locate(result['stage_id'],request['enemy_key'])


def selected_card(result,enemy_key):
    row=entity(result,enemy_key)
    return deepcopy(result['data']['complete_cards'][row['profile']])if row else None


def view_result(result,enemy_key,card=None):
    """A local read projection; it does not silently refresh or choose an entity."""
    if card is not None and type(card)is not str:return None
    row=entity(result,enemy_key)
    if result is None or(enemy_key is not None and row is None):return None
    if card is not None and(row is None or card not in dict(CARDS[row['kind']])):return None
    return{**result,'selected':deepcopy(row),'card':card}


def player_text(result):
    if result is None:return UNAVAILABLE
    lines=[result['stage_name']+' · 埃尔伯特与火种',NOTICE]
    row=result['selected']
    if row is None:
        return '\n'.join(lines+['','请选择本关首领或火种。首领、召唤出的火种和退场法杖分开说明。',
                                 '这是当前四份固定关卡的阅读入口，不表示本局已经遇到哪一份配置。'])
    profile=result['data']['profiles'][row['profile']];card=result['card']or'overview'
    lines+=['','【正在查阅】'+row['name']]
    if row['kind']=='boss':
        if card in('overview','summon'):
            lines+=['','【火种从哪里来】',
                    '文献说明其普通攻击属于持续进行的行为，本体这次行为不直接造成伤害，而是在自身所在地块中心召唤1个“火种”，让火种沿自身路径前进。',
                    '普通的“攻击方式”标签不能据此理解为完全没有攻击行为；这里也没有把配置攻击间隔当成实际每次生成的时刻。',
                    '重要区别：火种如何增大或减弱，由火种在这份关卡里的配置决定，与首领叫埃尔伯特还是“异端”无关。',
                    '原图鉴用“随移动距离减小/增大”概括；完整机制文献另说明时间变化与关卡配置。两种来源分别保留，不能直接用移动距离计算伤害。']
        if card in('overview','blink'):
            lines+=['','【闪现】',
                    '文献的触发限制：未被阻挡时才可触发。先进行开启动作，技能正常结束时传送到下一个路径点，并在闪现期间有保护。',
                    '保护还包含后摇'+profile['blink_recovery_text']+'秒；这是文献动作说明，不是整场战斗的绝对时间或本局已触发时刻。',
                    '文献初始冷却0秒、之后冷却'+str(profile['blink_cooldown'])+'秒；冷却就绪不等于立刻实际触发，还受阻挡、动作和实际脚本条件影响。',
                    '文献另列失衡免疫、自缚及被传送免疫。自缚指自身不能正常移动；不能把免疫被传送理解为不会执行自身闪现。']
        if card in('overview','staff'):
            lines+=['','【退场后留下的法杖】',
                    '文献用的是“退场后”，不能缩写为仅被击倒时。法杖留在退场位置，对半径20范围内的敌方单位提供“埃尔伯特的增益”，无视它们的可选性。',
                    '效果说明：攻击速度+50；移动速度最终变为原来的150%（增加50%，不是增加150%）。同名效果不叠加。',
                    '范围和数值是机制文献及原设置的参考，不证明本局已留下法杖、哪些敌人获得增益或最终面板，也不把其它来源的增益一并消掉。']
    else:
        if card in('overview','collision'):
            lines+=['','【碰撞与爆炸】',
                    '完整文献列出无敌与孤立：通常不能被不同阵营选中，也不能被同阵营选中；无法攻击或被阻挡。实际特殊例外仍按完整来源核对。',
                    '文献默认：半径0.25内出现我方单位时爆炸，中心在触发的我方单位处；对爆炸范围内我方单位造成法术伤害和凋亡损伤，然后自身退场。',
                    '“无法攻击”不等于爆炸不会造成伤害。减伤等规则是否影响这次爆炸，需要结合文献对伤害的具体分类判断；完整分类保留在另一页原文中。',
                    '此判定采用文献所说的“中点判定”，不受迷彩制约。完整判定说明见原文；仅凭地图图标位置或地面、高台标签，不能推定是否触发。',
                    '这里不计算实际碰撞时间、最终爆炸范围、伤害或凋亡爆发时钟。']
        if card in('overview','configuration'):
            lines+=['','【默认文献如何变化】',
                    '默认文献写：登场10秒后自行退场；爆炸半径、法术伤害和元素损伤在10秒内由最大值线性降低至0，每秒变化一次。关卡也可以把它改为从0增加到最大值。',
                    '文献默认最大值依次为半径2、法术伤害1000、凋亡损伤200；这些是有适用条件的默认说明，不是当前敌人预计面板或本局伤害结果。']
            if row['constructor']=='independent':
                lines+=['','【本关必须另看】本关火种使用独立配置，不能直接套用上述10秒、半径2和法术1000的默认数值。',
                        '本关原件另外列有6秒、范围1.5、法术500等配置参数；完整原值在来源页。参数记录不等于实际实例已应用、实际变强方向或最终有效伤害。',
                        '不因为本关首领叫“异端”就自动判为增长曲线，也不按路程反算每秒强度。']
            else:
                lines+=['','【本关资料对照】本关沿用原始敌人资料，没有单独改写这份火种配置；其中上述数值与默认文献一致。',
                        '这只证明固定资料对应，实际创建、变化方向、首个变化时点、碰撞与退场仍没有实机证据，不直接输出一条伤害曲线。']
    lines+=['','【适用范围与未知】','完整机制来源：PRTS '+profile['title']+'，采用已保存的资料版本；关卡和敌人来自固定国服资料。修订号与准确出处可在另一页查看。',
            '准确关卡配置分别保留，不按同名关卡、相同图片或首领名称合并。未迁移的保密等级、分队、技能及阶段修正仍未知。',
            '只作局外查阅，不分析实况站位、不进行战斗操作、不改变本局记忆或数值计算，不推荐路线或生成概率。']
    return '\n'.join(lines)
