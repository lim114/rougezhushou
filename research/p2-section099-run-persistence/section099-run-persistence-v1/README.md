# 第 99 节本局保存连续性候选

这是仓库外 Source 准备包，不是已完成的小节。没有导入或运行项目、测试、候选、窗口、Wine、Git 或 fixture codec；没有修改仓库。Root 必须先完成第 98 节，再以真实字节校核、应用、实际检验、归档及提交推送。本包不把此前 full095 搁置改成 PASS。

## 真实问题及最小增量

当前实际 `RunState.apply()` 在合并本局内存并更新 `last_read` 后才 `save()`；原保存 IO 异常会跳过 `app.apply_run_observation()` 后续的队伍、本局摘要、培养与计算刷新。手动 `reset_run()` 先增加采样 epoch、丢弃待处理帧、安装新局，再保存，异常同样会截断后续 UI 清理。构造函数把迁移后保存放在读取的 try 内，保存的 IO/编码错误可能误报为“原本局记录无法读取”。

精确候选以第 98 节 Source 的 `run_state.py` 为基线：48937 B，SHA256 `799b5ce95e679d5c4e1c6c620ca8fa40c44f56073877e0e228ddb69cea7f21da`。Root 若完成 98 的实际字节不同，须重适配本节精确增量，不能覆盖整份旧快照。`run-persistence.patch` 只修改构造保存位置、`save()` 和摘要会话提示；98 的结构 guard、history 安全读取和 bool 清单输入资格完整保留。

1. 新增会话字段 `save_issue=None`，不写入 JSON，保持读取损坏门 `preserve_unreadable` 的含义。构造函数将已接受修复的保存移到读取异常处理之外。
2. 保存先检查读取保护及本会话保存失败门，再完成 JSON 序列化与 Unicode 资格；合格路线保留 UTF-8、indent=2、键顺序、原 `write_text` 平台换行和 `mkdir→write_text→replace` 顺序。
3. 实际 `OSError` 家族将保存标为失败并返回 False；已接受本局内存、ID、时间、历史和计算事实不回滚，不从原文件或 temp 恢复旧局。后续有效采样仍按原规则接受，保存失败会话不再做写盘 IO。
4. `persistence_notice()` 由既有 `summary()` 追加。正常摘要文本保持原样；失败时只在展示中移除“持续累积并保存”的错误持久化暗示，状态内原 notice 不修改。无需提供或覆盖 `app.py`；真实 app 已在采样和手动重置后调用 `run.summary()` 更新可见 `run_summary`。这保留真实第 96/98 节 app 增量。

`save()` 从原无显式结果改为成功 True、保护/已知失败 False；既有读取修复、apply 和 reset 调用都不以此结果否定已接受内存。`reset()` 本身的原返回语义不变。

## 手动开始新局的明确边界

手动新局仍生成新 ID、清空当前局内存并解除旧的读取损坏门；健康保存继续持久化新局。若本会话曾保存失败，手动新局不清除 `save_issue`、不自动重试、不覆盖先前 temp 证据。手动动作已发生，因此不会回滚成旧局；采样/UI 后续清理得以继续。

该失败会话中的新读取和新局只在内存有效。重新启动可能读取磁盘较早的局，而不是刚开始的新局，界面明确提示这一限制。一个新的独立健康对象可读原盘；它不会为正在运行的失败对象解除保护。本包不宣称跨会话的 temp 永远保留，也不引入自动恢复、启动新局或重试按钮。用户应先处理保存原因再重启并明确确认新局，不能默默把磁盘旧局回放到当前内存。

## 原文件、temp、Unicode 与异常优先级

实际 app 的路径是 `.local/run-state.json`，temp 为不同的 `.local/run-state.tmp`。正常异路径下，仅成功 replace 发布目标；失败写入可能已经创建、截断或写入部分 temp。本节不删除、不补写、不回放这些证据。缺失目标不被说成“原文件已保留”。

