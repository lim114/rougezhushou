# 第296节反查API合同

公共模块rouge.battle_event_references，主函数stage_event_references(stage_id)、resolve_stage_event_reference(stage_id, token)、source_data()。没有状态、当前库存或来源覆盖输入。

stage_id必须type为str且为固定8ID，否则主查询/resolve直接None，零来源读取。

## 返回对象

有效status=documented_reference，reference_kind=fixed_battle_documented_event_choices；source_valid=true。stage_reference含原7字段stage_id/name/code/difficulty/level_id/is_boss_parameter/source_selector，另level_source完整url/sha256/bytes。rows是准入，excluded_rows是明确难度排除；原顺序保留。

每行：

    reference_id: battle-event:加64位SHA，完整来源身份的稳定短字符串
    stage_id, stage_reference
    event_id, event_title, event_node_types
    event_documented_main_floors: 仅事件资料主层
    event_floor_scope: event_documented_main_floors_only
    scene_key, choice_key, choice_title, choice_description, conditional_text
    scene_number, choice_number: 按完整event.scenes/scene.choices实际顺序1起
    stage_page: title/url/anchor_text
    source_difficulty_matches: null或true；明确排除为false
    excluded_by_explicit_difficulty: bool
    token: 准入完整对象；排除null

top/每行stage_global_floors=null、full_stage_origin_floors_known=false；actual_stage_id/actual_choice_eligible/actual_entered始终null。每行source_scene_link_verified=false，top current_server_verified=false。scope_counts为整个固定包14原边/11准入/3排除/5事件/8选项/8关卡，不是本局概率。raw_edge_count是当前stage资料关系数。

## token

    reference_kind: fixed_battle_to_documented_event_choice
    reference_id, stage_id, event_id, scene_key, choice_key
    scene_number, choice_number
    stage_record: 原7字段（不加level_source）
    stage_page: 完整title/url/anchor_text
    level_source: 完整url/sha256/bytes
    source_identity:
      manifest_sha256, reference_data_sha256, node_catalog_sha256
      event_planning_data_sha256, battle_previews_sha256, game_commit
      documents: [{revision, sha256}, ...]

resolve必须先fresh重建，再递归比较整个token。多key/缺key、dict或str子类、bool冒充int、stage变体、原文页面或源SHA改变均拒绝。返回当前匹配row的副本或None，不执行导航/状态修改。

## 来源失败

status=unknown，source_valid=false，stage_reference/source_identity=null，rows/excluded_rows=[]，不保留旧token；上述actual仍null。source_data失败返回None，有效时返回小参考JSON的副本加source_identity，不暴露内部大解析缓存。

## 根UI接缝

combo currentData存reference_id短str；默认-1，不选首项、不自动发token。玩家显示事件中文、真实场景/选项号与完整选项名、事件主层及未知边界。点击时用当前stage和完整旧token调用resolve，再使用fresh返回的精确event/scene/choice打开节点资料；不是游戏操作。当前stage改变或source失效必须清旧行/选择。相同stage刷新可按稳定ID保存阅读，但不能跳过点击前fresh整token核对。
