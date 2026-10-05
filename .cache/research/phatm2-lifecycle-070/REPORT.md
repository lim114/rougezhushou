# 酒神 S1：原生结束、阻回解除与普通攻击冷却交接

本调查只读安装原件与此前固定证据，全部新输出位于本目录。没有执行游戏 DLL、读取进程内存、操作游戏、访问私人状态、发送聊天、启动程序或修改生产源码。结论限定为**已固定原版配置与原生默认分支**；XLua 分支在这些方法中真实存在，不能声称当前运行的热更新必然一致。

## 证据与复现

- 安装原件：`D:/Hypergryph Launcher/games/Arknights/GameAssembly.dll`，SHA-256 `6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`。
- metadata：同安装目录 `Arknights_Data/il2cpp_data/Metadata/global-metadata.dat`，SHA-256 `ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。
- 实际技能配置复用 `../phatm2-s1-069/skill-prefabs.json`：基包 `26-08-16-14-00-43_415873` 的 `skchr_phatm2_1.prefab`，来源 `battle/prefabs/[uc]skills.ab`，SHA-256 `696ab9409c73c9ad0ddafdc610b4bf792fdccde9a7e2a3e95702147818ef8796`。S1 skill component `-7067969616294705369`，攻击 component `1442620349020702503`（MultiMeleeAttack）。同级原数据固定版本 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。
- 原生虚表与字段偏移由 `read_metadata.py` 从原文件解出，保存在 `lifecycle-metadata.json`；不是根据类名猜测继承。
- 新增 87 个完整 CFG、8,509 条指令，逐条使用 physical offset 比对安装 DLL 字节，全部匹配。`proof.json` 记录各方法地址、可达字节散列及复用材料散列。完整 CFG 无截断或遍历限额。
- 本次进行了定向资料查询（酒神 S1 阻回、ReplacementSkill earlySkillFinish/useEscapeTime）；[PRTS 酒神页面](https://prts.wiki/w/Tragodia) 能支持技能基础描述，不能证明本报告的回调与帧调度，故精确生命周期结论均以原件静态证据为准。

复现（在项目根目录运行，仅写本研究目录）：

```powershell
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe .cache/research/phatm2-lifecycle-070/read_evidence.py --extract
```

不加 `--extract` 仍会重读原件 metadata 并逐条校验全部 CFG 指令。脚本只使用纯文件读取、解析和反汇编，不加载游戏代码。首次完整重提取核对通过 86 个方法；随后新增 SetRemainingTime 的 26 条指令已单独重提取，并再次验证最终 87 个方法。

## 实际配置与作用

1. `_allowSpRecoveryWhenAffecting=0`：BasicSkill 的 recoverSpWhenAffecting 为假，`get_abnormalFlagMask` 返回 SP_RECOVER_STOPPED 对应位；OnCastSucceed 注册阻回 modifier，UpdateSpRecovery 按 isAffecting 更新注册。它不是规定一个任意的固定阻回秒数。
2. `_earlySkillFinishAtAttackFinished=0`：OnSkillStart 不订阅 Entity 的 `ON_ATTACK_FINISHED_EVENT` 来提前结束技能。末段后 `_DoCast` 发送的是 AbilityStandard 的 `ON_SPELL_END=5`，不能把它当作 `ON_ATTACK_FINISH=6` 或 Entity 的攻击完成事件。
3. `_useEscapeTime=0`：BasicSkill.get_escapeTime 返回 FP0；攻击能力本身 `_escapeTime=0`。这是实际原版配置中的逃逸等待设置，不证明首段起点为 0。
4. 攻击 component `_resetCdStrategy=1` 对应 EasyToStartAbility 的 **HALF_FRAME**；`_minPostDelay=0`。重置还受下面的原生判断保护，不是无条件清零所有计时器。

上述分别可查 `lifecycle-cfg.json`、`events-cfg.json`、`start-escape-cfg.json`、`lifecycle-metadata.json`；脚本断言实际 prefab 三个 flags 均为 0、reset strategy 为 1、min post delay 为 0。

## 末段至正常结束：不能直接写 max(周期, 末段)

复用 0.69 已闭合的段间等待，不重复推导首段动画绑定。实际 `_DoCast` 在末段后调用 OnWaitForPostDelay，外层状态 3 恢复后调用 `FinishIfNot(NORMAL_EXIT, false)`。

- `EasyToStartAbility.get_postDelay(0x180ed3e20)` 计算 `max(0, m_cachedDuration - (fixedPlayTime - m_realStartTime))`；MultiMeleeAttack 与实际 `_minPostDelay=0` 取最大值。
- `EasyToStartAbility.OnWaitForPostDelay(0x180ed3750)` 的嵌套 iterator 使用 **FP** 版本 `AsyncUtil.WaitForFixedSeconds(0x180615a50)`。
- 对应 FP iterator `MoveNext(0x18066e260)` 请求 `max(1, MathUtil.RoundToInt(postDelay / FP(floatDeltaPlayTime)))` 次固定等待。`RoundToInt(0x1862fd1e0) → FP.Round(0x186313800)` 是最近整数、正好半值取偶数。等待计数器每次恢复加 1。
- 因此 **postDelay=0 仍请求至少 1 次固定等待**；完整持续不能未经量化直接设为 `max(cachedDuration, lastHit)`，也不能在上式外再随意添加一帧。

这里闭合的是“末段之后请求多少次固定等待”的原生算法。若缺少首段绑定，不能从它构造绝对完整持续；若尚未核验嵌套协程驱动时序，不能把请求次数直接冒充游戏可观察结束帧。攻击死亡、被打断等分支也不适用此正常路径。

## FinishIfNot 的实际顺序

`Ability.FinishIfNot(0x1805e9020)` 中，正常未完成能力按以下顺序执行：

1. 保存一次性 finish callback；调用虚表 slot 43 的 CleanupForNextCast（`0x1805e90ef`）。实际 MultiMeleeAttack 继承 AbilityStandard.CleanupForNextCast；base cleanup 清掉 isCasting 和一次性 callback。
2. 调用 slot 53 的 OnCastEnd（`0x1805e9118`）。实际 override 链是 **MultiMeleeAttack.OnCastEnd(0x180e912a0) → AbstractBasicAttack.OnCastEnd(0x180e7b8d0) → AbstractAnimatedAbility.OnCastEnd(0x180ec7dc0) → EasyToStartAbility.OnCastEnd(0x180ed3620)**。不能跳过 MultiMeleeAttack 自己的 override。
3. 普通 NORMAL_EXIT 且 resetReady=false 的 UpdateCooldownWhenFinish 不作 target-dead/resetReady 分支重置。
4. 调用常驻 finish callback（`0x1805e91db`），实际 BasicSkill.AssignData 绑定的是 skill.OnCastFinish；ReplacementSkillFixed 的实际 slot 79 指向 ReplacementSkill.OnCastFinish，其正常分支调用 BasicSkill.OnCastFinish。isAffecting 已清后调用 OnSkillEnd。
5. 最后调用已保存的一次性 finish callback（`0x1805e91fe`），来自 Character AttackState._StartAttack，进入 `_StartAttack>b__5_0`。

证据：`outer-cfg.json`、`cast-end-chain-cfg.json`、`basic-cast-end-cfg.json`、`attack-state-cfg.json`、`attack-callback-cfg.json`，虚表及参数用 `lifecycle-metadata.json` 复核。

## 冷却交接：复制结束后的 S1 remaining，不是技能前旧普攻剩余值

EasyToStartAbility.OnCastEnd 先执行 base end，再 `_CheckNeedResetCooldown(0x180ed3a00)`。真实策略 HALF_FRAME 路径要求：

- `MathUtil.Equals(m_cachedDuration, virtual get_cooldown())` 为真（`0x1862fb2d0`，有原生精度阈值，不要替换成毫无说明的任意近似）。
- `MathUtil.IsInHalfFrame(ability.remainingTime)` 为真（`0x1862fbdd0` 使用 MathUtil 的固定 HALF_FRAME 阈值与 LT 判断）。

满足时对**当前 S1 ability 自己的 m_cooldown timer**调用 `PeriodicTimer.Reset(false)(0x181f13fc0)`，将 remaining 设为 FP0；不是直接重置原普攻 timer。未满足则保留原生 remaining。

随后一次性 finish callback 调用 Character.OnAfterAttack，再经实际 slot 68 进入 NextAttackOrCombatSkill.OnAfterAttack。它先执行 BasicSkill.OnAfterAttack，再调用 slot 85 的 ReplacementSkill.CancelAfterAttack。正常实际 S1 命中同一 replacement ability 时执行：

```text
ReplacementSkill.CancelAfterAttack(0x1809641d0)
 → Character.UnregisterReplacement(0x180a10100)
 → Character.ClearReplacement(0x180a05770)
 → 原战斗/原普攻能力.UpdateCooldownToMatch(S1 ability, false)
 → S1 ability.ResetCooldown（在回拷之后）
