# 第 102 节登记候选的导入依赖源审

状态：Source-only；15 个 selector（7 个全模块、8 个方法）对应 52 个 AST 测试方法。实际执行 0、PASS 0、完成小节 0。

本次沿 10 个根测试模块追踪了 40 个项目／测试模块的 eager AST 导入，包括原件哈希、逐 selector 方法坐标与全部导入边。没有导入项目、调用测试或使用 Git／Wine／网络。

| Selector | AST 方法数 | eager 外部依赖 | 原断言与夹具范围 |
|---|---:|---|---|
| test_frame_buffer | 13 | cv2, numpy | 13 methods; own numpy arrays + real FrameBuffer. Eager cv2/numpy C extensions; original local monotonic patch, no capture/window/OCR construction. |
| test_difficulty_relics | 2 | cv2, numpy | 2 methods; synthetic RunState in TemporaryDirectory. RunState eagerly imports relic_recognition -> operator_recognition/anchors -> cv2/numpy. apply imports real relics/run_config; numeric/icon family behavior remains existing assertions. |
| test_inventory_tools | 3 | cv2, numpy | 3 methods; synthetic temporary RunState. Same eager cv2/numpy chain even though methods do not recognize screenshots; local reset affects only temporary fixture. |
| test_node_rewards | 8 | 标准库 | 8 methods; node_rewards eager imports are stdlib; real product reference JSON read lazily. No new reward model or real grant; missing product reference is ERROR. |
| test_projection_screen_029 | 12 | cv2, numpy | 12 methods; real EnergyScreen/ProjectionScreen and cv2 correlation on seeded owned arrays. Original patch.object prepared_templates/artwork_families fixtures retain asserted RGB/ambiguity checks. No ScreenReader/Qt/OCR invocation. |
| test_relic_screening_024 | 3 | cv2, numpy | 3 methods; real EnergyScreen and cv2 correlation on owned arrays, original prepared_templates local fixture. No screenshot/Qt/OCR invocation. |
| test_chat | 3 | httpx | 3 methods; eager httpx. Original HTTP fixtures bind 127.0.0.1:0 and use empty API key; stream_chat sets trust_env=False/follow_redirects=False. No actual external provider, account, client, or user message. Loopback bind/HTTP/TLS-independent dependency failures remain ERROR. |
| test_numeric_recognition_024.NumericRecognition024Tests.test_verified_zero_uses_only_recognizer_across_moved_resized_panels | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader and full recognition chain, but calls only counter helper + near_number with original injected engine closure. No ScreenReader construction/read, RapidOCR, Qt/font, native capture, or sample screenshot call occurs in these three selected bodies. Product counter PNG is a real prerequisite. |
| test_numeric_recognition_024.NumericRecognition024Tests.test_ten_or_empty_or_wrong_topology_cannot_shortcut_to_zero | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader and full recognition chain, but calls only counter helper + near_number with original injected engine closure. No ScreenReader construction/read, RapidOCR, Qt/font, native capture, or sample screenshot call occurs in these three selected bodies. Product counter PNG is a real prerequisite. |
| test_numeric_recognition_024.NumericRecognition024Tests.test_weak_recognizer_result_falls_back_without_relaxing_threshold | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader and full recognition chain, but calls only counter helper + near_number with original injected engine closure. No ScreenReader construction/read, RapidOCR, Qt/font, native capture, or sample screenshot call occurs in these three selected bodies. Product counter PNG is a real prerequisite. |
| test_node_content.NodeContentTests.test_legacy_clearing_record_recovers_only_confirmed_same_layout_history | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader, RunState, tests.test_map_templates.first_map, and map_data. first_map is merely defined/lru_cache-decorated, not called by these four selected methods; no class setUp/setUpClass exists. Bodies use public source_graph/map_data plus temporary RunState, not ScreenReader/read or font rendering. Import dependency closure must still succeed. |
| test_node_content.NodeContentTests.test_passed_clearing_keeps_original_type_and_consumes_generation_budget_after_restart | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader, RunState, tests.test_map_templates.first_map, and map_data. first_map is merely defined/lru_cache-decorated, not called by these four selected methods; no class setUp/setUpClass exists. Bodies use public source_graph/map_data plus temporary RunState, not ScreenReader/read or font rendering. Import dependency closure must still succeed. |
| test_node_content.NodeContentTests.test_fog_next_to_visible_vantage_point_reports_visibility_conflict | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader, RunState, tests.test_map_templates.first_map, and map_data. first_map is merely defined/lru_cache-decorated, not called by these four selected methods; no class setUp/setUpClass exists. Bodies use public source_graph/map_data plus temporary RunState, not ScreenReader/read or font rendering. Import dependency closure must still succeed. |
| test_node_content.NodeContentTests.test_immediately_revealed_nodes_are_not_fog_candidates_on_later_floors | 1 | cv2, numpy | Each selected method eagerly imports ScreenReader, RunState, tests.test_map_templates.first_map, and map_data. first_map is merely defined/lru_cache-decorated, not called by these four selected methods; no class setUp/setUpClass exists. Bodies use public source_graph/map_data plus temporary RunState, not ScreenReader/read or font rendering. Import dependency closure must still succeed. |
| test_run_config.RunConfigTests.test_settings_survive_missing_pages_restart_and_only_manual_reset_clears_them | 1 | cv2, numpy | Selected method eagerly imports ScreenReader/full recognition chain but invokes only temporary RunState apply/restart/reset. No setUp/setUpClass or ScreenReader/read call in this body. Do not broaden to first screenshot method without its actual sample/OCR prerequisites. |

