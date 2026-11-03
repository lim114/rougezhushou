# 第 63 节候选：只读公开数量 probe

所有调用从外部冻结包 `baseline/` 导入，冻结 HEAD 为 `c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf`。本辅助任务没有修改 tracked 文件、baseline 源码或实现代码，没有运行 Wine、GUI、游戏，也没有读取私人状态。原始机制闭合由同目录 `source-closure.json` / `NOTE-source.md` 提供，本 probe 不新增数量上界、回复 tick、实际在场数量或生命组合机制。

本次共 **538 次**公开 `calculate_damage` 调用：**514 次**原契约场景（主矩阵384、补充合法及既有错误76、inactive 54），**16 次**明确合成 HP 组合层未核验守卫，**8 次**无观察 wrapper 的原函数对照。**374 次返回、164 次抛异常**；异常和 report 前部分结果没有计为公开调用通过。主矩阵覆盖深海色 S1/S2、continuous/frames、精零/一/二、未装备及锁定/已解锁 SUM-Y、低/高技能 rank。精零 S2 的现有解锁错误保留，未被改成可以使用技能。

主矩阵有288对比较：192对均返回，其中44对整个结果相同，另外148对只存在报告数量原始类型显示差异；全部192对报告外结果相同。另72对是整数输入正常返回，而已经被模型接受的 `"0"` / `"1"` / `"1.0"` 在 S1 的原报告中抛 `TypeError: can't multiply sequence by non-int of type 'float'`；观察到的模型结果与整数调用完全相同。24对两边均有原解锁错误，明确记为 `both_rejected_not_a_pass`。264对已经抵达报告的模型结果完全相同。

总计78次观察到的报告 TypeError：主矩阵72、补充 `"0.0"` / `"1e0"` 4、合成 HP 守卫2。无 wrapper 重放还原2个原报告异常，另外12个 TypeError 来自 None/list/dict 的既有数值转换失败；其余72个 ValueError 属于现有解锁、有限非负整数及范围约束。S2成功的数字字符串仅影响 `summons.summon_count` / 已解锁模组面板 `model_count` 的显示类型，报告外伤害、时序、培养和属性等结果未变。不得把这类显示修正描述为改变实际触手数量。

冻结基线仍接受 raw bool 深海色数量为0/1；这只是 c3ccf25 的原契约观察，之后第61节布尔守卫不在本冻结包中，不建议重新放开。未启用该参数的 mechanist S1、桃金娘 S1、医疗阿米娅 S1，两模式共48个配对均与省略 `summon_count` 的全结果一致，包括 bool、字符串、负数、NaN 和分数；不应顺带把 inactive 输入改成新错误。

合成守卫通过 `unittest.mock.patch` 临时让现有 `rouge.summons.module_rules` 的 `hp_composition_verified=False`，同时明确声明普通 HP 加成和百分比回复藏品。这是既有未知保护合同，不代表当前原始 SUM-Y 生命叠加层未知。16个模型观察都保留 `hp=None`、依赖 HP 的 `regeneration_rate=None`、`hp_composition_pending=True` 和 `complete=False`；其中2个S1字符串调用仍在原报告失败，不能视为完整成功。成功的 S1 整数调用固定每只回复70，数量0/1/2显示合计0/70/140；未把它改成依赖未知 HP 的回复。

诊断 instrumentation 仅暂时观察 `build_report` 前现有 result 和内部 scenario 的深拷贝，之后**始终调用原 `build_report`**，未替换报告、未抑制异常、未写源码。8个对照以原函数无 wrapper 重放，返回全JSON或原异常类型/消息一致。原输入、cached catalog、cached module_rules、121个冻结 py/json 源码均在调用前后保持一致。非有限浮点输入在证据中使用明确标签，JSON使用 `allow_nan=False`；这些标签不作为数值验证成功的依据。

`public-outcomes.json` 保存每次真实输入、完整返回JSON或异常及traceback，以及报告前观察和配对差异。`SUMMARY.json` 保存数量、分类、输入/目录/源码守卫及两个完整 source hash inventory。外部重放入口：项目 `.venv/bin/python probe_count63.py`，只输出同目录审计文件。该脚本运行后重新补充的汇总统计及本说明为只读后处理，不属于实现补丁。