```

ClearReplacement 的回拷点 `0x180a0589c` / `0x180a0590f` 均传 false，仅同步 remaining，不同步原计时器 duration。`Ability.UpdateCooldownToMatch(0x1805ea7d0)` 最终将 S1 timer.remaining 交给 `PeriodicTimer.SetRemainingTime(0x181f140f0)`，该 setter 明确计算：

```text
raw.remaining = Min(S1.remaining_after_OnCastEnd, raw.timer.duration)
```

所以不能将技能前普通攻击的“旧周期剩余值”当作技能结束后的恢复等待。HALF_FRAME 条件将 S1 清到 0 时，回拷也为 0；条件不通过时需保留并限幅实际 S1 remaining。原生 timer 是否在本帧已 Tick、外部属性改变等观察阶段仍不能从这段回拷独自推定。

`AttackState.<_StartAttack>b__5_0(0x180a2a5f0)` 保存 `nextAttackTime = fixedPlayTime + usedAbility.escapeTime`；实际 escapeTime=0。OnAfterAttack 返回后，如果仍在该 state、结束 reason 不是 INTERRUPTED、当前 attack ability.isReady，它在**同一完成 callback**继续 `_NextAttackOrExit`（调用点 `0x180a2a798`）。这是可继续检查下一次普通攻击的原生路径，不是保证所有目标/状态下都立即命中下一击，也不保证新增固定的 1 帧空转。

证据：`cooldown-cfg.json`、`math-guards-cfg.json`、`resume-cfg.json`、`set-remaining-cfg.json`、`attack-callback-cfg.json`。

## 阻回解除：本次结束 callback 内有直接更新

`NextAttackOrCombatSkill.OnAfterAttack(0x180963650)` 在 CancelAfterAttack 返回 true 后，直接调用 slot 78 的 **BasicSkill.UpdateSpRecovery**（`0x18096371b`）。ReplacementSkillFixed 实际虚表确认 slot 78 正是该方法；不能仅依据 BasicSkill.OnTick 再统一添加下一帧。

正常非 used-up 路径下，UpdateSpRecovery 使用 get_isAffecting=false 调用 set_registeredAsModifier(false)，移除阻回 modifier。这个动作发生在正常完成 callback 内。**解除 modifier 与下一次实际技力增加的可观察帧是两个问题**；外部 SP 事件/周期恢复的调度顺序本批未闭合，不得把“同 callback 解除”当作“该时刻必得 1 SP”，也不得伪造完整技能回转秒数。

## 精确剩余未知与可接入范围

已可接入：实际三个 lifecycle flags、末段后 FP 量化且最少一次等待、正常结束 callback 顺序、HALF_FRAME 条件对 S1 timer 的作用、回拷 timer 的阶段和 Min 限幅、正常 finish callback 内的阻回更新与下一攻击 ready 检查。

本批仍未证明：

- 运行中的 XLua/资源热更新与原版 default branch 等价；本调查不追读进程或私人热更新状态。
- 无首段绑定时的全局 first-hit 起点、绝对完整技能持续与完整周期数值。
- 嵌套协程恢复、普通攻击 timer Tick 与外部 SP 调度的全局同帧顺序，因此不把请求等待次数当作可观察结束帧。
- target-dead、打断、皮肤变体、外部修改等分支与原版正常路径是否等价。

以上未知保留为未知；不再由“相邻能力常用一帧”“库存/配置看起来类似”推断。原版正常链闭合不代表实际运行全部分支验收完成。
