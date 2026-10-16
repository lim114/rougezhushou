# 根集成合同（候选，不改旧live）

我只拥有候选中新文件。旧`node_catalog.py`、`player_node_information.py`和`node_catalog_view.py`由根代理修改。不得为了此功能放宽旧typed奖励、补原`game_choice_ids`、更改资格/资源计算或减少25/57统计。

## 返回字段

```text
event_item_references(event_id)
  非精确EVENT: None，零来源读取
  源失效: status=unknown, source_valid=False, items=[]
  源有效: status=documented_reference, source_valid=True, items=[reference]

reference:
  reference_id             完整choice + documented-item + item标识
  event_id/scene_key/choice_key/choice_title/choice_description
  item_id/name/item_type='RELIC'/item_kind_name='收藏品'
  icon_reference: file/sha256/bytes/git_blob_sha1/url
  reference_kind='documented_named_item'
  original_choice_content_reference  仅原文内容佐证，不是入口
  original_item_pointer_present=False
  original_choice_entry_bound=False
  quantity_reference/actual_reward/actual_selectable=None
  source_scene_link_verified=False

item_details(event_id, scene_key, choice_key, item_id)
  同上来源资格，另给 item / reference / icon_reference / unlock_notice
  错误完整标识: ValueError，不找相似名称、不fallback首项
```

完整标识常量由模块集中导出`EVENT/SCENE/CHOICE/ITEM`，旧集成文件不必再次散布字符串。它们是静态资料身份，不是本局实例。所有返回值均为防御性副本。

## 推荐目录接缝

`event_reward_options`在逐choice循环外最多调用一次`event_item_references(e['id'])`，只将相同`scene_key/choice_key`参考追加到独立`documented_items`字段。不要并入旧`rewards`，不要把原`named_reward_found`、`named_grant_only`或领取资格升级。

对非目标事件不必新增空字段，以便原有输出可逐值保持；若根选择统一添加空字段，历史对照只允许这个明确的新字段差异，不能删除整个旧结果比较。来源失效时保留明确的补充资料unknown通知且列表为空，旧选项原文保留。

玩家说明可追加“资料写明的物品：沙盘α（收藏品）；数量与本局实际领取尚未确认。可通过下方入口查看物品说明。”原文已有基本效果，不应再把同一全文重抄成进度。

## 推荐窗口接缝

导入`DocumentedChoiceItemPanel`，按293模式只创建一个非模态窗口。父窗口增加一个紧凑入口，不加多个纵向控件。父按钮只打开阅读；`set_reference(EVENT, scope_key=current_entry_key)`不传默认选择、不操作节点绑定。

父刷新时，同一有效事件与reading key调用同scope以保留对话框阅读；换事件、失效或父条目不存在时将子窗口设为`set_reference(None, scope_key=None)`或当前目标但源失效，由子窗口清除全部旧内容。入口不得借其他事件标题或相似名称打开。

若入口与已有“场景/选项”筛选联动，务必明确是“该事件的物品资料”或仅对精确目标choice显示，不把另一选项当作沙盘α来源。对话框自己的条目始终保留完整选项名，默认未选。

父窗口原key/search/页签/文字选区/非零scroll、dossier/map_context/node_context/runtime_context不得被打开或刷新子窗口改变。非模态对话框关闭后可重用。根需要补父窗口集成测试和真实Windows脚本，候选Qt8项只覆盖新dialog。

## 需要根实际运行的范围

缓存首轮后端14项通过仅作作者候选检查。正式必要范围应包括后端14、新dialog8、根的旧17奖励/非目标37事件/统计不变对照与父阅读保存测试；不得把现有相关验收范围删掉。源失效清空、恢复未选、被篡改完整ID拒绝、三阅读页文字/图标清空需要真实Qt验证。根独立真实Windows验证后才可宣称产品通过。
