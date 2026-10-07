# 只读来源审计：术师阿米娅 S1 continuous 有限正敌生命周期/范围

本轮不修改 tracked 文件，不访问私人状态、游戏、桌面或聊天。仅在本目录保存审计资料。按 parent/root 后续收窄，只推荐一个普通 public 候选：`char_002_amiya` 的 S1；不扩大到 Gnosis48、Haruka49 或其它技能。

## 来源结论

已有证据**没有证明**此来源的 finite-positive continuous native clocks、首击/释放/命中相位或 owner range 获取/重获/停止事件。

- `research/p2-empty-enemy-scope/NOTE.md:17` 已核同一阿米娅身份、自然/攻击技力来源和独立部署初动；`:28` 明确 finite-positive disappearance 和非空 range 未实现，沿用 parameter reference；`:44` 将其列为未知。邻接 source-receipt 的 `existing_contracts.rouge/timing.py` 也记录 continuous floor duration 不咨询 selectable_lifetime。`:42` 的 522 个控制情景数值不变证明旧参数保留，**不证明** finite-positive native 生效。
- 本轮直接重读固定原表（commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`）并复核 SHA256，与上述 receipt 完全一致。`character_table.char_002_amiya.skills[0].skillId = skcom_magic_rage[3]`。`character_table.char_002_amiya.talents[0].candidates[1]` 是 E2、potentialRank0 的情绪吸收：攻击敌人回复2 SP、消灭敌人回复8 SP，黑板键为 `amiya_t_1[atk].sp` 与 `amiya_t_1[kill].sp`。不由攻击或目标离场推断击杀。
- `skill_table.skcom_magic_rage[3].levels[9]` 是 AS+90、名义 duration30、`INCREASE_WITH_TIME`、cost30、init15、increment1.0。这些是参数；记录没有实际首击、释放/命中、重置、获取/离场回调、结束/阻回或跨周期脚本。
- `rouge/data/timing-profiles.json:62` 的 Amiya 普攻提取值是 OnAttack19帧、总动画53帧、`binding_status:reference_only`。`original-animation-references.json` 的 Front/Back Attack 同样 `runtime_binding_verified:false`；顶层 scope 明确无 measured skill reset/projectile/multi-hit/phase/runtime selector binding。`research/p2-phase-guards/source-receipt.json` 也为 runtime false、fresh native false。它们不能把连续首击放到19帧、0秒或完整1.6秒，也不能证明此 S1 选择/重置这些动作。本云端未迁入旧 dps_anim 原件，本轮只复核已保存的提取记录，不声称重验动画二进制。

完整原表选择器、来源哈希、已有回执具体字段及6个实际 public 调用保存在 `source-receipt.json`。本轮定向搜索 existing research 与已迁入 native REPORT/proof/fields，未找到阿米娅 S1 continuous 绑定新证据；没有新线索，不重复既有网络失败路由。

## 当前实现与复现

`timing.py:232–259` 的 continuous 路径按 `floor((duration-ready)/interval)` 生成 `ready+(i+1)*interval`，只在 `target_disappears_seconds == 0` 清空。有限正值与 `target_windows` 没进入 selectable。这些**合成 interval timestamps** 虽已放入 `times_seconds`，仍只代表参数参考；不能仅凭该字段存在就当作明确 native/用户事件时刻。真正带来源/显式时刻的分项须保持自身 provenance 和已有边界，不能被本次 interval guard 全局覆盖。

`operator_engine.py:1270–1287` 的 caster mixed-SP continuous 单独按普通间隔循环，只有 life0 转自然参考；precast `first` 独立生成。`:1417–1426` 再把技能和普通充能伤害组成周期。`timing.py:389–391` continuous 提前返回使完整性/时钟说明未按 frames 的路径传播。

公开输入均为 `operator=char_002_amiya, skill=1, timing_mode=continuous, base_attack=1000, window_seconds=10`：

| timing | 窗口伤害 | cast/phase参数伤害 | 充能/周期参数秒 | 周期伤害参数 | complete |
| --- | ---: | ---: | --- | ---: | --- |
| 省略 | 11000 | 35000 | 14 / 44 | 43000 | true |
| life .1 | 11000 | 35000 | 14 / 44 | 43000 | true |
| life 1 | 11000 | 35000 | 14 / 44 | 43000 | true |
| range [[0,1]] | 11000 | 35000 | 14 / 44 | 43000 | true |
| life 0 | 0 | 0 | 30 / 60 | 0 | true |
| range [] | 11000 | 35000 | 14 / 44 | 43000 | true |

每项原 initial7、名义 duration30 均保持。`range []` 与 finite-positive range 应分开：前者明确定义全程没有该敌方获取来源，可做已知零边界；非空有限区间不能由其长度推出实际次数。`life0` 是已完成数学零源控制，不能作为 positive native lifecycle 证明。

## 窄护栏建议（未实施）

1. 限定 caster Amiya S1、continuous、enemy-facing interval 来源，且 explicit finite-positive lifetime 或明确 owner target-window 约束；其它 skills、friendly、instant、独立碰撞/显式时刻分项保持现有归属。默认无约束仍保留旧条件估算。本轮不证明有限正时钟，不做 `min(life,window)` 或按 range 长度剪 floor 次数。
2. 旧11/35次、每击1000、35000 cast、14/44 mixed-SP 等保留在明确 `parameter/reference` 对象；合成 interval `times_seconds` 改标 reference provenance，不能冒充 actual events。对正观察且 life>0 的来源，actual 次数/命中/窗口和完整伤害、实际 post-skill recharge/cycle/周期伤害/DPS 保持 unknown，`complete=false`。仅补 `notes` 而让 aggregate 保持11000/43000及 complete true 无法消除误报。可以复用 `actual_total=None` 的 pending aggregate 机制，但应从 full/shown/normal 三路一致传播。
3. 零观察、life0、该敌向来源 empty range 的已知零边界分别保留。**合成参考 hit0 不足以推出 actual0**：窗口短于 interval、life短或参考供靶未命中时，只要真实来源仍可能，仍需 unknown。现有 `preserve_unplaced_sources` 的 `possible and c['hits']>0` 条件不宜直接复用到此路径，它会把参考0误当实际0。
4. 独立自然回复 rate1、cost30/init15 和名义 duration30 保留参数；`30/rate` 可另列 natural-only 条件参考，不能以此替代 positive finite life 的实际 native recharge。旧 deployment initial7 是独立条件参数：本次 skill-relative 约束不自动改其 pre-cast 输入。治疗0等独立已知量无需全局 unknown；未知周期分母会使依赖它的 cycle HPS/DPS 未知。
5. 对应 public 验证应至少覆盖 life .1/1、非空 range、短正窗口参考hit0、zero观察/life0/empty range、无约束控制、initial7、自然SP原参和其它skills/friendly/explicit-event隔离。本轮6项为只读重现，不是新增测试，也未运行全量/Wine/真实UI。
