# 伪装资料接口合同

模块：`rouge.enemy_form_reference`，无Qt、网络或状态写入。

`disguise_reference(stage_id,enemy_id,level)` 仅支持 `ro6_n_2_3/ro6_e_2_3` 与四个明确 `enemy_2133_shdopl_lancer/mpmage/sword/demonk`、严格整数级别0的8个组合。布尔、浮点、未知等级、基础原型或其他关卡/别名均返回None且不读来源，不按名字或资源猜绑定。

成功返回 `source_valid=True,status='documented_reference'`，以及：

- `reference` 完整行；顶层同时提供该行字段。
- `body_reference`：固定本关本体完整对象，保留名称“空植体”及未定义分类。
- `disguise_enemy_reference`：同一固定关卡明确指定敌人的完整独立对象；不是实际伪装实例，也不代表本体能力。
- `complete_original_reference`：原关卡完整 `enemyDbRefs` 对象，包含未赋值的分类与完整召唤黑板。
- `declared_summon_enemy_key`、`selected_disguise_reference_level=0`、`declared_summon_level=None`。
- `documented_variant_name`、`community_base_name`、`fixed_name`；`documented_base_tier_reference='普通'` 与 `fixed_body_tier=None` 分别保存。
- `documented_lifecycle`：三阶段 `{phase_key,title,text,conditions,source_quotes}`；`source_differences` 保留名称、面板、等级、触发措辞及原型适用边界。
- `source` 原件、修订与URL；`source_identity={manifest_sha256,data_sha256}`；`scope_notice`。

`actual_form,actual_rank,actual_spawn_success,actual_disguise_enemy,actual_disguise_level,actual_damage_event,actual_reveal_time,actual_position,actual_remaining_route,actual_body_attributes,actual_disguise_abilities,actual_current_server_eligibility` 全为None。`modifiers_changed,maps_changed,level_type_applied,run_state_updated,current_server_verified` 全为False。

有效组合来源失效返回 `source_unavailable`，`reference/body_reference/disguise_enemy_reference/source/source_identity=None`，阶段和差异列表清空，实际状态仍未知。恢复后重新选取，不沿用旧对象。

`reference_text(result,technical=False)` 先给具名对应关系及独立能力，再说明变化条件、来源差异和未知状态。默认不显示原代码标识、黑板或原数据JSON；technical=True另附详细身份、完整对象、逐字文献与版本。None结果返回空文本，来源失效只给清空提示。

完整构建器 `scripts/build_enemy_form_reference_306.py` 只复用已有固定公开原件并核对新完整文献；不生成概率、等级继承、敌人修正或实时地图。构建器需要源包的两页完整JSON、术语完整HTML和后端模板；大文件不重复复制。
