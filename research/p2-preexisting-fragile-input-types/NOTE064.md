# 第 64 节 · 凛御银灰 S3 脆弱条件不接受字符串确认

原公开 `preexisting_fragile='false'` 会按 Python truthiness 启用所选技能脆弱，与真正 `True` 完整输出相同。默认 rank 10 的技能倍率 1.3 因而误计入输入本想表达的 False 情景。本节仅拒绝实际使用该字段的字符串，不创建猜测用户意图的文字解析器，不更改脆弱、伤害或叠加公式。

## 原始来源与实际代码路径

固定原表 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，当前 character/skill 缓存原字节已重新哈希：

- character_table.json：14,975,251 字节，SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`。
- skill_table.json：11,447,929 字节，SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。
- 本次正常 TLS 下载并核验 [gamedata_const.json](https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/a550f5e048bb94e7cdefc6eb97a4091f0c4c7add/zh_CN/gamedata/excel/gamedata_const.json)：57,803 字节，SHA256 `216985a6185c199ee703eac1fb8c35f51ca6d45141894df9c1fd9397b6c940ee`。文件只保存在外部审计目录，没有填入 root 缺失历史 cache 或改变原测试可用性。

公开别名 `silverash` 是 `char_1045_svash2`「凛御银灰」，职业先锋。S3 `skchr_svash2_3`「变革已至」解锁门槛精二 1 级；其原描述为丹增造成直线范围物理伤害并施加该技能脆弱。倍率来自所选 S3 rank 的 `damage_scale`，不是基础天赋。全三技能的 30 个 rank 黑板数值、描述、持续参数和技能解锁门槛均与现规范资料核对相同；完整原黑板保留 `valueStr`，数值规范映射使用原 `value` 字段。S3 rank 1–3 倍率 1.15，4–6 为 1.2，7–9 为 1.25，rank 10 为 1.3；不是所有等级一律 30%。

当前 `silverash` 走 legacy `_skill_damage` 和 `build_estimate`，不是 `Combat.calculate`。S3 的本体/声明协同丹增均是 physical 分项，通过同一个原始 `bb['damage_scale']` 条件乘区；当前 `scenario.get('preexisting_fragile',False)` 直接测试 truthiness。估算器的「开放性开局」选择只处理初始技力/再部署，「雪境先驱」选择只处理防御/生命回复资料；报告使用 `operator_engine.selected_talents`。精零、精一、精二 × potential 1/5/6 的 9 次选择中，已选择的基础具名天赋没有 `damage_scale`。6 个原隐藏 unnamed 候选也保留在来源回执中，没有自动附着或合并它们。

GUI 已有 `MainWindow.fragile` 是 `QCheckBox`，标签「全程计该技能脆弱（不勾选则全程未计）」、默认勾选，只在 silverash S3 显示；提交使用 `.isChecked()` 产生真实 Python bool。GUI 默认 True 与裸 API 缺省 False 是既有的两种调用约定，本节都保留；当前没有该字段的 GUI 文字解析入口。本作者只查控件与 producer 源码，没有将静态检查冒充实际窗口操作。

## 脆弱与叠加的已知/未知范围

固定常量 `termDescriptionDict['ba.fragile']` 明确原文：

> 受到的物理、法术、真实伤害提升相应比例（同名效果取最高）

这闭合基础术语与「同名最高」文案；当前 S3 分项本身是物理。它不证明手工 `damage_taken` 效果与 S3 脆弱是否来自同名来源，也不闭合模板附着、首次命中先后、刷新、快照、结束残留或当前热更新。原 `weak[limit]` 等字段只保留原参数，不能据名称猜叠层数、覆盖率或实例数量。

当前现有手工 math 合同是：匹配伤害类型的 `damage_taken` 值先加算为 `1+sum(values)`，再与已声明的该技能条件倍率相乘。这是既有测试情景算式，本节不把它当作多个实际脆弱来源的原生叠加证据，不更改该公式。现存 `.cache/research` 177 个文本回执/CFG 已逐个哈希，并按 `char_1045_svash2`, `skchr_svash2_3`, `svash2_s_3`, `svash2_t_`, `ba.fragile` 精准检索，没有当前 S3 的匹配原生绑定。搜索范围局限于保留文件，不能证明完整安装包里无实现。

来源、producer、实际调用路径和限定范围见 `source-receipt064.json`、`source_audit064.py`、`constant-download064.json`。

## 最窄修改

在 `_prepare_damage` 原 skill/rank/training 资格检查之后，对 `operator=='silverash' and skill==3` 的 `preexisting_fragile` 原值仅增加 `isinstance(raw,str)` 拒绝。错误信息要求提供明确布尔条件，字符串「false」「true」「0」「1」和空串都不会被解释成新的确认。

- bool False/True、数值 0/1（含 0.0/1.0/-0.0）、null、缺省保持旧完整结果。
- 其他现有非字符串输入的旧 behavior 也保持；这次没有扩展为全局严格 bool validator。
- silverash S1/S2 与其他干员/技能的 inactive 同名字段保持旧完整输出，即使其字段内容是字符串。
- E0/E1 尚未开放 S3 时继续先返回原资格错误，不用字符串 guard 改写错误归因。
- 原 rank 数值、基础天赋/培养选择、协同声明、伤害类型、每击减伤、所有源倍率、scope/时钟与报告公式均未改变。
- 零观察窗口、零敌方生命周期等仍需合法当前字段，不能靠输出恰好为零而把字符串当作有效确认。

## 公开回归与冻结证据

外部冻结是 section 60 commit `c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf`，从 `git archive` 取精确提交。root 初次观察该提交时干净，之后推进 61；冻结时实际 root 已为其他已提交 HEAD，回执分别记录，没有混入 root WIP。原冻结 2,167 个公开文件逐个哈希保持完整。

只读原公开探针保存 976 次调用的完整 JSON/错误，显示真实 False/True 与数值/null 的既有契约及字符串 truthy 反例。另在外部 draft 执行同一 976 个请求，总计 1,952 次公开调用：

- 50 个已开放 S3 的 active 字符串从旧成功变为明确 ValueError。
- 866 个其余成功请求的完整 JSON 哈希一致，包括非目标类型、合法数值/null、inactive 全技能与现有合作/手工伤害类型情景。
- 60 个精英/技能资格错误的类型与文字完全相同。
- 0 未解释差异；所有调用者输入与缓存 catalog 保持。

7 个新测试方法通过，覆盖全 rank 1–10/两模式、字符串、不变的合法原值、inactive 全 87 技能范围、原资格错误、零窗口/生命周期、合作与手工来源、输入隔离。与 4 个现有目标回归模块合跑共 73 个方法，73 通过，0 skip/失败/错误，源码起止 SHA 同。原基线定向红测 1 个方法/160 个字符串子场景如实失败，是旧行为的缺陷证据，不计通过或重复开发尝试。

第一版新测曾误假设 legacy continuous S3 的 `target_windows=[]` 必须有零伤害。实际原基线该情景仍显示旧 math 52,240，而 frames 为 0。已保留失败日志，改成核验既有缺省完整结果不变；零窗口/零生命周期为 0 的原行为仍直接核验。本节没有顺带改变 continuous 范围合同或声称其实际命中。最终所有回归通过。

补丁只含 damage.py 两行输入 guard 与新独立测试模块。精选 runner 注册由 root 集成时增加 `test_preexisting_fragile_input_types`，避免夹带过期 runner hunk。`manifest064.json` 保存所有公开成品哈希，`handoff-receipt064.json` 记录最终 root apply-check、基线/测试/矩阵和独立审阅状态。

独立审阅、root 实际集成与每五节 Linux/Wine/实际窗口全量验证由各自最终回执记录，本作者 Python API 探针不冒充 Windows、游戏或 GUI 验收。P2 的首次施加、叠加实例身份、覆盖/快照、残留与实际脚本绑定仍保留为未闭合问题。
