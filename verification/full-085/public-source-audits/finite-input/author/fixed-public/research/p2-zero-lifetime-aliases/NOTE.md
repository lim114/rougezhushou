# 第 56 节：已验证零生命周期字符串归一化

最终件以干净第 55 节提交 `15e0fa455aad05d27303428299d24d15db4c572c` 的独立 gitarchive 为基线。所有草稿、测试与回执仅写外部持久目录；未修改 tracked。根代理已告知第 55 节全量与实际 GUI 完成，待其归档后独立合入本补丁。

`section56.patch` 包含四个文件：

- `rouge/damage.py`：公共 `_prepare_damage` 末端新增 7 行。仅该 timing 字段原始类型为 str 时，先以既有 `AttackTimeline` 验证完整原始时序，再用既有 `finite(...,3600)`；值严格等于 0 才建立内部 timing 副本并替为数字 0。保留源码 CRLF。
- `tests/test_zero_lifetime_aliases.py`：10 项公开边界测试，含 87 技能、双模式完整结果比较。
- `tests/test_amiya_continuous_lifetime.py`：仅更新第 52 节未闭合的字符串零测试，改为三种别名与原数字零结果完全同、伤害 0、自然回充 30/周期 60/初动 7，以及不生成正约束未知引用；其余正生命周期、范围及零观察保护不变。
- `scripts/verify_cloud.py`：登记新测试模块。

`git apply --check section56.patch` 已成功。不要以完整旧 snapshot 文件覆盖根目录，只合入补丁 hunks。

## 当前验证

104 项相关测试通过。精选 777 运行、776 通过、1 历史跳过，0 失败/错误，见 `related-tests-055.log`、`cloud-tests-055.log` 与 `draft-validation-055.json`。

前后矩阵共 2,216 次真实公开 API 调用：

- 87 技能、双模式、数字 0 / `"0"` / `"0.0"` / `"-0"` 各侧 696 调用；另各侧 64 手动来源调用。
- 570 个字符串零配对全部与各自数字零的完整结果 JSON 完全同。原有 190 个数字零场景完整结果保持；393 个旧字符串零结果得到修正，177 个原等值场景保持。
- 非零字符串/数值、极小正字符串、非法与布尔输入、其它时序字符串字段、只在 units 中给零字符串等 348 场景，各侧 348 调用；全部完整结果或原错误保持。
- 全部 caller 输入未变，两个矩阵执行前后的源码哈希未变。

总比较见 `public-comparison-055.json`。原始完整结果与逐项摘要在 `audit-before-055`、`audit-draft-055`；非零/非法等控制在 `controls-before-055.json`、`controls-after-055.json`。`audit_zero.py`、`capture_controls.py` 可重放。

## 来源与边界

重用第 40 节 `research/p2-empty-enemy-scope/source-receipt.json` 的数学空源、友方独立治疗、即时/未定位来源和部署初动分离契约，并重新核对固定 character/skill 表 SHA256，详见 `source-receipt.json`。字符串数字原已被 `timing.finite` 接受；其 bool 在 float 转换前被明确拒绝。本节只统一等值零的入口表示，不新增实际获取、叠加、有限正生命周期或原生事件相位。

公共参数的数字零既有分支继续决定友方治疗、医疗弹药友方 fallback、伤转疗、即时伤害、独立条件量、SP 与初动。未修改 `AttackTimeline` 的来源门禁、任何非零时序值或嵌套 units 覆盖。

## 历史证据区别

`audit-051` 与 `closure-audit-051.json` 是原第 51 节发现：760 调用，31 个 frames /79 个 continuous 技能的数值摘要出现等值零分歧；不能当作最终整合验收。

`draft-052`、`baseline-052` 及其日志是在 HEAD 52、根正 staging 53 时抓取的过渡快照，准确字节由 `draft-freeze-052.json` 描述。首次精选因旧第 52 节字符串零测试期待 unknown 引用而出错；更新该测试时首次补丁还留有两行旧 None 断言，第二日志显示矛盾，随后移除已被 30/60 明确断言替代的旧断言，29 项新/阿米娅定向测试通过。两份失败日志原样保留；没有把它们记为通过。最终验证使用新的干净第 55 节 gitarchive 与完整语义更新，777 项已通过。

本子代理未执行 GUI、Wine、原生 Windows、游戏或桌面集成。第 55 节根代理的全量与实际窗口结果由根独立归档；本回执只证明外部第 56 节 Linux 草稿。
