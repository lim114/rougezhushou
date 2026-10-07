# 人数 bool 输入只读审计（第 54 节候选）

根代理随后批准三 key 活动范围。外部草稿已完成，`changes.patch` 只含 `rouge/damage.py` 的 11 行原始 bool 守卫和新增 `tests/test_target_count_input_types.py`；保留源码 CRLF。`git apply --check` 成功，没有向 tracked 应用。根须另将 `tests.test_target_count_input_types` 加入 `scripts/verify_cloud.py` 的 MODULES（外部 draft 的 runner 已添加），在第 53 节后独立合入。

最终 11 新测试/113 相关测试通过；精选 727 运行、726 通过、1 历史跳过，0 失败/错误。成对矩阵 908 场景、前后共 1816 公开调用：826 完整结果或错误逐 JSON 哈希相同，82 变化全部为活动人数 bool 变为明确输入错误；医疗阿米娅 S2 的 False 原已范围错误，2 模式原错误字符串保持。756 个非 bool 人数场景（540 合法、216 原范围拒绝）、28 无关字段 bool、16 checkbox bool、24 其它次数 bool 的完整结果均保持；84 活动人数 bool 在草稿中全部拒绝。见 `draft-validation.json`、`matrix-before.json`、`matrix-after.json` 和 `matrix-comparison.json`。

首轮新测试夹具误读结果身份和深海色报告原始 bool 值，已按真实公开结构修正，原 4 失败/16 子错误日志保留；精选首轮外部目录缺夜刀既有公开来源回执，补只读 `research` 路径后通过，原单错误日志保留。无数值模型更改。

未修改 tracked；使用现有 checkout，当前分支 `codex/p2-development`。已读取 AGENTS、CLOUD_HANDOFF、PROJECT_PROGRESS、WORK_IN_PROGRESS 和 DEVELOPMENT_CHECKPOINT；不重复第 51 节整数培养或第 52 节有限正生命周期调度。

## 公开复现结果

执行：

```text
cd /workspace/rougezhushou
.venv/bin/python /workspace/.continuation/p2-after-051/target-bool/reproduce.py
```

15 个支持技能 × 2 时序模式 × 2 个 bool 共 60 个 bool/整数配对；连同 8 个真实 bool 选项控制共 128 次公开 `rouge.damage.calculate_damage` 调用。58 个 bool 调用获接受，2 个医疗阿米娅 S2 的 `amiya_hit_targets=False` 因转换后的数值 0 受到既有范围拒绝。所有 60 对完整输出以规范 JSON 逐字节一致；全部公开输入未变，6 个审计源码/数据哈希未变。

| 输入（frames，base_attack=1000） | False 当前行为 | True 当前行为 |
| --- | --- | --- |
| 桃金娘 S2 `healing_targets` | 等同整数 0，总治疗 0 | 等同整数 1，总治疗 8000 |
| 遥 S1 E2/60/BLS-Y 一级/window10 `healing_targets` | 等同整数 0，窗口治疗 0 | 等同整数 1，窗口治疗 6750 |
| 医疗阿米娅 S2/window10 `amiya_hit_targets` | 等同整数 0，范围错误 | 等同整数 1，声明命中 1、后续攻击参考 1300，完整伤害与治疗仍 unknown |
| 伊内丝 S2/window10 `stolen_enemy_count` | 等同整数 0，攻击 2100、伤害 29400 | 等同整数 1，攻击 2190、伤害 30660 |

`public-pairs.json` 含每对摘要、输入未变检查、结果 SHA256、源码前后 SHA256；`public-results.json` 保留全部原始公开输出；`reproduce.py` 可重新运行。不要在根合入修复后覆盖本次修复前回执。

## 原因与既有资格

`rouge/operator_engine.py:136–143` 的 `Combat.value/option` 在检查整数前执行 `float(value)`；`bool` 已被转成 0.0/1.0。适用调用在 200（伊内丝）、308（治疗人数）、479–480（医疗阿米娅 S2）。旧三干员引擎通过 `rouge/estimate.py:17–26` 的 `nonnegative` 完成同样转换。因此只修 `Combat.value` 会漏掉旧路径。

| 参数 | GUI 控件资格 | 后端既有数值资格 |
| --- | --- | --- |
| `healing_targets` | `rouge/app.py:563–565` QSpinBox 默认 1，0–100；957–959 使用 `reporting.has_healing` 可见资格；978–985 按技能/模组上限 | 两引擎 0–100；超过技能上限的声明仍按既有模型参考处理 |
| `amiya_hit_targets` | `operator_options.py:13`，仅医疗阿米娅 S2；`app.py:669–670` 默认 1，1–100 | 1–100，整数 0 仍明确不支持 |
| `stolen_enemy_count` | `operator_options.py:19`，仅伊内丝 S1/2/3；`app.py:669` 默认 1，0–100 | 0–100；整数 0 表示未声明既有偷攻来源 |

当前公开资料不证明任何实际友方获取、相位、真实人数或叠加机制；本审计只涉及数字输入资格。`source-receipt.json` 重用第 47/49/39 节已有来源，并重新核对固定 `character_table/skill_table` SHA256。原表伊内丝精二潜能 1 单目标偷攻参数为 90，医疗阿米娅叠层参数为 0.3、上限 5；不新增机制推断。

## 已批准并用于外部 draft 的最窄范围

在公开 `_prepare_damage`（`rouge/damage.py:235`）完成已有技能/rank/培养可用性校验后、所有数值转换前，只拒绝原始 bool：

1. `healing_targets`：仅现有 `reporting.has_healing(operator, skill)` 可见技能。
2. `amiya_hit_targets`：仅 `char_1037_amiya3` S2。
3. `stolen_enemy_count`：仅 `char_4087_ines` 三技能。

明确保留数字 0、各自当前范围、默认值，以及已支持的整数浮点/数字字符串输入；未适用字段不新增拒绝。保留真实 checkbox：`low_cost_healing_target`、`haruka_repeat`、`frozen_at_skill_end`、`ines_first_deployment` 的 False/True（本次 8 调用均接受且输入未变）。

不要全局收紧 `Combat.value(integer=True)`：那会影响 27 个独立 key，除上述三 key 还新增 24 个参数的拒绝。后续若另审事件次数，单独明确范围。

## 已有测试与验证

```text
.venv/bin/python -m unittest tests.test_amiya_input_qualification tests.test_myrtle_healing_targets tests.test_haruka_healing_targets tests.test_ines_dot_reference -v
```

33 项运行、33 通过、0 跳过、0 错误/失败。日志 `existing-tests.log`。三 key 没有 bool 测试；现有保护包括：

- `test_amiya_input_qualification.py:9–45` 的 0/负数/.5/101/NaN/Inf、有效 1/5/100、默认 1 与不改输入。
- `test_myrtle_healing_targets.py:13–30` 的合法 0/1/2/100。
- `test_haruka_healing_targets.py:26–82` 的人数/rank/module、第三份未知及零声明。
- `test_ines_dot_reference.py:57–60` 的合法 `stolen_enemy_count=0`。

建议新测试同时覆盖两引擎、双时序、两 bool、适用与未适用字段、数字 0 与原默认，且验证坏输入未改调用者 dict。有效数字与现有 unknown/时钟的整份公开输出要保持。

本次只读源码/GUI 控件检查及 Linux 公开计算；没有运行 GUI、Wine 或原生 Windows，不声称实际界面/客户端验证。
