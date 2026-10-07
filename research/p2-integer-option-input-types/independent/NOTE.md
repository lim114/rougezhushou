# 第 61 节候选：独立只读整数参数调用与 UI 来源审计

审阅边界为持久冻结 `4543b9b91ac7b61fc019bb96a3d6d5ac2593a6bc`（HEAD58）的 121 个公开文件。逐文件重新校验 manifest 后无漂移。没有读取活动本局/私人数据、操作游戏、修改 tracked 文件或作者副本，也没有创建 patch。此审计没有重跑主审计公开矩阵，没有启动 Qt/Wine，不代表原生 Windows 或实际窗口验证。

独立 AST 核出 `Combat.option(..., integer=True)` 共 28 个调用点、27 个唯一字段；`casts_used` 在 `calculate` 内查询两次。排除第 54 节的 `healing_targets`、`amiya_hit_targets`、`stolen_enemy_count` 后，余 24 个唯一字段。它们在 `OPTIONS` 中对应 25 条整数默认值控件记录，差异来自两个干员共用 `drone_warmup_hits`。实际 app 源码先判断 `bool` 建 `QCheckBox`，再判断 `int` 建 `QSpinBox`，并按实际控件类型发送 `.isChecked()` 或 `.value()`。所有余 24 字段均走真实 `QSpinBox` 构建分支；23 条真实 bool-default checkbox 记录没有任何字段与全部 27 个 integer=True 调用字段相交。这里证明的是已有构建和转交源码，未假称已实例化窗口。

主审计 `type-audit-summary.json` 只作为已经执行的公开 trace 证据读取，未重复执行：23 个字段确有 192 次被查询且原始 bool 被接受；`enemy_weight` 的 12 个 bool 控制已在 `enemy_environment.resolve_enemy` 上游拒绝，未到 option。因此准确范围是 **24 个余下整数契约字段，其中 23 个新 bool 缺陷，1 个已有上游 guard**，不能写成 24 个新缺陷。上游的数值/字符串拒绝与显式敌人覆盖边界仍须保留。

| 字段 | 冻结源码中的查询边界 |
| --- | --- |
| summon_count | Deepcl S1/S2，技能与普通阶段 plan |
| slash_kills | Chen3 S2，非普通阶段 |
| amiya_slash_kills | 战术阿米娅 S2，非普通阶段 |
| incoming_hits | Hsgma2 S1，非普通阶段 |
| shield_contact_ticks | Hsgma2 S2，非普通阶段 |
| cold_state | Gnosis S1/S2/S3，技能与普通阶段 |
| bubble_bursts | Haruka S1/S2/S3，非普通阶段 |
| levitate_triggers | Haruka S3，非普通阶段 |
| snow_entries | Sbell2 S1/S2/S3，三元表达式仅非普通阶段才调用 |
| drone_warmup_hits | Cammou S1/S2 与 Whitw2 S1/S2/S3，技能与普通阶段 |
| note_count | Oblvns S1/S2/S3，技能与普通阶段 |
| enemy_weight | Aglna2 S1/S2/S3，技能与普通阶段；上游已有原始 bool 拒绝 |
| bait_triggers | Phatm2 S2，非普通阶段 |
| enemy_attack_count | Phatm2 S1/S2/S3，非普通阶段 |
| palsy_overflow_hits | Mantra S3，非普通阶段 |
| palsy_triggers | Mantra S1/S2/S3，非普通阶段 |
| connected_stones / trap_triggers | Wang S1/S2/S3，非普通阶段 |
| trap_dot_ticks | Wang S1，非普通阶段 |
| dragon_arrow_hits | Orchd2 S3，非普通阶段 |
| ghost_count | Wisdel S1/S2/S3，技能与普通阶段 |
| ghost_casts | Wisdel S1/S2/S3，但只有已经查询的 ghost_count 非零才继续查询 |
| dash_hits | Yato2 S3，非普通阶段 |
| casts_used | Susuro S2，calculate 中两次按 operator/skill 短路查询，分别限制本次开启与后续回转 |

最窄可审查修正位置是 `Combat.option` 中调用现有 float 转换之前：只有 `integer=True`、字段属于明确的余下字段集合、且原始值 `isinstance(raw, bool)` 时拒绝；其它值仍交给原 `value` 处理。可以保留 24 字段契约表并说明 `enemy_weight` 在公开入口已被守卫，或仅列 23 个新缺陷字段。此处没有任何新的事件次数、上限、技能时刻或叠层模型。

关键风险是 `healing_targets`：`plan` 在所有 extended 干员上都无条件读取它，即便 `has_healing` 为假。第 54 节特意只在活跃治疗能力上拒绝 bool。把本次 guard 扩为所有 integer=True 参数会改变这些旧 inactive 行为，故这三个第 54 节字段必须显式留在原 guard 边界。也不能在 scenario 全局或按 UI 可见技能预先验证字段；否则其它干员、其它技能、`ghost_count=0` 时未查询的 `ghost_casts` 都会改变。应沿用实际调用点而非猜新的 active 范围。

既有整数、浮点整数、字符串、缺省、范围及错误必须保持，包括主审计发现的旧 `summon_count` 字符串 TypeError 与 `enemy_weight` 字符串拒绝。整数默认但没有 integer=True 调用的 `initial_neural_buildup`、`closure_prior_casts` 等不在此次范围。真实 checkbox、非整数 option 参数也不属于此候选。

已有 target-count、incoming-clock、Wisdel ghost、Haruka healing、environment/lifecycle 来源回执已只读查看并记录文件 hash。这些回执只用于保留已研究参数与未知边界；历史 `/tmp` 原文件没有重新获取或假称重新哈希。主审计负责当前缓存原表的 closure。对独立召唤物时钟、首次附着、接触、随机性、覆盖/叠层、native 生命周期和热更新等未知，本候选没有补充结论。

完整字段、AST 条件路径、UI 默认值/技能范围、源码 hash、复用主 trace hash 与候选风险见 `receipt.json`；可复核脚本为 `source_audit.py`。结论是来源与最窄修正范围可供审查，尚未实现或验证修正。
