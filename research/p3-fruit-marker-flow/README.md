# 藏果地/迷藏独立声明标记流程候选

仅供根代理串行接入的完整功能组，当前全部在 work，不是已提交/已完成第259节。

新增能力：明确地图与标记节点身份、初始标记、独立放置及文明之烬覆盖，逐步复核普通探索和曲折密道另一端进入/钻出的来源条件。密道特例要求独立配对端、入口、标记端钻出和另一端正声明全部一致；ID不同不能自动证明入口关系。初始持有迷藏/进入新区域只核生成参数条件，不制造标记。每步保留原输入、来源条件后状态和独立后状态；冲突不归为通过；旧步骤不被自动改绑到新节点。

原版迷藏原文明确一个随机自然物；三件具名候选是恋家果/光彩松露/板藤，原ID和完整原记录各自保持。普通探索后标记状态仍未知；只有文档另一端钻出特例有条件保留。连续两次特例每行仍可列原版一个的参考，但实际领取、重复上限与总量始终None，不推断独立随机抽取。

## 来源与边界

四完整原items来自固定a550f5e原表的已封完整302物品selected packet，父文件SHA保留。黑流数据库434599的完整文明之烬/藏果地原段落已摘录，其完整rawSHA与seed来源回执相等。零件目录434637的标志定义和三件完整卡片另摘录，原ID名称双向核对。source-receipt.json保存完整来源URL/revision/whole SHA/fragment SHA。构建器逐叶验字节，按固定原句及身份校核，再完整重建JSON；未知版本变化拒绝复用。

当前服务器资格、原生实际入口与两端绑定、触发/实收、常规探索消除、其它覆盖/共存、重复触发上限和数量、跳转后库存全部未知。不操作游戏、不写本局/私态/地图绑定；不提供生成概率。临时Qt offscreen非原Windows可见/游戏/聊天验收。

## 必要验收

首轮15不同检查全部通过：12来源/API边界+3实际Qt点击流程。UI文案和列宽变化后仅复跑受影响3Qt检查，全通过；不能合计为18不同用例。两张PNG均实际查看；封存final-window.png是最终UI。现有ui_state.replace_text被复用，刷新实际保留技术开关、已声明入口/步骤选择、阅读滚动；真实按钮发出只读节点预览signal，actual_map_binding_verified=False。首次没有失败/跳过；无既有全量重跑。

## root接入

- rouge/fruit_marker_planning.py、fruit_marker_view.py、data/fruit-marker-reference.json
- scripts/build_fruit_marker_reference.py、tests/test_fruit_marker_planning.py
- 本目录公开证据全部转至 research/p3-fruit-marker-flow。
- API declared_marker_flow(node, events=None, relic_owned=None, new_region_entered=None)。node五项：node_id/map_id/node_type/marker/paired_node_id；标记fruit/civilization/none/unknown。place与visit的完整输入合同见函数docstring/测试。
- FruitMarkerPanel.set_reference(node)、set_events(events)、set_corridor_route(entry_node_id,exit_node_id,from_other_end)。nodePreviewRequested(dict)仅引用明确声明身份，root须自行核对真实已绑定图后才预览，不能按任意ID匹配或写状态。
- 根代理负责单次接入可见节点/局外工具入口、必要相关检查和适当实际窗口检验，同节原子提交/普通推送后才更新完成节数。

work验证bootstrap只将candidate/rouge加入rouge.__path__后加载candidate/tests；生产转移后可正常运行QT_QPA_PLATFORM=offscreen python -m unittest tests.test_fruit_marker_planning。
