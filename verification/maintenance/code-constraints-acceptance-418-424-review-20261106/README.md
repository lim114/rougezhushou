# 维护：418—424验收源码

七份文件全文、player_acceptance分派和player_ui_verification.require调用契约已核对。421中连续两次读取currentItem合并，中间require只判定/记名，不处理事件或改变选择；422去掉map_data/predict_map/snapshot_text未使用导入；424去掉未使用Qt导入。assert/require属于验收需求，未删；被编辑、等待、刷新隔开的读取保留。

419/420/421/424按三条代码规则完成回顾。418/422/423的finally清理与恢复D308待审；418重复释放不借此次普通清理删除。所有check均是实际分派入口，无无意义单次包装。

只编译七文件并核对check(window,gui,require)入口，没有执行历史验收、全量或游戏操作。该证据不证明旧功能在当前源码重新通过实机。测试窗口按批次更新并核对可见/响应，日志截图仅.local/code-constraints-review-140/，未改旧验收记录。

完整60、部分184、仅异常40、结构274，共558（目录内包括这些验收模块）；待审271组。
