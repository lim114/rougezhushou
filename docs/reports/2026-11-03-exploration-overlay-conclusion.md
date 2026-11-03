# 探索地图叠加结论报告 · 2026-11-03

**结论：第一轮的三类切换和节点卡片交互已有用户确认与日志支持；本节属于部分通过，尚未满足两轮完整验收。** 鼠标靠近小卡消失的主要原因已查明并修正；最后版本完成了列表高度和阅读状态修正。网页实机、第二大窗口、最终图像对照及落点错漏计数仍缺证据，473继续在制。

日常入口的缺口已补：此前只能在独立白色地图选类型，未选择时游戏叠加没有数字；现在游戏客户区内的类型胶囊直接控制相同状态，普通启动不预选类型。

本报告对照原单七项交付。代码依据为功能提交`c3c50b5d2e7569a734288583996c7212871a5b8b`；报告采集前main为`c31f7b6f1c474023395ad265f5c96bdcc72a4f26`，该提交仅整理文档行尾，产品源码不变。当前叠加模块SHA256为`18e9f4a02da498c34060dee2d1032f23eda027b127901f9866ec21efcac0f98b`。完整逐轮源码摘要和指标快照见[conclusion-metrics.json](../../verification/maintenance/map-overlay-video-20261103/conclusion-metrics.json)。

**1．截图对照与判定**

| 对照对象 | 当前结论 | 原因与已有证据 |
|---|---|---|
| hd_70：左侧类型胶囊 | 部分一致 | 游戏客户区左边缘竖向图标胶囊、点选和取消已录到；保留原游戏下方按钮。最后源码的三类切换有记录，最终尺寸/间距图待补 |
| hd_70：白色历史频率 | 可读性通过，落点验收未完成 | 用户明确确认白字清楚；数字使用白色粗体、阴影，移除“候选/原”前缀。旧实机图仍有原文字重叠，之后加暗底；最后落点需独立逐点对照 |
| hd_85：三列节点小卡 | 第一轮交互通过，最终外观对照待补 | 用户确认可以移入并展开，随后回复列表修正版“第一轮卡片完成”；日志有不同节点的点击和卡片绘制。已保留的旧卡图存在列表压缩，已改高度计算和内容更新；缺最后版卡片截图 |
| hd_100：网页浮窗 | 未完成实机验收 | 共享网页、网址栏及独立保留已做定向控制器检查；各真实轮次未录到web_open，没有真实网页对照图 |

本机并排图位于`.local/overlay-video-20261103-143013/comparisons/type-old-white.png`和`card-cursor-fixed-clipped.png`，后者明确保留失败外观。**本轮截图采集有缺口：截图记录器在30分钟后退出，用户后续操作发生在退出之后。** 因此有交互日志而没有相应最终图。后续只补所缺画面，不重做已确认的整轮操作。图片和原始会话不进入Git。

**2．五项指标与拒绝原因**

| 指标 | 最后源码实测结果 | 结论 |
|---|---|---|
| 开关点击到数字绘制 | 中位/p95：27.47 / 73.72（5次）毫秒 | 只计count>0的绘制，排除取消及没有数字的类别 |
| 点击节点到小卡绘制 | 中位/p95：68.11 / 267.77（20次）毫秒 | 20次绘制含重复点击，不等于相同数量的不同节点 |
| 百分比落点：错节点/漏显/误显 | 未完成独立真值计数 | 不能把没有记录到错误写成0；需最后图与模板逐点核对 |
| 开关/小卡撤下 | 中位/p95：108.58 / 409.71（6次）毫秒 | 测量父窗口原生可见性，每50毫秒轮询；不是逐子控件单独测量 |
| 冷启动首次交互 | 14.843秒 | 还包括初始化与等待首个识别结果 |

上一节切页场景记录的最大撤下延迟为512.76毫秒，缩放场景为1713.37毫秒；本轮为411.64毫秒。后续以相同场景成对比较；本轮尚未完成专门的切页/失焦验收。[上节原回执](../../verification/maintenance/map-overlay-display-20261103/summary.json)保留。

| 校验结果 | 旧点击失败轮次 | 最后源码轮次 |
|---|---|---|
| 参考帧或助手尚未就绪 | 8 | 9 |
| 校验通过 | 1070 | 1767 |
| 锚点文字或图案变化 | 63 | 20 |
| 窗口条件不满足（含游戏非前台） | 71 | 577 |
| 页面或地图模板未匹配 | 0 | 5 |

这些是记录事件次数，采集时长和操作不同，不据此计算准确率或时间占比。最后轮次仍有文字变化拒绝，光标修正并未使所有拒绝消失。

第一轮已录到三种不同类型：秘境行商、狭路相逢、不期而遇；21次节点按下、20次卡片显示、1次来源展开事件。用户确认本轮完成。作战网页、第二种大尺寸、专门安排的切页返回和卡片失焦场景尚未完成。

