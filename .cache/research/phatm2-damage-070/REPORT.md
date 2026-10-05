# 0.70 P2 酒神 S1：伤害节点与实际天赋数据流

本批只做磁盘静态源研究。所有新文件均位于本目录；没有修改生产代码、测试、项目文档，没有运行游戏、DLL、应用或读取进程内存、聊天和私态。

结论：固定实际 S1 的默认原生分支在每段 `ON_SPELL_ON` 的同一次同步 action pass 中，按 `ApplyDamage → AlwaysNext → ApplyElementDamage` 顺序执行，先提交法术生命伤害 modifier，再提交直接 SANITY modifier。SANITY 节点的比例不是由枚举或相邻机制猜出：实际角色的 `UnitDataFlowConfig` 把天赋 1 的 `attack@ep_damage_ratio` 赋给技能 0 的 `ep_damage_ratio`，并经实际技能继承入口进入能力黑板。直接 SANITY 的基数是来源当前攻击力乘该比例，独立于最终法术生命伤害和 S1 `atk_scale`。

最后一次实际配置检索还命中了 S1 束缚模板 `phatm2_s_1[unmove]`：它把 event 68 绑定到 `EpDamageScale`，只接受 SANITY，非反向、非按层数缩放。原生 `OnTakeEPDamage` 确实派发 event 68，节点读取 buff 黑板的 `ep_damage_scale`（缺失默认 1）并乘接收 modifier 的 value。**完整新 buff 初始化与黑板复制、首次命中 attachment 成功、已有束缚的刷新交互没有在本批继续展开；因此不能仅凭此报告声称首次命中倍率或当前游戏热更新行为完全精准。**

## 固定实际输入

- GameAssembly SHA256：`6edbc00b11e016c8935bbc45f158d5363f63d35038b0a69f8297612235e533ce`。
- metadata SHA256：`ee7f1239e1cff67620a7964d651189dbb5c98e13699169096be2a907fd541118`。
- 唯一地址映射 `../p1-native-mapping-054/script.json`，SHA256：`ee2df4d3595653a2483e8622f0cfb05b4338e6eb01416a6e8dd5cae06699c42b`。
- `../phatm2-s1-069/skill-prefabs.json`，实际 prefab `skchr_phatm2_1`、能力 pathID `1442620349020702503`：`_damageType=2(MAGICAL)`、`_extraDamageType=0`、`_elementDamageType=1(SANITY)`、`_epDamageRatio=0`、`_splitDamage=0`、`_atkScale=1`、`_atkScaleKey=atk_scale`。选定树精确读完，能力自身无 EpDamageScale action。
- 实际角色 AB `charpack/char_1042_phatm2.ab` SHA256：`2c3863cb24a3f0dac73c7253b84d445d6250be06d079960e020717b60f119386`。数据流组件 pathID `2090084769798240522`，PropertiesHash `93998a60fc75d8c5eae26c6cf07a393f`，在固定公开 MonoScript receipt 中唯一匹配 `Torappu.Battle.UnitDataFlowConfig`。
- 实际模板源 `config/buff_template_holder.ab` SHA256：`7f2a20c0c37054501cf256d33f637e43ea6a04dd67877c4b8621e7cede22f34f`。唯一 `phatm2_s_1[unmove]` 在 holder pathID `6070581171229484677` 的 `_templates[4431]`。本批按该唯一模板重读原 AB，保存为 `s1-unmove-template.json`。
- 原始 base 版本 `26-08-16-14-00-43_415873`。引用旧 receipt 是复用其公开来源与解析成果，没有向旧目录写入。

## 天赋到实际 S1 的原生小链

配置精确为 TWO、ASSIGN、source TALENT、sourceTalentKey `1`、sourceKey `attack@ep_damage_ratio`、target SKILL、targetKey `ep_damage_ratio`、validateSkillIndices=true、skillIndices `[0]`。不使用天赋另一项未加前缀的 `ep_damage_ratio`；后者属于独立的周围目标损伤，不在本研究范围。

`Character._AssignData` 在 `0x180a11403` 调 `UnitDataFlowConfig.Init`；`ModifierConfig.CreateModifier` 在 `0x180ac1bad` 限定技能下标、在 `0x180ac1cf0` 选择天赋 1 黑板、在 `0x180ac1fd9` 读取实际 sourceKey。`Modifier._ModifyBlackboard` 的 target=SKILL、formula=TWO、modify=ASSIGN 分支在 `0x180ac360c` 调 Blackboard.Assign，把该源浮点值写入 delta。

`Character._AssignSkill` 在 `0x180a117fd` 以 dataType=1(SKILL) 取 delta，再调实际技能 slot 51。**实际 ReplacementSkillFixed 的该槽是 NextAttackOrCombatSkill.AssignData，并非直接 BasicSkill。** 新提取的实际继承方法 `0x180963300` 在 `0x18096338a` 转调 BasicSkill.AssignData，保留 delta；后者在 `0x18091a4ec` Union 进技能黑板，在 `0x18091a7e4` 给主能力 SetData。能力 slot 27 指向 MultiMeleeAttack.DoSetData，依次进入 MeleeAttack、AbstractBasicAttack 的 DoSetData。`0x180e7b59a` 从能力黑板取 `ep_damage_ratio`，取 max(0)，所以实际天赋比例为正时创建直接神经节点。

## 节点、顺序与同段同步范围

