# 第 100 节最终 v2 独立 Source 审阅

结论：指定最终 v2 产品及局部 app 运输未发现新的 Source blocker。旧 v1 的“拒绝原本可安全夹取的 float、允许溢出的巨大 int”与“培养 fallback 连带丢弃独立本局强化/招募”两项问题，在此最终 Source 中已闭合。该结论不是项目、29 个测试或真实窗口通过；第 100 节仍须由 Root 精确应用并完成 Runtime 验收。本人项目/helper/test/codec/Qt/Wine/Git 执行为 0，repo 写入和私人读取为 0，仅标准库读取、AST、哈希、compile-only 与仓库外报告。

旧 v1 审阅与 v2 draft 非等级审阅保持原样，不将其旧 blocker 或当时待证小数边界改写成历史通过。此次 fresh 报告依据最终文件和 Root 已保存的真实 Qt 原件解除相应 Source 阻断。

## 实际最终版本

以下文件相对 `/workspace/.continuation/section100-training-cache-v2/`：

| 文件 | bytes | SHA256 |
|---|---:|---|
| `candidate/rouge/training_view.py` | 6050 | `5bef7b6f03592a5df615711568d116a0ffd9170f9be99832ca75d9eee78fcdb4` |
| `candidate/tests/test_training_view_100.py` | 14452 | `f5a11226278b1295acb09deec4d5596e61bb4e483ef50eeeee849e2b92981814` |
| `exact-app-local-transports.json` | 2924 | `0b6eaaa2735ea3264b1aca7e1359d9c2e075631e7002eb46c69a31e91ec28368` |
| `app-current-operator-state-increment.txt` | 3131 | `0375a688bdaa7c733a3d01390a1f90f063371a5b3005cc770367252a99c65fe5` |

独立实读的当前 `/workspace/rougezhushou/rouge/app.py` 为 99166 B，SHA256 `d1a9fe6aa89b8a24a38fd51dc72b010ed93e793c46f0d293b104c0f90b6bdcbc`。这份 app 包含此前 98 的 `member.get('fields',{})` 改动；99 未改 app。此审阅没有生成或写入最终 app，不能替 Root 宣称最终运行产品已绑定。

## 等级门与已有真实原件

独立实读两份 Root 原件：

| Root 原件 | bytes | SHA256 | 记录 |
|---|---:|---|---|
| `/workspace/.continuation/section100-qt-probe-actual-wine-v1.json` | 153770 | `093c89213681671f0f390cc4c4ff1d1878251c2b1bc650c1d2ae26419864a078` | 222 level、13 timestamp |
| `/workspace/.continuation/section100-qt-probe-fraction-actual-wine-v1.json` | 67369 | `2206388cfe1154da0117735cc955b0538ce8de4b0bcdd73e9ac17edf17d74c12` | 102 level |

原件报告 win32/Wine、PySide/Qt 6.9.3，且明确 `project_full_pass=false`、`native_windows_verified=false`。Root 原基础工具完成 `e8af6c` primary 0；补充分数工具 `7ccdd2` primary 0，均非本审阅执行。

普通有限 float、bool、int32 闭区间以及若干超出 raw int32 边界但截整仍在界内的 float，可进入原 setter 并被夹取。具体 `-2147483648.9/.5/.1` 与 `2147483647.1/.5/.9` 均无 exception；`2147483648.0/.1` 及整数端点之外则 OverflowError。None、str/list/dict 原 setter 拒绝，inf/nan/巨大值也不能安全进入。preserve_level 分支没有调用 setter，因此原记录中未消费的等级不应被当作错误。

最终 `spinbox_level_usable` 只接受 JSON 原生 int/float（含 bool），先 `int(value)`，捕获 OverflowError/ValueError，再比较 int32。Source 顺序与这些真实观察一致；不修改或归一化原 field，真实 QSpinBox 仍完成夹取。`training_view_issue` 在 `use_record_level=False` 时跳过保存等级并从校核副本移除 level，保留手动 override 下原未消费值。此门属于特定 UI binding，不能推广为游戏培养规则、任意 Python numeric 对象或所有 Qt 版本的通用资格。

`source-actual-probe-consistency-v1.json` 为 86153 B / `f0e114c81f20125185930f1787d3bde7a4d96c59ec55d9f6b0836548f5fbec97`。本审阅没有盲信其 True：标准库工具 `578b32` primary 0 独立把全部 324 行 `(receipt,input_name,elite,preserve_level)` 唯一身份及 native type 对照到真实原件，集合完全一致，并确认 13 时间记录数量。作者的 arithmetic claim 被读取，未重新执行 helper 或该作者脚本。原直接 `time.localtime` 调用仍保留 None/bool 等行为，Wine 上 -1 的 OSError 不被编造成 Linux/所有平台规则。

