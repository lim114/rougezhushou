# 第 100 节培养视图 v1 独立 Source 审阅

结论：当前实际 v1 **存在阻断，不能作为最终产品或已完成安全门**。已发现两项需要 fresh 修订后重新审查的边界：真实 Qt 接收的安全浮点等级被 v1 拒绝、真实会溢出的巨大整数被 v1 全部接受；培养 fallback 同时丢掉独立有效的本局招募/个人强化元数据。后者为确定 Source 数据流问题，尚未项目复现。其余已审 consumer/混合/未消费字段范围未发现另一项新增 blocker，但不代表实际验收通过。

本审阅只读公开 Source、既存 Root 原始公开观察 JSON 和标准库 AST/哈希；没有运行项目、candidate、tests、fixture codec、Qt、Wine、Git 或私人状态，也没有修改 repo。Root probe 的真实结果属于 Root，本报告读取结果不冒充自己运行的证据。

## 实际版本绑定

| 文件（位于 `/workspace/.continuation/`，除特别注明） | bytes | SHA256 |
|---|---:|---|
| `section100-training-cache-v1/candidate/rouge/training_view.py` | 5126 | `d2eb94cace489a9837fdc6e5811fccf4bbc86737ebacfdc89c8c03debf24e176` |
| `section100-training-cache-v1/candidate/tests/test_training_view_100.py` | 12651 | `94cec66350a456272bc97bbf102444b1a4d0a2ce61b689c6c18fb236af1dd5b9` |
| `section100-training-cache-v1/app-current-operator-state-increment.txt` | 2086 | `0c22ed7f51fcd8c3d115971fd7e27fbc2badb973bfe84df96f94415fb407c55b` |
| `section100-training-cache-v1/OPTIONAL_ORIGINAL_PROTECTION_SOURCE_NOTE.md` | 2488 | `5b3927c501052204fa2574d01f6145a1bbea2b27af6ccaa628e2c986d6b09eff` |
| `section100-qt-probe-actual-wine-v1.json`（Root 原件） | 153770 | `093c89213681671f0f390cc4c4ff1d1878251c2b1bc650c1d2ae26419864a078` |
| `resume099-100-original-reproduction-v1.json`（Root 原件） | 835 | `bd54d399e55a506fc36edd507700cd7e23b1e50106a5bc44588f4d08f4e3d659` |
| 实际 `/workspace/rougezhushou/rouge/app.py` | 99159 | `0c388853b351e3869a01f32f42058fc8e0a0cb23fc67f25d6141bde13350423d` |
| 实际 `/workspace/rougezhushou/rouge/account_cache.py` | 10398 | `17250d93fa3932fc6233bc5b8dd8d1a17d76a283feee5fe694ffebe530ecb5d5` |
| 实际 `/workspace/rougezhushou/rouge/catalog.py` | 3404 | `92acb14e3235b06eb48556bb40d0c04e7519674f7233c15a9c5169c5beea2bb2` |
| 实际 `/workspace/rougezhushou/rouge/operator_summary.py` | 3541 | `d1a6c6c70265835bbe804e15bca1e17ee2d7705f543490e965fe794f8b5a29cf` |

标准库 Source AST/哈希检查 chunk `30ceab` 返回 0，仅确认本次读取 pins 和 25 方法可解析；不是方法执行或测试通过。旧 `source-binding.json` 中还存在 helper 4192 B、测试 10608 B、app increment 1359 B 的历史 pins，不能把它们当当前 5126/12651/2086 B 的绑定。最终应用仍须以实际完成 98/99 的 Source 重新绑定，不覆盖 Root/同伴的新代码。

## 阻断 1：等级类型与真实 setter 不一致

