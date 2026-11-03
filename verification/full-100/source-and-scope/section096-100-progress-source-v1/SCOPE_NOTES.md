# 测试选择器范围及20个未登记模块（只读源码清单）

当前维护范围为200个有序选择器：112个云端项、101个历史项及6个新增项去重形成；其中196个整模块和4个单方法。实际Linux回执的有序选择器与此并集完全一致。217个顶层测试模块中覆盖197个，20个完全未登记。以下120个方法为AST直接测试方法数，未运行，不能替代运行数量或通过结论。

| 未登记模块 | AST方法数 | 源码条件与适用性 |
|---|---:|---|
| [tests.test_adaptive_recognition](/workspace/rougezhushou/tests/test_adaptive_recognition.py) | 5 | 历史截图及OCR。 |
| [tests.test_capture_queue](/workspace/rougezhushou/tests/test_capture_queue.py) | 4 | Win32及windows_capture；原FakeWGC回调夹具不证明真实Windows采集。 |
| [tests.test_chat](/workspace/rougezhushou/tests/test_chat.py) | 3 | 三个本地127.0.0.1 HTTP夹具；不访问外部服务，不验证真实服务商。 |
| [tests.test_difficulty_relics](/workspace/rougezhushou/tests/test_difficulty_relics.py) | 2 | 临时RunState与公开静态资料。 |
| [tests.test_dynamic_resolution](/workspace/rougezhushou/tests/test_dynamic_resolution.py) | 4 | 历史截图及OCR。 |
| [tests.test_empty_inventory](/workspace/rougezhushou/tests/test_empty_inventory.py) | 3 | 历史截图及OCR。 |
| [tests.test_frame_buffer](/workspace/rougezhushou/tests/test_frame_buffer.py) | 13 | 自有数组、cv2/numpy和原局部时钟夹具，不调用采集。 |
| [tests.test_inventory_tools](/workspace/rougezhushou/tests/test_inventory_tools.py) | 3 | 临时RunState；库存工具与手动重置。 |
| [tests.test_map_clearing](/workspace/rougezhushou/tests/test_map_clearing.py) | 8 | 历史地图截图及OCR。 |
| [tests.test_map_templates](/workspace/rougezhushou/tests/test_map_templates.py) | 7 | 历史exploration-map.png及地图详情截图。 |
| [tests.test_node_content](/workspace/rougezhushou/tests/test_node_content.py) | 10 | 四个公开图结构和临时状态方法可独立登记；其余含截图及Qt/微软雅黑字体/OCR条件。 |
| [tests.test_node_rewards](/workspace/rougezhushou/tests/test_node_rewards.py) | 8 | 本地公开节点资料；保留资格、概率未知。 |
| [tests.test_numeric_recognition_024](/workspace/rougezhushou/tests/test_numeric_recognition_024.py) | 5 | 三个自有合成图方法仍需要产品counter-zero图标；另外两个依赖历史截图。 |
| [tests.test_projection_screen_029](/workspace/rougezhushou/tests/test_projection_screen_029.py) | 12 | 固定随机种子合成图及原局部模板夹具。 |
| [tests.test_recognition](/workspace/rougezhushou/tests/test_recognition.py) | 15 | 历史截图及OCR。 |
| [tests.test_recognition_reuse](/workspace/rougezhushou/tests/test_recognition_reuse.py) | 4 | 历史截图及OCR。 |
| [tests.test_relic_recognition_022](/workspace/rougezhushou/tests/test_relic_recognition_022.py) | 4 | setUpClass需要历史藏品截图及OCR。 |
| [tests.test_relic_screening_024](/workspace/rougezhushou/tests/test_relic_screening_024.py) | 3 | 自有合成图及原EnergyScreen模板夹具。 |
| [tests.test_run_badges](/workspace/rougezhushou/tests/test_run_badges.py) | 5 | 历史地图和本局信息截图及OCR。 |
| [tests.test_run_config](/workspace/rougezhushou/tests/test_run_config.py) | 2 | 一个临时RunState方法可独立登记；另一个依赖run-info-trade.png。 |

另有已部分登记的[tests.test_enemy_environment](/workspace/rougezhushou/tests/test_enemy_environment.py)：五个AST方法只登记四个。遗漏的`test_visible_region_updates_and_survives_partial_pages_and_restart`需要历史run-map-empty.png及OCR，不能以缺样本时的不可用记录代替通过。

在AGENTS、交接文件、历史验证表及现有维护脚本等已列明来源中，没有找到20模块已退役的明确依据。未登记不证明退役，源码中仍有产品API也不证明测试预期有效。实际执行后才可判断通过、真实错误或不可用。

## 后续第102节可考虑的有界恢复方案（未编入、未执行）

优先补登记七个可独立运行整模块：frame_buffer、difficulty_relics、inventory_tools、node_rewards、projection_screen_029、relic_screening_024、chat；共44个原AST方法。再独立登记numeric_recognition_024的三个合成图方法、node_content的四个公开图结构方法、run_config的一个临时状态方法。八个完整方法名称在JSON中逐项保留。

若实际编入并执行，这15个选择器预计覆盖52个原AST方法，使有序并集增至215项（203整模块、12单方法），覆盖207个物理模块。仍有10个完全未登记模块，以及四个部分登记模块的10个遗漏方法，不可宣称全库。建议只扩充full的新增选择器，保持原云端选定回归范围；另行明确物理文件与登记缺口。

原AvailableResult不可用规则需保留：缺少历史samples/native-client或.cache来源、白名单环境依赖才按原规则记录不可用。产品素材缺失、非白名单异常、错误断言仍应真实报错。不可扩大skip规则以取得绿灯。Qt字体缺失可能产生IndexError；Windows采集依赖和历史截图需要真实能力或材料，不能猜测成功。

本清单仅标准库读取、哈希、AST和JSON整理。项目导入、项目测试、helper、Git、Wine及tracked修改均为零。详见[test-scope-and-source-list.json](/workspace/.continuation/section096-100-progress-source-v1/test-scope-and-source-list.json)。
