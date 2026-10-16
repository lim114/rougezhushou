# 独立只读接口合同

模块 `rouge.expedition_results`；没有data/evaluator/当前状态覆盖入口。

- `source_data()`：返回完整且刚核验来源的深复制包，失效返回None。
- `event_reference(event_id)`：只接受精确内置字符串`community_group_024`；其他值立即None、不读源。有效返回`status=documented_reference`、`source_valid=True`、三行`rows`、独立`return_explanatory_reference`、item/icon/source与版本边界。
- `choice_reference(event_id, scene_key, choice_key)`：只接受开始场景的三条完整键；不使用标题、后缀或同名fallback。有效返回该行与source。说明块不作为第四个选择返回。
- `annotation_reference(event_id, scene_key, choice_key)`：只接受`community_group_024:scene:2:choice:1`及其精确event/scene；返回原description/presentation_role、`is_actual_button=False`、`effect_phase=on_return`、2希望与信标资料引用。
- `item_details(event_id, scene_key, choice_key)`：仅源头完整选择，返回完整item、已绑定固定图标、原选择引用及解锁说明；不能从内部、休息或说明块调用。

三行原顺序为`community_group_024:scene:0:choice:0/1/2`，原游戏ID依次`choice_ro6_scout_1/3/2`。资源数组统一为`{resource: hope, quantity_reference: 2}`；内部探索两个资源数组均为空（不代表没有物资），源头只在`return_resource_references`有2希望，休息只在`immediate_resource_references`有2希望。`effect_phase_reference`两派出为on_return，休息为on_choice。

`documented_return_item`只在源头存在，item_id为`rogue_6_relic_final_3`，数量未在原文数字说明所以quantity_reference=None。`promotion_reference`源头False、内部和休息None；它是资料值，实际进阶仍None。派出`dispatch_reference.special_region_equivalence=None`；“喙”`applies_to_root_branch=None`，不强套特殊分支。

精确目标的来源失效返回`status=source_unavailable`、`source_valid=False`、rows空、return_explanatory_reference/item/icon_reference/source/source_reference/reference均None，保留目标身份与中文提示；不返回缓存内容。源恢复后API可再次返回资料，但模型不保存/重选界面选择。所有actual_*为None、inventory_updated/eligibility_evaluated/current_server_verified为False。
