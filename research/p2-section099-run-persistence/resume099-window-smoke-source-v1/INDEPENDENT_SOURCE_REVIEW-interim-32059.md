# 第 99 节 bounded actual-window smoke 独立 Source 审阅

结论：本次实际读取的最新 runner 在指定公开夹具和调用范围内未发现新的 Source blocker，可交给 Root 进行实际运行；这不是窗口、测试或工程通过。初始 31721 B / `1de3ed...` 不是本次最终绑定：作者在审阅期间修正空总览 snapshot 对有成员 getter 的误调用，本报告重新读取并编译了下表最新版本。

| 文件 | bytes | SHA256 |
|---|---:|---|
| `window.py` | 32059 | `806c0d66c3a3ee5d8aed73589a0adc7ef8954b9026beed0a813cfc73246ee8ec` |
| `native_evidence.py` | 6468 | `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a` |

文件目录为 `/workspace/.continuation/resume099-window-smoke-source-v1/`。独立实际标准库 `compile(bytes,path,'exec')`（没有 exec 结果或导入模块）工具 `e726fe` primary 0；此前初版同样仅 compile 的工具 `9ed8e1` primary 0 不替代最新绑定。最新 helper 与 `/workspace/.continuation/resume097-window-smoke-source-v1/native_evidence.py` 独立全字节比较相等。没有运行 runner、helper/codec、项目、tests、Qt、Wine、Git、采样或聊天，没有读取私人状态；仅只读公开 Source 和仓库外本报告写入。

## 启动资格、闭包和隔离

1. 主入口在 import numpy/Qt/rouge 之前读取 source guard，要求 section==99、完整 maintained source_map 与 guard 的 source_sha256 字典精确相等，且 run_state.py 为 `1b6f66e7f864238880c5214f431da042e94c7fd7def8103352439609bbfd35d9`。未以单个核心 hash 冒充全部 source；运行前后重新核对维护源码并记录 drift。Root 必须提供真实已应用 98/99 的完整新 guard，旧当前产品不满足该门。
2. `application/module/window/active_folder/run_path/account_path` 均在 main 外层先绑定；fresh 的 nonlocal 有合法闭包对象。Source compile 已实际检查语法/绑定，不只做 AST。`import rouge.app as module` 在同一外层作用域，后续 nested 函数正常引用；没有替换真实 MainWindow、RunState 或数值算法。
3. 每个 fresh 先将账户、本局、SETTINGS 全部重指向对应公开 TemporaryDirectory，DesktopBackend factory 仍调用原类，只把 chat 目录隔离。真正账户和 run fixture 为显式 ASCII JSON 公共内容；restart 的 fresh 不重新写 fixture，保留失败路径原盘与 sentinel。输出路径先 resolve，禁止在 repo 内且必须不存在；记录目录也是新鲜目录。
4. MainWindow 构造后明确取消自动采样、停 timer、关闭 collecting，不连接游戏；process 每步检查 visible、auto/timer/target/collecting、desktop process/chat/busy 状态和不存在 chat 文件夹。没有点击任何聊天/连接/采样按钮，手动公开 sample_received 只交付内存制造的 numpy 零图和固定 observation；不调用 reader/OCR 或游戏操作。私有 settings/记录在构造前已隔离，desktop 原类 __init__ 仅保留目录和回调，未启动进程。
5. 最新 snapshot 在无选定 operator 的空总览中不调用 training_conditions/skill_rank_value，记 `None` 与 `training_getters_invoked=False`；真实成员窗口才调用原 getter。current_operator_state(None)、widget getters 和摘要仍如实记录。这个修正避免将 runner 自身的无 profile getter 条件误报成 reset 产品错误，未 mock 或改变产品。

## Native evidence 与代理可达

6. helper 只接受 exact None/bool/int/float/str/bytes/dict/list/tuple；validate 遍历共享/循环图，freeze 的 pickle protocol4 往返后检查类型、浮点位、dict 次序和双向容器 aliases。write_record 对限制性 unpickler 往返自查后压缩、独占写入、hash/length，并拒绝 globals/persistent refs。此处只 Source 阅读，没有执行 helper 或 codec，也不把这些性质当已 Runtime 证明。
7. 文件系统快照先把 Path 转成相对字符串、文件 bytes/hash 或 directory 描述；QImage/QPixmap 只描述尺寸，不交给 native freeze。此次夹具没有 map graph，map_frames 为空或显式塞入公共 QImage，因此当前 frame_description 路径有明确支持范围，不宣称任意真实 map_frames tuple 都适用。
8. RunState apply/save 代理保留 original 并透传原参数和返回值，记录完整前后状态/失败字段，并核查 caller positional/keywords native 不变。代理自身没有接受/修复状态、伪造 True/False 或吞掉 OSError。save 没有 Path 参数；apply 的本次字典/时间夹具是 exact builtins。
9. Path.mkdir/write_text/replace 的代理只记录 owned 父目录或 run.tmp，其他路径直接透传；owned 集合在各 fresh 之前加入，并保留 prior fresh 路径供真实 restart 核查。Path positional/keyword/return 先由 describe_io_argument 变为类型名和 str，不把 Path 交给 freeze。真实写文本 int 返回、mkdir None、replace Path 返回及本次 OSError args 都是可描述/支持的证据形状。
10. 数值入口仅包装原 module.calculate_damage，调用原算法后核查 scenario caller；完整 returned math 和 scenario 保存为 native evidence。没有全局 profile/trace，没有 stub 数值、formatter、reset 或文件方法。包装可能增加观察开销，因此应以 Root 真正返回码/时限结果为准。

