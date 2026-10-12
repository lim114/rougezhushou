# 机械师模组：显式条件下的防御前逐包计算

本组对应 PROJECT_PROGRESS.md 的“机械师S3原生冲锋碰撞时钟与攻击快照、模组条件范围”。新增能力是将已封存原件中的模组规则接入真实计算、报告、单包算例、既有冲锋/破屏窗口对照和机械师条件界面。默认关闭；不补全原生碰撞、当前热更新或实际阻挡状态。

## 来源与适用版本

- 参数目录固定于原始数据提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。
- 当前物理 AB 清单版本 `26-09-13-15-28-10-30688348`，五个 AB 原件均重新核验 SHA256、大小及清单 MD5。
- 当前 GameAssembly SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。
- 复用已证 92 字节类型结构及当前注册表，不重新猜测元数据布局。选取 57 个准确 declaring type/method_index 的方法，9097 条唯一物理指令重新与原件匹配，窗口无截断限制。`selected-metadata.json` 保留字段、槽位及方法元数据。
- MonoScript 原始 gmassets SHA256 `02266c5aff4a6d7b6e08db5b70acd76cbaf8dc14818bdeaa0c94af04a25efcce` 与封存脚本源匹配，PPtr 与脚本类型绑定保留于 AB 收据。
- 定向查证 [PRTS 机械师](https://prts.wiki/w/机械师) 可佐证“自己或结构性原理阻挡目标时提高伤害”及冲锋投射来源描述。公开页面不能替代本组原生一级技能门，也不能证明当前热更新一致。

## 原件闭合链

1. `uniequip_002_mcnist` 三阶段隐藏 `11_root` 候选含 `atk_scale=1.5`，限 `rogue_6`，不是 token 属性。resKey 分别为 `mcnist_equip_1_1_p2`、`mcnist_equip_1_2_p2`、`mcnist_equip_1_3_p2`。每个原件同一 GO 上的 BasicTalent 与 PassiveBuffAbility 绑定，后者持有 `mcnist_e_002_trait_atk`。BasicTalent.AssignData → Ability.SetData、DoAttach → Ability.Attach、AddPassiveBuffs 的链证明它是可附着的能力，并不证明一场实际战斗已经附着。
2. 当前一级 `_checkValidBySkillIndex=[0]`，二、三级为 `[]`。准确 converter method_index 77906 从 `AdvancedCharacterInst.skillIndex` 读取 `CharacterData.skills[index]`（`0x180abd037..0x180abd044`），零即第一条技能，再于 `0x180abd6ef..0x180abd6f3` 传入 BattleCharacterData.mainSkillIndex。Character._AssignTalents 从该字段调用 BasicTalent.CheckValidBySkillIndex；当前空列表 helper `0x1844acab0` 返回有效，否则做 Contains。故本组一级仅技能1可选，二、三级可选全部技能；不推广到未知热更新。
3. 模板 `mcnist_e_002_trait_atk` 使用 `ON_CALCULATE_DAMAGE=14`。IfElse 成功支检查目标由本体阻挡；失败支检查由本体 token 阻挡，后续 AtkScaleUp 受前一检查结果门控。ActionNodes.IfElse.Execute 的准确类型地址为 `0x181145ba0`，排除同名 LevelScript 方法。CheckBlocked.Execute method_index 99452（`0x181134510`）读取目标 blocker，对比本体或 FetchTokenOrHost 的拥有关系；数量不证明身份。
4. AtkScaleUp.Execute method_index 96910（`0x18104b320`）在 overwrite=False 分支以 MergeScale（`0x180ae1fa0`）乘以 1.5，再送入 AttackInfo.GetFinalAtk 与防御/抗性公式。Context+Snapshot/AttackInfo 的值类型实际参数布局去掉对象头，`+0xd8` 精确对应 atkInfo.atkScale。不能误作 originAtk、面板加攻或防御后乘法。
5. BuffContainer.OnCalculateDamage → Buff.OnCalculateDamage 的事件14在 source-valid 的 CalculateDamageBySource 路径触发。本体普通/S1/S2本体物理动作、S3法术轰击的 RangedAttack `_useCachedAtkOnly=0` 走继承 NewDamageNode → ApplyDamage → source-valid 路径；实际源是否仍有效保持未知。
6. BattleController.CreateProjectile method_index 64709、flags `0x86` 是实例方法：rcx instance、rdx key、r8 damage source、r9 start。本体 RangedAttack.CreateProjectile 将 owner 放入 r8。S3 额外被动经 token buff 再 CreateBuffToHost，使 `mcnist_s_3_projectile_real` 的 BUFF_OWNER 为机械师；EmitProjectileToTileUseSelector `_sourceType=BUFF_OWNER` 放入 r8，而 `_spawnSourceType=BUFF_SOURCE` 的 token 只用于起点/选择器。冲锋 AdvancedApplyDamage 的 SOURCE 为机械师，缓存/无源/跳 modifier 均关闭，故其 source-valid 路径同样触发14。不能把 token 作为这包伤害的攻击力来源。
7. S2 破屏 AdvancedApplyDamage 的 BUFF_SOURCE 同样绑定机械师。破屏次数仍使用已有“主buff及所属 ability 计数门成立”的条件预算；本组没有产生新的事件时刻、耗弹或补盾状态。

## 接入计算的行为

- 仅机械师具备对应模组培养、`rogue_6` 适用范围和已证技能门时显示 `mechanist_module_static_reference`。默认 False，未选择时全部既有数字和报告不变。
- 使用已有局外情景 JSON 的 `mechanist_target_blocker`：`self`、`own_token` 应用1.5，`other`、`none` 应用1，缺失或 `unknown` 保持单包未知并列两候选。拒绝布尔值、数量、字典或未支持别名。该身份只接受手动情景声明，不从本局记忆、阻挡数、上限、召唤数或目标区间自动推导。
- 独立显示本体常态单次普攻、S1单段、S2单次爆炸、S3本体轰击及机械师来源的冲锋。技能/天赋/稳定藏品加攻先归入已有攻击力参考，技能 atk_scale 与模组 atkScale 相乘，再减防/抗性并应用既有最终减伤/承伤层；不重复改面板、技能加攻或减伤。
- 实际计算结果的逐包组件、单包算例和已有破屏/冲锋预算使用选中的条件包；报告另列攻击力、原包倍率、模组倍率、防御前数值、单包伤害、已有预览/声明次数和条件小计。S3 冲锋仍不推断碰撞；S2 全技能破屏次数不安放进普通观察窗口。
- 已知目标寿命0可排除声明次数；本体获取区间为空不能排除独立破屏爆炸。显式零秒观察预算为0；未提供时长不能伪装成已知零窗口。
- 旧 `known_damage_subtotals` 不能冒充此条件模型的全量结果，选择本组后移除该字段，改用明示模组条件小计。完整施放、阶段、实际观察窗口、回转及DPS均 None，complete=False；只对已证包提供参考。

## 验收与失败保留

最终新增15条数值/来源边界和2条实际 MainWindow 类的临时公共状态 offscreen 检查通过：`Ran 17 tests ... OK`。原有相关兼容78例首轮76通过、2错误来自隔离副本遗漏公共045数据文件；补齐原封存公共文件后仅重跑这2例，两例通过。合计95条唯一用例具有通过回执，不能称为一次95例全量通过。

新检查初次15例中有1失败、1导入错误，原回执保留。失败发现“未提供技能时长”被误当显式零秒窗口；已修正到只在输入明确 `window_seconds=0` 时计零，原断言保留。导入错误来自 root 同期公共211模块未进入早期隔离副本，原样复制依赖到 base/work 后修复。准备阶段 propertiesHash 字典及 exploratory parameterStart 错字段的失败也保留，未用错误参数名称建模。

新增 GUI 检查只验证真实 MainWindow 类控件、情景传递和报告，使用公共合成培养观察与临时状态，未操作游戏、未发送聊天、未读取或写入私人状态。root 串行集成后仍需原项目可见窗口验收；本收据不冒充实机桌面核验。

## 剩余未知与重启条件

实际 blocker、隐藏能力实时附着、源仍有效、每包攻击快照时间、S3碰撞/选择器相位、S2实际破屏/计数门时刻、当前热更新、皮肤/模式路径及完整实际总量均保留未知。本组没有推广到 token 自身伤害、召出结构伤害、治疗或未证作用范围。后续只有取得与版本对应的实际状态/热更新/事件绑定原件或已授权实机证据，才可继续关闭这些缺口；不由当前静态绑定反推。
