# 探索叠加第一版：类型、历史频率、小卡和网页

用户于11月3日确认：本批对照原片01:03—01:24及本机hd_70、hd_85、hd_100。完成能力后按实际改动记第473节；未验收范围继续在待办。

- 百分比只用路标Wiki公开历史频率，标签写“历史频率”，来源日期/口径可展开。结合本局条件的概率保留后续。
- 客户区左边缘只增加可滚动类型胶囊，点选高亮、再次取消。下方定位/放大属于游戏原有按钮，用户确认保留原按钮，不覆盖、不代操作。
- 百分比仅用于`overlay_rows`判为candidate的位置。已揭示、经过、固定节点不显示频率；证据强弱移入小卡。已记录零计数且分母非零显示0%，没有记录显示—，位置绑定不足显示“暂无资料”。
- 小卡第一版为类型/历史频率三列网格、来源日期、敌方情报/地图、更多。深色半透明圆角，卡外点击关闭；Esc只处理助手收到的按键，不注册游戏Esc。缩略图、种子固定节点和事件缩略图不做。
- 原大资料卡改由更多入口打开。网页用原TomimiPanel、ToolPage/ReferenceWindow及共享导航入口，显示网址栏并居中，不另建浏览器实现。实际关卡标题/变体未绑定时，按钮标关卡待确认。
- 绘制窗口全部点击穿透；独立交互窗口用Qt原生区域遮罩，仅类型胶囊、节点热区和小卡接收鼠标，不转发游戏输入。绘制、交互和卡片共用一次payload结果；拒绝一起撤下，网页独立保留。30秒/2秒、0.99和0.9—1.1均不改。

## 11月3日收尾确认的三项决定

1. 同意在具体节点旁显示同层、距入口最短步数相同的共用历史频率。小卡来源现有共用说明保留；独立点位统计不再列为473缺口，本局条件概率留后续。原片hd_70多个位置同时显示27.11%与25.16%，用户已核对为相同口径。
2. 保留pynput，但仅小卡打开期间创建并启动Listener；换卡不重复安装。卡外、助手Esc、叠加撤下及窗口关闭统一stop并join，清空引用；启动和无卡时不装全局鼠标钩子。回调只发队列信号，不操作游戏。实机记录实际安装/卸载、满载识别时的点击响应与卡外关闭；低级钩子超时可被Windows静默摘除，线程running不能当作仍在系统安装的证据。
3. 保留QSaveFile原子保存的open/write/commit和损坏文件不覆盖、不误开启的保护。mkdir和open失败合并为一个I/O失败出口和同一句提示；FileNotFoundError首次运行路径保持。

官方依据：[pynput监听线程与停止后新建规则](https://pynput.readthedocs.io/en/latest/mouse.html#the-mouse-listener-thread)、[微软低级鼠标钩子与超时移除说明](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc)。本地核对固定pynput1.8.1源码；stop后join用于等待其SystemHook退出、完成UnhookWindowsHookEx，而非重用停止的线程。

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

## 清理b：按用户决定落实

| 分支 | 处理 | 保留的保护 |
|---|---|---|
| mkdir / open失败 | 一个I/O失败出口，同一句文件/目录权限提示 | 目录创建或临时文件打开失败时不截断旧设置 |
| write / commit失败 | 保留QSaveFile、cancelWriting及原失败出口 | 写入不全、磁盘/提交失败时保留旧设置 |
| 读取 / 格式失败 | 保留readable=False及不覆盖 | 不把损坏设置改成默认开启 |
| FileNotFoundError | 原首次启动正常路径不变 | 未保存时默认开启 |

## 成熟方案与来源

评估了[CrossHairLIN](https://github.com/liuroland55/CrossHairLIN)（PySide6、MIT，自述全窗穿透/交互切换）与[koverlay](https://github.com/erik96/koverlay)（MIT、Wayland）。前者的整窗切换不能直接满足局部热区，后者不适用Windows；未复制其源码。绘制和局部穿透使用Qt6的[窗口类型](https://doc.qt.io/qt-6/qt.html#WindowType-enum)与[区域遮罩](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.QWidget.setMask)，图集、统计与网页阅读器沿用项目实现。

卡外点击采用成熟的[pynput鼠标监听](https://pynput.readthedocs.io/en/latest/mouse.html#monitoring-the-mouse)，固定1.8.1，仅Windows依赖，LGPLv3许可保存在`licenses/pynput-1.8.1-LGPL.txt`。核对PyPI wheel源码后安装，SHA256为`42dfcf27404459ca16ca889c8fb8ffe42a9fe54f722fd1a3e130728e59e768d2`。仅小卡打开时创建监听器，处理左键按下，`suppress=False`；关闭卡片时stop/join并释放，不创建输入控制器，不注册移动回调或键盘钩子。低级钩子自身仍接收系统鼠标事件，其同步/GIL风险按上面的实测要求核验；Esc只由助手自身Qt事件处理。

## 游戏光标遮挡

实机的Windows系统光标为隐藏状态，但WGC原始图仍有游戏绘制的白色光标（本次量得亮色主体52×60物理像素）。`cursor_capture=False`只影响系统光标，不能去掉画面内图案。点击节点时原有文字锚点相关度降至约0.53–0.64，触发原门槛撤下。

复用OpenCV的[连通域与形状工具](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html)确认原生鼠标位置上的尖头亮色图形，在内存中学习其像素；后续用带遮罩的模板匹配跟踪，包括鼠标进入助手后留在游戏画面上的光标。原生位置由[GetCursorInfo](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorinfo)读取，按采样时物理客户区映射。未确认图形不提供排除范围；不按鼠标周围任意半径忽略变化。

光标范围与各自帧一起传递和保留。核对时只排除参考帧或当前帧光标实际相交的节点文字，标题始终参与，仍需标题加至少三个未遮挡节点；原30秒/2秒、0.99相关度和0.9–1.1对比度不变。模板只保存在进程内，不把私人采样制作成仓库资产。该规则的局部样本与实机交互分别验收。

截图、逐轮日志及源码摘要只存本机.local；公开回执保留汇总和未通过范围，不上传本局内容。
