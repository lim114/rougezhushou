"""Conditional current base rewards, separated by entrance and source region."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import current_stage_directory as directory
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-settlement-318';DATA='rouge/data/current-settlement-reference.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='022db302ff6b150e2c2fae2ce4c3e5138685c4b29dc04e56b5117bbaa86a139d'
ENTRIES=[('unknown','实际入口尚未确认'),('map','地图上的作战'),('event','事件、商店或居民等特殊入口'),('pursuit','通常追猎'),('boss_pursuit','险路恶敌追猎')]
REGIONS=[('catalog','资料所列区域'),('portal','当前在秘境'),('side_path','当前在熄日余径')]
UNAVAILABLE='基础奖励来源暂时无法核对，旧数值已清除；恢复后请重新核对。'

def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);objects={}
        if manifest['schema']!='current_settlement_318_manifest_v1':return None
        for name,pin in manifest['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            objects[name]=raw
        current=directory.packet()
        if current is None:return None
        return {'data':json.loads(objects[DATA]),'directory':current,'source_identity':MANIFEST_SHA256,'actual_reward':None}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError):return None

def stage_reference(stage_id,entry='unknown',region='catalog'):
    if entry not in dict(ENTRIES)or region not in dict(REGIONS):raise ValueError('入口或区域尚未支持。')
    ref=packet()
    if ref is None:return None
    info=directory.detail(stage_id,reference=ref['directory'])
    if info is None:return None
    stage=info['row'];raw=stage['original_stage'];data=ref['data'];rows=[]
    def add(rule,label,required,region_match=True):
        matches=None if entry=='unknown'else entry==required
        status='not_matched'if matches is False or region_match is False else'unknown'if matches is None or region_match is None else'listed_matched'
        rows.append({'label':label,'required_entry':required,'entry_matches':matches,'region_matches':region_match,'status':status,'rule':deepcopy(rule),'actual_received':None})
    source_floor='source0'if stage['region']=='源流交汇处'else stage['floor']if stage['region']=='主要区域'else None
    if stage['play_kind']in('normal','emergency','boss'):
        kinds=[stage['play_kind']]+(['boss_pursuit']if stage['play_kind']=='boss'else[])
        for kind in kinds:
            rule=data['main_floor_table'].get(source_floor,{}).get(kind)
            if rule is None:rule={'base_gold':None,'current_experience':None,'historical_experience_reference':None,'source_missing_reason':'当前表未列出这一区域的对应基础奖励；不能借用同层另一特殊区域。'}
            region_match=True if region=='catalog'else True if region=='portal'and kind in('normal','emergency')else None
            add(rule,'普通或紧急作战的通关基础分项'if kind in('normal','emergency')else'险路恶敌追猎的基础分项'if kind=='boss_pursuit'else'险路恶敌的通关基础分项','boss_pursuit'if kind=='boss_pursuit'else'map',region_match)
    for rule in data['special_battle_table']:
        if rule['difficulty']==raw['difficulty']and any(link['name']==raw['name']and link['code']==raw['code']for link in rule['links']):add(rule,'这个具名特殊入口的通关基础分项','event',True if region=='catalog'else None)
    if stage['kind']=='pursuit'and raw['isBoss']==0:add(data['ordinary_pursuit'],'通常追猎的基础分项','pursuit',True if region=='catalog'else None)
    if not rows:add({'base_gold':None,'current_experience':None,'historical_experience_reference':None,'source_missing_reason':'当前基础奖励表没有这个具名关卡的专门条目，不按名称或共用地图借数值。'},'基础奖励尚未核实','event'if stage['kind']in('challenge','duck','duel','resident','shop')else'map',None)
    applicable=[r for r in rows if r['status']!='not_matched'];qualified=bool(applicable)and all(r['status']=='listed_matched'for r in applicable)
    values=[r['rule']['base_gold']for r in applicable];gold=values[0]if qualified and values and values[0]is not None and all(v==values[0]for v in values)else None
    values=[r['rule']['current_experience']for r in applicable];xp=values[0]if qualified and values and values[0]is not None and all(v==values[0]for v in values)else None
    bonus={'random_relics':1,'condition':'完成熄日余径的普通作战节点','actual_received':None}if region=='side_path'and entry=='map'and stage['play_kind']=='normal'else None
    return {'stage_id':stage_id,'stage_name':stage['name'],'stage_grouping':info,'entry_declared':entry,'region_declared':region,'rows':rows,'conditional_base_gold':deepcopy(gold),'conditional_current_experience':xp,'documented_side_path_bonus':bonus,
        'source_identity':ref['source_identity'],'source':data['source'],'current_nonzero_experience_modes_verified':False,'actual_reward_total':None,'complete_reward_pool_known':False,'inventory_updated':False,'actual_victory_verified':False,'actual_entry_verified':False,'reward_modifiers_applied':False}

def amount(value):
    if value is None:return '未知'
    return str(value['minimum'])if value['minimum']==value['maximum']else str(value['minimum'])+'至'+str(value['maximum'])

def player_text(result):
    labels={'unknown':'入口或区域尚未确认','not_matched':'与声明的入口或区域不符','listed_matched':'已列条件相符，仍须实际通关与结算'}
    lines=[result['stage_name'],'','【先看这两项】','符合下列入口、未计任何额外加成时的基础源石锭：'+amount(result['conditional_base_gold'])+'。','当前指挥经验：'+('未知'if result['conditional_current_experience']is None else str(result['conditional_current_experience']))+'。','完整奖励总量：未知；没有据此修改本局持有。']
    for row in result['rows']:
        rule=row['rule'];lines+=['','【'+row['label']+'】',labels[row['status']],'适用入口：'+dict(ENTRIES)[row['required_entry']],'基础源石锭参考：'+amount(rule['base_gold'])+'。']
        if rule.get('recruit_ticket_reference')is not None:lines+=['文献注明通关后有1张招募券；券种、实际领取与其它效果仍未确认。','通常追猎的指挥经验为0；不可把这个规则套到险路恶敌追猎或同名事件战斗。']
        else:lines+=['当前指挥经验：还需核对。网页把基础与满科技两种显示放在一起，不能合成一个经验数。']
        history=rule.get('historical_experience_reference')
        if history and history['base']is not None:lines+=['旧版经验资料参考：基础'+str(history['base'])+'；满级生命游戏'+str(history['full_technology'])+'。这是旧版网页的经验参考，未用于当前数值，也不默认你已点满科技。']
        if rule.get('source_missing_reason'):lines+=[rule['source_missing_reason']]
    if result['region_declared']=='portal':lines+=['','秘境只沿用文献明确说明的普通/紧急所属关卡基础分项；不把秘境编号当主层，也不填补首领奖励空列。']
    if result['region_declared']=='side_path':lines+=['','熄日余径的完整基础结算规则尚未核实，不按下一层或原地图编号直接套算。']
    if result['documented_side_path_bonus']:lines+=['文献明确的额外分项：完成该普通作战节点后另有1件随机收藏品。完整候选池和实际领取未知，不与所有关卡奖励相加。']
    lines+=['','【这些还没算进去】','保密等级、分队、科技、收藏品、零件、恶笼草、无漏怪等条件的奖励变化和实际结算尚未全部核实。只列基础参考，未知不当作零，也不把多个入口候选相加。']
    return '\n'.join(lines)
