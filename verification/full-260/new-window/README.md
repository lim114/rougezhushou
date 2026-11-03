# 真实主窗口238–260工作流

独立工作目录，只写脚本与回执，不改生产。仅在根代理宣布源码冻结后运行 `bash work/full260-current-window/run-window.sh PHASE`，使用真实Wine11 devel Python、真实win32gui/qwindows，并经过 `scripts/wine_python.sh` 共用锁。第一次失败保留原phase，修复后使用新phase；Python断言通过还必须真实进程exit0。

`window.py` 保留238–245原13流程，并调用 `window_added_flows.py`、`window_extra_flows.py` 检查246–260全部15节的实际MainWindow入口、控件信号、字面量输出、独立输入/草稿/阅读状态刷新保留、未知和反例。科技目标使用真实modal，移动来源按钮实际导航目录，果标引用实际显示主窗地图说明。各节保存模型原输出及必要界面截图。

RUN_STATE、OPERATOR_STATE、SETTINGS和DesktopBackend均重定向到临时目录。自动采集关闭、capture.target无绑定、桌面后端process为空；不操作游戏、不发送聊天、不访问原用户运行状态。实际Qt应用销毁后再保存退出回执。真实Windows/game验证仍不具备，此处仅Wine兼容工作流。

回执记录实际冻结工作树的rouge/scripts/tests及data哈希前后和本验证脚本哈希；HEAD仅为标签，不声称包含未提交维护。此新增流程独立于全量离线与原旧全窗口范围，不能替代或减少它们。

`preparation.json` 仅静态准备回执，含独立审查发现的两处脚本错误与修正依据，不是运行成功证据。正式输出在指定PHASE目录的 `window.json`、`execution.json`、`process.log`、逐节结果及截图。
