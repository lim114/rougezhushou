"""Consolidate source-backed findings only; no projection acceptance or functional progress."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
load=lambda p:json.loads(p.read_bytes())
inventory=load(HERE/'original-input-inventory.json')
coverage=load(HERE/'level-coverage.json')
signatures=load(HERE/'preview-signatures-fields.json')
cfg=load(HERE/'preview-camera-cfg.json')
config=load(HERE/'camera-config-value-type.json')
fetched=load(HERE/'unity-properties-fetch.json')
pins=dict(inventory['source_pins'])
extra=['.cache/research/map-projection-044/maa-TileCalc2.hpp',
 '.cache/research/map-projection-044/source-receipts.json',
 '.cache/research/p2-native-current-263/mapping-verification.json',
 '.cache/research/p2-native-current-263/read_metadata_static.py',
 'rouge/map_projection.py','rouge/data/battle-map-projections.json',
 'rouge/data/fixed-landmark-references.json','PROJECT_PROGRESS.md',
 'verification/sections/297-preparation/map-first-fit/initial-fit-results.json',
 '.cache/batch186-285/p2-units/research/public-enemy-hotfix/cameracontrollerhotfixer.lua',
 '.cache/batch186-285/p2-units/research/public-enemy-hotfix/vcameracontrollerhotfixer.lua']
for name in extra:
 raw=(ROOT/name).read_bytes();pins[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
for name,pin in pins.items():
 raw=(ROOT/name).read_bytes()
 assert len(raw)==pin['bytes']and sha256(raw).hexdigest()==pin['sha256'],name
assert coverage['stage_count']==105 and coverage['unique_level_urls']==68
assert not coverage['missing_level_urls']and not coverage['sha_mismatch_stage_ids']
assert all(row['camera_fields']=={'cameraPlugin':''}and row['mapData_camera_fields']=={}for row in inventory['levels'])
assert cfg['dll_sha256']==signatures['dll_sha256']==config['dll_sha256']
assert cfg['metadata_sha256']==signatures['metadata_sha256']==config['metadata_sha256']
by_index={row['index']:row for row in signatures['methods']}
assert by_index[34265]['return_type']=='UnityEngine.Sprite'
assert config['types'][0]['name']=='Torappu.Battle.MapGraphic+CameraConfig'
assert [(x['name'],x['type'])for x in config['types'][0]['fields']]==[
 ('focus','UnityEngine.Transform'),('cameraOffset','UnityEngine.Vector3')]
assert len(cfg['methods'])==11 and all(not method['limits']for method in cfg['methods'])
failed=load(ROOT/'verification/sections/297-preparation/map-first-fit/initial-fit-results.json')
failed_rows=[{'id':row['id'],'max_error_px':max(x['error_px']for x in row['checks']),
 'accepted':False,'threshold_px':4}for row in failed]
assert {row['id']for row in failed_rows}=={'ro6_c_2','ro6_c_4'}
assert all(row['max_error_px']>4 for row in failed_rows)
result={
 'kind':'SECTION298_MAP_CAMERA_SOURCE_RESEARCH_ONLY_NO_FUNCTIONAL_COMPLETION',
 'at_utc':datetime.now(timezone.utc).isoformat(),
 'conclusion':'现有原件不足以安全建立固定mapreview原图的通用投影。找到独立的预览图资源加载链和战斗相机/地面世界坐标链，但未取得两者到同一原图生成过程的绑定。不是证明通用投影不可能。',
 'can_implement_universal_mapping_from_current_evidence':False,
 'new_calibration_or_product_capability_delivered':False,
 'existing_scope_unchanged':{'regular':[12,24],'direct':[10,18,58],'whole_map_gaps':[81,59]},
 'existing_rejected_first_fits':failed_rows,
 'verified_facts':[
  {'fact':'105条固定作战引用68个唯一原level URL；68份缓存原件全部存在，按每条stage引用逐SHA匹配。',
   'evidence':'level-coverage.json; original-input-inventory.json/source_pins'},
  {'fact':'这68份level的cameraPlugin均为空字符串；mapData键为map/tiles/blockEdges/tags/effects/layerRects，不直接含camera/view/projection参数。',
   'scope':'已解析原level的顶层与mapData，不把这一点扩成所有资源中不存在相机。','evidence':'compact-inventory.json; original-input-inventory.json/levels'},
  {'fact':'已保存的map_camera_views源码说明是MAA作战定位用途；已有044研究已明确预览FOV/crop未证，FOV38探测未作为默认。',
   'evidence':'.cache/research/map-projection-044/resource-readme.md note5; evidence.json/remaining_unknown'},
  {'fact':'旧MAA TileCalc2在其作战定位函数用1280×720、默认垂直半视场20度及特定宽高比位置修正；这些不是固定mapreview PNG捕获参数的证据。',
   'evidence':'.cache/research/map-projection-044/maa-TileCalc2.hpp: camera_pos/camera_matrix_from_trans/world_to_screen'},
  {'fact':'实际安装DLL及metadata SHA与原索引固定来源相同；11个具名方法进行了纯文件CFG及签名读取，1531行方法指令重新对原DLL字节校验。',
   'evidence':'cfg-process.json; preview-camera-cfg.json; preview-signatures-fields.json',
   'not_claimed':'未证明当前热更新、动态分支、场景对象、所有被调函数或任何游戏运行结果。'},
  {'fact':'StageDataUtil.LoadStagePreviewMap(string stageId, ILoadAsset assetLoader)返回UnityEngine.Sprite；CommonMapPreviewDlg._imgMapPreview为UnityEngine.UI.Image。',
   'evidence':'preview-signatures-fields.json methods34265/typeCommonMapPreviewDlg'},
  {'fact':'CommonMapPreviewDlg.OnRender、RoguelikeFocusView.LoadPreviewMap及RL06FocusViewPlugin._LoadPreviewMap直接调用GetStageMapPreviewPath，并可走UIAssetLoader.get_missingSprite回退。',
   'evidence':'preview-camera-cfg.txt lines528..606,918..1027,1247..1356',
   'interpretation':'支持固定资源展示链，不提供生成这张资源时采用的相机矩阵或裁切。'},
  {'fact':'Battle.Map.MapToWorldPosition的普通分支先取get_anchorTransform；MapGraphic.GetCameraConfig返回的类型仅有focus:Transform与cameraOffset:Vector3两个字段。',
   'evidence':'preview-camera-cfg.txt lines254..310/314..401; camera-config-value-type.json',
   'not_claimed':'没有取得实际focus/anchor Transform矩阵，也不把WorldToMap输入输出等同PNG像素。'},
  {'fact':'固定相机摘要对ro6_c_2/c_4记highlandHeight约0.3、cameraView3及各自focus/offset；这些是相机资产线索，未包含mapreview捕获FOV、viewport、裁切、后处理和原图blob绑定。',
   'evidence':'ro6-resource-camera-records.json exact ro6_c-2/ro6_c-4'},
  {'fact':'官方Unity API说明屏幕点依赖相机，fieldOfView为垂直角度，pixelRect为渲染像素矩形，修改projectionMatrix可脱离fieldOfView。',
   'evidence':'Camera.WorldToScreenPoint.html; Camera-fieldOfView.html; Camera-pixelRect.html; Camera-projectionMatrix.html',
   'scope':'2023.2官方通用API，不是本游戏或该PNG导出环境的版本/数值证明。'}],
 'missing_evidence':[
  '固定mapreview PNG的原始生成或导出脚本，以及与当前原图blob一致的资产版本。',
  '该生成过程实际使用的camera worldToCamera/projection matrix或可唯一重建的Transform/FOV/aspect/orthographic/near/far及任何自定义矩阵。',
  '捕获viewport/render target、缩放、裁切/填边与输出PNG尺寸的精确关系。',
  '逻辑网格中心与场景anchor/地面层的世界变换；高台高度、表面和立体入口不能借同一零高平面。',
  '旧公开资源版本与当前安装、热更新的适用关系，不能只凭相同stage名称借用。'],
 'risk_and_alternative_explanations':[
  '512×286原图不是1280×720的等比例512×288输出；不能凭2px之差断定上下裁切。',
  '仅有相机位置或focus/offset不足以唯一确定屏幕投影；直接套MAA40度会把未知当已知。',
  '两次首拟合失败只能说明既定观测/模型未过4px门，不证明地图不存在平面投影，也不证明必为原点/透视/人工读数中的某一原因。',
  '若为追求过门重新调读点或用拟合输出作验证，会产生泄漏；本轮没有进行这些操作。',
  '扩大原生调用正常性证明但仍无导出camera资产，不会实质减少固定原图的81/59缺口。'],
 'next_actions':[
  {'priority':1,'scope':'恢复此地图路线的确切条件','action':'取得原mapreview导出工具或固定相机prefab/截图配置与PNG blob的唯一绑定，再静态重建；不做新手工调点。',
   'acceptance':'使用原始参数直接给出投影；既有独立holdout不参与重建，保持4px门；高台/偏移另有证才扩域。',
   'currently_ready':False},
  {'priority':2,'scope':'可独立推进的P3候选','action':'转到PROJECT_PROGRESS的4个辅助实体图片精确ID/原图来源关联；仅在官方资源表与图像blob唯一绑定后接入玩家信息。',
   'acceptance':'实际实体身份、原始图像字节和用途对应清楚；未知档次/实例资格保持未知，不通过名字相似配图。',
   'currently_ready':False,'reason':'这是建议的下一研究入口，尚未在本审计查证，不能预报为可完成298功能。'}],
 'preparation_failures_and_limits':[
  '初次过宽rg查询输出被截断；之后改为具体缓存目录/机器JSON筛选，没有以截断输出证明不存在。',
  '初次Windows rg glob目录写法返回123、读不存在的battle_projection.py；实际实现为map_projection.py。',
  '一次PowerShell -c内字符串$$被扩展，summary helper报empty separator；改为独立.py文件后成功，不是产品测试失败。',
  '三个官方property URL初误用方法点号语法，真实HTTP404保留unity-reference-fetch.json；改用已查证的连字符property URL后200原件另存，不将404当API缺失。'],
 'source_pins':pins,
 'file_only':True,'game_dll_executed':False,'process_memory_read':False,'private_state_read':False,
 'new_manual_points_or_fit_executed':False,'Qt_or_product_tests_executed':False,'production_or_Git_modified':False,
 'section298_completed':False}
with(HERE/'FINDINGS.json').open('xb')as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
members={}
for path in sorted(HERE.iterdir()):
 if path.is_file()and path.name!='research-manifest.json':
  raw=path.read_bytes();members[path.name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
manifest={'kind':'SECTION298_CACHE_MAP_CAMERA_RESEARCH_MEMBERS_NOT_ACCEPTANCE',
 'files':members,'input_pins_all_fresh_match':True,'functional_or_calibration_pass_claimed':False}
with(HERE/'research-manifest.json').open('xb')as stream:stream.write((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'findings_sha256':sha256((HERE/'FINDINGS.json').read_bytes()).hexdigest(),
 'manifest_sha256':sha256((HERE/'research-manifest.json').read_bytes()).hexdigest(),
 'source_pin_count':len(pins),'member_count':len(members),'decision':'NOT_READY_FOR_UNIVERSAL_PROJECTION',
 'new_fit_game_Qt_tests_product_or_Git_operations':False},ensure_ascii=False))
