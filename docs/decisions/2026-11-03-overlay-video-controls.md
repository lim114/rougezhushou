# 探索叠加第一版：类型、历史频率、小卡和网页

用户于11月3日确认：本批对照原片01:03—01:24及本机hd_70、hd_85、hd_100。完成能力后按实际改动记第473节；未验收范围继续在待办。

- 百分比只用路标Wiki公开历史频率，标签写“历史频率”，来源日期/口径可展开。结合本局条件的概率保留后续。
- 客户区左边缘只增加可滚动类型胶囊，点选高亮、再次取消。下方定位/放大属于游戏原有按钮，用户确认保留原按钮，不覆盖、不代操作。
- 百分比仅用于`overlay_rows`判为candidate的位置。已揭示、经过、固定节点不显示频率；证据强弱移入小卡。已记录零计数且分母非零显示0%，没有记录显示—，位置绑定不足显示“暂无资料”。
- 小卡第一版为类型/历史频率三列网格、来源日期、敌方情报/地图、更多。深色半透明圆角，卡外点击关闭；Esc只处理助手收到的按键，不注册游戏Esc。缩略图、种子固定节点和事件缩略图不做。
- 原大资料卡改由更多入口打开。网页用原TomimiPanel、ToolPage/ReferenceWindow及共享导航入口，显示网址栏并居中，不另建浏览器实现。实际关卡标题/变体未绑定时，按钮标关卡待确认。
- 绘制窗口全部点击穿透；独立交互窗口用Qt原生区域遮罩，仅类型胶囊、节点热区和小卡接收鼠标，不转发游戏输入。绘制、交互和卡片共用一次payload结果；拒绝一起撤下，网页独立保留。30秒/2秒、0.99和0.9—1.1均不改。

## 统计与位置

现有FrequencyIndex按层和距入口步数分桶，并非按模板内每一个位置单独统计。模板构建使用从入口广度优先遍历的最短距离。画面唯一匹配模板后，节点ID、行列、距离须与来源模板一致，才能把该桶频率映射到此节点；多个节点可以对应同一个桶，不将它们伪装为独立位置统计。模板/距离不能对应的不显示数字。分母仍是同层同距离全部节点，不在当前候选中重新归一化。

## 模块调用关系

| 合并前 | 合并后 |
|---|---|
| app识别结果→GameMapOverlay.payload→OverlaySurface | app只提供参考帧/本局数据→GameMapOverlay→原payload→统一投影结果 |
| 白色MapPanel单向调用set_kind | GameMapOverlay持有类型状态；kindChanged与MapPanel双向同步 |
| GameMapOverlay→HoverGate→PreviewMapView→NodeHoverCard，悬停自动打开大卡 | 同一模块内绘制→区域遮罩/命中→NodeCard；更多才构造原大卡 |
| 关卡阅读器各自跳网页 | 小卡数据→player_reference_links→原TomimiPanel和共享ReferenceWindow |

移除探索游戏层自动悬停计时、悬停位置计算及为了普通小卡而创建的PreviewMapView/大卡；深资料与白色地图各自现有阅读能力保留。`map_projection.py`是固定战斗地图投影，不在探索链上，不合并。绘制/命中/小卡实例的所有权集中在GameMapOverlay；白色地图不是第二套游戏叠加。

## 清理a：确定的属性

MainWindow初始化直接设置compact_window=None、map_overlay_reference=None。采样入口只判断compact_window是否已经创建，其后直接访问game_overlay；参考帧直接访问。移除该链的嵌套getattr及接收结果时的重复getattr。

## 清理b：本批保留，等待用户确认

| 现有分支 | 触发条件 | 保护范围 | 后续取舍建议 |
|---|---|---|---|
| mkdir失败 | 本地目录无权限、被同名文件占用或不可写 | 用户切开关仍可在当前进程生效；提示无法保存 | 可保留保存入口的单一I/O失败提示，合并重复文案 |
| QSaveFile.open失败 | 临时文件不能创建或目标目录不可写 | 不截断已保存设置 | 保留原子保存方式；可与前项合并报告 |
| write/commit失败 | 写入不全、提交重命名失败、空间不足等 | 丢弃未提交临时文件，保留旧设置 | 建议保留；失败后声称已保存会丢失明确关闭意图 |
| 读取/格式失败 | 文件读失败、JSON损坏、enabled不是布尔值 | 不把损坏文件覆盖成默认值，不误开启叠加 | 建议保留不覆盖保护，可再简化报错路径 |

FileNotFoundError是首次启动的正常路径，不属于“文件损坏”；该路径默认开启。本单不删除、添加或改写这些失败分支。

## 成熟方案与来源

评估了[CrossHairLIN](https://github.com/liuroland55/CrossHairLIN)（PySide6、MIT，自述全窗穿透/交互切换）与[koverlay](https://github.com/erik96/koverlay)（MIT、Wayland）。前者的整窗切换不能直接满足局部热区，后者不适用Windows；未复制其源码。绘制和局部穿透使用Qt6的[窗口类型](https://doc.qt.io/qt-6/qt.html#WindowType-enum)与[区域遮罩](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.QWidget.setMask)，图集、统计与网页阅读器沿用项目实现。

卡外点击采用成熟的[pynput鼠标监听](https://pynput.readthedocs.io/en/latest/mouse.html#monitoring-the-mouse)，固定1.8.1，仅Windows依赖，LGPLv3许可保存在`licenses/pynput-1.8.1-LGPL.txt`。核对PyPI wheel源码后安装，SHA256为`42dfcf27404459ca16ca889c8fb8ffe42a9fe54f722fd1a3e130728e59e768d2`。仅监听左键按下，`suppress=False`，不创建输入控制器、不监听移动或键盘，退出时停止。替代轮询按键状态，避免漏掉短点击；Esc仍只由助手自身Qt事件处理。

## 游戏光标遮挡

实机的Windows系统光标为隐藏状态，但WGC原始图仍有游戏绘制的白色光标（本次量得亮色主体52×60物理像素）。`cursor_capture=False`只影响系统光标，不能去掉画面内图案。点击节点时原有文字锚点相关度降至约0.53–0.64，触发原门槛撤下。

复用OpenCV的[连通域与形状工具](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html)确认原生鼠标位置上的尖头亮色图形，在内存中学习其像素；后续用带遮罩的模板匹配跟踪，包括鼠标进入助手后留在游戏画面上的光标。原生位置由[GetCursorInfo](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorinfo)读取，按采样时物理客户区映射。未确认图形不提供排除范围；不按鼠标周围任意半径忽略变化。

光标范围与各自帧一起传递和保留。核对时只排除参考帧或当前帧光标实际相交的节点文字，标题始终参与，仍需标题加至少三个未遮挡节点；原30秒/2秒、0.99相关度和0.9–1.1对比度不变。模板只保存在进程内，不把私人采样制作成仓库资产。该规则的局部样本与实机交互分别验收。

截图、逐轮日志及源码摘要只存本机.local；公开回执保留汇总和未通过范围，不上传本局内容。
