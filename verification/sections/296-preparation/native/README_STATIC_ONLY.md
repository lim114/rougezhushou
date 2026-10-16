# 第296节原生窗口脚本 · 缓存准备

此目录仅是脚本候选和静态检查，不是实际Windows验收。没有启动Qt、运行产品测试、操作Git或改写live文件。首次草稿保留在`first-draft/`，最终脚本的AST/compile结果在`static-compile.json`；没有把静态通过记成窗口通过。

root正式提升目标：`scripts/verify_battle_entry_references_window_296.py`。脚本只有在这个canonical路径且实际Windows运行时才导入Qt/产品；root还须在最终UI、两模型、两资料包、四集成、新测试和脚本全部冻结后，由独立进程监督器运行与清理。草案不自行启动子进程。

源码摘要以执行当时`bound_files()`实际产生的selected map为准：两份manifest的所有成员、两研究包全部文件（含SCHEMA等）、两个新模型、四集成文件、两个builder、四个新测试、脚本和所列旧依赖。既有完整433770 HTML也核前后SHA。它不是全部传递依赖已审计的声明，不预填源文件数量，不用候选SHA替代正式实际before/after。

使用295的四个临时状态路径与八个原外部入口拦截，均在MainWindow构造之前安装；关闭窗口的finally仍位于这些patch内部，避免失败清理时恢复到私人路径后写盘。只复制选定公开资料到临时source clone，不复制私人状态。负例真的向临时manifest追加字节，再恢复原字节；live原件从不改动。

主窗口要求真实1050×720客户区；dialog要求真实900×680客户区；真实HWND必须可见、不最小化并属于当前Qt PID。每条11准入身份都经真实combo变化及QTest按钮点击→BattlePreviewPanel→App→NodeCatalogPanel完整链，恰一次完整token。三条明确排除的普通版本没有可选入口，并分别重核App和NodeCatalog的拒绝，无导航副作用。波次、敌人、出怪列表、地图格、读区文本/选区/非零滚动、上下文均取实际快照核对返回后不变。没有把同名或level等价当身份。

无效验尸只显示四条配置，分开第3/4/5层和原资料的假层；完整标记/藏品说明及实际条件未知，不出现事件选择控件。两个模型分别实际临时来源失效、两读区清空、旧token/button清空、恢复未选；跨stage旧token拒绝。既有stage_context的数据/条件不变，不减少15未知。

默认120秒deadline；必要流程每步由QTimer排队，完成后仍保留到deadline，失败即时关闭。程序报告只从实际执行的require/导航/图片记录计数，不预填passed或断言N。它只证明自身窗口隐藏；进程实际退出、wrapper PID/Qt PID、运行时间、最终sources与五份私人状态由root监督器另证。

五张计划截图为代表性页面：

- event-reference-selected：一个真实事件入口选项。
- exact-event-option-opened：该选项跳转后的主窗口。
- autopsy-four-configurations：无效验尸配置说明。
- event-source-invalidated：事件模型临时来源失败。
- configuration-source-invalidated：配置模型临时来源失败。

实际运行只有保存成功才append截图并计数；不声称八张关卡都有独立截图。

receipt.kind为`isolated_native_windows_fixed_battle_entry_references`。实际列表位于`navigated_documented_entries`、`explicit_exclusions`、`source_negative_fixtures`、`same_scope_refresh_observations`；`public_observations`为单对象列表，含实际stage IDs/click数/排除数/配置读数/刷新路径/损坏的临时模型及实际游戏进入未知。这些记录未执行时保持空，不用预估N冒充实测。

静态核对时曾把事件data路径误写为`battle-event-entry-references.json`作只读查询，Get-Content实际报不存在；随后按模型常量核对到`battle-event-references.json`。这不是产品测试或GUI失败；原工具错误保留在本会话输出，未另行封存完整原始工具响应，也未重演充原件。

root的玩家页标题仍可能改善；最终执行前只需按冻结UI复核语义断言与API，不能为了通过把实际720尺寸、11条点击或失效清理断言降级。
