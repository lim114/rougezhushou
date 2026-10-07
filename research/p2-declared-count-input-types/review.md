# 第 57 候选：legacy 声明计数输入类型独立审计

2026-10-07，只读审计生产 checkout 与外部第 53 草稿；仅在本外部目录写证据。开始时 production HEAD 为 `fba536e118906f58ed2bcef359480f76e0ae4d67`（第 51 节 `fix: reject boolean cultivation values before calculation`），分支 `codex/p2-development`，工作目录 clean。第 53/54/55 尚未按本次证据集成；不能把外部 snapshot 当作 production HEAD。

结论：四个生效计数入口都将 raw bool 作为 0/1 接收。最窄修复是在公开 `_prepare_damage` 中，技能/rank/培养及技能开放资格已验证之后，`prepare_run` / `relics.prepare` / 两引擎路径之前，按 operator + skill 精确映射拒绝生效字段的 raw bool。保留旧字符串、整数浮点、范围、闲置字段及错误优先级；不要引入事件相位或数值上限推断。第 53 草稿新增的破屏字符串回归应在第 53 独立修复，不混入第 57 bool 修复。

## 当前实际接收路径

`rouge/damage.py::_prepare_damage` 把 scenario 复制，但不验证四个计数。legacy `_skill_damage_base` 再复制 scenario，先对 `activation_count / deployment_stacks / shield_break_count / charge_count` 全局执行 `float(raw)`，检查有限、整数、非负（deployment 另限 2），随后 `int(value)`。这次转换只更新该局部副本，没有传播回 `_prepare_damage` 的 scenario。后续 `finish_charge_reference`，以及第 53 草稿的 `finish_shield_break_reference`，重新读取原始 scenario。

| 生效范围 | 字段 | 省略默认 | 当前 API 数值范围 |
| --- | --- | --- | --- |
| mechanist S2 | shield_break_count | 0 | 有限非负整数，未设上限 |
| mechanist S3 | charge_count | 0 | 有限非负整数，未设上限 |
| silverash S2 | activation_count | 1 | 有限非负整数，未设上限 |
| silverash S2 | deployment_stacks | 0 | 0–2 整数 |

四字段都接受整数浮点 `1.0 / 2.0`，拒绝 `1.5 / -1 / nan / inf`。`None` 在现有 `float(None)` 路径为 TypeError，空字符串或普通文字为 ValueError。不要为了 bool 修复改变这些错误或转换规则。

字符串具有 field-specific 公开行为：

| 生效字段 | `"1"` | `"1.0"` / `"1e0"` | 当前根与第 53 草稿差异 |
| --- | --- | --- | --- |
| shield_break_count | 接受 | 第 51 接受 | 第 53 新 finisher 的 `int(raw_string)` 拒绝小数/指数数字字符串 |
| charge_count | 接受 | 拒绝 | 两者均被既有 `finish_charge_reference` 的 `int(raw_string)` 拒绝 |
| activation_count | 接受 | 接受 | 两者相同 |
| deployment_stacks | 接受（限 2） | 接受（限 2） | 两者相同 |

GUI 的前三字段 QSpinBox 范围 0–100，部署叠层范围 0–2。前三者的 UI 上限不等于当前公开 API 上限。本次另执行 8 个公开边界探针：shield/charge/activation 的 100 与 101 均接受，deployment 的 100 与 101 都保持既有字段 ValueError。没有充分来源要求在 bool 修复中新增 API 上限 100。

## 公开复现与闲置隔离

`independent_public_probe.py` 在两独立 Python 进程分别加载 production 第 51 package 与 `/workspace/.continuation/p2-after-051/shield-draft`，只调用公开 `calculate_damage`，不注入私有字段。每个 package 执行 536 调用：176 个生效字段/类型案例与 360 个闲置字段案例。全部请求保持不变；两个 artifact 记录各 package 代码哈希、观测 production HEAD 和 UTC 时间。结果摘要中的组件是投影，未出现字段经 `.get()` 表示为 null；不能据此推断原结果存在 `actual_total`。

共同基础请求：

```json
{"operator":"mechanist","skill":2,"skill_rank":10,"elite":2,"base_attack":1000,"companion_attack":1000,"window_seconds":10,"timing_mode":"frames","shield_break_count":true}
```

将 operator/skill/field 按上表替换即可覆盖四入口。`companion_attack=1000` 避免 silverash 部署叠层的受益攻击缺失错误。两模式的 false/true 共 16 个生效 bool 案例，在第 51 与第 53 草稿都接受，且完整结果 SHA256 均与对应整数 0/1 一致。

第 51 frames 顶层现有数值示例（仅复现当前实现，不声明实际事件已核验）：

| 输入 | false | true |
| --- | --- | --- |
| mechanist S2 shield_break_count | 0 | 5000 |
| mechanist S3 charge_count | 19760（轰击） | 31160（另含11400冲锋条件量） |
| silverash S2 activation_count | 0 | 3800 |
| silverash S2 deployment_stacks | 3800（本体默认一次） | 7600（另含3800受益者量） |

第 53 将正破屏实际总量转为 unknown、保留条件参考，不关闭 bool 接收。其余三字段行为保持。

