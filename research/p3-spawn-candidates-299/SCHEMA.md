# 299 固定主队列候选资料 · 缓存合同

新增产品能力是普通战斗预览中的手动中文阅读、资料位置与敌人入口，不是新分组机制。163节已有`battle_planning.candidate_groups`与原键表，不能重记为机制查证。

模块`rouge.spawn_candidates`提供`stage_reference(stage_id)`、`action_reference(stage_id, action_id)`、`member_token(stage_id, origin_action_id, member_action_id, relation_id)`、`resolve_reference(token)`。无公共source/evaluator/data覆盖参数。分支动作不借用主队列。

有效查询envelope：`status='documented_reference'`, `source_valid=True`, `stage_id`, `stage_name`, `scope_key`(str), `origin_action_id`(None或完整主动作ID), `selected_action`(None或完整主动作), `groups`, `packages`, `source_identity`, `notice`, `actual_selection=None`, `probabilities=None`。

`selected_action`精确键：`action_id, queue_id, wave, fragment, raw_action, source_selector`。

`relation`精确键：`reference_id, kind, queue_id, wave, fragment, ordinal, display_label, group_key, package_key, members, actual_selection`。kind仅group/package，ordinal按同一队列同kind的原出现顺序。两类关系独立，package保留group_key=None成员，不宣称共同生效。不同队列、普通/紧急、同名不同动作不合并。

`member`精确键：`reference_id, action_id, action_type, type_label, display_name, display_label, queue_id, wave, fragment, declared_count, raw_action, source_selector, enemy_references, predefined_reference, spawn_reference, token, actual_selected`。enemy_references每项`id,level,name,level_type,source_role='fixed_stage_enemy_reference'`，保留全部级别。predefined_reference仅ACTIVATE：`status,alias,objects,position_is_actual=False`；objects每项`entity_id,name,raw,source_selector,display_cell,container`。无alias/重复alias/找不到alias不定位。空key ACTIVATE与EMPTY不同。

`spawn_reference`只在SPAWN+本关同ID唯一等级+基础主路线有效且起格可用时非None，精确键`stage_id,action_id,enemy_id,level,route_index_reference,level_source_sha256`，不是位置投影结果或实际出生。其他类型不能伪装该入口。

member在查询结果中自带token，避免view为每行再次query。token精确键：`kind='fixed_spawn_candidate_member',stage_id,scope_key,origin_action_id,relation_id,relation_kind,queue_id,relation_key,action_id,member_reference_id,source_identity`。source_identity精确键`manifest_sha256,battle_previews_sha256,data_sha256,level_sha256`。token没有实际选择、像素或游戏状态。伪造/多键/错scope/错origin/跨queue/跨stage均拒绝。

resolve_reference返回：`stage_id,scope_key,origin_action_id,relation`(去掉members的关系元数据),`member,token,source_identity,actual_selection=None`，否则None。caller不能把本关任意relation借给不属于它的origin动作。

非目标/非法ID/branch动作返回None。69目标来源失效时查询返回相同基础键但`status='source_unavailable',source_valid=False,stage_name/scope_key/origin_action_id/selected_action/source_identity=None,groups/packages=[]`，所有旧目标未知；token/resolve返回None。来源恢复不负责自动选择（view负责保持默认未选）。

源包绑定全9.9MB battle-previews、69关/38份原level完整字节、固定角色表中五个预置实体完整记录及原来源表SHA、数据/说明。每次查询fresh hash manifest+全battle文件+索引/名称/说明+当前关卡原level，解析快照仅内部缓存；当前`battle_data()`的source与完整选中stage JSON还须type-strict匹配独立解析值。返回只复制本次查询，不复制全包；不读取private或当前游戏。

库存285主组、215包属于固定记录数，不是敌人数/概率/实际入选/互斥次数/同时出现证明；最终构建必须重新核对。默认先中文名称/单条数量参考/类型，权重、原键、完整对象与来源放依据。实际激活、生成数、当前服务器、全局时钟仍未知。
