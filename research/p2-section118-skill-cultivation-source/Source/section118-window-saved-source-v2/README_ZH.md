# 118 Saved v2：已授权方法重入计算的严格时序（Source 未执行）

Root 报告 v1 实际读回已解码并保留所有 records，但 raw1：core D 公共观察入口更新账号后立即触发 calculate，最终显式 ingress receipt 尚未写入，v1 错拿旧 current joint 比较这个中间状态。作者没有读取该失败 artifact、native 或 gzip；诊断来自 Root 消息及完整阅读的 sealed window118.py 和相关产品方法 Source。v1 sealed 包和实际失败保持原样，本包不重跑 GUI。

本包仅含 Source 候选、f040 原 helper 和精确局部 transport。Root 必须完整读新 Source 和 MANIFEST，然后对同一原实际 window artifact 执行第二 Saved 尝试。CLI 仍为 --root --guard --window --window-exit --runner --out（全新独立目录）--source-count（当前实际 map 长度）。window runner 仍严格 da217e2296d5f6347b6431010f50f8c185acb61a9a5cab127eaab295305ea30f，helper 仍严格 f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a；原完整 Source/CORE、原 raw0、receipt/metadata/records/PNG 与全字节冻结检查未改。

三个合法 interval 使用 exact runner 的实际 snapshot 作前锚，唯一最终显式 receipt 作后锚；不是仅靠 active case 名豁免。

- core D：C-continuous snapshot → actual_explicit_public_observation_ingress；中间记录的 metadata 必须是 (core, D-public-observation, intentional_public_fixture_update)。
- H：H-before-incompatible-read snapshot → actual_explicit_public_account_ingress；必须是 (H, H-new-account-mastery, intentional_public_account_observation)。
- core L：L-before-real-new-run snapshot → actual_explicit_new_run；必须是 (core, L-real-reset, explicit_user_reset)。

每类后锚唯一，前锚必须来自已存在 exact case/phase/context 的实际 window row，位置不得反转；两个锚之间只能有同 tuple 的 actual_calculate_result，其他 kind 或重叠都失败。该 protocol 合同没有预填实际计算数量；每处数量由实际 record 位序决定，也允许 Source 方法本身未发出 numerical call 的空区间。

每个 bracket 中 calculation 仍首先核整个 caller/joint 的 native before == after。中间完整 joint 必须严格等于有限阶段之一：D 只允许整体 before、账号内存和 account.json 已更新而整个 run 与其他公盘尚未改变、整体 final-after；H/L 只允许整体 before 或整体 final-after。账号先保存后 calculate、run 先保存后 UI calculate 来自已读 AccountCache.observe/save、RunState.apply/reset/save 与 MainWindow ingress/reset 方法 Source。阶段不得倒退，每条计算记录单独留下所匹配阶段与所属最终 receipt。原 helper 核类型、float 位值、dict 顺序及全容器 alias/cycle；不能靠比较任意子集通过。

interval 内的 final before 仍须等于正在跟踪的 current graph；最终 ingress/reset receipt 原 v1 的所有完整范围断言保持原字节，包括 D 的其他账号/成员/先前 history/独立强化和招募证据、公盘范围，H 的整 run 保留，L 的完整账号/其他公盘保留和原 reset 全字段合同。所有 ordinary UI、fresh API、formatter、snapshot、close/reload 检查保持严格。方法返回后后续 pure 控件可能继续沿用同 active tuple，但已在 interval 之外，仍严格与更新后的 current 完整 graph 比较。

新增 receipt 字段只描述实际 bracket 和成功匹配的重入 record，数量从实际读回派生。输出仍保留全部 compressed record 原字节、原 receipt/raw0 和两 PNG，180 秒 watchdog 不变。审计无项目/API/formatter/Qt/Wine 重执行，Source/CORE/原输入任何漂移都取消 passed。

v1 的 45 状态配方、完整 caller/result、fresh original API 对照、三全文、八取消对、六 context close/reload exactnotice、两 PNG 原字节和实际交集检查均保持原字节。technical 中间显示字符串和 non-numeric 隐藏控件 flags 未单独保存的边界继续如实说明。此包不证实原生 Windows、游戏、聊天或精0公共5–7真实肉鸽可用性。AST/compile-noexec 与九项拒绝情形的 Source 说明都不是 Runtime PASS。
