# 第 100 节 v2 draft 非等级增量独立 Source 审阅

结论：此次 v2 draft 的独立本局元数据运输，在 Source 层闭合了 v1 已指出的“培养 fallback 连带抹掉个人强化/招募”问题；未发现非等级增量的新 blocker。**等级 int32 小数边界仍待 Root 原 probe，当前 draft 不能视为最终 Source 合格或 Runtime-ready。** 全部项目、测试、Qt、Wine、Git、fixture codec 调用为 0；没有 repo 写入或私人读取，仅只读 Source 和仓库外本报告。

此前 v1 阻断审阅位于 `/workspace/.continuation/section100-training-view-independent-source-review-v1.md`（11045 B，`ead6cc794f5dbb1d13d937cd0e054e52df99eb4b047327442848dff47141a78b`）。它保留旧产品与真实发现，不因 fresh draft 而改成通过。

## 这次实际 draft pins

文件均相对 `/workspace/.continuation/section100-training-cache-v2/`：

| 文件 | bytes | SHA256 |
|---|---:|---|
| `candidate/rouge/training_view.py` | 5974 | `f7f8531101b9888e2cb260b1a6a947922d528f7194800999ad7b6a082b3f698a` |
| `candidate/tests/test_training_view_100.py` | 14170 | `756e35a495afe2e54799008717f4346286283166976db33094434ccfed38e661` |
| `app-current-operator-state-increment.txt` | 3131 | `0375a688bdaa7c733a3d01390a1f90f063371a5b3005cc770367252a99c65fe5` |

独立标准库 Source AST/哈希工具 `a398f0` primary 0，只确认这些读取和 AST，不能称项目或 29 方法通过。DRAFT_BINDING 明确 `AUTHOR_DRAFT_FRACTIONAL_INT32_CONVERSION_PENDING_ROOT_SUPPLEMENT`，未把它的状态当最终闭合证据。

## 非等级 Source 观察

1. 新 helper `run_operator_metadata(member,enabled=True)` 的三项资格与既有 metadata 消费门一致：开关启用、member 存在且 present 原真值、scope 恰为 run；不满足则空 dict。满足时返回原 member 只读引用，不重新校准 recruitment 或 buff schema。一个培养叶子失效不自动使独立元数据失效；账号 scope 不冒充本局事实。
2. 新 app 方法 `current_run_operator_state` 从 UI 当前选项 key 查询本局成员，再交给 helper 原门。未依赖 current_operator_state 的培养 fallback 或 opaque member id 元数据；无需为了保护 buff 重新把账号培养强标为 scope run。
3. app 增量只在 calculate 的五项个人强化/招募赋值前加入 run_state，并把这五项的元数据读取改为 run_state。原 `state=current_operator_state()` 仍用于 fields、rank 和 unconfirmed/source 标签；target-test unions、relic/config、培养数值与账号/档案预览提示保留原视图。这是建议运输文本，尚未生成/应用最终 app；Root 必须精确校核方法和五个替换范围，不能用全局 state 字符串替换。
4. `sync_target_buffs` 把原一行的 metadata state 来源换成 `current_run_operator_state`，其正向、complete 和 pending 后续读取仍在同一原局 view。这使 UI 强化状态和 calculate 来源一致，避免培养 fallback 令显示也归零；该改动不写入原 run，也不改目标测试强化选择缓存。
5. 独立 AST 比较确认 `select_training_view` 与 `format_run_training_observation` 相对 v1 完全未变。v1 其它非等级观察继续适用：先合并再资格、账号只补 fields、本局不补账号 ranks、invalid mask、锁定/无技能/未用 module stage、可信选项身份只读投影、浅层 opaque/caller 不变、None/bool 原时间行为等保留。数值等级 gate 的改变不在本报告最终资格内。
6. safe 培养仍返回账号/档案预览，scope/来源标签不因 metadata 恢复而变成“本局培养已确认”。account_training_status 仍可正确按照这个培养 state 提供账号 notice，然后追加培养 unavailable 说明；需要绑定真实已完成 97 的保存失败提示和最终 app，Source draft 并未证明 UI 显示。
7. 新四方法 Source 对应：培养 unsafe fallback 后 metadata 为原 member 且五个值 is 原值；关闭本局培养不提供 metadata；离队不提供 metadata；account scope 不提供 metadata。其公共 `public_receipt_id/public_absence/public_pending` 是 transport 占位，不是游戏表有效强化 ID；不能据这些纯 helper 测试声称真实机制/伤害数值验收。
8. 独立 AST 确认 29 个 test_ 方法。原 v1 25 控制保留，两个等级相关方法按已取得普通 float/int32 原件调整，四个 metadata 控制新增。本报告未执行任何方法，也没有真实主码/计数/截图。

## 未闭合的资格与 Root 下一步

`spinbox_level_usable` draft 采用 `int(value)` 后比较 int32。Root 原 Wine probe 已证普通 float、bool、int32端点和巨大值的结果；尚不能推导 int32 两端小数是先截整还是先原 float 比较。draft docstring 正确写待补充 probe；本报告不提前认定这段代码与真实 Qt 全边界一致。

Root 原件到达后，应 fresh 最终绑定 helper/tests/app 增量与完整实际 98/99 app/source；再次核对最终等级门、29 方法和所有已审非等级运输未被其他改动覆盖。实际项目窗口须以真实有效强化/招募 fixture 对照培养坏值 fallback、开关关闭、离队及合法混合，保留 caller/原盘 bytes、三种报告/数值和增强状态 UI；不能用四个占位 helper 控制代替这些数值/窗口检查。

构造器 evidence-only 修复可能在 UI 门之前 save 的原盘保护范围仍未被本 draft 扩展；v1 OPTIONAL 原说明保持诚实，没有载入前全局保护完成声明。任何扩展须另有真实 Source/IO 证据，不能借此包自动实现新 schema/callback 或改历史原件。

本报告仅证明指定 draft 的非等级 Source 闭合，不增加已完成小节，不代表 Runtime、Git 保存、Windows native 或第 100 节全量检验通过。
