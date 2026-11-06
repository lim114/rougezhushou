# 维护：出怪与物件对话框统一单次清理

三个对话框CurrentEnemySpawnsDialog、CurrentStageObjectsDialog、CurrentObjectPositionDialog原closeEvent与done重复clear_reference。Windows Qt本机探针实测close各2次，reject/accept各1次；删除closeEvent包装后各路径均1次、窗口隐藏、资料清空。物件父面板close_children删除调用子窗close之前的额外clear_reference，子窗done承担清理。

未删除来源失效、图片处理或动作定位保护；本批只认证关闭路径，模块其它路径未完成。未新增函数或异常捕获。

定向27项首次26通过1失败（40.351秒）；失败为旧文案“尚未核验”不符当前“待补齐本局修正”。加载修改前两个源模块复测同一失败（0.809秒）。仅更新测试的该文案断言，单项重跑通过（0.704秒），其余26项源码未再改变复用原证据。不能称首次27全通过。测试模块包含offscreen设置，窗口实机确认和前后计数由独立本机进程完成；未做游戏会话验收、未跑全量。

测试窗口已更新，原始记录截图仅.local/code-constraints-review-115/。全模块47、部分151、仅异常48、结构312；189组待审不变。下一步继续这些面板的选项读取重复和来源保护范围。
