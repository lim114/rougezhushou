# 101 原实现 char-buff Qt 探针独立 Source 审阅

结论：冻结探针未发现 Source blocker，可交 Root 实际运行。仅原实现观察，不是产品验收；本审未 import/执行任何 project、Qt、Wine、helper、codec、tests 或 Git，未改 tracked/产品或读私有数据。

独立标准库工具 `407c06` primary 0 实读并 `compile(source,path,'exec')`、AST parse（不执行模块）：`probe101.py` 11109 B / `933b8181cf70cb5ddb666c0be6d614a6be02153ff9a74b5af8cbce477755f471`；`source-manifest.json` 526 B / `fa01bf95f3e6a852c060ea00a38d86543a1cc6bf894c3c61fe44ed85d985b64b`。`fa744c` primary 0 复核实际 app 99596 B / `34f0c92061460b239fd0af80ec263673765a16753826f6151fde87a88b89a35b`，training_view 6050 B / `5bef7b6f03592a5df615711568d116a0ffd9170f9be99832ca75d9eee78fcdb4`；本审未改其 bytes。

Source 观察：

- 项目 import 前比较全部原实现 Source map 与 Root guard，要求743项且 app/view hashes 与指定原实现一致；最后再次比较 Source map。out 必须 fresh、在 repo 外。
- 三项 public fixture 为 healthy SNACK、未知 bound ID、未知 pending ID；均先构造真实 RunState，要求原 JSON 被接受、成员等于原 public fixture、run raw disk 未变，再构造真实 MainWindow。unknown ID 为明确公共占位，不宣称有效机制。
- 每窗 account/run/settings 在新的 TemporaryDirectory，DesktopBackend 只重定向路径保留真实对象；关闭采样/计时器并校核无 sample/chat/request busy、无 desktop process/pending。没有连接游戏、采样或聊天请求路径。默认保存路径在窗口构造前均已替换。
- 真实 mechanist/S3、SNACK 的 healthy case 必须产生已有规则的 SP28，且无新增 Qt hook exception；失败会抛出并标 probe_failure。unknown 两项允许真实失败，分别保存 sys.excepthook 的 Qt signal exception 和 try/except 的 direct constructor/call exception，不预填成功或错误类型。
- Qt/processEvents/实际 calculate 都是将由 Root 执行的真实调用，未用模拟数值或假的成功 setter。row 收集实际 UI status、damage_result、level、metadata；该 JSON 观察不宣称 native alias/所有类型无损比较。
- finally 关闭真实顶层 MainWindow，再检查 account/run 原 bytes 和 tmp absence，保留每项 hook 记录。异常 traceback 保留实际调用栈；Root 应区分目标 label 异常与 cleanup 中可能记录的异常，不能只靠 case 的 exception 总数判定因果。
- 300 秒 watchdog 在项目/Qt import 前启动，超时写片段并退出124。最终 observations 只有在3项完成、最后 Source guard一致时设置 observation_complete；product_pass 始终 False。Root仍须保留真实primary exit、日志和观察JSON，primary0/observation_complete不代表修复或产品PASS。

本次只认可探针 Source 控制及绑定。未查看或生成实际观察记录，未宣称未知 buff 导致的 Qt/constructor 结果已被本审复现；实际原实现复现及后续候选须独立留档。
