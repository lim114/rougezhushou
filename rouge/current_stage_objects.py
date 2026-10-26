"""Complete original predefines, distinct instances and cards, no activation."""
from copy import deepcopy
from hashlib import sha256
import json,re
from . import current_battle_reference as battle
from .battle_preview import display_cell
PACK='research/p3-current-stage-objects-373'
MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='a47c7111c11e184aa97185c6690116fd10fe08e6497aea1290b0a1acf65686c0'
KINDS=((None,'总览（物件与卡片）'),('instance','场景预置物件'),('card','预置可用物件卡'))
LINKS=((None,'全部启用记录情况'),('linked','有直接启用记录'),('unlinked','未找到直接启用记录'))
DIRECTIONS={'UP':'向上','DOWN':'向下','LEFT':'向左','RIGHT':'向右','NONE':'未指定方向'}
NOTICE='阅读本关资料中预先声明的物件与可用卡片；它们可能需要条件才出现或启用。预置声明、隐藏标记、启用记录和已经生效分别看待。'
UNAVAILABLE='本关物件与机关资料无法核对，旧说明、启用记录和地图资料已清除；资料恢复后请重新选择。'
def same(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
    if type(a)in(list,tuple):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
    return a==b
def packet():
    try:
        raw=battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw)
        if manifest['schema']!='current_stage_objects_373_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
        if set(manifest['files'])!={PACK+'/selected-originals.json',PACK+'/source-selection.json',PACK+'/source-notes.json',PACK+'/source-extraction-audit.json',PACK+'/scope-inventory.json'}:return None
        objects={}
        for name,pin in manifest['files'].items():
            body=battle.version._file(name).read_bytes()
            if type(pin['bytes'])is not int or len(body)!=pin['bytes']or sha256(body).hexdigest()!=pin['sha256']:return None
            objects[name]=json.loads(body)
        selected=objects[PACK+'/selected-originals.json']
        if selected['commit']!=battle.version.NEW_COMMIT:return None
        return{'selected':selected,'sources':objects[PACK+'/source-selection.json'],'notes':objects[PACK+'/source-notes.json'],'identity':MANIFEST_SHA256,'inventory':objects[PACK+'/scope-inventory.json']}
    except(OSError,ValueError,KeyError,TypeError):return None
def description(value):
    text=re.sub(r'\{[^}]+\}','（具体数值待核对）',value or'')
    return battle.plain(text).replace('\\n','\n').strip()
def _derive(current,reference):
    records=[]
    for container in('predefines','hardPredefines'):
        for field in('characterInsts','tokenInsts','characterCards','tokenCards'):
            for i,raw in enumerate((current['level'].get(container)or{}).get(field)or[]):
                selector=f'$.{container}.{field}[{i}]';kind='instance'if field.endswith('Insts')else'card'
                inst=raw.get('inst')or{};entity=inst.get('characterKey')or raw.get('characterKey');character=reference['selected']['characters'].get(entity)
                if character is None:raise ValueError('Every exact predefined entity requires its original record')
                skills=[]
                for s in character.get('skills')or[]:
                    key=s.get('skillId')
                    if key is None:continue
                    original=reference['selected']['skills'].get(key)
                    if original is None:raise ValueError('Exact original skill missing')
                    levels=original['levels'];level=raw.get('mainSkillLvl')
                    exact=levels[level-1]if type(level)is int and 1<=level<=len(levels)else None
                    skills.append({'id':key,'original_skill':deepcopy(original),'selected_level':deepcopy(exact),
                                   'selected_by_index':type(raw.get('skillIndex'))is int and 0<=raw['skillIndex']<len(character.get('skills')or[])and character['skills'][raw['skillIndex']].get('skillId')==key})
                alias=raw.get('alias');actions=[deepcopy(a)for a in current['actions']if kind=='instance'and type(alias)is str and alias and a['raw'].get('actionType')=='ACTIVATE_PREDEFINED'and a['raw'].get('key')==alias and any(c['source_selector']==selector for c in a['predefined_candidates'])]
                records.append({'key':selector,'source_selector':selector,'kind':kind,'container':container,'field':field,'ordinal':i+1,'entity_id':entity,'name':battle.plain(character['name']).strip(),'raw':deepcopy(raw),'character':deepcopy(character),'skills':skills,'activation_actions':actions,'actual_active':None,'actual_occurrence':None,'actual_reward':None,'actual_position':None})
    return{'stage_id':current['id'],'stage_name':current['name'],'entries':records,'level_key':current['level_key'],'original_level_source':deepcopy(current['source']),'source_identity':(reference['identity'],current['source_identity']),'battle_source_identity':current['source_identity'],'actual_active':None,'actual_server_verified':False,'run_updated':False}
