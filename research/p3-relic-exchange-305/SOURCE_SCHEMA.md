# 交换资料接口合同

模块：`rouge.relic_exchange_flow`。这些接口是只读文献核对，不执行游戏操作。

## 完整事件

`event_reference('community_group_025')` 返回：

- `event_title='回滚文明'`、`scenes` 完整11场景、`choices` 完整19条资料记录、`flow_notices` 玩家提示。
- `catalogue` 按原顺序的272项列表，每项为 `{item_id,name,rarity,canSacrifice,item}`；`item` 是原表完整对象。`catalogue_scope.current_complete_catalogue=False`。
- `rarity_labels` 与模块 `RARITY_LABELS` 一致：NORMAL→低稀有度、RARE→中稀有度、SUPER_RARE→高稀有度。该分档不决定奖励。
- `source_valid`、`status`、`source_identity={manifest_sha256,data_sha256}` 和原件来源。

每个 `choices` 行固定包含 `event_id,scene_key,choice_key,reference_id,choice_title,choice_description,condition_text,presentation_role,catalog_choice,documented_rules,documented_result_text,original_scene_candidates,related_stage_reference`。其中 `reference_id=choice_key`，`catalog_choice` 完整保留目录原记录，`related_stage_reference=None`。`documented_rules` 为 `{rule_id,title,text,source_refs}` 的列表，可以为空。

附加 `documented_destinations` 只保留原目录的目标场景、原文与原ID，是文献导航；每项 `actual_reached=None`。`original_choice_ids` 保留原目录ID列表。新补两个退出结果不增加目录转移边，两条分别有独立源行和同样4个完整原场景候选；`source_scene_link_verified=False`。

这两条旧导航并非空：事件页427904均写 `data-dest=5`，指向“感谢你提供了宝贵的实验材料”；调查记录349818分别写出“它见你要离开”。两份文献后续原文不一致，因此同时保存带来源的旧导航和独立补充结果，不能删除旧导航来让测试通过，也不能把其中一份当作已证服务器转移。

`choice_details(event_id,scene_key,choice_key)` 的 `.reference` 与完整事件中相应行严格相等，不另造简化行。参数必须是该事件真实三元组合。

## 提供物核对

`relic_offer_reference(item_id, *, exchange_index=1, first_exchange_item_type=None, palm_unlocked=None, owned=None)` 返回完整 `item`、`item_id`、原旗标 `can_offer_reference`、`exchange_index` 及分项 `checks`。每项为 `{key,matches,title,text}`，`matches` 只是真、假或未知。

- 次数只接受整数1或2，拒绝布尔数、浮点数和字符串。
- `owned/palm_unlocked` 只接受严格布尔或None。
- 首次类型只接受RELIC、SCRAP、None；第1次不能同时声明已经有首次交换类型。
- 第1次检查原提供物旗标、声明持有；第2次另检查声明手掌、首次同为RELIC。
- 任一分项假→`documented_condition_status='excluded'`；无假且有未知→`unknown`；全部真→`matched`。`matched` 只是列出的资料与离线声明相符，不能称作实际可选。
- 不查或修改实际库存、剩余次数、科技、奖励、掉落率。`actual_selectable,actual_consumed,actual_offered_consumed,actual_reward,actual_quantity,actual_reward_pool,quantity,reward_pool` 以及其他实际状态字段全部None，三种状态更新字段全部False。

## 失败及无关参数

非目标事件/物品或错误三元组合返回None且不读取资料。目标来源不一致返回 `status='source_unavailable',source_valid=False`，旧 `catalogue/scenes/choices/checks` 清空，`reference/source/source_identity/item/can_offer_reference=None`，实际字段仍未知。提供物失效结果保留输入 `item_id/exchange_index`，不保留旧项。

## 资料版本边界

原表固定提交与本体272件边界见README和manifest；当前编目只核语义和21个禁止提供物，不作当前完整目录或服务器证明。两个“见好就收”结果是文献结果，4个同文原场景不能反推入口。未知当前可选、实际发生、数量、奖励池和概率不得用默认值填补。
