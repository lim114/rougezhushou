# 第 062 节候选只读审计：复选框文本不能自动确认条件

本目录只做来源与公开输入合同调查，没有补丁，没有改 tracked 文件。最窄、来源充分的候选是黍 `four_sui` 的非布尔文本被当成已经确认四岁编队；银灰 S3 `preexisting_fragile` 是另一个已复现的候选。尚未指定全局拒绝、字符串转换、数字或 null 策略。

## 快照与资料

首次复制的是 HEAD `cab0c03e5bcc82597c698f79ecd4f68562ea7317` 上 root 第 060 节正在工作的公开 package `.py/.json` 文件，共 121 个，准确的 WIP 状态和逐文件哈希保存在 `freeze-receipt.json`。并未把这个副本误称为干净的 059 提交。随后第 060 节提交 `c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf` 后，全部 121 个文件与提交后干净源码哈希一致，见 `commit060-equivalence.json`；这是等价性复核，原矩阵仍是在明确的冻结副本执行。

使用已经固定的原 game commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`，重新核验两个当前原表缓存的 SHA256：character `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`，skill `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。精确 selector 和完整原记录见 `source-receipt.json`：

- `character_table.char_2025_shu.talents[1].candidates[0]`：PHASE_2 / level 1 的天有四时明确要求“编队中有四名【岁】干员”，提供 `atk=.12, interval=4, sp=1`。该参数只支持符合资格时的静态攻击和周期参数；没有提供新的首跳、重置、阻回时钟。
- `skill_table.skchr_svash2_3.levels[9]`：S3 脆弱参数 `damage_scale=1.3`、显示量 `.3`。现复选框是“全程计该技能脆弱”，没有以本次输入调查证明实际首次施加或覆盖时间。
- 复用第 060 节既有资料，确认不把四岁周期参数改回均匀自然 SP；本次问题是条件被文本误确认，而非该机制时钟的新推测。

## 实际公开反例

普通 `calculate_damage`，`base_attack=1000`、`window_seconds=10`，两种时序模式均可复现：

| 输入 | False 布尔控制 | `'false'` / `'unknown'` / `'0'` 文本 |
| --- | --- | --- |
| 黍 S3 `four_sui` | 攻击 1500，窗口伤害/治疗各 12000，初动 15 秒、充能 45 秒 | 整份结果与 True 完全相同；攻击 1620，窗口伤害/治疗各 12960，且进入第 060 节四岁周期 SP 的未知时钟分支 |
| 银灰 S3 `preexisting_fragile` | 窗口伤害 16000 | 整份结果与 True 完全相同；窗口伤害 20800 |
| 银灰 S3 `cooperative` | 窗口伤害 16000 | 整份结果与 True 完全相同；窗口伤害 32000，生成协同来源 |

文本本身没有确认编队、脆弱覆盖或协同覆盖的证据。定位分别是 `operator_engine.py:185` 的 `self.s.get('four_sui')`、`damage.py:184/190` 的脆弱 truthiness，以及 `damage.py:193` 的协同 truthiness。这里仅确认公开输入如何走进现有模型，不声称这些数值为实际游戏结果。

`public-counterexamples.json` 保留 90 个重点公开输入、整份返回值和格式化报告。`boolean-input-matrix.json` 广泛调查 25 个 checkbox 定义（23 个 OPTIONS 条目与 2 个全局银灰控制），共 96 个 operator / skill / mode 活动组合、每组合 18 种输入，1728 次调用、0 计算错误。`'false'`、`'unknown'`、`'0'` 在全部 96 组合均与 True 完整结果相同；其中 92 组合与 False 不同，其余 4 个组合在当前窗口下 True/False 本来相同。没有以这 96 组合对全部其它机制作原生绑定结论，也没有调查整数或状态下拉框作为 bool。

## Qt 合同与旧兼容性

真实生产 serializer 的源码是：`operator_options.py:2` 标明 bool default 对应 checkbox；`app.py:665–667` 用 QCheckBox 创建该控件，`app.py:1035–1037` 只序列化当前 owner / skill 的选项，并调用 `widget.isChecked()`。全局 `cooperative` / `preexisting_fragile` 在 `app.py:1031` 同样用 `.isChecked()`。本次没有新增 GUI/Wine 执行；另一代理只读复核的代码哈希、行号和限制保存在 `qt-contract-review.json`。

已有 UI060 runner 明确断言了 `four_sui` raw 参数为 True 及控件输出的真实 bool 类型；它没有对全局 fragile / cooperative 添加单独 bool 类型断言。runner 断言存在不等于本次已运行 GUI，也不把旧 87 技能循环宣称成新的专门类型验收。

对 94 份 tracked 公开 Markdown（排除 research / verification）检索这三个 API 字段，没有找到接受任意 truthy 文本或规定 numeric 0/1/null 域的文档。既有相关测试使用真正 False/True。源码 truthiness 可观察的兼容性和明确的文档合法域仍应区分，见 `contract-audit.json`。

当前所有 96 组合中 `0/0.0/None` 完整输出与 False 相同，`1/1.0` 与 True 相同；default=True 的选项显式 None 与省略字段还可能有不同语义。本次没有把这些旧兼容输入改为报错，亦没有把 `'false'` 擅自转换为 False 或把 `'unknown'` 擅自变成某个状态。后续修复应明确限制输入合同，至少先保留已经观察到的 numeric0/1/null、缺省和真正 bool；不能因本候选引入全局强制转换。

## 不活跃与资格控制

广泛矩阵另有 1258 次其它 owner / 不适用技能控制，全部与省略字段的整份输出相同。最窄四岁候选再单独核验：

- 黍 E0 S1、E1 S1/S2 × 两种模式 × 8 种 bool/numeric/null/text 值，加省略对照，共 54 次调用：48 个指定值完整输出均与省略值相同，没有未解锁的四岁参考。
- 其余 84 个技能 × 两种模式 × 同 8 种值，加省略对照，共 1512 次调用：1344 个指定值完整输出均与省略字段相同。

以上全部来源于真实公开 API，调用者输入均保持。详情见 `narrow-four-sui-controls.json`。后续只改当前活跃条件的文本误确认，应保留其它 owner / 不适用字段的行为，并明确处理未解锁资格的已有 no-op 边界。

## 候选交接

总共 4552 次公开调用通过调查断言；这些是行为/合同观察，不是 4552 项单元测试。121 个冻结代码/数据文件末尾复核无漂移，两个原表 selector 的参数已明确断言。最窄优先候选为 `four_sui` 的文本误确认，若同节包含银灰 fragile，则应独立声明适用范围与源支持，勿直接推广为 25 个字段的全局策略。

尚未写任何 patch 或生产测试。后续 draft 需保留真正 bool 和已经明确记录的旧兼容输入，针对非布尔文本给出清楚的输入错误/合同处理，并验证活动/不活动/未解锁控制及两种模式。资料没有支持任何新的周期 SP、fragile 首附着、覆盖或协同事件时钟。P2 仍未完成，本审计没有读取私人状态、执行游戏或聊天，也没有原生 Windows、Wine 或实际 GUI 新验证。
