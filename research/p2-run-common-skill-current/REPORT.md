# 已读本局公共等级用于其它技能的显式计算参考

本组对应“肉鸽受限精英形态的已培养公共技能等级可用性”。已有118节手选当前技能的账号等级，已经允许公共1–7作精英0参考；单独把旧说明中的未知改成已证不构成新功能。本组新增的是：本局只读到某一技能的公共等级时，在精英0/1的已确认形态下，可明确选择该公共等级参与其它已开放但未直接读取的技能计算，同时显示全部技能的原件使用资格与来源。

例如本局已读苏苏洛S1等级3、S2尚未读取：默认继续旧等级7预览；选择公共等级来源参考后，S2实际计算输入改为3，回复单包、技能参数和回技力预算随之改变。取消后恢复原结果。S2依然标记“未直接读取”，不写入账号或本局记录，不确认实际施放。

## 已证来源

当前 GameAssembly SHA256 `583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5`，metadata SHA256 `d3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f`。复用已证92字节类型结构和当前注册表；本组20个方法、4778条唯一物理指令均重新与原文件逐字节匹配，CFG窗口无截断。读取文件，不执行游戏代码或读进程内存。

- 当前实际数据类型是 `PlayerRoguelikeV2.CurrentData.Char/RecruitChar`，二者继承 `PlayerCharacter`。没有用旧名称“CharacterUseData”猜当前类型。其公共 `mainSkillLvl+0x34` 与各技能 `PlayerCharSkill.unlock/specializeLevel` 分开。
- `RoguelikeBasicCharInfoModel` 构造器157263（`0x1821942c0`）将同一个 PlayerCharacter.mainSkillLvl 复制至模型 `+0xa8`，技能数组复制至 `+0xb0`。
- `GenerateSkillViewModel` 34097（`0x182846320`）遍历所有技能，每项都从同一个 get_mainSkillLvl 读取公共等级，再单独传入该技能 specializeLevel。`GetSkillData` 33612（`0x1827433b0`）将两者相加取原始技能等级。
- `GetFinalSkillLvl` 29007（`0x182107220`）从同一公共字段读取等级，并且仅在该技能 unlock 成立时增加它自己的 specializeLevel。两个准确数组辅助窗口保留；不将未知 helper 的托管名称冒充已解出的符号。
- 肉鸽 `CreateBattlePlayerData` 34095 和 `RoguelikeBattleStartControllerPlugin.OverrideInParams` 157351 以当前肉鸽 PlayerCharacter 调用该等级求和，再传入 AdvancedCharacterInst 和实际战斗转换。
- `_ConvertInternal` 77906 的 `0x180abd09e..0x180abd0c4` 调用 MainSkill.TryGetUnlockCondition 和 UnlockCondition.Validate。前者 `0x182327cc0` 对公共等级1–7返回技能自身 initialUnlockCond（`+0x30`），并不读取 allSkillLvlup 公共训练门；仅专精等级且非空 specializeLevelUpData（`+0x28`）才读取专精条件。Validate 比较阶段，阶段相同才比较等级。使用门和训练门必须分开。
- 失败分支不会证明“自动截成公共7”或任何招募补偿。好友 SharedCharData 的 CheckData/CheckAllSkillAndEquipData 参数已定位，但尚未绑定成肉鸽招募生成路径，所以没有借用好友限制规则。

参数原件固定于 `Kengxxiao/ArknightsGameData` 提交 `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。character_table、skill_table、roguelike_topic_table 均与已有原件哈希匹配；char_patch_table 使用同一固定提交重新下载并与本地字节比较。431形态、949技能的ID、阶段门和技能数量完整对齐，阿米娅两升变职业使用自己的 patchChars 原件。这里只新增技能使用门绑定；118原来的30形态训练资料保持其原范围，不借用法术形态填充升变训练资料。

定向查证 [PRTS 集成战略](https://prts.wiki/w/集成战略) 可佐证常规、临时、助战招募的能力来源不同及未进阶限制。该页面不证明精英0使用公共5–7的原生门，也不证明自动公共等级补偿算法；对应缺口仍保留。

## 功能边界

- 新界面选择默认关闭。只有同一干员、scope=run、精英0/1已列入 run_confirmed_fields、精英字段未失效、至少一项当前已开放技能具有有效公共整数1–7且来源一致时可用。其它技能必须通过自身原件使用门。
- 无效、布尔、字符串、小数、被屏蔽、锁定技能、其它干员或账号档案来源不作为共享等级；互相冲突的公共等级不选定结果。只保留符合来源资格的公共读数。
- 已直接读取的当前技能不会被公共参考覆盖。账号等级手选继续遵循118原规则；明确选择账号参考时优先使用该来源。账号专精仍不会自动截7。
- 精英2缺失的专精不由其它技能推导。本组没有将mastery读数转换成公共等级来源，未采用招募阶段上限填补等级，也没有计算临时招募补偿。
- 选定后，现有计算的实际 skill_rank 输入、回复/伤害单包及回技力参数使用该等级；培养说明列出全部技能的来源、选用等级和静态资格。报告的未确认培养项明确显示所选技能未直接读取。记录和私人设置不变。
- `e0_common_use_verified` 继续保留实际使用未知；新增 `native_skill_use_rule.native_static_rule_verified` 描述封存编译规则。原生静态门已证，不等于当前热更新或实机状态已证。

## 验收

最终34条必要检查全部通过：新14条API边界、2条实际 MainWindow 类的公共临时状态检查、既有118的18条检查。其中实际 training_view 合并入口确认账号等级没有混进本局公共等级来源；未知在场状态回退账号时不采用。所有旧118约束保持，包括不截账号专精、不填招募上限、缺失升变训练资料、直接读取优先、取消恢复以及原件训练坐标。

初次31条有1错误，测试误用不存在的 estimate.skill.sp_cost；改为比较真实 recharge_seconds 输出，保留原回复和取消恢复检查。第二轮33条有1错误，测试误取 AccountCache.state；改为实际 records 字段，保留账号/本局不变断言。初次失败均封存，不能计为通过。两个GUI检查使用真实 MainWindow 类、公共合成视图和临时状态，没有游戏采样、聊天或私人状态访问；串行集成后仍需实际可见项目窗口检查。

## 剩余工作

账号到本局 CurrentData 的招募限制/补偿生成算法、真实临时或助战培养来源、每技能实时 unlock、精英2未读专精及当前热更新仍未闭合。重启条件是取得版本对应的招募生成/原始响应变换路径或已授权真实状态证据。本组只关闭公共等级的封存使用门和显式共享参考能力，不删除整个培养来源待办。