闲置 bool 144 个案例均接受，且每个 package 内与相同技能省略该字段的完整结果一致。覆盖三 legacy aliases 的所有技能与 extended Susuro S1；生效字段已从闲置集合排除。值得保留的非 bool 既有差别：legacy 即使字段闲置仍执行旧全局计数验证，故闲置 `"x"` 拒绝、闲置 deployment=3 拒绝；extended Susuro 忽略这些字段。最窄 bool 修复应保持这套原行为，不以“隔离”为由顺便全跳过旧验证或全局新增拒绝面。

## 第 53 新字符串回归必须独立修复

同一公开请求 `mechanist S2 + shield_break_count="1.0"`：第 51 接受，顶层 5000；第 53 草稿报 `ValueError: invalid literal for int() with base 10: '1.0'`。`"0" / "1" / 1.0` 仍接受，`"0.0" / "1.0" / "2.0" / "1e0"` 会经过 legacy float 验证后在新 finisher 出错。建议仅把第 53 finisher 的重新读计数改为 `int(float(scenario.get('shield_break_count', 0)))`，复用先前公开核心已完成的有限/整数/非负验证；添加公开数字字符串与同数值 integer/float 成对回归。不要借此修复既有 charge 字符串错误或改变第 57 范围。

## 最窄 raw bool guard 建议

```python
declared_count_fields = {
    ('mechanist', 2): ('shield_break_count',),
    ('mechanist', 3): ('charge_count',),
    ('silverash', 2): ('activation_count', 'deployment_stacks'),
}.get((scenario['operator'], skill), ())
for field in declared_count_fields:
    if isinstance(scenario.get(field), bool):
        raise ValueError(f'{field} 需要非负整数；部署触发叠层最多为 2。')
```

放在 `_prepare_damage` 现有技能开放判断之后，与第 54 同类公开 raw bool 入口检查并列。不要在这段做 float/int 归一化，不改变字段省略默认，也不验证闲置字段。采用现有计数错误文本可保持其兼容约定；虽该通用文本对非 deployment 字段也提叠层，改文案属于额外范围。本审计没有实现 guard。

有意义的回归应覆盖：四 active fields × false/true × 两模式；同整数 0/1 保持；省略默认；integer float 与 field-specific numeric string；已有范围/非有限错误；inactive legacy/extended bool结果保持；输入/catalog不变；非法skill/rank/培养优先于计数 bool。正/零观察或目标生命周期不应被新增 bool guard 用来推断真实事件时钟。

## 已有固定来源及其限度

复用 `Kengxxiao/ArknightsGameData` commit `a550f5e048bb94e7cdefc6eb97a4091f0c4c7add`。本次重新哈希并读取 `.cache/p2-s1-binding/character_table.json`（SHA256 `68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697`，14975251字节）及 `skill_table.json`（SHA256 `86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca`，11447929字节）。完整三个精确 selector 的原文存于 `independent-source-facts.json`。

- `character_table.char_4230_mcnist.skills[1]` → `skill_table.skchr_mcnist_2.levels[9]`：自身与结构性原理获屏障，摧毁时条件法伤，rank10 atk=1.5、atk_scale=2、弹药参数8，可手停。第 53 外部 `research/p2-shield-break-reference/source-receipt.json` / NOTE 记录本体与结构性原理的总次数归属、双方耗弹及结束顺序尚未闭合。弹药8不能成为给定总破屏次数的已确认上限，故本次不收紧。
- `character_table.char_4230_mcnist.skills[2]` → `skill_table.skchr_mcnist_3.levels[9]`：冲锋碰到敌人或高台时条件物伤并停，rank10 atk=2.8、atk_scale=3、轰击 attack@atk_scale=2.6。现有 `research/p2-charge-clock/source-receipt.json` 明确：给定情景次数支持线性条件量，不能证明碰撞时刻或完整技能次数；本体0.8秒延迟不能用于冲锋。不给 charge_count 新造每技能/每窗口上限或事件时刻。
- `character_table.char_1045_svash2.skills[1]` → `skill_table.skchr_svash2_2.levels[9]`：本体技能范围物伤、受益干员部署时以自身攻击力施放一次范围效果，最多叠加2次；rank10 atk_scale=3.8、max_stack_cnt=2。该原文支持当前 deployment_stacks≤2 和 companion_attack 路径；“可充能2次”不证明任意情景中的 activation_count≤2。现有 raw 记录也见 `research/p2-empty-enemy-scope/source-receipt.json`。本次不推断本体/受益者回调、施放phase、获取时钟或事件归属。

本次没有网络请求、tracked 修改、UI/Wine/native Windows/游戏或私人状态验证。测试属于公开输入实现观察，不能当作 native 机制合法性证据。尝试将来源工作分派子代理被 thread limit 拒绝，随后由本代理独立完成。

复现命令：

```bash
/workspace/rougezhushou/.venv/bin/python -B /workspace/.continuation/p2-declared-count-types/independent_public_probe.py /workspace/rougezhushou /workspace/.continuation/p2-declared-count-types/independent-root51-results.json
/workspace/rougezhushou/.venv/bin/python -B /workspace/.continuation/p2-declared-count-types/independent_public_probe.py /workspace/.continuation/p2-after-051/shield-draft /workspace/.continuation/p2-declared-count-types/independent-draft53-results.json
```

之后重跑 production 命令可能命中父代理已推进的新 HEAD；必须保留/核对新 artifact 的 head 与代码哈希，不继续将其称为第 51 基线。
