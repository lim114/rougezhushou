# 第 60 节 · 黍「天有四时」周期技力原参数与未知时钟

当前来源证明的是「编队中有四名【岁】干员时所有干员攻击力 +12%，且 4 秒获得 1 点技力」。原计算把 1/4 直接加入 `sp_extra`，从而把黍自然回复速度显示为 1.25；默认 rank 10 的 S1/S2/S3 初动分别成为 3.2/4/12 秒，S2/S3 结束后充能成为 20/36 秒。原表不证明这个周期来源可当作均匀自然回复，也不证明首跳、计时起点、重置或阻回期间的处理。

## 来源与已知范围

固定原始 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。本次重新读取当前保留缓存并校验 SHA256：

- [character_table.json](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/character_table.json)：14,975,251 字节，`68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。
- [skill_table.json](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/skill_table.json)：11,447,929 字节，`86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。

精确 selector `character_table.char_2025_shu.talents[1].candidates[0]` 为 PHASE_2、等级 1、requiredPotentialRank 0、prefabKey `2`；原参数 `interval=4, sp=1, atk=0.12` 与现规范资料一致。三技能各 10 rank 的 SP 类型、费用和初始 SP 与原表逐项核验，共 30 个 selector。未将现有第一天赋的模组覆盖借给第二天赋，也没有从 potential 推导更快的周期。

本次逐个重哈希当前 `.cache/research` 的 177 个文本回执/CFG/研究文档，以 `char_2025_shu`, `skchr_shu`, `shu_t_`, `天有四时` 精确检索，没有匹配的实际天赋时钟绑定。此搜索只描述当前保留文件，不能证明完整安装文件不存在相关脚本，更不能证明运行中的热更新。旧 0.66 报告只证明五个已命名正自然回复来源的加算与职业/领取者筛选，不能扩展为黍周期天赋的平均化。逐字段原表摘要、当前缓存哈希和搜索范围见 `source-receipt060.json`，复现脚本 `source_audit060.py`。

## 修改边界

只修改 `operator_engine.py` 与报告，并增加一个公开回归模块；没有更改资料数值或其他干员的周期来源。

- 保留现资格判断与声明的四岁编队条件，不自动读取或猜测编队成员。E0/E1 无原第二天赋时不新增参考；False 或其他干员不生效。
- 保留四岁攻击力 +12%，三职业生命加成、三同职业攻速加成、模组门槛和 potential 的既有数学值。
- 周期 `4 秒 / 1 点` 单列 `shu_periodic_sp_reference`，首跳、实际 tick 列表、时钟起点、重置、阻回归属均为未知；没有排程事件，也没有借用 Wine 的部署相位。
- 已计自然回复速度只包含原有自然来源，不再加 0.25。其余来源单独计算的充能值仅留在带 `excludes_four_sui_periodic_credit=True` 的条件参考中，不作为含四岁来源的完整资源时钟。
- 在所有原有 SP 计算之后、周期与普通攻击充能期构建之前收窄初动和结束后充能。初始 SP 已满足费用时保留 0 秒；仍需充能时初动未知。充能、完整周期、周期伤害/治疗与 DPS/HPS 未知，也不生成依赖该充能期的普通攻击流。
- S2/S3 技能相对窗口、单次与阶段数学量、静态面板和组件保留；S1 既有友方获取/治疗结束未知边界保留。部署后初动未知不会删除这些既有技能相对算例。
- 零观察窗口仍没有实际输出。当前敌人零生命周期或空敌方供靶不会取消独立友方 SP 来源，也不会证明其实际时钟。
- 当前局外范围已将 `attack_sp`, `received_sp`, `event_sp` 战斗触发来源退休为资料；控制用例保留这些引用/职业不适用状态，没有重新启用回调或伪造它们的执行。
- 报告增加「天有四时 · 周期技力待核验」；仅受影响报告把原「初动/回转已按模拟帧处理」旧句替换为完整资源时钟未知。scope 与 scenario_scope 同步。

## 验证与交接

原冻结 baseline commit `4c5fdc528da191693b325c2569749e5264ed0a15` 的 2,167 个公开文件逐一校验未变；原 engine/report/catalog 在开始时与 root 56 一致。没有将共享 root 的后来 WIP 混入基线。新测试覆盖资格、potential/模组、静态加成、技能相对阶段、初满/不满、零窗口、敌方缺失、独立自然来源与退休回调引用、报告和请求/资料隔离。

- 13 个新测试通过。
- 76 个相关测试通过，0 失败/错误；另 2 个原生成器测试因 `.cache/game-data/roguelike_topic_table.json` 缺失明确列为 unavailable，不伪造缓存或计作通过。
- 3,060 个场景在 baseline/draft 分别调用公开 API，共 6,120 次。最终 0 计算错误、0 提取错误；354 个 False/非黍/未解锁控制完整 JSON 哈希一致；2,706 个已解锁四岁用例只改变资源时钟/边界文字，原静态、组件、单次、技能相对阶段与窗口数值均相同。矩阵包含 3 技能、两种时序、rank 1/7/10、6 种培养、5 种窗口/敌方情景及 5 种独立来源组合。
- 原基线定向红测 1 个方法的 6 个子场景如实失败：旧初动仍是确定数值。这是缺陷证据，不计通过或开发重复尝试。
- root `4543b9b91ac7b61fc019bb96a3d6d5ac2593a6bc` 上 `git apply --check` 通过。补丁未包含旧的精选 runner 注册 hunk；root 集成时需加入 `test_shu_periodic_sp_reference`。
- 独立审阅通过，0 未解决 blocker：另有 960 paired scenarios / 3,842 public calls，含 720 qualified、72 未解锁与 168 其他技能控制，240 控制完整 JSON 相同；全 30 rank、阻回/硬直、空敌、数字/字符串零生命周期与移动/打断边界通过。报告旧句修正已复查。详情和源码哈希见 `independent-review060.md`、`independent-comparison060.json`、`independent-handoff060.json`。
- Wine/实际窗口验收由 root 后续明确回执记录；上述 Python API 矩阵不冒充 Windows GUI 或真实游戏验证。

保留初版诊断日志：第一轮新测错误地把已退休的战斗来源当成 active；第二轮将近卫专用 attack SP 误期望为黍的 reference_only，实际是职业不适用；第三轮按既有范围更正后通过。矩阵首版提取器把 legacy 缺少 `components/total_healing` 当成 KeyError，并错误地假设持有 +18 初始 SP 在所有 rank 都足够；最终改为正确字段能力检查和原初始就绪条件后重跑，最终没有错误。独立审阅发现的旧报告时钟句已定向修正。这些日志不算最终验收。

仍未完成：实际黍第二天赋脚本附着、首跳与计时起点、重置、阻回接收/丢弃/积存顺序、当前客户端热更新等价性。这些缺口不会以局外数学算例补全。P2 不因此宣称完成。
