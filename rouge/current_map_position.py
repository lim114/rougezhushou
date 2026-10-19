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
        return {'data':data,'current':current,'source_identity':MANIFEST_SHA256,'absolute_accuracy_verified':False}
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
    if mapping:
        envelope={k:level[k]for k in ref['data']['geometry_keys']};digest=sha256(json.dumps(envelope,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if mapping['current_level_key']!=key or mapping['image']!=image or mapping['full_selected_geometry_sha256']!=digest:return None
    return {'stage_id':stage_id,'stage_name':stage['name'],'rows':len(grid),'cols':len(grid[0]),'map':deepcopy(grid),'tiles':deepcopy(tiles),'complete_current_geometry':{k:deepcopy(level[k])for k in ref['data']['geometry_keys']},'current_level_key':key,'image':deepcopy(image),'points':points,'mapping_evidence':mapping,'source_identity':ref['source_identity'],'full_map_projection_verified':False,'supports_inverse':False,'supports_segments':False,'actual_combat_positions_verified':False,'run_updated':False}
def cell_reference(result,row,col):
    if result is None or type(row)is not int or type(col)is not int or not 0<=row<result['rows']or not 0<=col<result['cols']:return None
    tile=deepcopy(result['tiles'][result['map'][row][col]]);point=next((deepcopy(p)for p in result['points']if p['row']==row and p['col']==col),None)
    return {'row':row,'col':col,'tile':tile,'point':point,'mapped_to_original':point is not None,'actual_spawn_position':None,'actual_deployment_qualification':None}
def summary_text(result):
    return '\n'.join([result['stage_name'],'','【怎样查看】','在左侧方格图点选格子，或从已核对格子列表中选择。右侧显示这场作战的固定原图。',f"本图有{result['rows']}行、{result['cols']}列；目前有{len(result['points'])}个格子中心能与原图对应。",'只有核对过的近似中心会画出标记；其它格子不会按相邻位置猜测。',('这些中心只在新旧完整地形导出、相机字段和原图字节均一致时复用；没有新增测量，也没有证明完整地图或战斗中的位置。'if result['points']else'本图当前地形和原图可读，但没有满足条件的已核对中心；右侧不画位置。'),'地形只是固定资料，不表示本局一定出现、能部署、敌人从这里出场或经过。','高台表面、未读格、实际出生偏移与地图上的整段路径仍待核验；右侧图片不能点击反推其它格子。'])
def cell_text(result,cell):
    if cell is None:return summary_text(result)
    tile=cell['tile'];terrain={'tile_floor':'普通地面','tile_road':'道路','tile_wall':'高台地块','tile_start':'敌人入口标记','tile_end':'保护目标标记','tile_forbidden':'地图边界或禁行地块'};heights={'LOWLAND':'地面','HIGHLAND':'高台'};buildable={'NONE':'不可部署','MELEE':'近战位','RANGED':'远程位','ALL':'全部类型'}
    return '\n'.join([f"第{cell['row']+1}行 · 第{cell['col']+1}列",'地形：'+terrain.get(tile.get('tileKey'),'名称尚未整理'),'高度标注：'+heights.get(tile.get('heightType'),'未知'),'部署标注：'+buildable.get(tile.get('buildableType'),'未知'),'原图位置：'+('已标出核对过的近似中心。'if cell['mapped_to_original']else'本格中心尚未核对，不在原图上猜位置。'),'这些是静态地块标注，不表示当前能部署或敌人实际站位；此页没有读取战斗。','没有从本格推断出怪、隐藏分支或实际路线。'])
