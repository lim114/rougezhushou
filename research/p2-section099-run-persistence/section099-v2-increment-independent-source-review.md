# 第 99 节 v2 增量独立 Source 审阅

结论：在此次实际读取的 v1 生成件、v2 预备组装源码和 23 个测试方法内，未发现新增增量 blocker。v2 尚未组装，本结论不能替代对最终第 98 节基线及最终第 99 节生成件的精确重基审阅、实际回归或窗口验收。只审本节持久化增量，没有重新审第 98 节整体 guard，没有执行候选、项目、测试、Git、Wine、Qt 或 fixture codec；仅使用只读源码、标准库 AST/差异/哈希和仓库外本报告写入。

## 实际输入与范围

| 输入 | bytes | SHA256 |
|---|---:|---|
| `section099-run-persistence-v1/baseline/rouge/run_state.py` | 48937 | `799b5ce95e679d5c4e1c6c620ca8fa40c44f56073877e0e228ddb69cea7f21da` |
| `section099-run-persistence-v1/candidate/rouge/run_state.py` | 50576 | `2ee957817f09cfbd5f790d00f9b08f2541380295f1dce07abab67224f4a8c899` |
| `section099-run-persistence-v1/run-persistence.patch` | 4687 | `a5315ce746243f635620e21b2407b58aa88c27f1da2f289198ce6a39b94414eb` |
| `section099-run-persistence-v2/build_candidate.py` | 8584 | `470358d5ddf40ba9b1843c22b70b5931be67cb0a8da30691c5ba641b8873baa6` |
| `section099-run-persistence-v2/candidate/tests/test_run_persistence_099.py` | 26468 | `e1d3d192811bb5317c5d31ff06466c6a21634e4d25a5494d1dfd7a2b97120eb0` |

路径均位于 `/workspace/.continuation/`。没有运行 build_candidate.py；其带独占写入的生成动作也未被本审阅触发。AST 解析只能证明读取源码可解析和方法计数，不能证明目标运行成功。

## 精确增量审阅

1. v1 的变动仅新增会话 save_issue、将构造修复的 save 移到读取 except 外、替换 save、增加 persistence_notice，以及 summary 追加展示提示。原 reset 状态字典和 apply 内存合并没有改变。v2 预备 Source 在这些变动之外，新增 FileNotFoundError 的 lstat 分辨分支，未提供 app 覆盖件。最终仍须以真正完成 98 的当前字节进行重基；不能直接覆盖本次 v1 的旧完整文件。
2. 保护/失败门在 serializer 之前：preserve_unreadable 或 save_issue 为真时返回 False，不进入 mkdir/write_text/replace。已有读坏文件的门不被正常 apply 解除。成功保存返回 True；apply 和 reset 未将 False 当作否定已接受内存。
3. json.dumps 在 IO 前执行且不在 OSError try 中；循环 ValueError、非 JSON TypeError 等保持传播。合格文本的 mkdir/write_text/replace 只捕获 OSError，注入的 RuntimeError、ValueError 和 UnicodeEncodeError 不会被错误吞并。这里不声称任意路径的 Unicode 编码问题属于已修复范围。
4. 完成 quoting 后检测真正邻接原生 high→low；命中后设置 save_issue、返回 False，尚未进行任何 IO。孤立/隔开的/反序码点使用 backslashreplace 形成 JSON 转义，正常 scalar emoji、字面反斜杠-u 保留区别。多个 JSON 字符串之间的引号/逗号会阻断邻接检测；v2 测试新增列表分离字符串和 dict key/value 分离字符串边界。保持这项既定资格范围，不把账户 97 或此处称为任意 Python 值通用无损算法。
5. OSError 后只设会话失败，未回滚 accepted state、id、last_read 或 history，未删除/回放 temp，未声称缺失目标原文件已保留。write 失败可留下部分 temp，replace 失败可留下完整 temp。正常 `run-state.json/run-state.tmp` 异路径范围仍须明确；路径别名、.tmp 目标、并发写者和 fsync/断电不由本节证明。
6. reset 仍先创建新局，清除读取损坏门；save_issue 不被清除，因此先前已失败会话的手动新局只改变内存，不自动重试或回滚旧局。首次手动 reset 发生 IO 失败时也保留新 id。一个新的独立对象可以再次读原盘，但不能为旧失败对象解锁。提示明确重启可能恢复较早盘记录。
7. save_issue 不写 state/JSON。summary 只在局部展示字符串替换“持续累积并保存”为“持续累积”后追加 persistence_notice，未改原 state notice。健康摘要保持原内容；失败摘要不会把有效内存说成已持久化。实际 UI 刷新仍由 Root 验证，Source 单元测试未导入 Qt。
8. `repair_needs_save` 在读 try 前为 False，只在成功返回的修复资格后赋值；读取 except 之后才 save。这样 save 的 OSError 成为 save_issue，非 IO ValueError 从读取处理范围外传播，不误报读取损坏。测试中的 qualified_repair 是显式注入控制，不证明真实修复机制本身；真实 origin_discovery 相关回归仍必需。
9. v2 缺失分支：read 遇 FileNotFoundError 后，只有 lstat 也抛 FileNotFoundError 才认定确实不存在。lstat 成功（包括 dangling symlink entry）或 lstat OSError 均保守设置读取保护；提示为“原路径”，没有虚构存在已读的原文件。lstat 的非 IO 程序异常不被内层 except 捕获；在 except handler 中抛出不会落回同层原外部 except。这个传播结论是 Source 控制流审阅，23 方法中没有专门注入 lstat RuntimeError 的执行回执。

