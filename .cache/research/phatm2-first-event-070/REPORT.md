# 酒神 S1：原版首段事件、动画绑定与协程观察相位（0.70）

## 范围与结论

本回执只研究酒神 `skchr_phatm2_1` 的动画与协程首段，不修改计算代码。使用安装目录中的公开基础资源与磁盘上的 GameAssembly/metadata，未执行游戏 DLL、读取进程、操作游戏、读取私人状态或发送聊天。

已闭合原版基础资源中的 `Skill_1` 动画绑定、19 号攻击事件的等待、动画与协程在默认原生路径中的调用顺序。原版 Front/Back 均为 `OnAttack=0.5 秒`，动画总长为 float32 `1.600000023841858 秒`，对应表示归一化后的 15/48 帧。**这些是原版资源参考，不是当前运行时的精确伤害帧。** 动画事件在该帧的协程模拟之后产生；回调只设置等待标志，要由之后的协程模拟观察。当前热更新、皮肤、BakeMuzzle 有效路径、additionalFrame 跳帧与施法起点的帧编号仍未证明，不能自动统一加一帧。

可用于局外参考的范围：首段原版事件时间、按真实攻击周期缩放的动画速度、第二段相对第一段的固定等待。当前实机的绝对首击、技能结束、阻回结束和下一轮可施法时刻仍不能由本回执自动认定。

## 固定来源