`AbstractBasicAttack.DoSetData (0x180e7b3e0)` 清空 m_actions。实际 extraDamageType=0 跳过额外伤害节点；main damage 经 slot 106 CreateDamageNode 创建并在 `0x180e7b75f` append。正 ep ratio 分支在 `0x180e7b7ee` append AlwaysNext，再经 slot 108 CreateElementDamageNode 在 `0x180e7b827` append。

- slot 106/107 的实际继承方法是 AbstractAnimatedAbility.CreateDamageNode/NewDamageNode；`0x180ec7b2c` 调 ApplyDamage 的实际带参 ctor。
- slot 108 是 AbstractAnimatedAbility.CreateElementDamageNode；`0x180ec71aa` 调 ApplyElementDamage 的实际带参 ctor，存入 m_epDamageNode。
- `MeleeAttack.GetEventActions` 在 `0x180e8c9c2` 比较 event=4，在 `0x180e8c9d4` 返回上述 m_actions；metadata 原枚举名是 `ON_SPELL_ON`。
- append helper `0x18053c2c0` 在正常容量分支把元素存入旧 size 位置再增加 size，slot helper `0x18003b2d0` 按 16 字节虚表槽调用；实际类型的 slot 与字段偏移均由固定 metadata 重读核验。
- AlwaysNext 的默认 executeCondition=0，CheckExecute 对条件 0 无条件返回 true；AlwaysNext.Execute 返回 true，恢复后续节点的前项结果条件。
- 复用 root 的 `../phatm2-actions-070` 已验证顺序迭代和节点 slot 6 同步 Execute。两个 Execute 分别在 `0x18102c23f`、`0x18102d9b2` 同步调 Entity.ApplyModifier；这是同一次 action pass 的前后提交，不包含两个节点间的等待/跨 tick 调度。

生命节点 CreateDamageModifier 走 CalculateDamageBySource；元素节点的 m_epDamageRatio×m_epDamageScale 在 `0x18102d137` 相乘，随后 `0x18102d160` 调 CalculateElementDamage(source,target,ratio)。其 source overload 在 `0x18066477d` 读当前 atk，然后乘 ratio，转入 elemental resistance 公式。创建时 m_epDamageScale=1；没有把该基数设置成最终生命伤害，也没有自动乘 S1 `atk_scale`。法术节点先造成的死亡、取消、免疫等可影响后续执行，所以“同段顺序”不意味着无条件两项必定生效。

## 实际束缚倍率回调

S1 实际 `_activeBuffs[0]` 的 templateKey 是 `phatm2_s_1[unmove]`，durationKey 是 `unmove`。模板 event 68 唯一节点是 EpDamageScale，filterElementType=true、elementType=SANITY、filterApplyWay=false、isOneMinus=false、isStackable=false。不是名称相似的 rogue 全局 buff；`global-ep-scale-prefab.json` 特意保存最后一次 globals 搜索的无关结果与实际 char/S1 中无显式倍率 action 的结果。

Entity.ApplyModifier 在 `0x1806fd810` 进入 `_OnApplyingModifier`；其 elementDamage 分支经 slot 132（Entity、Character、Enemy 均继承 Entity.OnTakeEPDamage）调用 `0x180707c30`，在 `0x180707d95` 转 BuffContainer.OnTakeEPDamage。容器把当前 modifier 放入 ChangeGuard，并在 `0x1806860f7` 调 Buff.OnTakeEPDamage；该方法以 `0x44=68` 调 `_RunActions`。`0x18069967b` 使用 buff.m_blackboard 进入同步 ActionUtil.RunActions。EpDamageScale 在 `0x181036e03` 取固定 literal `ep_damage_scale`、在 `0x181036f24` 把接收 modifier.value 与倍率相乘、在 `0x181036f33` 回写。当前接收 modifier 的语义由此直接建立。

父批 OnCastOnTarget 已含 attachment.Apply 位于 action 执行之前；本批也保存了该 interface dispatch 的 CFG，但没有继续展开实际 Buff 初始化/黑板复制全过程。此次闭合的是“实际束缚模板的倍率回调绑定及原生执行方式”，不是任何未知首击/刷新边界的补猜。

## 复现与边界

使用项目已配置 Python 执行：

```powershell
& 'C:/Users/李娜/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' .cache/research/phatm2-damage-070/verify.py
& 'C:/Users/李娜/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' .cache/research/phatm2-damage-070/verify.py --replay
```

普通核验重新读取 DLL，每条保存的 instruction / RIP 数据逐字节比较，并核验固定来源 AB、实际配置、唯一 PropertiesHash、虚表槽、字段偏移和关键指令锚点；`--replay` 先重提本目录 CFG、metadata 和定向模板，再做同样检查。metadata helper 只执行 `selected=[]` 前缀，CFG helper 的输出根始终是本目录。native-proof.json 由 verify.py 生成，含可机器核验的来源、锚点与剩余边界。

重提与核验已通过。本目录 52 个方法条目 / 7221 条指令；连同复用的父批 8 个方法条目 / 1330 条指令，共 60 / 8551。此计数按 CFG 方法条目统计，可包含复用入口，不冒充不同函数数量。另核验 34 个关键指令锚点、44 个相关 metadata 类型与 430 个已解码 type/string 引用。

XLua/hotfix override 分支存在，静态文件不能证明当前运行等价；本批不碰 live 状态。整体 tick scheduler、血量最终扣除、元素爆发、溅射天赋、取整、首击束缚 attachment 与后续刷新均不由本报告扩大声称。
