# Sealed Source contract 的范围更正

原封存文件 `/workspace/.continuation/p2-runstate-leads-root-probe-source-v1/SOURCE_CONTRACT.md` 第 13 行写道：

> The script imports only rouge.run_state and its normal dependencies at Root runtime, never app, GameCapture, recognition APIs, Qt, Wine or chat.

其中 `recognition APIs` 表述过宽，现明确撤回。原包保持 STOPWRITE；此 sidecar 是更正记录，未回写原文、runner、manifest、fixtures 或维护代码。

Root 实际 receipt 的 `actual_imported_source_log` 记录 12 个经过 Source SHA 校验的项目模块，包含 `rouge.relic_recognition`、`rouge.operator_recognition` 和 `rouge.map_recognition`。`run_state.py` 顶层引入 `resolve_owned_icons`、`resolve_difficulty_icons`、`difficulty_families`；正常 reconcile/apply 路径会使用这些复制 icon/card dict 并查询固定资料的函数。`restore_passed_node_types` 正常引入 map_recognition 的 predict_map。实际 import 不等于实际图像/OCR 入口调用，纯资料 resolver 也不是 whole-project 零 helper 调用。

可支持的范围是：公开 probe Source 没有调用 app/MainWindow、GameCapture、图像识别入口、OCR、live sampling、Qt 或聊天；Root observation 单独记录 `direct_recognition_image_OCR_live_sampling_calls_in_probe=false`。公开输入是固定 JSON/dict，没有游戏画面或私人缓存。profile 仅测量 exact run_state.py source frames；其它项目 helper 没有被全面计数。因此不能声称 whole-project 零 API、所有 recognition helper 零调用，或以未记录的全项目函数轨迹推导任何数量。

当前 sidecar 只读取原 Source 和过去 receipt；没有 import 或执行 recognition 模块。原 import_log 的完整路径/bytes/SHA 与 Source map 对齐记录在 `actual-counters.json` 与 `source-integrity.json`，源文件原字节在 source-snapshots 中。