def stage_reference(stage_id):
    if type(stage_id)is not str:return None
    current=battle.stage_reference(stage_id);reference=packet()
    if current is None or reference is None:return None
    if reference['inventory']['battle_identity']!=current['source_identity']or stage_id not in reference['inventory']['stages']:return None
    declared=reference['inventory']['stages'][stage_id]
    if declared['level_key']!=current['level_key']or declared['original_source']!=current['source']:return None
    try:return _derive(current,reference)
    except(ValueError,KeyError,TypeError,IndexError):return None
def rows(result,query='',kind=None,link=None):
    if type(result)is not dict or type(query)is not str or kind not in dict(KINDS)or link not in dict(LINKS):return[]
    wanted=query.strip().casefold()
    return[deepcopy(r)for r in result['entries']if(not wanted or wanted in r['name'].casefold())and(kind is None or kind==r['kind'])and(link is None or bool(r['activation_actions'])==(link=='linked'))]
def resolve(result,key,action_key=None):
    if type(result)is not dict or type(key)is not str or(action_key is not None and type(action_key)is not str):return None
    fresh=stage_reference(result.get('stage_id'))
    if fresh is None or not same(fresh,result):return None
    row=next((r for r in fresh['entries']if r['key']==key),None)
    if row is None:return None
    action=next((a for a in row['activation_actions']if a['key']==action_key),None)if action_key is not None else None
    if action_key is not None and action is None:return None
    return{'reference':fresh,'row':deepcopy(row),'action':deepcopy(action),'run_updated':False}
def position_reference(result,key):
    chosen=resolve(result,key)
    if chosen is None or chosen['row']['kind']!='instance':return None
    from . import current_map_position as positions
    grid=positions.stage_reference(result['stage_id'])
    if grid is None or grid['current_level_key']!=result['level_key']:return None
    cell=display_cell(chosen['row']['raw'].get('position'),grid['rows'],grid['cols'])
    if cell is None:return None
    point=positions.cell_reference(grid,**cell)
    return{'stage_id':result['stage_id'],'key':key,'row':chosen['row'],'grid':grid,'cell':cell,'center':deepcopy(point['point'])if point else None,'source_identity':(result['source_identity'],grid['source_identity']),'actual_position':None,'actual_active':None,'actual_path':None,'run_updated':False}
def label(row):return row['name']+' · '+('物件'if row['kind']=='instance'else'卡片')+str(row['ordinal'])
def player_text(result,row=None,action=None):
    lines=[result['stage_name'],'','【本关物件】',f"资料中共{len(result['entries'])}条预置声明；这不是当前场上数量或本局实际持有数量。",'地图物件与预置可用卡片分开列出，同名不同声明不合并。']
    if row is not None:
        lines+=['', '【'+row['name']+'】',description(row['character'].get('description'))or'原物件表未给出独立说明；请查看下方已列技能说明。']
        for skill in row['skills']:
            selected=skill['selected_level']
            if selected is None:lines+=['此技能的原选择等级无法核对，不借用其它等级说明。'];continue
            lines+=['','技能：'+battle.plain(selected['name'])+('（本声明所选技能）'if skill['selected_by_index']else'（同物件的其它技能，仅供查阅）'),description(selected.get('description'))or'原技能表未给出说明；未猜测它的隐藏效果。']
        lines+=['','【声明与出现条件】']
        if row['kind']=='card':lines+=['原卡片初始数量设置：'+battle.number(row['raw'].get('initialCnt'))+'；不作为当前库存。','这是关卡预置可用卡片的声明，不是已经部署的场景物件，也不证明你当前仍持有这张卡；不标到地图。']
        else:
            hidden=row['raw'].get('hidden');lines+=['原隐藏设置：'+('隐藏'if hidden is True else'不隐藏'if hidden is False else'未取得明确设置')+'。这不证明当前可见或已经启用。','原朝向：'+DIRECTIONS.get(row['raw'].get('direction'),'未取得明确设置')+'；不据此绘制攻击或影响范围。']
        n=len(row['activation_actions']);lines+=['找到'+str(n)+'条直接启用记录。'+('可选择一条查看其波次、候选与条件。'if n else'未找到直接启用记录不等于不会出现或生效，仍可能依赖其它脚本。')]
        if any(len(a['predefined_candidates'])>1 for a in row['activation_actions']):lines+=['其中有启用记录的别名对应多份原声明；全部候选均保留，实际采用哪一份尚未确认。']
        if row['raw'].get('overrideSkillBlackboard')or row['raw'].get('overrideTalents')or row['raw'].get('uniEquipIds')or row['raw'].get('tmplId'):lines+=['本声明带有关卡覆盖或其它培养设置；上面是固定原说明，不代表覆盖后的完整数值或实际效果。']
        if action is not None:lines+=['','【所选启用记录】',*battle.action_text(action).splitlines()]
    lines+=['','【使用提醒】','这里只作局外查阅，不启动装置或操作游戏。实际启用、击破、领取、最终数值与当前服务器结果仍需核对。','明确声明的位置可查看格子；只有既有校准允许的位置才标到固定原图，卡片和缺位置记录不会猜坐标。']
    return'\n'.join(lines)