## 23 方法的静态可达和观察边界

以下是计划中方法的 Source 观察，不是实际执行或通过计数。共 23 个 test_ 方法，其中旧 21 个保留，2 个新增；另外现有 2 个方法增加跨字符串 surrogate 和 UnicodeEncodeError 注入边界。

| 测试方法（省略共同 `test_` 前缀） | 静态审阅的路径与断言 |
|---|---|
| ordinary_unicode_preserves_platform_writer_and_healthy_restart | 真实 save True、完整 decoded state、平台 writer 完整 bytes、重启 id/history/opaque/持有一致。 |
| loaded_lone_surrogate_keys_and_values_keep_exact_decoded_points | ASCII 公共夹具四端点及 key/value；完整 disk 对内存，重启 ord-array。 |
| native_nonadjacent_surrogates_and_literal_escapes_remain_distinct | 单独/分隔/反序、literal、scalar、list 分离字符串和 dict 分离 key/value，完整往返。 |
| ascii_escaped_pair_loads_as_scalar_and_saves_normally | ASCII escaped pair 明确已载入为 scalar，不冒充 native 两码点夹具。 |
| native_adjacent_pair_refuses_before_io_and_keeps_accepted_memory | seed 在 spy 前成功；新事实已接受，mkdir/write/replace 均无调用，target/temp/caller/opaque/id 保留。 |
| pair_refusal_of_absent_target_does_not_create_parent | 真缺失入口及父目录，pair 在 IO 前拒绝，不创建路径。 |
| serialization_errors_precede_io_and_do_not_claim_io_failure | 非 JSON object、循环、object+pair；预期 TypeError/ValueError 优先于注入 PermissionError，全部 IO 无调用、无 save_issue。 |
| non_io_program_errors_are_not_mislabeled_or_swallowed | 每 IO 阶段 RuntimeError、ValueError、UnicodeEncodeError 注入；新持有仍在内存，原目标不改，异常传播、未误设失败状态。 |
| oserror_at_each_stage_keeps_target_memory_and_stop_order | 每阶段 PermissionError/OSError/FileExistsError 注入；helper 要求 apply True/caller 不变/last_read/持有正确，后续写和 replace 按阶段不执行。 |
| partial_write_evidence_is_neither_deleted_nor_published | new=interrupted 的方法绑定得到真实 Path；写指定公开 partial bytes 后 OSError；target 原字节、temp 原样、后续 save False。 |
| replace_failure_retains_complete_temp_distinct_from_final_target | 真实 write 后受控 replace 失败；完整 temp decoded==accepted state，后续 accepted observation 不重写，独立对象读旧目标。 |
| actual_open_failure_keeps_nonempty_temp_directory_and_healthy_old_restart | 非空 temp 目录带 sentinel，实际 write_text open 失败；目标/sentinel/目录集合保持，健康独立对象仍读旧局。不是实际 mkdir/replace 权限验证。 |
| absent_target_io_failure_does_not_invent_saved_original | mkdir 注入拒绝，原目标和 temp 都不存在，提示不说已保留原文件。 |
| failed_session_keeps_accepting_current_run_without_automatic_retry | 首次失败后两次递增时间 observation 继续 True；旧 history 前缀保留，三阶段 spy 皆无调用，目标/temp 不改。 |
| manual_reset_after_save_failure_clears_memory_without_retry_or_rollback | 失败后 reset 创建新 id、空 operators/relics/maps/history、last_read None，save_issue sticky；IO spy 皆无调用，另一个对象原文件不动，新观察保留新 id。 |
| io_failure_during_first_manual_reset_keeps_new_run_in_memory | 健康对象首次 reset write 注入失败，仍新 id、空局；独立重启明确恢复旧盘 id，并未回滚正在运行对象。 |
| healthy_manual_reset_still_persists_new_id_and_leaves_other_file_alone | 健康 reset 及重启新 id/空持有，完整 disk==state，另一个状态文件不改。 |
| load_corruption_remains_distinct_and_manual_reset_retains_old_contract | JSON/UTF-8/maps 类型坏夹具由 98 guard 或读处理保护；apply 不覆盖；手动 reset 清除读门并健康写入。这里依赖最终 98 guard，未审其整体正确性。 |
| existing_load_guard_precedes_serializer_and_new_io | 读坏后再放非 JSON object；保护直接 False，不因 serializer 抛错，不改 target/temp。 |
| restart_repair_write_failure_is_not_misreported_as_load_corruption | qualified_repair 返回 True 后 constructor 真 write/注入 replace；accepted repair 内存及完整 temp 保留，恢复提示和保存提示同时存在，无误读保护。 |
| non_io_error_in_restart_repair_save_escapes_read_error_handler | 注入已资格修复后 write ValueError 从 constructor 传播；原目标不改。仅分类控制，非真实修复机制证据。 |
| actual_dangling_symlink_is_not_missing_until_explicit_manual_reset | 若真实 symlink 建立不可用则明确 skip/未执行；可用时保留 link entry/readlink/缺失 target，无 temp；手动 reset 的 replace 替换入口成为 regular JSON，缺失 target 仍未建立。 |
| missing_read_with_existing_or_unknown_lstat_preserves_entry | read_text 注入 FileNotFoundError；lstat 真实成功或 PermissionError/OSError 三分支，fallback 新 id/空 history，apply True 但 save False，无 temp，旧目标字节保留，无保存失败误提示。 |

