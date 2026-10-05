# 0.70 酒神 S1 接入的有界只读审查

审查范围：`rouge/multi_melee.py`、`operator_engine.py` 的 S1/未知生命周期处理、`reporting.py` 新参考段落和 `tests/test_multi_melee_070.py`。没有修改生产代码；功能探针使用纯计算输入，禁用 bytecode 写入，无私人状态或应用启动。仅运行新增 13 个测试，全部通过，没有运行整套测试。

## 实质问题

### P2：施法启动后的显式打断/移动窗口被静默忽略

`multi_melee.py:59–77` 仅在寻找 start 时检查 `timeline.unavailable(start)`。确定 start 后无论 `movement_windows` 或 `interrupt_windows` 是否跨过前摇、首段或第二段，都照常产生两个释放时刻，只检查目标存活。此前通用 `AttackTimeline.attacks` 至少在前摇内检查 cut；新专门路径绕过该语义。

可复现纯计算输入：

`calculate_damage({'operator':'char_1042_phatm2','skill':1,'base_attack':1000,'timing':{'interrupt_windows':[[.3,.8]]}})`

和 `interrupt_windows=[[.7,1]]` 均返回 `.5/.9 秒` 两段及参考总伤 9000，与没有打断的结果相同；`movement_windows=[[.3,.8]]` 也相同。前一种输入在明确的 unavailable 区间中仍展示命中。

这不是目标“离开射程”与“消失”的区别，不能用锁定目标规则排除。现有证据没有证明酒神各类打断的取消、补发或重开时机；建议保守地拒绝/标未知与参考施放重叠的显式阻断情景，并说明缺的是对应生命周期证据，不沿用相邻普攻的重开规则。不要静默保留无阻断数值。新增测试尚未覆盖启动后的阻断。

## 输出标称的小问题

- `reporting.py:302` 对自动回退采用原版 Skill_1 的情形也写“明确选用原版动画参考”。自动选择不是用户明确选择；可依 `automatic_original_reference` 改为“自动采用原版参考”，显式选择时保留原文。
- `reporting.py:294–295` 的“窗口首个出手/命中”数值来自尚未验证当前首伤相位的资源参考。专门段落与“战斗时序参考”标题已有清晰边界，所以不是阻塞问题；指标名称加“参考”可避免单独查看该数值时误读。
- `animation_reference.choices` 允许显式为 S1 选择 Attack_1/Attack_2，而专门段落始终陈述原版技能 Skill_1 对应关系。当前酒神三种动作恰好都是 15/48，故没有数值差异；如保留普通攻击动作选择，需要将其标为用户替代参考，不能暗示该选择也是实际 S1 prefab 绑定。

## 已核对且没有发现错误的范围

- `relative_wait` 按 float32 的 interval、animation duration、除法及 triggerDelta 乘法计算，动画比例限制 0.1–1，段间除以 float32 1/30、最近偶数取整并至少 1 帧。没有再用 cadence 取整后的周期推算比例，没有额外给每段统一 +1。
- 原始 prefab `_timeMode=FROM_ATTACK_SPEED` 的原生来源与代码传入的未取整攻击周期方向一致。应用计算值属于原版局外参考，不是复刻当前全部 FP/热更新执行状态；`exact_binding`、实际首伤/结束/阻回/普攻恢复标志保持 false。
- `duration_seconds`、`recharge_seconds`、`cycle_seconds`、phase/cycle damage 和 cycle DPS 均保留 None；没有拿资源动画尾帧或第二段 +1 当实际技能结束。
- 两段法伤与附带神经损伤共用时刻；窗口采用左闭右开；单次技能总量与观察窗口总量分开。实测 `.5/.51/.9/.91` 秒边界和既有新测试一致。
- 离开供靶范围不会换第二段目标，目标消失会取消对该目标的后续伤害。代码没有从其他目标中重选一个替代目标。
- continuous 模式也保持生命周期未知；新增 13 个测试通过。

静态研究的条件分支与 current_hotfix、实际皮肤、BakeMuzzle、additionalFrame 等边界仍以本目录 `REPORT.md` / `proof.json` 为准；此审查没有把这些未知补成事实。

## 修复复核

已轻量复核主代理的后续生产改动：

- `wine_s1` 在确定参考施放区间后，检查与显式 movement/interrupt 的重叠并抛出“机制尚未核验”，不会再静默返回无阻断两段结果，也没有猜取消、补发或重新施放。`provisional_end` 是保守拒绝情景的边界，没有填入实际 duration、阻回或周期。
- 原版参考的自动采用与手动选择分别标称；首个释放/命中改为“原版锚点”；手动普通攻击动作另说明仅预览，不声明为实际 S1 绑定。
- 初始技力充足时初动为 0；初始技力不足的默认情景保留 None，没有继承 continuous 模式中的旧 1.6 秒普攻槽作为首次施放。实际完整 duration/recharge/cycle 仍保持未知。
- 新增打断/移动交叉场景与初始技力不足断言已覆盖以上问题。仅执行当前 `tests.test_multi_melee_070` 的 15 项测试，全部通过（0.365 秒）；没有运行整套测试、启动应用或增加机制研究。

上述 P2 与三个标称问题已得到处理。本次复核未发现需要主代理继续修改的实质问题；实际相位与当前热更新等研究边界仍不算完成。
