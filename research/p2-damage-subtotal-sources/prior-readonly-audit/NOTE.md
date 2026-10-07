# P2 section 055 后派生伤疗与报告来源只读审计

冻结公开代码：`15e0fa455aad05d27303428299d24d15db4c572c`。完整只读副本为 `frozen/`，逐文件 SHA256 为 `freeze-manifest.json`。本轮没有 tracked 编辑，没有操作游戏、读取私人状态或发送聊天。`reproduce.py` 使用 frozen 中的真实 `calculate_damage`、`format_estimate`，保存 10 项完整公共输入、结果和报告至 `public-results.json`。原公共来源缓存仅用于重新核验 SHA256 和定向选择三个已研究 selector。

本轮只确认一个新的报告来源误注候选；两个 Wine 公共反例命中同一分支。没有确认新的实际伤害/治疗数值缺口，不以未知原生首跳或生命周期补猜结果，不重做 048/049/052，亦不扩大 056 零生命周期或 057 bool 计数。

## 一个候选：未选河谷祭祈的神经未知来源小计仍归因于该藏品

公开输入 A：

```json
{"operator":"char_1042_phatm2","skill":1,"base_attack":1000,"relic_ids":[]}
```

结果只有 `neural_s1_reference`，不存在 `neural_relic_reference`，`relic_resolution.records` 没有河谷祭祈。`total_damage`、技能实际总伤、实际 recharge/cycle 均为 null，`known_damage_subtotals.total_damage/window_damage` 均为 3000。S1 束缚倍率首次附着/刷新尚未闭合是其真实未知来源。`known_damage_subtotals` 报告区仍显示：

> 这些数值不包含河谷祭祈未排程的额外持续伤害，不能当作完整总伤或完整 DPS。

公开输入 B：

```json
{"operator":"char_1042_phatm2","skill":2,"base_attack":1000,"enemy_attack_count":20,"relic_ids":[]}
```

结果只有 `neural_incoming_reference`，同样没有河谷来源。实际 `total_damage` 与窗口伤害均为 null；观察窗口已计法伤小计 24000（30 秒，DPS 小计 800）。S2 无限技能的 total/cycle subtotal 均 null；自然 recharge 原参数 25 保留。该未知来自目标普通攻击次数未提供事件时刻。小计报告区仍显示同一河谷注释。

定位：`frozen/rouge/reporting.py:692` 建立小计区，699–704 的注释判断已包含 S3、诱饵及多种其它未知来源，但遗漏 `neural_s1_reference` / `neural_incoming_reference`；最终 else 固定写河谷。其它机制报告区和 estimate.notes 已正确解释 S1 或堕梦未知来源，因此这不是 numeric aggregate 恢复成 actual 的缺口。

最窄后续方案：仅在小计区补 S1 / incoming 来源判断，或使最后默认提示不专指某个藏品；保留“已计小计”“不能当作完整输出”边界。S1 可说明小计仅保留原版动作参考下的法伤，不含束缚附着/刷新所影响的未知神经爆发；incoming 可说明小计不含缺少目标普通攻击事件时刻所影响的未知爆发。多未知来源可采用通用来源提示或并列原因，不改变现有数字、mask、元素调度、实际 clock、完整性或技能 scope。河谷名称只应由确有河谷来源的报告区/条件引入。

建议独立验证：两个 no-River 小计区不能出现河谷，S1 与 incoming 未知原因能被读者找到，actual null 和小计数值完全保留；S1/incoming 同时存在不遗漏未知；确实选 River 的原有机制说明保留；S3 无 River 与 incoming=0 的现有报告不回退。不借此引入新 damage/healing 数值模型。

## 已核来源与不支持的边界

先读取了已有 `research/p2-s1-binding/source-receipt.json`、`research/p2-incoming-clock/source-receipt.json`、medical Amiya phase、healing subtotal scaling、unbound cast 和相关元素报告/小计研究。随后重新核验固定 `Kengxxiao/ArknightsGameData` commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 原缓存：character 表 SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`、skill 表 SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca` 均匹配。定向 selector 和完整选中项见 `source-receipt.json`。

- `skill_table.skchr_phatm2_1.levels[9]` 支持两次 1.5 ATK 法伤、束缚 3 秒及束缚期间神经损伤 1.8 倍条件参数。
- `character_table.char_1042_phatm2.talents[0].candidates[PHASE_2,potentialRank=0]` 支持攻击附带 30% ATK 神经损伤参数，不能把法伤易伤重复用于原始积累。
- `character_table.char_1042_phatm2.talents[1].candidates[PHASE_2,potentialRank=0]` 支持范围内敌人普通攻击时受 70 神经损伤；次数不能证明时间戳。
- 复用 `.cache/research/phatm2-{s1-069,first-event-070,damage-070}` 公开迁入回执，S1 damage 相关三个文件哈希与既有 receipt 一致。只复用它们的原版相对动作/条件模板边界，没有重新读取或执行游戏二进制。

来源不支持当前 native 首附着/刷新/同帧顺序、当前 hotfix 等价、实际 burst count/timestamps、实际技能结束或 recharge/cycle。此次报告反例仅依赖已存在的 reference flags 和空藏品选择，与补齐这些 native 未知无关。

## 派生数字路径核过的具体范围

`operator_engine.py:1212` 的 damage-dependent healing 循环在父 damage 具有 `actual_total=None` 时使派生 healing 同样 pending，并保存已知父来源到 `known_healing_sources`。`uncertain_sources.py` 排除 pending 分项，只将已知来源列作小计；`relics.py:397` 单个已确认 healing_factor 同步 public aggregate、estimate、小计、healing 组件及 nested known sources。medical Amiya S2 + active Rose 本轮公开控制的 actual 总伤/治疗仍 null，opening damage 小计 2000，healing component 中 known sources、小计、opening healing reference 均 1200，未找到重复缩放或派生 actual 泄漏。

`elemental_relics.py` 在 incoming/binding/S3/诱饵叠加时复用第一个已经排除未知 burst 的小计；River 再处理附加未排程来源不会恢复实际总量。本轮 Wine S1/S2 River 组合和既有相关测试没有出现重复扣除/重建 actual 的新反例。这个结论限于当前公开可达搭配，不声称已经证明任意未来混合 damage/healing 来源。

Wine S1 的 magic damage_taken +100% 控制令法伤小计从 3000 变为 6000；`neural_s1_reference.direct_buildup_raw` 仍 300，actual 完整总伤仍 null。该项支持当前已知法伤倍率只计算一次的窄边界，不代表全环境或所有属性层已闭合。

Hsgma2 S2 + Rose 的 unplaced healing total 与 conditional reference 不全同不能直接判定 bug：既有 section 043 明确保留独立条件参考在最终受疗缩放之前，且当前 actual damage/healing 均 null、已计 subtotal 为 0（尚无可排程伤疗来源）；没有据此改变参考数字或推断盾接触时刻。

## 验证与复现

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/p2-after-055-audit/derived-report/reproduce.py
PYTHONDONTWRITEBYTECODE=1 /workspace/rougezhushou/.venv/bin/python /workspace/.continuation/p2-after-055-audit/derived-report/collect_source.py
```

10 项完整公共输出与上述断言通过。冻结副本的 6 组已有相关测试共 88 项通过，0 failure/error/skip；详见 `validation.json`。首次公共脚本将 Hsgma2 ID 误写 `char_1045_hsgma2`，纠正为原有 `char_1044_hsgma2` 后运行通过，没有改生产代码。再次检查原仓库 tracked 状态须保持干净；本轮结果不代表 Windows 原生/游戏/聊天验证。
