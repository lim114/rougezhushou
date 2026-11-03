# 第 100 节真实窗口 runner 非作者独立 Source 审阅

结论：指定冻结 runner 未发现 Source blocker，可交 Root 按既定顺序实际执行 Gold 与 Candidate。该结论不代表 Gold/Candidate、四张图、项目测试或五节全量检验通过。本人没有 import/执行 runner、helper、codec、项目、tests、Qt、Wine 或 Git，没有 repo 写入或私人读取；仅标准库 Source 哈希、AST、compile-only、公开项目 API/资料只读和本仓库外报告。

## 独立实际 pins 与编译

| 本目录文件 | bytes | SHA256 |
|---|---:|---|
| `window100.py` | 25241 | `8c0a42a606619c60639649c9047e0579afc5be72348d2d4e7d8e23d0f326f467` |
| `native_evidence.py` | 6468 | `f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a` |
| `README.md` | 6057 | `cbd2d1512366738027322aa0deb616feece03e921740eb0344319e424aec1ecc` |
| `source-manifest.json` | 989 | `74f86e6e1196df0ab470c4d293574f947ee3cbff817feb6c6f465e114796f129` |

独立标准库工具 `ac363e` primary 0 对两份 Python Source 调用 `compile(source,path,'exec')`，未 exec 代码对象；`278dbc` primary 0 复核相同 pins 和 compile-only；最终 AST 读取 `4c6244` primary 0 再次确认 runner pin。这比单纯 AST 更能发现嵌套函数作用域/语法错误，但不能说明运行控制流通过。

只读对照的实际已应用 100 app 为 `/workspace/rougezhushou/rouge/app.py` 99596 B / `34f0c92061460b239fd0af80ec263673765a16753826f6151fde87a88b89a35b`；此前产品独立审阅文件为 `/workspace/.continuation/section100-training-view-independent-source-review-v2-final.md`，本次不重做或更改该产品结论。Root 报告实际 99 Gold 已由 Git 原件 27fa 逐 blob 构建并对旧 guard 字节校核；本审阅未调用 Git 验证此过程，runner 自身的 Source/记录绑定如下。

## 先后绑定与证据链

1. 在项目 import 之前，runner 实际调用维护 Source map 并与 Root guard 完全比较，校核复制 native helper hash。Gold 拒绝已安装 training_view helper，且不接受 baseline 参数；Candidate 校核最终 helper `5bef7...`、test `f5a112...`，要求外部 Gold primary-exit 文件的实际值为 0，以及 Gold receipt passed/workflow_complete 均为 True。
2. Candidate 要求同一 runner hash、相同五个健康 case IDs；与 Gold 的 Source 集合比较只允许增加 helper/test、既有文件只允许 app/verify_cloud 改动且 app 必须变化。每个健康 pair 使用相同 public disk SHA，并读取 Gold 实际 native snapshot record，检查压缩/raw 长度哈希和 native 内容，不靠理论结果或硬编码预填成功。
3. Source guard 在所有 case 完成后再次完整比较。passed/workflow_complete 只在窗口数量、PNG 数量、Qt exception 集合和最终 guard 检查之后设置；异常保存 failure 并向外抛出。Root 仍必须实际捕获本次 primary exit；receipt 单独 True 不足以视为通过。

## 窗口与比较的实际 Source 控制

Gold 过滤为五个健康 fixture：full、mixed、masked、None 时间、float91.9/夹取90。Candidate 执行这些相同 fixture，加 bad elite、坏 active rank、巨大 level、坏 consumed timestamp、无账号预览、manual level override、账号/本局混合不兼容，共十二个真实 MainWindow。Source 中循环的三项 unsafe fixture 使十个 append 语句展开为十二项，不是实际已运行计数。

每项创建真实 MainWindow，显示、切到伤害页、选择真实 mechanist 与 S3，并调用真实 calculate。记录 original calculate_damage 的 native 参数及实际返回，只包装观测，不替换数值实现；调用前后使用支持类型/float bits/字典顺序/双向容器别名的比较，验证调用者未变。report_snapshot 要求真实 damage_result，调用 estimate/default/technical 三种真实 formatter，检查 legacy estimate 与 default 一致、实际 UI 文本对应 default，并比较 formatter 前后的 native damage_result。

五个 Candidate 健康 pair 完整比较 native damage_result/scenario、三份文本、widget level/skill、实际 training_conditions 和 ranks。培养错误场景则检查真实 fallback scope/notice，不把原账号或档案预览强标为本局培养已确认。masked case 保留被排除 elite/level/rank 的原语义；无账号 case 明确档案预览和未确认字段；不兼容账号 case 使用有效 run-only potential6 和默认 elite2，不污染成账号 elite1。

