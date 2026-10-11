# 离线零件与探索规划

使用固定公开原件与声明地图，不读取或修改私人本局。加工品范围候选不等于游戏可进入状态；次数、行动力、住民、迷雾及当前资格仍需真实依据。

```powershell
.venv/Scripts/python.exe scripts/exploration_planning_cli.py items
.venv/Scripts/python.exe scripts/exploration_planning_cli.py targets --input exploration-input.json
```

`targets` 输入 `graph`、`item_id`，可选 `start`、`remaining_uses`。节点需要唯一 `id`、从0计的 `row`/`col`；起点来自明确声明或 `graph.current_node`。`node_type_raw` 或 `base_node_type` 使用原表类型，界面名称可用 `observed_type`。模板或历史名称不自动视为当前类型。

`EVENTS`/`BATTLES` 内部成员关系不在本原件中，缺证时保留全部范围候选并输出未知；可显式声明 `scrap_category` 为 `EVENTS`、`BATTLES`、`EMPTY`。该声明不会被标为实机核验。加工品直达不借用路径长度；随机加工品保留全部候选且不选择终点、不输出概率。同格再进入单列未知。

`effects` 在 `targets` 条件之外增加 `target` 和可选的 `passive_items` 持有声明。每项概念体使用 `item_id` 和可选 `remaining_activations`；缺少次数时不认定可触发。结果逐项显示加工品的希望/锭/AP具名增量及6概念体的节点条件、次数条件、效果描述。攻速保留为战斗资料，不接入战斗数值；随机收藏品仅列数量，完整池未知。条件不符或未知不会当作已领取收益，重复同类概念体叠加不猜。

`zones` 列原件26个区域ID，各自目标和耗尽提示；同名秘境不合并。`budget` 输入 `zone_id`、可选 `action_points` 与 `goal_completed`；以 `walking_steps` 或 `item_id` 选择一种移动成本。分别显示付款后小计、移动奖励后小计及到零边界。首领目标需要胜利，抵达本身不算完成；主层追猎、特殊区返回明确分开。缺AP不做可负担判断，退款不自动用来支付前置成本，到零与奖励/出口的执行顺序仍未知。

`valuation` 输入自然物 `item_id`、可选 `initial_estimate` 及 `events` 账本。事件 `kind` 支持 `battle_completed`、`node_revealed`、`operator_recruited`、`movement_completed`、`parts_obtained`、`item_obtained`；`count` 是声明的独立触发次数，默认1。作战可声明 `perfect`。分别显示已证估价增量、未知变化、完美/损坏分支和已损坏后的不再触发。多生苔藓的3个枯苔藓球列具名数量，派生触发顺序不自动补入。上下限和售卖修正缺证，算术小计可为负数但实际售价始终未知。

`options` 输入 `graph`、`target`、可选 `action_points`、`inventory`、`passive_items`、`start` 和 `include_walking`。库存每项使用 `item_id`、可选 `remaining_uses` 和独立 `instance_id`。步行使用声明 `edges`，区分纯拓扑、没有已知阻碍及所有中途条件已声明清楚的最短路线。节点可声明 `completed_declared`、`occupied_declared`、`other_blocked_declared`，均为布尔或未知。未完成/占领中途节点可阻断步行，加工品仍按直达范围比较。最低基础AP成本只比较保留的候选，未把未知库存/随机传送当保证，也不评价未证完整收益；原地再进入基础参考1AP而非免费。

`itinerary` 输入同样的声明图、库存/AP/概念体和 `steps`。每一步使用 `mode`（`walking` 或库存 `instance_id`）、`target`。独立账本扣减加工品次数；一次性概念体已满足条件后参考次数归零，不重复发放。未知资格/次数、随机落点或AP不足会停止依赖链，后续步骤原样保留为未求值。付款到零与AP未知使完整条件链未知；源规则算术账本不证明实际连续探索，节点完成和住民移动不会擅自模拟。

源版本：`Kengxxiao/ArknightsGameData@a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，完整原件哈希和精确字段在 `research/p3-exploration-planning/source-receipt.json` 与结果中。步行规则复用已核对PRTS页面与 `.cache/research/routes-049/evidence.json`；本次未冒充服务器重新验证。仅提取小范围事实参数；未声称上游许可证已核实。