## 独立元数据与非等级行为

1. `run_operator_metadata` 使用旧门：本局培养开关启用、成员存在且 present 原真值、scope 恰为 run。满足时返回原成员引用；不满足返回空 dict。它不采用新的 metadata schema，也不因一个培养坏值撤销独立招募或个人强化事实。
2. `current_run_operator_state` 按 UI 当前选项 key 查询成员，不依赖培养视图 fallback 或可选 opaque id。calculate 保留安全培养 `state` 用于 fields/ranks/来源标签，仅 recruitment_kind、char_buff_ids、char_buffs_complete、char_buff_absent_ids、char_buff_pending_ids 五项读取独立 run_state；目标测试 unions 和其它 scenario 消费仍保持。sync_target_buffs 使用同一独立来源，complete/pending 与正向强化显示不再随培养 fallback 丢失。
3. 培养失败仍返回原账号参考/档案预览，未把它的 scope 强制改为 run，未宣称本局培养确认。account_training_status 先取得当前培养 state，保留账号 notice，再追加 unavailable 说明；training_view_notice 在读取前由 current_operator_state 每次设置。账号持久化提示并未被新 notice 取代。
4. `select_training_view`、`format_run_training_observation` 相对 v1 的函数 AST 完全相同。合并视图先校核、账号只补 fields、不补本局 ranks、原 invalid mask、有效原值优先、锁定/未消费 rank 和 module stage、已选择 catalog key 的只读身份投影、opaque 叶子引用、调用者不修改的原审阅结论仍适用。独立比较还确认 actual app 98 的 current/ranks 两个 comprehension 与最终 selector 中两段 AST 精确相同，包括 `.get` 和 invalid mask；它们被搬入 helper，不能误称替换后的 app 仍含原方法字节。
5. update_operator 显式传入 preserve_level，避免读取上一轮 level_override；未知已选干员的 calculate formatter 和 raw run summary 使用选项 key 只读投影，不写回存储 id。formatter保护与数值资格分开，不把能显示的 raw `elite=[]` 宣称为可供 phase 索引计算。

## 当前 app 运输与编译检查

独立标准库工具 `8707bd` primary 0 完成最终 helper、测试 Source 的 compile-only，AST 计数 29 个 test_ 方法，以及实际 app 内以下五项局部匹配：update_operator 一项、calculate 两项、sample_received 一项、sync_target_buffs 一项；每条 before 在指定方法内恰好出现一次。

当前 app 有 1567 个 CRLF；匹配及内存预览只在 Source 文本中转 LF，原 bytes 的 hash 单独保留。该预览不构成 raw byte 应用，Root 仍需按自己的运输方式保留适当换行并重新绑定最终 Source。

审阅脚本只在内存组合既定方法文本和五项局部替换，未执行产品或作者 assembler；预览 compile-only 成功。6 个原方法变化为 current_operator_state、account_training_status、update_operator、calculate、sample_received、sync_target_buffs，新增 current_run_operator_state。其它 52 个 MainWindow 方法 AST 全部不变，原类从 58 个方法变为 59 个。该结果验证运输范围及 Source 语法，不验证 Qt 控制流或全部 98/99 产品。

29 方法仅 Source 已读、已数、已编译；四个 metadata 用例中的公共占位 buff ID 只验证原引用运输，不代表实际游戏机制或数值。真实有效强化、招募、三种报告、原内存/原盘不变及开关/离队对照，仍须实际窗口验证。

独立附证：

- `/workspace/.continuation/section100-training-view-independent-final-source-audit.json`：2050 B / `6c354479282ed6b70c64582632b5a5179832c8f2e530d77e8a8c0ed1578c1b4a`。
- `/workspace/.continuation/section100-training-view-independent-final-receipt-collation.json`：3697 B / `d13e418515048c636d0fed74d2fc84e5e423c05db89f343a17a69eb50f150bb5`。

## 保留的范围限制

app 在 UI 门之前构造 AccountCache、RunState。现有 evidence-only 修复可能先 save 的原盘保护范围未被此 UI helper 扩展；原 OPTIONAL Source 说明仍诚实保留，尚无“任何坏培养叶子都在载入前无损保护”的结论，也未凭未知机制添加 schema/callback。

Root 原始 RunState/catalog repro 只证明接受特定 raw 记录、实际 catalog 计算 ValueError，不能冒充 Qt 崩溃证明。这个独立审阅不增加已完成小节，不证明 P2/P3 阶段完成、Git commit/push、Windows native 或第 100 节 Runtime PASS。Source 无 blocker 后，可继续由 Root 精确应用和实际检验。
