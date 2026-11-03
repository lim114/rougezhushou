# 第 98 节本局缓存与库存输入可靠性候选

本包为 Source 候选，未导入或执行项目、测试、Wine、Git、Qt，也未改维护树或私人状态。`source-manifest.json` 的 23 个 `test_*` 方法为源码计数，不是执行结果。第 96、97 节实际完成后，由 Root 对真实当前源重新核对并应用，再运行检验、归档、commit/push。

本组保留旧 098 候选的两个行为目标，并补完整功能所需的消费边界：

- 读缓存后、`state.update(saved)` 及同局迁移前，验证 `operators/relics/maps/resources/tactical_tools` 外层及被消费记录、history 非 list 和深层 nodes 等容器。新门槛只读 saved；发生不合格时走原 `ValueError → preserve_unreadable` 路径，不浅安装任何同文件兄弟数据，不损坏原文件或旧临时文件。
- 验证成员 fields / skill_ranks / sources / times、强化与状态列表，藏品 icon_evidence，历史图标 memory 及 candidates、库存 signature、node_contents / 最近内容，以及真实当前窗口消费的 config difficulty/squad/zone。未知未消费额外字段继续原样保留；空旧成员、缺省字典/列表、None 的合法可选字段、旧历史非有限 opaque 时间继续保留。已消费的资源时间需可格式化。未持有的未来未知藏品仍保留；当前窗口无法解释的未知在队干员或持有物品会保护原文件。
- `maps` 中匹配成功或当前 zone 选中的图，验证窗口直接索引的 template/grid/nodes/edges/source；未被消费的局部 opaque 图仍可保留。history 的未知/缺省 kind 用 `.get` 跳过，而非扩编任何迁移依据。对正常历史，该两行改动输出不变。
- incoming 库存 `count` 为 bool 时，仅在原局部副本中把 count 设为 None，不把 False/True 当作明确整数 0/1。保留原来的 stale/cross-run 早退、成员错误次序、正常非 bool 行为和调用方完整对象图。
- 真实 MainWindow 的 `current_operator_state` 使用 `member.get('fields', {})`，让被保留的合法空旧成员也能打开、选择与计算。只有这一行 UI 变更；它使用已存在的缺省账号参考/预览行为，不添加数值机制。

候选共运输 `rouge/run_state.py`、新 `tests/test_run_state_reliability.py`，另对当前 `rouge/app.py` 精确应用单行；Root 在实际第 97 节的 `scripts/verify_cloud.py` 注册 `test_run_state_reliability`。不要复制本包整份 app 到维护树，也不要复制旧候选的未来 097 registry。AccountCache 完全不在本组改动范围。

## 来源与保留范围

当前维护源 / 本包 baseline 是合同依据：RunState.__init__/restore_passed_node_types/restore_origin_discovery_buffs/reconcile_relic_icons/apply/summary；app.current_operator_state/sync_run_config/render_map；relic_counter_semantics.reusable_resources；map_view.set_map/_positions；map_reporting.format_map/format_node；operator_summary.format_operator_observation。没有新增游戏机制，无需从邻近技能或历史次数推导规则。

原 098 候选及 22 项独立源审阅位于 `/workspace/.continuation/p2-runstate-reliability098-candidate-source-v1` 与 `/workspace/.continuation/p2-runstate-reliability098-independent-source-review-v1`。原审阅明确只证明浅门槛、bool 副本及旧 17 个 Source 测试；本包六个新增方法和新 helper 尚需独审和 Root 实际运行，不继承过去 PASS。

保留原 17 个测试原文，新增 6 个有实际损坏 / 合法对照的测试方法：深层容器与非 list 历史保护；成员与未知已消费身份保护；合法 opaque 原始数据和保存重启；缺 kind 清空迁移；真实地图文本消费者的合法保存重启；坏缓存保护下本局内存继续可用、仅显式手动新局解除保护且不改另一临时局。

不声称完整 JSON / 数值 / 来源 schema 已认证：任意干员非法 elite、level、skill rank、member 时间等数值仍需另外按证据处理；合法缓存和真实窗口的实测范围要如实列出。RunState 的 save IO/Unicode、符号链接/特殊文件保护不在本候选改写范围，交由第 99 节独立功能组按实际完成 98 源适配。原生 Windows / 实际游戏 / OCR / 私人损坏发生率仍未验证。

## Root 验收建议

1. 对同一公开原 raw JSON 启动旧/新隔离实例，至少实际复现 history None/dict、nodes None、fields None、memory 缺 icons/candidates 的原异常/失败与候选保护，记录完整 raw，不以采集器 0 当产品 PASS。候选保护下 `.save()` 不改原文件/旧 tmp；正常 apply 仍在内存可用。
2. 执行新测试模块及 run_crew_count_boolean_input、inventory_tools、inventory_snapshot_051、inventory_catalog_053、empty_inventory、relic_grade_sync_032、origin_discovery_055、node_content、run_reuse_guards_032、run_config_validation 和 recipient/counter 范围，再跑精选回归。遇到故障保留具体异常，不以扩大 skip 替代修复。
3. 实际 Wine MainWindow 全程临时路径、离线采样/聊天禁用：坏 fields/history/memory 启动得到保护提示且窗口可见；坏原文件前正常本局 observation 可选 mechanist、显示 summary 和计算，原 raw 不变；通过真实 reset_run 路径显式新局，然后关闭/重启核对新局和另一临时 accounts/run 未受损。
4. 单独对合法空旧成员（known mechanist、缺 fields）、正常带 fields 成员、实际公开完整 map seed 做窗口启动、选择、run 培养勾选、summary/map/report/计算、close/restart。bool False/True 经 MainWindow.apply_run_observation 与相同原 raw 的 None 配对；明确 int 0/1 继续授权原库存移除，调用方 bool 与对象结构不变。保存实际窗口 PNG、实际报告、原始日志、退出码和源码前后哈希。不要把本文件作为已完成验收记录。