## 实际失败与连续、手动新局、对照设计

11. 健康控制 fresh 安装同一固定 run id/时间/事实，实际公开 sample_received 将 level 从1更新3和4；真实 save 后 disk decoded==完整接受 state，临时兄弟文件不存在。完整 state、calculation output、三种原文本一起保存；它是同一实际 099 源的健康控制，不冒称执行旧版本 gold。
12. 失败 fresh 的 run.json 与 run.tmp 是不同路径。fixture 设置 run.tmp 非空目录＋公开 sentinel，随后才记 IO index；fixture 自身不是产品 retry。deliver3 会按真正核心 save 进入 owned parent.mkdir、temp.write_text；目录上的真实 open/write 抛 OS OSError，原核心应返回 False，apply True。runner 要求 ledger 顺序严格 mkdir(returned)、write_text(actual OSError)、没有 replace，并留原目标/账号 bytes 和目录 sentinel 集合。没有 chmod 伪权限、错误返回注入或回放 temp。
13. 此次 accepted state3/4 与同事实健康 state 完整 native 对比；后续 deliver4 应接受并更新实际 UI、时间、培养 getter和 raw run summary，但 owned IO 不再增加。原盘、sentinel不改；run_summary 明确会话保存失败、仅内存、重启可能旧盘，不能误报 unreadable 或“持续累积并保存”。
14. reports 找到实际“计算属性与技能预估”按钮并 click，要求数值代理实际新增调用且 damage_result 非空；使用原 estimate/default/technical 三全文，核查 visible 文本及 full math formatter 不修改。失败3/4报告必须与健康同事实报告完整 native 一致；计算过程还必须不修改 run/account 与每个 owned 文件。不是只比较一个总伤害数字或预造成功文本。
15. 手动步骤显式准备公共 map_frame/preview/test 条件后 click 真 reset_run_button；要求 epoch 增加、新 id、空 operators/relics/maps/history、last_read None、采样 observation/map/target/preview 清理、sticky save_issue、owned IO 不增加、原盘/账号/sentinel不改。随后在新 started_at+1 deliver5，要求保留新 id、不回滚、不重试及显示失败；公开失败窗口 never 被注入旧盘/clone状态。
16. 新局同事实 healthy clone 仅写另一公开目录，并真正构造新 MainWindow，核查 level5和完整 math/三文本相等。最后对原 io_folder 构造新 MainWindow，不重写 fixture，必须真正恢复原id/level1、无本会话save_issue、无新的 owned IO、同初始完整报告，原盘和 sentinel 保留。这证明设计明确区分正在运行的失败新局与独立重启旧盘，没有伪称失败新局已持久化。

## 数量、时限、错误和 Root 收尾

17. Source 成功路线有4次 fresh MainWindow（初始健康、真实失败、健康新局clone、原盘restart），5个 record（健康3/4、失败3/4、手动新局、clone、restart），以及两次 screenshot各2张合计4 PNG。截图来自真实 window.grab，检查 non-null、实际 save、PNG header/hash/尺寸；每张 `root_visual_inspection_completed=False`，Root 仍须实际打开查看，runner 主码0不能替代截图审阅。
18. watchdog 从 pre-import 之后的 started 起计，thread Event.wait(300) 未完成时记录当前 step/pending量和明确 TimeoutError，再 os._exit(124)。process 亦核查 elapsed<300。这是设计中的预算及独立 watchdog，不是实际计时完成记录；Root 应保存真实启动/完成/raw 主码，任何124、其他非0或缺少 final receipt均不可写通过。
19. Python Qt 异常交给 sys.excepthook 列表，每次 process 和最终检查都要求空；main 出错时保留 unfinished record/failure，pass 初始 False且只有所有业务断言之后才 True。finally 对 close/Qt/source drift再次否定 pass，恢复所有模块/RunState/Path原方法和原 excepthook，再关闭公开临时目录并写最终receipt。失败 record 保存自己失败时明确记 unfinished_save_error，不替代假完整证据。
20. 记录保存时源数据支持资格或算法/窗口任何未知差异都由真实运行揭示；本次 Source 审阅没有运行4窗口、5记录、4PNG、计算、file IO 或 watchdog，也没有实际 call counts/主码。Root 的 Saved读回、图片实际视察、Source guard/raw主码和归档闭合仍必需。

这只是一节范围受限的本局 IO/手动新局 actual-window smoke Source 审查，不是 full095 通过、全量回归、原生 Windows、游戏采样或聊天验证。第 100 节 v2 draft int32 小数转换的 pending gap不因本任务改变；不得将其借本 smoke Source 结论改为完成。
