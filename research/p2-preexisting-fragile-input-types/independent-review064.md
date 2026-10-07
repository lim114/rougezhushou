# 第 64 节独立来源、补丁与公开 API 审查

结论：无未解决 blocker，可以由 root 在第 63 节后集成。本审查不修改 tracked 文件，只使用作者从精确已提交 section 60 `c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf` 取得的外部 baseline，不冻结当前 root 工作区。

## 来源和代码边界

独立重新哈希 character/skill 原字节及本节下载的 gamedata_const.json，均与固定原表 commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add` 的回执相等。独立对照全三技能 30 rank 的原描述、黑板数值、持续参数与技能解锁门槛。

`silverash` 为 `char_1045_svash2`，S3 条件倍率来自所选技能 rank：1–3 为 1.15，4–6 为 1.2，7–9 为 1.25，10 为 1.3。9 个精英/潜能原具名天赋选择均无 damage_scale；原技能来源没有转移至基础天赋。现有 177 个 native 文本证据文件的当前哈希与作者精准搜索回执一致，缺少本技能实际附着证据的限制保留。

原常量脆弱术语覆盖物理、法术、真实伤害并注明「同名效果取最高」。该术语不授权把任意手工 damage_taken 与本技能判为同名来源，也不证明第一次命中先后、刷新、快照、残留、模板或热更新。本节没有修改这些公式或补原生机制。

独立验证外部冻结全部 2,167 个公开文件完整。将 actual draft damage.py 的新增两行 guard 精确移除后，整文件原字节与 baseline 相等；所有伤害公式、来源、倍数、资格、时钟与报告原代码均未变。guard 在已有 skill/rank、培养与技能开放条件校验之后，仅实际使用 preexisting_fragile 的 silverash S3 拒绝原字符串，不解释文字布尔。

## 独立验证

新执行 77 对公开场景 / 154 次 calculate_damage，记录完整结果与错误：

- 22 个 active 字符串改为明确 ValueError，包括 false/true/数字文字/空串/空白/unknown，以及零观察窗口、零敌方生命和空供靶。
- 46 个完整结果保持：bool、null、数值 0/1、浮点 0/1/负零、缺省，rank 分段、协同与手工 physical 来源，以及 inactive 其它技能/干员两模式控制。
- 9 个原错误保持：精零/精一未开放 S3、bool skill/rank/elite、错误 rank 类型/范围以及 bool level/potential 仍先返回原资格或类型错误。
- 请求、缓存 catalog 和实际源码起止哈希保持，无未解释差异。

独立重跑作者新增 7 个测试方法全部通过；不是重复作者 73 个 related 方法的整套回归。

另对作者已经执行并保存的 976 对完整结果做严格重新比较，重新计算每份完整 JSON 的记录哈希：50 个 active 字符串 ValueError、866 个成功结果整份 JSON 相同、60 个原资格错误类型和文字相同，0 差异。该比较没有再次执行原 1,952 次公开调用，不把它们计入本次 154 个新调用。

已审阅原测试 initial failure：legacy continuous target_windows=[] 的旧 math 不保证零伤害，该误期望已改为原完整输出保持；零窗口/零生命周期原 0 行为另外核验。未借此扩展范围或声称实际命中。

## 成品版本和剩余未知

- patch SHA256：`d29ce484137dba8c3887e19126dd5f2c453a842d140b61e87d1b6cd777a72222`
- actual draft damage.py SHA256：`8d6bab09813a74d2d28973a21195877f26e6da3ff011e1914512c91c3216c160`
- 完整独立来源：independent-source064.json。
- 77 对输入/结果和日志：independent-baseline064.json/log、independent-draft064.json/log、independent-probe064.py。
- 精确数量和作者结果再比较：independent-comparison064.json。
- 新增测试日志：independent-new-tests064.log。

GUI 既有 QCheckBox 使用 isChecked() 产生 bool，静态 producer 与两行输入 guard 相容。本审查没有执行 GUI、Wine、原生 Windows 或游戏；正式集成、新 runner 注册和每五节的全量及实际窗口检查由 root 完成。实际脆弱来源身份/叠加实例、首次施加及生命周期仍显式未知。
