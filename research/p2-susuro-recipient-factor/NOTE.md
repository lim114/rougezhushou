# Draft 046 — 苏苏洛低费受疗资格覆盖充能期普疗

仅/tmp修改，生产源码/测试/公开数据固定复制自 `codex/p2-development` 第45节提交 `2180a22a4fee4b9fd0ff6c01791d2791d0a44475`，生产依赖hash在 `base-receipt.json`。`baseline/rouge` 是该提交原始未改代码；`rouge` 是同一依赖集加本节窄修改。未动tracked生产文件，未联网、未运行原生游戏/聊天、未写私人状态。父代理全量45仍继续运行，合入前采用 `draft.patch`；不能用整个/tmp旧文件覆盖后续生产改动。

## 原来源与公开问题

固定 game commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`；原表重算SHA/bytes并核对catalog manifest，见 `source-receipt.json`。

- character_table `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。
- skill_table `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。
- uniequip_table `b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9`。
- battle_equip_table `006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460`。

`character_table.char_298_susuro.talents[0].candidates[0..3]`：编入队伍时，初始费用不超过10的干员受疗增强，E1潜能1/5为1.10/1.13，E2潜能1/5为1.20/1.23。它是受疗资格，不是仅在技能期间开启的增益。现有公开 `low_cost_healing_target` 已明确声明该资格，不自动从任何实际队伍或友方血量推断。

技能原绑定：`character_table.char_298_susuro.skills[0].skillId = skcom_heal_up[2]`，S2为 `skchr_susuro_2`。两技能十级参数全部核对归一化一致，level9原值保存在receipt。

`uniequip_table.equipDict.uniequip_002_susuro` 解锁E2 Lv40；`battle_equip_table.uniequip_002_susuro.phases[1]/[2].parts[1]` 为同身份 TALENT_DATA_ONLY、talentIndex0/prefabKey1、同名微创治疗、non-token/null tags，E2模组2潜能1/5为1.23/1.26，模组3为1.25/1.28；模组1不覆盖。此处复用已存在 selected_talents 选择/资格和同身份替换，不叠乘原天赋。parts[0]另有低血HP<.5、1.15治疗trait，未接入本节低费factor，不推新叠加规则或宣称整个模组已完成。

旧公开 source-backed S1，base_attack1000、E2 P1：frames 非低费 skill15300/cycle26300，低费 skill18360/cycle29360，充能普疗仍11000而应按同资格13200。连续低费旧cycle26320、应28320。S2同一遗漏，frames旧56400→57600、continuous旧55400→56400。原始14调用和独立审计在 `/tmp/p2-audit/after-045/alternate-source-and-reproduction.json`，本提交未改45草稿。

## 窄修改

仅 `rouge/operator_engine.py` 的苏苏洛/古米/黍共用分支，增加 `recipient_factor`（仅苏苏洛且已选低费资格才读取微创治疗heal_scale，否则1）；技能和normal普疗都传相同scale，各一次。完整技能/窗口仍沿现有技能分支factor，唯一数值修复是charge/recharge计划中 普通治疗 的受疗因子。没有改selected_talents、base属性、常规攻击事件、friendly目标scope、初动/自然SP/充能时长、观察窗口、投射与阶段计数、技能S2整场次数规则或任何其它干员模型。

既有单个final healing_factor路径保持，用活玫瑰检查现有参考中的最终数额乘一次，不重新验证该组合的原生叠加层。未知多因子与其它机制沿既有状态。零受疗人数0、单目标受疗上限、E0未解锁微创治疗、P4/P5边界、模组39/40资格均保持。

## 验证

10项新增公开测试和4个现有相关模块合计83 tests通过，见 `related-final.log`。覆盖两模式两技能明确worked numbers、E1/E2 P1/P4/P5因子、E0 rank1未解锁、模组三阶段/P4/P5和39级锁定、zero/cap100、事件与自然SP钟保持、100秒投射的阶段/周期裁剪、既有最终治疗缩放、S2 casts0/1/2、空观察和输入/返回隔离。公共报告仍显示真实友方获取时钟未核验（frames已有说明）；没有调用实际UI或重复已搁置探针。连续语义说明恢复由父代理独立第50节诊断负责，不由本节处理。

`public-baseline.json` 和 `public-draft.json` 各96场景、共192 public calls，`public-comparison.json`：40场景全结构相同，56场景只改变已符合资格的充能疗量和依赖cycle HPS/报告；所有组件、技能/窗口/阶段治疗、timing完整对象、属性与SP clocks完全相同。成对基线cycle按固定受疗资格倍率核对；单技能完整数额原本就正确保持，不借此证明真实友方时间轴。

首个选择器误包含 `tests.test_susuro_recipient_factor`（新增文件实际在/tmp根部），其余83项成功但整个run有一个导入错误；该命令不计通过。删去不存在模块名后完整83重跑通过。静态审阅建议E0用rank1，已调整并重跑83；原表升5/6/7需E1，这只避免测试声称不合法培养，不在46改变现有公开训练等级validation。

独立read-only审阅 `/tmp/p2-audit/after-045/susuro46-static-review.md` 无阻断；其测试hash针对调整E0输入前的版本，最终hash由本freeze给出，不冒称旧审阅已运行最终文件。

## 保持未完成

实际友方获取/阈值/有限正生命周期的连续时序、原生技能/模组绑定和当前热更新/预计实际面板仍未知。第40节友方说明UI三次失败档案保留；父代理已独立诊断 continuous semantic note 丢失并安排第50节，46不重复实际UI检查。本节无全量云/Wine/UI运行，父代理最终合入后按批次执行，不将Wine当原生Windows/game/desktop证明。

阿米娅 `amiya_hit_targets` API最低1与现UI范围一致性、E0技能训练资格仅记录为后续候选，不修改45草稿或本46源码。未凭0输入新造无开启目标链。P2仍未完成，不用一处确定参数修复销掉未知机制。