Mock 的 seed 和公开夹具建立发生在 patch 窗口之外，避免先前成功步骤被本轮故障提前截断。ExitStack 顺序和按阶段 conditional spy 允许指定故障确实到达，并约束该故障之后的 IO 未执行。真正 open 故障与其它阶段单元注入已分开命名；缺少 symlink 能力不能计为实际通过。

## 未替代的验证

- v2 最终生成件目前不存在；最终 98 修订后应重新固定 baseline/candidate/patch/测试 bytes 与 SHA，检查增量确实保留最终 98 guard 和 app 改动，再实际应用。这份 Source 审阅不提供最终整体资格或运行结果。
- 23 方法未执行。没有实际计数、返回码、Wine/native Windows 结果、截图或发布证据；UI 的 apply/reset 后刷新、sample_epoch、map/target/强化预览清理仍须真实项目窗口验收。
- 原生 high→low、孤立 surrogate、literal、scalar、普通中文的项目完整往返/拒绝仍须 Root 实测；既有官方文档只是范围依据，账户 97 结果不是本节运行证明。
- lstat 的程序异常传播目前仅静态确认；如果 Root 认为这一新分支是验收边界，可补一个明确单元控制。不得将此静态推断写成实际已执行。
- 第 95 节 full-window 三次未完成的搁置状态未被改变。第 99 节未提前计为完成、提交、推送或全量通过。
