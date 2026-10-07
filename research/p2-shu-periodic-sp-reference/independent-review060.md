# 第 60 节独立来源与公开 API 审查

结论：当前最窄 draft 无未解决 blocker。它撤销由原周期参数推导的均匀自然回技增量和完整资源时钟，保留已解锁天赋的静态攻击力及原有技能相对窗口，不补周期首跳、起点、重置或阻回规则。

审查只读 baseline、draft060 与当前公开来源；写入本外部审查目录，未改 root tracked 文件，未执行游戏、原生 Windows、Wine 或 GUI。冻结基线为 `4c5fdc528da191693b325c2569749e5264ed0a15`；最终接入分支及全量测试仍由根任务执行。

## 来源复查

- 当前 character_table.json 和 skill_table.json 原字节分别重新计算 SHA256，吻合来源回执中的 `68e3a3b5...8697`、`86f4aa64...38ca`，固定 game-data commit 为 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。
- 独立对照 `char_2025_shu.talents[1].candidates[0]`：精二 1 级、最低潜能 rank 0；黑板 `atk=.12, interval=4, sp=1` 及 HP/攻速参数和现有标准化条目相等。三技能全 30 rank 的费用、初始 SP、回复类型全部与原表相等，费用均为正值。
- 当前公开标准化黍模组没有 talentIndex 1 的覆盖候选；本修改不改变资格判断、模组门槛或能力附着。
- 独立重新计算 source-receipt060.json 列出的 177 个现存 native 文本证据文件哈希，全部相等。回执对黍身份/技能/天赋的精准搜索无命中。此范围仅限这些现存文件，不能证明安装文件/运行客户端中没有实现，更不能证明 XLua 等价。
- 已读 0.66 自然回技来源报告；其中正值自然属性的来源证明不适用于黍的离散周期天赋。没有把 4 秒/1 点参数当作 first tick、归属、reset 或阻回 credit 规则。

完整独立来源结果见 independent-source060.json。

## 控制流与未知边界

实际 code diff 只在 operator_engine.py 与 reporting.py。天赋仍使用原选择器和现有声明条件；`sp_extra += sp/interval` 被移除，保存命名明确的参数参考。

最终资源清理发生在现有自然、攻击、受击及事件 SP 分支之后、周期和普通充能段构建之前：初始 SP 足够时保留 0 秒就绪；其它初动、结束后充能未知，完整周期及其伤害/治疗派生值未知，不安排普通充能输出或四岁周期事件。独立来源旧算例只保存在 `independent_sp_clock_reference`，明确排除四岁周期来源。

S1 原友方获取、结束与多充能链未知保持；S2/S3 单次、技能相对窗口、组件和静态数字保持。敌方 target_windows=[] 或目标生命周期 0 不删除独立友方 SP 未知；0 秒观察窗口不产生观察输出。没有把部署初动未知扩展为删除已有技能阶段算术，也没有由 lockout 参数建立实际四岁 credit 时钟。退休 attack_sp/received_sp/event_sp 的规则和 reference 状态未被重新启用。

## 独立公开检查

independent_public060.py 在 baseline 和 draft060 分别执行 1,921 次公开 calculate_damage，总计 3,842 次（960 对场景加两包各一份格式化代表报告）：

- 720 对有效四岁天赋场景：全部 30 rank、两种 timing mode、六类时序和两组初始技力来源；时序覆盖默认、额外阻回与结束硬直、空供靶、数字/字符串零目标生命、移动及打断。
- 72 对精零/精一、不同等级及潜能、false/true/既有 truthy 声明的未解锁控制。
- 168 对其他干员技能的零窗口及零敌方生命控制。

720 对静态属性、攻击力、组件及全部原单次/技能阶段/观察窗口数字保持；240 个未解锁或其它技能控制的整份 JSON 保持。所有受影响实际资源/周期指标和已计小计的周期项 unknown，recharge_streams 空，自然回复速度精确移除 0.25，命名明确的独立 SP 算例与不含四岁声明的原计算相等。上层 report 时间指标与实际 skill 字段同步。

首次审查提取器错误要求 continuous timing 具有 frames 专属 initial_seconds 字段，产生 360 个 KeyError 记录；这些是提取器断言错误，公开调用本身全部完成。原 JSON/log 保存在 independent-draft060-initial-extractor-error.*；提取器改为仅核验存在字段，最终复跑与比较均无错误或差异。没有把该错误当作产品失败或隐藏原记录。

已指出并复核修正一处报告旧宣称：有效四岁场景不再显示「初动/回转已按模拟帧处理」，改为技能相对帧参考和完整 SP 初动/充能/回转未知。其它情景的原文字通过完整 JSON 控制保持。完整格式化代表报告、输入和摘要见 independent-baseline060.json、independent-draft060.json、independent-comparison060.json。

## 审查版本与后续限制

最终读取文件 SHA256：

- draft060/rouge/operator_engine.py：`8f91b8e2183d6ac15ec627ce2cf40424356a52be3ae39335300710c723fada26`
- draft060/rouge/reporting.py：`67e903f3853064d347bd36b7ad82d7ddb21d2101aad9d1148f8fcc8ea81f172b`

本结论覆盖这两份实际文件；root 最终接入如果有源码变化，应复核相应差异。四岁首次跳点、计时起点、reset、阻回期间归属、当前热更新及真实客户端尚无闭合证据，继续显式保留未知。独立审查不替代每五节的正式 Linux/Wine 全量和实际窗口验证。
