# D28：笔记目录扫描异常边界收窄

用户明确批准后，NoteLibraryPanel.refresh只捕获library.rows(query)的OSError/ValueError；搜索框读取置于try之前，成功提示置于else中。扫描错误仍清空目录并提示原因；界面错误直接暴露。未增加辅助函数、检查或重试，不改变笔记原件。

9项原生定向通过：新增边界2项、共享目录6项、搜索合并1项。验证界面提示/搜索框错误不再被当成文件扫描失败，文件读取失败仍显示原因且原件不改，选择/阅读/草稿及搜索行为保持。上一批1项失败基线保留，未重写历史回执，未运行全量检查。

原项目窗口正常退出并重开，工具条截图已确认可见、响应，stderr为空；单次窗口响应878.36ms，不作为持续流畅度验收。截图和原始日志只留本机.local/code-constraints-review-17/。

源码：[player_note_library.py](../../../rouge/player_note_library.py)；测试：[test_note_library_boundary_review.py](../../../tests/test_note_library_boundary_review.py)。[进度](PROGRESS.md)仍为426/77/54/1共558。D28从待办销项，其余未审路径继续；本批不增加功能节。
