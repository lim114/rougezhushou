# 笔记目录重复计算精简，D28待确认

已完成：catalogue_snapshot每次构建只生成一次关卡类型对照表；NoteLibraryPanel.refresh每条笔记路径只转一次文字，供条目身份和选择恢复共用。没有新增辅助函数。调用核对显示reference_context多处使用，_regular跨模块复用，未机械内联。

D28待确认：refresh当前将文件扫描与notice.setText一起捕获。隔离测试复现内部ValueError被当成扫描失败，1项失败；原try/except的AST保持不变。建议仅捕获library.rows，成功提示移到捕获外。用户批准前不执行，不计整改通过。拟用测试在本机.local/code-constraints-review-16/pending_boundary_case.py。

独立改动19项原生定向通过：选择器4项、资料部分缺失1项、共享笔记目录6项、笔记存储目录5项、扫描3项。覆盖分类、选择/阅读保留、资料缺失、读失败、搜索与共享窗口；未执行D28拟整改后的通过验收，未运行全量检查。

原项目测试窗口正常关闭并重新启动，工具条截图确认可见，单次窗口响应56.23ms，stderr为空；不作为流畅度验收。截图与原始日志留本机.local/code-constraints-review-16/。

[进度看板](PROGRESS.md)：426结构、77异常等价、54部分路径、1整模块，共558，数量不变。本轮只深化已有路径，不增加功能节。