step 在每个 UI 动作前后检查 native run/account 记录与 account/run 原 public disk bytes、临时文件存在状态；构造后原盘字节和真实 close 前后同样检查。formatter 的独立前后断言范围是 damage_result，不能把它描述为逐 formatter 都独立套了 disks/step 快照；其公开 Source 是只读格式化路径。Gold/Candidate records 留存 durable 与原盘 bytes，即使 TemporaryDirectory 最终清理，也能由 Root 从受校核原件复核。

## 实际公开机制与 metadata 可达性

已只读 `rouge/data/relic-mechanics.json`、`rouge/data/catalog.json` 与 `relics.py`，未 import 机制函数。SNACK `rogue_6_from_relic_13` 的既有公开 rule 为 sp_cost_factor0.8；mechanist S3 rank10 的公开 sp_cost35，故 runner 的 35/28 控制来自已有规则。CARGO `rogue_6_relic_cargo_10` 三个公开 effect 按 attack/hp/defense 顺序为0.4、condition emergency_hire；既有 context_value 对明确 non_emergency/emergency_hire 返回0/1，对未知返回 None，resolution 将 missing conditions 去重排序。runner 的普通0.0、应急0.4与 unknown missing `['emergency_hire']` 断言与这些 Source 相符，不是本审阅独立确认游戏实机机制。

所有数值窗口以真实有效 SNACK 领取事实和 held CARGO public fixture 进入原 calculation。Candidate 校核 current_run_operator_state 为原 member 引用。bad-elite 窗口在培养 fallback 后，先明确改变 public 内存 recruitment_kind 为 emergency，再实际 calculate，验证三个0.4 effect和28 SP；恢复 ordinary 后验证三个0.0；真实开关 off/on 与 present False/True 门分别控制35/28。四项 fixture mutation 都位于 step 之前且最后恢复，不冒充自动 loader repair、样本采集或“消费者可修改 caller”；step 校核的是随后的真实消费者不能再改变这些事实，磁盘始终是原 ordinary/present public bytes。

已实读 actual100 的 current_operator_state/current_run_operator_state、calculate 与 sync_target_buffs：培养视图与五项独立元数据读取分开，UI 强化状态同源。update_operator 和恢复按钮真实 signal 路径也已对照。manual case 原 saved level=None 先走安全 fallback；真实 level.setValue(17) 经 valueChanged 设置 override，再真实 preserve_level=True 保留未消费 None/potential6，actual conditions 使用17。实际“使用读取等级”按钮调用 preserve=False 路径，重新消费 None 时安全 fallback 至账号80/potential1，notice 仍不可用。这些都是 Source 可达目标，实际 assertions 尚待 Root。

四项 Candidate PNG 目标为 masked、float夹取、bad-elite回退且有效强化、manual override17；使用真实 window.grab().save 并记录实际文件长度/hash，没有生成或预置截图。

## 隔离、结束与本审阅范围

每窗的 account/run/settings 及真实 DesktopBackend 路径都在 fresh public TemporaryDirectory，且 out 必须 fresh、不在 repo 内。app module 的三个存储路径在构造前重定向，DesktopBackend 包装只改变 data_dir 参数，保留真实 backend；其 Source 构造器不启动 process/request。GameCapture 构造器不 connect，ScreenReader 构造器不 OCR；settings 指向不存在的新 public 文件。idle 校核真实 visible、auto False、timer inactive、sample/chat/request busy False、desktop process None/pending empty。未点击采样、连接游戏或聊天按钮；真实关闭只停止 timer/capture/backend，不保存账号/本局。Qt signal exception 通过 sys.excepthook 收集并在 idle/最终检查中拒绝。

watchdog 在 Qt/project import 前启动，450 秒运行预算到期写 timeout 片段并退出124；finally 恢复 calculate/backend 包装、关闭窗口、清理临时目录、恢复 excepthook 并写 receipt。Root 仍保存外部实际退出码和日志，不把预算或 cleanup 声明当实际成功。

此 Source 认可仅覆盖上述非迁移 public fixture 的 bounded real-window runner。原构造器载入/历史迁移保护的限度、raw sample ingestion、未实现干员 formatter 路径及全量回归并未借此闭合；README 正确把它们留给相应实际检查。未填任何 Runtime PASS、实际 PNG、Windows native 或小节完成结果。Root 可按冻结 pin 启动 Gold，再根据真实原件决定 Candidate 与后续验收。