<details>
<summary>展开全部轮次、源码哈希与原始原因统计</summary>

所有轮次如下；中位/p95均为毫秒，首显为秒。`round1-white`的一次卡片是自有窗口诊断，不算普通玩家通过；`round1-final`首显包含长时间等待前台，不作冷启动性能样本。`round1-ready`及`round1-pointer-track`的采集工具失败保留，没有计通过。

| 轮次 | 叠加源码SHA256 | 首显秒 | 有数字的类型切换：中位/p95 | 小卡：中位/p95 | 撤下：中位/p95 | reason事件分布 |
|---|---|---|---|---|---|---|
| `round1` | `e7f04e209e65e6a32de158c0c5f6a12bce451b9c6ba70916b35cbbcab938154f` | — | 未录到 | 未录到 | 未录到 | reference_or_companion_unavailable=9；window_not_eligible=165 |
| `round1-card-layout` | `18e9f4a02da498c34060dee2d1032f23eda027b127901f9866ec21efcac0f98b` | 14.843 | 27.47 / 73.72（5次） | 68.11 / 267.77（20次） | 108.58 / 409.71（6次） | reference_or_companion_unavailable=9；eligible=1767；anchor_pixels_changed=20；window_not_eligible=577；page_or_map_unmatched=5 |
| `round1-final` | `af87c65f05e29dc96be1ade53210a7fe4ac9941dba1a0608b5eccc386b5d3628` | 1631.196 | 未录到 | 未录到 | 未录到 | reference_or_companion_unavailable=9；window_not_eligible=1266；eligible=72；anchor_pixels_changed=7 |
| `round1-hotspots` | `a1f3010e5c7587fe11a28976177c8737a97233db6605dd9aee913afa31be9f4a` | 14.182 | 28.63 / 364.77（5次） | 未录到 | 201.38 / 730.43（24次） | reference_or_companion_unavailable=8；eligible=1070；window_not_eligible=71；anchor_pixels_changed=63 |
| `round1-native` | `27087ec0a79e04eabc293561d9da73332aefa6f02569d97dbdff98b13d5abb55` | 13.503 | 23.38 / 152.31（8次） | 未录到 | 113.63 / 267.01（5次） | reference_or_companion_unavailable=9；eligible=542；window_not_eligible=69；anchor_pixels_changed=1 |
| `round1-pointer` | `e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6` | 15.153 | 未录到 | 未录到 | 未录到 | reference_or_companion_unavailable=10；eligible=212 |
| `round1-pointer-final` | `e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6` | 14.739 | 23.60 / 28.02（3次） | 152.34 / 326.78（5次） | 108.30 / 477.18（8次） | reference_or_companion_unavailable=9；eligible=599；anchor_pixels_changed=11；window_not_eligible=18 |
| `round1-pointer-track` | `e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6` | — | 未录到 | 未录到 | 未录到 | 无叠加判定事件 |
| `round1-ready` | `27087ec0a79e04eabc293561d9da73332aefa6f02569d97dbdff98b13d5abb55` | — | 未录到 | 未录到 | 未录到 | reference_or_companion_unavailable=1 |
| `round1-white` | `6433b6870e20864d1ba4609b5192bc3d484e96fd1caedaec7d02dae6639dc4d9` | 14.289 | 20.39 / 744.22（30次） | 115.83 / 115.83（1次） | 231.79 / 549.33（133次） | reference_or_companion_unavailable=8；eligible=1548；anchor_pixels_changed=411；window_not_eligible=161；page_or_map_unmatched=8 |

</details>

**3．改动文件与模块关系**

| 范围 | 文件与实际改动 |
|---|---|
| 统一叠加 | rouge/player_game_map.py：识别结果校验、投影、绘制、区域遮罩、命中、小卡和导航所有权集中；对外保留开关/类型/关闭等小接口 |
| 帧与光标 | rouge/software_pointer.py、capture.py、frame_buffer.py、app.py：在内存学习游戏绘制光标，每帧保留其确认范围，参考帧与当前帧分别排除相交节点文字；初始化属性直访 |
| 类型与统计 | rouge/player_map.py、public_node_statistics.py：类型状态双向同步；明确零计数保留 |
| 网页与绑定 | player_reference_links.py、tomimi_view.py、player_reference_window.py、player_game_binding.py、player_compact.py：复用共享阅读窗，网址栏、缓存及地图撤下独立保留 |
| 检查与许可 | tests/test_map_overlay_video.py、test_software_pointer.py、test_frame_buffer.py、test_sampling_flow.py、test_overlay_display.py；pynput1.8.1及LGPL说明 |
| 项目记录 | requirements/pyproject、VIDEO_PARITY、项目要求/待办/完成范围/断点/在制记录、决定、回执和云端索引 |

{file_details}