v1 helper 只在 `isinstance(level,int)` 为真时接受保存等级，并称非整数 JSON 不能交给 setValue(int)。Root 实际 Wine 原件（win32 / PySide6 6.9.3 / Qt 6.9.3，状态为独立原输入观察，不是项目验收）已经记录：0.0、1.0、1.5、-1.5、90.5、91.9 都没有 setter 异常并按原控件转换/范围夹取；bool 也安全。因此拒绝所有 float 会改变已证的原安全行为。原测试 `test_non_integer_level_is_not_sent_to_set_value` 把 80.0 列为拒绝项，也须随依据修订，不能为了旧断言硬改产品行为。

同一 Root 原件明确 int32 闭区间端点可接受，int32 越界、巨大整数抛 OverflowError；v1 目前接受全部 int，因此未解决这一真实风险。它不能把阶段 maximum 的原控件夹取范围当 Qt 参数转换的无限安全范围。

Root 及作者正在进一步观察 int32 边界附近小数的截整/检查顺序。当前不能从 1.5 等普通值猜 ±2^31 附近的接受条件，也不能把 Source probe 的主码 0说成每个值都成功。本审阅未运行 probe。新门必须保留明确已经安全的原生类型/值和 preserve_level=True 的不消费分支，再按真实观察限定确实会抛错的 setter 输入。

## 阻断 2：培养 fallback 丢失独立本局元数据

当 combined 与 run_only 的培养输入都不可用，v1 `select_training_view` 返回 account 原视图，selection 为 `account_after_unusable_run`，scope 通常非 run。实际 `app.py:1083–1088` 的 calculate 从 current_operator_state 读取 recruitment_kind、char_buff_ids、char_buffs_complete、char_buff_absent_ids、char_buff_pending_ids，且每项仅在 scope == run 时使用。于是一个精英阶段坏叶子会令本来独立有效的招募来源/个人强化事实一并归空，继而可能改变计算。培养坏值不证明这些独立元数据也失效。

两条可能的最小运输方向：

- 保持培养 fallback 的 safe account/档案预览投影和清楚来源标签，把 scenario 的本局元数据独立从当前原 run 成员读取，遵守 use_run_training、present、scope == run 等原有门。这样不需为了个人强化把 account 培养重新标成 run 培养，提示风险较小。
- 如果选择在 fallback 投影中保留本局元数据，则必须明确仅由本局记录提供 metadata，fields/ranks 为 safe account/预览、run_confirmed_fields 为空；同步修正 update_operator 和 account_training_status 文字，不能把仅 metadata 的 run scope 误说成本局培养已确认，也不能把账号元数据当本局强化。

这是建议而非已实现方案。不要借培养可靠性新增未经依据的强化 schema；保留既有领取、完整性、离队及生命周期语义。Root 应对新方向单独 Source 审查和实际数值/文本对照。当前 v1 没有完成这一运输。

## 其余 consumer 边界的 Source 观察

