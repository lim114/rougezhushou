# v1 补充：真实地图消费者

此补充不改已提交给 Root 的 review.json 原字节。绑定同一 v1 run_state 候选 `799b5ce95e679d5c4e1c6c620ca8fa40c44f56073877e0e228ddb69cea7f21da`。以下均为源码直接消费判断，作者没有执行项目或制造实际异常回执。Root/98 作者已经收到具体消息，修订应 fresh v2 后独审。

- 完整 selected/matched map 的 grid.rows=3、node.row=3 可经过 v1 整数 gate；`map_reporting.location` 的三元 tuple 对 row 直接索引越界。需要实际零起点网格数组消费边界和合法对照，不能只说“row 是 int”。
- 非空 prediction 没有 candidates：v1 sequence 缺省 []，而 `format_map` 对非空 prediction 直接 `prediction['candidates']`。缺字段与 None 条件不可混称同一行为。
- `graph.limitations=None`：`format_map` 有 `*graph.get('limitations',[])`，外层 graph mapping 资格未保护这条真实迭代路线。
- `generation_budget` 在 `format_map` 真值分支需要 `.items()`；条目直接索引 known_total/fixed/source_max/random_eligible，`format_node` 还消费 revealed_additional。generation_limitations 被 extend；真值 constraint_conflicts 被 join。候选应按真实消费条件验证容器/必需字段，并保留原安全的 falsy/None 对照，避免变成任意全值 schema。

不是每个 node scene_candidates=None 都会旧异常：`format_node` 的真假分支会跳过某些 None；`last_node_content` 为 kind=event 时 `render_map` 使用 len(scene_candidates) 才有明确消费。所有归档运行描述必须以 Root 实际日志为准。

仍然没有为本节添加游戏机制、概率或计算规则。以上不扩展为“任意 JSON 损坏都已穷举”的承诺。