| 合并前调用 | 合并后调用 |
|---|---|
| app→payload→OverlaySurface；白色地图单向设类型 | app提供参考/本局数据→GameMapOverlay统一payload→投影/绘制/交互；kindChanged双向同步 |
| GameMapOverlay→HoverGate→PreviewMapView→自动打开大NodeHoverCard | GameMapOverlay→InteractionSurface→点击NodeCard；更多才构造原大资料卡 |
| 各阅读入口各自处理网页 | 小卡→player_reference_links→原TomimiPanel与共享ReferenceWindow |

删掉探索层自动悬停计时、重复命中排序及为小卡创建的隐藏PreviewMapView。map_projection.py提供固定战斗地图投影，不在探索调用链，没有无依据合并。白色地图和“更多”保留原阅读能力。成熟代码采用pynput只读监听及Qt原生遮罩；来源、固定版本、许可见[实现决定](../decisions/2026-11-03-overlay-video-controls.md)。

检查结论：102项前版定向通过；最后光标/缓冲/采样29项、卡片12项通过，存在重叠，不能相加当作143项不同检查。两项offscreen窗口尺寸失败在a6基线上复现，保留为原失败。此次报告没有修改产品源码，不重跑产品测试，不恢复全量。

**4．数据对应不上的位置与统计含义**

现有公开数据按“楼层＋距入口最短步数＋类型”汇总，没有模板内每个具体节点的独立计数。已匹配模板位置可唯一选择它所属的历史桶；多个位置可以共用一个桶。这回答的是同层同距离的历史频率，不能当作该具体位置的独立频率，更不是本局条件概率。

| 位置/数据情况 | 展示与现有结论 |
|---|---|
| 模板、节点ID、行列和距离相符 | 可选择对应历史桶；多位置共享桶的口径放来源说明 |
| 模板未匹配、ID重复、行列/距离与模板不符 | 不放数字，小卡“暂无资料”；定向检查覆盖 |
| 桶中没有此类型记录 | 显示“—”，不补成0 |
| 明确记录零计数且分母有效 | 显示0% |
| 已揭示、经过、固定节点 | 不显示候选历史百分比；小卡保留已读/原类型/模板依据 |
| 实机位置清单 | 保存的早期20位置快照未发现模板位置绑定失败；最后轮没有逐点图像真值，尚不能提交一份完整的最终错漏位置清单。实际位置与本机图像只保留在本地附录 |

这里有一项需要用户明确取舍：**是否允许把“同层同距离的聚合历史频率”放在具体节点旁，并在小卡中说明共享口径。** 如果要求每个具体位置独立统计，现有数据不足，应撤下这些数字或另找含模板位置的数据。当前代码采用前一种口径，本报告把区别列明，不能把“桶能对应”写成“已具备独立位置统计”。

**5．清理a与b**

a已处理：MainWindow初始化设置compact_window=None和map_overlay_reference=None；采样入口只判断一次compact_window，后续直接访问game_overlay；参考帧直接访问。相关链的嵌套getattr移除。

| b现有分支 | 实际触发条件 | 保护什么 | 建议 |
|---|---|---|---|
| mkdir失败 | 目录无权限、同名文件占用、文件系统不可写 | 本次选择仍可生效，提示未保存 | 可与保存失败提示合并，保留一次I/O错误出口 |
| QSaveFile.open失败 | 临时文件创建失败、目标目录不可写 | 不截断已保存设置 | 保留原子写入，合并提示 |
| write/commit失败 | 写入不全、空间不足、提交重命名失败等 | 丢弃未提交内容，保留旧文件 | 保留 |
| 读取/格式失败 | 读失败、JSON损坏或enabled类型不符 | 不覆盖损坏文件，不把明确设置改成默认开启 | 保留 |

四类分支本单均未删除，等待用户确认。FileNotFoundError是首次运行正常情况，默认开启；不属于损坏文件。

**6．提交与云端**

功能提交c3c50b5d2；文档行尾整理c31f7b6f1。之前已普通推送main，并核对32个公开文件与抓取的远端blob逐字节相同。本报告及第一轮新增记录随本次文档提交更新索引；实际新提交号在交付回复中给出，不预填未来哈希。源代码、本局记忆与私人设置在报告批次保持。

**7．未完成与需决定事项**

- 补最后源码的类型/小卡对照图；采集器提前退出的缺图由本次采集承担，不把用户已做的交互说成没做。
- 真实作战网页、第二个大窗口、切页返回、卡片失焦；完成落点错节点/漏显/误显计数。
- 决定同层同距离聚合频率能否放到具体节点旁；决定b四类设置保护如何精简。未获决定前保持现有实现与保护。
- 800×600识别、缩放恢复慢和高负载短页覆盖留在既有待办，本单没有处理。历史频率之外的本局概率、缩略图与事件图留后续。

这份报告的交付结论是“首轮交互已记录，整体验收未完成”，第473节不销项。
