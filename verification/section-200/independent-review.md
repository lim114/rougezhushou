# 第200节节点UI独立只读审查

范围：root新增 `node_catalog_view.py`、MainWindow地图导航/刷新接线与8条新测试。未改跟踪源码，未复跑旧检查，未读私人运行数据，未操作游戏或发聊天。只用公开构造地图运行针对性 Qt 离屏探针；这不是可见Windows窗口验收。

## 实际发现

1. 未揭示 `observed_type='未知的命运'`、模板预测 `['不期而遇']` 的节点，目录核心正确保留思乡心切，但新UI最初把占位标签作为确定node_type传入资格判定，显示“已列条件不符”。源类型检查为False，实际应为None/资格未确认。本图节点详情也同路径。已先行报告root；root修改后同探针观测到unknown，未把模板候选提升为已知观测。
2. 合法可选输入 `content_history=None`：`node_dossier` 接受并规范为 `[]`，新UI目录标题定位的星号展开抛 `TypeError: Value after * must be an iterable, not NoneType`；本图节点详情循环抛 `TypeError: 'NoneType' object is not iterable`。实际由 `set_map_context` 周期刷新或本图节点刷新触发。已先行报告root；root将两处改为 `(get(...) or [])` 后，同探针两个路径都不再抛异常。

复现：`review_node_ui_200.py`。最近探针JSON为 `review-node-ui-200-probes.json`；未知类型首次失败输出是excluded，root随后实时修复，最近回执是unknown。首次失败事实在本文保留，不将重跑成功改写为从未失败。

## 其余审查结论

MainWindow定位分支验证本局epoch、zone、template、nodeId以及严格整数row/col，在当前地图实体上核对位置后只导航助手预览。刷新由 MapView.set_map 发出当前所选节点信号，再更新独立目录map_context，最终使用新的图、条件及资源；新局清空地图时也会清除目录位置来源。当前/历史内容标题位置候选明示同名身份仍须核验，事件作战下拉保留原始精确资料候选，未把选中预览宣称为实际触发。未发现另一个有可达证据的错误绑定或崩溃路径。

旧窗口/游戏/聊天行为未在本独立审查执行，仍由root到期全量范围验收。
