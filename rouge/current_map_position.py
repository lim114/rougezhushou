"""Read-only current static grid and source-qualified observed centers."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import current_battle_reference as battle
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-map-position-319';DATA='rouge/data/current-map-position.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='c84bd87d6b0825e5e5e296d4d32f0d2626d4b252122e54772cf3d9f46cb54b67'
UNAVAILABLE='本版本地图位置资料无法核对，旧格子、原图与标记已清除；恢复后请重新选择。'
def packet():
    try:
        from .current_terrain import evidence_identity
        terrain_identity=evidence_identity()
        if terrain_identity is None:return None
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        manifest=json.loads(raw);objects={}
        if manifest['schema']!='current_map_position_319_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
        for name,pin in manifest['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            objects[name]=raw
        current=battle.packet()
        if current is None:return None
        data=json.loads(objects[DATA])
        if set(data['all_current_stage_ids'])!=set(current['version']['current']['details']['stages']):return None
        return {'data':data,'current':current,'source_identity':sha256((MANIFEST_SHA256+terrain_identity).encode()).hexdigest(),'terrain_source_identity':terrain_identity,'absolute_accuracy_verified':False}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError):return None
def stage_reference(stage_id):
    ref=packet()
    if ref is None or type(stage_id)is not str:return None
    stage=ref['current']['version']['current']['details']['stages'].get(stage_id)
    if stage is None:return None
    key='levels/'+stage['levelId'].lower()+'.json';level=ref['current']['inputs']['levels'][key];image=ref['current']['version']['images']['images'][stage_id]
    if battle.version.image_bytes(image)is None:return None
    grid=level['mapData']['map'];tiles=level['mapData']['tiles']
    if not grid or not grid[0]or any(len(row)!=len(grid[0])or any(type(i)is not int or not 0<=i<len(tiles)for i in row)for row in grid):return None
    mapping=deepcopy(ref['data']['compatible_stages'].get(stage_id));points=mapping['points']if mapping else[]
    identity=ref['source_identity']
    from . import current_map_markers as symbols
    if stage_id in symbols.STAGES:
        observed=symbols.mapping_for(stage_id,ref['current'])
        if observed is None or mapping is not None:return None
        mapping=observed['mapping'];points=mapping['points'];identity=(identity,observed['source_identity'])
    from . import boss_map_markers as boss_symbols
    if stage_id in boss_symbols.STAGES:
        observed=boss_symbols.mapping_for(stage_id,ref['current'])
        if observed is None or mapping is not None:return None
        mapping=observed['mapping'];points=mapping['points'];identity=(identity,observed['source_identity'])
    if mapping:
        envelope={k:level[k]for k in ref['data']['geometry_keys']};digest=sha256(json.dumps(envelope,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if mapping['current_level_key']!=key or mapping['image']!=image or mapping['full_selected_geometry_sha256']!=digest:return None
    return {'stage_id':stage_id,'stage_name':stage['name'],'rows':len(grid),'cols':len(grid[0]),'map':deepcopy(grid),'tiles':deepcopy(tiles),'complete_current_geometry':{k:deepcopy(level[k])for k in ref['data']['geometry_keys']},'current_level_key':key,'image':deepcopy(image),'points':points,'mapping_evidence':mapping,'source_identity':identity,'full_map_projection_verified':False,'supports_inverse':False,'supports_segments':False,'actual_combat_positions_verified':False,'run_updated':False}
def cell_reference(result,row,col):
    if result is None or type(row)is not int or type(col)is not int or not 0<=row<result['rows']or not 0<=col<result['cols']:return None
    tile=deepcopy(result['tiles'][result['map'][row][col]]);point=next((deepcopy(p)for p in result['points']if p['row']==row and p['col']==col),None)
    from .current_terrain import terrain_info
    return {'row':row,'col':col,'tile':tile,'terrain':terrain_info(tile),'point':point,'mapped_to_original':point is not None,'actual_spawn_position':None,'actual_deployment_qualification':None}

def terrain_locations(result,tile_key=None):
    if result is None or(tile_key is not None and type(tile_key)is not str):return []
    from .current_terrain import terrain_info
    rows=[]
    for row in range(result['rows']):
        for col in range(result['cols']):
            tile=result['tiles'][result['map'][row][col]]
            if tile_key is not None and tile.get('tileKey')!=tile_key:continue
            rows.append({'row':row,'col':col,'tile_key':tile.get('tileKey'),'name':terrain_info(tile)['name'],'mapped_to_original':any(p['row']==row and p['col']==col for p in result['points'])})
    return rows
def summary_text(result):
    if (result.get('mapping_evidence')or{}).get('annotation_kind')=='visible_map_symbol':
        entries=sum(p['tile_key']=='tile_start'for p in result['points']);targets=sum(p['tile_key']=='tile_end'for p in result['points'])
        return chr(10).join([result['stage_name'],'','【怎样查看】','从列表选入口或保护目标，或在左侧格子图点选；右侧会在固定原图上标出相应的可见标志。',f'本图{result["rows"]}行、{result["cols"]}列，已对照{entries}个入口标志与{targets}个保护目标标志。','','【标注范围】','这些位置直接取自本图可见的红色入口和蓝色保护目标标志；不是从旧图、同名关卡或附近格子外推。','标记是可见标志的近似中心，精确误差尚未测量；它不表示敌人实际落脚点、出生偏移或随机范围。','其余地块没有新增位置，不插值、不反向点击推算，也不连成实际路线。','每份配置各自核对完整地形、相机字段和固定原图；不能只凭同名或同图套用。','本页只看固定地图资料，不读取战斗、不操作游戏，也不代表本局一定进入这份配置。'])
    return '\n'.join([result['stage_name'],'','【怎样查看】','在左侧方格图点选格子，或从已核对格子列表中选择。右侧显示这场作战的固定原图。',f"本图有{result['rows']}行、{result['cols']}列；目前有{len(result['points'])}个格子中心能与原图对应。",'只有核对过的近似中心会画出标记；其它格子不会按相邻位置猜测。',('这些中心只在新旧完整地形导出、相机字段和原图字节均一致时复用；没有新增测量，也没有证明完整地图或战斗中的位置。'if result['points']else'本图当前地形和原图可读，但没有满足条件的已核对中心；右侧不画位置。'),'地形只是固定资料，不表示本局一定出现、能部署、敌人从这里出场或经过。','高台表面、未读格、实际出生偏移与地图上的整段路径仍待核验；右侧图片不能点击反推其它格子。'])
def cell_text(result,cell):
    if cell is None:return summary_text(result)
    if cell.get('point',{} )and cell['point'].get('kind')=='visible_map_symbol':
        return chr(10).join([f"第{cell['row']+1}行 · 第{cell['col']+1}列",cell['point']['label'],'原图已标出这个可见标志的近似中心；精确误差尚未测量。','这是地图标志位置，不是敌人实际脚点；出生偏移、随机范围和实际移动仍未知。','只对应本格，不推算相邻地块、部署资格或连接路线。'])
    tile=cell['tile'];terrain=cell['terrain'];heights={'LOWLAND':'地面','HIGHLAND':'高台'};buildable={'NONE':'不可部署','MELEE':'近战位','RANGED':'远程位','ALL':'全部类型'}
    lines=[f"第{cell['row']+1}行 · 第{cell['col']+1}列",'地形：'+terrain['name'],'高度标注：'+heights.get(tile.get('heightType'),'未知'),'部署标注：'+buildable.get(tile.get('buildableType'),'未知'),'原图位置：'+('已标出核对过的近似中心。'if cell['mapped_to_original']else'本格中心尚未核对，不在原图上猜位置。')]
    if terrain['effects']:lines+=['','【本格用途与效果】',*terrain['effects']]
    if terrain['unknowns']:lines+=['','【尚需注意】',*terrain['unknowns']]
    lines+=['','这些是静态地块标注，不表示当前能部署或敌人实际站位；此页没有读取战斗。','没有从本格推断出怪、隐藏分支或实际路线，也没有将地形效果写入本局计算。']
    return '\n'.join(lines)
