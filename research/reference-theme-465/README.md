# 第465节 + 商店挑战同窗查阅与分层配色

商店挑战、坎诺特与保险柜在主资料窗连续查阅，关联入口直达对应敌人或奖励，返回保留选择与阅读。资料页改为视频中的深灰色，藏品页保留黑灰与浅绿名称，地图和笔记保持浅色；精简商店挑战的说明、按钮和分支名称。

42项定向检查、83项原生窗口检查通过；七张最终窗口图已核对，测试窗口已更新。

[复用](reuse.json) · [修正记录](issues.json) · [机制依据](mechanism-evidence.json) · [视频配色](video-colors.json) · [验收](../../verification/sections/465.json)。

主题生成使用已核对的PyQtDarkTheme2.1.0本地源码和公开的theme-build-source.py，传入runtime、output与baseline-light参数。保留原有52份图标以兼容已有样式；当前全部静态资源字节列于rouge/data/player-theme/source.json。

继续整合其余深层入口和完整工作区，逐页校正布局、字体、图标与交互；识别覆盖及耗时同步推进。
