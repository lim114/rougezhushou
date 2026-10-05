# 酒神S1原配置与原生段间等待 · 0.69

2026-10-06。只读取安装文件与已固定资料；没有执行游戏代码、读取游戏进程、操作游戏或发送聊天。本批只保存证据，没有修改酒神数值模型，也没有把完整技能时序销项。

## 来源与已确认范围

- 本机公开基包 `26-08-16-14-00-43_415873`：`battle/prefabs/[uc]skills.ab`，1326068字节，SHA256 `696ab9409c73c9ad0ddafdc610b4bf792fdccde9a7e2a3e95702147818ef8796`。解析13170对象均精确消费；`skchr_phatm2_1.prefab`引用图9对象。`read_skill.py`可复现。
- 实际攻击组件1442620349020702503的PropertiesHash为`3b48c5e1f0d3c2bebcc7b66d81f8193d`；固定MonoScript公开TPK唯一对应`Torappu.Battle.Abilities.MultiMeleeAttack`。`_animKey=Skill_1`，首段等待攻击事件，后续段不逐段再等动画事件；`_triggerDelta=0.4000000059604645`，`_additionalTimes=1`，`_minPostDelay=0`、`_maxAnimScale=1`。刷新次数两个开关均关闭。
- 固定技能表十级黑板均`times=2`，不含`hit_interval`。原生DoSetData读取`times`，后续次数为max(0,times−1)；读取`hit_interval`时以配置_triggerDelta为缺省。`read_metadata.py`从原metadata复现字段、虚表、字符串键，不依赖人工填写类型名匹配结果。
- `MultiMeleeAttack.OnWaitForTriggerDelta`默认分支在`0x180e92b33/3d/45`读取`m_triggerDelta@0x240`，乘`m_animScale@0x1b0`，调用float版`AsyncUtil.WaitForFixedSeconds`（0x180615ac0）。因此段间等待不是固定0.01秒，也不能假定永远固定0.4秒。
- `AbstractAnimatedAbility.UpdatePlaybackSpeed`（0x180ec83d0）从原始attackTime与查得动画时长之比计算animScale，下限float约0.1，实际技能_maxAnimScale=1限制上限；并非先对攻击周期取整再计算比例。代码路径同时存在XLua替代入口，本批未证明当前热更新等价。
- float固定等待迭代器（0x1806285c0）按float秒数/deltaPlayTime四舍六入五取偶到整数，至少一次固定yield。round helper 0x18059eb00完整控制流处理±0.5与偶数边界。不能使用向上取整，或额外任意加入一帧。
- EasyToStartAbility.postDelay（0x180ed3e20）为`max(0,cachedDuration−(fixedPlayTime−realStartTime))`；MultiMeleeAttack再与_minPostDelay取max。这说明最后伤害事件不等于施法结束，不能沿用“末击+一帧”作为完整生命周期证据。
- `verify_wine_sources_069.py`核验6份完整CFG、16方法、1496指令字节与固定DLL/meta哈希。文件`native-proof.json`记录结果；未把参数等同于完整外层事件链。
- 目标来源搜索包括[PRTS酒神](https://m.prts.wiki/w/%E9%85%92%E7%A5%9E)，没有取得比上述原配置更具体的段间等待/终止链。已有原版动画库的Skill_1单OnAttack为15/48帧（正背面）；它是显式可选参考，不是已证明的当前客户端/皮肤实际模板。

## 剩余缺口与下次接入边界

1. 闭合技能替换的cast开始、首个动画事件、内部yield恢复、postDelay完成、结束事件和阻回解除的完整外层顺序。`ReplacementSkillFixed.DoTick`缺省仅为空路径/热更新入口，不能据此得出技能结束时刻。
2. 对当前客户端/皮肤动画绑定与热更新作独立证明；不能将15/48帧自动设为已核验默认。
3. 原模型S1法伤没有逐段事件，损伤使用0与0.01秒；此旧近似与新来源不符，仍需替换。替换应同步窗口裁剪、神经爆发/冷却、首伤顺序、技能持续、回转与周期，不能只移动两个损伤时间就宣布修复。
4. 明确限定已证明的相对等待和显式动画参考；未闭合的结束/周期保留未知。未证明实际事件顺序前，不增加猜测参数或战斗自动输入。