## 判定与实际风险

- `RunState` 经 `relic_recognition → operator_recognition/anchors` 在导入时即需要 `cv2/numpy`，不能将状态测试称为纯标准库。当前 Linux requirements 声明这两项；声明不代表实际导入成功。
- `numeric_recognition`、`node_content`、`run_config` 方法 selector 仍先导入整个所属模块及 `ScreenReader` 链。当前这条 eager 链只发现 `cv2/numpy` 等导入，没有 eager Qt、win32、PIL 或 RapidOCR。RapidOCR 在 `ScreenReader._read` 延迟导入；选定的 3 个 numeric 方法使用原测试 engine 夹具，4 个 node 方法和 1 个 run_config 方法也不调用 ScreenReader。
- `node_content` 还导入 `tests.test_map_templates.first_map`；这 4 个方法没有调用它，且没有 setUp／setUpClass，因此源审不要求它读取历史截图。必须由 Root 实际加载确认。
- 未选中的 node_content 绘图方法局部导入 PySide6 并读取 `Fonts/msyh.ttc`。不得因邻近四方法获登记就声称字体／Qt／OCR可用或扩大到整模块。字体为空时的 `families[0]` 会产生实际 ERROR；不属于自动 U。
- 原 `AvailableResult` 缺包 U 名单仅 PySide6、PIL、rapidocr_onnxruntime、win32gui、win32process、win32api、windows_capture。`cv2/numpy/httpx` 或其未列入名单的依赖缺包、C-extension/DLL/plugin 加载 ImportError/OSError、产品 JSON/PNG 缺失均不能自动归入 U。只有 `.cache` 与 `samples/native-client` 下带 filename 的 FileNotFoundError 可作为样本 U。addSubTest 不覆盖依赖缺包 U。
- chat 仅原 127.0.0.1 临时 HTTP fixture、空凭据，实际 stream_chat 禁用环境代理与跳转；不证明外部服务商、真实客户端或账号兼容。绑定端口、HTTP 依赖与线程问题仍需真实执行。
- 当前 `tests/__init__.py` 不存在；命名空间包是否被环境中其它 regular tests package 遮蔽，须实际模块坐标确认，源审不臆测。

## 给 Root 的界限

在实际完成第 101 节之后重新绑定源码，真实加载原 15 个 selector 并执行原断言，保留所有依赖 U、产品 ERROR、失败、skip、subtest 和真实 primary 退出码。不得降低断言、修改分类器或通过换夹具制造绿灯。52 仅为 AST 计划计数，不能写成 52 已通过。

完整逐 selector 导入边、方法调用坐标、资源存在性和原件哈希见 `import-audit.json`。
