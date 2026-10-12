# 事件资格三态与固定作战入口

`rouge.event_planning` 使用事件原件DOM中的逐组、逐场景、逐选项关系；全部38组、190场景、233选项都与既有目录核对。保留的13个作战引用条目中有11个战斗图标选项与14个具名关卡页面链接。topic原件的396个choices没有battleInfo/stageID，NEXT的nextSceneId只能证明目标场景。

```powershell
.venv/Scripts/python.exe scripts/event_planning_cli.py events
.venv/Scripts/python.exe scripts/event_planning_cli.py battles --input event-input.json
```

接口：

- `qualified_events(context, include_indirect=True)` 将固定目录分为 `matched`、`unknown`、`excluded`，完整原行仍在 `rows`；不把同节点类型全集当当前资格已确定。
- `event_eligibility(event_id, context)` 返回逐项已知条件、失败条件、未知条件和未完全恢复的服务器资格。
- `choice_eligibility(event_id, scene_key, context)` 返回本场景全部选项的三态、特殊条件、原choices引用及未解析原文；描述/结果角色保留，不冒充可选。
- `event_battle_links(event_id, scene_key=None, choice_key=None, context=None)` 返回逐选项精确关卡页面链接。普通/紧急或事件/追猎同名ID保持候选，按原levelId分组。可预览候选用 `preview_stage_candidates`，明确紧急条件排除的普通引用单列于 `excluded_stage_candidates`。`actual_stage_id` 始终未知。

`context` 可声明 `node_type`、`floor`、`special_region`、`difficulty`、`entry_mode`（unknown/natural/content/processed_item）、`movement_item_id`、`gold`、`item_quantities`、`inventory_complete` 与 `event_history`。事件历史按目录事件ID保存 `encountered`、`visited`、`entered` 三种独立布尔或未知。看见事件不自动算访问/进入；不完整持有表中的缺项不算没有。

已证特殊检查：红苔要求先遭遇沉寂之屋；黑诞笼控器选项要求G12；传奇团伙爆胎严格要求源石锭大于50；回滚文明复原要求怦然信标；好奇心与死的修正选项被同时持有沙盘α/β或访问窥视箱中排除。自然出现安眠一隅被原文明令排除，文档支持小八界入口；未证明其他途径绝对不可能，所以不擅自排除未知入口。

`matched` 只表示**已列出的资料条件在声明输入中相符**；`actual_server_eligible=None`、`all_server_conditions_known=False` 始终保留。自然资格未恢复的目录事件即使层数/类型相符，仍处未知区。当前帧已确认的内容身份应由原node_dossier单独保留，不能因为旧目录范围矛盾而删掉实际已读内容。

固定解析源是事件页面revision427904及已固定game commit；2026-10-12额外直接读在线页面确认关键文字仍在。当前在线观察不是固定原件的替代。原件45场景/63选项未知入口、实际stage实例、普通无明确紧急文字时的难度选择、完整服务器资格与特殊区“下一层”规则仍未知。