1. 原 current_operator_state 账号只补 fields、本局 fields 覆盖且 skill_ranks 不补账号；候选保留同样顺序。先资格 combined 再资格 run_only 很关键：账号 E0 能使本局技能 3 的 99 成为原来安全的锁定/formatter-only 值，不能按本局默认 E2 先拒绝。账号 E1 + 本局 rank 8 的混合不安全时，run-only 默认 E2 可以独立安全，去掉账号补足整组且明示预览是有现有 consumer 依据的 fallback。
2. current/ranks 的过滤保持原 invalid_fields/invalid_skill_ranks 的实际键比较，masked 值不构成新增拒绝。JSON 持久读入的 member 和容器资格仍依赖最终 98 guard；helper 不是任意输入的完整 RunState schema。
3. checked 的 id 使用可信 UI 当前 op，只用于 `_record_issue` 的政策查询，不写回结果/原 member。已实现 operator_attributes/scenario 使用 UI op，没有消费可选 member id；未实现 calculate formatter 和原 run formatter 确实消费 id，所以两处只读投影 `{**state,'id':op}` 有明确 consumer 依据。原 member id 可缺失或 opaque，不应擅自修写原记录。
4. `_record_issue` 对选定 profile 的 elite、trust、potential、truthy module identity/level 和活动技能等级，有既有 catalog/formatter/indexing 来源；不改数值模型。锁定等级 None/bool/0/负数/1.0/99、无技能档案未消费 rank、未知技能键和 selected_skill 非选项偏好保持原型，不被套上账户专属 schema。
5. falsy module_id 的阶段原值不影响 operator_attributes 的 module 分支；UI 原标签会字符串显示，所以 unused stage dict/list 不应拒绝。合法 truthy module 仍由既有表匹配且阶段资格保留，实际 unlock 的原行为不被提前推算。
6. 保存 level 在 preserve_level=True 时不会由 update_operator 调 setter，training_conditions 读取 widget 的实际整数；候选需要两个配套变动：current_operator_state 参数和 update_operator 显式传 preserve_level，不能只改前者。未消费坏保存 level 不应使其它安全 run 事实失效。
7. 时间资格直接做原 `strftime(localtime(...))`，不转换字符串、不强制数值 schema；None 默认当前时间、bool 是原可接受值。实际 Wine -1 OSError 属平台真实差异；本候选不把 Linux 与 Wine 转换行为混称原生 Windows 验收。实际 caller 时间对象和原记录未改。
8. raw run summary helper 只试实际 formatter，不套计算数值门。格式化时未知/列表精英文本可原样安全显示，与精英作为阶段索引的数值路径不同。已处理 KeyError/TypeError/ValueError/OverflowError 形成明确 unavailable 提示；没有 reset/save/目录/文件写入。缺失 id/opaque id 通过可信选项只读投影，rank 类型错误用明确暂不可显示提示，而非伪造正常文本。
9. helper 对 records 采用浅层外壳与 fields/ranks 副本；没有对 caller 原字典 pop/update，没有递归规范化 opaque extra。25 测试中 choose 的 deepcopy 前后断言及个别 is 原引用断言是计划中的 caller 检查，尚未执行。NaN 用 is 单独检查而非错误使用 NaN equality。
10. 新 account_training_status 先 current_operator_state 得到当前选择，再保留 account_cache.notice 并追加视图 notice。它不应抹去 97 保存失败说明；最终 97/99 的实际 Source 绑定及 UI 仍待验证。当前第 2 阻断修订时要再次检查 confirmed 文字是否准确，不能仅由恢复 run scope 自动宣称培养可用。

## 构造器原件保护与证据诚实性

实际 MainWindow 先 AccountCache、再 RunState，再构造 UI。最终 98/99 的 RunState 构造仍在 UI helper 之前安装 saved、执行既有 evidence-only 修复，修复返回 True 时可以 save。因此本节 UI fallback 不提供“所有培养坏叶子在载入前原文件已保护”的保证。候选的 OPTIONAL 原件说明诚实保留了这一点，并提出组合已有修复 fixture 与不安全培养叶子的最小 Root 复现；这不是已实际发生的自动覆盖缺陷，也不是已授权/已应用的额外 callback 实现。

Root `resume099-100-original-reproduction-v1.json` 原件只有：RunState 接受 elite=[]，实际 catalog API 以其既有 guard 抛 ValueError；范围明确为 Linux RunState/catalog API，实际 Qt consumption 尚未验证。它不能证明 MainWindow/Qt TypeError，更不能据此伪造崩溃截图或本节修复通过。

构造期原文件保护若未新增实际覆盖，完成报告必须继续留缺口；混合冲突也不能把两个分别安全的文件误判损坏。当前 v1 没有写入、修复、手动重置或迁移任何原记录；scope 不应扩成无证据全局 schema。

## 后续交接

这份 v1 审阅已将上述阻断直接发 Root 和 `/root/section100_training_cache_audit`。需要 fresh v2 绑定与审阅，不能覆盖或将旧 v1 重新贴为最终通过。25 方法只经 Source 解析，未运行；真实 Qt probe、项目界面、旧安全输入对照、三种报告/计算以及原件 IO 均由 Root 负责实际记录。实际全量和原生 Windows 状态各自保留，本报告不提前计完成或提交推送。
