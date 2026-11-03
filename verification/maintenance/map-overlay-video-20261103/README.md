# 探索叠加在制回执

当前完成至472；473在制。光标遮挡修正版的移入与来源展开已获用户实测确认，完整两轮验收尚待完成。

1. 开关/样式：本节沿用a6默认开启与用户明确关闭持久化；新增游戏左侧类型入口，和白色地图共用状态。白字已确认清楚。卡片仅点击打开，更多才开原大资料面板。
2. 原因：旧普通点击能命中节点，但光标改变文字像素，相关度约0.53—0.64，触发撤下。实机原图确认系统光标隐藏、游戏仍画光标。逐帧检测/跟踪光标，仅排除相交节点文字；保留标题及至少三个未遮挡节点，原所有数值门槛不改。修正版日志在保留14个锚点时继续通过，用户可进入并展开。
3. 数据：每个已确认的模板位置按楼层/距离选到一个历史桶；多个位置可共享同一个聚合桶，来源展开写明。模板、ID、行列或距离对不上的位置不显示数字。0计数和缺记录分别为0%和—。当前实际图已匹配，但其它图/未配准位置仍需核对。
4. 架构/清理：见[决定与前后调用表](../../../docs/decisions/2026-11-03-overlay-video-controls.md)。清理a已在初始化设置属性、采样时直接访问；清理b的mkdir、open、write/commit、读取/格式四类分支未改，逐项触发及保护见同文，待用户决定。引入pynput1.8.1只读左键监听，保留LGPL许可；未增加游戏输入。
5. 定向检查：102项前版检查通过；后续光标/缓冲/采样29项、网格及阅读状态12项通过。原失败、代码摘要、对应退出见summary.json。两项offscreen窗口尺寸断言在a6基线上同样失败，未计通过。无全量。
6. 实机缺口：最后源码两轮完整路径、真实关卡网页、切页与小卡失焦、第二大窗口以及错节点/漏显/误显的独立真值计数。冷启动和热切换已有记录；未完成量不写0。未到达网页场景，没有hd_100实机图。
7. 本机截图对照：comparisons/type-old-white.png对hd_70，类型胶囊及白字已出现，旧版文字重叠后来加暗底；comparisons/card-cursor-fixed-clipped.png对hd_85，光标修正可移入，但该轮网格被压缩，与原片不一致。随后已修复网格高度及保持展开状态，最后源码待两轮截图。日志、图和原始对局仅.local，Git只保存汇总。

指标表中的reason是记录事件次数，不是时间占比。冷启动列为启动到首次交互；round1-final包含等待前台约27分钟，不作冷启动性能样本。热状态列含类型取消和无数字类别，详见runs.json各次原始时长；不能当作每次均出现数字。round1-white唯一card_painted为自有窗口诊断115.83毫秒，不计普通玩家；round1-pointer-final已记录真实点击与用户确认。所有轮次保留，不挑最好值。

| 轮次 | 叠加源码SHA256 | 首次交互 | 类型到绘制：中位/p95 | reason分布 |
|---|---|---|---|---|
|round1|e7f04e209e65e6a32de158c0c5f6a12bce451b9c6ba70916b35cbbcab938154f|—|—|{'reference_or_companion_unavailable': 9, 'window_not_eligible': 165}|
|round1-card-layout|18e9f4a02da498c34060dee2d1032f23eda027b127901f9866ec21efcac0f98b|14.843秒|—|{'reference_or_companion_unavailable': 9, 'eligible': 248}|
|round1-final|af87c65f05e29dc96be1ade53210a7fe4ac9941dba1a0608b5eccc386b5d3628|1631.196秒|—|{'reference_or_companion_unavailable': 9, 'window_not_eligible': 1266, 'eligible': 72, 'anchor_pixels_changed': 7}|
|round1-hotspots|a1f3010e5c7587fe11a28976177c8737a97233db6605dd9aee913afa31be9f4a|14.182秒|29.05/338.83毫秒|{'reference_or_companion_unavailable': 8, 'eligible': 1070, 'window_not_eligible': 71, 'anchor_pixels_changed': 63}|
|round1-native|27087ec0a79e04eabc293561d9da73332aefa6f02569d97dbdff98b13d5abb55|13.503秒|25.57/124.43毫秒|{'reference_or_companion_unavailable': 9, 'eligible': 542, 'window_not_eligible': 69, 'anchor_pixels_changed': 1}|
|round1-pointer|e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6|15.153秒|—|{'reference_or_companion_unavailable': 10, 'eligible': 212}|
|round1-pointer-final|e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6|14.739秒|24.79/28.14毫秒|{'reference_or_companion_unavailable': 9, 'eligible': 599, 'anchor_pixels_changed': 11, 'window_not_eligible': 18}|
|round1-pointer-track|e976249f1084b288d67d71186d7737ad113704e992b75f5e489506d4875958b6|—|—|{}|
|round1-ready|27087ec0a79e04eabc293561d9da73332aefa6f02569d97dbdff98b13d5abb55|—|—|{'reference_or_companion_unavailable': 1}|
|round1-white|6433b6870e20864d1ba4609b5192bc3d484e96fd1caedaec7d02dae6639dc4d9|14.289秒|20.39/410.70毫秒|{'reference_or_companion_unavailable': 8, 'eligible': 1548, 'anchor_pixels_changed': 411, 'window_not_eligible': 161, 'page_or_map_unmatched': 8}|

提交身份由包含本回执的提交绑定；远端核对记录保存在本机，不预填未来提交号。
