# 第 122 节真实窗口方案：Source 候选

本目录只有公开源码、公开临时输入和执行提案。作者未导入或运行项目、候选、测试、helper、Qt、Wine、native、Saved、Git，未读取私态或解码 gzip，未修改 tracked 文件。AST/compile-noexec 是语法检查，不能记为 Runtime 通过。实际执行、图像检查和 Git 操作均由 Root 完成。

产品修复仍绑定原封存候选 MF `44613f8d440e06543d569c69ca60776975050c7c0f46ee333a68536e8a2f893a` 及独立消费者 Source 审阅 MF `cabd576982c0735401ab57e5b45208cf5a9897e2b37a8177da185128afa02f65`。本窗口补充真实消费验证，不覆盖原产品包、不把候选快照全文件覆盖到当前 app。Root 必须先精确组合实际源码，再建立本次 Source guard。

`cases.json` 包含全部六份 run/account 公开 JSON 和明确更新包：字符串、数字、null 未知标记；精确 True、False；缺少标记的旧合同。每个窗口从公开临时文件载入，初始及普通 UI/API/格式化操作均必须保留当前 run、账号与磁盘原始 bytes。真实已招募总览、自动藏品勾选、当前培养来源、原始培养摘要、来源/进阶/强化投影和计数资格一起检查，不能只测试 `bool` helper。

计划共 42 个完整 GUI 状态，每个保存原实际调用、完整 caller/result/joint、一次新实际 API 参考、三种 formatter 的联合纯度、真实技术/普通报告切换、完整文本和投影。初始六个窗口各两种时序；字符串窗口 12 次逐项公开更新各两种时序；四次账号参考选择/取消；数字窗口一次明确零清单/空队伍更新后两种时序。普通步骤仍与当前完整 joint 相等；不能凭同 case 或 phase 放宽纯度。

字符串窗口更新依序为身份、完整持有栏、等级、精英及其明确重读的培养字段、当前 S3 等级、来源、进阶标记、B 的部分强化弹窗、重复身份、A 的部分弹窗、独立新计数、完整空弹窗。旧字段/来源/强化/计数保持原证据，必须分别等待自己的新明确证据。原身份重新确认事件包含完整旧成员记录，未知持有转为 True 或 False 不制造旧的获得/失去/离队事件。数字窗口同时验证未知标记转为 False 的原始培养、强化和计数记录仍保留。

**公开更新与普通纯度的边界：** `actual_ingress_begin` 到其唯一 `actual_ingress_end` 内只允许实际 numeric 回调。实际 `MainWindow.apply_run_observation` 在更新 UI 前已经调用 `RunState.save`，所以这些回调的完整 joint 必须等于 end 的精确 after；更新包 caller 前后全图纯净，账号内存与原始账号磁盘不变。end 后所有 setter/事件循环/API/格式化重新恢复普通 current-joint 检查。每个 native record 和 checkpoint 都 flush/fsync；900 秒 watchdog 保存明确失败断点并退出 124。

**等级文案澄清：** 原产品包的计划句子把两种默认分支混在一起，此处根据完整实际第 118 节 `select_rank` Source 更正，不改原封包。未知在场初始回退到账号对象，该对象已读 S1/S3 等级 3，因此默认来源为 `account_reference`、等级 3。身份重新确认后，run scope 中旧等级仍被遮罩、有效等级为空，按既有 E2 默认使用 `preview_unconfirmed` 等级 10；显式勾选账号参考才选择 3，取消恢复 10。两者都不能作为本局确认等级。S3 等级 10 的固定公共 `sp_cost` 是 35，A 的原表系数 0.8 得 28；等级 7 是 41，不能混入该算例。B 的原表只增加攻击速度，不改变 SP 需求。

**保存及重读的边界：** 明确保存检查实际平台的 JSON 序列化 raw bytes。live history 与成员可共享强化 list；JSON 不保存共享引用，因此不能用 native 图相等假定 JSON roundtrip 保留 live alias。六次真实 close 必须保持 live 图与所有磁盘；随后独立 RunState/AccountCache 重读。预期 run 从实际磁盘解析图及旧 constructor key order 推导，仅 restore notice 替换；所有其它 leaf/type/order/float bits 不得改变。普通内存 caller/result/report/joint 则完整保留双向 container alias 检查。没有第二个 live MainWindow 重启的声明。

两幅 PNG 在对应完整 native snapshot 后立即生成：未知初始 run-summary QLabel 全部在真实 central-widget viewport 内，以及新确认 A 后的真实 damage metrics 连续文档块。保存完整图、文本、bounded cursor/label geometry 与原始 PNG bytes/hash。Saved 只审查指定可见范围和证据绑定；Root 必须另外查看原图，不宣称整份长报告或所有字段都在截图内。

Root 执行参数为 `--root`、`--guard`、`--out`、`--source-count`，必须提供本次实际值。guard section 必须为 122，Source count/map、CORE 原始 hash、runner/helper/cases 原始 hash 均绑定；输出必须是 checkout 外的新目录。未预填未来 HEAD、Source count、真实结果目录或 PASS。结束时恢复 app 的三个公开路径变量、DesktopBackend 和 calculate_damage，核对 Source/CORE/guard 无漂移、Qt 错误为空、全部状态和重读完成、deadline 未超时后才可写实际 passed。

独立 Saved 在另一个目录准备，不运行项目、API、formatter 或 Qt；它严格核完整 refs/meta/hash、原始压缩 bytes、chronological current joint、每个显式更新 bracket 和完整 caller/result/report 图。Root 可以在实际窗口通过且 Saved 通过、两幅原图查看后，才将此项记为 Runtime 验证完成。
