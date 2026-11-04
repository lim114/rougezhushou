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
2. 保留pynput，用户随后确认将监听时段扩展为“小卡打开或鼠标停在左侧类型栏”，以修复两处滚轮带动游戏缩放。共用一个Listener；离开类型栏且无小卡、叠加撤下或关闭窗口时stop并join、释放引用。启动和其余空闲时间不装钩子。仅助手这两个区域内、游戏仍在前台的滚轮会交给对应列表并拦下；游戏区域的滚轮、鼠标点击和键盘保持正常。实机记录实际安装/卸载、满载识别时的点击响应与卡外关闭；低级钩子超时可被Windows静默摘除，线程running不能当作仍在系统安装的证据。
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

卡外点击采用成熟的[pynput鼠标监听](https://pynput.readthedocs.io/en/latest/mouse.html#monitoring-the-mouse)，固定1.8.1，仅Windows依赖，LGPLv3许可保存在`licenses/pynput-1.8.1-LGPL.txt`。核对PyPI wheel源码后安装，SHA256为`42dfcf27404459ca16ca889c8fb8ffe42a9fe54f722fd1a3e130728e59e768d2`。按上面最新决定在小卡打开或悬停类型栏时共用监听器，处理左键按下及这两个区域的滚轮，`suppress=False`；两个监听条件都结束时stop/join并释放，不创建输入控制器，不注册移动回调或键盘钩子。低级钩子自身仍接收系统鼠标事件，其同步/GIL风险按上面的实测要求核验；Esc只由助手自身Qt事件处理。

## 游戏光标遮挡

实机的Windows系统光标为隐藏状态，但WGC原始图仍有游戏绘制的白色光标（本次量得亮色主体52×60物理像素）。`cursor_capture=False`只影响系统光标，不能去掉画面内图案。点击节点时原有文字锚点相关度降至约0.53–0.64，触发原门槛撤下。

复用OpenCV的[连通域与形状工具](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html)确认原生鼠标位置上的尖头亮色图形，在内存中学习其像素；后续用带遮罩的模板匹配跟踪，包括鼠标进入助手后留在游戏画面上的光标。原生位置由[GetCursorInfo](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getcursorinfo)读取，按采样时物理客户区映射。未确认图形不提供排除范围；不按鼠标周围任意半径忽略变化。

光标范围与各自帧一起传递和保留。核对时只排除参考帧或当前帧光标实际相交的节点文字，标题始终参与，仍需标题加至少三个未遮挡节点；原30秒/2秒、0.99相关度和0.9–1.1对比度不变。模板只保存在进程内，不把私人采样制作成仓库资产。该规则的局部样本与实机交互分别验收。

截图、逐轮日志及源码摘要只存本机.local；公开回执保留汇总和未通过范围，不上传本局内容。

## 收尾中的关卡绑定修正

用户实机重测仍显示关卡待确认。原图与后台结果确认标题和变体已经读到，问题在选中光圈的中心与模板图标中心略有偏移、部分弧段较暗。原算法只沿模板中心采样亮弧，没有绑定具体节点。

复用现有OpenCV的HoughCircles拟合光圈中心，在可见节点围成的区域内搜索；再用低饱和边缘核验0.65的原弧覆盖，并要求光圈只对应一个节点。无唯一结果保留待确认。属于选中身份识别修正，原payload的30秒/2秒、标题及至少三未遮挡节点、0.99与0.9—1.1不变。本机固定OpenCV版本见本次回执。方法依据[OpenCV官方霍夫圆教程](https://docs.opencv.org/4.13.0/d4/d70/tutorial_hough_circle.html)。

返回探索地图后网页入口读取同一节点已确认的remembered_content，沿用same_frame_selected_node来源、准确标题/变体核验。运行状态原有同局/地图归属规则保持；其它节点不借用该标题。13项定向检查通过，实际网页打开继续按用户操作验收。


## 两处滚轮的实机记录

用户确认类型栏和节点小卡都会出现滚轮带动游戏缩放。已同意仅在小卡打开或悬停类型栏时共用监听，离开且无卡即卸载。先用pynput的win32_event_filter处理两个区域，原Qt列表收到角度事件，键盘及卡外滚轮不变。E轮仍失败，F轮确认Qt收到普通鼠标Wheel、低级监听仅收到点击而没有对应滚轮。G轮补上助手窗口WM_MOUSEWHEEL处理，日志确认本窗已消费消息，游戏原图仍出现真实缩放。因此这条输入问题继续未通过，不能据局部单测销项。

方法来源为[pynput定向事件过滤](https://pynput.readthedocs.io/en/latest/faq.html#how-do-i-suppress-specific-events-only)、[微软WM_MOUSEWHEEL说明](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-mousewheel)与[Qt滚轮事件](https://doc.qt.io/qt-6.11/qwheelevent.html)。没有输入控制器、游戏进程注入或游戏按键/点击发送。已经向用户提出后续交互选择，答复前不改变前台判定或自动切焦点。

E/F/G未通过输入方案及测试已归档本机，产品恢复保留关卡绑定修复的D版，当前实际仍仅小卡期间监听。上面的类型栏悬停范围为用户已允许的实现范围，尚无实机通过实现。焦点取舍与PRTS403继续待办。

## 点击激活与归还焦点的最终取舍

用户随后明确接受点击助手时自然获得焦点。交互窗去掉WindowDoesNotAcceptFocus，保留WA_ShowWithoutActivating；叠加只额外允许自身交互窗处于前台，其它程序仍撤下。前台窗口句柄由BindingApi读取，原快照保留原值，探索控制器只在自身窗口前台时传入调整后的副本。payload的30秒/2秒、标题及文字阈值保持。

I轮用户实测确认两处滚动正常、游戏未缩放。该轮反馈的卡顿进一步确认为切回游戏第一次点击需重按。用户再确认，鼠标离开助手回到游戏可点击区域时可归还游戏焦点。J版在离开交互窗后80毫秒重新核对窗口与鼠标归属，仍在游戏区域且前台为自身交互窗时调用SetForegroundWindow；进入助手即取消待处理动作，关闭时停止计时器。实际结果按本轮回执记录。

类型栏和小卡直接复用Qt滚动，pynput保留小卡期间监听。新增行为依据[Qt窗口标志和显示属性](https://doc.qt.io/qt-6.11/qt.html)、[微软SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)。


## 节点点击与监听失效的最终决定

游戏节点图标保留给游戏；点击节点名称或白色百分比打开助手小卡，交互文字显示手形鼠标。卡片右上角保留“×”。卡片关闭后立即移除其窗口热区，不留下透明遮挡。

K轮两次受控移除都只摘除本助手自己的鼠标钩子。第一次随后切出前台，卡片因窗口失效撤下，不算卡外点击验收；第二次用户确认卡外点击不再关闭而“×”正常。用户明确选择保留“× / 助手Esc”作为关闭入口并记录该限制，不增加自动恢复。此试验模拟监听缺失，不代表复现Windows自身超时摘除。

K轮安装10次、成功卸载10次，其中2次是受控提前卸载；后续清理同一已摘除句柄返回失败2次，另列，不伪装成全部调用成功。助手Esc关闭2次有Qt记录；用户确认游戏自己的Esc正常。没有全局键盘钩子。

此前允许类型栏悬停期间监听属于许可范围，最终实现无需采用：用户点击自然获焦后，两处滚动使用Qt原生控件，小卡关闭时仍为0鼠标钩子。I轮用户确认两处滚轮正常、游戏不缩放；J轮用户确认归还焦点后队伍和藏品第一下即可打开。保留E/F/G失败轮次和来源。

## PRTS请求标识及等待优化

同一Qt阅读器默认标识实际403；明确的rougezhushou/0.70标识对照取得正确关卡正文。使用Qt官方QWebEngineProfile.setHttpUserAgent，在创建PRTS页面前设置；Tomimi沿用原配置，不发送本局内容。

小卡等待剖析发现本局保存逐字扫描耗时。用Python标准库re的相邻高低代理字符范围匹配替换Python逐字符迭代，保留所有原保存保护。9项定向与1464组字符边界对照通过；实际交互延迟另验，不用合成扫描速度代替。
