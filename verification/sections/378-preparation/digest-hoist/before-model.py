"""Find fixed stages by their exact terrain declarations; never infer live state."""
from copy import deepcopy
from hashlib import sha256
import json
from . import current_battle_reference as battle
from . import current_stage_directory as directory
from . import current_terrain as terrain

NOTICE='按地形和效果查找固定关卡，再查看这一类地块的准确格子。同名关卡和不同地块参数分别保留；这不是本局出现范围或部署资格。'
UNAVAILABLE='地形目录的来源无法核对，旧条目和地图已清除；恢复后请重新选择。'
KINDS=((None,'全部地形用途'),('entry','侵入点'),('goal','保护目标'),('passage','通道'),('hazard','危险地形'),('healing','生命回复'),('tactical','推拉效果'),('cover','草丛'),('highland','高台'),('ground','地面'),('blocked','阻隔或禁入'),('placeholder','占位'),('unknown','名称或用途未确认'))

def digest(value):
    return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def packet():
    identity=terrain.evidence_identity();current=battle.packet();classified=directory.packet()
    if identity is None or current is None or classified is None:return None
    rows=[]
    try:
        stages=current['version']['current']['details']['stages']
        if set(stages)!=set(classified['data']['rows']):return None
        same_names={}
        for sid,stage in stages.items():same_names.setdefault(stage['name'],[]).append(sid)
        for sid,stage in stages.items():
            group=classified['data']['rows'][sid]
            if group['original_stage']!=stage:return None
            level_key='levels/'+stage['levelId'].lower()+'.json';level=current['inputs']['levels'][level_key]
            tiles=level['mapData']['tiles'];grid=level['mapData']['map'];cells={}
            if not grid or not grid[0] or any(len(row)!=len(grid[0]) for row in grid):return None
            for r,row in enumerate(grid):
                for c,index in enumerate(row):
                    if type(index)is not int or not 0<=index<len(tiles):return None
                    cells.setdefault(index,[]).append([r,c])
            for index,positions in cells.items():
                tile=tiles[index];info=terrain.terrain_info(tile)
                rows.append({'key':[sid,index],'stage_id':sid,'tile_index':index,'stage_name':stage['name'],
                    'same_name_stage_number':same_names[stage['name']].index(sid)+1,
                    'same_name_stage_count':len(same_names[stage['name']]),'terrain_setting_number':index+1,
                    'floor':group['floor'],'play_kind':group['play_kind'],'tile_key':tile.get('tileKey'),
                    'terrain_name':info['name'],'terrain_kind':info['kind'],'terrain':info,
                    'tile':deepcopy(tile),'cells':positions,'level_key':level_key,
                    'stage_sha256':digest(stage),'map_data_sha256':digest(level['mapData'])})
        return {'rows':rows,'source_identity':(current['identity'],classified['source_identity'],identity),
                'stage_count':len(stages),'actual_occurrence':None,'run_updated':False}
    except(KeyError,TypeError,ValueError,OverflowError):return None

def rows(search='',kind=None,floor=None,play_kind=None,*,reference=None):
    if type(search)is not str or kind not in dict(KINDS) or floor not in dict(directory.FLOORS) or play_kind not in dict(directory.KINDS):raise ValueError('不支持的筛选条件。')
    ref=packet() if reference is None else reference
    if ref is None:return []
    term=search.strip().casefold()
    return [deepcopy(row) for row in ref['rows'] if (kind is None or row['terrain_kind']==kind)
        and(floor is None or row['floor']==floor) and(play_kind is None or row['play_kind']==play_kind)
        and(not term or term in (' '.join([row['stage_name'],row['terrain_name'],*row['terrain']['effects'],*row['terrain']['unknowns']])).casefold())]

def detail(key,*,reference=None):
    ref=packet() if reference is None else reference
    if ref is None or type(key)not in(tuple,list) or len(key)!=2 or type(key[0])is not str or type(key[1])is not int:return None
    row=next((r for r in ref['rows'] if r['key']==list(key)),None)
    if row is None:return None
    return {'row':deepcopy(row),'source_identity':ref['source_identity'],'actual_occurrence':None,'actual_deployment_qualification':None,'actual_effect_applied':None,'run_updated':False}

def exact_map(info):
    if type(info)is not dict:return None
    from . import current_map_position as positions
    fresh=packet()
    if fresh is None or info.get('source_identity')!=fresh['source_identity']:return None
    known=detail(info.get('row',{}).get('key'),reference=fresh)
    if known!=info:return None
    row=info['row'];current=battle.stage_reference(row['stage_id']);mapped=positions.stage_reference(row['stage_id'])
    if current is None or mapped is None:return None
    if digest(current['stage'])!=row['stage_sha256'] or digest(current['level']['mapData'])!=row['map_data_sha256']:return None
    if mapped['current_level_key']!=row['level_key'] or mapped['map']!=current['level']['mapData']['map'] or mapped['tiles']!=current['level']['mapData']['tiles']:return None
    return mapped

def effect_summary(row):
    effects=row['terrain']['effects']
    numeric=[text for text in effects if any(character.isdigit() for character in text)]
    return '；'.join(numeric or effects[:1]) or ('效果尚未核验' if row['terrain']['unknowns'] else '原资料未列额外效果')

def label(row):
    identity=('同名关卡资料'+str(row['same_name_stage_number'])+'/'+str(row['same_name_stage_count'])
        +' · 地形设置'+str(row['terrain_setting_number']))
    return (row['terrain_name']+' · '+row['stage_name']+' · '+dict(directory.FLOORS)[row['floor']]
        +' · '+dict(directory.KINDS)[row['play_kind']]+' · '+identity+' · '+str(len(row['cells']))+'格'
        +'\n效果摘要：'+effect_summary(row))

def player_text(info):
    if info is None:return '选择一种地形记录，查看效果、适用限制和对应格子。'
    row=info['row'];lines=[row['terrain_name']+' · '+row['stage_name'],'',
        '【在哪些格子】',dict(directory.FLOORS)[row['floor']]+' · '+dict(directory.KINDS)[row['play_kind']],
        '同名关卡资料'+str(row['same_name_stage_number'])+'/'+str(row['same_name_stage_count'])+' · 地形设置'+str(row['terrain_setting_number'])+'。',
        '本份关卡资料中，共'+str(len(row['cells']))+'格使用这套完全相同的地形设置。',
        '资料编号和地形设置序号只用于区分固定资料，不是游戏中的关卡顺序、难度或地图坐标。',
        '右侧选择具体格子后可打开方格图；只有已核对的位置才会标在固定原图上。','',
        '【这份地块的用途与效果】',*(row['terrain']['effects'] or [('效果资料尚未核验，不能判断是否有额外效果。' if row['terrain']['unknowns'] else '原资料未为这类地块提供额外效果。')])]
    if row['terrain']['unknowns']:lines+=['','【哪些地方还不能确定】',*row['terrain']['unknowns']]
    lines+=['','【适用范围】',NOTICE,'不同参数的同类地块不合并；搜索命中不代表本局会进入本关、能部署、实际触发或受到该效果。',
            '通道入口和出口不在此自动配对；危险地形不推算首次生效、命中时刻或最终伤害。']
    return '\n'.join(lines)
