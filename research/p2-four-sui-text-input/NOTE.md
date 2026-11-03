# 第 062 节：仅已启用四岁条件的原始文本输入报错

本草稿只改外部副本中的 `Combat.apply_self_talents` 两行，以及新增 `test_four_sui_text_input.py`，没有改 tracked 文件。固定基线是干净的第 060 节提交 `c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf`，通过 `git archive` 复制公开 `rouge/tests/scripts`；693 个 `.py/.json` 文件逐一固定并复核未漂移。此前 4552 案例只读调查的来源、合同、公开输出与原 no-policy 记录原样保留在 `prior-readonly-audit/`，没有把原调查改写为最终实现证明。

## 来源与适用边界

固定 game commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。原 character / skill 表缓存分别重新核验 SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`、`86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`。

`character_table.char_2025_shu.talents[1].candidates[0]` 的天有四时原资格是 PHASE_2、level1、potentialRank0，明确要求“编队中有四名【岁】干员”，提供静态 `atk=.12` 与独立周期 `interval=4, sp=1` 参数。`selected_talents` 已按该原资格选择天赋；当前所有模块/潜能均沿用这项第二天赋，模组没有替换它的资格。已有四岁实际数值查询使用名为「天有四时」的已选天赋，不从报告 reference 标志推断资格。

生产 Qt 根据 `OPTIONS` bool default 创建 QCheckBox，调用 `.isChecked()` 序列化当前 owner / skill。原合同调查没有找到允许 `four_sui` 非布尔文本确认编队的文档；原接口却把 `'false'`、`'unknown'`、`'0'` 等非空文本全部当作 True，从而启用原四岁攻击加成及第 060 节的周期 SP 未知边界。例如黍 S3 `base_attack=1000, window_seconds=10` 的 False 控制攻击为 1500、伤疗各 12000，文本 `'false'` 会变为攻击 1620、伤疗各 12960。

本次在原黍分支实际查询处，仅当现有选中天赋中包含「天有四时」且 `four_sui` 原始值为 `str` 时给明确 ValueError：

> four_sui 不接受文本条件；请使用布尔值。

不会裁剪、解析或把文本转换成新条件；空串、空白、`'true'`、`'1'` 同样保持文本类型并报这个输入错误。测试比较完整错误原文，而非拿结果中的某个 source/reference 标志当作应报错的依据。

真正 bool、旧数值 0/1、对应浮点、null、省略值与所有其它旧非文本结果均保持。其它 owner 的 `four_sui`、黍 E0/E1 未解锁的同名字段及已有上游培养/输入错误保持原行为。没有建立全局 boolean helper，没有同时修正 fragile/cooperative 或其它复选框。第 060 节原静态攻击参数、未知周期 SP 首跳/时钟和本体技能相对参考保持；没有补造真实编队、首跳、阻回或技能结束。

## 完整公开结果配对

`requests.json` 保留全部原 4552 个调查案例，再加入资格边界和额外原始文本：E2 level1、potential1/6、rank1/7/10、模组锁定 level59、解锁 level60 的一阶与 level90 三阶，以及培养/技能/目标数的早期错误控制，共 5189 案例。

baseline/draft 各调用公开 `calculate_damage` 一次，共 10378 次。完整 JSON 或异常类型/原文保存在 `baseline-matrix.json.gz`、`draft-matrix.json.gz`，均为无损 gzip：

- 420 个已解锁四岁原始文本输入从整份旧结果改为上述准确的 ValueError。
- 4769 个其它完整 JSON 或既有异常完全相同，其中 7 个上游原异常的类型与原文保持。
- 比较器只允许上述输入错误差异；没有剥掉数字、actual null、时钟、scope、完整性、报告或阶段字段。全部调用者输入均保持。
- 资格判定来自输入与固定原 selector，未使用输出的 `shu_periodic_sp_reference` 等标志决定是否应该报错。

原调查的文件与来源 hash 留存，不删除非文本、E0/E1、不适用、其它 checkbox 或其它技能案例来缩小范围。旧字符串兼容不等于新的全局合法输入域；本节只按明确授权收窄了这一字段的已解锁文本条件。

## 测试、合并与交接

7 项新增公共测试通过；加 64 项既有相关测试共 71 项通过，failure/error/skip 为零。相同新增测试在原基线运行：7 方法中 79 个预期失败（包含 78 个按技能/模式/文本的失败子案例和 1 个错误原文方法失败），0 error。这是原缺陷证据，单列保留在 `baseline-new-tests.*`，未计为通过或开发重复失败。

第 061 节补丁在外部 `combined061062` 上 apply-check 和实际应用通过；两节的 source hunk 分别在整数 option 与四岁查询处，没有重叠。合并包的四岁新测试、整数输入、目标数和第 060 节资源边界共 39 项通过。root 当前分支只读 apply-check 与 `cr-at-eol` 空白检查也通过。此处外部验证不是已经在 root 第 061 节提交后的 fresh 回归。

独立审查已完成，无 blocker：重新核验 693 个冻结文件、原表 SHA 和 PHASE_2 / level1 / potentialRank0 精确 selector；另跑 414 对公开小案例（828 调用），102 个文本改为准确错误、312 个完整结果/旧异常相同。独立重比较已经完成的 5189 对 gzip 全 JSON，核对 420 / 4769 / 7 统计一致，没有重跑大矩阵计算。新增 7 项与第 060 节共 20 项测试独立通过；外部合并 061/062 并包含 058/059 边界共 54 项测试通过。独立文件保存在 `independent-review/`。

补丁 `section62.patch` SHA256：`82ab295699731f83b7c6ad3caaed64e77a9c42d6e2df7e7803de870892f58200`。root 应注册 `tests.test_four_sui_text_input` 并在集成后跑当前分支相关/精选；最终公共归档列表见 `archivable-public-manifest.json`。只归档 manifest 所列公开文件，排除完整 `baseline060/`、`draft062/`、`combined061062/` 运行副本。

本节未运行 Wine/实际窗口/原生 Windows、游戏或聊天，也未读取私人状态。P2 实际机制未知仍保留。
