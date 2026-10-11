# 离线零件与探索规划

使用固定公开原件与声明地图，不读取或修改私人本局。加工品范围候选不等于游戏可进入状态；次数、行动力、住民、迷雾及当前资格仍需真实依据。

```powershell
.venv/Scripts/python.exe scripts/exploration_planning_cli.py items
.venv/Scripts/python.exe scripts/exploration_planning_cli.py targets --input exploration-input.json
```

`targets` 输入 `graph`、`item_id`，可选 `start`、`remaining_uses`。节点需要唯一 `id`、从0计的 `row`/`col`；起点来自明确声明或 `graph.current_node`。`node_type_raw` 或 `base_node_type` 使用原表类型，界面名称可用 `observed_type`。模板或历史名称不自动视为当前类型。

`EVENTS`/`BATTLES` 内部成员关系不在本原件中，缺证时保留全部范围候选并输出未知；可显式声明 `scrap_category` 为 `EVENTS`、`BATTLES`、`EMPTY`。该声明不会被标为实机核验。加工品直达不借用路径长度；随机加工品保留全部候选且不选择终点、不输出概率。同格再进入单列未知。

源版本：`Kengxxiao/ArknightsGameData@a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，完整原件哈希和精确字段在 `research/p3-exploration-planning/source-receipt.json` 与结果中。仅提取小范围事实参数；未声称上游许可证已核实。