1. 原读取保护和已有 `save_issue` 最先拒写，甚至不尝试序列化；它们不会因后续有效采样而自动解除。
2. JSON serializer 的 TypeError、循环 ValueError、RecursionError 等非 IO 错误保持传播，不改成普通保存失败。为安全资格判断，序列化提前到 mkdir 前；如果同时存在非法值和 mkdir 故障，现在先见序列化错误，这是明确的优先级变化。
3. 原生相邻 high→low surrogate 的两个 Python 码点在完成 JSON quoting 后检出，并在任何 IO 前拒写；接受内存与原盘、原 temp 都不改。正常 emoji 是一个 scalar，不命中。含序列化非法值时，serializer 错误先于 pair 资格，不伪造保存状态。
4. 单独、分开的或 low→high surrogate 仅在 JSON quoting 后用 `backslashreplace` 转 ASCII JSON 转义；普通中文、真正 supplementary scalar 和字面反斜杠-u 保持各自含义。只讨论已声明 CPython-accepted 码点范围，不声称这些值跨 JSON 实现可互操作。
5. 合格文本的目录、写入、replace 只捕获 OSError，包括 PermissionError 和 FileExistsError；RuntimeError、ValueError 等程序错误仍传播。构造修复保存如今在读取 try 外，非 IO 保存错误也不会被误称读取坏文件。

来源已读取，无需重复猜测或重复联网：既存 `p2-after096-account-metadata-source-survey-v1/public-documents/python-json-3.12.html` 的 Character Encodings 和 RFC 8259 §8.2 原正文、下载 receipt，以及实际 Python 3.12 `pathlib.write_text/replace` 与 JSON decoder 源码。Python HTML 是 3.12.15 家族文档，实际本机源为 3.12.14，二者版本未混称。设计独立 Source 研究见 `/workspace/.continuation/section099-io-semantics-static-review-v1.md`；它未验收这份候选或项目运行。

## Root 实际验收

`candidate/tests/test_run_persistence_099.py` 有 21 个测试方法，尚未执行。它覆盖普通 Unicode 和平台原写字节、健康重启、ASCII-load lone surrogate 的 key/value、native 分隔与反序、escaped pair 已是 scalar、真正 native pair 无 IO 拒写、序列化/IO 双重故障优先级、非 IO 程序错误、每个 IO 阶段的受控注入、部分 temp/完整 temp、不存在原文件、连续接受、手动新局的健康/失败两条路线、load 损坏优先级、构造修复保存的 IO 与非 IO 错误分类。

非空 temp 目录带公开 sentinel 的测试是真正 `open/write_text` 的 OS 失败，不是 chmod 伪权限证明，也不冒称真实 mkdir 或 replace 权限故障。其他阶段明确是单元注入。构造修复分类测试只注入已资格的修复返回，并不声称复现实际强化修复机制；相关实际 origin_discovery 回归必须一起运行。

Root 在完成 98 后添加 `tests.test_run_persistence_099` 到真实当前 `scripts/verify_cloud.py` 的精选登记，保留其他项与顺序，不移植旧 registry。随后实际运行新测试及相关回归：`test_run_state_reliability`、`test_target_memory`、`test_origin_discovery_055`、`test_run_reuse_guards_032`、`test_counter_lifecycle_064`、`test_relic_grade_sync_032`、`test_node_content`、`test_run_config`、`test_run_config_validation`、`test_account_persistence` 和真实 096 培养条件回归，再跑当前精选。

实际项目窗口用独立公开临时状态目录观察：一次健康保存/重启；非空 run-state.tmp 目录触发真实 open 失败后，摘要可见、新持有/本局培养与计算仍刷新、后续采样不重试；失败后手动点击开始新局，确认 ID 和 sample_epoch 已换、采样/地图/目标/强化预览清理继续、新局观察不泄漏旧局，提示新局未落盘。留完整 target/temp/sentinel 前后字节、已接受内存、输入 caller、实际返回和窗口截图；截图实际打开查看。仅 Root 记录真实计数/退出码及 commit/push。

本节不证明 `.tmp` 目标/路径别名/符号链接攻击、路径编码错误、并发多个写者、fsync 与断电耐久、任意非 JSON 对象/循环/非字符串键/NaN 精确往返、非 CPython 实现或原生 Windows/游戏/聊天。既有 serializer 与深层 opaque 输入政策不借本节扩写；有新实际消费缺陷时再单独查证。