- 安装基础清单版本：`26-08-16-14-00-43_415873`。
- GameAssembly SHA256：`6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`。
- metadata SHA256：`ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。
- 实际技能 prefab 与完整原生等待/施法 CFG：复用 `.cache/research/phatm2-s1-069`，不修改旧证据。
- 实际原版美术包：`chararts/char_1042_phatm2.ab`，7160299 字节，MD5 `79f60304324db3d1712aa855f3ce176b`，SHA256 `f8a5ddfd7a326194225d09ccaf54585da2ba882fa9e072d3d4e3ca7d83b2e766`。
- 原版动作库来源：ArknightsResource 固定 commit `d0b5af0b004b044d322397ce5ae79632b6d9fcdd`。Front/Back 原件哈希与本机基础包内的 TextAsset 完全相同，见 `art.json`、`proof.json`。
- 本目录 `metadata.json` 从固定 metadata 及 Assembly-CSharp 方法指针重新读取方法、字段、枚举、虚表与字符串引用。各 CFG 的每条指令均与源 DLL 的磁盘字节核对，且 bounded traversal 完成，无命中限制。

## 原版实际资源绑定

`dyn/battle/prefabs/skins/character/char_1042_phatm2/defaultskin.prefab` 的根对象为 `-7456859797188275225`，CharacterAnimator 为 `5395107965992408039`。其 PropertiesHash `3f542986ad873354e56cde5b742ce778` 通过公开 MonoScript TPK 唯一对应 `Torappu.Battle.CharacterAnimator`。

该组件 `_animations` 明确将 `Skill_1 → Skill_1`，`speed=1`、`loop=0`。Front SkeletonAnimation `997924176756249575` → SkeletonDataAsset `-1841130023594453041` → TextAsset `-1005696099493026627`；Back 分别为 `8116843474029482983` → `-4082353809600318584` → `7761050131639854937`。SkeletonData 的 modifiers、fromAnimation 与 toAnimation 为空。两份 `.skel` 的哈希分别是：

- Front：`0878a28bf8b77efbdf1aaec7405862323647d70ff4ff48fd5f96d9f1ed27642b`，414093 字节。
- Back：`30241587ed52e7536f75d84c7694fa070ab1504c21dfb8a2f6779bfcacb8ebbd`，273545 字节。

解析计数边界：100 个对象中通用读取器 97 个完整读取；3 个二进制 skel TextAsset 使用原始 length/payload/alignment 校验读取。全部 27 个 MonoBehaviour 均完整读取，不能将通用读取计数写为 100/100。

这证明**安装基础包原版 prefab 的绑定**。不证明本局选择该皮肤、不证明热更新后的对象和代码与基础包等价，也不改写旧动作库的 `runtime_binding_verified=false`。

## duration 与动画缩放

实际 S1 MultiMeleeAttack 的 `_timeMode=0`，metadata 枚举对应 `FROM_ATTACK_SPEED`；`_cooldownKey='duration'` 不会覆盖该分支。`AbstractAnimatedAbility.get_cooldown (0x180ec8bf0)` 的 0 分支在 `0x180ec8e38` 调用 `Entity.get_attackTime (0x18070eb70)`。后者读取 BASE_ATTACK_TIME 与 ATTACK_SPEED，调用 `BattleFormula.CalculateAttackInterval (0x180663640)` 得到原始 FP 攻击周期；该链没有先做 30Hz 周期帧取整。

`UpdatePlaybackSpeed (0x180ec83d0)` 先将上述 FP 记为 `m_attackTime`，再 `FP.AsFloat (0x180ec8648)`，`divss (0x180ec8653)` 除以动画返回的 float32 duration。结果 `maxss` 下限 0.1，实际 prefab `_maxAnimScale=1` 再做 `minss` 上限。`m_animScale@0x1b0` 为 float32；动画播放速度是 float32 `1 / m_animScale × spineAnimSpeed`。原版 binding speed 为 1。

无相应减速分支作用的原版参考写为：

`scale = min(1, max(0.1, float32(FP_attack_interval.AsFloat / float32(1.6))))`。

不要用已经取整的攻击步长除以 48 帧替代该来源。`GetDuration (0x180ec77b0)` 返回 `m_attackTime`；UpdatePlaybackSpeed 在 `0x180ec8709..8717` 又将 float32 `scale × animation_duration` 转回 FP。EasyToStartAbility.OnCastStart 将 GetDuration 缓存到 `m_cachedDuration@0x118`。因此该 duration 不是随意把表格技能黑板的 duration 搬入首段等待。

减速、热更新与动画查找失败分支存在；本回执没有证明本局实时进入哪个分支。

## 首段等待与事件 19

实际 S1 `_waitForAttackEvent=1`，`_waitAttackEventForAllAttacks=0`，`_interuptIfTargetDead=0`。默认原生链：

1. MultiMeleeAttack.OnCastStart → AbstractBasicAttack.OnCastStart → AbstractAnimatedAbility.OnCastStart → EasyToStartAbility.OnCastStart，并播放实际 `_animKey='Skill_1'`；上/下方向专用键为空。
2. AbilityStandard._DoCast 的 initial 分支在 `0x1805fa209` 等待虚表 slot 78 `OnWaitForPreDelay`，恢复后直接进入 OnSpellStart；该处没有固定的空一帧指令。
3. Multi 的 PreDelay iterator `0x180e928e0` 先等待 Easy 的 PreDelay iterator `0x180ed6a00`。Easy 在 `0x180ed6aa7` 记录 fixedPlayTime，并因 waitForAttackEvent 为真创建 `WaitForNextEvent(0x13, m_cachedDuration)`。
4. `Entity.Event.ON_ATTACK_EVENT=19=0x13`。WaitForNextEvent iterator `0x180ed71d0` 注册 owner eventPool 回调 `_OnReceiveEvent`，以 `_CheckNotReceiveEvent` 做固定等待谓词，随后注销回调。`_OnReceiveEvent (0x180ed3d10)` 在 `0x180ed3d53` 仅将 `m_receivedEvent@0x120` 置 1；谓词返回该标志的反值。
5. SpineAnimator._RegisterSkeletonEvents 明确注册 `_OnEvent`。`_OnEvent (0x180624780)` 匹配 metadata literal `OnAttack`；在 BakeMuzzleController 无效的默认 fallback 分支向 owner eventPool 发出 19。BakeMuzzle 有效时该分支抑制重复发出，不能泛化为所有 OnAttack 都直接进入同一发出点。

FP WaitWhile iterator `0x18066e6f0` 初次 MoveNext 计算最大 tick 数并至少 yield 一次，初次不调用谓词；resume 分支在 `0x18066e80a` 调用谓词，若 false 则结束。等待完成后 Multi 因 `_waitAttackEventForAllAttacks=0` 不再另等一个逐段攻击事件。

尚未证明实际本局 BakeMuzzle 的有效状态，也没有把 timeout 当成观测到攻击事件。伤害/损伤动作执行链由主代理单独封存，本回执不重复认定该链的最终伤害落点。

## 协程嵌套恢复与第二段

CoroutineSimulator.StartCoroutine `0x18066a060` 立即调用 RuntimeHandler.MoveNext `0x18066cdd0`。栈中每个新 Routine 以 `firstTouch=true` 创建；子 iterator 已经 yield 后，该记录转为 false。正常子 iterator 完成时（false 且 firstTouch=false）同一次 MoveNext 继续父 iterator，不必自动加一个桥接 tick。**新子 iterator 初次就 false 且 firstTouch=true 的分支会结束当次调度**；不能据此反过来声称所有零等待都同帧恢复。

实际 S1 段间 iterator 为 `float32(triggerDelta × m_animScale)`，triggerDelta 是序列化 float32 `0.4000000059604645`。既有 0.69 已确认 float fixed wait 按 `seconds / deltaPlayTime` round-to-even，并强制至少一次 yield。该子 iterator 已经正常 yield 后完成，不属于 firstTouch 立即 false 的额外调度边界。因而第二段相对第一段的默认原生等待是：

`max(1, round_even(float32(triggerDelta × scale) / deltaPlayTime))` 个 fixed yield。

deltaPlayTime 使用运行时实际值；以 30Hz 做局外原版参考时要标明该约定。不能改为 ceil，不能对所有两段等待固定再加一帧。

## 默认原生 tick 顺序与绝对首击边界

本批只补了一条具体入口链，没有追完整游戏 tick 系统：

`BattleController.OnTick → CoroutineSimulator.SimulateTick (0x18063bc9f) → ObjectManager.OnLateFixedUpdate (0x18063bd40) → Character vslot28 = Unit.OnLateTick → get_animator vslot161 → CharacterAnimator vslot30 = OnTick → SpineAnimator.OnTick → _TickSpineManually → SkeletonAnimation.Update`。

ObjectManager 的 late 调用点 `0x1808c34ac` 使用 vslot28；Unit.OnLateTick 在 `0x180aa9936` 使用 animator vslot30。对应虚表由本批 metadata 直接读取。CharacterAnimator 继承 MonoBehaviour，与 BObject 的 vslot27 不同：BObject/Character 的 slot27 为 Character.OnTick，CharacterAnimator 的 slot27 是 SpineAnimator.UpdateTimeScale，不能混用槽号。协程后的 BattleController `m_globalBuffs@0x68` 循环也不是 animator 循环。

Spine._TickSpineManually 读取 RemoteConfig.spineTickInAdditionalFrame；配置不允许时 additionalFrame 只累积时间，实际更新移后。执行更新时在 `0x180625442` 以累积 FP.AsFloat delta 调用 SkeletonAnimation.Update。由此证明默认手动动画路径中的 OnAttack 在当次 CoroutineSimulator 之后触发，事件回调置位后至少要由后续的协程调用观察。

仍不能直接得到“当前技能第 16 帧造成首段伤害”：本批没有证明施法起点相对于 tick 的编号、动画第一次推进是否计入起点、当前 additionalFrame 配置、热更新替换和实际 BakeMuzzle 路径。15 帧仍是原版资源事件参考。将观测顺序作为误差边界说明可以；将统一 +1 自动写成实际首击不可以。

## 复现与验收

在项目根目录使用 `.venv/Scripts/python.exe`：

1. 运行 `read_art.py`，读取固定安装基础包并核对清单，更新本目录 `art.json`。
2. 按 `verify_sources.py` 中 `CFG_REQUESTS` 重跑 CFG 读取；每个输出使用 `../phatm2-first-event-070/...`，不会覆盖旧 evidence。
3. 运行 `read_metadata.py` 更新本目录 metadata。
4. 运行 `verify_sources.py`，检查源哈希、全部 CFG 指令字节、关键调用/字段/槽号、事件枚举、原版 Front/Back 数据与 TPK 类型身份，生成 `proof.json`。

`proof.json.passed=true` 仅表示上述静态证据与边界经过核验，不表示当前运行时绑定、完整技能生命周期或实际面板配对通过。
